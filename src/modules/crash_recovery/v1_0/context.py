# SPDX-License-Identifier: GPL-3.0-or-later
"""Private, bounded log context that survives a native process crash."""

from __future__ import annotations

import json
import os
from pathlib import Path
import time


CRASH_CONTEXT_SECONDS = 5 * 60
CRASH_CONTEXT_MAX_BYTES = 2 * 1024 * 1024
CRASH_CONTEXT_RETAIN_BYTES = 1024 * 1024


def _open_private_append(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW,
        0o600,
    )
    stream = os.fdopen(descriptor, "a", encoding="utf-8")
    os.fchmod(stream.fileno(), 0o600)
    return stream


def _read_tail(path: Path, limit: int = CRASH_CONTEXT_MAX_BYTES) -> bytes:
    if path.is_symlink():
        return b""
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as stream:
        size = os.fstat(stream.fileno()).st_size
        if size > limit:
            stream.seek(-limit, os.SEEK_END)
            stream.readline()
        return stream.read(limit)


def _truncate_private(path: Path) -> None:
    if path.is_symlink():
        return
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW,
        0o600,
    )
    with os.fdopen(descriptor, "wb") as stream:
        os.fchmod(stream.fileno(), 0o600)


def append_crash_context(path: Path, line: str, *, observed_at: float | None = None) -> bool:
    """Append one already-redacted line to the active crash ring file."""
    if not line or path.is_symlink():
        return False
    try:
        if path.is_file() and path.stat().st_size > CRASH_CONTEXT_MAX_BYTES:
            tail = _read_tail(path, CRASH_CONTEXT_RETAIN_BYTES)
            first_newline = tail.find(b"\n")
            if first_newline >= 0:
                tail = tail[first_newline + 1:]
            _truncate_private(path)
            with _open_private_append(path) as stream:
                stream.buffer.write(tail)
        payload = {"time": time.time() if observed_at is None else observed_at, "line": line.rstrip()}
        with _open_private_append(path) as stream:
            stream.write(json.dumps(payload, ensure_ascii=True) + "\n")
            stream.flush()
        return True
    except (OSError, TypeError, ValueError):
        return False


def recover_crash_context(
    current_path: Path,
    snapshot_path: Path,
    *,
    unexpected_exit: bool,
    observed_at: float | None = None,
) -> list[str]:
    """Return and snapshot only the final five minutes of an abnormal session."""
    now = time.time() if observed_at is None else observed_at
    recovered: list[str] = []
    try:
        raw = _read_tail(current_path) if current_path.exists() else b""
        if unexpected_exit:
            cutoff = now - CRASH_CONTEXT_SECONDS
            for encoded in raw.decode("utf-8", errors="replace").splitlines():
                try:
                    record = json.loads(encoded)
                    stamp = float(record.get("time"))
                    line = record.get("line")
                except (AttributeError, TypeError, ValueError, json.JSONDecodeError):
                    continue
                if cutoff <= stamp <= now + 5 and isinstance(line, str) and line:
                    recovered.append(line)
            if not snapshot_path.is_symlink():
                _truncate_private(snapshot_path)
                with _open_private_append(snapshot_path) as stream:
                    stream.write("Open Hardware Control · letzte fünf Minuten vor dem Absturz\n")
                    if recovered:
                        stream.write("\n".join(recovered) + "\n")
        _truncate_private(current_path)
    except OSError:
        return []
    return recovered
