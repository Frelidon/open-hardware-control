#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Qt application-theme controller shared by all registered OHC visual themes."""

from __future__ import annotations

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

from .registry import resolve_theme
from .style_base import base_widget_stylesheet
from .style_controls import control_widget_stylesheet


class UiThemeMixin:
    """Apply a registered palette and the shared widget language to the host window."""

    def apply_theme(self) -> None:
        app = QApplication.instance()
        if app is None:
            return
        accent = QColor(self.accent_hex)
        if not accent.isValid():
            accent = QColor("#00aaff")
            self.accent_hex = accent.name()

        theme = resolve_theme(self.theme_mode, self.system_palette, accent)
        palette = QPalette() if theme.palette_colors else QPalette(self.system_palette)
        for role, value in theme.palette_colors.items():
            palette.setColor(role, QColor(value))

        palette.setColor(QPalette.ColorRole.Highlight, accent)
        palette.setColor(QPalette.ColorRole.Link, accent)
        highlighted_text = QColor("#111111") if accent.lightness() > 155 else QColor("#ffffff")
        palette.setColor(QPalette.ColorRole.HighlightedText, highlighted_text)
        app.setPalette(palette)

        scale = self.ui_scale_percent / 100.0
        app_font = QFont(self.base_font)
        base_point = self.base_font.pointSizeF() if self.base_font.pointSizeF() > 0 else 10.0
        app_font.setPointSizeF(max(8.0, base_point * scale))
        app.setFont(app_font)
        hover = accent.lighter(118) if theme.dark else accent.darker(108)
        pressed = accent.darker(125)
        styles = theme.styles
        content_rgba = styles["content"]
        panel_rgba = styles["panel"]
        panel_border_rgba = styles["panel_border"]
        input_rgba = styles["input"]
        neutral_button_rgba = styles["neutral_button"]
        table_header_rgba = styles["table_header"]
        rail_bg = styles["rail_bg"]
        rail_border = styles["rail_border"]
        brand_logo_bg = styles["brand_logo_bg"]
        brand_logo_border = styles["brand_logo_border"]
        brand_color = styles["brand_color"]
        sidebar_status_bg = styles["sidebar_status_bg"]
        sidebar_status_border = styles["sidebar_status_border"]
        sidebar_status_color = styles["sidebar_status_color"]
        nav_item_color = styles["nav_item_color"]
        nav_reset_color = styles["nav_reset_color"]
        nav_selected_color = styles["nav_selected_color"]
        design_status_bg = styles["design_status_bg"]
        design_status_border = styles["design_status_border"]
        design_title = styles["design_title"]
        design_active = styles["design_active"]
        neutral_status_title = styles["neutral_status_title"]
        dashboard_neutral_fg = styles["dashboard_neutral_fg"]
        dashboard_neutral_bg = styles["dashboard_neutral_bg"]
        dashboard_meta = styles["dashboard_meta"]
        module_hero_bg = styles["module_hero_bg"]
        curve_overlay_bg = styles["curve_overlay_bg"]
        fan_detail_bg = styles["fan_detail_bg"]
        hardware_row_bg = styles["hardware_row_bg"]
        hardware_row_border = styles["hardware_row_border"]
        fan_icon_bg = styles["fan_icon_bg"]
        fan_icon_border = styles["fan_icon_border"]
        fan_icon_color = styles["fan_icon_color"]
        cooling_metrics = styles["cooling_metrics"]
        ownership_bg = styles["ownership_bg"]
        ownership_border = styles["ownership_border"]
        lcd_card = styles["lcd_card"]
        lcd_card_hover = styles["lcd_card_hover"]
        lcd_card_selected = styles["lcd_card_selected"]
        lcd_category = styles["lcd_category"]
        lcd_category_selected = styles["lcd_category_selected"]
        # These rules intentionally finish the style sheet for every theme.
        # Several older module rules used dark literal colors, which made the
        # regular light theme and studio-light look almost identical and left
        # pale pages with dark grey islands.
        themed_surface_overrides = f"""
            QFrame#gpuHeroCard, QFrame#gpuMetricCard, QWidget#gpuToolbar,
            QGroupBox#gpuWorkspaceColumn, QFrame#gpuTuningRow,
            QGroupBox#gpuWorkflowCard, QGroupBox#gpuActionCard,
            QGroupBox#gpuProfileCard, QGroupBox#gpuArtworkCard, QGroupBox#gpuOwnershipCard,
            QGroupBox#gpuControlCard, QGroupBox#gpuPreviewCard,
            QFrame#snapshotMetricCard, QFrame#snapshotWorkspaceCard,
            QFrame#automationSummaryCard, QFrame#automationWorkspaceCard {{
                background: {panel_rgba}; border: 1px solid {panel_border_rgba}; border-radius: 11px;
            }}
            QLabel#gpuHeroTitle, QLabel#gpuMetricTitle, QLabel#gpuMetricValue,
            QLabel#gpuDeviceHeading, QLabel#gpuTuningLabel, QLabel#gpuWorkflowStatus,
            QLabel#gpuStressMetric, QGroupBox#gpuWorkspaceColumn,
            QGroupBox#gpuWorkspaceColumn QLabel, QGroupBox#gpuControlCard QLabel,
            QGroupBox#gpuPreviewCard QLabel {{ color: palette(window-text); }}
            QGroupBox#gpuWorkspaceColumn QComboBox, QGroupBox#gpuWorkspaceColumn QSpinBox,
            QGroupBox#gpuWorkspaceColumn QDoubleSpinBox, QSpinBox#gpuTuningSpin,
            QDoubleSpinBox#gpuTuningSpin, QSpinBox#gpuFanSpin, QSpinBox#gpu_fan_static_speed,
            QDoubleSpinBox#caseDistanceSpin, QSpinBox#snapshotMetricSpin {{
                color: palette(text); background: {input_rgba}; border: 1px solid {panel_border_rgba};
            }}
            QTabWidget#gpuSections QTabBar::tab {{
                color: palette(window-text); background: {neutral_button_rgba}; border-color: {panel_border_rgba};
            }}
            QTabWidget#gpuSections QTabBar::tab:selected {{
                color: white; background: {accent.name()}; border-color: {accent.name()};
            }}
            QFrame#snapshotMetricCard {{
                background: {panel_rgba}; border-color: {panel_border_rgba};
            }}
            QSpinBox#snapshotMetricSpin {{
                color: palette(text); background: {input_rgba}; border-color: {panel_border_rgba};
            }}
            QToolButton#lcdDesignCard {{
                padding: 5px; border: 1px solid {panel_border_rgba}; border-radius: 10px;
                background: {lcd_card}; color: palette(window-text);
            }}
            QToolButton#lcdDesignCard:hover {{
                border-color: {accent.name()}; background: {lcd_card_hover}; color: palette(window-text);
            }}
            QToolButton#lcdDesignCard:checked {{
                border: 2px solid {accent.name()}; background: {lcd_card_selected}; color: palette(window-text);
                font-weight: 700;
            }}
            QToolButton#lcdCategoryButton {{
                padding: 7px 11px; border: 1px solid {panel_border_rgba}; border-radius: 9px;
                background: {lcd_category}; color: palette(window-text);
            }}
            QToolButton#lcdCategoryButton:hover {{ border-color: {accent.name()}; }}
            QToolButton#lcdCategoryButton:checked {{
                border: 1px solid {accent.name()}; background: {lcd_category_selected};
                color: palette(window-text); font-weight: 750;
            }}
            """
        base_px = max(10, round(12 * scale))
        title_px = max(19, round(23 * scale))
        card_px = max(18, round(22 * scale))
        style_context = locals()
        self.setStyleSheet(base_widget_stylesheet(**style_context) + control_widget_stylesheet(**style_context))
        if hasattr(self, "navigation"):
            nav_palette = QPalette(palette)
            nav_palette.setColor(QPalette.ColorRole.Text, QColor(nav_item_color))
            nav_palette.setColor(QPalette.ColorRole.WindowText, QColor(nav_item_color))
            nav_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(nav_selected_color))
            self.navigation.setPalette(nav_palette)
        if hasattr(self, "pump_curve_table"):
            self.pump_curve_table[2].set_accent_color(accent)
        if hasattr(self, "fan_curve_table"):
            self.fan_curve_table[2].set_accent_color(accent)
        if hasattr(self, "design_preview"):
            self.design_preview.setText(
                f"{self.theme_mode_combo.currentText()} · Akzent {self.accent_hex} · Skalierung {self.ui_scale_percent} %"
            )
        if hasattr(self, "background_widget"):
            blocked = not theme.animated_background_allowed
            self._animated_background_theme_blocked = blocked
            self.background_widget.configure(
                enabled=self.background_enabled and not blocked,
                theme=self.background_theme,
                fps=self.background_fps,
                intensity=self.background_intensity,
                pause_inactive=self.background_pause_inactive,
            )
            self.ensure_background_layer_order()
            if hasattr(self, "background_enabled_checkbox"):
                self.background_enabled_checkbox.setEnabled(not blocked)
                self.background_theme_combo.setEnabled(not blocked)
                self.background_fps_combo.setEnabled(not blocked)
                self.background_intensity_slider.setEnabled(not blocked)
                self.background_pause_checkbox.setEnabled(not blocked)
            if hasattr(self, "background_theme_notice"):
                self.background_theme_notice.setVisible(blocked)
        if hasattr(self, "dashboard_cards_layout"):
            self.adapt_dashboard_layout()
