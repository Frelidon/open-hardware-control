# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded read-only process supervision, never new hardware ownership."""
import json
import math
import os
from pathlib import Path
import sys
import time
from PySide6.QtCore import QObject, QProcess, QTimer
from .diagnostics import record


class ProcessRuntime(QObject):
    def __init__(self, host):
        super().__init__(host)
        self.host = host
        self.process = QProcess(self)
        self.process.setObjectName('ohcSensorWorker')
        self.process.readyReadStandardOutput.connect(self.receive)
        self.process.readyReadStandardError.connect(self.receive_error)
        self.process.finished.connect(self.finished)
        self.process.errorOccurred.connect(self.error)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.poll)
        self.restart = QTimer(self)
        self.restart.setSingleShot(True)
        self.restart.timeout.connect(self.start)
        self.closed, self.pending, self.snapshot = False, False, {}
        self.received = self.requested = 0.0
        self.buffer = b''
        self.failures = 0
        self.started = 0.0
        self.stderr = b''
        self.failure_reason = ''
        self.pid = 0
        self.process.started.connect(self.did_start)

    def did_start(self):
        self.pid = int(self.process.processId())
        record('sensors', 'started', pid=self.pid)

    def receive_error(self):
        self.stderr = (self.stderr + bytes(self.process.readAllStandardError()))[-8192:]

    def fail(self, reason):
        self.snapshot = {}
        if self.failure_reason: return
        self.failure_reason = reason
        self.process.kill()

    def start(self):
        if self.closed or self.process.state() != QProcess.ProcessState.NotRunning: return
        self.buffer, self.pending, self.snapshot = b'', False, {}
        self.stderr, self.failure_reason, self.pid = b'', '', 0
        self.started = time.monotonic()
        self.process.setProgram(sys.executable)
        self.process.setArguments([str(Path(__file__).with_name('sensor_worker.py'))])
        self.process.start()
        self.timer.start()

    def poll(self):
        if self.closed: return
        now = time.monotonic()
        if self.pending:
            if now - self.requested >= 3.0:
                self.fail('sample-timeout: no reply within 3 s; stale sensors unavailable')
            return
        if self.process.state() == QProcess.ProcessState.Running:
            self.pending = self.process.write(b'{"op":"sample"}\n') >= 0
            self.requested = now

    def receive(self):
        self.buffer += bytes(self.process.readAllStandardOutput())
        if len(self.buffer) > 64 * 1024:
            self.fail('protocol-size: reply exceeded 64 KiB'); return
        while b'\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\n', 1)
            try:
                raw = json.loads(line)
                if not self.pending or raw.get('schema') != 1: raise ValueError('SENSOR_SCHEMA')
                for key in ('cpu', 'gpu'):
                    value = raw.get(key)
                    if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or not 0 < value < 150):
                        raise ValueError('SENSOR_VALUE')
                if not isinstance(raw.get('sensors', []), list) or len(raw.get('sensors', [])) > 256:
                    raise ValueError('SENSOR_CATALOG')
                sampled = raw.get('sampled_at')
                if type(sampled) not in (int, float) or not math.isfinite(sampled) or not self.requested - .05 <= sampled <= time.monotonic() + .05:
                    raise ValueError('SENSOR_TIME')
                if not isinstance(raw.get('metrics'), dict) or len(raw['metrics']) > 128: raise ValueError('METRICS')
                if any(not isinstance(k, str) or len(k) > 64 or (v is not None and
                       (type(v) not in (int, float) or not math.isfinite(v))) for k, v in raw['metrics'].items()):
                    raise ValueError('METRIC_VALUE')
                self.snapshot, self.received, self.pending = raw, sampled, False
                if self.received - self.started >= 30: self.failures = 0
            except (ValueError, TypeError, AttributeError) as exc:
                self.fail(f'protocol-invalid: {type(exc).__name__}: {exc}')
                self.buffer = b''
                return

    def current(self):
        return self.snapshot if not self.closed and time.monotonic() - self.received <= 2.5 else {}

    def temperature(self, key):
        raw = self.current()
        return raw.get(key), str(raw.get(key + '_label', '—'))[:128]

    def metrics(self):
        return dict(self.current().get('metrics', {}))

    def sensors(self):
        from modules.temperature_history.v1_2.sensors import TemperatureSensorReading
        result = []
        for raw in self.current().get('sensors', [])[:256]:
            try:
                sensor = TemperatureSensorReading(**raw)
                if type(sensor.value_c) in (int, float) and math.isfinite(sensor.value_c) and 0 < sensor.value_c <= 150:
                    result.append(sensor)
            except (TypeError, ValueError): pass
        return tuple(result)

    def error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.failure_reason = 'failed-to-start: ' + self.process.errorString()
            self.finished(-1, QProcess.ExitStatus.NormalExit)

    def finished(self, exit_code=-1, status=QProcess.ExitStatus.NormalExit):
        self.receive_error()
        self.pending, self.snapshot = False, {}
        self.timer.stop()
        if self.closed or self.restart.isActive(): return
        self.failures += 1
        delay = 1000 * 2 ** (self.failures - 1) if self.failures <= 3 else None
        record('sensors', 'failure', pid=self.pid, exit_code=exit_code, exit_status=status.name,
               reason=self.failure_reason or 'unexpected-exit', request='sample' if self.requested else 'startup',
               runtime_s=round(time.monotonic() - self.started, 3), retry_ms=delay,
               stderr=self.stderr.decode('utf-8', 'replace'))
        if delay is not None: self.restart.start(delay)
        else: record('sensors', 'exhausted', reason='three automatic restarts exhausted')

    def shutdown(self):
        self.closed = True
        self.timer.stop(); self.restart.stop(); self.snapshot = {}
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.write(b'{"op":"stop"}\n'); self.process.closeWriteChannel()
            if not self.process.waitForFinished(300):
                self.process.kill(); self.process.waitForFinished(300)

    def retry(self):
        """Explicit read-only recovery never revives an exiting application."""
        if self.closed or self.process.state() != QProcess.ProcessState.NotRunning: return
        self.restart.stop()
        self.failures = 0
        record('sensors', 'manual-retry', reason='explicit read-only sensor restart')
        self.start()


def install(host):
    runtime = ProcessRuntime(host)
    if os.environ.get('OHC_DISABLE_HARDWARE_IO') != '1': QTimer.singleShot(0, runtime.start)
    return runtime
