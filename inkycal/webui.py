"""Very small local web UI for monitoring and controlling Inkycal."""

from __future__ import annotations

import html
import io
import json
import os
import platform
import subprocess
import sys
import time
import urllib.parse
from base64 import b64encode
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from zoneinfo import available_timezones

from inkycal.display.supported_models import supported_models
from inkycal.settings import Settings

settings = Settings()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVICE_NAME = os.getenv("INKYCAL_SERVICE_NAME", "inkycal.service")
WEBUI_HOST = os.getenv("INKYCAL_WEBUI_HOST", "127.0.0.1")
WEBUI_PORT = int(os.getenv("INKYCAL_WEBUI_PORT", "8080"))
PAYPAL_URL = os.getenv("INKYCAL_PAYPAL_URL", "https://www.paypal.com/paypalme/Aceinnolab")
HARDWARE_REFRESH_SECONDS = int(os.getenv("INKYCAL_WEBUI_HW_REFRESH_SECONDS", "10"))
PYTHON_BIN = os.getenv("INKYCAL_PYTHON_BIN", str(PROJECT_ROOT / "venv" / "bin" / "python"))
INKY_RUN = os.getenv("INKYCAL_RUNNER", str(PROJECT_ROOT / "inky_run.py"))
SETTINGS_GENERATOR_URL = "https://inkycal.aceinnolab.com/ui"
INKYCAL_OS_LITE_URL = "https://inkycal.aceinnolab.com/inkycal-os-lite"
DISCORD_SUPPORT_URL = "https://discord.gg/sHYKeSM"
DISCORD_LOGO_URL = "https://cdn.simpleicons.org/discord/5865F2"
DEMO_IMAGE_URL = "https://raw.githubusercontent.com/aceinnolab/Inkycal/refs/heads/assets/tests/Inkycal_cover.png"


