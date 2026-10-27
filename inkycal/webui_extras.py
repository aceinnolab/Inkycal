"""Extra features for the Inkycal local web UI.

Kept in a separate file so the upstream ``webui.py`` only needs a few hooks:

* live preview of the last rendered image, with module outlines
* height/width check of the layout
* settings editor grouped per module, with checkboxes, dropdowns and list fields
* add / remove / reorder modules
* named layouts (save, load, delete)
* power controls (refresh now, reboot, shut down)
* hideable cards (remembered in the browser)
"""

from __future__ import annotations

import html
import importlib
import json
import re
import subprocess
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from inkycal.display.supported_models import supported_models
from inkycal.settings import Settings

_settings = Settings()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LAYOUT_DIR = PROJECT_ROOT / "layouts"
IMAGE_FOLDER = Path(_settings.IMAGE_FOLDER)

# Actions handled by this file (dispatched from webui.do_POST)
ACTIONS = {
    "settings_form",
    "layout_save",
    "layout_load",
    "layout_delete",
    "power_refresh",
    "power_reboot",
    "power_shutdown",
    "night_on",
    "night_off",
    "update_restart",
}


class _Outcome:
    """Duck-typed stand-in for webui.ActionOutcome (message + sudo_required)."""

    def __init__(self, message: str, sudo_required: bool = False):
        self.message = message
        self.sudo_required = sudo_required


def _webui():
    # Imported lazily to avoid a circular import (webui imports this file).
    from inkycal import webui
    return webui


# ---------------------------------------------------------------------------
# Screen + module metadata
# ---------------------------------------------------------------------------
def screen_size(settings_data: Dict[str, object]) -> Tuple[int, int]:
    """Canvas size Inkycal draws on (portrait: width < height)."""
    model = str(settings_data.get("model", ""))
    w, h = supported_models.get(model, (800, 480))
    # Inkycal always renders in vertical mode (see main._assemble)
    return min(w, h), max(w, h)


_MODULE_CACHE: Dict[str, Optional[type]] = {}


def module_names() -> List[str]:
    try:
        from inkycal.modules import InkycalModuleImporter
        return [m.name for m in InkycalModuleImporter]
    except Exception:
        return []


def module_class(name: str) -> Optional[type]:
    if name in _MODULE_CACHE:
        return _MODULE_CACHE[name]
    cls = None
    try:
        from inkycal.modules import InkycalModuleImporter
        dotted = InkycalModuleImporter[name].value
        mod_name, cls_name = dotted.rsplit(".", 1)
        cls = getattr(importlib.import_module(mod_name), cls_name)
    except Exception:
        cls = None
    _MODULE_CACHE[name] = cls
    return cls


def module_specs(name: str) -> Dict[str, dict]:
    """requires + optional dicts of a module (label, options, default)."""
    cls = module_class(name)
    specs: Dict[str, dict] = {}
    if cls is None:
        return specs
    for attr in ("requires", "optional"):
        for key, spec in (getattr(cls, attr, {}) or {}).items():
            if isinstance(spec, dict):
                specs[key] = dict(spec, required=(attr == "requires"))
    return specs


def default_module_config(name: str, settings_data: Dict[str, object]) -> Dict[str, object]:
    width, _ = screen_size(settings_data)
    config: Dict[str, object] = {
        "size": [min(DEFAULT_MODULE_WIDTH, width), 120],
        "padding_top": 10,
        "padding_bottom": 10,
        "padding_left": 10,
        "padding_right": 10,
        "fontsize": 14,
        "language": settings_data.get("language", "en"),
    }
    for key, spec in module_specs(name).items():
        if "default" in spec:
            config[key] = spec["default"]
        elif spec.get("options"):
            config[key] = spec["options"][0]
        elif spec.get("required"):
            config[key] = [] if key in LIST_KEYS else ""
    if name == "Slideshow":
        from inkycal.webui_photos import PHOTO_DIR
        config["path"] = str(PHOTO_DIR)
    return config


# ---------------------------------------------------------------------------
# Labels, widget hints
# ---------------------------------------------------------------------------
LABELS = {
    "size.0": "width (px)",
    "size.1": "height (px)",
    "ical_urls": "calendar URLs (one per line)",
    "ical_files": "calendar files (one per line)",
    "api_key": "API key",
    "padding_x": "padding left/right",
    "padding_y": "padding top/bottom",
    "offset_x": "shift right (+) / left (-)",
    "offset_y": "shift down (+) / up (-)",
    "padding_top": "padding top",
    "padding_bottom": "padding bottom",
    "padding_left": "padding left",
    "padding_right": "padding right",
    "fontsize": "font size",
    "update_interval": "update interval (min)",
    "calibration_hours": "calibration hours",
    "image_hash": "only refresh when something changed",
    "info_section": "info bar at the bottom",
    "info_section_height": "info bar height (px)",
    "border_around_modules": "draw borders around modules",
    "walk_minutes": "walk to station (min)",
    "relative_time": "show 'in x min' instead of clock time",
    "lines": "only these lines (one per line, empty = all)",
    "show_platform": "show platform",
    "big_next": "big 'next train' line on top",
    "night_mode": "night mode on schedule",
    "night_start": "night starts at",
    "night_end": "night ends at",
}

FONT_CHOICES = [
    "noto_sans_semicondensed_medium",
    "noto_sans_semicondensed",
    "noto_sans_semicondensed_semibold",
    "noto_sans_ui_regular",
    "noto_sans_ui_bold",
    "atkinson_hyperlegible",
    "atkinson_hyperlegible_bold",
]

GENERAL_OPTIONS: Dict[str, List[object]] = {
    "orientation": [0, 180],
    "font": FONT_CHOICES,
    "text_rendering": ["smooth", "crisp"],
}
MODULE_OPTIONS: Dict[str, List[object]] = {
    "font": [""] + FONT_CHOICES,
}

