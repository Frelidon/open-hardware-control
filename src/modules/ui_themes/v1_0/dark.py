#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dark OHC theme."""

from PySide6.QtGui import QColor, QPalette

from .model import ThemeDefinition


def build_dark_theme(accent: QColor) -> ThemeDefinition:
    """Return dark-theme colors without mutating global Qt state."""

    rgb = f"{accent.red()}, {accent.green()}, {accent.blue()}"
    return ThemeDefinition(
        theme_id="dark",
        title="Dunkel",
        dark=True,
        palette_colors={
            QPalette.ColorRole.Window: "#11161d",
            QPalette.ColorRole.WindowText: "#eef2f7",
            QPalette.ColorRole.Base: "#191f29",
            QPalette.ColorRole.AlternateBase: "#202834",
            QPalette.ColorRole.ToolTipBase: "#202834",
            QPalette.ColorRole.ToolTipText: "#eef2f7",
            QPalette.ColorRole.Text: "#eef2f7",
            QPalette.ColorRole.Button: "#202834",
            QPalette.ColorRole.ButtonText: "#eef2f7",
            QPalette.ColorRole.BrightText: "#ffffff",
            QPalette.ColorRole.Mid: "#98a2b3",
            QPalette.ColorRole.Midlight: "#344054",
            QPalette.ColorRole.Dark: "#090d12",
            QPalette.ColorRole.PlaceholderText: "#667085",
        },
        styles={
            "content": "rgba(17, 22, 29, 166)",
            "panel": "rgba(12, 30, 47, 226)",
            "panel_border": f"rgba({rgb}, 92)",
            "input": "rgba(8, 23, 38, 238)",
            "neutral_button": "rgba(24, 45, 64, 238)",
            "table_header": "rgba(20, 48, 72, 245)",
            "rail_bg": "rgba(7, 19, 31, 248)",
            "rail_border": "rgba(83, 112, 139, 90)",
            "brand_logo_bg": "rgba(2, 8, 15, 205)",
            "brand_logo_border": "rgba(52, 151, 255, 105)",
            "brand_color": "#f2f7fb",
            "sidebar_status_bg": "rgba(15, 31, 47, 220)",
            "sidebar_status_border": "rgba(83, 112, 139, 110)",
            "sidebar_status_color": "#a8b6c5",
            "nav_item_color": "#e8eef5",
            "nav_reset_color": "#d9e4ee",
            "nav_selected_color": accent.lighter(125).name(),
            "design_status_bg": "rgba(11, 35, 54, 220)",
            "design_status_border": "#43b8ff",
            "design_title": "#eaf7ff",
            "design_active": "#54dda1",
            "neutral_status_title": "#d2dbe5",
            "dashboard_neutral_fg": "#c8d2dc",
            "dashboard_neutral_bg": "#44515f",
            "dashboard_meta": "#c4cfda",
            "module_hero_bg": "rgba(11, 28, 45, 218)",
            "curve_overlay_bg": "rgba(8, 23, 38, 244)",
            "fan_detail_bg": "rgba(8, 22, 36, 205)",
            "hardware_row_bg": "rgba(16, 35, 53, 190)",
            "hardware_row_border": "rgba(83, 112, 139, 75)",
            "fan_icon_bg": "rgba(28, 91, 151, 160)",
            "fan_icon_border": "rgba(74, 155, 239, 170)",
            "fan_icon_color": "#d9efff",
            "cooling_metrics": "#c6d0db",
            "ownership_bg": "rgba(75, 49, 12, 150)",
            "ownership_border": "#b87b17",
            "lcd_card": "rgba(12, 30, 47, 218)",
            "lcd_card_hover": "rgba(18, 45, 68, 236)",
            "lcd_card_selected": "rgba(16, 58, 86, 242)",
            "lcd_category": "rgba(17, 36, 54, 218)",
            "lcd_category_selected": "rgba(18, 66, 96, 238)",
        },
    )
