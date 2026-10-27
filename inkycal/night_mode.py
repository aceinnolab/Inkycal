"""Night mode for Inkycal.

During the night the display is refreshed once with a simple night screen
(date, tomorrow's first events, tomorrow's weather) and then left alone until
the night ends. No module data is fetched during that time.

Settings (settings.json):
    "night_mode": true/false        scheduled night mode on/off
    "night_start": "23:00"
    "night_end": "06:00"

The web UI button writes a small state file (night_state.json in the Inkycal
folder) to start or end night mode right away:
    {"manual": "on",  "until": "<iso time>"}   night mode now, until the next night_end
    {"manual": "off", "until": "<iso time>"}   night ended early, until the next night_start
"""
from __future__ import annotations

import json
import logging
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "night_state.json"

WEEKDAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONTHS_DE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
             "September", "Oktober", "November", "Dezember"]
WEATHER_DE = {
    "01": "sonnig", "02": "leicht bewölkt", "03": "bewölkt", "04": "stark bewölkt",
    "09": "Schauer", "10": "Regen", "11": "Gewitter", "13": "Schnee", "50": "Nebel",
}
WEATHER_ICONS = {
    "01": "", "02": "", "03": "", "04": "", "09": "",
    "10": "", "11": "", "13": "", "50": "",
}


# ---------------------------------------------------------------------------
# Schedule / state
# ---------------------------------------------------------------------------
def _parse_hhmm(value, fallback: str) -> time:
    for text in (str(value or ""), fallback):
        try:
            h, m = text.strip().replace(".", ":").split(":")
            return time(int(h), int(m))  # raises for invalid times like 25:99
        except Exception:
            continue
    return time(0, 0)


def schedule(settings: Dict) -> Tuple[time, time]:
    return (_parse_hhmm(settings.get("night_start"), "23:00"),
            _parse_hhmm(settings.get("night_end"), "06:00"))


def _in_window(now: datetime, start: time, end: time) -> bool:
    t = now.time()
    if start == end:
        return False
    if start < end:
        return start <= t < end
    return t >= start or t < end  # window over midnight


def next_time(now: datetime, at: time) -> datetime:
    candidate = now.replace(hour=at.hour, minute=at.minute, second=0, microsecond=0)
    return candidate if candidate > now else candidate + timedelta(days=1)


def read_state() -> Dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_state(state: Optional[Dict]) -> None:
    if not state:
        STATE_FILE.unlink(missing_ok=True)
        return
    STATE_FILE.write_text(json.dumps(state), encoding="utf-8")


def status(settings: Dict, now: Optional[datetime] = None) -> Tuple[bool, Optional[datetime], str]:
    """(active, until, reason). reason: 'button', 'schedule' or ''."""
    now = now or datetime.now()
    start, end = schedule(settings)

    state = read_state()
    if state.get("manual") in ("on", "off"):
        try:
            until = datetime.fromisoformat(state["until"])
        except Exception:
            until = None
        if until and now < until:
            if state["manual"] == "on":
                return True, until, "button"
            return False, until, "button"

    if settings.get("night_mode") and _in_window(now, start, end):
        return True, next_time(now, end), "schedule"
    return False, None, ""


def start_now(settings: Dict, now: Optional[datetime] = None) -> datetime:
    now = now or datetime.now()
    _, end = schedule(settings)
    until = next_time(now, end)
    write_state({"manual": "on", "until": until.isoformat(timespec="minutes")})
    return until


def end_now(settings: Dict, now: Optional[datetime] = None) -> None:
    now = now or datetime.now()
    start, _ = schedule(settings)
    if settings.get("night_mode"):
        # keep the dashboard on until tonight's scheduled start
        write_state({"manual": "off", "until": next_time(now, start).isoformat(timespec="minutes")})
    else:
        write_state(None)


# ---------------------------------------------------------------------------
# Night screen
# ---------------------------------------------------------------------------
def _find_module(settings: Dict, names: List[str]) -> Optional[Dict]:
    for mod in settings.get("modules", []) or []:
        if mod.get("name") in names:
            return mod.get("config") or {}
    return None


