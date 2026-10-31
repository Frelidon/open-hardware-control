# SPDX-License-Identifier: GPL-3.0-or-later
"""Process liveness does not imply a working LCD; observe confirmed sends."""
import time
from PySide6.QtCore import QObject, QProcess, QTimer
from modules.process_runtime.v1_1.diagnostics import record
from .progress import DisplayProgress


class LCDRuntime(QObject):
    def __init__(self, host):
        super().__init__(host)
        self.host = host
        self.progress = DisplayProgress()
        self.stream_pid = self.command_pid = 0
        self.stream_reason = self.command_reason = ''
        self.command_started = 0.0
        self.command_tokens = []
        self.command_active = False
        self.stop_started = 0.0
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.poll)
        host.command_process.started.connect(self.command_did_start)
        host.command_process.errorOccurred.connect(self.command_error)
        self.timer.start()

    def stream_launch(self):
        self.stream_pid, self.stream_reason = 0, ''
        self.progress.reset(time.monotonic())

    def stream_did_start(self):
        self.stream_pid = int(self.host.stream_process.processId())
        record('lcd-ticker', 'started', pid=self.stream_pid)

    def stream_done(self, exit_code, status, requested, delegated=False):
        if requested or self.host.shutdown_started: return
        if delegated:
            record('lcd-ticker', 'delegated', pid=self.stream_pid,
                   runtime_s=round(time.monotonic() - self.progress.started, 3))
            return
        record('lcd-ticker', 'failure', pid=self.stream_pid, exit_code=exit_code, exit_status=status.name,
               reason=self.stream_reason or 'unexpected-exit', frames=self.progress.frames,
               runtime_s=round(time.monotonic() - self.progress.started, 3),
               output=self.host.stream_output_tail)

    def command_launch(self, args):
        self.command_started = time.monotonic()
        # Only command identifiers, never paths, metric literals or media names.
        self.command_tokens = [str(v) for v in args[1:3] if not str(v).startswith('/')]
        self.command_pid, self.command_reason, self.command_active = 0, '', True

    def command_did_start(self):
        self.command_pid = int(self.host.command_process.processId())

    def command_error(self, error):
        if error == QProcess.ProcessError.FailedToStart and self.command_active:
            self.command_reason = 'failed-to-start: ' + self.host.command_process.errorString()
            self.host._on_command_finished(-1, QProcess.ExitStatus.NormalExit)

    def command_done(self, exit_code, status, output):
        self.command_active = False
        failed = bool(self.command_reason) or exit_code != 0 or status == QProcess.ExitStatus.CrashExit
        record('lcd-command', 'failure' if failed else 'completed', pid=self.command_pid,
               command=self.command_tokens, reason=self.command_reason or ('backend-exit' if failed else ''),
               exit_code=exit_code, exit_status=status.name, output=output,
               runtime_s=round(time.monotonic() - self.command_started, 3))
        return failed

    def poll(self):
        host = self.host
        if host.shutdown_started or host.test_mode.isChecked(): return
        now = time.monotonic()
        if (host.stream_stop_requested and getattr(host, '_fps_restart_pending', False)
                and host.stream_process.state() == QProcess.ProcessState.Running
                and now - self.stop_started >= 3):
            host.stream_process.kill()
        if (self.command_active and not self.command_reason
                and host.command_process.state() == QProcess.ProcessState.Running
                and now - self.command_started >= 45):
            self.command_reason = 'command-timeout: no completion within 45 s'
            host.command_process.kill()
        if (host.stream_should_run and not host.stream_stop_requested and not self.stream_reason
                and host.stream_process.state() == QProcess.ProcessState.Running
                and not host.daemon_restart_in_progress and not self.command_active
                and not host.pending_apply_sequence and self.progress.timeout(now)):
            self.stream_reason = 'send-timeout: no confirmed TRCC TickDisplay progress'
            host.stream_process.kill()

    def shutdown(self):
        self.timer.stop()
