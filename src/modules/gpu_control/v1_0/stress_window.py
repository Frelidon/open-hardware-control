# SPDX-License-Identifier: GPL-3.0-or-later
"""Nonblocking, PID-bound benchmark window presentation on KDE Wayland."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any

from PySide6.QtCore import QProcess, QTimer


BRIDGE = Path(__file__).with_name("stress_window_bridge.py")


def is_kwin_wayland() -> bool:
    desktops = os.environ.get("XDG_CURRENT_DESKTOP", "").upper().split(":")
    return os.environ.get("XDG_SESSION_TYPE", "").casefold() == "wayland" and "KDE" in desktops


def request_stress_window_state(owner: Any, benchmark: QProcess, mode: str, attempt: int = 0) -> None:
    """Ask KWin to change only the exact benchmark process window."""
    if not is_kwin_wayland() or benchmark.state() == QProcess.ProcessState.NotRunning:
        return
    process_id = getattr(benchmark, "processId", None)
    if not callable(process_id):
        return
    pid = int(process_id())
    if pid <= 1 or getattr(owner, "_stress_window_bridge", None) is not None:
        return
    helper = QProcess(owner)
    owner._stress_window_bridge = helper
    helper.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)

    def complete(*_args: object) -> None:
        if getattr(owner, "_stress_window_bridge", None) is not helper:
            return
        owner._stress_window_bridge = None
        try:
            state = json.loads(bytes(helper.readAllStandardOutput()).decode("utf-8").splitlines()[-1])["state"]
        except (IndexError, KeyError, TypeError, ValueError):
            state = "invalid-reply"
        helper.deleteLater()
        if state == "window-missing" and attempt < 2 and benchmark.state() != QProcess.ProcessState.NotRunning:
            QTimer.singleShot(350, owner, lambda: request_stress_window_state(owner, benchmark, mode, attempt + 1))
        elif hasattr(owner, "_gpu_log"):
            owner._gpu_log(f"GPU-LACT: Lasttest-Fenster · Modus={mode} · KWin={state}")

    helper.finished.connect(complete)
    helper.errorOccurred.connect(
        lambda _error: complete() if helper.state() == QProcess.ProcessState.NotRunning else None
    )
    helper.start(sys.executable, [str(BRIDGE), str(pid), mode])
    QTimer.singleShot(
        3500, helper,
        lambda: helper.kill() if helper.state() == QProcess.ProcessState.Running else None,
    )
