#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded TRCC-daemon release when the OHC parent disappears."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Callable

# The helper is executed by absolute file path after the main OHC process has
# gone away. In that mode Python adds only this v1_0 directory to sys.path,
# not the installed application root which owns the ``modules`` package.
_APPLICATION_ROOT = Path(__file__).resolve().parents[3]
if str(_APPLICATION_ROOT) not in sys.path:
    sys.path.insert(0, str(_APPLICATION_ROOT))

from modules.levita_daemon_health.v1_1 import DaemonMemorySample, find_trcc_daemon_memory, is_owned_trcc_daemon_pid


THERMALRIGHT_DEVICE_KEY = "87ad:70db"
_CLEAN_EXIT_TOKEN = "clean"


def _parent_identity_matches(
    pid: int,
    starttime: str,
    *,
    proc_root: Path = Path("/proc"),
) -> bool | None:
    """Confirm the exact live parent incarnation without trusting pipe EOF.

    False requires an absent, replaced, or zombie parent. An unreadable but
    still present entry remains unknown, so it cannot blank a live display.
    """

    process_dir = proc_root / str(int(pid))
    try:
        fields = (process_dir / "stat").read_text(
            encoding="utf-8", errors="replace",
        ).rsplit(")", 1)[1].split()
        current_starttime, state = fields[19], fields[0]
    except FileNotFoundError:
        return None if process_dir.exists() else False
    except (OSError, IndexError, ValueError):
        return None
    return current_starttime == str(starttime) and state != "Z"


def _current_process_starttime() -> str | None:
    try:
        fields = (Path("/proc") / str(os.getpid()) / "stat").read_text(
            encoding="utf-8", errors="replace",
        ).rsplit(")", 1)[1].split()
        return fields[19]
    except (OSError, IndexError, ValueError):
        return None


@dataclass(frozen=True, slots=True)
class FirmwareRestoreResult:
    ok: bool
    message: str = ""


def _trusted_trcc_executable(value: str) -> str:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute() or candidate.name != "trcc":
        raise ValueError("Ungültiger TRCC-Programmpfad")
    resolved = candidate.resolve()
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise ValueError("TRCC-Programm ist nicht ausführbar")
    return str(resolved)


