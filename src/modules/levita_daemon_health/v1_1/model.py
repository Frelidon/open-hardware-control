#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Health and strictly validated recovery checks for OHC's TRCC daemon."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import signal
from typing import Iterable


DAEMON_HEALTH_INTERVAL_MS = 60_000
# Animated playback is a visible surface: waiting a full minute before the
# first probe leaves a black panel for far too long.  The query is read-only
# IPC and cheap; a second confirmation still prevents one slow reply from
# triggering recovery.
PLAYBACK_HEALTH_INTERVAL_MS = 15_000
DAEMON_RSS_LIMIT_BYTES = 1024 * 1024 * 1024
DAEMON_RECOVERY_COOLDOWN_SECONDS = 5 * 60
# Confirmed playback loss already requires two probes and has its own bounded
# retry budget.  It must not inherit the longer generic daemon cooldown: a
# replacement VideoLoop can otherwise fail again while the LCD stays black.
PLAYBACK_RECOVERY_COOLDOWN_SECONDS = 30


@dataclass(frozen=True, slots=True)
class DaemonMemorySample:
    pid: int
    rss_bytes: int


def is_trcc_daemon_command(arguments: Iterable[str]) -> bool:
    """Match only the explicit ``trcc daemon`` command shape."""

    values = tuple(str(value) for value in arguments)
    if len(values) >= 2 and Path(values[-2]).name == "trcc" and values[-1] == "daemon":
        return True
    return len(values) >= 3 and values[-3:-1] == ("-m", "trcc") and values[-1] == "daemon"


def is_owned_trcc_daemon_pid(pid: int, *, proc_root: Path = Path("/proc"),
                             uid: int | None = None) -> bool | None:
    """Check the originally recorded PID, independent of any other daemon's RSS."""
    wanted_uid = os.getuid() if uid is None else int(uid)
    process_dir = proc_root / str(int(pid))
    try:
        arguments = tuple(part.decode("utf-8", errors="replace")
                          for part in (process_dir / "cmdline").read_bytes().split(b"\0") if part)
        status = (process_dir / "status").read_text(encoding="utf-8", errors="replace")
        uid_line = next(line for line in status.splitlines() if line.startswith("Uid:"))
        owner_uid = int(uid_line.split()[1])
    except FileNotFoundError:
        return None if process_dir.exists() else False
    except (OSError, StopIteration, ValueError, IndexError):
        return None
    return owner_uid == wanted_uid and is_trcc_daemon_command(arguments)


def find_trcc_daemon_memory(
    *,
    proc_root: Path = Path("/proc"),
    uid: int | None = None,
) -> DaemonMemorySample | None:
    """Return the largest matching daemon owned by this user, if present."""

    wanted_uid = os.getuid() if uid is None else int(uid)
    matches: list[DaemonMemorySample] = []
    try:
        process_dirs = tuple(proc_root.iterdir())
    except OSError:
        return None
    for process_dir in process_dirs:
        if not process_dir.name.isdigit():
            continue
        try:
            arguments = tuple(
                part.decode("utf-8", errors="replace")
                for part in (process_dir / "cmdline").read_bytes().split(b"\0")
                if part
            )
            if not is_trcc_daemon_command(arguments):
                continue
            status = (process_dir / "status").read_text(encoding="utf-8", errors="replace")
            status_fields = {
                line.split(":", 1)[0]: line.split(":", 1)[1].strip()
                for line in status.splitlines()
                if ":" in line
            }
            owner_uid = int(status_fields.get("Uid", "-1").split()[0])
            if owner_uid != wanted_uid:
                continue
            rss_kib = int(status_fields.get("VmRSS", "0 kB").split()[0])
            matches.append(DaemonMemorySample(int(process_dir.name), rss_kib * 1024))
        except (OSError, ValueError, IndexError):
            continue
    return max(matches, key=lambda sample: sample.rss_bytes, default=None)


def replacement_owned_trcc_pid(
    previous_pid: int | None,
    observed: DaemonMemorySample | None,
    *,
    previous_pid_exists=is_owned_trcc_daemon_pid,
) -> int | None:
    """Adopt a replacement only inside an explicitly tracked OHC restart.

    The caller owns the restart intent.  This helper merely verifies that the
    old exact daemon identity has disappeared and that discovery now reports a
    different same-user ``trcc daemon`` process.
    """

    if previous_pid is None or observed is None or observed.pid == int(previous_pid):
        return None
    if previous_pid_exists(int(previous_pid)) is not False:
        return None
    return observed.pid


def daemon_memory_exceeded(
    sample: DaemonMemorySample | None,
    *,
    limit_bytes: int = DAEMON_RSS_LIMIT_BYTES,
) -> bool:
    return sample is not None and sample.rss_bytes >= max(1, int(limit_bytes))


def signal_trcc_daemon(
    pid: int,
    requested_signal: int = signal.SIGTERM,
    *,
    proc_root: Path = Path("/proc"),
    uid: int | None = None,
    kill_fn=os.kill,
) -> bool:
    """Signal one PID only after revalidating the exact user-owned daemon.

    Re-reading both command line and owner immediately before signalling keeps
    the recovery path from touching an unrelated process after PID reuse.
    """

    wanted_uid = os.getuid() if uid is None else int(uid)
    process_dir = proc_root / str(int(pid))
    try:
        arguments = tuple(
            part.decode("utf-8", errors="replace")
            for part in (process_dir / "cmdline").read_bytes().split(b"\0")
            if part
        )
        status = (process_dir / "status").read_text(encoding="utf-8", errors="replace")
        uid_line = next(line for line in status.splitlines() if line.startswith("Uid:"))
        owner_uid = int(uid_line.split()[1])
    except (OSError, StopIteration, ValueError, IndexError):
        return False
    if owner_uid != wanted_uid or not is_trcc_daemon_command(arguments):
        return False
    try:
        kill_fn(int(pid), int(requested_signal))
    except (OSError, ValueError):
        return False
    return True


def is_probable_daemon_failure(output: str) -> bool:
    """Recognize stream failures for which a controlled daemon reset helps."""

    lowered = str(output).casefold()
    return any(marker in lowered for marker in (
        "peer closed without sending data",
        "connection refused",
        "broken pipe",
        "daemon is not running",
        "interface is in use by another process",
    ))


def is_usb_owner_conflict(output: str) -> bool:
    """Recognize TRCC's explicit USB-busy report, not a permissions hint.

    This proves a claimed interface, not a wedged daemon. The Ubuntu
    orchestrator handles it separately without terminating another owner;
    the existing daemon classifier remains unchanged for other runtimes.
    """

    return "interface is in use by another process" in str(output).casefold()


def backend_failure_detail(output: str) -> str:
    """Keep the actual failure instead of TRCC's trailing setup suggestion."""

    lines = [line.strip() for line in str(output).splitlines() if line.strip()]
    primary = [line for line in lines if not line.casefold().startswith("hint:")]
    conflict = next((line for line in reversed(primary) if is_usb_owner_conflict(line)), None)
    return conflict or (primary[-1] if primary else "")
