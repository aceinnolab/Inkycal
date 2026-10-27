"""
Waste collection module for Inkycal (Müllabfuhr).

Reads the collection dates from an iCalendar (.ics) link or file - e.g. the
AWM München "Abfuhrkalender" export - and shows the next pickups:

    Müllabfuhr
    Morgen      Restmüll
    Do 30.10.   Papier, Bio

The calendar is downloaded at most every 12 hours and saved to the cache
folder (inkycal/cache/, not in Git). Between downloads, and whenever a download
fails (WiFi drop, AWM offline), the saved copy is used, so the display keeps
showing the dates. "keine Daten" only appears if no copy was ever saved.
"""
import hashlib
import logging
import os
import time
from datetime import date, datetime, timedelta

import requests

from inkycal.modules.template import InkycalModule
from inkycal.settings import Settings
from inkycal.utils.canvas import Canvas

logger = logging.getLogger(__name__)

WEEKDAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

# Shorter names for typical AWM / German calendar titles
SHORT_NAMES = [
    ("rest", "Restmüll"),
    ("bio", "Bio"),
    ("papier", "Papier"),
    ("gelb", "Gelbe Tonne"),
    ("wertstoff", "Wertstoff"),
    ("glas", "Glas"),
    ("sperr", "Sperrmüll"),
    ("problem", "Problemmüll"),
]


class Waste(InkycalModule):
    name = "Waste collection (Müllabfuhr) - next pickup dates from an iCalendar"

    requires = {
        "ical_urls": {
            "label": "Link(s) to the waste calendar (.ics), e.g. from the AWM Abfuhrkalender",
        },
    }

    optional = {
        "ical_files": {
            "label": "Or local .ics file path(s) on the Pi",
            "default": None,
        },
        "days": {
            "label": "How many days ahead to look",
            "default": 21,
        },
        "short_names": {
            "label": "Shorten titles (e.g. 'Restmülltonne 2-wöchentlich' -> 'Restmüll')",
            "options": [True, False],
        },
        "title": {
            "label": "Heading shown at the top (empty = no heading)",
            "default": "Müllabfuhr",
        },
    }

    CACHE_SECONDS = 12 * 3600

    def __init__(self, config):
        super().__init__(config)
        cfg = config["config"]
        urls = cfg.get("ical_urls") or []
        files = cfg.get("ical_files") or []
        self.ical_urls = [urls] if isinstance(urls, str) else list(urls)
        self.ical_files = [files] if isinstance(files, str) else list(files)
        self.ical_urls = [u for u in self.ical_urls if u]
        self.ical_files = [f for f in self.ical_files if f]
        if not self.ical_urls and not self.ical_files:
            raise ValueError("Waste module: please set ical_urls or ical_files")
        self.days = int(cfg.get("days", 21) or 21)
        self.short_names = bool(cfg.get("short_names", True))
        self.title = cfg.get("title", "Müllabfuhr")
        self._cache = None  # last computed pickups, used if everything fails

    # ------------------------------------------------------------------
    def _short(self, title: str) -> str:
        if not self.short_names:
            return title
        low = title.lower()
        for needle, short in SHORT_NAMES:
            if needle in low:
                return short
        return title

    @staticmethod
    def _cache_file(url: str) -> str:
        # File name from a hash of the link, so the address in it is not visible
        key = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
        return os.path.join(Settings.CACHE_PATH, f"waste_{key}.ics")

    def _fetch_ics(self, url: str) -> str:
        """Return the .ics text for url: from the cache file if it is fresh,
        otherwise downloaded (and saved). Falls back to an old cache file
        if the download fails."""
        path = self._cache_file(url)
        age = time.time() - os.path.getmtime(path) if os.path.exists(path) else None

        if age is not None and age < self.CACHE_SECONDS:
            with open(path, encoding="utf-8") as f:
                return f.read()

        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            text = r.text
            if "BEGIN:VCALENDAR" not in text:
                raise ValueError("response is not an iCalendar file")
        except Exception as e:
            if age is None:
                raise
            logger.warning(f"Waste module: download failed ({e.__class__.__name__}: {e}), "
                           f"using saved calendar from {age / 3600:.1f} h ago")
            with open(path, encoding="utf-8") as f:
                return f.read()

        try:
            os.makedirs(Settings.CACHE_PATH, exist_ok=True)
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, path)
        except OSError as e:
            logger.warning(f"Waste module: could not save the calendar to the cache: {e}")
        logger.info("Waste module: calendar downloaded")
        return text

    def _load_calendars(self):
        from icalendar import Calendar
        cals = []
        for url in self.ical_urls:
            cals.append(Calendar.from_ical(self._fetch_ics(url)))
        for path in self.ical_files:
            with open(path, encoding="utf-8") as f:
                cals.append(Calendar.from_ical(f.read()))
        return cals

    def _pickups(self):
        """Return {date: [names]} for the next self.days days."""
        import recurring_ical_events

        today = date.today()
        end = today + timedelta(days=self.days)
        result = {}
        for cal in self._load_calendars():
            for ev in recurring_ical_events.of(cal).between(today, end + timedelta(days=1)):
                start = ev.get("DTSTART")
                if start is None:
                    continue
                d = start.dt.date() if isinstance(start.dt, datetime) else start.dt
                if d < today or d > end:
                    continue
                name = self._short(str(ev.get("SUMMARY", "")).strip())
                if name and name not in result.setdefault(d, []):
                    result[d].append(name)

        self._cache = result
        logger.debug(f"Waste module: {sum(len(v) for v in result.values())} pickups in the next {self.days} days")
        return result

    @staticmethod
    def _day_label(d: date) -> str:
        delta = (d - date.today()).days
        if delta == 0:
            return "Heute"
        if delta == 1:
            return "Morgen"
        return f"{WEEKDAYS_DE[d.weekday()]} {d.day:02d}.{d.month:02d}."

    # ------------------------------------------------------------------
    def generate_image(self):
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        canvas = Canvas((im_width, im_height), self.font, self.fontsize)
        line_h = int(canvas.get_line_height() * 1.25)

        try:
            pickups = self._pickups()
        except Exception:
            logger.exception("Waste module: could not load the calendar")
            if self._cache is None:
                canvas.write((0, 0), (im_width, im_height), "Müllabfuhr: keine Daten")
                return canvas.image_black, canvas.image_colour
            today = date.today()
            pickups = {d: v for d, v in self._cache.items() if d >= today}

        y = 0
        if self.title:
            canvas.write((0, y), (im_width, line_h), self.title, alignment="left")
            y += line_h

        if not pickups:
            canvas.write((0, y), (im_width, line_h), f"Keine Abholung in den nächsten {self.days} Tagen",
                         alignment="left")
            return canvas.image_black, canvas.image_colour

        col_day = int(im_width * 0.30)
        for d in sorted(pickups):
            if y + line_h > im_height:
                break
            soon = (d - date.today()).days <= 1
            colour = "colour" if soon else "black"  # red on 3-colour displays
            canvas.write((0, y), (col_day, line_h), self._day_label(d), alignment="left", colour=colour)
            canvas.write((col_day, y), (im_width - col_day, line_h), ", ".join(pickups[d]),
                         alignment="left", colour=colour)
            y += line_h

        return canvas.image_black, canvas.image_colour
