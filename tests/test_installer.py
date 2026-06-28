"""Tests for installer helpers."""

from pathlib import Path

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