# Friendly names shown in dropdowns (the value saved stays the same)
OPTION_LABELS = {
    "": "same as general setting",
    "noto_sans_semicondensed_medium": "Noto Sans Medium (Inkycal default)",
    "noto_sans_semicondensed": "Noto Sans Regular (thinner)",
    "noto_sans_semicondensed_semibold": "Noto Sans SemiBold",
    "noto_sans_ui_regular": "Noto Sans UI (wider)",
    "noto_sans_ui_bold": "Noto Sans UI Bold",
    "atkinson_hyperlegible": "Atkinson Hyperlegible (very readable)",
    "atkinson_hyperlegible_bold": "Atkinson Hyperlegible Bold",
    "smooth": "smooth (Inkycal default)",
    "crisp": "crisp (sharpest on e-paper)",
}

GENERAL_HINTS = {
    "night_mode": "Show a simple night screen between start and end, no refreshes in between.",
    "night_start": "Time like 23:00",
    "night_end": "Time like 06:00. The button in the Power card also ends a night started by hand.",
    "font": "Font for all modules. A module can pick its own font in its section.",
    "text_rendering": "Crisp draws text without grey edges, which looks sharper on e-paper.",
}

# Keys that hold a list of plain values (edited as one value per line)
LIST_KEYS = {"ical_urls", "ical_files", "lines", "calibration_hours", "feed_urls", "birthdays"}
INT_LIST_KEYS = {"calibration_hours"}
COMMA_SPLIT_KEYS = {"lines", "calibration_hours"}
SECRET_KEYS = {"api_key", "api_key_owm", "token", "todoist_api_key"}

GENERAL_ORDER = [
    "model", "update_interval", "orientation", "language", "font", "text_rendering",
    "night_mode", "night_start", "night_end", "image_hash",
    "border_around_modules", "info_section", "info_section_height", "calibration_hours",
]
MODULE_ORDER = ["size", "padding_top", "padding_bottom", "padding_left", "padding_right", "font", "fontsize",
                "language"]
DEFAULT_MODULE_WIDTH = 440
_LEGACY_PADDING = ("padding_x", "padding_y", "offset_x", "offset_y")


def sides_view(cfg: Dict[str, object]) -> Dict[str, object]:
    """Module config with padding_x/padding_y/offset_x/offset_y turned into the four sides."""
    def num(key):
        try:
            return int(cfg.get(key) or 0)
        except (TypeError, ValueError):
            return 0
    px, py, ox, oy = num("padding_x"), num("padding_y"), num("offset_x"), num("offset_y")
    view = {k: v for k, v in cfg.items() if k not in _LEGACY_PADDING}
    view.setdefault("padding_left", max(0, px + ox))
    view.setdefault("padding_right", max(0, px - ox))
    view.setdefault("padding_top", max(0, py + oy))
    view.setdefault("padding_bottom", max(0, py - oy))
    view.setdefault("font", "")
    return view


def drop_legacy_padding(cfg: Dict[str, object]) -> None:
    """Once the four sides are saved, the old keys would only double-shift the content."""
    if all(k in cfg for k in ("padding_left", "padding_right", "padding_top", "padding_bottom")):
        for key in _LEGACY_PADDING:
            cfg.pop(key, None)


def _label(rel: Tuple[str, ...]) -> str:
    joined = ".".join(rel)
    if joined in LABELS:
        return LABELS[joined]
    return LABELS.get(rel[-1], rel[-1].replace("_", " "))


def _path_str(path: Tuple[object, ...]) -> str:
    return ".".join(str(p) for p in path)


def _is_scalar(v: object) -> bool:
    return v is None or isinstance(v, (bool, int, float, str))


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------
def _field(path: Tuple[object, ...], rel: Tuple[str, ...], value: object,
           options: Optional[List[object]] = None, hint: str = "", css: str = "") -> str:
    row = _field_row(path, rel, value, options=options, hint=hint, css=css)
    if hint:
        row += f"<div class='kv-hint'>{html.escape(hint)}</div>"
    return row


def _field_row(path: Tuple[object, ...], rel: Tuple[str, ...], value: object,
           options: Optional[List[object]] = None, hint: str = "", css: str = "") -> str:
    key = rel[-1] if rel else ""
    p = _path_str(path)
    pe = html.escape(p)
    fid = "fld_" + re.sub(r"[^A-Za-z0-9_]", "_", p)
    label = html.escape(_label(rel))
    title = html.escape(hint or p)
    extra_cls = f" {css}" if css else ""

    # list of plain values -> textarea, one per line
    if isinstance(value, list) or (value is None and key in LIST_KEYS):
        items = value or []
        if key in INT_LIST_KEYS or (items and all(isinstance(i, int) and not isinstance(i, bool) for i in items)):
            kind = "list:int"
        elif items and all(isinstance(i, float) for i in items):
            kind = "list:float"
        else:
            kind = "list:str"
        if value is None:
            kind += ":nullable"
        text = "\n".join(str(i) for i in items)
        rows = max(2, min(6, len(items) + 1))
        return (
            f"<div class='kv-row kv-wide'><label class='kv-key' for='{fid}' title='{title}'>{label}</label>"
            f"<input type='hidden' name='t:{pe}' value='{kind}'>"
            f"<textarea id='{fid}' class='kv-value kv-list' name='f:{pe}' rows='{rows}'>{html.escape(text)}</textarea></div>"
        )

    if isinstance(value, bool):
        return (
            f"<div class='kv-row'><label class='kv-key' for='{fid}' title='{title}'>{label}</label>"
            f"<input type='hidden' name='t:{pe}' value='bool'>"
            f"<span class='kv-check'><input id='{fid}' type='checkbox' name='f:{pe}' value='1' {'checked' if value else ''}></span></div>"
        )

    if options:
        opts = list(options)
        if value not in opts:
            opts = [value] + opts
        kind = "int" if all(isinstance(o, int) and not isinstance(o, bool) for o in opts) else "str"
        option_html = "".join(
            f"<option value='{html.escape(str(o))}' {'selected' if o == value else ''}>"
            f"{html.escape(OPTION_LABELS.get(str(o), str(o)))}</option>"
            for o in opts
        )
        return (
            f"<div class='kv-row'><label class='kv-key' for='{fid}' title='{title}'>{label}</label>"
            f"<input type='hidden' name='t:{pe}' value='{kind}'>"
            f"<select id='{fid}' class='kv-value' name='f:{pe}'>{option_html}</select></div>"
        )

    if isinstance(value, int):
        kind, itype, step = "int", "number", "1"
    elif isinstance(value, float):
        kind, itype, step = "float", "number", "any"
    elif value is None:
        kind, itype, step = "null", "text", ""
    else:
        kind, itype, step = "str", "text", ""

    shown = "" if value is None else str(value)
    is_secret = key in SECRET_KEYS
    if is_secret:
        itype = "password"
    wide = " kv-wide" if len(shown) > 40 and not is_secret else ""
    step_attr = f" step='{step}'" if step else ""
    secret_js = " onfocus=\"this.type='text'\" onblur=\"this.type='password'\"" if is_secret else ""
    placeholder = " placeholder='empty'" if value is None else ""
    return (
        f"<div class='kv-row{wide}'><label class='kv-key' for='{fid}' title='{title}'>{label}</label>"
        f"<input type='hidden' name='t:{pe}' value='{kind}'>"
        f"<input id='{fid}' class='kv-value{extra_cls}' type='{itype}'{step_attr} name='f:{pe}' "
        f"value='{html.escape(shown)}'{placeholder}{secret_js}></div>"
    )


