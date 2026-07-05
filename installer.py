#!/usr/bin/env python3
"""Interactive installer/maintenance tool for Inkycal."""

from __future__ import annotations

import argparse
import json
import os
import pwd
import shutil
import select
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX only
    fcntl = None


APT_PACKAGES_FILE = "apt_packages.txt"

PIP_INDEX_ARGS = [
    "--index-url", "https://www.piwheels.org/simple",
    "--extra-index-url", "https://pypi.org/simple",
]

SWAP_CONF_DIR = Path("/etc/rpi/swap.conf.d")
SWAP_CONF_PATH = SWAP_CONF_DIR / "80-use-swapfile.conf"
SWAP_CONF_CONTENT = textwrap.dedent(
    """
    [Main]
    Mechanism=swapfile

    [File]
    FixedSizeMiB=1024
    """
).strip() + "\n"


INKYCAL_SERVICE_TEMPLATE = """[Unit]
Description=Inkycal dashboard service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User={user}
Group={group}
WorkingDirectory={repo}
Environment=PYTHONUNBUFFERED=1
Environment=INKYCAL_LOG_DIR={repo}/logs
Environment=INKYCAL_LOCK_FILE=/tmp/inkycal.lock
ExecStart={python_bin} {repo}/inky_run.py --mode run
Restart=on-failure
RestartSec=20
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""


INKYCAL_WEBUI_SERVICE_TEMPLATE = """[Unit]
Description=Inkycal local web UI
After=network-online.target inkycal.service
Wants=network-online.target

[Service]
Type=simple
User={user}
Group={group}
WorkingDirectory={repo}
Environment=PYTHONUNBUFFERED=1
Environment=INKYCAL_WEBUI_HOST={webui_host}
Environment=INKYCAL_WEBUI_PORT=8080
ExecStart={python_bin} {repo}/inky_webui.py
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""


@dataclass
class InstallerContext:
    repo_root: Path
    user: str
    group: str
    venv_dir: Path
    python_bin: Path
    state_file: Path
    apt_packages: list[str]


def run_command(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    use_sudo: bool = False,
    timeout: int = 900,
    check: bool = True,
) -> subprocess.CompletedProcess:
    cmd = list(command)
    if use_sudo and os.geteuid() != 0:
        cmd = ["sudo", *cmd]
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=check,
        timeout=timeout,
    )


def print_command_result(result: subprocess.CompletedProcess) -> None:
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())


def _read_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def _normalize_text(value: str) -> str:
    return "\n".join(line.strip() for line in value.strip().splitlines() if line.strip())


def is_raspberry_pi_zero() -> bool:
    model = _read_text_if_exists(Path("/proc/device-tree/model"))
    if model and "zero" in model.lower():
        return True
    machine = os.uname().machine.lower() if hasattr(os, "uname") else ""
    return machine == "armv6l"


def swap_is_configured() -> bool:
    existing = _read_text_if_exists(SWAP_CONF_PATH)
    return existing is not None and _normalize_text(existing) == _normalize_text(SWAP_CONF_CONTENT)


def setup_swap(ctx: InstallerContext, prompt: bool = True) -> None:
    if not is_raspberry_pi_zero():
        return
    if swap_is_configured():
        print(f"Swap already configured at {SWAP_CONF_PATH}; skipping.")
        return
    if prompt and not timed_yes_no("Set up the recommended Pi Zero swap file now?", timeout_seconds=60):
        print("Skipping swap setup.")
        return

    print("Setting up Pi Zero swap...")
    result = run_command(["mkdir", "-p", str(SWAP_CONF_DIR)], use_sudo=True)
    print_command_result(result)
    with tempfile.TemporaryDirectory(prefix="inkycal-swap-") as temp_dir:
        temp_path = Path(temp_dir) / SWAP_CONF_PATH.name
        temp_path.write_text(SWAP_CONF_CONTENT, encoding="utf-8")
        result = run_command(["install", "-m", "644", str(temp_path), str(SWAP_CONF_PATH)], use_sudo=True)
        print_command_result(result)
    result = run_command(["systemctl", "daemon-reexec"], use_sudo=True, check=False)
    print_command_result(result)
    result = run_command(["systemctl", "restart", "systemd-swap"], use_sudo=True, check=False)
    print_command_result(result)
    save_state(ctx, "swap", "ok")
    print("Swap setup complete.")


