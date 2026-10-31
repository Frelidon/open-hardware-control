#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only game and multi-core load probe isolated from the GUI thread."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from modules.levita_performance.v1_1 import parse_gamemode_status
from modules.snapshot_manager.v1_0.model import normalize_process_names, process_match
from modules.platform_support.v1_0 import helper_command


def cpu_times(path: Path = Path("/proc/stat")) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    try:
        lines = path.read_text(encoding="ascii", errors="replace").splitlines()
    except OSError:
        return result
    for line in lines:
        fields = line.split()
        if not fields or not fields[0].startswith("cpu") or fields[0] == "cpu":
            continue
        try:
            values = [int(value) for value in fields[1:11]]
        except ValueError:
            continue
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        result.append((sum(values), idle))
    return result


def cpu_sample(interval: float = 0.25) -> tuple[float, list[float]]:
    first = cpu_times()
    time.sleep(max(0.1, min(0.5, interval)))
    second = cpu_times()
    loads: list[float] = []
    for before, after in zip(first, second):
        total = after[0] - before[0]
        idle = after[1] - before[1]
        loads.append(max(0.0, min(100.0, 100.0 * (total - idle) / total)) if total > 0 else 0.0)
    return ((sum(loads) / len(loads)) if loads else 0.0, loads)


def gpu_busy() -> float | None:
    values: list[float] = []
    for path in sorted(Path("/sys/class/drm").glob("card*/device/gpu_busy_percent"))[:16]:
        try:
            values.append(float(path.read_text(encoding="ascii").strip()))
        except (OSError, ValueError):
            continue
    return max(values) if values else None


def running_names() -> list[str]:
    result: list[str] = []
    try:
        entries = Path("/proc").iterdir()
    except OSError:
        return result
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            name = (entry / "comm").read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue
        if name:
            result.append(name[:96])
    return result


def gamemode_active() -> bool:
    executable = shutil.which("gamemoded")
    if not executable:
        return False
    try:
        completed = subprocess.run(
            [executable, "-s"], capture_output=True, text=True,
            timeout=2, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return parse_gamemode_status(completed.stdout[-4096:], completed.returncode)


def fullscreen_state() -> tuple[bool, str]:
    """Query KDE's active window through a one-shot bounded bridge."""
    bridge = Path(__file__).with_name("fullscreen_probe.py")
    if not bridge.is_file() or os.environ.get("XDG_CURRENT_DESKTOP", "").casefold().find("kde") < 0:
        return False, "unavailable"
    try:
        program, arguments = helper_command(bridge)
        completed = subprocess.run(
            [program, *arguments], capture_output=True, text=True,
            timeout=3, check=False,
        )
        payload = json.loads(completed.stdout[-4096:])
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, TypeError):
        return False, "unavailable"
    return bool(payload.get("fullscreen")), str(payload.get("title", ""))[:128]


def probe(configured: tuple[str, ...], busy_core_percent: int) -> dict[str, object]:
    average, cores = cpu_sample()
    names = running_names()
    process_active, process_reason = process_match(names, configured)
    fullscreen, fullscreen_title = fullscreen_state()
    return {
        "schema": 1,
        "cpu_percent": round(average, 1),
        "busy_cores": sum(value >= busy_core_percent for value in cores),
        "logical_cores": max(1, len(cores)),
        "gpu_percent": gpu_busy(),
        "gamemode": gamemode_active(),
        "gamescope": any(name.casefold() in {"gamescope", "gamescope-wl"} for name in names),
        "fullscreen": fullscreen,
        "fullscreen_title": fullscreen_title,
        "process_active": process_active,
        "process_reason": process_reason,
    }


def lower_own_priority() -> None:
    """Keep the independent watcher away from interactive application work."""

    try:
        os.nice(15)
    except OSError:
        pass
    try:
        available = sorted(os.sched_getaffinity(0))
        if available:
            os.sched_setaffinity(0, {available[-1]})
    except (AttributeError, OSError):
        pass


def watch(configured: tuple[str, ...], busy_core_percent: int, interval: float) -> None:
    """Reuse one low-priority process instead of spawning Python every poll."""

    cadence = max(10.0, min(60.0, float(interval)))
    while True:
        started = time.monotonic()
        print(json.dumps(probe(configured, busy_core_percent), ensure_ascii=False), flush=True)
        time.sleep(max(1.0, cadence - (time.monotonic() - started)))


if __name__ == "__main__":
    lower_own_priority()
    configured = normalize_process_names(sys.argv[1] if len(sys.argv) > 1 else "")
    try:
        threshold = max(40, min(100, int(sys.argv[2]))) if len(sys.argv) > 2 else 65
    except ValueError:
        threshold = 65
    if len(sys.argv) > 4 and sys.argv[3] == "--watch":
        try:
            watch_interval = float(sys.argv[4])
        except ValueError:
            watch_interval = 20.0
        watch(configured, threshold, watch_interval)
    else:
        print(json.dumps(probe(configured, threshold), ensure_ascii=False), flush=True)