def _events_for(day: date, settings: Dict, tz: str) -> List[Tuple[str, str]]:
    cfg = _find_module(settings, ["Agenda", "Calendar"])
    if not cfg:
        return []
    urls = cfg.get("ical_urls") or []
    files = cfg.get("ical_files") or []
    urls = [urls] if isinstance(urls, str) else urls
    files = [files] if isinstance(files, str) else files

    import requests
    import recurring_ical_events
    from icalendar import Calendar
    from zoneinfo import ZoneInfo

    cals = []
    for url in urls:
        if url:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            cals.append(Calendar.from_ical(r.text))
    for path in files:
        if path:
            with open(path, encoding="utf-8") as f:
                cals.append(Calendar.from_ical(f.read()))

    zone = ZoneInfo(tz)
    items = []
    for cal in cals:
        for ev in recurring_ical_events.of(cal).at(day):
            start = ev.get("DTSTART")
            if start is None:
                continue
            value = start.dt
            title = str(ev.get("SUMMARY", "")).strip()
            if isinstance(value, datetime):
                local = value.astimezone(zone) if value.tzinfo else value
                items.append((local.strftime("%H:%M"), title, local.strftime("%H%M")))
            else:
                items.append(("ganztägig", title, "0000"))
    items.sort(key=lambda i: (i[2] != "0000", i[2], i[1]))
    return [(t, title) for t, title, _ in items]


def _weather_for(day: date, settings: Dict, tz: str) -> Optional[Dict]:
    cfg = _find_module(settings, ["Weather", "Fullweather"])
    if not cfg or not cfg.get("api_key") or not cfg.get("location"):
        return None
    from inkycal.utils.openweathermap_wrapper import OpenWeatherMap
    owm = OpenWeatherMap(api_key=cfg["api_key"], city_id=cfg["location"],
                         language=cfg.get("language", "de"), tz_name=tz)
    days_ahead = (day - date.today()).days
    return owm.get_forecast_for_day(max(0, days_ahead))


def render(settings: Dict, size: Tuple[int, int], font_enum, tz: str,
           now: Optional[datetime] = None, until: Optional[datetime] = None) -> Image.Image:
    """Draw the night screen. Network problems only leave parts out."""
    from inkycal.utils.canvas import Canvas
    from inkycal.utils.enums import FONTS

    now = now or datetime.now()
    # Everything on the night screen is about the coming day (the day the night ends),
    # so it stays correct whether you look at it before or after midnight.
    morning = (until or now).date()

    width, height = size
    pad = 30
    inner = width - 2 * pad
    canvas = Canvas((width, height), font_enum, 18)
    y = int(height * 0.12)

    def text(line, size_px, h, align="center"):
        nonlocal y
        c = Canvas((inner, h), font_enum, size_px)
        c.write((0, 0), (inner, h), line, alignment=align)
        canvas.image_black.paste(c.image_black, (pad, y))
        y += h

    # Date of the coming day
    text(WEEKDAYS_DE[morning.weekday()], 40, 60)
    text(f"{morning.day}. {MONTHS_DE[morning.month - 1]}", 30, 50)
    y += 30
    draw = ImageDraw.Draw(canvas.image_black)
    draw.line((pad + inner // 4, y, pad + 3 * inner // 4, y), fill="black", width=2)
    y += 40

    # Weather for the morning day
    try:
        w = _weather_for(morning, settings, tz)
    except Exception:
        logger.exception("Night screen: weather not available")
        w = None
    if w:
        code = str(w.get("icon", ""))[:2]
        icon = WEATHER_ICONS.get(code)
        if icon:
            c = Canvas((inner, 90), FONTS.weather_icons, 70)
            c.write((0, 0), (inner, 90), icon, alignment="center")
            canvas.image_black.paste(c.image_black, (pad, y))
            y += 95
        desc = WEATHER_DE.get(code, "")
        text(f"{round(w['temp_min'])}° / {round(w['temp_max'])}°", 26, 40)
        rain = w.get("precip_mm") or 0
        line = desc + (f" · {rain:.0f} mm" if rain >= 1 else "")
        if line:
            text(line, 20, 32)
        y += 30

    # Events of the morning day
    try:
        events = _events_for(morning, settings, tz)
    except Exception:
        logger.exception("Night screen: calendar not available")
        events = None
    if events is not None:
        text("Termine:" if events else "Keine Termine", 22, 36, align="left")
        for t, title in events[:3]:
            if y + 34 > height - pad:
                break
            text(f"{t}   {title}", 20, 34, align="left")
        if len(events) > 3 and y + 30 <= height - pad:
            text(f"+ {len(events) - 3} weitere", 18, 30, align="left")

    # Small footer
    footer = "Nachtmodus" + (f" bis {until:%H:%M}" if until else "")
    c = Canvas((inner, 26), font_enum, 14)
    c.write((0, 0), (inner, 26), footer, alignment="center")
    canvas.image_black.paste(c.image_black, (pad, height - pad - 26))

    return canvas.image_black