def _fields_for(container: Dict[str, object], base: Tuple[object, ...], order: List[str],
                specs: Optional[Dict[str, dict]] = None, general: bool = False) -> List[str]:
    out: List[str] = []
    specs = specs or {}

    def sort_key(k: str):
        return (0, order.index(k)) if k in order else (1, k)

    for key in sorted(container.keys(), key=sort_key):
        value = container[key]
        spec = specs.get(key, {})
        hint = str(spec.get("label", "")) or (GENERAL_HINTS.get(key, "") if general else "")
        options = spec.get("options") or (GENERAL_OPTIONS.get(key) if general else MODULE_OPTIONS.get(key))
        if general and key == "model":
            options = sorted(supported_models.keys())

        if key == "size" and isinstance(value, list) and len(value) == 2:
            out.append(_field(base + (key, 0), (key, "0"), value[0], css="js-w"))
            out.append(_field(base + (key, 1), (key, "1"), value[1], css="js-h"))
        elif isinstance(value, dict):
            out.extend(_fields_for(value, base + (key,), order, specs))
        elif isinstance(value, list) and not all(_is_scalar(v) for v in value):
            continue  # nested structures: JSON editor only
        else:
            out.append(_field(base + (key,), (key,), value, options=options, hint=hint))
    return out


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def render_settings_card(settings_data: Dict[str, object]) -> str:
    sw, sh = screen_size(settings_data)
    modules = settings_data.get("modules", []) if isinstance(settings_data.get("modules"), list) else []
    general = {k: v for k, v in settings_data.items() if k != "modules"}
    general.setdefault("font", "noto_sans_semicondensed_medium")
    general.setdefault("text_rendering", "smooth")
    general.setdefault("night_mode", False)
    general.setdefault("night_start", "23:00")
    general.setdefault("night_end", "06:00")

    parts: List[str] = [
        "<section class='card' style='margin-top: 1rem;' data-card='settings'>",
        "<h2>Settings</h2>",
        f"<div id='heightBar' class='height-bar' data-screen-w='{sw}' data-screen-h='{sh}'></div>",
        "<form method='post' id='settingsForm'>",
        "<input type='hidden' name='action' value='settings_form'>",
        "<details class='kv-section' data-key='general'><summary>General</summary><div class='kv-grid'>",
    ]
    parts.extend(_fields_for(general, (), GENERAL_ORDER, general=True))
    parts.append("</div></details>")

    for index, mod in enumerate(modules):
        if not isinstance(mod, dict):
            continue
        name = str(mod.get("name", f"Module {index + 1}"))
        cfg = mod.get("config") if isinstance(mod.get("config"), dict) else {}
        size = cfg.get("size") or ["?", "?"]
        known = name in module_names()
        warn = "" if known else " <span class='kv-warn'>unknown module</span>"
        parts.append(
            f"<details class='kv-section kv-module' data-key='mod-{html.escape(name)}-{index}' data-index='{index}'>"
            f"<summary>{index + 1} · {html.escape(name)}{warn}"
            f"<span class='kv-meta js-meta'>{html.escape(str(size[0]))} × {html.escape(str(size[1]))} px</span></summary>"
            "<div class='mod-tools'>"
            f"<button type='submit' name='op' value='up:{index}' class='small' {'disabled' if index == 0 else ''}>▲ Up</button>"
            f"<button type='submit' name='op' value='down:{index}' class='small' {'disabled' if index == len(modules) - 1 else ''}>▼ Down</button>"
            f"<button type='submit' name='op' value='remove:{index}' class='small danger' "
            f"onclick=\"return confirm('Remove module {html.escape(name)}?')\">✕ Remove</button>"
            "</div><div class='kv-grid'>"
        )
        parts.extend(_fields_for(sides_view(cfg), ("modules", index, "config"), MODULE_ORDER, module_specs(name)))
        parts.append("</div></details>")

    add_options = "".join(f"<option value='{html.escape(n)}'>{html.escape(n)}</option>" for n in module_names())
    parts.append(
        "<div class='add-module'>"
        f"<select name='new_module'>{add_options}</select>"
        "<button type='submit' name='op' value='add' class='secondary'>+ Add module</button>"
        "</div>"
        "<div class='button-row'>"
        "<button type='submit' name='op' value='save'>Save settings</button>"
        "<button type='submit' name='op' value='save_refresh' class='secondary'>Save &amp; refresh display</button>"
        "</div></form>"
        "<p class='muted'>Lists (calendar URLs, S-Bahn lines…) take one value per line. "
        "Hover a label to see the full setting name or help text.</p>"
        "</section>"
    )
    return "".join(parts)


