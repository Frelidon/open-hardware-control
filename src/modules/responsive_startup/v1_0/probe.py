#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-blocking Qt probe for the competing CoolerControl owner."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from PySide6.QtCore import QObject, QProcess, QTimer, Signal
from shiboken6 import isValid

from cooling_ownership import CoolingOwnerStatus


class CoolingOwnershipProbe(QObject):
    """Run the bounded systemd/process inspection outside the GUI process."""

    result_ready = Signal(object)
    failed = Signal(str)

    def __init__(self, *, process_tracker=None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._pending = False
        self._timeout_detail = ""
        self._failed_to_start = False
        self._stdout = bytearray()
        self._stderr = bytearray()
        self._shutting_down = False
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.errorOccurred.connect(self._process_error)
        self.process.finished.connect(self._finished)
        self.timeout = QTimer(self)
        self.timeout.setSingleShot(True)
        self.timeout.setInterval(8_000)
        self.timeout.timeout.connect(self._timed_out)
        self.process_tracker = process_tracker

    @property
    def busy(self) -> bool:
        return isValid(self.process) and self.process.state() != QProcess.ProcessState.NotRunning

    def request(self) -> None:
        if self._shutting_down or not isValid(self.process):
            return
        if self.busy:
            self._pending = True
            return
        self._stdout.clear()
        self._stderr.clear()
        self._timeout_detail = ""
        self._failed_to_start = False
        helper = Path(__file__).resolve().with_name("ownership_probe.py")
        arguments = [str(helper)]
        if self.process_tracker is not None:
            self.process_tracker(self.process)
        self.process.start(sys.executable, arguments)
        self.timeout.start()

    def _read_stdout(self) -> None:
        if isValid(self.process):
            self._stdout.extend(bytes(self.process.readAllStandardOutput()))

    def _read_stderr(self) -> None:
        if isValid(self.process):
            self._stderr.extend(bytes(self.process.readAllStandardError()))

    def _finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self.timeout.stop()
        if self._failed_to_start:
            self._failed_to_start = False
            return
        self._read_stdout()
        self._read_stderr()
        if self._timeout_detail:
            self.failed.emit(self._timeout_detail)
            self._timeout_detail = ""
        else:
            try:
                payload = json.loads(self._stdout.decode("utf-8", errors="replace"))
                if exit_code != 0 or not isinstance(payload, dict):
                    raise ValueError(self._stderr.decode("utf-8", errors="replace").strip())
                status = CoolingOwnerStatus(
                    coolercontrol_service_active=bool(payload["service_active"]),
                    coolercontrol_process_active=bool(payload["process_active"]),
                    coolercontrol_service_enabled=bool(payload["service_enabled"]),
                )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                self.failed.emit(str(exc)[:240] or "ungültige Statusantwort")
            else:
                self.result_ready.emit(status)
        if self._pending and not self._shutting_down:
            self._pending = False
            QTimer.singleShot(0, self.request)

    def _timed_out(self) -> None:
        if self.busy:
            self._timeout_detail = "Statusprüfung nach 8 Sekunden beendet"
            self.process.kill()

    def _process_error(self, error: QProcess.ProcessError) -> None:
        if error != QProcess.ProcessError.FailedToStart:
            return
        self._failed_to_start = True
        self.timeout.stop()
        self.failed.emit("Statusprüfung konnte nicht gestartet werden")
        if self._pending and not self._shutting_down:
            self._pending = False
            QTimer.singleShot(0, self.request)

    def shutdown(self) -> None:
        self._shutting_down = True
        self.timeout.stop()
        self._pending = False
        if self.busy:
            self.process.kill()
            self.process.waitForFinished(500)
