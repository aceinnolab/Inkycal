"""Very small local web UI for monitoring and controlling Inkycal."""

from __future__ import annotations

import html
import io
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
from typing import Dict, List, Tuple

from inkycal.settings import Settings

settings = Settings()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SERVICE_NAME = os.getenv("INKYCAL_SERVICE_NAME", "inkycal.service")
WEBUI_HOST = os.getenv("INKYCAL_WEBUI_HOST", "127.0.0.1")
WEBUI_PORT = int(os.getenv("INKYCAL_WEBUI_PORT", "8080"))
PAYPAL_URL = os.getenv("INKYCAL_PAYPAL_URL", "https://www.paypal.me/aceisace")
PYTHON_BIN = os.getenv("INKYCAL_PYTHON_BIN", str(PROJECT_ROOT / "venv" / "bin" / "python"))
INKY_RUN = os.getenv("INKYCAL_RUNNER", str(PROJECT_ROOT / "inky_run.py"))


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

    def _render_dashboard(self, message: str = "") -> str:
        state = _service_state()
        hardware = _hardware_details()
        logs = _list_logs()
        selected_name = self._query.get("log", [logs[0].name if logs else ""])[0]
        selected_path = next((p for p in logs if p.name == selected_name), None)
        log_content = _tail_file(selected_path) if selected_path else "No log file found."
        qr_uri = _qr_data_uri(PAYPAL_URL)

        options = "".join(
            f"<option value='{html.escape(item.name)}'"
            f" {'selected' if item.name == selected_name else ''}>{html.escape(item.name)}</option>"
            for item in logs
        )

        qr_html = (
            f"<img alt='PayPal QR' src='{qr_uri}' width='170' height='170'/>"
            if qr_uri
            else "<p>Install segno for offline QR generation.</p>"
        )

        return f"""
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>Inkycal Local UI</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 1rem; background: #f6f7f9; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }}
    .card {{ background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
    h1, h2 {{ margin-top: 0; }}
    button {{ margin: .2rem; padding: .4rem .7rem; }}
    pre {{ background: #111; color: #ddd; padding: .8rem; border-radius: 6px; max-height: 380px; overflow: auto; }}
    .msg {{ color: #0a5; font-weight: bold; }}
  </style>
</head>
<body>
  <h1>Inkycal Local UI</h1>
  <p class='msg'>{html.escape(message)}</p>
  <div class='grid'>
    <section class='card'>
      <h2>Status</h2>
      <p><strong>Inkycal:</strong> {html.escape(state)}</p>
      <p><strong>Service:</strong> {html.escape(SERVICE_NAME)}</p>
      <form method='post'>
        <button name='action' value='start'>Start</button>
        <button name='action' value='stop'>Stop</button>
        <button name='action' value='restart'>Restart</button>
        <button name='action' value='run_once'>Dry run</button>
      </form>
    </section>

    <section class='card'>
      <h2>Hardware</h2>
      <p><strong>Host:</strong> {html.escape(hardware['host'])}</p>
      <p><strong>Platform:</strong> {html.escape(hardware['platform'])}</p>
      <p><strong>Python:</strong> {html.escape(hardware['python'])}</p>
      <p><strong>Temp:</strong> {html.escape(hardware['cpu_temp'])}</p>
      <p><strong>Load:</strong> {html.escape(hardware['load'])}</p>
      <p><strong>Memory:</strong> {html.escape(hardware['memory'])}</p>
      <p><strong>Uptime:</strong> {html.escape(hardware['uptime'])}</p>
      <p><strong>Now:</strong> {html.escape(hardware['time'])}</p>
    </section>

    <section class='card'>
      <h2>Donate</h2>
      <p><a href='{html.escape(PAYPAL_URL)}' target='_blank' rel='noreferrer'>PayPal</a></p>
      {qr_html}
    </section>
  </div>

  <section class='card'>
    <h2>Logs</h2>
    <form method='get'>
      <select name='log'>{options}</select>
      <button type='submit'>Open</button>
    </form>
    <pre>{html.escape(log_content)}</pre>
  </section>
</body>
</html>
"""

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
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
        message = _run_action(action)
        self._query = {}
        self._send_html(self._render_dashboard(message=message))


def serve_webui(host: str = WEBUI_HOST, port: int = WEBUI_PORT) -> None:
    server = ThreadingHTTPServer((host, port), InkycalWebUiHandler)
    print(f"Inkycal web UI listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    serve_webui()