def _preview_file() -> Optional[Path]:
    for name in ("canvas.png",):
        path = IMAGE_FOLDER / name
        if path.exists():
            return path
    return None


def render_preview_card(settings_data: Dict[str, object]) -> str:
    sw, sh = screen_size(settings_data)
    path = _preview_file()
    if path:
        import time as _t
        stamp = int(path.stat().st_mtime)
        when = _t.strftime("%H:%M:%S", _t.localtime(stamp))
        img = (f"<img id='previewImg' src='/preview.png?t={stamp}' alt='Last rendered image' "
               f"data-stamp='{stamp}'>")
        info = f"Last drawn at <strong id='previewTime'>{when}</strong>"
    else:
        img = "<div class='preview-empty'>No image yet. It appears after the next display update.</div>"
        info = "No image rendered yet"

    # module outlines from current settings (percent of screen)
    boxes = []
    y = 0
    modules = settings_data.get("modules", []) if isinstance(settings_data.get("modules"), list) else []
    for index, mod in enumerate(modules):
        try:
            w, h = (int(v) for v in mod["config"]["size"])
        except Exception:
            continue
        boxes.append(
            f"<div class='pv-box' data-index='{index}' style='top:{y / sh * 100:.3f}%;height:{h / sh * 100:.3f}%;"
            f"width:{w / sw * 100:.3f}%'><span>{index + 1} {html.escape(str(mod.get('name', '')))}</span></div>"
        )
        y += h

    return f"""
    <section class='card preview-card' data-card='preview'>
      <h2>Display preview</h2>
      <div class='preview-wrap'>
        <div class='preview-frame' style='aspect-ratio:{sw} / {sh}'>
          {img}
          <div class='pv-boxes' id='pvBoxes'>{''.join(boxes)}</div>
        </div>
        <div class='preview-side'>
          <p class='muted'>{info}</p>
          <label class='inline'><input type='checkbox' id='pvToggle' checked> show module outlines</label>
          <p class='muted'>Outlines follow the settings below as you type; the image is the last real update
          ({sw} × {sh} px).</p>
          <form method='post'>
            <div class='button-row'>
              <button name='action' value='power_refresh'>Refresh display now</button>
            </div>
          </form>
        </div>
      </div>
    </section>
    """


def _night_html() -> str:
    from inkycal import night_mode
    data = _webui()._read_settings_json()
    active, until, reason = night_mode.status(data)
    start, end = night_mode.schedule(data)
    if active:
        how = "started by button" if reason == "button" else "scheduled"
        state = f"Night mode is <strong>on</strong> ({how}) until {until:%H:%M}."
        button = "<button name='action' value='night_off' class='secondary'>End night mode</button>"
    else:
        if data.get("night_mode"):
            state = f"Night mode is off. Scheduled from {start:%H:%M} to {end:%H:%M}."
        else:
            state = "Night mode is off. No schedule set (General settings)."
        button = "<button name='action' value='night_on'>Night mode now</button>"
    return (f"<h3 class='sub'>Night mode</h3><p class='muted'>{state}</p>"
            f"<form method='post'><div class='button-row'>{button}</div></form>")


def render_tools_cards() -> str:
    layouts = list_layouts()
    if layouts:
        rows = "".join(
            "<div class='layout-row'>"
            f"<span>{html.escape(n)}</span>"
            "<form method='post'>"
            f"<input type='hidden' name='layout_name' value='{html.escape(n)}'>"
            "<button name='action' value='layout_load' class='small'>Load</button>"
            "<button name='action' value='layout_delete' class='small danger' "
            f"onclick=\"return confirm('Delete layout {html.escape(n)}?')\">Delete</button>"
            "</form></div>"
            for n in layouts
        )
    else:
        rows = "<p class='muted'>No layouts saved yet.</p>"

    return f"""
      <section class='card' data-card='power'>
        <h2>Power</h2>
        <form method='post'>
          <div class='button-row'>
            <button name='action' value='power_refresh'>Refresh display now</button>
            <button name='action' value='power_reboot' class='secondary'
              onclick="return confirm('Reboot the Pi? It will be back in about 2 minutes.')">Reboot</button>
            <button name='action' value='power_shutdown' class='danger'
              onclick="return confirm('Shut down the Pi? You need to unplug and replug it to start it again.')">Shut down</button>
          </div>
        </form>
        <p class='muted'>After shutting down, wait until the green LED stops blinking before unplugging.</p>
        {_night_html()}
        {_update_html()}
      </section>

      <section class='card' data-card='layouts'>
        <h2>Layouts</h2>
        {rows}
        <form method='post' class='layout-save'>
          <input name='layout_name' placeholder='Name, e.g. Morning' maxlength='40' required>
          <button name='action' value='layout_save'>Save current</button>
        </form>
        <p class='muted'>Loading a layout replaces settings.json and refreshes the display.</p>
      </section>
    """


# ---------------------------------------------------------------------------
# Settings form handling
# ---------------------------------------------------------------------------
def _parse_path(p: str) -> List[object]:
    return [int(s) if s.isdigit() else s for s in p.split(".")] if p else []


def _set(container: object, path: List[object], value: object) -> None:
    cur = container
    for seg in path[:-1]:
        cur = cur[seg]  # type: ignore[index]
    cur[path[-1]] = value  # type: ignore[index]


def _convert(kind: str, raw: Optional[str], key: str) -> object:
    if kind == "bool":
        return raw is not None
    raw = raw if raw is not None else ""
    if kind.startswith("list:"):
        parts = kind.split(":")
        elem = parts[1]
        nullable = "nullable" in parts
        text = raw.replace("\r", "")
        if key in COMMA_SPLIT_KEYS or elem in ("int", "float"):
            text = text.replace(",", "\n")
        items = [s.strip() for s in text.split("\n") if s.strip()]
        if not items and nullable:
            return None
        if elem == "int":
            return [int(float(i)) for i in items]
        if elem == "float":
            return [float(i) for i in items]
        return items
    if kind == "int":
        return int(float(raw.strip()))
    if kind == "float":
        return float(raw.strip())
    if kind == "null":
        s = raw.strip()
        if s == "" or s.lower() in ("null", "none"):
            return None
        try:
            return json.loads(s)
        except Exception:
            return s
    return raw


