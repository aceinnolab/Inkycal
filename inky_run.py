"""Basic Inkycal run script.

Assumes that the settings.json file is in the /boot directory.
set render=True to render the display, set render=False to only run the modules.
"""
import asyncio
import argparse
import contextlib
import json
import os
import sys
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX only
    fcntl = None

from inkycal.main import Inkycal
from inkycal.display import Display
from inkycal.settings import Settings
from inkycal.utils.functions import get_inkycal_version

LOCK_PATH = os.getenv("INKYCAL_LOCK_FILE", "/tmp/inkycal.lock")


def _read_boot_id() -> str:
    try:
        with open("/proc/sys/kernel/random/boot_id", "r", encoding="utf-8") as boot_file:
            return boot_file.read().strip()
    except Exception:
        return "unknown-boot"


def _splash_flag_path(version: str) -> str:
    splash_dir = os.getenv("INKYCAL_SPLASH_STATE_DIR", "/tmp")
    version_safe = str(version).replace("/", "-")
    return os.path.join(splash_dir, f"inkycal-splash-{_read_boot_id()}-{version_safe}.flag")


def _resolve_settings_path() -> Path:
    configured = os.getenv("INKYCAL_SETTINGS_PATH")
    if configured:
        path = Path(configured)
        if path.exists() and path.is_file():
            return path

    settings = Settings()
    for location in settings.SETTINGS_JSON_PATHS:
        path = Path(location)
        if path.exists() and path.is_file():
            return path

    fallback = Path(__file__).resolve().parent / "inkycal" / "settings.json"
    return fallback


def _show_startup_splash_if_needed() -> None:
    settings_path = _resolve_settings_path()
    if not settings_path.exists():
        return

    try:
        settings_data = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception:
        return

    if not settings_data.get("show_startup_splash", True):
        return

    model = settings_data.get("model")
    if not isinstance(model, str) or not model:
        return

    version = get_inkycal_version()
    flag_path = _splash_flag_path(version)
    if os.path.exists(flag_path):
        return

    try:
        orientation = int(settings_data.get("orientation", 0))
        display = Display(model)
        display.render_startup_splash(
            title="Inkycal",
            version=f"v{version}",
            title_font_size=88,
            version_font_size=30,
            line_gap=28,
            orientation=orientation,
        )
        os.makedirs(os.path.dirname(flag_path), exist_ok=True)
        with open(flag_path, "w", encoding="utf-8") as marker:
            marker.write("1")
    except Exception:
        # Splash must never block startup if hardware/config is not ready.
        return


@contextlib.contextmanager
def single_instance_lock(lock_path: str):
    """Prevent concurrent Inkycal runs on POSIX systems."""
    lock_file = open(lock_path, "w", encoding="utf-8")
    try:
        if fcntl is not None:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError(f"Another Inkycal instance is already running (lock: {lock_path}).")
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        yield
    finally:
        lock_file.close()


async def run():
    """Run Inkycal nonstop. Default mode."""
    # create an instance of Inkycal
    # If your settings.json file is not in /boot, use the full path:
    # inky = Inkycal('path/to/settings.json', render=True)

    # when using experimental PiSugar support:
    # inky = Inkycal(render=True, use_pi_sugar=True, shutdown_after_run=False)
    _show_startup_splash_if_needed()
    inky = Inkycal(render=True)
    await inky.run()  # If there were no issues, you can run Inkycal nonstop


async def dry_run():
    """Useful for checking if the settings.json file is okay, without actually touching the display"""
    # create an instance of Inkycal
    # If your settings.json file is not in /boot, use the full path:
    # inky = Inkycal('path/to/settings.json', render=True)
    inky = Inkycal(render=False)
    await inky.run(run_once=True)  # dry-run without rendering anything on the display


async def clear_display():
    """Calibrate the display if you see some ghosting"""
    print("loading Inkycal and display driver...")
    inky = Inkycal(render=True)  # Initialise Inkycal
    print("clearing display...")
    inky.calibrate(cycles=1)  # Calibrate the display
    print("clear complete...")
    print("finished!")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Inkycal")
    parser.add_argument(
        "--mode",
        choices=["run", "dry-run", "clear"],
        default="run",
        help="run: normal loop, dry-run: one cycle without rendering, clear: one display calibration",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        with single_instance_lock(LOCK_PATH):
            if args.mode == "dry-run":
                asyncio.run(dry_run())
            elif args.mode == "clear":
                asyncio.run(clear_display())
            else:
                asyncio.run(run())
    except RuntimeError as error:
        print(error)
        sys.exit(1)
