#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compatibility window around the same embeddable reference-editor content."""
from PySide6.QtWidgets import QDialog, QVBoxLayout
from .panel import DesignLibraryPanel


class DesignLibraryDialog(QDialog):
    """Legacy callers retain their explicit Save/Cancel and state contract."""
    _folder_media = staticmethod(DesignLibraryPanel._folder_media)

    def __init__(self, state, translator=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle((translator or str)('LCD-Manager')); self.setMinimumSize(860, 520)
        layout = QVBoxLayout(self)
        self.panel = DesignLibraryPanel(state, translator, self)
        self.tree = self.panel.tree
        self.panel.saved.connect(lambda _state: self.accept())
        self.panel.canceled.connect(self.reject); layout.addWidget(self.panel)

    def state(self):
        return self.panel.state()