def apply_form(data: Dict[str, object], form: Dict[str, List[str]]) -> None:
    """Write submitted editor fields into the settings dict (raises on bad input)."""
    for name, kinds in form.items():
        if not name.startswith("t:"):
            continue
        path_s = name[2:]
        raw_list = form.get("f:" + path_s)
        raw = raw_list[0] if raw_list else None
        path = _parse_path(path_s)
        key = str(path[-1]) if path else ""
        if isinstance(path[-1], int) and len(path) > 1:
            key = str(path[-2])
        try:
            _set(data, path, _convert(kinds[0], raw, key))
        except (KeyError, IndexError, TypeError):
            continue  # field no longer exists (e.g. module removed)
        except ValueError as error:
            raise ValueError(f"'{_label(tuple(str(p) for p in path[-2:]))}': {error}")


def _renumber(modules: List[dict]) -> None:
    for i, m in enumerate(modules):
        if isinstance(m, dict):
            m["position"] = i + 1


def _form_module_indexes(form: Dict[str, List[str]]) -> set:
    found = set()
    for name in form:
        if name.startswith("t:modules."):
            part = name[len("t:modules."):].split(".", 1)[0]
            if part.isdigit():
                found.add(int(part))
    return found


def handle_settings_form(form: Dict[str, List[str]], sudo_password: str = ""):
    W = _webui()
    data = W._read_settings_json()
    if not isinstance(data, dict) or not data:
        return _Outcome("Settings save failed: settings.json could not be read. Nothing was changed - "
                        "reload the page and try again.")

    # Safety: the page must match the file. If modules the page knows about are missing
    # in the file (file changed in the meantime, or could not be read), save nothing.
    current = data.get("modules") if isinstance(data.get("modules"), list) else []
    expected = _form_module_indexes(form)
    if expected and max(expected) >= len(current):
        return _Outcome("Settings save failed: settings.json changed since this page was loaded. "
                        "Nothing was changed - reload the page and try again.")

    try:
        apply_form(data, form)
        for mod in data.get("modules", []) or []:
            if isinstance(mod, dict) and isinstance(mod.get("config"), dict):
                drop_legacy_padding(mod["config"])
    except ValueError as error:
        return _Outcome(f"Settings save failed: {error}")

    op = form.get("op", ["save"])[0]
    modules = data.setdefault("modules", [])
    msg = "Settings saved."

    try:
        if op.startswith(("up:", "down:", "remove:")):
            kind, idx_s = op.split(":", 1)
            idx = int(idx_s)
            if kind == "up" and idx > 0:
                modules[idx - 1], modules[idx] = modules[idx], modules[idx - 1]
                msg = "Module moved up."
            elif kind == "down" and idx < len(modules) - 1:
                modules[idx + 1], modules[idx] = modules[idx], modules[idx + 1]
                msg = "Module moved down."
            elif kind == "remove":
                removed = modules.pop(idx)
                msg = f"Module {removed.get('name', '')} removed."
        elif op == "add":
            name = form.get("new_module", [""])[0]
            if name not in module_names():
                return _Outcome(f"Add module failed: unknown module '{name}'.")
            modules.append({"position": len(modules) + 1, "name": name,
                            "config": default_module_config(name, data)})
            msg = f"Module {name} added at the bottom. Adjust its height, then save."
    except (ValueError, IndexError):
        return _Outcome("Settings save failed: invalid module operation.")

    _renumber(modules)
    backup_settings()
    outcome = W._write_settings_json(data, "Settings save failed", sudo_password=sudo_password)
    if outcome:
        return outcome

    if op == "save_refresh":
        r = power_action("power_refresh", sudo_password)
        if r.sudo_required or r.message.startswith("Refresh failed"):
            return _Outcome("Settings saved. " + r.message, r.sudo_required)
        msg = "Settings saved, display is refreshing."
    return _Outcome(msg)


# ---------------------------------------------------------------------------
# Layouts
# ---------------------------------------------------------------------------
def _safe_name(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9 _\-äöüÄÖÜß]", "", name).strip()
    return name[:40]


def list_layouts() -> List[str]:
    if not LAYOUT_DIR.exists():
        return []
    named = sorted(p.stem for p in LAYOUT_DIR.glob("*.json") if not p.stem.startswith("Backup "))
    backups = sorted((p.stem for p in LAYOUT_DIR.glob("Backup *.json")), reverse=True)
    return named + backups


BACKUPS_TO_KEEP = 10


def backup_settings() -> None:
    """Copy the current settings.json to layouts/'Backup <date time>.json' before it is changed."""
    try:
        import time as _t
        W = _webui()
        text = W._read_settings_text()
        parsed = json.loads(text)
        if not isinstance(parsed, dict) or not parsed.get("modules"):
            return  # never back up an empty/broken file over good backups
        LAYOUT_DIR.mkdir(parents=True, exist_ok=True)
        newest = sorted(LAYOUT_DIR.glob("Backup *.json"))
        if newest and newest[-1].read_text(encoding="utf-8") == text:
            return  # unchanged since the last backup
        (LAYOUT_DIR / f"Backup {_t.strftime('%Y-%m-%d %H-%M-%S')}.json").write_text(text, encoding="utf-8")
        for old in sorted(LAYOUT_DIR.glob("Backup *.json"))[:-BACKUPS_TO_KEEP]:
            old.unlink()
    except Exception:
        pass  # a failed backup must never block saving


