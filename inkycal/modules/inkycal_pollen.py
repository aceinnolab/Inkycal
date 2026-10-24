"""
Pollen forecast module for Inkycal (Deutscher Wetterdienst, free open data).

Shows today's and tomorrow's pollen load for one DWD region as small bars:

    Pollenflug                 heute  morgen
    Birke                      ███     ██
    Gräser                     █       █

Region IDs (partregion_id) for Bavaria:
    121  Allgäu / Oberbayern / Bayerischer Wald   (München)
    122  Donauniederungen
    123  Bayern nördlich der Donau
Data is published once a day (around 11:00) and downloaded at most every 3 hours.
"""
import logging
import time

import requests
from PIL import ImageDraw

from inkycal.modules.template import InkycalModule
from inkycal.utils.canvas import Canvas

logger = logging.getLogger(__name__)

URL = "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json"
LEVELS = {"0": 0.0, "0-1": 0.5, "1": 1.0, "1-2": 1.5, "2": 2.0, "2-3": 2.5, "3": 3.0}
NAMES = {"Graeser": "Gräser", "Beifuss": "Beifuß"}


class Pollen(InkycalModule):
    name = "Pollen - daily pollen forecast from the Deutscher Wetterdienst"

    optional = {
        "partregion_id": {
            "label": "DWD region: 121 = München/Oberbayern, 122 = Donauniederungen, 123 = Nordbayern",
            "default": 121,
        },
        "plants": {
            "label": "Only these plants (one per line, e.g. Birke, Graeser). Empty = all",
            "default": [],
        },
        "show_zero": {
            "label": "Also show plants with no pollen",
            "options": [False, True],
        },
        "title": {
            "label": "Heading shown at the top (empty = no heading)",
            "default": "Pollenflug",
        },
    }

    CACHE_SECONDS = 3 * 3600

    def __init__(self, config):
        super().__init__(config)
        cfg = config["config"]
        self.region = int(cfg.get("partregion_id", 121) or 121)
        plants = cfg.get("plants") or []
        if isinstance(plants, str):
            plants = plants.replace(";", ",").split(",")
        self.plants = [p.strip().lower() for p in plants if p.strip()]
        self.show_zero = bool(cfg.get("show_zero", False))
        self.title = cfg.get("title", "Pollenflug")
        self._cache = None
        self._cache_time = 0.0

    def _region_data(self):
        if self._cache is not None and time.time() - self._cache_time < self.CACHE_SECONDS:
            return self._cache
        r = requests.get(URL, timeout=20)
        r.raise_for_status()
        data = r.json()
        entry = None
        for item in data.get("content", []):
            if item.get("partregion_id") == self.region or (
                    item.get("partregion_id") == -1 and item.get("region_id") == self.region):
                entry = item
                break
        if entry is None:
            raise ValueError(f"DWD region {self.region} not found")
        self._cache, self._cache_time = entry, time.time()
        return entry

    def rows(self, entry):
        out = []
        for plant, values in (entry.get("Pollen") or {}).items():
            if self.plants and plant.lower() not in self.plants and NAMES.get(plant, plant).lower() not in self.plants:
                continue
            today = LEVELS.get(str(values.get("today", "0")), 0.0)
            tomorrow = LEVELS.get(str(values.get("tomorrow", "0")), 0.0)
            if today == 0 and tomorrow == 0 and not self.show_zero:
                continue
            out.append((NAMES.get(plant, plant), today, tomorrow))
        out.sort(key=lambda r: (-max(r[1], r[2]), r[0]))
        return out

    def generate_image(self):
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        canvas = Canvas((im_width, im_height), self.font, self.fontsize)
        line_h = int(canvas.get_line_height() * 1.25)

        try:
            entry = self._region_data()
        except Exception:
            logger.exception("Pollen module: could not load DWD data")
            if self._cache is None:
                canvas.write((0, 0), (im_width, im_height), "Pollen: keine Daten")
                return canvas.image_black, canvas.image_colour
            entry = self._cache

        col_name = int(im_width * 0.34)
        col_bar = (im_width - col_name) // 2
        y = 0
        if self.title:
            canvas.write((0, y), (col_name, line_h), self.title, alignment="left")
        canvas.write((col_name, y), (col_bar, line_h), "heute", alignment="left")
        canvas.write((col_name + col_bar, y), (col_bar, line_h), "morgen", alignment="left")
        y += line_h

        rows = self.rows(entry)
        if not rows:
            canvas.write((0, y), (im_width, line_h), "Kein nennenswerter Pollenflug", alignment="left")
            return canvas.image_black, canvas.image_colour

        draw = ImageDraw.Draw(canvas.image_black)
        bar_max = col_bar - 12
        bar_h = max(4, int(line_h * 0.45))
        for name, today, tomorrow in rows:
            if y + line_h > im_height:
                break
            canvas.write((0, y), (col_name, line_h), name, alignment="left")
            top = y + (line_h - bar_h) // 2
            for i, level in enumerate((today, tomorrow)):
                x0 = col_name + i * col_bar
                # outline = scale (0..3), filled part = level
                draw.rectangle((x0, top, x0 + bar_max, top + bar_h), outline="black", width=1)
                if level > 0:
                    draw.rectangle((x0, top, x0 + int(bar_max * level / 3), top + bar_h), fill="black")
            y += line_h

        return canvas.image_black, canvas.image_colour
