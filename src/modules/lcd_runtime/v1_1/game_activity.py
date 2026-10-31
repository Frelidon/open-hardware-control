# SPDX-License-Identifier: GPL-3.0-or-later
"""Coalesced read-only game probe with bounded IPC and current-intent guards."""
import json
from pathlib import Path
import sys
from PySide6.QtCore import QObject, QProcess, QTimer
from modules.process_runtime.v1_1.diagnostics import record
from modules.platform_support.v1_0 import helper_command


class GameActivity(QObject):
    def __init__(self, host):
        super().__init__(host)
        self.host = host
        self.intent = ()
        self.timed_out = False
        self.timeout = QTimer(self)
        self.timeout.setSingleShot(True)
        self.timeout.timeout.connect(self.expired)
        host.gamemode_process.errorOccurred.connect(self.error)

    def poll(self):
        host = self.host
        if host.shutdown_started: return
        if not host.game_auto_detection:
            host.gamemode_active = False
            host._update_game_activity(False, '')
            return
        if host.game_manual:
            host._update_game_activity(False, '')
        if host.gamemode_process.state() != QProcess.ProcessState.NotRunning: return
        self.intent = (
            tuple(host.game_process_names),
            bool(getattr(host, 'game_fullscreen_detection', True)),
            bool(getattr(host, 'game_borderless_detection', True)),
        )
        self.timed_out = False
        program, arguments = helper_command(Path(__file__).with_name('game_probe.py'), (
            ','.join(self.intent[0]), '1' if self.intent[1] else '0',
            '1' if self.intent[2] else '0',
        ))
        host.gamemode_process.start(program, arguments)
        self.timeout.start(3000)

    def expired(self):
        self.timed_out = True
        self.host.gamemode_process.kill()

    def error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.finished(-1, QProcess.ExitStatus.NormalExit)

    def finished(self, exit_code, status):
        self.timeout.stop()
        host = self.host
        output = bytes(host.gamemode_process.readAll()).decode('utf-8', 'replace')
        if host.shutdown_started: return
        if not host.game_auto_detection: return
        current_intent = (
            tuple(host.game_process_names),
            bool(getattr(host, 'game_fullscreen_detection', True)),
            bool(getattr(host, 'game_borderless_detection', True)),
        )
        if current_intent != self.intent:
            QTimer.singleShot(0, self.poll)
            return
        try:
            if self.timed_out or exit_code != 0 or status == QProcess.ExitStatus.CrashExit or len(output) > 4096:
                raise ValueError('PROBE_EXIT_SIZE_OR_TIMEOUT')
            raw = json.loads(output)
            if (not isinstance(raw, dict) or raw.get('schema') != 1
                    or type(raw.get('process_active')) is not bool
                    or type(raw.get('gamemode')) is not bool
                    or type(raw.get('fullscreen')) is not bool
                    or type(raw.get('borderless')) is not bool
                    or not isinstance(raw.get('process_reason'), str)):
                raise ValueError('PROBE_SCHEMA')
            host.gamemode_active = raw['gamemode']
            process_active = raw['process_active']
            reason = raw['process_reason'][:128]
            if not process_active and raw['fullscreen']:
                process_active, reason = True, 'Vollbildanwendung'
            elif not process_active and raw['borderless']:
                process_active, reason = True, 'Rahmenloses Vollbildfenster'
            host._update_game_activity(process_active, reason)
        except (ValueError, TypeError) as exc:
            record('game-probe', 'failure', reason='probe-timeout' if self.timed_out else str(exc),
                   exit_code=exit_code, exit_status=status.name, output=output[-1000:])
            host.gamemode_active = False
            host._update_game_activity(False, '')

    def shutdown(self):
        self.timeout.stop()
