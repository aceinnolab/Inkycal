"""Tests for installer helpers."""

from pathlib import Path
from types import SimpleNamespace

import installer


def test_detect_context_returns_paths():
    ctx = installer.detect_context(Path(__file__).resolve().parent.parent)
    assert ctx.repo_root.exists()
    assert ctx.user
    assert str(ctx.python_bin).endswith("venv/bin/python")


def test_render_service_contents_has_expected_fields():
    ctx = installer.detect_context(Path(__file__).resolve().parent.parent)
    service, webui = installer.render_service_contents(ctx, "0.0.0.0")
    assert "WorkingDirectory=" in service
    assert "ExecStart=" in service
    assert "INKYCAL_WEBUI_HOST=0.0.0.0" in webui


def test_install_wiringpi_skips_on_non_linux(monkeypatch, capsys):
    ctx = installer.detect_context(Path(__file__).resolve().parent.parent)
    calls = []

    def fake_run_command(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(installer.sys, "platform", "darwin")
    monkeypatch.setattr(installer, "run_command", fake_run_command)

    installer.install_wiringpi(ctx)

    assert calls == []
    assert "Skipping WiringPi install on non-Linux host." in capsys.readouterr().out


def test_install_wiringpi_runs_clone_and_build(monkeypatch):
    ctx = installer.detect_context(Path(__file__).resolve().parent.parent)
    run_calls = []
    saved_state = []

    def fake_run_command(command, **kwargs):
        run_calls.append((command, kwargs))
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(installer.sys, "platform", "linux")
    monkeypatch.setattr(installer, "run_command", fake_run_command)
    monkeypatch.setattr(installer, "save_state", lambda _ctx, key, value: saved_state.append((key, value)))

    installer.install_wiringpi(ctx)

    assert run_calls[0][0][:3] == ["git", "clone", installer.WIRINGPI_REPO_URL]
    assert run_calls[0][0][3].endswith("/WiringPi")
    assert run_calls[1][0] == ["./build"]
    assert run_calls[1][1]["use_sudo"] is True
    assert run_calls[1][1]["cwd"].name == "WiringPi"
    assert saved_state == [("wiringpi", "ok")]
