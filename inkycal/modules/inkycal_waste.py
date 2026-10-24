"""
Waste collection module for Inkycal (Müllabfuhr).

Reads the collection dates from an iCalendar (.ics) link or file - e.g. the
AWM München "Abfuhrkalender" export - and shows the next pickups:

    Müllabfuhr
    Morgen      Restmüll
    Do 30.10.   Papier, Bio

The calendar is downloaded at most every 6 hours.
"""
import logging
import time
from datetime import date, datetime, timedelta

import requests

from inkycal.modules.template import InkycalModule
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

    CACHE_SECONDS = 6 * 3600

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
        self._cache = None
        self._cache_time = 0.0

    # ------------------------------------------------------------------
    def _short(self, title: str) -> str:
        if not self.short_names:
            return title
        low = title.lower()
        for needle, short in SHORT_NAMES:
            if needle in low:
                return short
        return title

    def _load_calendars(self):
        from icalendar import Calendar
        cals = []
        for url in self.ical_urls:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            cals.append(Calendar.from_ical(r.text))
        for path in self.ical_files:
            with open(path, encoding="utf-8") as f:
                cals.append(Calendar.from_ical(f.read()))
        return cals

    def _pickups(self):
        """Return {date: [names]} for the next self.days days (cached)."""
        if self._cache is not None and time.time() - self._cache_time < self.CACHE_SECONDS:
            return self._cache

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

        self._cache, self._cache_time = result, time.time()
        logger.info(f"Waste module: {sum(len(v) for v in result.values())} pickups in the next {self.days} days")
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
            pickups = self._cache

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
