# SPDX-License-Identifier: GPL-3.0-or-later
"""Watch only the existing SDK client, preserving the sole hardware writer."""
import time
import math
from PySide6.QtCore import QObject, QProcess, QTimer
from .diagnostics import record
from .restart_policy import RestartBudget


class SDKSupervisor(QObject):
    def __init__(self, host):
        super().__init__(host)
        self.host = host
        self.budget = RestartBudget()
        self.started = self.progress_at = self.retry_at = 0.0
        self.pid = 0
        self.reason = ''
        self.active_generation = False
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.poll)
        host.openrgb_effect_process.started.connect(self.did_start)
        host.openrgb_effect_process.errorOccurred.connect(self.error)

    def reset(self):
        self.budget.attempts = 0
        self.retry_at = 0.0
        self.timer.start()

    def allowed(self):
        return time.monotonic() >= self.retry_at and self.budget.attempts <= 3

    def launching(self):
        self.started = time.monotonic()
        self.progress_at, self.pid, self.reason = 0.0, 0, ''
        self.active_generation = True
        self.timer.start()

    def did_start(self):
        self.pid = int(self.host.openrgb_effect_process.processId())
        record('rgb-sdk', 'started', pid=self.pid)

    def progress(self):
        self.progress_at = time.monotonic()
        self.budget.progress(self.started, self.progress_at)

    def fail(self, reason):
        if self.reason or not self.active_generation: return
        self.reason = reason
        self.host.openrgb_effect_process.kill()

    def accept_frame(self, message):
        """Validate before releasing the in-flight slot or renewing progress."""
        host = self.host
        if not host.openrgb_worker_frame_inflight: return False
        results = message.get('devices')
        duration = message.get('duration_ms', 0)
        if (type(message.get('id')) is not int or message['id'] != host.openrgb_worker_frame_sequence
                or not isinstance(results, list) or not 1 <= len(results) <= 256
                or type(duration) not in (float, int) or not math.isfinite(duration) or duration < 0):
            self.fail('protocol-frame: invalid ID, result catalog or duration')
            return False
        keys = set()
        for result in results:
            if not isinstance(result, dict):
                self.fail('protocol-device: invalid result object'); return False
            key, duration = result.get('key'), result.get('duration_ms', 0)
            if (not isinstance(key, str) or not 1 <= len(key) <= 128 or key in keys
                    or type(result.get('ok')) is not bool or type(duration) not in (int, float)
                    or not math.isfinite(duration) or duration < 0):
                self.fail('protocol-device: invalid key, success flag or duration'); return False
            keys.add(key)
        return True

    def poll(self):
        host = self.host
        if not host.openrgb_effect_active or host.rgb_manual_write_active:
            return
        process = host.openrgb_effect_process
        if process.state() != QProcess.ProcessState.Running or self.reason:
            return
        now = time.monotonic()
        # A started process is not readiness or a completed SDK transaction.
        if not host.openrgb_worker_ready and now - self.started >= 5:
            self.reason = 'ready-timeout: no SDK ready acknowledgement within 5 s'
        elif host.openrgb_worker_frame_inflight and now - host.openrgb_worker_frame_started >= 5:
            self.reason = 'frame-timeout: no SDK frame acknowledgement within 5 s'
        if self.reason:
            process.kill()  # Concrete owned client only; never the OpenRGB engine.

    def error(self, error):
        if error == QProcess.ProcessError.FailedToStart and self.active_generation:
            self.reason = 'failed-to-start: ' + self.host.openrgb_effect_process.errorString()
            self.host.on_openrgb_worker_finished(-1, QProcess.ExitStatus.NormalExit)

    def finished(self, exit_code, status):
        if not self.active_generation: return
        self.active_generation = False
        host = self.host
        if not host.openrgb_effect_active or host.rgb_manual_write_active:
            return
        delay = self.budget.failure()
        record('rgb-sdk', 'failure', pid=self.pid, exit_code=exit_code, exit_status=status.name,
               runtime_s=round(time.monotonic() - self.started, 3), reason=self.reason or 'unexpected-exit',
               request_id=host.openrgb_worker_frame_sequence, retry_ms=delay,
               stderr=host.openrgb_worker_stderr_buffer)
        if delay is None:
            self.retry_at = float('inf')
            record('rgb-sdk', 'exhausted', reason='three automatic restarts exhausted')
            host.stop_openrgb_effect('Animation angehalten · SDK-Worker dreimal beendet')
        else:
            self.retry_at = time.monotonic() + delay / 1000
            host.openrgb_worker_frame_pending = True

    def stop(self):
        self.active_generation = False
        self.timer.stop()
