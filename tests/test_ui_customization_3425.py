#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "src"
code = (root / "kraken_control.py").read_text(encoding="utf-8")
theme_controller = (root / "modules/ui_themes/v1_0/controller.py").read_text(encoding="utf-8")
theme_controller += "".join((root / "modules/ui_themes/v1_0" / name).read_text(encoding="utf-8")
                            for name in ("style_base.py", "style_controls.py"))
light_theme = (root / "modules/ui_themes/v1_0/light.py").read_text(encoding="utf-8")
privacy = (root / "privacy_logging.py").read_text(encoding="utf-8")
fan = (root / "mainboard_fan_control.py").read_text(encoding="utf-8")
module_panel = (root / "modules/navigation_settings/v1_0/panel.py").read_text(encoding="utf-8")

# Fixed navigation anchors and editable middle modules.
for token in (
    'NAVIGATION_DEFAULT_ORDER',
    '"☷  Navigation anpassen"',
    '"↺  Standard wiederherstellen"',
    'def toggle_navigation_customization',
    'def reset_navigation_customization',
    'DragDropMode.InternalMove',
    'navigation/hidden',
    'navigation/order',
):
    assert token in code, token
assert "build_module_visibility_settings(self)" in code
assert "MODULE_ROWS" in module_panel
assert "show_all_navigation_modules" in module_panel
assert 'setObjectName("moduleVisibilityCard")' in module_panel
assert 'setObjectName("moduleVisibilitySwitch")' in module_panel
assert 'setObjectName("moduleVisibilityDotOn" if enabled else "moduleVisibilityDotOff")' in module_panel
assert "QFrame#moduleVisibilityCard" in theme_controller
assert "QCheckBox#moduleVisibilitySwitch::indicator:checked" in theme_controller

# Overview stays fixed and Help/customization stay outside the movable tree.
assert 'page_item("overview", "⌂   Übersicht", 0, fixed=True)' in code
assert 'self.help_button = QPushButton("?  Hilfe")' in code
assert 'self.navigation_customize_button = QPushButton("☷  Navigation anpassen")' in code
assert '"wallpaper_engine": ("▧   Wallpaper Engine", 9)' in code
assert 'self.tabs.addTab(self.make_wallpaper_engine_tab(), "Wallpaper Engine")' in code
assert '"cooling", "rgb_studio", "lcd", "wallpaper_engine", "openlinkhub"' in code
assert '"profiles", "settings", "about", "log", "desktop_designs"' in code
assert 'NAVIGATION_LEGACY_DEFAULTS' in code
assert '"rail_bg": "rgba(255, 255, 255, 255)"' in light_theme
assert '"nav_item_color": "#17212b"' in light_theme
assert "QTreeWidget#hardwareNavigation::item {{" in theme_controller
assert "self.navigation.setPalette(nav_palette)" in theme_controller
assert "QPushButton#navigationCustomizeButton, QPushButton#helpNavigationButton" in theme_controller

# Cooling icon adapts to AIO / chassis-fan detection.
assert 'icon = "▥◉" if has_aio and has_case_fans' in code

# 3.4.25 case-fan curve editing is embedded, draggable and still table-backed.
assert 'def make_mainboard_curve_overlay' in code
assert 'CurveEditor(self._mainboard_default_curve(), 25, "Gehäuselüfter")' in code
assert 'def open_mainboard_curve_dialog' in code
curve_method = code.split('def open_mainboard_curve_dialog', 1)[1].split('@staticmethod\n    def mainboard_source_label', 1)[0]
assert 'QDialog(' not in curve_method
assert 'mainboard_curve_overlay_table' in code
assert 'pointsChanged.connect(self.update_mainboard_curve_overlay_table)' in code

# CPU temperature is the chassis-fan default for every built-in preset.
assert fan.count('source="cpu"') >= 3
assert 'source="max"' not in fan.split('MAINBOARD_FAN_PRESETS', 1)[1].split('def fan_preset', 1)[0]
assert 'source_default_cpu_3425' in code

# Shared modern page design is applied beyond Overview/Cooling.
assert 'def make_module_hero' in code
for title in (
    '"RGB-Studio"', '"LCD"', '"Profile"', '"Log & Diagnose"',
    '"Corsair · OpenLinkHub"', '"Einstellungen"', '"Über Open Hardware Control"', '"Hilfe & Anleitungen"',
):
    assert title in code, title

# Detail panels, editors and tables share the same blue-tinted card language.
for token in (
    'panel_rgba =',
    'panel_border_rgba =',
    'QTableWidget, QPlainTextEdit, QTextEdit, QTextBrowser, QListWidget',
    'QHeaderView::section',
    'background: {panel_rgba};',
):
    assert token in theme_controller, token

# Version-like four-part numbers are not blindly redacted as IPv4 addresses.
assert 'Four-part application versions' in privacy
print('3.4.25 navigation, curve editor, CPU default and design-consistency guards passed.')
