# SPDX-License-Identifier: GPL-3.0-or-later
"""Content-led GPU composition; existing controls and apply owners are reused."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget
from modules.ui_sections.v1_0.cards import Surface, SectionCard, heading
from .workspace_layout import WorkspacePair, ResizeRelay


def card(title, body):
    frame = Surface(); layout = QVBoxLayout(frame)
    layout.setContentsMargins(18, 16, 18, 18); layout.setSpacing(12)
    heading(title, layout); layout.addWidget(body)
    frame.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
    return frame


def build_workspace(page):
    sections = page.sections; layout = sections.body_layout
    artwork = Surface(); art = QVBoxLayout(artwork)
    art.setContentsMargins(20, 16, 20, 16); art.setSpacing(10)
    art.addWidget(page.tuning_gpu_name)
    art.addWidget(page.tuning_gpu_art)
    art.addWidget(page.tuning_artwork_actions)
    page.tuning_gpu_art.setMinimumHeight(170); page.tuning_gpu_art.setMaximumHeight(180)
    page.tuning_gpu_art.setMinimumWidth(0)
    page.tuning_gpu_art.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    metrics = card(page.tr('Live-Messwerte'), page.gpu_metrics_panel)
    metrics.setMinimumWidth(0)
    page.gpu_summary_panel = WorkspacePair(artwork, metrics, breakpoint=680, weights=(3, 2))
    layout.addWidget(page.gpu_summary_panel)

    tuning = card(page.tr('Übertakten und Leistung'), page.tuning_page)
    fan = card(page.tr('Lüfter und Kurve'), page.fan_page)
    page.gpu_cockpit_columns = [tuning, fan]
    page.gpu_primary_workspace = WorkspacePair(tuning, fan)
    page.gpu_cockpit_layout = page.gpu_primary_workspace.grid
    page.gpu_cockpit_page = sections
    layout.addWidget(page.gpu_primary_workspace)
    sections.route(page.tuning_page, target=page.gpu_summary_panel)
    sections.route(page.fan_page)
    page.tuning_page.show(); page.fan_page.show()

    page.gpu_workspace_sections = {}
    details = ((page.stress_page, 'Lasttest und Darstellung', 'gpu'),
               (sections.widget(3), 'GPU-Unterprofile', 'profiles'),
               (sections.widget(4), 'Messwerte und Beleuchtung', 'gpu'),
               (sections.widget(5), 'Hardwaredetails', 'hardware_checker'),
               (sections.widget(6), 'Diagnose und Protokolle', 'log'))
    for body, title, icon in details:
        section = SectionCard(page.tr(title), '', icon, body)
        page.gpu_workspace_sections[title] = section
        layout.addWidget(section); sections.route(body, section)
        body.show()
    # The main application already identifies this page. Retain the original
    # status controls, but place them alongside device selection instead.
    page.gpu_service_panel = QWidget(page.gpu_toolbar)
    service = QHBoxLayout(page.gpu_service_panel)
    service.setContentsMargins(0, 0, 0, 0); service.setSpacing(8)
    service.addWidget(page.gpu_service_badge); service.addWidget(page.gpu_service_note)
    page.gpu_hero_card.hide()
    page.gpu_geometry_relays = [ResizeRelay(page.tuning_page, page._layout_tuning_actions),
                                ResizeRelay(page.fan_page, page._layout_fan_controls),
                                ResizeRelay(page.tuning_gpu_art, page._update_tuning_artwork)]
    page._update_tuning_artwork()


def reflow_toolbar(page):
    grid = page.gpu_toolbar_layout
    while grid.count(): grid.takeAt(0)
    width = page.viewport().width()
    columns = 4 if width >= 1400 else 2 if width >= 980 else 1
    if columns >= 2:
        grid.addWidget(page.devices, 0, 0, 1, columns - 1)
        grid.addWidget(page.gpu_service_panel, 0, columns - 1)
        action_row = 1
    else:
        grid.addWidget(page.devices, 0, 0)
        grid.addWidget(page.gpu_service_panel, 1, 0)
        action_row = 2
    controls = (page.refresh_button, page.open_lact_button, page.install_button, page.overdrive_button)
    for index, control in enumerate(controls):
        grid.addWidget(control, action_row + index // columns, index % columns)
    for column in range(6): grid.setColumnStretch(column, 1 if column < columns else 0)
