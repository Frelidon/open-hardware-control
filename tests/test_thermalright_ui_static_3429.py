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
    assert 'self.settings.value("thermalright/split_mode", 3)' in UI


def test_real_notch_mask_and_background_movement_are_user_adjustable() -> None:
    assert "Schwarzen Balken wirklich auf das Display legen" in UI
    assert "Levita-Standard · 80 px und Bild zentriert" in UI
    assert "prepare_shifted_media(" in UI
    assert "create_black_notch_mask(" in UI
    assert "_MovableNotchItem" in UI
    assert "Einpassen · vollständig und unverzerrt" in UI


def test_overlay_spacing_presets_remain_individually_editable() -> None:
    assert "Zwei saubere Reihen" in UI
    assert "Untereinander" in UI
    assert 'self.apply_overlay_layout("two_rows")' in UI
    assert "Letzten Zustand wiederherstellen" in UI


def test_runtime_package_contains_all_thermalright_modules() -> None:
    assert '"thermalright_cooling.py"' in BUILD
    assert '"thermalright_display.py"' in BUILD
    assert '"thermalright_display_ui.py"' in BUILD


def test_lcd_tiles_follow_detected_display_shape_and_collapse_kraken_importer() -> None:
    assert "def update_lcd_hardware_layout" in MAIN
    assert 'area.set_key_visible("preview", has_kraken)' in MAIN
    assert 'area.set_key_visible("thermalright", thermalright_present)' in MAIN
    assert "def set_kraken_importer_expanded" in MAIN
    assert "eingeklappt · zum Aktivieren anklicken" in MAIN


def test_openrgb_crash_is_quarantined_and_ui_tests_disable_hardware_io() -> None:
    assert 'os.environ.get("OHC_DISABLE_HARDWARE_IO") == "1"' in MAIN
    assert "self.openrgb_engine_crash_quarantined = True" in MAIN
    assert "automatischer Neustart gesperrt" in MAIN