def remove_swap_setup() -> None:
    result = run_command(["systemctl", "disable", "--now", "systemd-swap"], use_sudo=True, check=False)
    print_command_result(result)
    result = run_command(["rm", "-f", str(SWAP_CONF_PATH)], use_sudo=True, check=False)
    print_command_result(result)
    result = run_command(["systemctl", "daemon-reexec"], use_sudo=True, check=False)
    print_command_result(result)


def remove_systemd_units() -> None:
    for service in ["inkycal.service", "inkycal-webui.service"]:
        result = run_command(["systemctl", "disable", "--now", service], use_sudo=True, check=False)
        print_command_result(result)
        result = run_command(["rm", "-f", f"/etc/systemd/system/{service}"], use_sudo=True, check=False)
        print_command_result(result)
    result = run_command(["systemctl", "daemon-reload"], use_sudo=True, check=False)
    print_command_result(result)


def purge_apt_dependencies(ctx: InstallerContext) -> None:
    result = run_command(["apt-get", "remove", "--purge", "-y", *ctx.apt_packages], use_sudo=True, check=False)
    print_command_result(result)
    result = run_command(["apt-get", "autoremove", "--purge", "-y"], use_sudo=True, check=False)
    print_command_result(result)


def full_wipe(ctx: InstallerContext) -> None:
    if not timed_yes_no("This will remove installer-managed system changes. Continue?", timeout_seconds=60):
        print("Full wipe cancelled.")
        return

    remove_systemd_units()
    remove_swap_setup()

    if ctx.state_file.exists():
        try:
            ctx.state_file.unlink()
        except Exception:
            pass
    try:
        ctx.state_file.parent.rmdir()
    except Exception:
        pass

    if timed_yes_no("Purge installer-managed apt packages too?", timeout_seconds=60):
        purge_apt_dependencies(ctx)

    if timed_yes_no("Delete the cloned Inkycal folder permanently?", timeout_seconds=60):
        shutil.rmtree(ctx.repo_root, ignore_errors=True)
        print("Inkycal folder deleted.")
    else:
        print("Keeping the cloned Inkycal folder.")


