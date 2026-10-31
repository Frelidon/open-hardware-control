# SPDX-License-Identifier: GPL-3.0-or-later
"""Private bounded exit journal, independent of Qt and the disappearing log UI."""
import atexit
import faulthandler
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from privacy_logging import application_state_directory, redact_private_text

_armed = False
_trace = None
_lifetime_observer_started = False


def record(event, **fields):
    try:
        directory = application_state_directory()
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        path = directory / "shutdown.jsonl"
        if path.is_symlink(): return
        if path.exists() and path.stat().st_size > 256 * 1024:
            previous = path.read_bytes()[-128 * 1024:]
            path.write_bytes(previous.partition(b"\n")[2])
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), 0o600)
            payload = dict(event=event, pid=os.getpid(), time=time.time(), **fields)
            stream.write(redact_private_text(json.dumps(payload, ensure_ascii=True)) + "\n")
            stream.flush()
    except (OSError, ValueError):
        pass  # Diagnostics can never become a reason to skip restoration.


def begin(reason):
    global _armed, _trace
    record("exit-request", reason=reason)
    if os.environ.get("OHC_DISABLE_HARDWARE_IO") == "1": return
    if _armed: return
    _armed = True
    atexit.register(lambda: record("python-atexit"))
    try:
        directory = application_state_directory()
        path = directory / "shutdown-stacks.log"
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
        _trace = os.fdopen(descriptor, "w")
        os.fchmod(_trace.fileno(), 0o600)
        # A native timer still reports a blocked Python/Qt thread. No automatic kill.
        faulthandler.dump_traceback_later(15, repeat=False, file=_trace)
        watcher = Path(__file__).with_name("watcher.py")
        subprocess.Popen([sys.executable, str(watcher), str(os.getpid()), str(directory)],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, close_fds=True)
    except (OSError, ValueError, RuntimeError) as exc:
        record("diagnostic-unavailable", error=type(exc).__name__)


def observe_lifetime() -> None:
    """Keep a small independent observer alive through the entire app session."""
    global _lifetime_observer_started
    from .watcher import identity
    current = identity(os.getpid())
    record("app-start", starttime=current[0] if current is not None else "")
    if os.environ.get("OHC_DISABLE_HARDWARE_IO") == "1" or _lifetime_observer_started:
        return
    try:
        directory = application_state_directory()
        watcher = Path(__file__).with_name("watcher.py")
        subprocess.Popen(
            [sys.executable, str(watcher), "--lifetime", str(os.getpid()), str(directory)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, close_fds=True, start_new_session=True,
        )
        _lifetime_observer_started = True
    except (OSError, ValueError) as exc:
        record("diagnostic-unavailable", error=type(exc).__name__)