def restore_firmware_logo(
    executable: str,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    finder: Callable[[], DaemonMemorySample | None] = find_trcc_daemon_memory,
    timeout: float = 2.0,
) -> FirmwareRestoreResult:
    """Release the daemon-owned Levita so its built-in logo can return."""
    try:
        trusted = _trusted_trcc_executable(executable)
        # Proxy commands auto-spawn TRCC. Closing OHC must never start a new
        # daemon solely to disconnect an already released display.
        if finder() is None:
            return FirmwareRestoreResult(True, "TRCC daemon already stopped")
        environment = os.environ.copy()
        environment["TRCC_DAEMON"] = "1"
        environment["QT_QPA_PLATFORM"] = "offscreen"
        completed = runner(
            [trusted, "device", "disconnect", THERMALRIGHT_DEVICE_KEY],
            capture_output=True,
            text=True,
            timeout=max(0.25, min(3.0, float(timeout))),
            check=False,
            env=environment,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return FirmwareRestoreResult(False, str(exc))
    detail = (completed.stdout or completed.stderr or "").strip()
    already_released = "not attached" in detail.casefold()
    return FirmwareRestoreResult(completed.returncode == 0 or already_released, detail)


def stop_owned_daemon(
    executable: str,
    expected_pid: int | None,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    finder: Callable[[], DaemonMemorySample | None] = find_trcc_daemon_memory,
    owned_pid_exists: Callable[[int], bool | None] = is_owned_trcc_daemon_pid,
) -> FirmwareRestoreResult:
    """Stop only the same daemon observed after OHC launched its first client."""
    if expected_pid is None:
        return FirmwareRestoreResult(True, "TRCC daemon was not started by OHC")
    sample = finder()
    if sample is None:
        return FirmwareRestoreResult(True, "TRCC daemon already stopped")
    if sample.pid != expected_pid:
        # The finder selects the largest same-user TRCC daemon. A different
        # match does not mean our originally recorded PID survived.
        if owned_pid_exists(expected_pid) is False:
            return FirmwareRestoreResult(True, "OHC-owned TRCC daemon already stopped; replacement left untouched")
        return FirmwareRestoreResult(False, "TRCC daemon PID changed; left running")
    try:
        trusted = _trusted_trcc_executable(executable)
        environment = os.environ.copy()
        environment.pop("TRCC_DAEMON", None)
        environment["QT_QPA_PLATFORM"] = "offscreen"
        completed = runner(
            [trusted, "kill"], capture_output=True, text=True,
            timeout=8.0, check=False, env=environment,
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return FirmwareRestoreResult(False, str(exc))
    remaining = finder()
    for _attempt in range(10):
        if remaining is None or remaining.pid != expected_pid:
            break
        time.sleep(0.1)
        remaining = finder()
    if remaining is not None and remaining.pid == expected_pid:
        return FirmwareRestoreResult(False, "TRCC daemon remained alive after kill request")
    detail = (completed.stdout or completed.stderr or "").strip()
    return FirmwareRestoreResult(completed.returncode == 0, detail)


class LevitaFirmwareGuard:
    """Pipe-bound helper that runs the fallback only after an unclean exit."""

    def __init__(
        self,
        executable: str | None,
        *,
        process_factory: Callable[..., subprocess.Popen[str]] = subprocess.Popen,
    ) -> None:
        self.executable = executable
        self._process_factory = process_factory
        self._process: subprocess.Popen[str] | None = None

    @property
    def armed(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def arm(self, executable: str | None = None) -> bool:
        # Offscreen tests may coexist with the user's real TRCC daemon. They
        # must never inherit display-release authority through a crash helper.
        if os.environ.get("OHC_DISABLE_HARDWARE_IO") == "1":
            return False
        if self.armed:
            return True
        if executable is not None:
            self.executable = executable
        if not self.executable:
            return False
        try:
            trusted = _trusted_trcc_executable(self.executable)
            parent_pid = os.getpid()
            parent_starttime = _current_process_starttime()
            if parent_starttime is None:
                return False
            self._process = self._process_factory(
                [sys.executable, str(Path(__file__).resolve()), "--watch", trusted,
                 str(parent_pid), parent_starttime],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True,
                close_fds=True,
                start_new_session=True,
            )
        except (OSError, ValueError, subprocess.SubprocessError):
            self._process = None
            return False
        return self.armed

    def finish(self, *, restored: bool) -> None:
        process, self._process = self._process, None
        if process is None or process.poll() is not None:
            return
        try:
            if restored and process.stdin is not None:
                process.stdin.write(_CLEAN_EXIT_TOKEN + "\n")
                process.stdin.flush()
            if process.stdin is not None:
                process.stdin.close()
            process.wait(timeout=1.0)
        except (OSError, subprocess.SubprocessError):
            # Closing the pipe without the clean token intentionally asks the
            # surviving helper to retry the bounded firmware release.
            try:
                if process.stdin is not None and not process.stdin.closed:
                    process.stdin.close()
            except OSError:
                pass


def _watch_parent_pipe(
    executable: str,
    parent_pid: int,
    parent_starttime: str,
    *,
    parent_probe: Callable[[int, str], bool | None] = _parent_identity_matches,
    sleeper: Callable[[float], None] = time.sleep,
) -> int:
    """Release only after both pipe loss and confirmed exact parent death."""

    token = sys.stdin.readline().strip()
    if token == _CLEAN_EXIT_TOKEN:
        return 0
    from modules.application_shutdown.v1_1.journal import record
    record("levita-guard-pipe-closed", parent_pid=parent_pid, parent_starttime=parent_starttime)
    # Pipe closure can occur while OHC remains alive. Wait for the same /proc
    # incarnation to end before handing the user's active LCD back to firmware.
    while parent_probe(parent_pid, parent_starttime) is not False:
        sleeper(1.0)
    record("levita-guard-parent-gone", parent_pid=parent_pid)
    return 0 if restore_firmware_logo(executable).ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--watch":
        try:
            watched_pid = int(sys.argv[3])
        except ValueError:
            raise SystemExit(2)
        if watched_pid <= 0 or not sys.argv[4].isdigit():
            raise SystemExit(2)
        raise SystemExit(_watch_parent_pipe(sys.argv[2], watched_pid, sys.argv[4]))
    raise SystemExit(2)
