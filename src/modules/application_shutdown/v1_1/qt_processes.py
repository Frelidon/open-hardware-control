# SPDX-License-Identifier: GPL-3.0-or-later
"""Reap only remaining window-owned QProcesses after hardware restoration."""
import time
from PySide6.QtCore import QProcess
from .journal import record


def stop_remaining(host):
    if not hasattr(host, 'findChildren'): return
    deadline = time.monotonic() + 2.0
    still_running = []
    for process in host.findChildren(QProcess):
        if not isinstance(process, QProcess): continue
        if process.parent() is getattr(host, 'backend', None): continue
        try:
            if process.state() == QProcess.ProcessState.NotRunning: continue
            pid = int(process.processId())
            record('owned-process-stop', child_pid=pid)
            process.closeWriteChannel()
            process.terminate()
            process.waitForFinished(min(150, max(0, int((deadline - time.monotonic()) * 1000))))
            if process.state() != QProcess.ProcessState.NotRunning:
                process.kill()
                process.waitForFinished(min(150, max(0, int((deadline - time.monotonic()) * 1000))))
            stopped = process.state() == QProcess.ProcessState.NotRunning
            record('owned-process-result', child_pid=pid, stopped=stopped)
            if not stopped:
                still_running.append(pid)
        except RuntimeError:
            pass
    if still_running:
        raise RuntimeError(f"Owned helper processes remained running: {still_running}")
