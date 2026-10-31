"""Game-display policy tests without inspecting or controlling real windows."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.lcd_runtime.v1_1 import game_probe  # noqa: E402
from modules.snapshot_manager.v1_0.fullscreen_probe import script_source  # noqa: E402


def test_game_probe_respects_independent_fullscreen_switches(monkeypatch) -> None:
    monkeypatch.setattr(game_probe, "running_names", lambda: ())
    monkeypatch.setattr(game_probe, "window_state", lambda: (True, True, "Example"))
    monkeypatch.setattr(game_probe.shutil, "which", lambda _name: None)
    full = game_probe.probe((), detect_fullscreen=True, detect_borderless=False)
    borderless = game_probe.probe((), detect_fullscreen=False, detect_borderless=True)
    assert full["fullscreen"] and not full["borderless"]
    assert not borderless["fullscreen"] and borderless["borderless"]


def test_kwin_bridge_reports_fullscreen_and_borderless_without_writing_windows() -> None:
    source = script_source("io.github.Frelidon.Test")
    assert "w.fullScreen" in source and "w.noBorder" in source
    assert "frameGeometry" in source and "output.geometry" in source
    assert "workspace.activeWindow" in source
    assert "closeWindow" not in source and "w.geometry =" not in source


def test_lcd_surface_has_inline_program_manager_and_default_enabled_signals() -> None:
    source = (ROOT / "src" / "thermalright_display_ui.py").read_text(encoding="utf-8")
    assert "Vollbildanwendungen erkennen" in source
    assert "Rahmenlose Vollbildfenster erkennen" in source
    assert "ProgramManagerPanel" in source
    assert '"thermalright/game_process_paths"' in source
    assert "self.game_program_manager.hide()" in source
