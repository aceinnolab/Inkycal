"""Basic Inkycal run script.

Assumes that the settings.json file is in the /boot directory.
set render=True to render the display, set render=False to only run the modules.
"""
import asyncio
import argparse
import contextlib
import os
import sys

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX only
    fcntl = None

from inkycal.main import Inkycal

LOCK_PATH = os.getenv("INKYCAL_LOCK_FILE", "/tmp/inkycal.lock")


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
