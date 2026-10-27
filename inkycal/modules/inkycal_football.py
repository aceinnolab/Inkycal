"""
Football module for Inkycal - last result and next matches of one team.

Uses the free OpenLigaDB API (api.openligadb.de). Default team: FC Bayern (ID 40).

    FC Bayern
    Letztes:  Bayern 2:2 Arsenal            CL
    Sa 25.10. 17:30  Freiburg – Bayern      BL
    Mi 29.10. 20:45  Bayern – Köln          Pokal

Data is downloaded at most every 30 minutes (every 5 minutes during a match).
"""
import logging
import time
from datetime import datetime, timezone

import requests

from inkycal.modules.template import InkycalModule
from inkycal.utils.canvas import Canvas

logger = logging.getLogger(__name__)

WEEKDAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
LEAGUES = {"bl1": "BL", "bl2": "2.BL", "ucl": "CL", "uel": "EL", "dfb": "Pokal", "dfbpokal": "Pokal"}
API = "https://api.openligadb.de/getmatchesbyteamid/{team}/{past}/{future}"


def _result(match):
    """Final (or latest) score as (goals1, goals2) or None."""
    results = match.get("matchResults") or []
    if not results:
        goals = match.get("goals") or []
        if goals:
            last = goals[-1]
            return last.get("scoreTeam1"), last.get("scoreTeam2")
        return None
    best = max(results, key=lambda r: r.get("resultOrderID", 0))
    return best.get("pointsTeam1"), best.get("pointsTeam2")


def _kickoff(match):
    utc = match.get("matchDateTimeUTC")
    if utc:
        return datetime.fromisoformat(utc.replace("Z", "+00:00")).astimezone()
    return datetime.fromisoformat(match["matchDateTime"]).astimezone()


class Football(InkycalModule):
    name = "Football - last result and next matches (OpenLigaDB)"

    optional = {
        "team_id": {
            "label": "OpenLigaDB team ID (FC Bayern = 40, 1860 München = 9, Dortmund = 7)",
            "default": 40,
        },
        "title": {
            "label": "Heading shown at the top (empty = no heading)",
            "default": "FC Bayern",
        },
        "upcoming": {
            "label": "How many upcoming matches to show",
            "default": 3,
        },
    }

    CACHE_SECONDS = 30 * 60
    LIVE_CACHE_SECONDS = 5 * 60

    def __init__(self, config):
        super().__init__(config)
        cfg = config["config"]
        self.team_id = int(cfg.get("team_id", 40) or 40)
        self.title = cfg.get("title", "FC Bayern")
        self.upcoming_count = int(cfg.get("upcoming", 3) or 3)
        self._cache = None
        self._cache_time = 0.0
        self._live = False

    def _matches(self):
        max_age = self.LIVE_CACHE_SECONDS if self._live else self.CACHE_SECONDS
        if self._cache is not None and time.time() - self._cache_time < max_age:
            return self._cache
        r = requests.get(API.format(team=self.team_id, past=3, future=5), timeout=20)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            raise ValueError("unexpected answer from OpenLigaDB")
        data.sort(key=_kickoff)
        self._cache, self._cache_time = data, time.time()
        return data

    @staticmethod
    def _short(team):
        return team.get("shortName") or team.get("teamName", "?")

    @staticmethod
    def _league(match):
        code = (match.get("leagueShortcut") or "").lower()
        if code in LEAGUES:
            return LEAGUES[code]
        return code.upper()[:5] if code else ""

    def generate_image(self):
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        canvas = Canvas((im_width, im_height), self.font, self.fontsize)
        line_h = int(canvas.get_line_height() * 1.25)

        try:
            matches = self._matches()
        except Exception:
            logger.exception("Football module: could not load matches")
            if self._cache is None:
                canvas.write((0, 0), (im_width, im_height), "Fußball: keine Daten")
                return canvas.image_black, canvas.image_colour
            matches = self._cache

        now = datetime.now(timezone.utc).astimezone()
        finished = [m for m in matches if m.get("matchIsFinished")]
        live = [m for m in matches if not m.get("matchIsFinished") and _kickoff(m) <= now]
        future = [m for m in matches if not m.get("matchIsFinished") and _kickoff(m) > now]
        self._live = bool(live)

        y = 0
        col_league = int(im_width * 0.14)
        col_main = im_width - col_league

        if self.title:
            canvas.write((0, y), (im_width, line_h), self.title, alignment="left")
            y += line_h

        def row(text, league, colour="black"):
            nonlocal y
            if y + line_h > im_height:
                return
            canvas.write((0, y), (col_main, line_h), text, alignment="left", colour=colour)
            canvas.write((col_main, y), (col_league, line_h), league, alignment="right")
            y += line_h

        for m in live[:1]:
            score = _result(m) or (0, 0)
            row(f"LIVE  {self._short(m['team1'])} {score[0]}:{score[1]} {self._short(m['team2'])}",
                self._league(m), colour="colour")

        if finished:
            m = finished[-1]
            score = _result(m)
            s = f"{score[0]}:{score[1]}" if score else "-:-"
            row(f"Letztes:  {self._short(m['team1'])} {s} {self._short(m['team2'])}", self._league(m))

        for m in future[: self.upcoming_count]:
            k = _kickoff(m)
            when = f"{WEEKDAYS_DE[k.weekday()]} {k.day:02d}.{k.month:02d}. {k:%H:%M}"
            row(f"{when}  {self._short(m['team1'])} – {self._short(m['team2'])}", self._league(m))

        if not (finished or live or future):
            row("Keine Spiele gefunden", "")

        return canvas.image_black, canvas.image_colour
