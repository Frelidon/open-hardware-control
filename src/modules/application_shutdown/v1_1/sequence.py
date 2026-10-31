# SPDX-License-Identifier: GPL-3.0-or-later
"""Run every existing exit phase despite an individual cleanup exception."""
import time
from PySide6.QtCore import QTimer
from privacy_logging import append_startup_event, redact_private_text
from .journal import record


class ShutdownSequence:
    def __init__(self, logger):
        self.logger = logger
        self.failures = []

    @property
    def success(self):
        return not self.failures

    def _log(self, message):
        try:
            self.logger(message)
        except Exception:  # A destroyed Qt log widget must not prevent exit.
            append_startup_event(message)

    def _execute(self, phase, action):
        started = time.monotonic()
        record("phase-start", phase=phase)
        self._log(f"SYSTEMENDE: phase={phase} state=start")
        try:
            result = action()
        except Exception as exc:
            record("phase-failed", phase=phase, error=type(exc).__name__)
            self.failures.append(phase)
            detail = redact_private_text(str(exc))[:500]
            self._log(f"SYSTEMENDE: phase={phase} state=failed type={type(exc).__name__} detail={detail}")
            return False, None
        record("phase-done", phase=phase, elapsed=round(time.monotonic() - started, 3))
        self._log(f"SYSTEMENDE: phase={phase} state=done elapsed={time.monotonic() - started:.3f}s")
        return True, result

    def run(self, phase, action):
        return self._execute(phase, action)[0]

    def value(self, phase, action):
        return self._execute(phase, action)[1]


def stop_owned_timers(host):
    """Quiesce only this window's Qt children, including inventory/retry timers."""
    for timer in host.findChildren(QTimer):
        try:
            timer.stop()
        except RuntimeError:
            pass
    # A process-finished callback must not restart the managed RGB engine.
    host.rgb_engine_restart_pending = False
    host.rgb_profile_autostart_pending = False
    host.openrgb_write_enable_pending = False
    # Quiesce timers and restart intent even if worker cancellation fails. The
    # existing phase runner records that exception and continues hardware exit.
    bundle = getattr(host, "profile_bundle_controller", None)
    if bundle is not None:
        bundle.cancel()
