# SPDX-License-Identifier: GPL-3.0-or-later
"""Observe the exposed canvas, including every enclosing scroll viewport."""
from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QTimer
from PySide6.QtWidgets import QApplication


def exposed(widget):
    if not widget.isVisible() or widget.window().isMinimized(): return False
    area = QRect(widget.mapToGlobal(QPoint(0, 0)), widget.size())
    parent = widget.parentWidget()
    while parent is not None:
        area = area.intersected(QRect(parent.mapToGlobal(QPoint(0, 0)), parent.size()))
        if area.isEmpty(): return False
        parent = parent.parentWidget()
    return not area.isEmpty()


class PreviewVisibility(QObject):
    def __init__(self, widget, callback, parent):
        super().__init__(parent)
        self.widget, self.callback = widget, callback
        self.timer = QTimer(self); self.timer.setSingleShot(True)
        self.timer.timeout.connect(callback)
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, watched, event):  # noqa: N802
        if event.type() in {QEvent.Type.Show, QEvent.Type.Hide, QEvent.Type.Move,
                            QEvent.Type.Resize, QEvent.Type.Wheel, QEvent.Type.WindowStateChange}:
            if not self.timer.isActive(): self.timer.start(40)
        return False

    def shutdown(self):
        self.timer.stop()
        QApplication.instance().removeEventFilter(self)
