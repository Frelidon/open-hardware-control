#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bright, high-contrast OHC theme."""

from PySide6.QtGui import QColor, QPalette

from .model import ThemeDefinition


def build_light_theme(accent: QColor) -> ThemeDefinition:
    """Return light-theme colors without mutating global Qt state."""

    rgb = f"{accent.red()}, {accent.green()}, {accent.blue()}"
    return ThemeDefinition(
        theme_id="light",
        title="Hell",
        dark=False,
        palette_colors={
            QPalette.ColorRole.Window: "#f3f6fa",
            QPalette.ColorRole.WindowText: "#17212b",
            QPalette.ColorRole.Base: "#ffffff",
            QPalette.ColorRole.AlternateBase: "#edf2f7",
            QPalette.ColorRole.ToolTipBase: "#ffffff",
            QPalette.ColorRole.ToolTipText: "#17212b",
            QPalette.ColorRole.Text: "#17212b",
            QPalette.ColorRole.Button: "#ffffff",
            QPalette.ColorRole.ButtonText: "#17212b",
            QPalette.ColorRole.BrightText: "#ffffff",
            QPalette.ColorRole.Mid: "#5b6878",
            QPalette.ColorRole.Midlight: "#c7d0dc",
            QPalette.ColorRole.Dark: "#344054",
            QPalette.ColorRole.PlaceholderText: "#718096",
        },
        styles={
            "content": "rgba(247, 249, 252, 248)",
            "panel": "rgba(255, 255, 255, 248)",
            "panel_border": f"rgba({rgb}, 88)",
            "input": "rgba(255, 255, 255, 255)",
            "neutral_button": f"rgba({rgb}, 18)",
            "table_header": f"rgba({rgb}, 30)",
            "rail_bg": "rgba(255, 255, 255, 255)",
            "rail_border": f"rgba({rgb}, 82)",
            "brand_logo_bg": "#f7f9fc",
            "brand_logo_border": f"rgba({rgb}, 88)",
            "brand_color": "#17212b",
            "sidebar_status_bg": "#edf2f7",
            "sidebar_status_border": f"rgba({rgb}, 65)",
            "sidebar_status_color": "#344054",
            "nav_item_color": "#17212b",
            "nav_reset_color": "#344054",
            "nav_selected_color": "#102a43",
            "design_status_bg": "#ffffff",
            "design_status_border": f"rgba({rgb}, 145)",
            "design_title": "#17212b",
            "design_active": "#147a4b",
            "neutral_status_title": "#344054",
            "dashboard_neutral_fg": "#344054",
            "dashboard_neutral_bg": "#dce3eb",
            "dashboard_meta": "#526170",
            "module_hero_bg": f"rgba({rgb}, 16)",
            "curve_overlay_bg": "rgba(255, 255, 255, 252)",
            "fan_detail_bg": "#f8fafc",
            "hardware_row_bg": "rgba(255, 255, 255, 245)",
            "hardware_row_border": "rgba(91, 104, 120, 80)",
            "fan_icon_bg": f"rgba({rgb}, 30)",
            "fan_icon_border": f"rgba({rgb}, 110)",
            "fan_icon_color": "#173b5f",
            "cooling_metrics": "#344054",
            "ownership_bg": "rgba(255, 244, 214, 245)",
            "ownership_border": "#b7791f",
            "lcd_card": "rgba(255, 255, 255, 224)",
            "lcd_card_hover": "rgba(239, 247, 255, 242)",
            "lcd_card_selected": "rgba(224, 241, 255, 248)",
            "lcd_category": "rgba(246, 249, 252, 220)",
            "lcd_category_selected": "rgba(220, 239, 255, 245)",
        },
    )
