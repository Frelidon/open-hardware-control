# SPDX-License-Identifier: GPL-3.0-or-later
"""Current-page geometry without reserving the tallest hidden workspace."""
from PySide6.QtCore import QSize, Signal, Qt
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget


class CurrentPageStack(QStackedWidget):
    def minimumSizeHint(self):
        page = self.currentWidget()
        return QSize(0, page.minimumSizeHint().height() if page else 0)

    def sizeHint(self):
        page = self.currentWidget()
        return QSize(0, page.sizeHint().height() if page else 0)


class WorkspaceTabs(QWidget):
    currentChanged = Signal(int)
    TITLES = ('Bibliothek', 'Komposition', 'Displaybetrieb')

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(16)
        strip = QHBoxLayout(); strip.setSpacing(8)
        self.group = QButtonGroup(self); self.buttons = []
        self.stack = CurrentPageStack(); self.stack.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        for index, title in enumerate(self.TITLES):
            button = QPushButton(title); button.setCheckable(True); button.setMinimumHeight(44)
            self.group.addButton(button); self.buttons.append(button)
            button.clicked.connect(lambda _checked=False, selected=index: self.setCurrentIndex(selected))
            strip.addWidget(button)
            page = QWidget(); layout = QVBoxLayout(page)
            layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(14)
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.stack.addWidget(page)
        root.addLayout(strip); root.addWidget(self.stack)
        self.setCurrentIndex(0)

    def currentIndex(self): return self.stack.currentIndex()
    def widget(self, index): return self.stack.widget(index)
    def count(self): return self.stack.count()

    def setCurrentIndex(self, index):
        if not 0 <= index < self.stack.count(): return
        self.stack.setCurrentIndex(index); self.buttons[index].setChecked(True)
        self.stack.updateGeometry(); self.updateGeometry(); self.currentChanged.emit(index)
