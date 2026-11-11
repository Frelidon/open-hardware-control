#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Frelidon contributors
"""Privacy filtering and bounded application lifecycle/crash logging."""

from __future__ import annotations

import faulthandler
import os
import platform
import re
import sys
import time
import threading
import traceback
from pathlib import Path

from PySide6.QtCore import qVersion

from app_constants import APP_DISPLAY_VERSION


ERROR_LOG_MAX_BYTES = 2 * 1024 * 1024
ERROR_LOG_RETAIN_BYTES = 1024 * 1024
_native_fault_stream = None
_error_listener = None
_error_log_lock = threading.RLock()


def redact_private_text(text: str) -> str:
    """Remove common personal/network identifiers before logs can be shared."""
    if not text:
        return text
    home = str(Path.home())
    if home and home != "/":
        text = text.replace(home, "~")
    text = re.sub(r"/home/[^/\s]+", "/home/[USER]", text)
    text = re.sub(r"(?im)^(\s*(?:serial(?: number)?|id_serial(?:_short)?)[=:]\s*).*$", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(machine-id|boot-id|product_uuid|system_uuid)(\s*[:=]\s*)[0-9a-f-]+", r"\1\2[REDACTED]", text)
    text = re.sub(r"(?im)^(\s*(?:hostname|static hostname|pretty hostname)(?:\s*[:=]\s*)).*$", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b", "[MAC]", text)

    def redact_ipv4(match: re.Match[str]) -> str:
        value = match.group(0)
        # Four-part application versions (for example a four-part x.y.z.hotfix value) can look like
        # IPv4 addresses. Keep them when the surrounding log text clearly
        # identifies a software version/build, while real network addresses
        # remain redacted.
        before = match.string[max(0, match.start() - 32):match.start()].casefold()
        after = match.string[match.end():match.end() + 20].casefold()
        if re.search(r"(?:version|v|release|build|open hardware control|ohc)\s*$", before) or re.match(r"\s*(?:intern|stable|alpha|beta|rc)\b", after):
            return value
        # Localhost and IANA documentation ranges are useful in technical logs
        # and cannot identify the user's network.
        octets = tuple(int(part) for part in value.split("."))
        if octets[0] == 127 or octets[:3] in {(192, 0, 2), (198, 51, 100), (203, 0, 113)}:
            return value
        return "[IP]"

    text = re.sub(r"(?<![0-9])(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![0-9])", redact_ipv4, text)
    # Require at least three colons so USB IDs such as 1e71:300e remain intact.
    text = re.sub(r"(?i)(?<![0-9a-f:])(?:[0-9a-f]{0,4}:){3,7}[0-9a-f]{0,4}(?![0-9a-f:])", lambda m: m.group(0) if m.group(0) in {"::1"} else "[IPv6]", text)
    text = re.sub(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[EMAIL]", text)
    return text


def application_state_directory() -> Path:
    """Return the private XDG state directory used for startup diagnostics."""
    configured = os.environ.get("XDG_STATE_HOME", "").strip()
    candidate = Path(configured).expanduser() if configured else Path.home() / ".local" / "state"
    if not candidate.is_absolute():
        candidate = Path.home() / ".local" / "state"
    return candidate / "open-hardware-control"


def append_startup_event(message: str) -> Path | None:
    """Append a bounded, privacy-filtered application lifecycle entry."""
    try:
        directory = application_state_directory()
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(directory, 0o700)
        path = directory / "startup.log"
        if path.is_file() and path.stat().st_size > 256 * 1024:
            tail = path.read_text(encoding="utf-8", errors="replace")[-128 * 1024:]
            path.write_text(tail, encoding="utf-8")
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{stamp}] {redact_private_text(message).rstrip()}\n")
        os.chmod(path, 0o600)
        return path
    except OSError:
        return None


def set_error_listener(listener):
    """Register a bounded thread-safe sink; the listener must never access Qt UI."""
    global _error_listener
    previous, _error_listener = _error_listener, listener
    return previous


def append_error_event(message: str, *, notify: bool = True) -> Path | None:
    """Append one durable, bounded and privacy-filtered runtime failure."""
    if notify and _error_listener is not None:
        try:
            _error_listener(redact_private_text(message))
        except Exception:  # Error reporting must not replace the original failure.
            pass
    with _error_log_lock:
        return _append_error_event_file(message)


def _append_error_event_file(message: str) -> Path | None:
    """Serialize file rotation/writes from Python and Qt worker threads."""
    try:
        directory = application_state_directory()
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(directory, 0o700)
        path = directory / "errors.log"
        if path.is_file() and path.stat().st_size > ERROR_LOG_MAX_BYTES:
            tail = path.read_text(encoding="utf-8", errors="replace")[
                -ERROR_LOG_RETAIN_BYTES:
            ]
            first_newline = tail.find("\n")
            if first_newline >= 0:
                tail = tail[first_newline + 1:]
            path.write_text(tail, encoding="utf-8")
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{stamp}] {redact_private_text(message).rstrip()}\n")
        os.chmod(path, 0o600)
        return path
    except OSError:
        return None


def write_application_crash_log(
    exception_type: type[BaseException],
    exception: BaseException,
    trace,
) -> Path | None:
    """Persist the latest uncaught Python exception without personal paths."""
    try:
        directory = application_state_directory()
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(directory, 0o700)
        path = directory / "last-crash.log"
        formatted = "".join(traceback.format_exception(exception_type, exception, trace))
        payload = (
            f"Open Hardware Control {APP_DISPLAY_VERSION}\n"
            f"Time: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n"
            f"Python: {platform.python_version()}\n"
            f"Platform: {platform.platform()}\n\n"
            f"{formatted}"
        )
        path.write_text(redact_private_text(payload), encoding="utf-8")
        os.chmod(path, 0o600)
        event = f"ABSTURZ: {exception_type.__name__}: {exception}"
        append_startup_event(event)
        append_error_event(event)
        return path
    except OSError:
        return None


def _install_native_fault_logging() -> Path | None:
    """Enable fatal-signal tracebacks in a private file kept across a crash."""
    global _native_fault_stream
    try:
        directory = application_state_directory()
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(directory, 0o700)
        current = directory / "native-crash-current.log"
        previous = directory / "last-native-crash.log"
        if current.exists() and not current.is_symlink():
            descriptor = os.open(current, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(descriptor, "r", encoding="utf-8", errors="replace") as stream:
                prior_payload = stream.read(2 * 1024 * 1024)
            if prior_payload.strip() and not previous.is_symlink():
                descriptor = os.open(
                    previous,
                    os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW,
                    0o600,
                )
                with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                    os.fchmod(stream.fileno(), 0o600)
                    stream.write(redact_private_text(prior_payload))
        if current.is_symlink():
            return None
        descriptor = os.open(
            current,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW,
            0o600,
        )
        _native_fault_stream = os.fdopen(descriptor, "w", encoding="utf-8")
        os.fchmod(_native_fault_stream.fileno(), 0o600)
        faulthandler.enable(file=_native_fault_stream, all_threads=True)
        return current
    except (OSError, RuntimeError, ValueError):
        return None


def install_application_exception_logging() -> None:
    """Install the uncaught-exception hook before the Qt window is created."""
    original_hook = sys.excepthook

    def log_uncaught(exception_type, exception, trace) -> None:  # noqa: ANN001
        path = write_application_crash_log(exception_type, exception, trace)
        if path is not None:
            print(f"Automatisches Absturzprotokoll: {path}", file=sys.stderr)
        original_hook(exception_type, exception, trace)

    sys.excepthook = log_uncaught
    _install_native_fault_logging()
    append_startup_event(
        f"START: Version {APP_DISPLAY_VERSION} · Python {platform.python_version()} · Qt {qVersion()}"
    )
