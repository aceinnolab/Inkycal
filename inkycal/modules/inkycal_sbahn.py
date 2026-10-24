"""
S-Bahn departures module for Inkycal (Munich, via the unofficial MVG API).

Shows the next departures from one station:
    08:42  S8  Flughafen München     +3
    08:47  S1  Freising              ✗ fällt aus

Needs the 'mvg' package:  pip install mvg
"""
import logging
from datetime import datetime

from inkycal.modules.template import InkycalModule
from inkycal.utils.canvas import Canvas

logger = logging.getLogger(__name__)


class SBahn(InkycalModule):
    name = "S-Bahn - next departures from an MVV station"

    def __init__(self, config):
        super().__init__(config)
        cfg = config["config"]

        # Station name as you'd type it on mvg.de, e.g. "Marienplatz" or "Pasing"
        self.station_name = cfg.get("station", "Marienplatz")
        # Minutes it takes you to walk to the station (hides trains you can't catch)
        self.walk_minutes = int(cfg.get("walk_minutes", 0) or 0)
        # Only show these lines, e.g. ["S3", "S8"]. Empty = all S-Bahn lines.
        self.lines = [l.upper() for l in (cfg.get("lines") or [])]
        # Show "in 5 min" instead of "08:42"
        self.relative_time = bool(cfg.get("relative_time", False))

        self._station_id = None

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
            limit=limit * 3,
            offset=self.walk_minutes,
            transport_types=[TransportType.SBAHN],
        )
        if self.lines:
            deps = [d for d in deps if str(d["line"]).upper() in self.lines]
        return deps[:limit]

    def generate_image(self):
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))

        canvas = Canvas((im_width, im_height), self.font, self.fontsize)
        line_h = int(canvas.get_line_height() * 1.25)

        # Header row
        header_h = line_h
        rows = max(1, (im_height - header_h) // line_h)

        try:
            departures = self._get_departures(rows)
        except Exception as e:
            logger.exception("S-Bahn module: could not load departures")
            canvas.write((0, 0), (im_width, im_height),
                         "S-Bahn: keine Daten", alignment="center")
            return canvas.image_black, canvas.image_colour

        canvas.write((0, 0), (im_width, header_h),
                     f"Abfahrten {self.station_name}", alignment="left")

        if not departures:
            canvas.write((0, header_h), (im_width, im_height - header_h),
                         "Keine Abfahrten", alignment="center")
            return canvas.image_black, canvas.image_colour

        # Column layout (pixels)
        col_time = int(im_width * 0.20)
        col_line = int(im_width * 0.12)
        col_status = int(im_width * 0.20)
        col_dest = im_width - col_time - col_line - col_status

        now = datetime.now().timestamp()

        for i, d in enumerate(departures):
            y = header_h + i * line_h

            if self.relative_time:
                mins = max(0, int((d["time"] - now) // 60))
                t = "jetzt" if mins == 0 else f"{mins} min"
            else:
                t = datetime.fromtimestamp(d["planned"]).strftime("%H:%M")

            if d.get("cancelled"):
                status = "fällt aus"
            elif d.get("delay"):
                status = f"+{d['delay']}"
            else:
                status = ""

            x = 0
            canvas.write((x, y), (col_time, line_h), t, alignment="left")
            x += col_time
            canvas.write((x, y), (col_line, line_h), str(d["line"]), alignment="left")
            x += col_line
            canvas.write((x, y), (col_dest, line_h), str(d["destination"]), alignment="left")
            x += col_dest
            canvas.write((x, y), (col_status, line_h), status, alignment="right")

        return canvas.image_black, canvas.image_colour