def _run_command(command: List[str], timeout: int = 10) -> Tuple[int, str, str]:
    """Run a command and return code/stdout/stderr without raising."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as error:  # pragma: no cover - defensive
        return 1, "", str(error)


def _service_state() -> str:
    code, out, _ = _run_command(["systemctl", "is-active", SERVICE_NAME])
    if code == 0 and out:
        return out
    code, out, _ = _run_command(["systemctl", "is-failed", SERVICE_NAME])
    if out == "failed":
        return "failed"
    code, out, _ = _run_command(["pgrep", "-f", "inky_run.py"])
    if code == 0 and out:
        return "running (manual)"
    return "down"


def _cpu_temperature_c() -> str:
    thermal_path = Path("/sys/class/thermal/thermal_zone0/temp")
    if thermal_path.exists():
        try:
            value = int(thermal_path.read_text(encoding="utf-8").strip()) / 1000.0
            return f"{value:.1f} C"
        except Exception:
            pass

    code, out, _ = _run_command(["vcgencmd", "measure_temp"])
    if code == 0 and out:
        return out.replace("temp=", "").replace("'", "")
    return "n/a"


def _memory_info() -> str:
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        return "n/a"
    values: Dict[str, int] = {}
    for line in meminfo.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        try:
            values[key] = int(value.strip().split()[0])
        except (ValueError, IndexError):
            continue
    total = values.get("MemTotal")
    available = values.get("MemAvailable")
    if not total or available is None:
        return "n/a"
    used = total - available
    return f"{used // 1024} MiB / {total // 1024} MiB"


def _uptime() -> str:
    uptime_file = Path("/proc/uptime")
    if not uptime_file.exists():
        return "n/a"
    try:
        total_seconds = int(float(uptime_file.read_text(encoding="utf-8").split()[0]))
    except Exception:
        return "n/a"
    days, rem = divmod(total_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    mins, _ = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h {mins}m"
    return f"{hours}h {mins}m"


def _hardware_details() -> Dict[str, str]:
    return {
        "host": platform.node() or "n/a",
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "timezone": _current_timezone(),
        "cpu_temp": _cpu_temperature_c(),
        "load": " ".join(f"{v:.2f}" for v in os.getloadavg()) if hasattr(os, "getloadavg") else "n/a",
        "memory": _memory_info(),
        "uptime": _uptime(),
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def _list_logs() -> List[Path]:
    candidates: List[Path] = []
    for path in [Path(settings.LOG_PATH), PROJECT_ROOT]:
        if not path.exists():
            continue
        for item in path.glob("inkycal.log*"):
            if item.is_file():
                candidates.append(item)
    return sorted(set(candidates), key=lambda p: p.stat().st_mtime, reverse=True)


def _tail_file(path: Path, max_lines: int = 300) -> str:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return "\n".join(lines[-max_lines:])


def _qr_data_uri(url: str) -> str:
    try:
        import segno
    except ImportError:
        return ""

    buffer = io.BytesIO()
    segno.make(url, micro=False).save(buffer, kind="png", scale=4, border=1)
    encoded = b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _paypal_qr_path() -> Path:
    return PROJECT_ROOT / "image_folder" / "paypal_qr.png"


def _ensure_paypal_qr(url: str) -> Optional[Path]:
    path = _paypal_qr_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        return None

    if path.exists() and path.stat().st_size > 0:
        return path

    try:
        import segno
    except ImportError:
        return None

    segno.make(url, micro=False).save(path, kind="png", scale=6, border=2)
    return path if path.exists() else None


def _resolve_settings_file() -> Path:
    candidates: List[Path] = []
    from_env = os.getenv("INKYCAL_SETTINGS_PATH")
    if from_env:
        candidates.append(Path(from_env))

    for location in settings.SETTINGS_JSON_PATHS:
        candidates.append(Path(location))

    candidates.append(PROJECT_ROOT / "inkycal" / "settings.json")

    for path in candidates:
        if path.exists() and path.is_file():
            return path

    return candidates[-1]


SETTINGS_FILE = _resolve_settings_file()


def _read_settings_text() -> str:
    if not SETTINGS_FILE.exists():
        return "{}\n"
    return SETTINGS_FILE.read_text(encoding="utf-8", errors="ignore")


def _read_settings_json() -> Dict[str, object]:
    try:
        return json.loads(_read_settings_text())
    except json.JSONDecodeError:
        return {}


def _iter_leaf_paths(value: object, path: Tuple[str, ...] = ()) -> List[Tuple[Tuple[str, ...], object]]:
    leaves: List[Tuple[Tuple[str, ...], object]] = []
    if isinstance(value, dict):
        for key in sorted(value.keys()):
            leaves.extend(_iter_leaf_paths(value[key], path + (str(key),)))
        return leaves

    if isinstance(value, list):
        for index, item in enumerate(value):
            leaves.extend(_iter_leaf_paths(item, path + (str(index),)))
        return leaves

    leaves.append((path, value))
    return leaves


def _path_to_label(path: Tuple[str, ...]) -> str:
    return ".".join(path)


def _path_from_label(path: str) -> List[object]:
    parts: List[object] = []
    for segment in path.split("."):
        if segment.isdigit():
            parts.append(int(segment))
        else:
            parts.append(segment)
    return parts


def _get_nested_value(container: object, path: List[object]) -> object:
    current = container
    for segment in path:
        current = current[segment]  # type: ignore[index]
    return current


def _set_nested_value(container: object, path: List[object], value: object) -> None:
    current = container
    for segment in path[:-1]:
        current = current[segment]  # type: ignore[index]
    current[path[-1]] = value  # type: ignore[index]


def _coerce_value(raw_value: str, existing_value: object) -> object:
    raw = raw_value.strip()

    if isinstance(existing_value, bool):
        lowered = raw.lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
        raise ValueError("expected boolean")

    if isinstance(existing_value, int) and not isinstance(existing_value, bool):
        return int(raw)

    if isinstance(existing_value, float):
        return float(raw)

    if existing_value is None:
        if raw.lower() in {"none", "null", ""}:
            return None
        return json.loads(raw)

    if isinstance(existing_value, str):
        return raw_value

    return json.loads(raw)


def _save_settings_kv(path_labels: List[str], values: List[str]) -> str:
    if len(path_labels) != len(values):
        return "Settings save failed: malformed key/value payload."

    data = _read_settings_json()
    if not isinstance(data, dict):
        return "Settings save failed: root JSON must be an object."

    for path_label, new_value in zip(path_labels, values):
        path = _path_from_label(path_label)
        try:
            existing = _get_nested_value(data, path)
            parsed_value = _coerce_value(new_value, existing)
            _set_nested_value(data, path, parsed_value)
        except Exception as error:
            return f"Settings save failed at '{path_label}': {error}"

    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f"Saved settings to {SETTINGS_FILE}"


def _save_settings_text(content: str) -> str:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as error:
        return f"Settings save failed: invalid JSON ({error})"

    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f"Saved settings to {SETTINGS_FILE}"


def _current_timezone() -> str:
    code, out, _ = _run_command(["timedatectl", "show", "--property=Timezone", "--value"])
    if code == 0 and out:
        return out

    if time.tzname and time.tzname[0]:
        return time.tzname[0]
    return "UTC"


def _set_timezone(timezone_name: str) -> str:
    timezone_name = timezone_name.strip()
    if not timezone_name:
        return "Timezone update failed: value is required."

    if timezone_name not in available_timezones():
        return "Timezone update failed: unknown timezone name."

    code, out, err = _run_command(["sudo", "timedatectl", "set-timezone", timezone_name], timeout=20)
    if code == 0:
        return f"Timezone set to {timezone_name}."
    return f"Timezone update failed: {err or out or 'unknown error'}"


def _service_is_active() -> bool:
    code, out, _ = _run_command(["systemctl", "is-active", SERVICE_NAME])
    return code == 0 and out == "active"


DISPLAY_ACTIONS = {
    "display_calibration": "calibration",
    "display_clear": "clear",
    "display_demo": "demo",
}

DISPLAY_TASK_RUNNER = """
import certifi
import requests
import sys
import tempfile
from pathlib import Path

