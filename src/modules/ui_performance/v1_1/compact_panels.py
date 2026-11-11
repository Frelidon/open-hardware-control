# SPDX-License-Identifier: GPL-3.0-or-later
"""Small compositional containers; no theme overrides or background layers."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QToolButton, QVBoxLayout, QWidget


class Disclosure(QWidget):
    def __init__(self, title, body, expanded=False):
        super().__init__()
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        self.button=QToolButton();self.button.setText(title)
        self.button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.button.setCheckable(True);self.button.setChecked(expanded)
        self.body=body
        layout.addWidget(self.button);layout.addWidget(body)
        self.button.toggled.connect(self.toggle)
        self.toggle(expanded)

    def toggle(self,expanded):
        self.body.setVisible(expanded)
        self.button.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)


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
