# SPDX-License-Identifier: GPL-3.0-or-later
"""Matching design gallery composed around the existing apply owners."""
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QToolButton, QVBoxLayout, QWidget,
)
from modules.responsive_gallery.v1_0 import ViewportResizeRelay, reflow_grid, responsive_column_count
from .catalog import PAIRS, pair_poster
from .controller import apply_pair, resolve_pair, preflight_pair, zoom_cache
from .preview import PairPreview
from .preparation import ZoomPreparation
from .size_controls import SizeControls


class DesignHubPage(QScrollArea):
    def __init__(self, host):
        super().__init__()
        self.host = host
        self.pair = PAIRS[0]
        self.message = ""
        self.pending_request = None
        self.pending_lcd_generation = None
        self.preparation = ZoomPreparation(self)
        self.preparation.ready.connect(self.prepared)
        self.preparation.failed.connect(self.preparation_failed)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget(); self.setWidget(body)
        root = QVBoxLayout(body)
        root.setContentsMargins(16, 14, 16, 16)
        root.setSpacing(12)
        root.addWidget(host.make_module_hero("◈", "Abgestimmte Designs",
            "Passende Farben und Animationen für Lüfter und Display gemeinsam entdecken."))
        self.preview = PairPreview()
        root.addWidget(self.preview)
        self.title = QLabel(); self.title.setObjectName("sectionTitle")
        self.description = QLabel(); self.description.setWordWrap(True)
        root.addWidget(self.title); root.addWidget(self.description)
        self.sizes = SizeControls(host)
        self.sizes.changed.connect(self.size_changed)
        root.addWidget(self.sizes)
        self.actions = {}
        actions = QHBoxLayout()
        for target, label in (("both", "Beide anwenden"), ("rgb", "RGB anwenden"), ("lcd", "LCD anwenden")):
            button = QPushButton(host.tr_static(label))
            if target == "both": button.setObjectName("primaryAction")
            button.clicked.connect(lambda _checked=False, value=target: self.apply(value))
            actions.addWidget(button); self.actions[target] = button
        root.addLayout(actions)
        note = QLabel(host.tr_static(
            "LCD für Levita: Die vorhandene Datenebene bleibt erhalten. Die Auswahl allein ändert keine Hardware."))
        note.setObjectName("muted"); note.setWordWrap(True); root.addWidget(note)
        self.status = QLabel(); self.status.setWordWrap(True); root.addWidget(self.status)
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(10)
        self.cards = []
        for pair in PAIRS:
            poster = pair_poster(pair)
            button = QToolButton()
            button.setObjectName("pairedDesignCard")
            button.setStyleSheet(
                "QToolButton#pairedDesignCard { padding: 8px; border-radius: 12px; "
                "border: 1px solid palette(mid); background: palette(base); }"
                "QToolButton#pairedDesignCard:hover { border-color: palette(highlight); }"
                "QToolButton#pairedDesignCard:checked { border: 2px solid palette(highlight); "
                "background: palette(alternate-base); }"
            )
            button.setText(pair.title)
            button.setCheckable(True)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            button.setIcon(QIcon(str(poster)))
            button.setIconSize(QSize(156, 70))
            button.setMinimumSize(174, 112)
            button.clicked.connect(lambda _checked=False, value=pair: self.select(value))
            self.cards.append(button)
        root.addLayout(self.cards_grid)
        root.addStretch()
        self.relay = ViewportResizeRelay(self.reflow, self)
        self.viewport().installEventFilter(self.relay)
        self.reflow(); self.select(self.pair)

    def reflow(self):
        columns = responsive_column_count(self.viewport().width(), card_width=174, gap=10, maximum=5)
        reflow_grid(self.cards_grid, self.cards, columns)

    def select(self, pair):
        self.cancel_preparation()
        self.pair = pair
        for value, card in zip(PAIRS, self.cards):
            card.setChecked(value.ident == pair.ident)
        self.sizes.load(pair)
        self.preview.select(pair, self.sizes.variant_id(), self.sizes.zoom.value())
        self.status.clear()
        self.message = ""
        self.refresh_language()

    def refresh_language(self):
        self.title.setText(self.pair.title)
        self.description.setText(self.host.tr_static(self.pair.description))
        self.status.setText(self.host.tr_static(self.message))
        self.sizes.refresh_language()

    def size_changed(self, reload_media):
        self.cancel_preparation()
        if reload_media:
            self.preview.select(self.pair, self.sizes.variant_id(), self.sizes.zoom.value())
        else:
            self.preview.set_zoom(self.sizes.zoom.value())
        self.message = ''; self.status.clear()

    def apply(self, target):
        self.cancel_preparation()
        try:
            error = preflight_pair(self.host, target)
            if error:
                self.set_message(error); return
            variant, zoom = self.sizes.variant_id(), self.sizes.zoom.value()
            if target in {'both', 'lcd'} and zoom != 100:
                _index, source = resolve_pair(self.pair, variant)
                self.pending_request = (self.pair, variant, zoom, target)
                self.pending_lcd_generation = getattr(
                    getattr(self.host.thermalright_display_studio, 'design_state', None), 'generation', None)
                self.set_message('LCD-Motivgröße wird vorbereitet. Die bisherige Geräteausgabe läuft weiter.')
                self.preparation.start(source, zoom_cache(self.host.thermalright_display_studio), zoom)
                return
            message = apply_pair(self.host, self.pair, target, variant_id=variant, zoom=zoom)
        except (OSError, ValueError, StopIteration):
            message = "Das Design konnte nicht vorbereitet werden. Bitte die Installation prüfen."
        self.set_message(message)

    def set_message(self, message):
        self.message = message
        self.status.setText(self.host.tr_static(message))

    def prepared(self, plan):
        request, self.pending_request = self.pending_request, None
        generation, self.pending_lcd_generation = self.pending_lcd_generation, None
        if request is None: return
        current = getattr(getattr(self.host.thermalright_display_studio, 'design_state', None), 'generation', None)
        if generation is not None and generation != current:
            self.set_message(''); return
        pair, variant, zoom, target = request
        try:
            _index, source = resolve_pair(pair, variant)
            if plan.source != source or plan.zoom != zoom: return
            message = apply_pair(self.host, pair, target, variant_id=variant, zoom=zoom, prepared_media=plan)
        except (OSError, ValueError, StopIteration):
            message = 'Das Design konnte nicht vorbereitet werden. Bitte die Installation prüfen.'
        self.set_message(message)

    def preparation_failed(self):
        if self.pending_request is None: return
        self.pending_request = None
        self.pending_lcd_generation = None
        self.set_message('Die LCD-Größe konnte nicht vorbereitet werden. Bitte ffmpeg und freien Speicher prüfen.')

    def cancel_preparation(self):
        self.pending_request = None
        self.pending_lcd_generation = None
        self.preparation.cancel()

    def hideEvent(self, event):
        pending = self.pending_request is not None
        self.cancel_preparation()
        if pending: self.set_message('')
        super().hideEvent(event)

    def shutdown(self):
        self.cancel_preparation()
        self.preparation.shutdown()
        self.preview.shutdown()
