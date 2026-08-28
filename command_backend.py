#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Frelidon contributors
"""Serial asynchronous process backend used for validated liquidctl commands."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

from app_constants import KRAKEN_MATCH, LIQUIDCTL, RGB_MATCH
from privacy_logging import redact_private_text


@dataclass
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str
    elapsed: float

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def combined(self) -> str:
        return "\n".join(part for part in (self.stdout.strip(), self.stderr.strip()) if part)


class PendingCommand:
    """A single queued liquidctl invocation."""

    def __init__(
        self,
        args: list[str],
        callback: Callable[[CommandResult], None] | None,
        error_callback: Callable[[str], None] | None,
        timeout: int,
        log_command: bool,
        log_output: bool,
    ):
        self.args = args
        self.callback = callback
        self.error_callback = error_callback
        self.timeout = timeout
        self.log_command = log_command
        self.log_output = log_output


class Backend(QObject):
    """Runs liquidctl sequentially with QProcess in Qt's main event loop.

    Version 2.0 used Python QRunnable objects in QThreadPool.  On the
    Python 3.14 / PySide6 6.11 combination this could race with Shiboken
    object destruction and crash the entire application.  QProcess is
    asynchronous without Python worker threads and also guarantees that
    callbacks update widgets only from the GUI thread.
    """

    log = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._queue: list[PendingCommand] = []
        self._current: PendingCommand | None = None
        self._process: QProcess | None = None
        self._started_at = 0.0
        self._timed_out = False
        self._shutting_down = False
        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._on_timeout)

    @staticmethod
    def kraken_args() -> list[str]:
        return [LIQUIDCTL, "--match", KRAKEN_MATCH]

    @staticmethod
    def kraken_direct_args() -> list[str]:
        """Use HID direct access for profile writes.

        With the nzxt-kraken3 kernel driver bound, liquidctl normally writes
        curves through hwmon.  Some distributions expose fixed PWM controls
        to the desktop user but keep the auto-point files root-only.  Direct
        access uses the already udev-authorized hidraw device and avoids that
        split-permission failure.
        """
        return [LIQUIDCTL, "--direct-access", "--match", KRAKEN_MATCH]

    @staticmethod
    def rgb_args() -> list[str]:
        return [LIQUIDCTL, "--match", RGB_MATCH]

    def run_async(
        self,
        args: list[str],
        callback: Callable[[CommandResult], None] | None = None,
        error_callback: Callable[[str], None] | None = None,
        timeout: int = 45,
        log_command: bool = True,
        log_output: bool = True,
    ) -> None:
        if self._shutting_down:
            return
        command = PendingCommand(
            args=list(args),
            callback=callback,
            error_callback=error_callback,
            timeout=max(1, int(timeout)),
            log_command=log_command,
            log_output=log_output,
        )
        self._queue.append(command)
        self._start_next()

    def is_idle(self) -> bool:
        """Return whether no liquidctl command is running or queued."""
        return self._process is None and self._current is None and not self._queue

    def active_process_id_for(self, executable_name: str) -> int:
        """Return the PID of a matching OHC-owned queued command, if active."""

        process = self._process
        command = self._current
        if process is None or command is None or not command.args:
            return 0
        if Path(command.args[0]).name.casefold() != str(executable_name).casefold():
            return 0
        if process.state() == QProcess.ProcessState.NotRunning:
            return 0
        return max(0, int(process.processId()))

    def _start_next(self) -> None:
        if self._shutting_down or self._process is not None or not self._queue:
            return

        self._current = self._queue.pop(0)
        command = self._current
        if command.log_command:
            self.log.emit(redact_private_text("$ " + " ".join(command.args)))

        process = QProcess(self)
        process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        process.finished.connect(self._on_finished)
        process.errorOccurred.connect(self._on_process_error)
        self._process = process
        self._started_at = time.monotonic()
        self._timed_out = False
        self._timeout_timer.start(command.timeout * 1000)
        process.start(command.args[0], command.args[1:])

    def _on_timeout(self) -> None:
        process = self._process
        command = self._current
        if process is None or command is None:
            return
        self._timed_out = True
        self.log.emit(redact_private_text(f"Zeitüberschreitung nach {command.timeout} Sekunden: {' '.join(command.args)}"))
        process.kill()

    def _on_process_error(self, error: QProcess.ProcessError) -> None:
        # Most runtime errors are followed by finished(); FailedToStart is not
        # guaranteed to be, so complete it explicitly on the next event turn.
        if error == QProcess.ProcessError.FailedToStart:
            QTimer.singleShot(0, self._finish_failed_start)

    def _finish_failed_start(self) -> None:
        if self._process is None or self._current is None:
            return
        self._complete(127, "", self._process.errorString())

    def _on_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        process = self._process
        if process is None:
            return
        stdout = bytes(process.readAllStandardOutput()).decode("utf-8", errors="replace")
        stderr = bytes(process.readAllStandardError()).decode("utf-8", errors="replace")
        if self._timed_out:
            exit_code = 124
            timeout_msg = f"Zeitüberschreitung nach {self._current.timeout if self._current else '?'} Sekunden"
            stderr = "\n".join(part for part in (stderr.strip(), timeout_msg) if part)
        self._complete(int(exit_code), stdout, stderr)

    def _complete(self, returncode: int, stdout: str, stderr: str) -> None:
        self._timeout_timer.stop()
        command = self._current
        process = self._process
        elapsed = time.monotonic() - self._started_at

        self._current = None
        self._process = None
        self._timed_out = False

        if process is not None:
            process.deleteLater()

        if command is not None:
            result = CommandResult(
                args=command.args,
                returncode=returncode,
                stdout=stdout,
                stderr=stderr,
                elapsed=elapsed,
            )
            if command.log_output and result.combined:
                self.log.emit(redact_private_text(result.combined))
            try:
                if command.callback is not None:
                    command.callback(result)
                elif not result.ok and command.error_callback is not None:
                    command.error_callback(result.combined or "Unbekannter Prozessfehler")
            except RuntimeError:
                # The window may already have been closed while a process ended.
                pass
            except Exception as exc:  # noqa: BLE001
                self.log.emit(f"Callback-Fehler: {exc}")
                if command.error_callback is not None:
                    command.error_callback(str(exc))

        if not self._shutting_down:
            QTimer.singleShot(0, self._start_next)

    def shutdown(self) -> None:
        self._shutting_down = True
        self._queue.clear()
        self._timeout_timer.stop()
        if self._process is not None:
            self._process.kill()
            self._process.waitForFinished(1000)
            self._process.deleteLater()
            self._process = None
        self._current = None
