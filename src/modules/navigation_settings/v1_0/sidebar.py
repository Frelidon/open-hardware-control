# SPDX-License-Identifier: GPL-3.0-or-later
"""Complete pointer selection before a page change can reflow sidebar rows."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QAbstractItemView, QTreeWidget


class NavigationTree(QTreeWidget):
    pageRequested = Signal(object, object)

    def __init__(self):
        super().__init__()
        self._pointer_selection = False
        self._pending_selection = None
        self.currentItemChanged.connect(self._request_page)

    def _request_page(self, current, previous):
        if self._pointer_selection:
            self._pending_selection = (current, previous)
        else:
            self.pageRequested.emit(current, previous)

    def mousePressEvent(self, event):
        # Customization keeps Qt's existing drag/drop behavior. Ordinary page
        # selection cannot collapse rows under a still-held pointer.
        self._pointer_selection = self.dragDropMode() == QAbstractItemView.DragDropMode.NoDragDrop
        self._pending_selection = None
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        try:
            super().mouseReleaseEvent(event)
        finally:
            self._pointer_selection = False
            pending, self._pending_selection = self._pending_selection, None
        if pending is not None:
            self.pageRequested.emit(*pending)

    def focusOutEvent(self, event):
        # A cancelled gesture must not defer subsequent keyboard/programmatic
        # requests indefinitely. Do not discard its already selected target.
        pending, self._pending_selection = self._pending_selection, None
        self._pointer_selection = False
        super().focusOutEvent(event)
        if pending is not None:
            self.pageRequested.emit(*pending)