from PIL import Image

from inkycal.display.display import Display
from inkycal.modules.inkycal_image import Inkyimage

action = sys.argv[1]
model = sys.argv[2]
demo_url = sys.argv[3]

display = Display(model)
size = display.get_display_size(model)

if action == "calibration":
    display.calibrate(cycles=1)

elif action == "clear":
    white = Image.new("1", size, "white")
    if display.supports_colour:
        display.render(white, Image.new("1", size, "white"))
    else:
        display.render(white)

elif action == "demo":
    response = requests.get(demo_url, timeout=20, verify=certifi.where())
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file.write(response.content)
        image_path = temp_file.name

    module_config = {
        "config": {
            "size": [size[0], size[1]],
            "padding_x": 0,
            "padding_y": 0,
            "fontsize": 14,
            "path": image_path,
            "palette": "bwr" if display.supports_colour else "bw",
            "autoflip": True,
            "orientation": "horizontal",
        }
    }

    try:
        image_module = Inkyimage(module_config)
        image_black, image_colour = image_module.generate_image()
        if display.supports_colour:
            display.render(image_black, image_colour)
        else:
            display.render(image_black)
    finally:
        Path(image_path).unlink(missing_ok=True)

else:
    raise ValueError(f"Unknown display action: {action}")
""".strip()


def _run_display_action(display_action: str, display_model: str) -> str:
    if display_action not in DISPLAY_ACTIONS:
        return "Unknown display action."

    if display_model not in supported_models:
        return f"Display action failed: unsupported model '{display_model}'."

    was_active = _service_is_active()
    if was_active:
        code, out, err = _run_command(["sudo", "systemctl", "stop", SERVICE_NAME], timeout=20)
        if code != 0:
            return f"Display action failed: could not stop service ({err or out or 'unknown error'})."

    mapped_action = DISPLAY_ACTIONS[display_action]
    timeout = 60 if mapped_action in {"demo", "clear"} else 600
    command = [PYTHON_BIN, "-c", DISPLAY_TASK_RUNNER, mapped_action, display_model, DEMO_IMAGE_URL]

    try:
        code, out, err = _run_command(command, timeout=timeout)
        if code == 0:
            return f"Display action '{mapped_action}' for '{display_model}' finished."
        return f"Display action '{mapped_action}' failed: {err or out or 'unknown error'}"
    finally:
        if was_active:
            _run_command(["sudo", "systemctl", "start", SERVICE_NAME], timeout=30)


def _run_action(action: str) -> str:
    if action in {"start", "stop", "restart"}:
        code, out, err = _run_command(["sudo", "systemctl", action, SERVICE_NAME])
        if code == 0:
            return f"Service action '{action}' done."
        return f"Service action '{action}' failed: {err or out or 'unknown error'}"

    if action == "run_once":
        code, out, err = _run_command([PYTHON_BIN, INKY_RUN, "--mode", "dry-run"], timeout=180)
        if code == 0:
            return "Dry run finished."
        return f"Dry run failed: {err or out or 'unknown error'}"

    return "Unknown action."


class InkycalWebUiHandler(BaseHTTPRequestHandler):
    """Simple HTML-only UI with no client-side framework dependencies."""

    def _send_html(self, content: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, payload: Dict[str, str], status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_binary(self, payload: bytes, mime_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "public, max-age=300")
        self.end_headers()
        self.wfile.write(payload)

    def _render_dashboard(self, message: str = "") -> str:
        state = _service_state()
        hardware = _hardware_details()
        logs = _list_logs()
        selected_name = self._query.get("log", [logs[0].name if logs else ""])[0]
        selected_path = next((p for p in logs if p.name == selected_name), None)
        log_content = _tail_file(selected_path) if selected_path else "No log file found."
        settings_content = _read_settings_text()
        settings_data = _read_settings_json()
        selected_display = str(settings_data.get("model", "n/a"))
        display_models = sorted(supported_models.keys())
        selected_display_model = self._query.get("display_model", [selected_display if selected_display in supported_models else (display_models[0] if display_models else "")])[0]
        settings_leaf_entries = _iter_leaf_paths(settings_data) if isinstance(settings_data, dict) else []

        qr_path = _ensure_paypal_qr(PAYPAL_URL)
        qr_uri = _qr_data_uri(PAYPAL_URL)

        options = "".join(
            f"<option value='{html.escape(item.name)}'"
            f" {'selected' if item.name == selected_name else ''}>{html.escape(item.name)}</option>"
            for item in logs
        )

        display_options = "".join(
            f"<option value='{html.escape(model_name)}'"
            f" {'selected' if model_name == selected_display_model else ''}>{html.escape(model_name)}</option>"
            for model_name in display_models
        )

        key_value_rows = "".join(
            (
                "<div class='kv-row'>"
                f"<input class='kv-key' value='{html.escape(_path_to_label(path))}' readonly>"
                f"<input type='hidden' name='kv_path' value='{html.escape(_path_to_label(path))}'>"
                f"<input class='kv-value' name='kv_value' value='{html.escape(json.dumps(value, ensure_ascii=False) if value is None else str(value))}'>"
                "</div>"
            )
            for path, value in settings_leaf_entries
        )

        if qr_path:
            qr_html = "<img alt='PayPal QR' class='qr-img' src='/paypal-qr.png' width='200' height='200'/>"
        elif qr_uri:
            qr_html = f"<img alt='PayPal QR' class='qr-img' src='{qr_uri}' width='200' height='200'/>"
        else:
            qr_html = "<p>Install segno for offline QR generation.</p>"

        message_class = "msg error" if "failed" in message.lower() else "msg"

        return f"""
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>Inkycal Local UI</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #eff2f7;
      --surface: #ffffff;
      --text: #1f2937;
      --muted: #64748b;
      --accent: #2563eb;
      --ok: #157347;
      --err: #b42318;
      --shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
      --border: #dbe2ef;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(180deg, #f8fbff 0%, var(--bg) 100%);
      color: var(--text);
    }}
    .wrapper {{ max-width: 1180px; margin: 0 auto; padding: 1rem; }}
    h1 {{ margin: 0 0 0.25rem; font-size: clamp(1.4rem, 2.2vw, 2rem); }}
    .subtitle {{ margin: 0 0 1rem; color: var(--muted); }}
    .msg {{ margin: 0.6rem 0 1rem; color: var(--ok); font-weight: 600; min-height: 1.2rem; }}
    .msg.error {{ color: var(--err); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1rem;
      box-shadow: var(--shadow);
    }}
    h2 {{ margin: 0 0 0.8rem; font-size: 1.1rem; }}
    p {{ margin: 0.45rem 0; }}
    .muted {{ color: var(--muted); font-size: 0.92rem; }}
    .button-row {{ display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.55rem; }}
    button {{
      border: 0;
      border-radius: 10px;
      padding: 0.55rem 0.8rem;
      background: var(--accent);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
    }}
    button.secondary {{ background: #475569; }}
    input, select, textarea {{
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 0.58rem 0.7rem;
      font: inherit;
      background: #fff;
      color: var(--text);
    }}
    label {{ display: block; margin: 0.4rem 0 0.35rem; font-weight: 600; }}
    textarea {{ min-height: 230px; resize: vertical; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    pre {{
      background: #0f172a;
      color: #e2e8f0;
      padding: 0.85rem;
      border-radius: 10px;
      max-height: 45vh;
      overflow: auto;
      margin: 0.75rem 0 0;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.85rem;
      line-height: 1.35;
    }}
    .metrics {{ display: grid; grid-template-columns: auto 1fr; gap: 0.35rem 0.65rem; }}
    .metrics strong {{ color: #0f172a; }}
    .qr-img {{ max-width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--border); }}
    .link-list a {{ color: #1d4ed8; text-decoration: none; font-weight: 600; }}
    .link-list a:hover {{ text-decoration: underline; }}
    .discord-link {{ display: inline-flex; align-items: center; gap: 0.55rem; margin-top: 0.4rem; }}
    .discord-logo {{ width: 22px; height: 22px; display: inline-block; }}
    .kv-grid {{ display: grid; gap: 0.5rem; }}
    .kv-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }}
    .kv-key {{ background: #f8fafc; color: #334155; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .kv-value {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    @media (max-width: 640px) {{
      .wrapper {{ padding: 0.75rem; }}
      .card {{ padding: 0.85rem; border-radius: 12px; }}
      pre {{ max-height: 38vh; }}
      .kv-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main class='wrapper'>
    <h1>Inkycal Local UI</h1>
    <p class='subtitle'>Monitor status, tweak timezone, and edit <code>settings.json</code> from your phone or desktop.</p>
    <p class='{message_class}'>{html.escape(message)}</p>

    <div class='grid'>
      <section class='card'>
        <h2>Status</h2>
        <p><strong>Inkycal:</strong> {html.escape(state)}</p>
        <p><strong>Service:</strong> {html.escape(SERVICE_NAME)}</p>
        <p><strong>Selected display:</strong> {html.escape(selected_display)}</p>
        <form method='post'>
          <div class='button-row'>
            <button name='action' value='start'>Start</button>
            <button name='action' value='stop' class='secondary'>Stop</button>
            <button name='action' value='restart'>Restart</button>
            <button name='action' value='run_once'>Dry run</button>
          </div>
        </form>
        <form method='post'>
          <label for='display_model'>Display model</label>
          <select id='display_model' name='display_model'>
            {display_options}
          </select>
          <div class='button-row'>
            <button name='action' value='display_calibration'>Run calibration</button>
            <button name='action' value='display_clear' class='secondary'>Clear</button>
            <button name='action' value='display_demo'>Show demo image</button>
          </div>
          <p class='muted'>Display action stops <code>{html.escape(SERVICE_NAME)}</code> temporarily and restores its previous state after completion.</p>
        </form>
      </section>

      <section class='card'>
        <h2>Hardware</h2>
        <div class='metrics'>
          <strong>Host</strong><span data-hw='host'>{html.escape(hardware['host'])}</span>
          <strong>Platform</strong><span data-hw='platform'>{html.escape(hardware['platform'])}</span>
          <strong>Python</strong><span data-hw='python'>{html.escape(hardware['python'])}</span>
          <strong>Timezone</strong><span data-hw='timezone'>{html.escape(hardware['timezone'])}</span>
          <strong>Temp</strong><span data-hw='cpu_temp'>{html.escape(hardware['cpu_temp'])}</span>
          <strong>Load</strong><span data-hw='load'>{html.escape(hardware['load'])}</span>
          <strong>Memory</strong><span data-hw='memory'>{html.escape(hardware['memory'])}</span>
          <strong>Uptime</strong><span data-hw='uptime'>{html.escape(hardware['uptime'])}</span>
          <strong>Now</strong><span data-hw='time'>{html.escape(hardware['time'])}</span>
        </div>
        <p class='muted'>Auto-updates every {HARDWARE_REFRESH_SECONDS}s while this page is open.</p>
      </section>

      <section class='card'>
        <h2>Timezone</h2>
        <form method='post'>
          <label for='timezone'>IANA timezone name</label>
          <input id='timezone' name='timezone' value='{html.escape(hardware['timezone'])}' placeholder='Europe/Berlin' required>
          <p class='muted'>Uses <code>timedatectl set-timezone</code>; may require sudo permissions.</p>
          <div class='button-row'>
            <button name='action' value='set_timezone'>Apply timezone</button>
          </div>
        </form>
      </section>

      <section class='card'>
        <h2>Resources</h2>
        <p class='link-list'>
          <a href='{SETTINGS_GENERATOR_URL}' target='_blank' rel='noreferrer'>Generate a new settings.json file from here</a>
        </p>
        <p class='link-list'>
          <a href='{INKYCAL_OS_LITE_URL}' target='_blank' rel='noreferrer'>InkyCalOS-Lite</a>
        </p>
        <p>
          <a class='discord-link' href='{DISCORD_SUPPORT_URL}' target='_blank' rel='noreferrer'>
            <img class='discord-logo' src='{DISCORD_LOGO_URL}' alt='Discord logo'>
            <span>Need some assistance? Join our discord server to get community help</span>
          </a>
        </p>
      </section>

      <section class='card'>
        <h2>Donate</h2>
        <p><a href='{html.escape(PAYPAL_URL)}' target='_blank' rel='noreferrer'>Open PayPal.me</a></p>
        {qr_html}
      </section>
    </div>

    <section class='card' style='margin-top: 1rem;'>
      <h2>Logs</h2>
      <form method='get'>
        <label for='log'>Log file</label>
        <select id='log' name='log'>{options}</select>
        <div class='button-row'>
          <button type='submit'>Open log</button>
        </div>
      </form>
      <pre>{html.escape(log_content)}</pre>
    </section>

    <section class='card' style='margin-top: 1rem;'>
      <h2>Settings Key/Value Editor</h2>
      <p class='muted'>Keys are read-only paths. Values are editable and saved with original types where possible.</p>
      <form method='post'>
        <div class='kv-grid'>
          {key_value_rows}
        </div>
        <div class='button-row'>
          <button name='action' value='save_settings_kv'>Save key/value settings</button>
        </div>
      </form>
    </section>

    <section class='card' style='margin-top: 1rem;'>
      <h2>Settings JSON</h2>
      <p class='muted'>Editing file: <code>{html.escape(str(SETTINGS_FILE))}</code></p>
      <form method='post'>
        <label for='settings_content'>settings.json</label>
        <textarea id='settings_content' name='settings_content' spellcheck='false'>{html.escape(settings_content)}</textarea>
        <div class='button-row'>
          <button name='action' value='save_settings'>Save settings</button>
        </div>
      </form>
    </section>
  </main>

  <script>
    (function() {{
      const intervalMs = {HARDWARE_REFRESH_SECONDS} * 1000;
      async function refreshHardware() {{
        try {{
          const response = await fetch('/api/hardware', {{ cache: 'no-store' }});
          if (!response.ok) return;
          const data = await response.json();
          Object.entries(data).forEach(([key, value]) => {{
            const target = document.querySelector(`[data-hw="${{key}}"]`);
            if (target) target.textContent = value;
          }});

          const timezoneInput = document.getElementById('timezone');
          if (timezoneInput && document.activeElement !== timezoneInput && data.timezone) {{
            timezoneInput.value = data.timezone;
          }}
        }} catch (error) {{
          // Ignore transient network errors while polling.
        }}
      }}

      refreshHardware();
      window.setInterval(refreshHardware, intervalMs);
    }})();
  </script>
</body>
</html>
"""

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/hardware":
            self._send_json(_hardware_details())
            return

        if parsed.path == "/paypal-qr.png":
            qr_path = _ensure_paypal_qr(PAYPAL_URL)
            if qr_path and qr_path.exists():
                self._send_binary(qr_path.read_bytes(), "image/png")
                return
            self._send_html("<h1>Not found</h1>", status=HTTPStatus.NOT_FOUND)
            return

        if parsed.path != "/":
            self._send_html("<h1>Not found</h1>", status=HTTPStatus.NOT_FOUND)
            return

        self._query = urllib.parse.parse_qs(parsed.query)
        self._send_html(self._render_dashboard())

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/":
            self._send_html("<h1>Not found</h1>", status=HTTPStatus.NOT_FOUND)
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        form = urllib.parse.parse_qs(body)
        action = form.get("action", [""])[0]
        display_model = form.get("display_model", [""])[0]
        if action == "save_settings":
            message = _save_settings_text(form.get("settings_content", [""])[0])
        elif action == "save_settings_kv":
            message = _save_settings_kv(form.get("kv_path", []), form.get("kv_value", []))
        elif action == "set_timezone":
            message = _set_timezone(form.get("timezone", [""])[0])
        elif action in DISPLAY_ACTIONS:
            message = _run_display_action(action, display_model)
        else:
            message = _run_action(action)
        self._query = {"display_model": [display_model]} if display_model else {}
        self._send_html(self._render_dashboard(message=message))


def serve_webui(host: str = WEBUI_HOST, port: int = WEBUI_PORT) -> None:
    server = ThreadingHTTPServer((host, port), InkycalWebUiHandler)
    print(f"Inkycal web UI listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    serve_webui()
