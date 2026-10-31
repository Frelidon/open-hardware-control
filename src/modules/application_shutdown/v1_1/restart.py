# SPDX-License-Identifier: GPL-3.0-or-later
"""Relaunch OHC only after the old single-instance owner has exited."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time


def process_starttime(pid: int) -> str:
    """Return the Linux starttime token used to reject PID reuse."""

    try:
        fields = Path(f"/proc/{int(pid)}/stat").read_text(encoding="utf-8").split()
    except (OSError, ValueError):
        return ""
    return fields[21] if len(fields) > 21 else ""


def relaunch_command(argv: list[str] | None = None) -> list[str]:
    """Build an exact Python entry command without preserving tray autostart."""

    values = list(sys.argv if argv is None else argv)
    entry = Path(values[0]).resolve() if values else Path(__file__).resolve().parents[3] / "kraken_control.py"
    forwarded = [value for value in values[1:] if value != "--autostart"]
    return [sys.executable, str(entry), *forwarded]


def schedule_relaunch(command: list[str], *, parent_pid: int | None = None) -> bool:
    """Start a detached waiter; it never launches while the old lock owner lives."""

    pid = int(parent_pid or os.getpid())
    starttime = process_starttime(pid)
    if not command or not starttime:
        return False
    try:
        subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--wait-parent", str(pid), starttime, "--", *command],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True,
        )
    except OSError:
        return False
    return True


def wait_and_exec(pid: int, starttime: str, command: list[str], *, timeout: float = 45.0) -> int:
    deadline = time.monotonic() + max(1.0, timeout)
    while time.monotonic() < deadline and process_starttime(pid) == starttime:
        time.sleep(0.1)
    if process_starttime(pid) == starttime or not command:
        return 1
    try:
        os.execv(command[0], command)
    except OSError:
        return 1
    return 0


def main(arguments: list[str]) -> int:
    if len(arguments) < 5 or arguments[1] != "--wait-parent" or arguments[4] != "--":
        return 2
    try:
        pid = int(arguments[2])
    except ValueError:
        return 2
    return wait_and_exec(pid, arguments[3], arguments[5:])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
