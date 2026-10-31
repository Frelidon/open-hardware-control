# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure shared Qt widget stylesheet fragments."""
from __future__ import annotations

def base_widget_stylesheet(*, accent, base_px, brand_color, brand_logo_bg, brand_logo_border, card_px, content_rgba, cooling_metrics, curve_overlay_bg, dashboard_meta, dashboard_neutral_bg, dashboard_neutral_fg, design_active, design_status_bg, design_status_border, design_title, fan_detail_bg, fan_icon_bg, fan_icon_border, fan_icon_color, hardware_row_bg, hardware_row_border, highlighted_text, hover, input_rgba, module_hero_bg, nav_item_color, nav_reset_color, nav_selected_color, neutral_button_rgba, neutral_status_title, ownership_bg, ownership_border, panel_border_rgba, panel_rgba, pressed, rail_bg, rail_border, sidebar_status_bg, sidebar_status_border, sidebar_status_color, table_header_rgba, themed_surface_overrides, title_px, **_unused) -> str:
    return f"""
            QWidget {{ font-size: {base_px}px; color: palette(window-text); }}
            QMainWindow {{ background: palette(window); }}
            QWidget#backgroundRoot {{ background: transparent; }}
            QWidget#contentRoot {{ background: {content_rgba}; }}
            QWidget#windowBody {{ background: transparent; }}
            QWidget#windowChrome {{
                background: {rail_bg};
                border-bottom: 1px solid {rail_border};
            }}
            QLabel#windowChromeTitle {{ color: {brand_color}; font-weight: 700; }}
            QPushButton#windowChromeButton, QPushButton#windowCloseButton {{
                padding: 0;
                border: 1px solid transparent;
                border-radius: 7px;
                background: transparent;
                color: {brand_color};
                font-size: 16px;
                font-weight: 700;
            }}
            QPushButton#windowChromeButton:hover {{
                border-color: {panel_border_rgba}; background: {neutral_button_rgba};
            }}
            QPushButton#windowCloseButton:hover {{
                border-color: #e05a5a; background: #b52d40; color: #ffffff;
            }}
            QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                width: 8px; margin: 2px 1px; border: none; background: transparent;
            }}
            QScrollBar::handle:vertical {{
                min-height: 28px; border-radius: 3px;
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 145);
            }}
            QScrollBar::handle:vertical:hover {{ background: {accent.name()}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; border: none; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
            QScrollBar:horizontal {{
                height: 8px; margin: 1px 2px; border: none; background: transparent;
            }}
            QScrollBar::handle:horizontal {{
                min-width: 28px; border-radius: 3px;
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 145);
            }}
            QScrollBar::handle:horizontal:hover {{ background: {accent.name()}; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; border: none; }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}
            QLabel#mainTitle {{ font-size: {title_px}px; font-weight: 750; }}
            QLabel#subtitle, QLabel#muted, QLabel#cardHint {{ color: palette(mid); }}
            QLabel#connectionPending {{ color: #d49b21; font-weight: 700; }}
            QLabel#connectionOk {{ color: #2fbf71; font-weight: 700; }}
            QLabel#connectionBad {{ color: #e05a5a; font-weight: 700; }}
            QLabel#cardTitle {{ color: palette(mid); font-size: 13px; }}
            QLabel#cardValue {{ font-size: {card_px}px; font-weight: 750; }}
            QLabel#healthGood {{ color: #2fbf71; font-weight: 700; }}
            QLabel#healthWarn {{ color: #d49b21; font-weight: 700; }}
            QLabel#healthCritical {{ color: #e05a5a; font-weight: 800; }}
            QLabel#healthNeutral {{ color: palette(mid); }}
            QLabel#warningText {{ color: #d49b21; }}
            QLabel#successText {{ color: #2fbf71; font-weight: 700; }}
            QFrame#coolingSafetyNote {{
                background: rgba(212, 155, 33, 24);
                border: 1px solid rgba(212, 155, 33, 105);
                border-radius: 8px;
            }}
            QLabel#coolingSafetyTitle {{ color: #d49b21; font-weight: 800; }}
            QLabel#coolingSafetyText {{ color: palette(window-text); }}
            QFrame#rgbDesignStatusPanel {{
                background: {design_status_bg};
                border: 2px solid {design_status_border};
                border-radius: 12px;
            }}
            QLabel#rgbDesignSelection {{ color: {design_title}; font-weight: 700; font-size: 14px; }}
            QLabel#rgbDesignActive {{ color: {design_active}; font-weight: 600; }}
            QFrame#rgbStartupAutomationPanel {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 28);
                border: 2px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 175);
                border-radius: 12px;
            }}
            QLabel#rgbStartupAutomationTitle {{
                color: {accent.lighter(125).name()}; font-size: 18px; font-weight: 850;
            }}
            QLabel#rgbStartupAutomationSummary {{
                color: palette(window-text); font-size: 14px; font-weight: 650;
            }}
            QLabel#infoText {{ color: palette(mid); }}
            QLabel#designPreview {{
                border: 2px solid {accent.name()};
                border-radius: 8px;
                background: palette(base);
                color: {accent.name()};
                font-weight: 700;
                padding: 8px;
            }}
            QFrame#valueCard, QFrame#profileCard {{
                border: 1px solid {panel_border_rgba};
                border-radius: 10px;
                background: {panel_rgba};
            }}
            QFrame#gpuHeroCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(8, 24, 43, 245), stop:0.72 rgba(11, 36, 61, 236),
                    stop:1 rgba({accent.red()}, {accent.green()}, {accent.blue()}, 46));
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 145);
                border-radius: 14px;
            }}
            QLabel#gpuEyebrow {{ color: {accent.lighter(125).name()}; font-size: 11px; font-weight: 800; letter-spacing: 2px; }}
            QLabel#gpuHeroTitle {{ color: #f5f8ff; font-size: {title_px}px; font-weight: 850; }}
            QLabel#gpuServiceBadge {{
                color: #6ee7b7; background: rgba(16, 185, 129, 30);
                border: 1px solid rgba(52, 211, 153, 115); border-radius: 10px;
                padding: 7px 13px; font-weight: 800;
            }}
            QFrame#gpuMetricCard {{
                background: rgba(8, 26, 46, 235);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 90);
                border-radius: 12px;
            }}
            QFrame#gpuMetricCard:hover {{ border-color: {accent.lighter(118).name()}; }}
            QLabel#gpuMetricIcon {{
                color: {accent.lighter(132).name()}; background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 35);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 95); border-radius: 9px;
                font-size: 18px; font-weight: 800;
            }}
            QLabel#gpuMetricTitle {{ color: #a9b9cb; font-size: 11px; }}
            QLabel#gpuMetricValue {{ color: #f4f7ff; font-size: 16px; font-weight: 850; }}
            QWidget#gpuToolbar {{
                background: rgba(9, 26, 44, 205); border: 1px solid {panel_border_rgba}; border-radius: 11px;
            }}
            QTabWidget#gpuSections::pane {{ border: none; background: transparent; top: -1px; }}
            QTabWidget#gpuSections QTabBar::tab {{
                min-width: 88px; padding: 10px 16px; margin-right: 3px;
                background: rgba(9, 28, 47, 190); border: 1px solid {panel_border_rgba};
                border-radius: 9px; color: #aab8c8;
            }}
            QTabWidget#gpuSections QTabBar::tab:selected {{
                color: white; background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 70);
                border: 1px solid {accent.name()}; font-weight: 800;
            }}
            QWidget#gpuCockpit {{ background: transparent; }}
            QGroupBox#gpuWorkspaceColumn {{
                color: #eef4ff; font-size: 18px; font-weight: 850;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(8, 27, 49, 242), stop:1 rgba(5, 18, 34, 238));
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 150);
                border-radius: 14px; margin-top: 18px; padding: 10px;
            }}
            QGroupBox#gpuWorkspaceColumn::title {{
                subcontrol-origin: margin; left: 14px; padding: 0 8px;
            }}
            QLabel#gpuDeviceHeading {{
                color: #dce9ff; font-size: 15px; font-weight: 820;
                padding: 3px 2px 7px 2px;
            }}
            QLabel#gpuCockpitArtwork {{
                background: rgba(3, 13, 27, 130);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 70);
                border-radius: 11px; padding: 8px;
            }}
            QFrame#gpuTuningRow {{
                background: rgba(7, 24, 43, 205);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 72);
                border-radius: 10px;
            }}
            QFrame#gpuTuningRow:hover {{
                border-color: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 145);
            }}
            QLabel#gpuTuningLabel {{ color: #d7e4f5; font-weight: 700; }}
            QSpinBox#gpuTuningSpin, QDoubleSpinBox#gpuTuningSpin {{
                min-height: 27px; padding: 4px 8px; color: #e8f2ff;
                background: rgba(4, 17, 33, 225);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 115);
                border-radius: 8px; font-weight: 800;
            }}
            QSpinBox#gpuFanSpin, QSpinBox#gpu_fan_static_speed, QDoubleSpinBox#caseDistanceSpin {{
                min-height: 30px; padding: 5px 9px; color: #eef6ff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(3, 17, 34, 238), stop:1 rgba({accent.red()}, {accent.green()}, {accent.blue()}, 28));
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 145);
                border-radius: 9px; font-size: 14px; font-weight: 850;
            }}
            QSlider#gpuTuningSlider::groove:horizontal {{
                height: 7px; border-radius: 3px; background: rgba(60, 91, 127, 125);
            }}
            QSlider#gpuTuningSlider::sub-page:horizontal {{
                border-radius: 3px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2686ff, stop:1 {accent.lighter(125).name()});
            }}
            QSlider#gpuTuningSlider::handle:horizontal {{
                width: 16px; margin: -6px 0; border-radius: 8px;
                background: #f7fbff; border: 3px solid #277dff;
            }}
            QGroupBox#gpuWorkspaceColumn QComboBox,
            QGroupBox#gpuWorkspaceColumn QSpinBox,
            QGroupBox#gpuWorkspaceColumn QDoubleSpinBox {{
                min-height: 28px; border-radius: 8px;
                background: rgba(6, 23, 42, 225);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 88);
            }}
            QGroupBox#gpuWorkflowCard, QGroupBox#gpuActionCard {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 18);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 105);
                border-radius: 11px; margin-top: 12px; padding: 9px;
            }}
            QLabel#gpuWorkflowStatus {{
                color: #cbe9ff; font-weight: 750; padding: 4px;
            }}
            QLabel#gpuStressMetric {{
                color: #dcecff; font-weight: 750; padding: 10px 5px;
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 20);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 70);
                border-radius: 8px;
            }}
            QGroupBox#gpuProfileCard, QGroupBox#gpuArtworkCard, QGroupBox#gpuOwnershipCard,
            QGroupBox#gpuControlCard, QGroupBox#gpuPreviewCard {{
                background: rgba(7, 24, 42, 235);
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 105);
                border-radius: 13px; margin-top: 16px; padding: 12px;
            }}
            QLabel#gpuProfileArtwork {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(5, 18, 32, 245), stop:1 rgba({accent.red()}, {accent.green()}, {accent.blue()}, 36));
                border: 1px solid rgba({accent.red()}, {accent.green()}, {accent.blue()}, 80);
                border-radius: 12px; padding: 10px;
            }}
            QPushButton#gpuPrimaryAction {{
                min-height: 34px; padding: 8px 16px; color: white; font-weight: 800;
                background: {accent.name()}; border: 1px solid {accent.lighter(125).name()}; border-radius: 9px;
            }}
            QPushButton#gpuPrimaryAction:hover {{ background: {hover.name()}; color: white; }}
            QPushButton#gpuPrimaryAction:disabled {{
                color: #718091; background: rgba(70, 84, 99, 70);
                border-color: rgba(103, 117, 131, 90);
            }}
            QPushButton#gpuCommitAction {{
                min-height: 34px; padding: 8px 16px; color: {accent.name()}; font-weight: 800;
                background: transparent; border: 1px solid {accent.name()}; border-radius: 9px;
            }}
            QPushButton#gpuCommitAction:hover {{ background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 36); }}
            QPushButton#gpuCommitAction:disabled {{ color: #677583; border-color: rgba(103, 117, 131, 110); }}
            QPushButton#gpuDangerAction {{ color: #ff98a6; border-color: rgba(224, 90, 90, 150); }}
            QFrame#rgbDeviceTile {{
                border: 2px solid {panel_border_rgba};
                border-radius: 12px;
                background: {panel_rgba};
            }}
            QFrame#rgbDeviceTile:hover {{ border-color: {accent.name()}; }}
            QLabel#profileTitle {{ font-size: 17px; font-weight: 700; }}
            QLabel#lcdPreview {{
                background: #101010;
                border: 3px solid {accent.name()};
                border-radius: 150px;
                color: #aaaaaa;
            }}
            CurveEditor#curveEditor {{
                border: 1px solid {panel_border_rgba};
                border-radius: 10px;
                background: {input_rgba};
            }}
            QGroupBox {{
                border: 1px solid {panel_border_rgba};
                border-radius: 10px;
                margin-top: 14px;
                padding: 9px;
                font-weight: 700;
                background: {panel_rgba};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}
            QPushButton {{
                padding: 6px 10px;
                border: 1px solid {panel_border_rgba};
                border-radius: 7px;
                background: {neutral_button_rgba};
            }}
            QPushButton:hover {{ border-color: {hover.name()}; color: {accent.name()}; }}
            QPushButton:pressed {{ border-color: {pressed.name()}; background: palette(midlight); }}
            QToolButton#layer2PreviewCard {{
                padding: 5px; border: 1px solid {panel_border_rgba}; border-radius: 10px;
                background: {neutral_button_rgba}; color: palette(window-text);
            }}
            QToolButton#layer2PreviewCard:hover {{
                border-color: {accent.name()}; background: {table_header_rgba}; color: palette(window-text);
            }}
            QToolButton#layer2PreviewCard:checked {{
                border: 2px solid {accent.name()}; background: {panel_rgba}; color: palette(window-text);
            }}
            QPushButton:checked {{
                border: 2px solid #2fbf71;
                background: rgba(47, 191, 113, 52);
                color: #54dda1;
                font-weight: 750;
            }}
            QPushButton#dangerButton {{
                border: 2px solid #e05a5a;
                background: #9f2636;
                color: #ffffff;
                font-weight: 850;
            }}
            QPushButton#dangerButton:hover {{ border-color: #ff9aa8; background: #b52d40; color: #ffffff; }}
            QPushButton#coolingModeButton[coolingState="active"] {{
"""
