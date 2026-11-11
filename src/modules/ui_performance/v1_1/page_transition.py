# SPDX-License-Identifier: GPL-3.0-or-later
"""Reveal a live content page without snapshots or graphics-effect buffers."""

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import QWidget
from shiboken6 import isValid


def transition_duration(settings) -> int:
    try:
        value = int(settings.value("performance/transition_duration_ms", 380))
    except (TypeError, ValueError, OverflowError):
        return 380
    return value if value in {220, 380, 550} else 380


class TransitionOverlay(QWidget):
    """Fade a background veil while the real page optionally glides into place."""

    def __init__(self, parent: QWidget, style: str, accent: QColor) -> None:
        super().__init__(parent)
        self.style_name = style
        self.accent = accent
        self.progress = 1.0
        self.origin = None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.hide()

    def prepare(self, style: str) -> None:
        page = self.parentWidget()
        self.style_name = style
        self.origin = page.pos()
        self.background = page.palette().color(QPalette.ColorRole.Window)
        self.setGeometry(page.rect())
        self.set_progress(0.0)

    def set_progress(self, value: object) -> None:
        self.progress = max(0.0, min(1.0, float(value)))
        page = self.parentWidget()
        if self.origin is not None and isValid(page):
            remaining = 1.0 - self.progress
            offset = (QPoint(round(32 * remaining), 0) if self.style_name == "slide"
                      else QPoint(0, round(24 * remaining)) if self.style_name == "rise"
                      else QPoint())
            page.move(self.origin + offset)
        self.update()

    def finish(self) -> None:
        page = self.parentWidget()
        origin, self.origin = self.origin, None
        if origin is not None and page is not None and isValid(page):
            page.move(origin)
        self.progress = 1.0
        self.hide()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        background = QColor(self.background)
        background.setAlphaF(1.0 - self.progress)
        painter.fillRect(self.rect(), background)
        if self.style_name == "glow":
            accent = QColor(self.accent)
            accent.setAlpha(round(70 * (1.0 - self.progress)))
            painter.fillRect(0, 0, self.width(), 2, accent)
