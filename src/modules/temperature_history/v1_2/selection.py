# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded sensor drag payloads and native Qt selection controls."""
import json
from PySide6.QtCore import QEvent, QMimeData, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPainter, QPalette, QPen, QPixmap
from PySide6.QtWidgets import QAbstractItemView, QTreeWidget
from modules.navigation_settings.v1_0.artwork import category_icon

MIME = "application/x-ohc-temperature-sensors"


def sensor_mime(keys):
    clean = list(dict.fromkeys(key for key in keys if isinstance(key, str) and 0 < len(key) <= 256))[:64]
    mime = QMimeData(); mime.setData(MIME, json.dumps(clean).encode())
    return mime


def sensor_keys(mime, known):
    if not mime.hasFormat(MIME): return []
    raw = bytes(mime.data(MIME))
    if len(raw) > 20_000: return []
    try: values = json.loads(raw)
    except (ValueError, UnicodeDecodeError): return []
    if not isinstance(values, list) or len(values) > 64: return []
    return list(dict.fromkeys(key for key in values if isinstance(key, str) and key in known))


def sensor_icon(group, palette):
    if group in {"gpu", "cooling"}:
        return category_icon("gpu" if group == "gpu" else "cooling", palette, 32)
    pix = QPixmap(32, 32); pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(palette.color(QPalette.ColorRole.Text), 1.6))
    if group == "memory":
        p.drawRoundedRect(3, 9, 26, 14, 2, 2)
        for x in (7, 13, 19): p.drawRect(x, 12, 4, 7)
        for x in range(6, 27, 4): p.drawLine(x, 24, x, 27)
    elif group == "storage":
        p.drawRoundedRect(5, 4, 22, 24, 3, 3); p.drawEllipse(9, 8, 14, 14)
        p.drawEllipse(14, 13, 4, 4); p.drawLine(10, 25, 16, 25)
    elif group in {"cpu", "mainboard"}:
        p.drawRoundedRect(8, 8, 16, 16, 2, 2); p.drawRect(12, 12, 8, 8)
        for x in (10, 16, 22):
            p.drawLine(x, 3, x, 7); p.drawLine(x, 25, x, 29)
            p.drawLine(3, x, 7, x); p.drawLine(25, x, 29, x)
    else:
        p.drawRoundedRect(12, 3, 8, 19, 4, 4); p.drawEllipse(9, 17, 14, 12)
    p.end(); return QIcon(pix)


class SensorTree(QTreeWidget):
    keysDropped = Signal(object)

    def __init__(self):
        super().__init__()
        self.known_keys = set()
        self.setProperty("keepViewportHeight", True)
        self.setMinimumHeight(90)
        self.setDragEnabled(True); self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.setIconSize(QSize(28, 28))

    def mimeData(self, items):
        return sensor_mime([item.data(0, Qt.ItemDataRole.UserRole) for item in items])

    def dragEnterEvent(self, event):
        if sensor_keys(event.mimeData(), self.known_keys): event.acceptProposedAction()
        else: event.ignore()

    def dragMoveEvent(self, event): self.dragEnterEvent(event)

    def dropEvent(self, event):
        keys = sensor_keys(event.mimeData(), self.known_keys)
        if keys and event.source() is not self:
            self.keysDropped.emit(keys); event.acceptProposedAction()
        else: event.ignore()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.PaletteChange:
            pending = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]
            while pending:
                item = pending.pop()
                group = item.data(0, Qt.ItemDataRole.UserRole.value + 1)
                if group: item.setIcon(0, sensor_icon(group, self.palette()))
                pending.extend(item.child(i) for i in range(item.childCount()))
