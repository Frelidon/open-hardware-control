# SPDX-License-Identifier: GPL-3.0-or-later
"""Matching design gallery composed around the existing apply owners."""
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QToolButton, QVBoxLayout, QWidget,
)
from modules.responsive_gallery.v1_0 import ViewportResizeRelay, reflow_grid, responsive_column_count
from .catalog import PAIRS
from .controller import apply_pair, resolve_pair
from .preview import PairPreview


class DesignHubPage(QScrollArea):
    def __init__(self, host):
        super().__init__()
        self.host = host
        self.pair = PAIRS[0]
        self.message = ""
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
            _index, media = resolve_pair(pair)
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
            button.setIcon(QIcon(str(media.with_suffix(".jpg"))))
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
        self.pair = pair
        for value, card in zip(PAIRS, self.cards):
            card.setChecked(value.ident == pair.ident)
        self.preview.select(pair)
        self.status.clear()
        self.message = ""
        self.refresh_language()

    def refresh_language(self):
        self.title.setText(self.pair.title)
        self.description.setText(self.host.tr_static(self.pair.description))
        self.status.setText(self.host.tr_static(self.message))

    def apply(self, target):
        try:
            message = apply_pair(self.host, self.pair, target)
        except (OSError, ValueError, StopIteration):
            message = "Das Design konnte nicht vorbereitet werden. Bitte die Installation prüfen."
        self.message = message
        self.status.setText(self.host.tr_static(message))

    def shutdown(self):
        self.preview.shutdown()
