# SPDX-License-Identifier: GPL-3.0-or-later
"""Adaptive columns/tabs keep the same live form widgets and draft values."""
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QTabWidget, QVBoxLayout, QWidget
from modules.ui_performance.v1_1.dynamic_text import remember


class EditorSections(QWidget):
    def __init__(self, host, sections):
        super().__init__()
        self.host, self.sections = host, sections
        self.wide = False
        self.last_tab = 0
        self.setObjectName("caseEditorSections")
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0)
        self.columns = QWidget()
        row = QHBoxLayout(self.columns); row.setContentsMargins(0, 0, 0, 0); row.setSpacing(12)
        self.tabs = QTabWidget(); self.tabs.setObjectName("caseEditorTabs")
        self.tabs.setDocumentMode(True)
        root.addWidget(self.columns); root.addWidget(self.tabs)
        self.columns.hide()
        for caption, widget in sections:
            self.tabs.addTab(widget, host.tr_static(caption))
        remember(host, self.tabs, tabs=[caption for caption, _widget in sections])

    def minimumSizeHint(self):  # noqa: N802
        # The hidden two-column view must never force the whole app wider.
        return QSize(0, max(widget.minimumSizeHint().height() for _, widget in self.sections) + (0 if self.wide else 42))

    def resizeEvent(self, event):  # noqa: N802
        threshold = max(620, sum(widget.minimumSizeHint().width() for _, widget in self.sections) + 12)
        wide = self.width() >= threshold
        if wide != self.wide:
            self.wide = wide
            if wide:
                self.last_tab = max(0, self.tabs.currentIndex())
                while self.tabs.count(): self.tabs.removeTab(0)
                self.tabs.hide()
                for _caption, widget in self.sections:
                    self.columns.layout().addWidget(widget, 1)
                    widget.show()
                self.columns.show()
            else:
                self.columns.hide()
                for caption, widget in self.sections:
                    self.columns.layout().removeWidget(widget)
                    self.tabs.addTab(widget, self.host.tr_static(caption))
                self.tabs.setCurrentIndex(min(self.last_tab, self.tabs.count() - 1))
                self.tabs.show()
        super().resizeEvent(event)


def adapt_topology(host, editor):
    """Only the inline LED form is rearranged; physical geometry is untouched."""
    if editor.property("caseResponsive"): return
    editor.setProperty("caseResponsive", True)
    root = editor.layout()
    parts = [root.takeAt(0).widget() for _ in range(root.count())]
    group, direction_label, movement, note, error = parts
    # removeWidget preserves the Python/Qt ownership of the live preview.  A
    # discarded takeRow result can release its wrapper while timers still use it.
    group.layout().removeWidget(editor.preview)
    details = QWidget(); left = QVBoxLayout(details); left.setContentsMargins(0, 0, 0, 0)
    left.addWidget(group); left.addWidget(direction_label); left.addWidget(movement); left.addStretch()
    preview = QGroupBox(host.tr_static("Vorschau"))
    right = QVBoxLayout(preview)
    right.addWidget(editor.preview, 1); right.addWidget(note)
    root.addWidget(EditorSections(host, [("LED-Verlauf", details), ("Vorschau", preview)]), 1)
    root.addWidget(error)
