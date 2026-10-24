"""
Birthdays module for Inkycal.

Enter one birthday per line in the web UI, for example:

    Max 14.03.1985
    Oma 02.11.
    Lisa 1990-07-21

and the module shows the upcoming ones:

    Geburtstage
    Heute       Oma
    in 3 Tagen  Max wird 41
"""
import logging
import re
from datetime import date

from inkycal.modules.template import InkycalModule
from inkycal.utils.canvas import Canvas

logger = logging.getLogger(__name__)

_DE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})?")
_ISO = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")


def parse_birthday(line: str):
    """'Max 14.03.1985' -> ('Max', 3, 14, 1985). Returns None if no date found."""
    line = line.strip()
    m = _ISO.search(line)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        m = _DE.search(line)
        if not m:
            return None
        day, month = int(m.group(1)), int(m.group(2))
        year = int(m.group(3)) if m.group(3) else None
    name = (line[:m.start()] + line[m.end():]).strip(" :-,;\t")
    if not name or not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    return name, month, day, year


def next_occurrence(month: int, day: int, today: date) -> date:
    for year in (today.year, today.year + 1, today.year + 2):
        try:
            d = date(year, month, day)
        except ValueError:  # 29.02. in a non-leap year -> 28.02.
            d = date(year, month, 28)
        if d >= today:
            return d
    return today


class Birthdays(InkycalModule):
    name = "Birthdays - upcoming birthdays from a simple list"

    requires = {
        "birthdays": {
            "label": "One per line: name and date, e.g. 'Max 14.03.1985' or 'Oma 02.11.'",
        },
    }

    optional = {
        "days": {
            "label": "How many days ahead to show",
            "default": 60,
        },
        "title": {
            "label": "Heading shown at the top (empty = no heading)",
            "default": "Geburtstage",
        },
    }

    def __init__(self, config):
        super().__init__(config)
        cfg = config["config"]
        raw = cfg.get("birthdays") or []
        if isinstance(raw, str):
            raw = raw.splitlines()
        self.entries = []
        for line in raw:
            parsed = parse_birthday(str(line))
            if parsed:
                self.entries.append(parsed)
            elif str(line).strip():
                logger.warning(f"Birthdays module: could not read '{line}'")
        self.days = int(cfg.get("days", 60) or 60)
        self.title = cfg.get("title", "Geburtstage")

    def upcoming(self, today: date = None):
        today = today or date.today()
        items = []
        for name, month, day, year in self.entries:
            d = next_occurrence(month, day, today)
            delta = (d - today).days
            if delta <= self.days:
                age = d.year - year if year else None
                items.append((delta, d, name, age))
        items.sort(key=lambda i: (i[0], i[2]))
        return items

    @staticmethod
    def _when(delta: int, d: date) -> str:
        if delta == 0:
            return "Heute"
        if delta == 1:
            return "Morgen"
        if delta < 7:
            return f"in {delta} Tagen"
        return f"{d.day:02d}.{d.month:02d}."

    def generate_image(self):
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        canvas = Canvas((im_width, im_height), self.font, self.fontsize)
        line_h = int(canvas.get_line_height() * 1.25)

        y = 0
        if self.title:
            canvas.write((0, y), (im_width, line_h), self.title, alignment="left")
            y += line_h

        items = self.upcoming()
        if not items:
            canvas.write((0, y), (im_width, line_h), f"Keine in den nächsten {self.days} Tagen", alignment="left")
            return canvas.image_black, canvas.image_colour

        col_when = int(im_width * 0.30)
        for delta, d, name, age in items:
            if y + line_h > im_height:
                break
            text = f"{name} wird {age}" if age else name
            colour = "colour" if delta == 0 else "black"
            canvas.write((0, y), (col_when, line_h), self._when(delta, d), alignment="left", colour=colour)
            canvas.write((col_when, y), (im_width - col_when, line_h), text, alignment="left", colour=colour)
            y += line_h

        return canvas.image_black, canvas.image_colour
