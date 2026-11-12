# SPDX-License-Identifier: GPL-3.0-or-later
"""One GPU workspace, with legacy section routing and width-aware groups."""
from PySide6.QtCore import QEvent, QObject, QTimer, Qt, Signal
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QVBoxLayout, QWidget
from shiboken6 import isValid


class WorkspaceSections(QWidget):
    """Keep builder/section IDs while every section lives on one real page.

    This is a scroll-navigation adapter, not a hidden tab stack. The historical
    setCurrentIndex API opens the corresponding card and reveals its real body.
    """
    currentChanged = Signal(int)

    def __init__(self, owner):
        super().__init__()
        self.owner = owner; self.entries = []; self.routes = {}; self.current = 0
        self.body_layout = QVBoxLayout(self)
        self.body_layout.setContentsMargins(0, 0, 0, 0); self.body_layout.setSpacing(18)
        self.body_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)

    def addTab(self, page, title):
        page.setParent(self); page.hide()
        self.entries.append((page, title)); return len(self.entries) - 1

    def count(self): return len(self.entries)
    def widget(self, index): return self.entries[index][0] if 0 <= index < self.count() else None
    def tabText(self, index): return self.entries[index][1] if 0 <= index < self.count() else ''
    def currentIndex(self): return self.current
    def currentWidget(self): return self.widget(self.current)
    def indexOf(self, page): return next((i for i, (widget, _title) in enumerate(self.entries) if widget is page), -1)

    def route(self, page, section=None, *, target=None):
        index = self.indexOf(page)
        self.routes[index] = (section, target or page)
        if section is not None:
            section.expandedChanged.connect(lambda opened, key=index: self._opened(key) if opened else None)

    def _opened(self, index):
        # Reopening the same card is a fresh explicit visit, just like returning
        # to its former tab. Read-only diagnostics should refresh on that visit.
        if self.current == index:
            self.currentChanged.emit(index)
        else:
            self._selected(index)

    def _selected(self, index):
        if self.current != index:
            self.current = index; self.currentChanged.emit(index)

    def setCurrentWidget(self, page): self.setCurrentIndex(self.indexOf(page))

    def setCurrentIndex(self, index):
        if not 0 <= index < self.count(): return
        section, target = self.routes.get(index, (None, self.widget(index)))
        if section is not None: section.button.setChecked(True)
        self._selected(index)
        QTimer.singleShot(0, self, lambda: self.owner.ensureWidgetVisible(target, 16, 16)
                          if isValid(target) and target.isVisible() else None)


class WorkspacePair(QWidget):
    def __init__(self, first, second, *, breakpoint=1080, weights=(2, 3)):
        super().__init__()
        self.first, self.second, self.breakpoint, self.weights = first, second, breakpoint, weights
        self.grid = QGridLayout(self); self.grid.setContentsMargins(0, 0, 0, 0); self.grid.setSpacing(18)
        self.narrow = None
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        self.reflow()

    def reflow(self):
        narrow = self.width() < self.breakpoint
        if narrow == self.narrow: return
        while self.grid.count(): self.grid.takeAt(0)
        self.grid.addWidget(self.first, 0, 0, Qt.AlignmentFlag.AlignTop)
        self.grid.addWidget(self.second, 1 if narrow else 0, 0 if narrow else 1, Qt.AlignmentFlag.AlignTop)
        self.grid.setColumnStretch(0, 1 if narrow else self.weights[0])
        self.grid.setColumnStretch(1, 0 if narrow else self.weights[1])
        self.narrow = narrow
        self.updateGeometry()

    def resizeEvent(self, event):
        self.reflow(); super().resizeEvent(event)


class ResizeRelay(QObject):
    def __init__(self, widget, callback):
        super().__init__(widget)
        self.timer = QTimer(self); self.timer.setSingleShot(True)
        self.timer.timeout.connect(callback); widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Resize and not self.timer.isActive(): self.timer.start(0)
        return False
