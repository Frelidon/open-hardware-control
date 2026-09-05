#!/usr/bin/env python3
"""Regression guards for the embedded RGB Studio controls."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODE = (ROOT / "kraken_control.py").read_text(encoding="utf-8")
GALLERY = (ROOT / "modules" / "rgb_studio" / "v1_1" / "design_gallery.py").read_text(
    encoding="utf-8"
)


def test_engine_controls_are_embedded_toggle_buttons() -> None:
    rgb_ui = CODE[CODE.index("    def make_rgb_tab("):CODE.index("    def show_rgb_setup_wizard(")]
    assert 'QPushButton("RGB-Steuerung · AUS")' in rgb_ui
    assert 'QPushButton("Startprofil-Automatik · AUS")' in rgb_ui
    assert 'QPushButton("Automatische Wiederübernahme · AUS")' in rgb_ui
    assert "devices_effects_layout.addWidget(openrgb_box)" in rgb_ui
    assert '("engine", openrgb_box)' not in rgb_ui


def test_color_context_menu_uses_persisted_effect_colors() -> None:
    assert "design_context_requested = Signal(int, QPoint)" in GALLERY
    assert "from modules.rgb_studio.v1_1 import (" in CODE
    menu = CODE[
        CODE.index("    def show_rgb_effect_color_menu("):
        CODE.index("    def request_rgb_direct_apply(")
    ]
    assert "color_count = effect_color_count(effect_id)" in menu
    assert 'self.rgb_right_click_hint_label.setText(hint)' in menu
    assert 'kein separates Popup-Fenster' in menu
    assert '"rgb_studio/design_color_overrides"' in CODE
    assert "self.rgb_design_overrides[data] = self.current_rgb_studio_config()" in CODE


def test_brightness_native_results_and_sequence_cleanup_stay_in_page() -> None:
    rgb_ui = CODE[CODE.index("    def make_rgb_tab("):CODE.index("    def show_rgb_setup_wizard(")]
    assert "self.rgb_studio_brightness = QSlider(Qt.Orientation.Horizontal)" in rgb_ui
    assert "self.rgb_studio_brightness.setRange(0, 100)" in rgb_ui
    assert 'QLabel("Gesamthelligkeit")' in rgb_ui
    assert 'setHeaderLabels(["Gerät / Kanal", "Hardwaremodus", "Status"])' in rgb_ui
    sequence = CODE[
        CODE.index("    def run_rgb_command_sequence("):
        CODE.index("    def run_openrgb_write(")
    ]
    assert sequence.count("finished(False)") >= 3
