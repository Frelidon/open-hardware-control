# SPDX-License-Identifier: GPL-3.0-or-later
"""One cancellable local encoder, started only by an explicit apply action."""
from pathlib import Path
import shutil
import uuid
from PySide6.QtCore import QObject, QProcess, QTimer, Signal
from .scaling import encoder_arguments, valid_output, zoom_plan


class ZoomPreparation(QObject):
    ready = Signal(object)
    failed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._drain)
        self.process.finished.connect(self._finished)
        self.process.errorOccurred.connect(self._error)
        self.deadline = QTimer(self); self.deadline.setSingleShot(True)
        self.deadline.setInterval(180_000); self.deadline.timeout.connect(self._timeout)
        self.plan = None; self.temporary = None; self.cancelled = False
        self.restarting = None
        self.output_tail = ''

    def start(self, source, cache, zoom):
        self.cancel()
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.restarting = (source, cache, zoom)
            return
        self._start(source, cache, zoom)

    def _start(self, source, cache, zoom):
        self.cancelled = False
        self.output_tail = ''
        try:
            plan = zoom_plan(source, cache, zoom)
            if valid_output(plan):
                self.plan = plan
                QTimer.singleShot(0, lambda: self.ready.emit(plan) if self.plan is plan and not self.cancelled else None)
                return
            executable = shutil.which('ffmpeg')
            if not executable: raise ValueError('ffmpeg unavailable')
            plan.target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            if plan.target.parent.is_symlink(): raise ValueError('symlink cache')
            self.plan = plan
            self.temporary = plan.target.parent / f".paired-zoom-{uuid.uuid4().hex}.mp4"
            self.process.setProgram(executable)
            self.process.setArguments(encoder_arguments(plan, self.temporary))
            self.process.start(); self.deadline.start()
        except (OSError, ValueError, StopIteration) as error:
            self.plan = None; self._fail(f'{type(error).__name__}: {error}')

    def _drain(self):
        # Keep only a bounded failure tail; never turn encoder output into a
        # per-frame GUI feed or an unbounded in-memory log.
        chunk = bytes(self.process.readAllStandardOutput()).decode('utf-8', 'replace')
        self.output_tail = (self.output_tail + chunk)[-2048:]

    def _fail(self, detail):
        from privacy_logging import append_error_event
        append_error_event(f'DESIGN-HUB-ZOOM: {str(detail)[-2048:]}')
        self.failed.emit()

    def _finished(self, code, status):
        self.deadline.stop(); self._drain()
        plan, temporary = self.plan, self.temporary
        self.plan = self.temporary = None
        success = False
        if not self.cancelled and code == 0 and status == QProcess.ExitStatus.NormalExit and plan and temporary:
            try:
                from dataclasses import replace
                if valid_output(replace(plan, target=temporary)):
                    temporary.chmod(0o600)
                    temporary.replace(plan.target)
                    success = True
            except OSError as error:
                self.output_tail = f'{type(error).__name__}: {error}'
        if temporary:
            try: temporary.unlink(missing_ok=True)
            except OSError: pass
        if success: self.ready.emit(plan)
        elif not self.cancelled: self._fail(self.output_tail or f'encoder exit={code}; invalid output')
        restart, self.restarting = self.restarting, None
        if restart: self._start(*restart)

    def _error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.deadline.stop()
            if not self.cancelled: self._fail('encoder failed to start')
            self.plan = None

    def _timeout(self):
        self.cancel()
        self._fail('encoder deadline exceeded (180 seconds)')

    def cancel(self):
        self.cancelled = True; self.restarting = None; self.deadline.stop()
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
        elif self.temporary:
            try: Path(self.temporary).unlink(missing_ok=True)
            except OSError: pass
            self.temporary = self.plan = None

    def shutdown(self):
        self.cancel()
