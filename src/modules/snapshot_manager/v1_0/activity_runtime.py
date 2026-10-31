#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistent low-priority activity probe orchestration outside page layout."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QProcess, QTimer
from shiboken6 import isValid

from modules.platform_support.v1_0 import helper_command


class ActivityProbeRuntime(QObject):
    """Own one reusable worker and deliver bounded JSON samples to the page."""

    def __init__(
        self, parent: QObject, script: Path,
        sample_callback: Callable[[object], None], log_callback: Callable[[str], None],
    ) -> None:
        super().__init__(parent)
        self.script = script
        self.sample_callback = sample_callback
        self.log_callback = log_callback
        self.process: QProcess | None = None
        self.buffer = bytearray()
        self.sample_seen = False
        self.enabled = False
        self.arguments: tuple[str, int, int] = ("", 65, 20)

    def start(self, names: str, busy_core_percent: int, interval_seconds: int) -> None:
        self.arguments = (names, int(busy_core_percent), int(interval_seconds))
        self.enabled = True
        if self.process is not None:
            return
        process = QProcess(self)
        self.process = process
        self.buffer.clear()
        self.sample_seen = False
        process.readyReadStandardOutput.connect(lambda child=process: self._ready(child))
        process.finished.connect(
            lambda exit_code, status, child=process: self._finished(child, exit_code, status)
        )
        process.errorOccurred.connect(
            lambda _error, child=process: self._finished(
                child, -1, QProcess.ExitStatus.NormalExit,
            )
        )
        program, arguments = helper_command(self.script, (
            names, busy_core_percent, "--watch", interval_seconds,
        ))
        process.start(program, arguments)
        QTimer.singleShot(5_000, self, lambda child=process: self._expire_start(child))

    def restart(
        self, names: str, busy_core_percent: int, interval_seconds: int, *, enabled: bool,
    ) -> None:
        self.enabled = bool(enabled)
        self.arguments = (names, int(busy_core_percent), int(interval_seconds))
        self.stop()
        self.enabled = bool(enabled)
        if self.enabled:
            QTimer.singleShot(250, self, self._restart_saved)

    def _restart_saved(self) -> None:
        if self.enabled and self.process is None:
            self.start(*self.arguments)

    def _ready(self, process: QProcess) -> None:
        if self.process is not process:
            return
        self.buffer.extend(bytes(process.readAllStandardOutput()))
        if len(self.buffer) > 65_536:
            self.log_callback("Aktivitätswächter: Antwort über der Größenbegrenzung verworfen")
            self.buffer.clear()
            return
        while b"\n" in self.buffer:
            line, _, remaining = self.buffer.partition(b"\n")
            self.buffer = bytearray(remaining)
            if not line.strip():
                continue
            try:
                payload = json.loads(line.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError):
                continue
            self.sample_seen = True
            self.sample_callback(payload)

    def _finished(
        self, process: QProcess, exit_code: int, _status: QProcess.ExitStatus,
    ) -> None:
        if isValid(process):
            process.deleteLater()
        if self.process is not process:
            return
        self.process = None
        self.buffer.clear()
        if self.enabled:
            QTimer.singleShot(5_000 if exit_code else 1_000, self, self._restart_saved)

    def _expire_start(self, process: QProcess) -> None:
        if self.process is process and not self.sample_seen:
            self.log_callback("Aktivitätswächter nach 5 Sekunden ohne erste Antwort beendet")
            self.stop()
            self.enabled = True
            QTimer.singleShot(5_000, self, self._restart_saved)

    def stop(self) -> None:
        self.enabled = False
        process, self.process = self.process, None
        self.buffer.clear()
        if process is None:
            return
        try:
            if process.state() != QProcess.ProcessState.NotRunning:
                process.terminate()
                QTimer.singleShot(1_000, self, lambda child=process: self._kill_if_running(child))
            else:
                process.deleteLater()
        except RuntimeError:
            pass

    @staticmethod
    def _kill_if_running(process: QProcess) -> None:
        if not isValid(process):
            return
        try:
            if process.state() != QProcess.ProcessState.NotRunning:
                process.kill()
        except RuntimeError:
            pass
