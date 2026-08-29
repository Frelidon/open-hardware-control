from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "kraken_control.py").read_text(encoding="utf-8")
UI = (ROOT / "thermalright_display_ui.py").read_text(encoding="utf-8")
BUILD = (ROOT / "scripts" / "build_release.py").read_text(encoding="utf-8")


def test_thermalright_studio_is_a_full_width_lcd_tile() -> None:
    assert "from thermalright_display_ui import ThermalrightDisplayStudio" in MAIN
    assert '("thermalright", self.thermalright_display_studio, 3)' in MAIN


def test_test_mode_defaults_to_no_usb_writes() -> None:
    assert 'self.settings.value("thermalright/test_mode", True, type=bool)' in UI
    assert "if self.test_mode.isChecked():" in UI
    assert "nur Vorschau, keine USB-Schreibzugriffe" in UI


def test_cutout_and_drag_editor_are_visible() -> None:
    assert "LEVITA_CUTOUT_X" in UI
    assert "ItemIsMovable" in UI
    assert 'cutout_label = self._scene.addSimpleText("NOTCH")' in UI


def test_runtime_package_contains_all_thermalright_modules() -> None:
    assert '"thermalright_cooling.py"' in BUILD
    assert '"thermalright_display.py"' in BUILD
    assert '"thermalright_display_ui.py"' in BUILD
