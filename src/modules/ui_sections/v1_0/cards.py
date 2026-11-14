# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared card surfaces. Reuse the application palette and background layer."""
from PySide6.QtCore import QEvent, Qt, QRectF, QSize, Signal
from PySide6.QtGui import QColor, QPainter, QPalette, QPen
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout
from modules.navigation_settings.v1_0.artwork import category_icon
from .reveal import scroller
from shiboken6 import isValid


class Surface(QFrame):
    def paintEvent(self, _event):
        palette = QApplication.palette()
        fill = QColor(palette.color(QPalette.ColorRole.Base))
        fill.setAlpha(232 if fill.lightness() > 150 else 218)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(palette.color(QPalette.ColorRole.Mid), 1))
        painter.setBrush(fill)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 16, 16)
        painter.end()


class SectionCard(Surface):
    expandedChanged = Signal(bool)

    def __init__(self, title, description, icon, body, *, expanded=False):
        super().__init__()
        self.icon_key = icon
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(self); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        self.button = QPushButton(title)
        self.button.setObjectName('sectionHeader')
        self.button.setCheckable(True); self.button.setMinimumHeight(56)
        self.button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button.setIconSize(QSize(24, 24))
        self.button.setStyleSheet('QPushButton#sectionHeader {text-align: left; padding: 12px 46px 12px 16px; border-radius: 14px; font-weight: 600;} QPushButton#sectionHeader:checked {color: palette(window-text);}')
        arrow_layout = QHBoxLayout(self.button); arrow_layout.setContentsMargins(0, 0, 18, 0)
        arrow_layout.addStretch()
        self.arrow = QLabel('⌄'); self.arrow.setFixedWidth(20)
        self.arrow.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        arrow_layout.addWidget(self.arrow)
        layout.addWidget(self.button)
        self.body = QFrame(); self.body.setObjectName('sectionBody')
        content = QVBoxLayout(self.body); content.setContentsMargins(18, 16, 18, 18); content.setSpacing(14)
        if description:
            label = QLabel(description); label.setObjectName('muted'); label.setWordWrap(True)
            content.addWidget(label)
        content.addWidget(body); self.content = body
        layout.addWidget(self.body)
        self.button.setChecked(expanded); self.body.setVisible(expanded)
        self.arrow.setText('⌃' if expanded else '⌄')
        self.button.toggled.connect(self.toggle)
        self.refresh_palette()

    def toggle(self, expanded):
        self.arrow.setText('⌃' if expanded else '⌄')
        controller = scroller(self)
        if expanded:
            self.body.show()
            if controller is not None: controller.opened(self)
        else:
            def hide_body():
                if isValid(self) and not self.button.isChecked(): self.body.hide(); self.updateGeometry()
            if controller is None or not controller.closing(self, hide_body): hide_body()
        self.updateGeometry(); self.expandedChanged.emit(expanded)

    def refresh_palette(self):
        if self.icon_key: self.button.setIcon(category_icon(self.icon_key, QApplication.palette(), 24))
        self.update()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.StyleChange) and hasattr(self, 'button'):
            self.refresh_palette()


def heading(text, parent_layout):
    label = QLabel(text); label.setWordWrap(True)
    label.setStyleSheet('font-size: 17px; font-weight: 650; background: transparent;')
    parent_layout.addWidget(label)
    return label
