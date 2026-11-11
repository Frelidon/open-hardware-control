# SPDX-License-Identifier: GPL-3.0-or-later
"""Palette-aware accessible cards; user profile names remain user data."""
from PySide6.QtCore import Qt, Signal, QEvent, QRectF
from PySide6.QtGui import QPalette, QPainter, QPen
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QVBoxLayout
from modules.navigation_settings.v1_0.artwork import category_icon


class ProfileCard(QFrame):
    selected = Signal(str)

    def __init__(self, profile, tr, parent=None):
        super().__init__(parent)
        self._selected = False
        self.ident = str(profile.get("id", ""))
        self.setObjectName("profileLibraryCard")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName(str(profile.get("name", "")))
        layout = QHBoxLayout(self); layout.setContentsMargins(12, 10, 12, 10)
        self.icon = QLabel(); self.icon.setPixmap(category_icon("profiles", self.palette(), 36).pixmap(36, 36))
        layout.addWidget(self.icon)
        text = QVBoxLayout(); text.setSpacing(4)
        builtin = bool(profile.get("builtin"))
        name = str(profile.get("name", ""))
        title = QLabel(tr(name) if builtin else name); title.setWordWrap(True)
        font = title.font(); font.setBold(True); title.setFont(font)
        text.addWidget(title)
        badge = QLabel(tr("Standardprofil" if builtin else "Eigenes Profil") + " · " + tr(str(profile.get("category", "Gesamt"))))
        badge.setObjectName("muted"); badge.setWordWrap(True); text.addWidget(badge)
        layout.addLayout(text, 1)
        self.set_selected(False)

    def set_selected(self, selected):
        self._selected = bool(selected)
        self.icon.setPixmap(category_icon("profiles", QApplication.palette(), 36).pixmap(36, 36))
        self.update()

    def paintEvent(self, _event):
        palette = QApplication.palette()
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = palette.color(QPalette.ColorRole.Highlight if self._selected or self.hasFocus() else QPalette.ColorRole.Mid)
        painter.setPen(QPen(color, 2 if self.hasFocus() else 1))
        painter.setBrush(palette.color(QPalette.ColorRole.Base))
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(1,1,-1,-1), 12, 12)
        painter.end()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.PaletteChange and hasattr(self, 'icon'):
            self.icon.setPixmap(category_icon("profiles", QApplication.palette(), 36).pixmap(36, 36))
            self.update()
        super().changeEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self.ident)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.selected.emit(self.ident); event.accept()
        else:
            super().keyPressEvent(event)
