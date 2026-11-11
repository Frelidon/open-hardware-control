# SPDX-License-Identifier: GPL-3.0-or-later
"""Reusable sensor reading cards, sharing the recorder's sampled values."""
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPainter, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QVBoxLayout,
)
from .selection import sensor_icon, sensor_keys, sensor_mime


class ReadingList(QListWidget):
    keysDropped = Signal(object)
    removeRequested = Signal(object)

    def __init__(self, translate):
        super().__init__()
        self.translate = translate; self.known_keys = set(); self.rows = {}
        self.setProperty("keepViewportHeight", True)
        self.setDragEnabled(True); self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSpacing(5); self.setMinimumHeight(130)

    def mimeData(self, items):
        return sensor_mime([item.data(Qt.ItemDataRole.UserRole) for item in items])

    def dragEnterEvent(self, event):
        if sensor_keys(event.mimeData(), self.known_keys): event.acceptProposedAction()
        else: event.ignore()

    def dragMoveEvent(self, event): self.dragEnterEvent(event)

    def dropEvent(self, event):
        keys = sensor_keys(event.mimeData(), self.known_keys)
        if keys and event.source() is not self:
            self.keysDropped.emit(keys); event.acceptProposedAction()
        else: event.ignore()

    def keyPressEvent(self, event):
        if event.key() in {Qt.Key.Key_Delete, Qt.Key.Key_Backspace}:
            self.removeRequested.emit([item.data(Qt.ItemDataRole.UserRole) for item in self.selectedItems()])
        else: super().keyPressEvent(event)

    def update_readings(self, data):
        if tuple(self.rows) != tuple(data):
            self.clear(); self.rows = {}
            for key in data:
                item = QListWidgetItem(); item.setData(Qt.ItemDataRole.UserRole, key)
                item.setSizeHint(QSize(260, 154)); self.addItem(item)
                card = QFrame(objectName="coolingSummaryCard"); layout = QVBoxLayout(card)
                top = QHBoxLayout(); icon = QLabel(); icon.setFixedSize(30, 30)
                title = QLabel(); title.setWordWrap(True); title.setObjectName("coolingCardTitle")
                remove = QPushButton("×"); remove.setFixedWidth(32)
                remove.clicked.connect(lambda _checked=False, k=key: self.removeRequested.emit([k]))
                top.addWidget(icon); top.addWidget(title, 1); top.addWidget(remove); layout.addLayout(top)
                metrics = QGridLayout(); captions = []; values = []
                for column in range(3):
                    caption = QLabel(); value = QLabel(); value.setObjectName("cardValue" if column == 0 else "coolingMetrics")
                    metrics.addWidget(caption, 0, column); metrics.addWidget(value, 1, column)
                    captions.append(caption); values.append(value)
                layout.addLayout(metrics); measured = QLabel(objectName="muted"); layout.addWidget(measured)
                self.setItemWidget(item, card)
                self.rows[key] = (item, card, icon, title, remove, captions, values, measured)
        tr = self.translate
        for key, (name, group, source, current, minimum, maximum, timestamp) in data.items():
            item, card, icon, title, remove, captions, values, measured = self.rows[key]
            title.setText(name); card.setToolTip(source)
            icon.setPixmap(sensor_icon(group, self.palette()).pixmap(30, 30))
            remove.setToolTip(tr("Messwert entfernen")); remove.setAccessibleName(tr("Messwert entfernen") + ": " + name)
            for label, caption in zip(captions, ("Aktuell", "Minimum", "Maximum")): label.setText(tr(caption))
            for label, value in zip(values, (current, minimum, maximum)): label.setText(value)
            measured.setText(tr("Zeitpunkt") + ": " + timestamp)
        self.fit_rows()
        self.viewport().update()

    def fit_rows(self):
        width = max(220, self.viewport().width() - 2 * self.spacing())
        for item, card, *_rest in self.rows.values():
            card.ensurePolished()
            height = max(154, card.layout().heightForWidth(width))
            item.setSizeHint(QSize(width, height))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "rows"): self.fit_rows()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.count():
            painter = QPainter(self.viewport()); painter.setPen(self.palette().color(QPalette.ColorRole.Text))
            painter.drawText(self.viewport().rect().adjusted(12, 12, -12, -12), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                             self.translate("Sensoren hierher ziehen oder links auswählen."))
