# SPDX-License-Identifier: GPL-3.0-or-later
"""Small compositional containers; no theme overrides or background layers."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QWidget
from modules.ui_sections.v1_0.cards import SectionCard


class Disclosure(SectionCard):
    """Compatibility constructor backed by the shared full-width section card."""
    def __init__(self, title, body, expanded=False):
        super().__init__(title, "", None, body, expanded=expanded)


class ResponsiveColumns(QWidget):
    def __init__(self, breakpoint=950):
        super().__init__()
        self.breakpoint=breakpoint
        self.columns=QBoxLayout(QBoxLayout.Direction.LeftToRight,self)
        self.columns.setContentsMargins(0,0,0,0);self.columns.setSpacing(14)

    def addWidget(self,widget,stretch=1):
        self.columns.addWidget(widget,stretch)

    def resizeEvent(self,event):
        self.columns.setDirection(QBoxLayout.Direction.TopToBottom if self.width()<self.breakpoint else QBoxLayout.Direction.LeftToRight)
        super().resizeEvent(event)
