#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
code = (root / "kraken_control.py").read_text(encoding="utf-8")
privacy = (root / "privacy_logging.py").read_text(encoding="utf-8")
fan = (root / "mainboard_fan_control.py").read_text(encoding="utf-8")

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

# Overview stays fixed and Help/customization stay outside the movable tree.
assert 'page_item("overview", "⌂   Übersicht", 0, fixed=True)' in code
assert 'self.help_button = QPushButton("?  Hilfe")' in code
assert 'self.navigation_customize_button = QPushButton("☷  Navigation anpassen")' in code

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
    assert token in code, token

# Version-like four-part numbers are not blindly redacted as IPv4 addresses.
assert 'Four-part application versions' in privacy
print('3.4.25 navigation, curve editor, CPU default and design-consistency guards passed.')
