#!/usr/bin/env python3
"""Regression guards for the embedded RGB Studio controls."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODE = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
GALLERY = (ROOT / "src/modules" / "rgb_studio" / "v1_15" / "design_gallery.py").read_text(
    encoding="utf-8"
)
PANELS = (ROOT / "src/modules" / "rgb_studio" / "v1_15" / "studio_panels.py").read_text(
    encoding="utf-8"
)


def test_engine_controls_are_embedded_toggle_buttons() -> None:
    rgb_ui = CODE[CODE.index("    def make_rgb_tab("):CODE.index("    def show_rgb_setup_wizard(")]
    assert 'QPushButton("RGB-Steuerung · AUS")' in rgb_ui
    assert 'QPushButton("Startprofil-Automatik · AUS")' in rgb_ui
    assert 'QPushButton("Automatische Wiederübernahme · AUS")' in rgb_ui
    assert "rgb_devices_effects_panel_layout.addWidget(openrgb_box)" in rgb_ui
    assert "devices_effects_layout.addWidget(self.rgb_devices_effects_panel)" in rgb_ui
    assert '("engine", openrgb_box)' not in rgb_ui


def test_animated_gallery_replaces_redundant_preview_and_precedes_device_details() -> None:
    rgb_ui = CODE[CODE.index("    def make_rgb_tab("):CODE.index("    def show_rgb_setup_wizard(")]
    gallery = rgb_ui.index("layout.addWidget(design_gallery_box)")
    sections = rgb_ui.index("section_container, self.rgb_section_area")
    pc_view = rgb_ui.index('(\"pc_layout\", pc_layout_box)', sections)
    devices = rgb_ui.index('(\"devices_effects\", devices_effects_box)', sections)
    assert gallery < sections < pc_view < devices
    assert 'QGroupBox("Live-Vorschau")' not in rgb_ui
    assert "self.rgb_studio_preview = RGBEffectPreview()" not in rgb_ui
    assert "rgb_devices_effects_panel_layout.addWidget(design_gallery_box)" not in rgb_ui


def test_gallery_text_is_bounded_and_visible_cards_only_are_painted() -> None:
    assert "base_font = QFont(painter.font())" in GALLERY
    assert "title_font.setPixelSize(13)" in GALLERY
    assert "QFontMetrics(title_font).elidedText" in GALLERY
    assert "if not area.intersects(exposed)" in GALLERY
    assert "bucket = int(value * 10.0)" in GALLERY


def test_color_context_menu_uses_persisted_effect_colors() -> None:
    assert "design_context_requested = Signal(int, QPoint)" in GALLERY
    assert "from modules.rgb_studio.v1_15 import (" in CODE
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
    assert 'setHeaderLabels(["Gerät / Kanal", "Hardwaremodus", "Status"])' in PANELS
    assert "self.rgb_devices_effects_toggle = QPushButton" in rgb_ui
    assert "set_rgb_devices_effects_expanded" in rgb_ui
    assert "def set_rgb_native_results_expanded" in PANELS
    assert "tree.setMinimumHeight(320)" in PANELS
    assert "Kein Extra-Fenster" in rgb_ui
    assert "build_native_hardware_channel_panel" in rgb_ui
    assert "self.rgb_native_results_button.setChecked(False)" not in CODE
    assert "self.rgb_native_results_button.setChecked(False)" not in PANELS
    sequence = CODE[
        CODE.index("    def run_rgb_command_sequence("):
        CODE.index("    def run_openrgb_write(")
    ]
    assert sequence.count("finished(False)") >= 3
