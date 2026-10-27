"""
S-Bahn departures module for Inkycal (Munich, via the unofficial MVG API).

Shows the next departures from one station:

    Nächste: S8 Flughafen München in 4 min          (optional big line)
    08:42  S8  Flughafen München    Gl. 2    +3
    08:47  S1  Freising             Gl. 1    entfällt   (struck through)

Needs the 'mvg' package:  pip install mvg
MVG tolerates moderate private use - keep update_interval at 5 minutes or more.
"""
import logging
from datetime import datetime

from PIL import ImageDraw, ImageFont

from inkycal.modules.template import InkycalModule
from inkycal.utils.canvas import Canvas

logger = logging.getLogger(__name__)


class SBahn(InkycalModule):
    name = "S-Bahn - next departures from an MVV station"

    requires = {
        "station": {
            "label": "Station name as on mvg.de, e.g. Pasing or Marienplatz",
        },
    }

    optional = {
        "walk_minutes": {
            "label": "Minutes you need to walk to the station (hides trains you can't catch)",
            "default": 0,
        },
        "lines": {
            "label": "Only show these lines, e.g. S3 and S8. Empty = all S-Bahn lines",
            "default": [],
        },
        "relative_time": {
            "label": "Show 'in 5 min' instead of the clock time",
            "options": [False, True],
        },
        "show_platform": {
            "label": "Show the platform (Gleis)",
            "options": [True, False],
        },
        "big_next": {
            "label": "Show a big 'next train' line at the top",
            "options": [True, False],
        },
    }

    def __init__(self, config):
        super().__init__(config)
        cfg = config["config"]

        self.station_name = cfg.get("station", "Marienplatz")
        self.walk_minutes = int(cfg.get("walk_minutes", 0) or 0)
        lines = cfg.get("lines") or []
        if isinstance(lines, str):
            lines = [l for l in lines.replace(";", ",").split(",")]
        self.lines = [str(l).strip().upper() for l in lines if str(l).strip()]
        self.relative_time = bool(cfg.get("relative_time", False))
        self.show_platform = bool(cfg.get("show_platform", True))
        self.big_next = bool(cfg.get("big_next", False))

        self._station_id = None

    # ------------------------------------------------------------------
    def _get_departures(self, limit):
        # Imported here so a missing package gives a clear error in the log
        from mvg import MvgApi, TransportType

        if self._station_id is None:
            station = MvgApi.station(self.station_name)
            if not station:
                raise ValueError(f"Station '{self.station_name}' not found at MVG")
            self._station_id = station["id"]
            self.station_name = station["name"]
            logger.info(f"S-Bahn module: using station {self.station_name} ({self._station_id})")

        api = MvgApi(self._station_id)
        # Ask for more than needed, because we may filter out lines afterwards
        deps = api.departures(
            limit=max(10, limit * 3),
            offset=self.walk_minutes,
            transport_types=[TransportType.SBAHN],
        )
        if self.lines:
            deps = [d for d in deps if str(d["line"]).upper() in self.lines]
        return deps[:limit]

    @staticmethod
    def _minutes_until(ts, now):
        return max(0, int((ts - now) // 60))

    # ------------------------------------------------------------------
    def generate_image(self):
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))

        canvas = Canvas((im_width, im_height), self.font, self.fontsize)
        line_h = int(canvas.get_line_height() * 1.25)

        header_h = line_h
        big_h = int(line_h * 1.8) if self.big_next else 0
        rows = max(1, (im_height - header_h - big_h) // line_h)

        try:
            departures = self._get_departures(rows + 1)
        except Exception:
            logger.exception("S-Bahn module: could not load departures")
            canvas.write((0, 0), (im_width, im_height), "S-Bahn: keine Daten", alignment="center")
            return canvas.image_black, canvas.image_colour

        now = datetime.now().timestamp()
        y = 0

        # Big "next train" line
        if self.big_next:
            nxt = next((d for d in departures if not d.get("cancelled")), None)
            if nxt:
                mins = self._minutes_until(nxt["time"], now)
                when = "jetzt" if mins == 0 else f"in {mins} min"
                text = f"{nxt['line']} {nxt['destination']} {when}"
            else:
                text = "Keine Abfahrt"
            # pick the largest font that fits the width and ~75% of the height
            size = max(self.fontsize, int(big_h * 0.75))
            while size > self.fontsize:
                font = ImageFont.truetype(self.font.value, size)
                if font.getlength(text) <= im_width and font.getbbox("Ag")[3] <= big_h:
                    break
                size -= 1
            big = Canvas((im_width, big_h), self.font, size)
            big.write((0, 0), (im_width, big_h), text, alignment="left")
            canvas.image_black.paste(big.image_black, (0, y))
            y += big_h

        canvas.write((0, y), (im_width, header_h), f"Abfahrten {self.station_name}", alignment="left")
        y += header_h

        if not departures:
            canvas.write((0, y), (im_width, im_height - y), "Keine Abfahrten", alignment="center")
            return canvas.image_black, canvas.image_colour

        # Column layout (pixels)
        col_time = int(im_width * 0.17)
        col_line = int(im_width * 0.10)
        col_plat = int(im_width * 0.12) if self.show_platform else 0
        col_status = int(im_width * 0.18)
        col_dest = im_width - col_time - col_line - col_plat - col_status

        draw_black = ImageDraw.Draw(canvas.image_black)
        draw_colour = ImageDraw.Draw(canvas.image_colour)

        for d in departures[:rows]:
            if y + line_h > im_height:
                break

            if self.relative_time:
                mins = self._minutes_until(d["time"], now)
                t = "jetzt" if mins == 0 else f"{mins} min"
            else:
                t = datetime.fromtimestamp(d["planned"]).strftime("%H:%M")

            cancelled = bool(d.get("cancelled"))
            delay = d.get("delay") or 0
            if cancelled:
                status = "entfällt"
            elif delay:
                status = f"+{delay}"
            else:
                status = ""

            x = 0
            canvas.write((x, y), (col_time, line_h), t, alignment="left")
            x += col_time
            canvas.write((x, y), (col_line, line_h), str(d["line"]), alignment="left")
            x += col_line
            canvas.write((x, y), (col_dest, line_h), str(d["destination"]), alignment="left")
            x += col_dest
            if self.show_platform:
                plat = d.get("platform")
                canvas.write((x, y), (col_plat, line_h), f"Gl. {plat}" if plat not in (None, "") else "",
                             alignment="left")
                x += col_plat
            # delays/cancellations go on the colour layer (red on 3-colour displays, black on b/w)
            canvas.write((x, y), (col_status, line_h), status, alignment="right",
                         colour="colour" if status else "black")

            if cancelled:
                # strike through time, line and destination
                mid = y + line_h // 2
                end = col_time + col_line + col_dest - 4
                draw_black.line((0, mid, end, mid), fill="black", width=2)
                draw_colour.line((0, mid, end, mid), fill="black", width=2)

            y += line_h

        return canvas.image_black, canvas.image_colour
