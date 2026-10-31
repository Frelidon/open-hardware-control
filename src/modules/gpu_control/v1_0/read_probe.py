# SPDX-License-Identifier: GPL-3.0-or-later
"""One cancellable, bounded read-only GPU process with stale-result isolation."""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QTimer, Signal
from modules.platform_support.v1_0 import helper_command


class GpuReadProbe(QObject):
    completed = Signal(str, object)
    failed = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = None
        self.timeout = QTimer(self)
        self.timeout.setSingleShot(True)
        self.timeout.setInterval(25_000)
        self.timeout.timeout.connect(self._expire)
        self.kind = ""
        self.output = bytearray()
        self.expired = False
        self.stopped = False

    def request(self, kind: str, socket: Path, gpu_id: str = "") -> None:
        self.cancel()
        self.stopped = False
        self.expired = False
        self.kind = kind
        self.output.clear()
        process = QProcess(self)
        self.process = process
        process.readyReadStandardOutput.connect(lambda: self._read(process))
        process.finished.connect(lambda *_: self._finish(process))
        process.errorOccurred.connect(lambda error: self._finish(process)
                                     if error == QProcess.ProcessError.FailedToStart else None)
        program, arguments = helper_command(Path(__file__).with_name("read_worker.py"))
        process.start(program, arguments)
        process.write(json.dumps({"kind": kind, "socket": str(socket), "gpu_id": gpu_id}).encode() + b"\n")
        process.closeWriteChannel()
        self.timeout.start()

    def _read(self, process) -> None:
        if process is not self.process:
            return
        self.output.extend(bytes(process.readAllStandardOutput()))
        if len(self.output) > 2 * 1024 * 1024:
            self.expired = True
            process.kill()

    def _finish(self, process) -> None:
        if process is not self.process:
            return
        self.timeout.stop()
        self._read(process)
        self.process = None
        try:
            payload = json.loads(self.output)
            if self.expired or process.exitCode() != 0 or not isinstance(payload, dict):
                raise ValueError("GPU read process failed or timed out")
            if payload.get("ok") is not True or not isinstance(payload.get("data"), dict):
                raise ValueError(str(payload.get("error") or "Invalid GPU response"))
        except (ValueError, TypeError) as exc:
            if not self.stopped:
                self.failed.emit(self.kind, str(exc)[:300])
        else:
            if not self.stopped:
                self.completed.emit(self.kind, payload["data"])
        finally:
            process.deleteLater()

    def _expire(self) -> None:
        if self.process is not None:
            self.expired = True
            self.process.kill()

    def cancel(self) -> None:
        self.stopped = True
        self.timeout.stop()
        process, self.process = self.process, None
        if process is not None:
            process.kill()
            process.waitForFinished(500)
            process.deleteLater()
