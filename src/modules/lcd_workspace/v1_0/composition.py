# SPDX-License-Identifier: GPL-3.0-or-later
"""Arrange existing Levita controls once; no copied controls or apply paths."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
                              QScrollArea, QSizePolicy, QVBoxLayout, QWidget)
from modules.ui_sections.v1_0.cards import Surface, SectionCard
from modules.ui_performance.v1_1.compact_panels import ResponsiveColumns
from .navigation import WorkspaceTabs


class CollectedUi:
    """Give legacy rows an owning widget before moving them into workspaces."""
    def __init__(self, owner):
        self.layout = QVBoxLayout(owner); self.rows = {}; self.widgets = []
        self.layout.setContentsMargins(0, 0, 0, 0)

    def setSpacing(self, value): self.layout.setSpacing(value)

    def addWidget(self, widget):
        self.widgets.append(widget); self.layout.addWidget(widget)

    def addLayout(self, layout):
        wrapper = QWidget(); outer = QVBoxLayout(wrapper); outer.setContentsMargins(0, 0, 0, 0)
        outer.addLayout(layout); self.rows[id(layout)] = wrapper; self.addWidget(wrapper)

    def row(self, layout): return self.rows[id(layout)]

    def detach(self):
        for widget in self.widgets: self.layout.removeWidget(widget)


def _surface(widgets):
    panel = Surface(); layout = QVBoxLayout(panel)
    layout.setContentsMargins(16, 14, 16, 14); layout.setSpacing(12)
    for widget in widgets: layout.addWidget(widget)
    return panel


def _section(title, widget, *, icon='settings'):
    return SectionCard(title, '', icon, widget)


def _row_widgets(row):
    result = []
    while row.count():
        item = row.takeAt(0)
        if item.widget() is not None: result.append(item.widget())
    return result


def _form_viewport(widget, height):
    """Keep large compatibility editors inside their own bounded viewport."""
    viewport = QScrollArea(); viewport.setFrameShape(QFrame.Shape.NoFrame)
    viewport.setWidgetResizable(True); viewport.setWidget(widget)
    viewport.setMinimumWidth(0); viewport.setMinimumHeight(height)
    viewport.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
    return viewport


def _safe_preview(studio):
    # Preserve the canvas' fixed logical editor size and move only its viewport.
    studio.preview_canvas_row.removeWidget(studio.canvas)
    viewport = QScrollArea(); viewport.setFrameShape(QFrame.Shape.NoFrame)
    viewport.setWidget(studio.canvas); viewport.setWidgetResizable(False)
    viewport.setMinimumWidth(0); viewport.setMinimumHeight(420)
    viewport.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
    studio.preview_canvas_scroll = viewport
    studio.preview_canvas_row.insertWidget(0, viewport, 1)


def organize_studio(studio, builder, p):
    builder.detach(); root = builder.layout
    studio.setTitle(''); studio.setObjectName('lcdLevitaWorkspace'); studio.setFlat(True)
    studio.setStyleSheet('QGroupBox#lcdLevitaWorkspace {border: none; margin: 0; padding: 0;}')
    tabs = studio.workspace_tabs = WorkspaceTabs()
    library, composition, operation = (tabs.widget(index).layout() for index in range(3))

    toolbar = Surface(); top = QVBoxLayout(toolbar); top.setContentsMargins(16, 14, 16, 14)
    row = QHBoxLayout(); summary = QVBoxLayout()
    title = QLabel('Designauswahl'); title.setStyleSheet('font-size: 17px; font-weight: 650;')
    summary.addWidget(title)
    studio.selection_summary = QLabel(); studio.selection_summary.setWordWrap(True)
    studio.selection_summary.setObjectName('muted'); summary.addWidget(studio.selection_summary)
    studio.workspace_output_status = QLabel(); studio.workspace_output_status.setWordWrap(True)
    studio.workspace_output_status.setObjectName('muted'); summary.addWidget(studio.workspace_output_status)
    row.addLayout(summary, 1)
    p['library_toolbar'].removeWidget(studio.top_apply_button)
    studio.top_apply_button.setMinimumHeight(44); row.addWidget(studio.top_apply_button)
    effect_button = QPushButton('Display-Effekte öffnen'); effect_button.setMinimumHeight(40)
    effect_button.clicked.connect(lambda: getattr(studio.window(), 'tabs').setCurrentIndex(
        getattr(studio.window(), 'display_effects_page_index', 11)))
    row.addWidget(effect_button); top.addLayout(row)
    p['options_row'].removeWidget(studio.preview_status)
    studio.preview_status.setWordWrap(True); top.addWidget(studio.preview_status)
    root.addWidget(toolbar); root.addWidget(tabs)

    source_panel = QWidget(); source = QVBoxLayout(source_panel); source.setContentsMargins(0, 0, 0, 0)
    source_grid = QGridLayout(); source_grid.setSpacing(10)
    for index, widget in enumerate((p['standard_button'], studio.library_manager_button,
                                   studio.remembered_media_button, studio.custom_media_enabled)):
        p['library_toolbar'].removeWidget(widget); source_grid.addWidget(widget, index // 2, index % 2)
    source.addLayout(source_grid); source.addWidget(studio.library_manager_panel)
    studio.source_section = _section('Quellen & Kataloge', source_panel, icon='lcd')
    library.addWidget(builder.row(p['library_toolbar']))
    library.addWidget(studio.source_section)
    library.addWidget(studio.thumbnail_progress_panel)
    categories = QScrollArea(); categories.setFrameShape(QFrame.Shape.NoFrame)
    categories.setWidgetResizable(True); categories.setWidget(p['category_frame']); categories.setFixedHeight(65)
    categories.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    library.addWidget(categories)
    galleries = ResponsiveColumns(1100)
    for box in (studio.layer1_library_box, studio.layer2_library_box):
        p['galleries'].removeWidget(box); box.setMinimumWidth(0)
        for label in box.findChildren(QLabel): label.setWordWrap(True)
        galleries.addWidget(box)
    library.addWidget(galleries); library.addWidget(studio.media_directory_label)

    p['library_toolbar'].removeWidget(studio.geometry_toggle)
    p['preview_stage_layout'].removeWidget(p['performance_box'])
    p['preview_title'].setWordWrap(True)
    p['preview_stage'].setStyleSheet(
        'QFrame#levitaPreviewStage {background: palette(base); border: 1px solid palette(mid); border-radius: 12px;}'
        'QFrame#layer2InlineEditor {background: palette(base); border: 1px solid palette(mid); border-radius: 10px;}')
    studio.preview_canvas_row.removeWidget(studio.geometry_scroll)
    studio.geometry_scroll.setMinimumWidth(0); studio.geometry_scroll.setMaximumHeight(620)
    _safe_preview(studio)
    composition.addWidget(p['preview_stage'])
    editor_widgets = _row_widgets(studio.layer2_editor_bar.layout())
    editor_layout = studio.layer2_editor_bar.layout()
    editor_widgets[0].setWordWrap(True); editor_layout.addWidget(editor_widgets[0])
    studio.layer2_editor_bar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
    editor_controls = QWidget(); controls = QHBoxLayout(editor_controls)
    controls.setContentsMargins(0, 0, 0, 0)
    for widget in editor_widgets[1:]: controls.addWidget(widget)
    editor_layout.setDirection(QHBoxLayout.Direction.TopToBottom); editor_layout.addWidget(editor_controls)
    composition.addWidget(studio.layer2_editor_bar)
    studio.geometry_section = _section('Geometrie & Aussparung', studio.geometry_scroll)
    studio.geometry_toggle.toggled.disconnect(studio.geometry_scroll.setVisible)
    studio.geometry_scroll.show()
    studio.geometry_section.button.toggled.connect(studio.geometry_toggle.setChecked)
    studio.geometry_toggle.toggled.connect(studio.geometry_section.button.setChecked)
    composition.addWidget(studio.geometry_section)
    studio.overlays_section = _section('Eigene Einblendungen', _form_viewport(studio.custom_overlays_box, 400), icon='lcd')
    studio.overlays_toggle.toggled.disconnect(studio.custom_overlays_box.setVisible)
    studio.custom_overlays_box.show()
    studio.overlays_section.button.toggled.connect(studio.overlays_toggle.setChecked)
    studio.overlays_toggle.toggled.connect(studio.overlays_section.button.setChecked)
    composition.addWidget(studio.overlays_section)
    notes = _surface([p['intro'], p['layer_note'], builder.row(p['options_row']), p['split_notice']])
    composition.addWidget(_section('Ebenen & Vorschauhinweise', notes, icon='help'))
    studio.geometry_toggle.hide(); studio.overlays_toggle.hide()

    status_widgets = _row_widgets(p['status_row'])
    operation.addWidget(_surface([studio.playback_health_status, *status_widgets]))
    studio.startup_status.setWordWrap(True)
    operation.addWidget(_surface(_row_widgets(p['startup_row'])))
    performance = _form_viewport(p['performance_box'], 330)
    studio.performance_section = _section('Leistung & Spiele', performance, icon='games')
    operation.addWidget(studio.performance_section)
    maintenance = _surface([*_row_widgets(p['action_row']), *_row_widgets(p['display_recovery_row']), p['safety']])
    studio.restore_firmware_button.setObjectName('lcdFirmwareReturn')
    studio.maintenance_section = _section('Wartung & Rückgabe', maintenance, icon='hardware_fix')
    operation.addWidget(studio.maintenance_section)

    def selection_summary(*_args):
        translate = getattr(studio.window(), 'tr_static', lambda value: value)
        first = studio.media_combo.currentText() or '—'
        second = studio.hardware_design_combo.currentText() or translate('Eigene OHC-Werte · frei verschiebbar')
        studio.selection_summary.setText(translate('Ebene 1 · Hintergrund') + ': ' + first + '\n'
                                         + translate('Ebene 2 · Datenoberfläche') + ': ' + second)
        mode = studio.test_mode.text() if studio.test_mode.isChecked() else translate('USB-Ausgabe aktiviert')
        studio.workspace_output_status.setText(mode)
        studio.top_apply_button.setToolTip(mode)
    studio.refresh_workspace_summary = selection_summary
    studio.media_combo.currentIndexChanged.connect(selection_summary)
    studio.hardware_design_combo.currentIndexChanged.connect(selection_summary)
    studio.test_mode.toggled.connect(selection_summary)
    selection_summary()
    def workspace_changed(index):
        if index != 0:
            studio._pause_thumbnail_workers()
            studio.gallery_preparation.timer.stop()
            studio.hover_preview_timer.stop(); studio.hover_preview_debounce.stop()
            studio._cancel_hover_extract()
        else:
            studio._materialize_visible_galleries()
        studio.media_preview.refresh()
    tabs.currentChanged.connect(workspace_changed)
    # Old row wrappers are retained but hidden; none contains unique visible content.
    for widget in builder.widgets:
        if widget.parentWidget() is studio and widget not in (toolbar, tabs): widget.hide()
