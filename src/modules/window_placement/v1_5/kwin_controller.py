# SPDX-License-Identifier: GPL-3.0-or-later
"""Nonblocking compositor-side placement of OHC's own Wayland window."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any

from PySide6.QtCore import QProcess, QTimer


_BRIDGE = Path(__file__).with_name("kwin_bridge.py")
_SUCCESS = {"correct", "moved"}
_RETRY = {"window-missing", "unconfirmed", "reply-timeout"}


def is_kwin_wayland() -> bool:
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").upper().split(":")
    return os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland" and "KDE" in desktop


def reset_kwin_confirmation(window: Any) -> None:
    window._kwin_placement_confirmed = False
    window._kwin_placement_attempts = 0


def request_kwin_confirmation(window: Any, reason: str) -> None:
    """Run one bounded child; only KWin's own output is a confirmation."""
    if not is_kwin_wayland() or not window.isVisible() or window.isMinimized():
        return
    if getattr(window, "_kwin_placement_confirmed", False):
        return
    if getattr(window, "_kwin_placement_process", None) is not None:
        return
    attempts = int(getattr(window, "_kwin_placement_attempts", 0))
    if attempts >= 2:
        return
    screen, _matched = window.preferred_window_screen()
    target = str(screen.name()).strip() if screen is not None else ""
    if not target:
        return
    window._kwin_placement_attempts = attempts + 1
    process = QProcess(window)
    window._kwin_placement_process = process
    finished = {"done": False}
    process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)

    def complete(*_args: object) -> None:
        if getattr(window, "_kwin_placement_process", None) is not process:
            return
        finished["done"] = True
        window._kwin_placement_process = None
        raw = bytes(process.readAllStandardOutput()).decode("utf-8", "replace").strip()
        try:
            result = json.loads(raw.splitlines()[-1])
        except (ValueError, IndexError):
            result = {"state": "invalid-reply"}
        state = str(result.get("state", "invalid-reply")) if isinstance(result, dict) else "invalid-reply"
        before = str(result.get("before", "")) if isinstance(result, dict) else ""
        after = str(result.get("after", "")) if isinstance(result, dict) else ""
        geometry = str(result.get("geometry", "")) if isinstance(result, dict) else ""
        if state in _SUCCESS and after == target:
            window._kwin_placement_confirmed = True
            window.log_message(
                f"FENSTERPOSITION: {reason} · KWin bestätigt={after} · vorher={before or '<unbekannt>'}"
                f" · Geometrie={geometry or '<unbekannt>'}"
            )
        else:
            window.log_message(
                f"FENSTERPOSITION: {reason} · KWin nicht bestätigt · Ziel={target} · "
                f"Ist={after or '<unbekannt>'} · Status={state}"
            )
            if state in _RETRY and window._kwin_placement_attempts < 2:
                QTimer.singleShot(650, window, lambda: request_kwin_confirmation(window, reason + " · Wiederholung"))
        process.deleteLater()

    process.finished.connect(complete)
    process.errorOccurred.connect(lambda _error: complete() if process.state() == QProcess.ProcessState.NotRunning else None)
    process.start(sys.executable, [str(_BRIDGE), str(os.getpid()), target])
    QTimer.singleShot(5000, process, lambda: process.kill() if not finished["done"]
                      and process.state() == QProcess.ProcessState.Running else None)