def handle_layout(action: str, form: Dict[str, List[str]], sudo_password: str = ""):
    W = _webui()
    name = _safe_name(form.get("layout_name", [""])[0])
    if not name:
        return _Outcome("Layout: please enter a name (letters, numbers, spaces, - and _).")
    path = LAYOUT_DIR / f"{name}.json"

    if action == "layout_save":
        text = W._read_settings_text()
        try:
            if not json.loads(text).get("modules"):
                return _Outcome("Layout not saved: the current settings have no modules.")
        except Exception:
            return _Outcome("Layout not saved: settings.json could not be read.")
        LAYOUT_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return _Outcome(f"Layout '{name}' saved.")

    if action == "layout_delete":
        if path.exists():
            path.unlink()
            return _Outcome(f"Layout '{name}' deleted.")
        return _Outcome(f"Layout '{name}' not found.")

    if action == "layout_load":
        if not path.exists():
            return _Outcome(f"Layout '{name}' not found.")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            return _Outcome(f"Layout load failed: invalid JSON ({error})")
        backup_settings()
        outcome = W._write_settings_json(data, "Layout load failed", sudo_password=sudo_password)
        if outcome:
            return outcome
        r = power_action("power_refresh", sudo_password)
        if r.sudo_required or r.message.startswith("Refresh failed"):
            return _Outcome(f"Layout '{name}' loaded. " + r.message, r.sudo_required)
        return _Outcome(f"Layout '{name}' loaded, display is refreshing.")

    return _Outcome("Unknown layout action.")


# ---------------------------------------------------------------------------
# Power
# ---------------------------------------------------------------------------
def _sudo_ok(sudo_password: str) -> Optional[str]:
    """Return None if sudo works, else an error string ('password' if one is needed)."""
    W = _webui()
    try:
        code, out, err = W._run_sudo_command(["true"], sudo_password=sudo_password, timeout=10)
    except W.SudoPasswordRequiredError:
        return "password"
    if code != 0:
        return "password" if W._is_sudo_password_error(err, out) else (err or out or "sudo failed")
    return None


def _delayed(command: List[str], sudo_password: str, delay: float = 2.0) -> None:
    def run():
        if sudo_password:
            p = subprocess.Popen(["sudo", "-S", "-p", "", *command], stdin=subprocess.PIPE, text=True)
            p.communicate(sudo_password + "\n")
        else:
            subprocess.Popen(["sudo", "-n", *command])
    threading.Timer(delay, run).start()


