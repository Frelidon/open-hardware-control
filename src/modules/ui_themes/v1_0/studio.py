#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Opaque, animation-free studio themes for the complete OHC interface."""

from PySide6.QtGui import QColor, QPalette

from .model import ThemeDefinition


def _theme(accent: QColor, *, dark: bool) -> ThemeDefinition:
    rgb = f"{accent.red()}, {accent.green()}, {accent.blue()}"
    if dark:
        colors = {
            QPalette.ColorRole.Window: "#070b12",
            QPalette.ColorRole.WindowText: "#eef4fb",
            QPalette.ColorRole.Base: "#111923",
            QPalette.ColorRole.AlternateBase: "#172230",
            QPalette.ColorRole.ToolTipBase: "#172230",
            QPalette.ColorRole.ToolTipText: "#eef4fb",
            QPalette.ColorRole.Text: "#eef4fb",
            QPalette.ColorRole.Button: "#15202c",
            QPalette.ColorRole.ButtonText: "#eef4fb",
            QPalette.ColorRole.BrightText: "#ffffff",
            QPalette.ColorRole.Mid: "#8290a3",
            QPalette.ColorRole.Midlight: "#2b3a4d",
            QPalette.ColorRole.Dark: "#030509",
            QPalette.ColorRole.PlaceholderText: "#7c899b",
        }
        styles = {
            "content": "#0b111a", "panel": "#121b26", "panel_border": "#26384b",
            "input": "#0c141e", "neutral_button": "#172432", "table_header": "#192838",
            "rail_bg": "#070b12", "rail_border": "#1e2b3b", "brand_logo_bg": "#111923",
            "brand_logo_border": f"rgba({rgb}, 105)", "brand_color": "#f3f7fb",
            "sidebar_status_bg": "#111b27", "sidebar_status_border": "#26394d",
            "sidebar_status_color": "#9eacbd", "nav_item_color": "#dce5ef",
            "nav_reset_color": "#aeb9c6", "nav_selected_color": accent.lighter(125).name(),
            "design_status_bg": "#102335", "design_status_border": accent.name(),
            "design_title": "#eef6fd", "design_active": "#54dda1",
            "neutral_status_title": "#d2dbe5", "dashboard_neutral_fg": "#c8d2dc",
            "dashboard_neutral_bg": "#344252", "dashboard_meta": "#bdc8d5",
            "module_hero_bg": "#111e2b", "curve_overlay_bg": "#0d1824",
            "fan_detail_bg": "#0e1823", "hardware_row_bg": "#121e2a",
            "hardware_row_border": "#293a4c", "fan_icon_bg": "#193c5d",
            "fan_icon_border": "#397fba", "fan_icon_color": "#d9efff",
            "cooling_metrics": "#c6d0db", "ownership_bg": "#4b310c",
            "ownership_border": "#b87b17", "studio_shell": "true",
            "lcd_card": "#121b26", "lcd_card_hover": "#172534",
            "lcd_card_selected": "#17334a", "lcd_category": "#111b27",
            "lcd_category_selected": "#173853",
        }
        theme_id, title = "studio-dark", "Studio Schwarz"
    else:
        colors = {
            QPalette.ColorRole.Window: "#eef2f7",
            QPalette.ColorRole.WindowText: "#182332",
            QPalette.ColorRole.Base: "#ffffff",
            QPalette.ColorRole.AlternateBase: "#f1f5f9",
            QPalette.ColorRole.ToolTipBase: "#ffffff",
            QPalette.ColorRole.ToolTipText: "#182332",
            QPalette.ColorRole.Text: "#182332",
            QPalette.ColorRole.Button: "#ffffff",
            QPalette.ColorRole.ButtonText: "#182332",
            QPalette.ColorRole.BrightText: "#ffffff",
            QPalette.ColorRole.Mid: "#607086",
            QPalette.ColorRole.Midlight: "#d3dbe5",
            QPalette.ColorRole.Dark: "#304158",
            QPalette.ColorRole.PlaceholderText: "#758398",
        }
        styles = {
            "content": "#eef2f7", "panel": "#ffffff", "panel_border": "#d3dce7",
            "input": "#ffffff", "neutral_button": "#f1f5f9", "table_header": "#e9eff6",
            "rail_bg": "#ffffff", "rail_border": "#d9e1ea", "brand_logo_bg": "#f7f9fc",
            "brand_logo_border": f"rgba({rgb}, 90)", "brand_color": "#182332",
            "sidebar_status_bg": "#f0f4f8", "sidebar_status_border": "#d3dde8",
            "sidebar_status_color": "#526277", "nav_item_color": "#26364a",
            "nav_reset_color": "#526277", "nav_selected_color": "#173b62",
            "design_status_bg": "#f7fbff", "design_status_border": accent.name(),
            "design_title": "#182332", "design_active": "#147a4b",
            "neutral_status_title": "#344054", "dashboard_neutral_fg": "#344054",
            "dashboard_neutral_bg": "#dfe6ee", "dashboard_meta": "#526170",
            "module_hero_bg": "#f7fbff", "curve_overlay_bg": "#ffffff",
            "fan_detail_bg": "#f7f9fc", "hardware_row_bg": "#ffffff",
            "hardware_row_border": "#d7dfe8", "fan_icon_bg": "#e6f3ff",
            "fan_icon_border": "#82bce8", "fan_icon_color": "#173b5f",
            "cooling_metrics": "#344054", "ownership_bg": "#fff4d6",
            "ownership_border": "#b7791f", "studio_shell": "true",
            "lcd_card": "#ffffff", "lcd_card_hover": "#f2f7fc",
            "lcd_card_selected": "#e4f2ff", "lcd_category": "#f5f7fa",
            "lcd_category_selected": "#e2f1ff",
        }
        theme_id, title = "studio-light", "Studio Hell"
    return ThemeDefinition(
        theme_id=theme_id,
        title=title,
        dark=dark,
        palette_colors=colors,
        styles=styles,
        animated_background_allowed=False,
    )


def build_studio_light_theme(accent: QColor) -> ThemeDefinition:
    return _theme(accent, dark=False)


def build_studio_dark_theme(accent: QColor) -> ThemeDefinition:
    return _theme(accent, dark=True)
