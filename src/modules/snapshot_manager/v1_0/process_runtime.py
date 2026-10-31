#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded asynchronous process boundary for the Snapshot Manager."""

from __future__ import annotations

import json
import os
from pathlib import Path
from PySide6.QtCore import QProcess, QTimer
from shiboken6 import isValid
from modules.platform_support.v1_0 import helper_command

HELPER = Path("/usr/libexec/open-hardware-control-snapshot-helper")
ADMIN_HELPER = Path("/usr/libexec/open-hardware-control-snapshot-admin-helper")
ADMIN_ACTIONS = frozenset({"create", "delete", "setup-root"})
PKEXEC_CANDIDATES = (Path("/usr/bin/pkexec"), Path("/bin/pkexec"))


class SnapshotProcessRuntimeMixin:
    def _log(self, message: str) -> None:
        callback = getattr(self.host, "log_message", None)
        if callable(callback):
            callback(f"SNAPSHOT: {message}")

    def refresh_system(self) -> None:
        if self._processes_stopped or self.probe_process is not None:
            return
        process = QProcess(self)
        self.probe_process = process
        process.finished.connect(lambda code, status, child=process: self._probe_finished(child, code, status))
        process.errorOccurred.connect(
            lambda _error, child=process: self._probe_finished(child, -1, QProcess.ExitStatus.NormalExit)
        )
        program, arguments = helper_command(Path(__file__).with_name("probe.py"))
        process.start(program, arguments)
        QTimer.singleShot(8_000, self, lambda: self._expire(process, "system-probe", 8))

    def _probe_finished(self, process: QProcess, exit_code: int, _status: QProcess.ExitStatus) -> None:
        if self.probe_process is not process:
            return
        self.probe_process = None
        process.deleteLater()
        if exit_code != 0:
            self.os_label.setText(self.tr("Erkennung nicht verfügbar"))
            return
        try:
            output = bytes(process.readAllStandardOutput())
            if len(output) > 524288:
                return
            report = json.loads(output.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return
        if isinstance(report, dict) and report.get("schema") == 1:
            self.report = report
            self._populate_report()

    def run_helper(self, action: str, arguments: list[str]) -> bool:
        if self._processes_stopped or self.helper_process is not None:
            self._log(
                f"Aktion '{action}' nicht gestartet · Helfer belegt durch "
                f"'{self.pending_helper_action or 'unbekannt'}'"
            )
            target = self._action_target(action)
            target.setText(self.tr("Eine andere Snapshot-Aktion läuft noch. Bitte kurz warten."))
            return False
        pkexec = next((path for path in PKEXEC_CANDIDATES if path.is_file()), None)
        helper = ADMIN_HELPER if action in ADMIN_ACTIONS else HELPER
        if not pkexec or not helper.is_file():
            target = self._action_target(action)
            target.setText(self.tr("Snapshot-Helfer ist noch nicht installiert."))
            missing = "pkexec" if not pkexec else helper.name
            self._log(f"Aktion '{action}' nicht gestartet · fehlt={missing}")
            return False
        process = QProcess(self)
        self.helper_process = process
        self.pending_helper_action = action
        process.started.connect(
            lambda selected=helper, requested=action, child=process: self._log(
                f"Polkit-Anfrage gestartet · Aktion={requested} · "
                f"Helfer={selected.name} · PID={int(child.processId())} · "
                f"Sitzung={os.environ.get('XDG_SESSION_TYPE', 'unbekannt')} · "
                f"KDE-Agentbus={'vorhanden' if os.environ.get('DBUS_SESSION_BUS_ADDRESS') else 'fehlt'}"
            )
        )
        process.finished.connect(
            lambda exit_code, status, child=process, requested=action:
                self._helper_finished(child, requested, exit_code, status)
        )
        process.errorOccurred.connect(
            lambda error, child=process, requested=action:
                self._helper_process_error(child, requested, error)
        )
        self._log(
            f"Polkit-Anfrage vorbereitet · Aktion={action} · Helfer={helper.name} · "
            f"dauerhafte Automatikfreigabe={'ja' if self._persistent_authorized() else 'nein'}"
        )
        process.start(str(pkexec), [str(helper), action, *arguments])
        QTimer.singleShot(90_000, self, lambda: self._expire(process, action, 90))
        return True

    def _helper_process_error(
        self, process: QProcess, action: str, error: QProcess.ProcessError,
    ) -> None:
        if self.helper_process is not process:
            return
        self._log(f"Polkit-Prozessfehler · Aktion={action} · Qt-Fehler={error.name}")
        self._helper_finished(process, action, -1, QProcess.ExitStatus.NormalExit)

    def _expire(self, process: QProcess, action: str, timeout_seconds: int) -> None:
        if not isValid(process):
            return
        try:
            if process.state() != QProcess.ProcessState.NotRunning:
                self._log(
                    f"Snapshot-Prozess nach {timeout_seconds} Sekunden beendet · Aktion={action} · "
                    + (
                        "möglicherweise kein Authentifizierungsagent erreichbar"
                        if timeout_seconds >= 90 else "begrenzte Hintergrundprüfung hat nicht geantwortet"
                    )
                )
                process.kill()
        except RuntimeError:
            # The owning page may already have disposed the Qt process.
            return

    def stop_processes(self) -> None:
        self._processes_stopped = True
        self.poll_timer.stop()
        self.activity_runtime.stop()
        processes = (self.probe_process, self.helper_process)
        self.probe_process = self.helper_process = None
        for process in processes:
            if process is not None and isValid(process) and process.state() != QProcess.ProcessState.NotRunning:
                process.kill()
