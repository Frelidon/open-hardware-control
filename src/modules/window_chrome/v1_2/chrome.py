#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Accessible custom title bar with Wayland-safe move and resize delegation."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPointF, Qt, QTimer
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPushButton, QWidget


def edge_at_position(position: QPointF, width: int, height: int, margin: int = 7) -> Qt.Edge:
    """Return the resize edges at a local window position."""

    edge = Qt.Edge(0)
    if position.x() <= margin:
        edge |= Qt.Edge.LeftEdge
    elif position.x() >= width - margin:
        edge |= Qt.Edge.RightEdge
    if position.y() <= margin:
        edge |= Qt.Edge.TopEdge
    elif position.y() >= height - margin:
        edge |= Qt.Edge.BottomEdge
    return edge


def _cursor_for_edge(edge: Qt.Edge) -> Qt.CursorShape:
    if edge in {Qt.Edge.LeftEdge, Qt.Edge.RightEdge}:
        return Qt.CursorShape.SizeHorCursor
    if edge in {Qt.Edge.TopEdge, Qt.Edge.BottomEdge}:
        return Qt.CursorShape.SizeVerCursor
    if edge in {
        Qt.Edge.TopEdge | Qt.Edge.LeftEdge,
        Qt.Edge.BottomEdge | Qt.Edge.RightEdge,
    }:
        return Qt.CursorShape.SizeFDiagCursor
    if edge:
        return Qt.CursorShape.SizeBDiagCursor
    return Qt.CursorShape.ArrowCursor


class FramelessResizeController(QObject):
    """Use the window-system resize operation instead of manual geometry math."""

    def __init__(self, window: QWidget, margin: int = 7):
        super().__init__(window)
        self.window: QWidget | None = window
        self._app = QApplication.instance()
        self._cursor_widget: QWidget | None = None
        self.margin = max(4, min(16, int(margin)))
        window.setMouseTracking(True)
        window.destroyed.connect(self.detach)
        if self._app is not None:
            self._app.installEventFilter(self)
        else:
            window.installEventFilter(self)

    def detach(self, *_args: object) -> None:
        """Remove the global filter before Shiboken invalidates the window wrapper."""
        self.clear_resize_cursor()
        if self._app is not None:
            self._app.removeEventFilter(self)
        self.window = None

    def clear_resize_cursor(self) -> None:
        """Remove every cursor override installed by the resize edge helper."""
        widget = self._cursor_widget
        self._cursor_widget = None
        if widget is not None:
            try:
                widget.unsetCursor()
            except RuntimeError:
                pass

    def _set_resize_cursor(self, widget: QWidget, edge: Qt.Edge) -> None:
        if not edge:
            self.clear_resize_cursor()
            return
        if self._cursor_widget is not widget:
            self.clear_resize_cursor()
        widget.setCursor(_cursor_for_edge(edge))
        self._cursor_widget = widget

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        window = self.window
        if window is None or not isinstance(watched, QWidget):
            return False
        abort_events = {
            QEvent.Type.Leave,
            QEvent.Type.Hide,
            QEvent.Type.Close,
            QEvent.Type.Destroy,
            QEvent.Type.WindowDeactivate,
            QEvent.Type.WindowStateChange,
        }
        if event.type() in abort_events:
            self.clear_resize_cursor()
        try:
            belongs_to_window = watched is window or window.isAncestorOf(watched)
            unavailable = window.isMaximized() or window.isFullScreen()
        except RuntimeError:
            self.detach()
            return False
        if not belongs_to_window:
            return False
        if unavailable or not window.isVisible():
            self.clear_resize_cursor()
            return False
        window_control = bool(watched.property("windowControlHitTarget"))
        if window_control:
            self.clear_resize_cursor()
            return False
        local_position = watched.mapTo(window, event.position().toPoint()) if isinstance(event, QMouseEvent) else None
        if event.type() == QEvent.Type.MouseMove and isinstance(event, QMouseEvent):
            edge = edge_at_position(QPointF(local_position), window.width(), window.height(), self.margin)
            self._set_resize_cursor(watched, edge)
        elif event.type() == QEvent.Type.MouseButtonPress and isinstance(event, QMouseEvent):
            if event.button() == Qt.MouseButton.LeftButton:
                edge = edge_at_position(QPointF(local_position), window.width(), window.height(), self.margin)
                handle = window.windowHandle()
                if edge and handle is not None and handle.startSystemResize(edge):
                    event.accept()
                    return True
        return False


class WindowChrome(QWidget):
    """Compact application title bar with keyboard-accessible window actions."""

    def __init__(self, window: QWidget, title: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.window = window
        self.setObjectName("windowChrome")
        self.setFixedHeight(42)
        self.setMouseTracking(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 0, 0)
        layout.setSpacing(5)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("windowChromeTitle")
        layout.addWidget(self.title_label)
        layout.addStretch()
        self.minimize_button = self._button("−", "Fenster minimieren")
        self.maximize_button = self._button("□", "Fenster maximieren")
        self.close_button = self._button("×", "Fenster schließen", "windowCloseButton")
        self.close_button.setFixedSize(48, 42)
        minimize = getattr(window, "minimize_to_tray", window.showMinimized)
        self.minimize_button.clicked.connect(minimize)
        self.maximize_button.clicked.connect(self.toggle_maximized)
        self.close_button.clicked.connect(window.close)
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)
        self._captions = {
            "minimize": "Fenster minimieren", "maximize": "Fenster maximieren",
            "restore": "Fenster wiederherstellen", "close": "Fenster schließen",
        }

    def _button(self, text: str, accessible_name: str, name: str = "windowChromeButton") -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(name)
        button.setAccessibleName(accessible_name)
        button.setToolTip(accessible_name)
        button.setProperty("windowControlHitTarget", True)
        button.setFixedSize(34, 30)
        return button

    def toggle_maximized(self) -> None:
        if self.window.isMaximized():
            self.window.showNormal()
            restore = getattr(self.window, "restore_safe_windowed_geometry", None)
            if callable(restore) and not getattr(self.window, "_window_restore_pending", False):
                QTimer.singleShot(0, lambda: restore("Fensterleiste: Wiederherstellen"))
        else:
            remember = getattr(self.window, "remember_windowed_geometry", None)
            if callable(remember):
                remember()
            self.window.showMaximized()
        self.sync_state()

    def sync_state(self) -> None:
        maximized = self.window.isMaximized()
        self.maximize_button.setText("❐" if maximized else "□")
        caption = self._captions["restore"] if maximized else self._captions["maximize"]
        self.maximize_button.setAccessibleName(caption)
        self.maximize_button.setToolTip(caption)

    def set_translations(self, minimize: str, maximize: str, restore: str, close: str) -> None:
        self._captions = {
            "minimize": minimize, "maximize": maximize, "restore": restore, "close": close,
        }
        self.minimize_button.setAccessibleName(minimize)
        self.minimize_button.setToolTip(minimize)
        self.close_button.setAccessibleName(close)
        self.close_button.setToolTip(close)
        self.sync_state()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximized()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and not self.window.isMaximized():
            handle = self.window.windowHandle()
            if handle is not None and handle.startSystemMove():
                event.accept()
                return
        super().mousePressEvent(event)
