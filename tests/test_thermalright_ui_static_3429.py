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
    assert 'cutout_label = self._scene.addSimpleText(f"NOTCH · {cutout_width} px")' in UI


def test_broken_trcc_split_modes_are_clearly_preview_only() -> None:
    assert "Stil A · derzeit nur Vorschau" in UI
    assert "TRCC Linux 9.9.11 bricht sie" in UI
    assert 'self.settings.value("thermalright/split_mode", 0)' in UI


def test_real_notch_mask_and_background_movement_are_user_adjustable() -> None:
    assert "Schwarzen Balken wirklich auf das Display legen" in UI
    assert "Breiter Standard · 320 px und Bild nach links" in UI
    assert "prepare_shifted_media(" in UI
    assert "create_black_notch_mask(" in UI


def test_overlay_spacing_presets_remain_individually_editable() -> None:
    assert "Zwei saubere Reihen" in UI
    assert "Untereinander" in UI
    assert 'self.apply_overlay_layout("two_rows")' in UI


def test_runtime_package_contains_all_thermalright_modules() -> None:
    assert '"thermalright_cooling.py"' in BUILD
    assert '"thermalright_display.py"' in BUILD
    assert '"thermalright_display_ui.py"' in BUILD
