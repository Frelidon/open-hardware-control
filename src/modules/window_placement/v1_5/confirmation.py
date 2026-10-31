#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Post-mapping confirmation for compositor-controlled top-level windows."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication

from .placement import resolve_start_maximized
from .kwin_controller import is_kwin_wayland, request_kwin_confirmation, reset_kwin_confirmation


def _screen_name(screen: Any | None) -> str:
    try:
        return str(screen.name()).strip()
    except (AttributeError, RuntimeError, TypeError):
        return ""


def finish_initial_window_mapping(window: Any, maximize: bool) -> None:
    """Reveal the first mapped surface only in its requested final state."""
    if maximize:
        window.setWindowState(window.windowState() | Qt.WindowState.WindowMaximized)
    else:
        window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMaximized)
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, False)
    window.show()
    sync_presentations = getattr(window, "sync_active_page_performance", None)
    if callable(sync_presentations):
        sync_presentations(window.tabs.currentIndex())
    window._window_screen_repositioning = False


def apply_initial_window_presentation(window: Any, tray_available: bool) -> None:
    """Apply the saved startup presentation without exposing an intermediate frame."""
    if not window.should_start_minimized_from_autostart():
        reset_kwin_confirmation(window)
        window.release_autostart_window_surface()
        maximize = resolve_start_maximized(window.window_start_mode, window.window_last_maximized)
        window._window_screen_repositioning = True
        window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMaximized)
        window.position_window_on_preferred_screen("Programmstart")
        QTimer.singleShot(0, window, lambda: finish_initial_window_mapping(window, maximize))
        QTimer.singleShot(350, window, lambda: confirm_window_screen_after_mapping(window, "Programmstart-Nachprüfung"))
        QTimer.singleShot(450, window, lambda: request_kwin_confirmation(window, "Programmstart-KWin-Prüfung"))
        QTimer.singleShot(1400, window, lambda: confirm_window_screen_after_mapping(window, "Programmstart-Spätprüfung"))
    elif tray_available:
        window.hide()
        window.log_message("AUTOSTART: Hauptfenster bleibt minimiert/im Tray · Einstellungen werden im Hintergrund angewendet.")
    else:
        window.release_autostart_window_surface()
        window.position_window_on_preferred_screen("minimierter Programmstart ohne Infobereich")
        window.showMinimized()
        window.log_message("AUTOSTART: Kein Tray verfügbar · Hauptfenster minimiert gestartet.")


def activate_window_from_tray(window: Any) -> None:
    """Reveal, place and confirm a window activated from its tray icon."""
    window.release_autostart_window_surface()
    reset_kwin_confirmation(window)
    window.showNormal() if window.isMinimized() else window.show()
    window.position_window_on_preferred_screen("Öffnen aus dem Infobereich")
    window.sync_active_page_performance(window.tabs.currentIndex())
    QTimer.singleShot(350, window, lambda: confirm_window_screen_after_mapping(window, "Infobereich-Nachprüfung"))
    QTimer.singleShot(450, window, lambda: request_kwin_confirmation(window, "Infobereich-KWin-Prüfung"))
    QTimer.singleShot(1400, window, lambda: confirm_window_screen_after_mapping(window, "Infobereich-Spätprüfung"))
    window.raise_()
    window.activateWindow()


def confirm_window_screen_after_mapping(window: Any, reason: str) -> bool:
    """Use Qt as a hint; only KWin can confirm its Wayland window output."""
    if not window.isVisible() or window.isMinimized():
        return False
    target, _matched = window.preferred_window_screen()
    if target is None:
        return False
    handle = window.windowHandle()
    handle_screen = handle.screen() if handle is not None else None
    geometry_screen = QApplication.screenAt(window.frameGeometry().center())
    # Under Wayland, frameGeometry() can retain the requested global position
    # although KWin mapped the surface to another output.  The mapped QWindow
    # screen is therefore authoritative when the two disagree.
    observed = handle_screen or geometry_screen
    target_name = _screen_name(target)
    observed_name = _screen_name(observed)
    if is_kwin_wayland():
        window.log_message(
            f"FENSTERPOSITION: {reason} · Qt-Sicht={observed_name or '<unbekannt>'} · "
            f"Ziel={target_name or '<unbekannt>'} · KWin-Bestätigung separat · "
            f"Fenstersurface={_screen_name(handle_screen) or '<unbekannt>'} · "
            f"Qt-Geometrie={_screen_name(geometry_screen) or '<unbekannt>'}"
        )
        return False
    if observed_name == target_name and observed_name:
        window.log_message(
            f"FENSTERPOSITION: {reason} · bestätigt={observed_name} · "
            f"Fenstersurface={_screen_name(handle_screen) or '<unbekannt>'} · "
            f"Qt-Geometrie={_screen_name(geometry_screen) or '<unbekannt>'} · "
            f"Geometrie={window.geometry().x()},{window.geometry().y()} "
            f"{window.geometry().width()}×{window.geometry().height()}"
        )
        return True
    window.log_message(
        f"FENSTERPOSITION: {reason} · Compositor-Abweichung "
        f"Ziel={target_name or '<unbekannt>'} · Ist={observed_name or '<unbekannt>'} · "
        f"Fenstersurface={_screen_name(handle_screen) or '<unbekannt>'} · "
        f"Qt-Geometrie={_screen_name(geometry_screen) or '<unbekannt>'} · wird korrigiert"
    )
    window.position_window_on_preferred_screen(f"{reason} · Nachkorrektur")
    return False
