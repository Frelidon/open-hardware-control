# SPDX-License-Identifier: GPL-3.0-or-later
"""Scroll the existing viewport, without screenshots or layout animation."""
from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPoint, Qt, QPropertyAnimation, QTimer
from PySide6.QtWidgets import QScrollArea
from shiboken6 import isValid


def enclosing_scroll(widget):
    parent = widget.parentWidget()
    while parent is not None:
        if isinstance(parent, QScrollArea):
            return parent
        parent = parent.parentWidget()
    return None


def animations_enabled(widget):
    settings = getattr(widget.window(), 'settings', None)
    return settings is None or settings.value('performance/transitions_enabled', True, type=bool)


class SectionReveal(QObject):
    def __init__(self, scroll):
        super().__init__(scroll)
        self.scroll = scroll
        self.animation = QPropertyAnimation(scroll.verticalScrollBar(), b'value', self)
        self.animation.setDuration(420)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.finished.connect(self.finished)
        self.owner = None
        self.origin = 0
        self.completion = None
        self.generation = 0
        scroll.viewport().installEventFilter(self)
        scroll.verticalScrollBar().installEventFilter(self)
        scroll.verticalScrollBar().sliderPressed.connect(self.cancel)
        scroll.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() in (QEvent.Type.Wheel, QEvent.Type.TouchBegin):
            self.cancel()
        elif event.type() == QEvent.Type.MouseButtonPress and watched is self.scroll.verticalScrollBar():
            self.cancel()
        elif event.type() == QEvent.Type.KeyPress and event.key() in (Qt.Key.Key_Home, Qt.Key.Key_End, Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
            self.cancel()
        elif event.type() == QEvent.Type.Hide and watched is self.scroll:
            self.cancel()
        return super().eventFilter(watched, event)

    def cancel(self):
        self.generation += 1
        self.animation.stop()
        self.owner = None
        completion, self.completion = self.completion, None
        if completion is not None:
            completion()

    def finished(self):
        completion, self.completion = self.completion, None
        if completion is not None:
            self.owner = None
            completion()

    def animate(self, target, completion=None):
        bar = self.scroll.verticalScrollBar()
        target = max(bar.minimum(), min(bar.maximum(), round(target)))
        self.animation.stop()
        self.completion = completion
        if target == bar.value():
            self.finished()
            return
        self.animation.setStartValue(bar.value())
        self.animation.setEndValue(target)
        self.animation.start()

    def opened(self, section):
        self.cancel()
        self.owner, self.origin = section, self.scroll.verticalScrollBar().value()
        generation = self.generation

        def reveal():
            if (self.generation != generation or not isValid(section)
                    or not section.button.isChecked() or not section.isVisible()):
                return
            viewport = self.scroll.viewport()
            top = section.mapTo(viewport, QPoint()).y()
            height, available = section.height(), viewport.height()
            if height + 32 > available or top < 16:
                target = self.scroll.verticalScrollBar().value() + top - 16
            elif top + height > available - 16:
                target = self.scroll.verticalScrollBar().value() + top + height - available + 16
            else:
                return
            self.animate(target)
        QTimer.singleShot(0, self, lambda: QTimer.singleShot(0, self, reveal))

    def closing(self, section, completion):
        if self.owner is not section:
            return False
        self.generation += 1
        self.animate(self.origin, completion)
        return True


def scroller(section):
    scroll = enclosing_scroll(section)
    if scroll is None:
        return None
    controller = getattr(scroll, '_ohc_section_reveal', None)
    if not animations_enabled(section):
        if controller is not None: controller.cancel()
        return None
    if controller is None:
        controller = SectionReveal(scroll)
        scroll._ohc_section_reveal = controller
    return controller