def _git(*args: str, timeout: int = 30) -> Tuple[int, str, str]:
    try:
        r = subprocess.run(["git", *args], cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as error:
        return 1, "", str(error)


def _update_html() -> str:
    code, out, _ = _git("log", "-1", "--format=%h|%cd", "--date=format:%d.%m.%Y %H:%M")
    version = ""
    if code == 0 and "|" in out:
        commit, when = out.split("|", 1)
        version = f"Installed version: <code>{html.escape(commit)}</code> from {html.escape(when)}"
    return (
        "<h3 class='sub'>Update</h3>"
        f"<p class='muted'>{version}</p>"
        "<form method='post'><div class='button-row'>"
        "<button name='action' value='update_restart' "
        "onclick=\"return confirm('Download the latest version and restart Inkycal and this page?')\">"
        "Update &amp; restart</button></div></form>"
    )


def update_and_restart(sudo_password: str = ""):
    """git pull --ff-only, then restart Inkycal and the web UI if something changed."""
    problem = _sudo_ok(sudo_password)
    if problem == "password":
        return _Outcome("Update requires sudo password.", sudo_required=True)
    if problem:
        return _Outcome(f"Update failed: {problem}")

    _, before, _ = _git("rev-parse", "HEAD")
    code, out, err = _git("pull", "--ff-only", timeout=120)
    if code != 0:
        return _Outcome(f"Update failed: {err or out or 'unknown error'}")
    _, after, _ = _git("rev-parse", "HEAD")
    if before == after:
        return _Outcome("Already up to date - nothing to do.")

    W = _webui()
    # restart after the answer was sent (restarting the web UI ends this process)
    _delayed(["systemctl", "restart", W.SERVICE_NAME, "inkycal-webui.service"], sudo_password)
    _, log, _ = _git("log", "--format=%s", f"{before}..{after}")
    changes = "; ".join(log.splitlines()[:5])
    return _Outcome(f"Updated, restarting - this page reloads in about 20 seconds. New: {changes}")


def power_action(action: str, sudo_password: str = ""):
    W = _webui()
    if action == "power_refresh":
        try:
            code, out, err = W._run_sudo_command(["systemctl", "restart", W.SERVICE_NAME],
                                                 sudo_password=sudo_password)
        except W.SudoPasswordRequiredError:
            return _Outcome("Refresh requires sudo password.", sudo_required=True)
        if code == 0:
            return _Outcome("Display is refreshing (takes about 20 seconds).")
        if W._is_sudo_password_error(err, out):
            return _Outcome("Refresh failed: incorrect sudo password.", sudo_required=True)
        return _Outcome(f"Refresh failed: {err or out or 'unknown error'}")

    if action in ("power_reboot", "power_shutdown"):
        problem = _sudo_ok(sudo_password)
        if problem == "password":
            return _Outcome(f"{'Reboot' if action == 'power_reboot' else 'Shutdown'} requires sudo password.",
                            sudo_required=True)
        if problem:
            return _Outcome(f"Failed: {problem}")
        _delayed(["systemctl", "reboot" if action == "power_reboot" else "poweroff"], sudo_password)
        if action == "power_reboot":
            return _Outcome("Rebooting… reload this page in about 2 minutes.")
        return _Outcome("Shutting down… wait until the green LED stops blinking, then unplug.")

    return _Outcome("Unknown power action.")


def night_action(action: str, sudo_password: str = ""):
    from inkycal import night_mode
    data = _webui()._read_settings_json()
    if action == "night_on":
        until = night_mode.start_now(data)
        msg = f"Night mode on until {until:%H:%M}."
    else:
        night_mode.end_now(data)
        msg = "Night mode ended."
    r = power_action("power_refresh", sudo_password)
    if r.sudo_required or r.message.startswith("Refresh failed"):
        return _Outcome(f"{msg} {r.message}", r.sudo_required)
    return _Outcome(f"{msg} The display updates in about 20 seconds.")


def handle(action: str, form: Dict[str, List[str]], sudo_password: str = ""):
    if action.startswith("night_"):
        return night_action(action, sudo_password)
    if action == "update_restart":
        return update_and_restart(sudo_password)
    if action == "settings_form":
        return handle_settings_form(form, sudo_password)
    if action.startswith("layout_"):
        return handle_layout(action, form, sudo_password)
    if action.startswith("power_"):
        return power_action(action, sudo_password)
    return _Outcome("Unknown action.")


# ---------------------------------------------------------------------------
# GET routes
# ---------------------------------------------------------------------------
def preview_png() -> Optional[bytes]:
    path = _preview_file()
    return path.read_bytes() if path else None


def preview_stamp() -> Dict[str, str]:
    path = _preview_file()
    if not path:
        return {"stamp": ""}
    import time as _t
    stamp = int(path.stat().st_mtime)
    return {"stamp": str(stamp), "time": _t.strftime("%H:%M:%S", _t.localtime(stamp))}


def sudo_passthrough_fields(form: Optional[Dict[str, List[str]]]) -> str:
    """Hidden inputs so the sudo password dialog can resend the whole form."""
    if not form:
        return ""
    out = []
    for name, values in form.items():
        if name in ("action", "sudo_password"):
            continue
        for v in values:
            out.append(f"<input type='hidden' name='{html.escape(name)}' value='{html.escape(v)}'>")
    return "".join(out)


# ---------------------------------------------------------------------------
# CSS + JS injected into the page
# ---------------------------------------------------------------------------
CSS = """
    .kv-section { border: 1px solid var(--border); border-radius: 12px; margin: 0.6rem 0; background: #fff; }
    .kv-section > summary { cursor: pointer; padding: 0.7rem 0.9rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem; list-style: none; }
    .kv-section > summary::-webkit-details-marker { display: none; }
    .kv-section > summary::before { content: '▸'; color: var(--muted); }
    .kv-section[open] > summary::before { content: '▾'; }
    .kv-meta { margin-left: auto; font-weight: 400; color: var(--muted); font-size: 0.88rem; }
    .kv-warn { color: var(--err); font-weight: 600; font-size: 0.82rem; }
    .kv-section > .kv-grid { padding: 0 0.9rem 0.9rem; }
    .kv-wide { grid-template-columns: 1fr !important; }
    .kv-check { display: flex; align-items: center; }
    .kv-check input { width: 1.4rem; height: 1.4rem; accent-color: var(--accent); }
    textarea.kv-list { min-height: 0; }
    h3.sub { margin: 1rem 0 0.2rem; font-size: 0.98rem; }
    .kv-hint { color: var(--muted); font-size: 0.82rem; margin: -0.25rem 0 0.2rem 0.2rem; }
    .mod-tools { display: flex; gap: 0.4rem; padding: 0 0.9rem 0.7rem; flex-wrap: wrap; }
    button.small { padding: 0.35rem 0.6rem; font-size: 0.85rem; }
    button.danger { background: var(--err); border-color: var(--err); }
    button:disabled { opacity: 0.4; cursor: default; filter: none; box-shadow: none; }
    .add-module { display: flex; gap: 0.5rem; margin: 0.8rem 0 0.2rem; }
    .add-module select { flex: 1; }
    .height-bar { padding: 0.55rem 0.8rem; border-radius: 10px; font-weight: 600; margin-bottom: 0.4rem; background: #ecfdf5; color: var(--ok); border: 1px solid #a7f3d0; }
    .height-bar.bad { background: #fef2f2; color: var(--err); border-color: #fecaca; }
    .preview-card { margin-bottom: 1rem; }
    .preview-wrap { display: grid; grid-template-columns: minmax(180px, 320px) 1fr; gap: 1rem; align-items: start; }
    .preview-frame { position: relative; width: 100%; background: #fff; border: 2px solid #1a1a18; border-radius: 6px; overflow: hidden; }
    .preview-frame img { width: 100%; height: 100%; display: block; image-rendering: pixelated; }
    .preview-empty { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; text-align: center; padding: 1rem; color: var(--muted); }
    .pv-boxes { position: absolute; inset: 0; pointer-events: none; }
    .pv-boxes.off { display: none; }
    .pv-box { position: absolute; left: 0; outline: 2px dashed rgba(217, 119, 6, 0.85); outline-offset: -2px; background: rgba(217, 119, 6, 0.06); }
    .pv-box span { position: absolute; right: 2px; top: 2px; background: rgba(217, 119, 6, 0.9); color: #fff; font-size: 0.7rem; padding: 0 0.3rem; border-radius: 4px; }
    .pv-box.over { outline-color: var(--err); background: rgba(220, 38, 38, 0.12); }
    label.inline { display: flex; gap: 0.5rem; align-items: center; font-weight: 500; }
    label.inline input { width: auto; }
    .layout-row { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid var(--border); }
    .layout-row form { display: flex; gap: 0.35rem; }
    .layout-save { display: flex; gap: 0.5rem; margin-top: 0.7rem; }
    .card { position: relative; }
    .card-hide { position: absolute; top: 0.6rem; right: 0.6rem; background: transparent; border: 0; color: var(--muted); padding: 0.1rem 0.4rem; font-size: 1rem; box-shadow: none; }
    .card-hide:hover { color: var(--err); filter: none; box-shadow: none; }
    #hiddenCards { margin: 0 0 0.8rem; }
    #hiddenCards button { margin: 0.2rem 0.3rem 0 0; }
    @media (max-width: 640px) {
      .preview-wrap { grid-template-columns: 1fr; }
      .preview-frame { max-width: 300px; }
    }
"""

JS = """
    (function() {
      // ---- remember which settings sections are open ----
      const KEY_OPEN = 'inkycal-open-sections';
      let openSet = [];
      try { openSet = JSON.parse(localStorage.getItem(KEY_OPEN) || '[]'); } catch (e) {}
      document.querySelectorAll('details.kv-section').forEach(d => {
        if (openSet.includes(d.dataset.key)) d.open = true;
        d.addEventListener('toggle', () => {
          const keys = [...document.querySelectorAll('details.kv-section')].filter(x => x.open).map(x => x.dataset.key);
          try { localStorage.setItem(KEY_OPEN, JSON.stringify(keys)); } catch (e) {}
        });
      });

      // ---- height bar + live outlines ----
      const bar = document.getElementById('heightBar');
      const boxes = document.getElementById('pvBoxes');
      function update() {
        if (!bar) return;
        const sw = +bar.dataset.screenW, sh = +bar.dataset.screenH;
        let total = 0, widest = 0, y = 0;
        const mods = [...document.querySelectorAll('details.kv-module')];
        if (boxes) boxes.innerHTML = '';
        mods.forEach((d, i) => {
          const wIn = d.querySelector('input.js-w'), hIn = d.querySelector('input.js-h');
          const w = wIn ? +wIn.value || 0 : 0, h = hIn ? +hIn.value || 0 : 0;
          total += h; widest = Math.max(widest, w);
          const meta = d.querySelector('.js-meta');
          if (meta) meta.textContent = w + ' × ' + h + ' px';
          if (boxes) {
            const b = document.createElement('div');
            b.className = 'pv-box' + ((y + h > sh || w > sw) ? ' over' : '');
            b.style.top = (y / sh * 100) + '%';
            b.style.height = (h / sh * 100) + '%';
            b.style.width = (Math.min(w, sw) / sw * 100) + '%';
            const name = d.querySelector('summary').childNodes[0].textContent.trim();
            b.innerHTML = '<span></span>';
            b.querySelector('span').textContent = name;
            boxes.appendChild(b);
          }
          y += h;
        });
        const info = document.querySelector('input[name="t:info_section"]');
        const infoOn = document.querySelector('input[name="f:info_section"]');
        const infoH = document.querySelector('input[name="f:info_section_height"]');
        const reserved = (info && infoOn && infoOn.checked && infoH) ? (+infoH.value || 0) : 0;
        const used = total + reserved;
        let text = 'Height: ' + used + ' / ' + sh + ' px';
        if (reserved) text += ' (incl. ' + reserved + ' px info bar)';
        let bad = false;
        if (used > sh) { text += ' — too tall by ' + (used - sh) + ' px!'; bad = true; }
        else { text += ' — ' + (sh - used) + ' px free'; }
        if (widest > sw) { text += ' · a module is wider than the screen (' + widest + ' > ' + sw + ' px)'; bad = true; }
        bar.textContent = text;
        bar.classList.toggle('bad', bad);
      }
      document.querySelectorAll('input.js-w, input.js-h, input[name="f:info_section"], input[name="f:info_section_height"]')
        .forEach(el => el.addEventListener('input', update));
      update();
      const tog = document.getElementById('pvToggle');
      if (tog && boxes) tog.addEventListener('change', () => boxes.classList.toggle('off', !tog.checked));

      // ---- reload preview when a new image was drawn ----
      const img = document.getElementById('previewImg');
      async function checkPreview() {
        try {
          const r = await fetch('/api/preview', { cache: 'no-store' });
          if (!r.ok) return;
          const d = await r.json();
          if (!d.stamp) return;
          if (img && img.dataset.stamp !== d.stamp) {
            img.src = '/preview.png?t=' + d.stamp;
            img.dataset.stamp = d.stamp;
            const t = document.getElementById('previewTime');
            if (t) t.textContent = d.time;
          } else if (!img) { location.reload(); }
        } catch (e) {}
      }
      window.setInterval(checkPreview, 15000);

      // ---- reload after "Update & restart" ----
      const msgEl = document.querySelector('.msg');
      if (msgEl && msgEl.textContent.startsWith('Updated, restarting')) {
        let left = 20;
        const tick = () => {
          if (left <= 0) { location.href = '/'; return; }
          msgEl.textContent = msgEl.textContent.replace(/reloads in (about )?[0-9]+ seconds/, 'reloads in ' + left + ' seconds');
          left -= 1; setTimeout(tick, 1000);
        };
        tick();
      }

      // ---- hideable cards ----
      const KEY_HIDE = 'inkycal-hidden-cards';
      let hidden = [];
      try { hidden = JSON.parse(localStorage.getItem(KEY_HIDE) || '[]'); } catch (e) {}
      const holder = document.createElement('div');
      holder.id = 'hiddenCards';
      const msg = document.querySelector('.msg');
      if (msg) msg.after(holder);
      function saveHidden() { try { localStorage.setItem(KEY_HIDE, JSON.stringify(hidden)); } catch (e) {} }
      function render() {
        holder.innerHTML = '';
        document.querySelectorAll('section.card').forEach(card => {
          const h2 = card.querySelector('h2');
          if (!h2) return;
          const id = h2.textContent.trim();
          card.style.display = hidden.includes(id) ? 'none' : '';
          if (!card.querySelector('.card-hide')) {
            const b = document.createElement('button');
            b.type = 'button'; b.className = 'card-hide'; b.title = 'Hide this card'; b.textContent = '✕';
            b.addEventListener('click', () => { hidden.push(id); saveHidden(); render(); });
            card.appendChild(b);
          }
        });
        if (hidden.length) {
          const label = document.createElement('span');
          label.className = 'muted'; label.textContent = 'Hidden: ';
          holder.appendChild(label);
          hidden.forEach(id => {
            const b = document.createElement('button');
            b.type = 'button'; b.className = 'small secondary'; b.textContent = '+ ' + id;
            b.addEventListener('click', () => { hidden = hidden.filter(x => x !== id); saveHidden(); render(); });
            holder.appendChild(b);
          });
        }
      }
      render();
    })();
"""
