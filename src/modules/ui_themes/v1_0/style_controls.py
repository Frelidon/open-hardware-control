# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure shared Qt widget stylesheet fragments."""
from __future__ import annotations

def control_widget_stylesheet(*, accent, base_px, brand_color, brand_logo_bg, brand_logo_border, card_px, content_rgba, cooling_metrics, curve_overlay_bg, dashboard_meta, dashboard_neutral_bg, dashboard_neutral_fg, design_active, design_status_bg, design_status_border, design_title, fan_detail_bg, fan_icon_bg, fan_icon_border, fan_icon_color, hardware_row_bg, hardware_row_border, highlighted_text, hover, input_rgba, module_hero_bg, nav_item_color, nav_reset_color, nav_selected_color, neutral_button_rgba, neutral_status_title, ownership_bg, ownership_border, panel_border_rgba, panel_rgba, pressed, rail_bg, rail_border, sidebar_status_bg, sidebar_status_border, sidebar_status_color, table_header_rgba, themed_surface_overrides, title_px, **_unused) -> str:
    return f"""                border: 2px solid #2fbf71;
                background: #238b55;
                color: #ffffff;
                font-weight: 750;
            }}
            QPushButton#coolingModeButton[coolingState="active"]:hover {{
                border-color: #59d992;
                background: #238b55;
                color: #ffffff;
            }}
            QPushButton#coolingModeButton[coolingState="active"]:pressed {{
                border-color: #8aefb7;
                background: #1b6f44;
                color: #ffffff;
            }}
            QPushButton#coolingQuickProfileButton[profileState="active"] {{
                border: 2px solid {accent.lighter(125).name()};
                background: {accent.name()};
                color: #ffffff;
                font-weight: 800;
            }}
            QPushButton#coolingQuickProfileButton[profileState="active"]:hover {{
                border-color: {accent.lighter(140).name()};
                background: {hover.name()};
                color: #ffffff;
            }}
            QPushButton#coolingQuickProfileButton[profileState="active"]:pressed {{
                border-color: {accent.lighter(150).name()};
                background: {pressed.name()};
                color: #ffffff;
            }}
            QPushButton:focus, QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTableWidget:focus {{
                border: 2px solid {accent.name()};
            }}
            QTabWidget::pane {{ border: 1px solid {panel_border_rgba}; border-radius: 8px; background: {panel_rgba}; }}
            QScrollArea#settingsScrollArea {{ border: none; background: transparent; }}
            QScrollArea#settingsScrollArea > QWidget > QWidget {{ background: transparent; }}
            QWidget#settingsContent {{ background: transparent; }}
            QTabBar::tab {{ padding: 9px 16px; border-bottom: 2px solid transparent; }}
            QTabBar::tab:selected {{ font-weight: 700; color: {accent.name()}; border-bottom-color: {accent.name()}; }}
            QTreeWidget#hardwareNavigation {{
                border: 1px solid {panel_border_rgba};
                border-radius: 10px;
                background: {panel_rgba};
                padding: 7px;
            }}
            QTableWidget, QPlainTextEdit, QTextEdit, QTextBrowser, QListWidget {{
                border: 1px solid {panel_border_rgba};
                border-radius: 7px;
                background: {input_rgba};
                alternate-background-color: {panel_rgba};
                selection-background-color: {accent.name()};
                selection-color: #ffffff;
            }}
            QTableWidget#diagnosticTable, QTreeWidget#sensorSelectionTree {{
                border: 1px solid {panel_border_rgba}; border-radius: 10px;
                background: {input_rgba}; alternate-background-color: {panel_rgba};
                selection-background-color: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 65);
                selection-color: palette(window-text);
            }}
            QTableWidget#diagnosticTable::item, QTreeWidget#sensorSelectionTree::item {{
                padding: 6px 10px; border-bottom: 1px solid {panel_border_rgba};
            }}
            QTableWidget#diagnosticTable::item:hover, QTreeWidget#sensorSelectionTree::item:hover {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 28);
            }}
            QHeaderView::section {{
                border: none;
                border-right: 1px solid {panel_border_rgba};
                border-bottom: 1px solid {panel_border_rgba};
                padding: 7px;
                background: {table_header_rgba};
                font-weight: 700;
            }}
            QLineEdit, QComboBox, QSpinBox {{
                padding: 6px;
                border: 1px solid {panel_border_rgba};
                border-radius: 6px;
                background: {input_rgba};
            }}
            QComboBox {{ padding-right: 28px; min-height: 24px; }}
            QComboBox::drop-down {{
                subcontrol-origin: padding; subcontrol-position: top right;
                width: 27px; border: none; border-left: 1px solid {panel_border_rgba};
                background: {neutral_button_rgba};
            }}
            QComboBox:hover {{ border-color: {accent.name()}; }}
            QComboBox QAbstractItemView {{
                color: palette(text); background: {input_rgba};
                border: 1px solid {panel_border_rgba}; border-radius: 8px;
                padding: 5px; outline: 0;
                selection-background-color: {accent.name()};
                selection-color: {highlighted_text.name()};
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 28px; padding: 5px 9px; border-radius: 5px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 34);
            }}
            QComboBox QAbstractItemView::item:disabled {{ color: palette(mid); }}
            QFrame#navigationRail {{
                background: {rail_bg};
                border: 1px solid {rail_border};
                border-radius: 12px;
            }}
            QLabel#brandLogo {{
                background: {brand_logo_bg}; border: 1px solid {brand_logo_border};
                border-radius: 12px; padding: 4px;
            }}
            QLabel#brandLabel {{ font-size: 17px; font-weight: 750; padding: 3px 8px 8px 8px; color: {brand_color}; }}
            QLabel#sidebarServiceStatus {{
                color: {sidebar_status_color}; border: 1px solid {sidebar_status_border};
                border-radius: 9px; padding: 9px; background: {sidebar_status_bg};
            }}
            QLabel#pageTitle {{ font-size: {title_px}px; font-weight: 800; color: palette(window-text); }}
            QLabel#sectionTitle, QLabel#fanCardTitle, QLabel#coolingCardTitle, QLabel#dialogTitle {{ font-size: 16px; font-weight: 780; }}
            QLabel#heroTitle {{ font-size: {title_px}px; font-weight: 830; }}
            QLabel#snapshotStateBadge {{
                color: {accent.lighter(128).name()}; border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 125);
                border-radius: 9px; padding: 8px 12px; background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 30);
                font-weight: 800;
            }}
            QFrame#snapshotMetricCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(8, 27, 48, 235), stop:1 rgba({accent.red()}, {accent.green()}, {accent.blue()}, 24));
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 95);
                border-radius: 11px;
            }}
            QFrame#snapshotMetricCard:hover {{
                border-color: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 175);
            }}
            QLabel#snapshotMetricLabel {{ color: palette(window-text); font-size: 14px; font-weight: 800; }}
            QLabel#snapshotMetricHint {{ color: palette(mid); font-size: 11px; }}
            QSpinBox#snapshotMetricSpin {{
                min-height: 28px; padding: 5px 8px; color: {accent.lighter(135).name()};
                background: rgba(2, 14, 28, 185); border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 135);
                border-radius: 8px; font-size: 14px; font-weight: 850;
            }}
            QSlider#snapshotMetricSlider::groove:horizontal {{
                height: 7px; border-radius: 3px; background: rgba(76, 101, 128, 105);
            }}
            QSlider#snapshotMetricSlider::sub-page:horizontal {{
                border-radius: 3px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {accent.darker(112).name()}, stop:1 {accent.lighter(120).name()});
            }}
            QSlider#snapshotMetricSlider::handle:horizontal {{
                width: 17px; margin: -6px 0; border-radius: 8px;
                background: white; border: 3px solid {accent.name()};
            }}
            QCheckBox#snapshotToggle {{
                padding: 6px 8px; border-radius: 7px;
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 12);
            }}
            QFrame#snapshotTimePicker {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 14);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 78);
                border-radius: 10px;
            }}
            QLabel#snapshotTimeValue {{
                color: {accent.lighter(128).name()}; font-size: 16px; font-weight: 850;
                padding: 4px 10px; border-radius: 7px;
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 24);
            }}
            QSlider#snapshotTimeSlider::groove:horizontal {{
                height: 8px; border-radius: 4px; background: rgba(76, 101, 128, 105);
            }}
            QSlider#snapshotTimeSlider::sub-page:horizontal {{
                border-radius: 4px; background: {accent.name()};
            }}
            QSlider#snapshotTimeSlider::handle:horizontal {{
                width: 18px; margin: -6px 0; border-radius: 9px;
                background: white; border: 3px solid {accent.name()};
            }}
            QPushButton#snapshotSecondaryAction {{
                color: {accent.lighter(125).name()}; border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 130);
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 20); font-weight: 750;
            }}
            QPushButton#snapshotSecondaryAction:hover {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 42);
            }}
            QLabel#accentText {{ color: {accent.name()}; font-weight: 700; }}
            QLabel#metricStatusDot {{ color: #63d76a; font-weight: 900; }}
            QLabel#metricStatusBad {{ color: #e05a5a; font-weight: 900; }}
            QLabel#dashboardStatusTitle {{ color: #63d76a; font-size: 16px; font-weight: 800; }}
            QLabel#dashboardStatusNeutralTitle {{ color: {neutral_status_title}; font-size: 16px; font-weight: 780; }}
            QLabel#dashboardStatusIcon {{
                color: white; background: #4aaa4f; border-radius: 18px; font-size: 20px; font-weight: 900;
            }}
            QLabel#dashboardStatusNeutral {{
                color: {dashboard_neutral_fg}; background: {dashboard_neutral_bg}; border-radius: 18px; font-size: 18px; font-weight: 800;
            }}
            QLabel#dashboardMeta {{ color: {dashboard_meta}; min-width: 110px; }}
            QFrame#dashboardStatusBanner, QFrame#dashboardSection, QFrame#coolingSummaryCard,
            QFrame#fanChannelCard, QFrame#fanChannelCardSelected, QFrame#fanInlineDetail,
            QFrame#moduleHeroCard, QFrame#curveOverlayCard, QFrame#settingsCard {{
                background: {panel_rgba};
                border: 1px solid {panel_border_rgba};
                border-radius: 11px;
            }}
            QFrame#settingsCard {{ padding: 4px; }}
            QFrame#moduleHeroCard {{
                border-left: 3px solid {accent.name()};
                background: {module_hero_bg};
            }}
            QFrame#curveOverlayCard {{
                border: 2px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 155);
                background: {curve_overlay_bg};
            }}
            QLabel#moduleHeroIcon {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 45);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 115);
                border-radius: 10px; color: {accent.lighter(128).name()}; font-size: 21px; font-weight: 800;
            }}
            QLabel#moduleHeroBadge {{
                color: {accent.lighter(125).name()}; border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 110);
                border-radius: 8px; padding: 5px 8px; background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 24);
                font-weight: 700;
            }}
            QLabel#featureLifecycleBadge {{
                color: {accent.lighter(125).name()};
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 92);
                border-radius: 7px; padding: 2px 6px;
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 18);
                font-size: 11px; font-weight: 700;
            }}
            QFrame#fanChannelCardSelected {{ border: 1px solid {accent.name()}; }}
            QFrame#fanInlineDetail {{ background: {fan_detail_bg}; }}
            QFrame#hardwareListRow {{
                background: {hardware_row_bg}; border: 1px solid {hardware_row_border}; border-radius: 8px;
            }}
            QFrame#moduleVisibilityCard {{
                background: {hardware_row_bg}; border: 1px solid {hardware_row_border}; border-radius: 9px;
            }}
            QFrame#moduleVisibilityCard:hover {{
                border-color: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 125);
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 18);
            }}
            QLabel#moduleVisibilityIcon {{
                color: {accent.lighter(128).name()};
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 34);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 88);
                border-radius: 8px; font-size: 16px; font-weight: 800;
            }}
            QLabel#moduleVisibilityTitle {{ font-weight: 750; }}
            QLabel#moduleVisibilityDotOn {{ color: #63d76a; font-size: 16px; font-weight: 900; }}
            QLabel#moduleVisibilityDotOff {{ color: #738294; font-size: 16px; font-weight: 800; }}
            QCheckBox#moduleVisibilitySwitch {{ spacing: 0; padding: 0; }}
            QCheckBox#moduleVisibilitySwitch::indicator {{
                width: 36px; height: 18px; border-radius: 9px;
                border: 1px solid rgba(120, 140, 160, 155); background: rgba(70, 82, 94, 190);
            }}
            QCheckBox#moduleVisibilitySwitch::indicator:hover {{
                border-color: {accent.lighter(118).name()};
            }}
            QCheckBox#moduleVisibilitySwitch::indicator:checked {{
                border-color: {accent.lighter(118).name()}; background: {accent.name()};
            }}
            QPushButton#moduleVisibilityReset {{ min-width: 190px; }}
            QLabel#fanCardIcon {{
                background: {fan_icon_bg}; border: 1px solid {fan_icon_border};
                border-radius: 8px; color: {fan_icon_color}; font-size: 18px;
            }}
            QLabel#coolingMetrics {{ color: {cooling_metrics}; padding: 4px 0; }}
            QFrame#coolingDashboard {{ background: transparent; border: none; }}
            QGroupBox#ownershipBanner {{
                border: 1px solid {ownership_border}; background: {ownership_bg}; border-radius: 9px;
            }}
            QPushButton#primaryAction, QPushButton#primaryDashboardAction, QPushButton#profilePrimary {{
                background: {accent.name()}; color: white; border: 1px solid {accent.lighter(118).name()}; font-weight: 750;
            }}
            QPushButton#primaryAction:hover, QPushButton#primaryDashboardAction:hover, QPushButton#profilePrimary:hover {{
                background: {hover.name()}; color: white;
            }}
            QPushButton#dangerAction {{
                background: rgba(224, 90, 90, 28); color: #e76b6b;
                border: 1px solid rgba(224, 90, 90, 125); font-weight: 720;
            }}
            QPushButton#dangerAction:hover {{ background: rgba(224, 90, 90, 52); color: #ff8b8b; }}
            QPushButton#dashboardAction {{ text-align: left; min-height: 48px; }}
            QPushButton#headerActionButton {{ min-height: 34px; }}
            QPushButton#headerMoreButton {{ font-size: 20px; padding: 4px; }}
            QFrame#valueCard {{ min-width: 135px; }}
            QTreeWidget#hardwareNavigation {{ border: none; background: transparent; padding: 2px; color: {nav_item_color}; }}
            QTreeWidget#hardwareNavigation::item {{
                min-height: 38px; padding: 4px 9px; border-radius: 7px; color: {nav_item_color};
            }}
            QTreeWidget#hardwareNavigation::item:hover {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 28); color: {nav_item_color};
            }}
            QTreeWidget#hardwareNavigation::item:selected {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 55); color: {nav_selected_color};
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 100); font-weight: 750;
            }}
            QTreeWidget#hardwareNavigation::indicator {{
                width: 30px; height: 16px; border-radius: 8px;
                border: 1px solid rgba(120, 140, 160, 150); background: rgba(70, 82, 94, 190);
            }}
            QTreeWidget#hardwareNavigation::indicator:checked {{
                border-color: {accent.name()}; background: {accent.name()};
            }}
            QPushButton#navigationCustomizeButton, QPushButton#helpNavigationButton {{
                text-align: left; font-weight: 700; color: {nav_item_color};
            }}
            QPushButton#navigationResetButton {{ text-align: left; color: {nav_reset_color}; }}
            QSlider::groove:horizontal {{ height: 6px; border-radius: 3px; background: palette(midlight); }}
            QSlider::sub-page:horizontal {{ background: {accent.name()}; border-radius: 3px; }}
            QSlider::handle:horizontal {{
                width: 17px; margin: -6px 0; border-radius: 8px;
                background: {accent.name()}; border: 2px solid palette(base);
            }}
            {themed_surface_overrides}
            """