def load_apt_packages(repo_root: Path) -> list[str]:
    apt_packages_path = repo_root / APT_PACKAGES_FILE
    if not apt_packages_path.exists():
        raise RuntimeError(f"Missing required apt package file: {apt_packages_path}")

    apt_packages = [
        line.strip()
        for line in apt_packages_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not apt_packages:
        raise RuntimeError(f"No apt packages found in {apt_packages_path}")
    return apt_packages


def detect_context(repo_root: Path) -> InstallerContext:
    if os.geteuid() == 0:
        sudo_user = os.environ.get("SUDO_USER")
        if not sudo_user or sudo_user == "root":
            raise RuntimeError(
                "Do not run installer directly as root. Run it as your normal user, "
                "or via sudo while preserving SUDO_USER."
            )
        username = sudo_user
    else:
        username = pwd.getpwuid(os.getuid()).pw_name

    try:
        pw = pwd.getpwnam(username)
    except KeyError:
        # Some CI environments provide SUDO_USER values that don't exist inside
        # the runtime image. Fall back to the current uid's account instead.
        pw = pwd.getpwuid(os.getuid())
        username = pw.pw_name
    home = Path(pw.pw_dir)
    venv_dir = repo_root / "venv"
    python_bin = venv_dir / "bin" / "python"
    state_file = home / ".config" / "inkycal-installer" / "state.json"
    apt_packages = load_apt_packages(repo_root)
    return InstallerContext(
        repo_root=repo_root,
        user=username,
        group=username,
        venv_dir=venv_dir,
        python_bin=python_bin,
        state_file=state_file,
        apt_packages=apt_packages,
    )


def save_state(ctx: InstallerContext, key: str, value: str) -> None:
    ctx.state_file.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if ctx.state_file.exists():
        try:
            data = json.loads(ctx.state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    data[key] = value
    ctx.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def repair_permissions(ctx: InstallerContext) -> None:
    print("Repairing file ownership for project and runtime folders...")
    targets = [
        ctx.repo_root,
        ctx.repo_root / "logs",
        ctx.repo_root / "venv",
        ctx.repo_root / "tmp",
        ctx.repo_root / "inkycal" / "tmp",
    ]
    for target in targets:
        if target.exists():
            result = run_command(["chown", "-R", f"{ctx.user}:{ctx.group}", str(target)], use_sudo=True)
            print_command_result(result)
    save_state(ctx, "permissions", "ok")


def install_or_repair(ctx: InstallerContext) -> None:
    print("Running install/repair...")
    repair_permissions(ctx)

    try:
        result = run_command(["apt-get", "update", "-y"], use_sudo=True)
        print_command_result(result)
        result = run_command(["apt-get", "install", "-y", *ctx.apt_packages], use_sudo=True)
        print_command_result(result)
    except Exception as error:
        print(f"Warning: apt dependency step failed: {error}")

    setup_swap(ctx, prompt=True)

    if not ctx.venv_dir.exists():
        result = run_command(["python3", "-m", "venv", str(ctx.venv_dir)], cwd=ctx.repo_root)
        print_command_result(result)

    pip = str(ctx.venv_dir / "bin" / "pip")
    result = run_command([pip, "install", "--upgrade", "pip", "wheel", "setuptools", *PIP_INDEX_ARGS], cwd=ctx.repo_root)
    print_command_result(result)

    result = run_command([pip, "install", "-e", ".", *PIP_INDEX_ARGS], cwd=ctx.repo_root)
    print_command_result(result)

    raspberry_reqs = ctx.repo_root / "raspberry_os_requirements.txt"
    if raspberry_reqs.exists():
        result = run_command([pip, "install", "-r", str(raspberry_reqs), *PIP_INDEX_ARGS], cwd=ctx.repo_root)
        print_command_result(result)

    save_state(ctx, "install", "ok")
    print("Install/repair completed.")


def update_inkycal(ctx: InstallerContext) -> None:
    print("Updating Inkycal repository...")
    try:
        result = run_command(["git", "pull", "--ff-only"], cwd=ctx.repo_root)
        print_command_result(result)
    except subprocess.CalledProcessError as error:
        print_command_result(error)
        raise RuntimeError(
            "git pull failed. Resolve local changes/conflicts, then rerun installer."
        ) from error

    install_or_repair(ctx)
    save_state(ctx, "update", "ok")


def render_service_contents(ctx: InstallerContext, webui_host: str) -> tuple[str, str]:
    service = INKYCAL_SERVICE_TEMPLATE.format(
        user=ctx.user,
        group=ctx.group,
        repo=ctx.repo_root,
        python_bin=ctx.python_bin,
    )
    webui = INKYCAL_WEBUI_SERVICE_TEMPLATE.format(
        user=ctx.user,
        group=ctx.group,
        repo=ctx.repo_root,
        python_bin=ctx.python_bin,
        webui_host=webui_host,
    )
    return service, webui


def install_services(ctx: InstallerContext, webui_host: str) -> None:
    print("Installing portable systemd services...")
    service_content, webui_content = render_service_contents(ctx, webui_host)

    with tempfile.TemporaryDirectory(prefix="inkycal-installer-") as temp_dir:
        temp_dir_path = Path(temp_dir)
        service_path = temp_dir_path / "inkycal.service"
        webui_path = temp_dir_path / "inkycal-webui.service"
        service_path.write_text(service_content, encoding="utf-8")
        webui_path.write_text(webui_content, encoding="utf-8")

        for src, dst in [
            (service_path, "/etc/systemd/system/inkycal.service"),
            (webui_path, "/etc/systemd/system/inkycal-webui.service"),
        ]:
            result = run_command(["install", "-m", "644", str(src), dst], use_sudo=True)
            print_command_result(result)

    for cmd in [
        ["systemctl", "daemon-reload"],
        ["systemctl", "enable", "--now", "inkycal.service"],
        ["systemctl", "enable", "--now", "inkycal-webui.service"],
    ]:
        result = run_command(cmd, use_sudo=True)
        print_command_result(result)

    save_state(ctx, "services", "ok")
    print("Services installed and enabled.")


def service_action(action: str) -> None:
    for service in ["inkycal.service", "inkycal-webui.service"]:
        result = run_command(["systemctl", action, service], use_sudo=True)
        print_command_result(result)


def show_service_status() -> None:
    result = run_command(["systemctl", "status", "inkycal.service", "--no-pager"], use_sudo=True, check=False)
    print_command_result(result)
    result = run_command(["systemctl", "status", "inkycal-webui.service", "--no-pager"], use_sudo=True, check=False)
    print_command_result(result)


def _current_timezone() -> str:
    result = run_command(["timedatectl", "show", "--property=Timezone", "--value"], check=False)
    tz = result.stdout.strip()
    return tz if tz else "UTC"


def configure_timezone_via_raspi_config() -> None:
    if shutil.which("raspi-config") is None:
        print("raspi-config was not found on this system.")
        return

    current_tz = _current_timezone()
    print(f"Current timezone: {current_tz}")
    requested_tz = input("Enter timezone (e.g. Europe/Berlin) or leave empty to cancel: ").strip()
    if not requested_tz:
        print("Timezone update cancelled.")
        return

    print(f"Applying timezone via raspi-config: {requested_tz}")
    result = run_command(
        ["raspi-config", "nonint", "do_change_timezone", requested_tz],
        use_sudo=True,
        check=False,
    )
    print_command_result(result)

    if result.returncode != 0:
        print("Non-interactive timezone update failed.")
        print("Please run the interactive tool manually:")
        print("  sudo raspi-config")
        print("Then open: Localisation Options -> Timezone")
        return

    print(f"Timezone is now: {_current_timezone()}")


def choose_with_curses(title: str, options: list[str]) -> int:
    import curses

    selected = 0

    def _draw(stdscr):
        nonlocal selected
        curses.curs_set(0)
        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, title)
            stdscr.addstr(1, 0, "Use arrow keys and Enter.")
            for idx, option in enumerate(options):
                prefix = "-> " if idx == selected else "   "
                stdscr.addstr(idx + 3, 0, f"{prefix}{option}")
            key = stdscr.getch()
            if key in (curses.KEY_UP, ord("k")):
                selected = (selected - 1) % len(options)
            elif key in (curses.KEY_DOWN, ord("j")):
                selected = (selected + 1) % len(options)
            elif key in (10, 13):
                return

    curses.wrapper(_draw)
    return selected


def choose_option(title: str, options: list[str]) -> int:
    if sys.stdin.isatty() and sys.stdout.isatty():
        try:
            return choose_with_curses(title, options)
        except Exception:
            pass

    print(title)
    for idx, option in enumerate(options, start=1):
        print(f"  {idx}. {option}")
    while True:
        raw = input("Select a number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        print("Invalid selection.")


def timed_yes_no(prompt: str, timeout_seconds: int = 60) -> bool:
    print(f"{prompt} [y/N] (auto-no in {timeout_seconds}s): ", end="", flush=True)
    readable, _, _ = select.select([sys.stdin], [], [], timeout_seconds)
    if not readable:
        print("\nNo response received in time.")
        return False
    answer = sys.stdin.readline().strip().lower()
    return answer in {"y", "yes"}


def display_test(ctx: InstallerContext, timeout_seconds: int = 60) -> None:
    from inkycal.display.supported_models import supported_models

    models = sorted([name for name in supported_models.keys() if not name.startswith("image_file")])
    idx = choose_option("Select display model for test", models)
    model = models[idx]
    print(f"Testing model: {model}")

    cmd = [str(ctx.python_bin if ctx.python_bin.exists() else Path(sys.executable)), str(ctx.repo_root / "installer.py"), "--run-display-test-worker", model]
    try:
        result = run_command(cmd, cwd=ctx.repo_root, timeout=timeout_seconds, check=False)
    except subprocess.TimeoutExpired:
        print(textwrap.dedent(
            f"""
            Display test timed out after {timeout_seconds}s.
            Please double-check wiring and verify that this is the correct model.
            """
        ).strip())
        return

    print_command_result(result)
    if result.returncode != 0:
        print("Display test command failed. Please verify model selection and wiring.")
        return

    if timed_yes_no("Did the display refresh correctly?", timeout_seconds=timeout_seconds):
        print("Display test passed.")
        save_state(ctx, "last_display_model", model)
    else:
        print("Display test marked as failed. Re-check wiring or choose another model.")


def run_display_test_worker(model: str) -> int:
    from PIL import Image, ImageDraw

    from inkycal.display import Display

    width, height = Display.get_display_size(model)
    im_black = Image.new("1", (width, height), "white")
    draw = ImageDraw.Draw(im_black)
    draw.rectangle([(10, 10), (width - 10, height - 10)], outline="black", width=3)
    draw.text((20, 20), "Inkycal display test", fill="black")
    draw.text((20, 50), f"Model: {model}", fill="black")

    im_colour = Image.new("1", (width, height), "white")
    display = Display(model)
    if "colour" in model:
        display.render(im_black, im_colour)
    else:
        display.render(im_black)
    return 0


def run_menu(ctx: InstallerContext) -> None:
    menu_actions: list[tuple[str, Callable[[], None]]] = [
        ("Install / Repair Inkycal", lambda: install_or_repair(ctx)),
        ("Update Inkycal", lambda: update_inkycal(ctx)),
        (
            "Install / Refresh services",
            lambda: install_services(
                ctx,
                ["127.0.0.1", "0.0.0.0"][choose_option("Web UI bind host", ["127.0.0.1 (localhost only)", "0.0.0.0 (LAN exposed)"])],
            ),
        ),
        ("Configure Pi Zero swap", lambda: setup_swap(ctx, prompt=True)),
        ("Full wipe", lambda: full_wipe(ctx)),
        ("Start services", lambda: service_action("start")),
        ("Stop services", lambda: service_action("stop")),
        ("Restart services", lambda: service_action("restart")),
        ("Display test (60s timeout)", lambda: display_test(ctx, timeout_seconds=60)),
        ("Set timezone (raspi-config)", configure_timezone_via_raspi_config),
        ("Repair permissions", lambda: repair_permissions(ctx)),
        ("Show service status", show_service_status),
        ("Exit", lambda: (_ for _ in ()).throw(SystemExit(0))),
    ]

    while True:
        idx = choose_option("Inkycal installer menu", [label for label, _ in menu_actions])
        action_name, action = menu_actions[idx]
        print(f"\n--- {action_name} ---")
        try:
            action()
        except SystemExit:
            raise
        except Exception as error:
            print(f"Action failed: {error}")
        print("\nPress Enter to continue...")
        input()


def acquire_installer_lock() -> object | None:
    if fcntl is None:
        return None
    lock_file = open("/tmp/inkycal-installer.lock", "w", encoding="utf-8")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        raise RuntimeError("Another installer instance is already running.") from error
    lock_file.write(str(os.getpid()))
    lock_file.flush()
    return lock_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inkycal interactive installer")
    parser.add_argument(
        "--run-display-test-worker",
        metavar="MODEL",
        help="Internal helper mode used by installer to run one display test",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.run_display_test_worker:
        return run_display_test_worker(args.run_display_test_worker)

    repo_root = Path(__file__).resolve().parent
    ctx = detect_context(repo_root)
    lock_handle = acquire_installer_lock()
    try:
        run_menu(ctx)
    finally:
        if lock_handle is not None:
            lock_handle.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
