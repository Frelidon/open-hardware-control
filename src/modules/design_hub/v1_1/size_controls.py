# SPDX-License-Identifier: GPL-3.0-or-later
"""Per-design LCD zoom and real Matrix glyph variants; no apply side effects."""
from PySide6.QtCore import Qt, QSignalBlocker, Signal
from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget
from .catalog import MATRIX_SIZES


class SizeControls(QWidget):
    changed = Signal(bool)

    def __init__(self, host):
        super().__init__()
        self.host, self.pair = host, None
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0)
        form = QFormLayout(); form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.zoom_caption = QLabel(); self.zoom_value = QLabel()
        self.zoom = QSlider(Qt.Orientation.Horizontal)
        self.zoom.setRange(50, 200); self.zoom.setSingleStep(5); self.zoom.setPageStep(10)
        self.zoom.setTickInterval(25); self.zoom.setMinimumWidth(180)
        zoom_row = QWidget(); row = QHBoxLayout(zoom_row); row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self.zoom, 1); row.addWidget(self.zoom_value)
        form.addRow(self.zoom_caption, zoom_row)
        self.glyph_caption = QLabel(); self.glyph_value = QLabel()
        self.glyph = QSlider(Qt.Orientation.Horizontal)
        self.glyph.setRange(0, len(MATRIX_SIZES) - 1); self.glyph.setSingleStep(1); self.glyph.setPageStep(1)
        self.glyph.setTickInterval(1); self.glyph.setMinimumWidth(180)
        self.glyph_row = QWidget(); row = QHBoxLayout(self.glyph_row); row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self.glyph, 1); row.addWidget(self.glyph_value)
        form.addRow(self.glyph_caption, self.glyph_row); root.addLayout(form)
        self.note = QLabel(); self.note.setObjectName('muted'); self.note.setWordWrap(True); root.addWidget(self.note)
        self.zoom.valueChanged.connect(self._zoom_changed)
        self.glyph.valueChanged.connect(self._glyph_changed)
        self.refresh_language()

    def _setting(self, key, fallback):
        settings = getattr(self.host, 'settings', None)
        return settings.value(key, fallback) if settings is not None else fallback

    def _save(self, key, value):
        settings = getattr(self.host, 'settings', None)
        if settings is not None: settings.setValue(key, value)

    def load(self, pair):
        self.pair = pair
        try: zoom = int(self._setting(f'design_hub/zoom/{pair.ident}', 100))
        except (TypeError, ValueError, OverflowError): zoom = 100
        zoom = min(200, max(50, round(zoom / 5) * 5))
        variant = str(self._setting(f'design_hub/variant/{pair.ident}', 'large-30'))
        index = next((index for index, (_size, ident) in enumerate(MATRIX_SIZES) if ident == variant), 1)
        with QSignalBlocker(self.zoom): self.zoom.setValue(zoom)
        with QSignalBlocker(self.glyph): self.glyph.setValue(index)
        matrix = pair.ident == 'matrix'
        self.glyph_caption.setVisible(matrix); self.glyph_row.setVisible(matrix)
        self.refresh_language()

    def variant_id(self):
        return MATRIX_SIZES[self.glyph.value()][1] if self.pair and self.pair.ident == 'matrix' else None

    def _zoom_changed(self, value):
        snapped = min(200, max(50, round(value / 5) * 5))
        if snapped != value:
            with QSignalBlocker(self.zoom): self.zoom.setValue(snapped)
        if self.pair: self._save(f'design_hub/zoom/{self.pair.ident}', snapped)
        self.refresh_language(); self.changed.emit(False)

    def _glyph_changed(self, _value):
        if self.pair: self._save(f'design_hub/variant/{self.pair.ident}', self.variant_id())
        self.refresh_language(); self.changed.emit(True)

    def refresh_language(self):
        tr = self.host.tr_static
        self.zoom_caption.setText(tr('LCD-Motivgröße'))
        self.glyph_caption.setText(tr('Matrix-Zeichengröße'))
        self.zoom.setAccessibleName(tr('LCD-Motivgröße'))
        self.glyph.setAccessibleName(tr('Matrix-Zeichengröße'))
        self.zoom_value.setText(f'{self.zoom.value()} %')
        self.glyph_value.setText(f'{MATRIX_SIZES[self.glyph.value()][0]} %')
        self.note.setText(tr('Die Motivgröße skaliert nur den LCD-Hintergrund. Die Datenebene bleibt unverändert. Erst Anwenden überträgt die Auswahl.'))
