#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure state and safety policy for Snapshot Manager 1.0."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Iterable


DEFAULT_DESKTOP_IOPS = 50
DEFAULT_DESKTOP_KBPS = 16_384
DEFAULT_GAME_IOPS = 5
DEFAULT_GAME_KBPS = 2_048
DEFAULT_CPU_THRESHOLD = 70
DEFAULT_GPU_THRESHOLD = 65
DEFAULT_BUSY_CORE_PERCENT = 65
DEFAULT_CPU_CORE_LIMIT = 2
DEFAULT_CPU_PERCENT_PER_CORE = 50
MAX_PROCESS_NAMES = 64
_PROCESS_NAME = re.compile(r"^[A-Za-z0-9_.+:-]{1,96}$")


@dataclass(frozen=True)
class SnapshotPolicy:
    automatic_game_pause: bool = True
    fullscreen_signal: bool = True
    load_heuristic: bool = True
    cpu_threshold: int = DEFAULT_CPU_THRESHOLD
    gpu_threshold: int = DEFAULT_GPU_THRESHOLD
    busy_core_percent: int = DEFAULT_BUSY_CORE_PERCENT
    high_samples: int = 3
    release_samples: int = 3
    desktop_iops: int = DEFAULT_DESKTOP_IOPS
    desktop_kbps: int = DEFAULT_DESKTOP_KBPS
    game_iops: int = DEFAULT_GAME_IOPS
    game_kbps: int = DEFAULT_GAME_KBPS
    cpu_core_limit: int = DEFAULT_CPU_CORE_LIMIT
    cpu_percent_per_core: int = DEFAULT_CPU_PERCENT_PER_CORE

    @property
    def cpu_quota_percent(self) -> int:
        """Return systemd's total quota where 100 percent equals one CPU."""

        return self.cpu_core_limit * self.cpu_percent_per_core


@dataclass(frozen=True)
class ActivitySample:
    cpu_percent: float = 0.0
    busy_cores: int = 0
    logical_cores: int = 1
    gpu_percent: float | None = None
    gamemode: bool = False
    gamescope: bool = False
    fullscreen: bool = False
    process_active: bool = False
    process_reason: str = ""


@dataclass(frozen=True)
class GateDecision:
    blocked: bool
    reason: str
    high_streak: int
    idle_streak: int


@dataclass(frozen=True)
class SnapshotRecord:
    number: str
    created: str
    description: str
    cleanup: str = ""
    used_bytes: int | None = None
    source: str = "system"


def bounded_int(value: object, low: int, high: int, fallback: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(low, min(high, number))


def normalized_bool(value: object, fallback: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return fallback
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().casefold()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off", ""}:
        return False
    return fallback


def normalize_policy(raw: dict[str, object] | None = None) -> SnapshotPolicy:
    values = raw or {}
    return SnapshotPolicy(
        automatic_game_pause=normalized_bool(values.get("automatic_game_pause"), True),
        fullscreen_signal=normalized_bool(values.get("fullscreen_signal"), True),
        load_heuristic=normalized_bool(values.get("load_heuristic"), True),
        cpu_threshold=bounded_int(values.get("cpu_threshold"), 40, 100, DEFAULT_CPU_THRESHOLD),
        gpu_threshold=bounded_int(values.get("gpu_threshold"), 30, 100, DEFAULT_GPU_THRESHOLD),
        busy_core_percent=bounded_int(values.get("busy_core_percent"), 40, 100, DEFAULT_BUSY_CORE_PERCENT),
        high_samples=bounded_int(values.get("high_samples"), 2, 12, 3),
        release_samples=bounded_int(values.get("release_samples"), 2, 18, 3),
        desktop_iops=bounded_int(values.get("desktop_iops"), 25, 1000, DEFAULT_DESKTOP_IOPS),
        desktop_kbps=bounded_int(values.get("desktop_kbps"), 8_192, 262_144, DEFAULT_DESKTOP_KBPS),
        game_iops=bounded_int(values.get("game_iops"), 1, 100, DEFAULT_GAME_IOPS),
        game_kbps=bounded_int(values.get("game_kbps"), 1_024, 65_536, DEFAULT_GAME_KBPS),
        cpu_core_limit=bounded_int(values.get("cpu_core_limit"), 1, 8, DEFAULT_CPU_CORE_LIMIT),
        cpu_percent_per_core=bounded_int(
            values.get("cpu_percent_per_core"), 10, 100, DEFAULT_CPU_PERCENT_PER_CORE,
        ),
    )


def normalize_process_names(value: object) -> tuple[str, ...]:
    raw = str(value or "").replace(",", "\n").replace(";", "\n")
    result: list[str] = []
    for line in raw.splitlines():
        name = Path(line.strip()).name.casefold()
        if name and _PROCESS_NAME.fullmatch(name) and name not in result:
            result.append(name)
        if len(result) >= MAX_PROCESS_NAMES:
            break
    return tuple(result)


def trusted_game_reason(sample: ActivitySample, policy: SnapshotPolicy) -> str:
    if sample.gamemode:
        return "Feral GameMode"
    if sample.gamescope:
        return "Gamescope"
    if sample.process_active:
        return sample.process_reason or "Programmliste"
    if policy.fullscreen_signal and sample.fullscreen:
        return "Vollbildanwendung"
    return ""


def load_signal(sample: ActivitySample, policy: SnapshotPolicy) -> bool:
    if not policy.load_heuristic or sample.gpu_percent is None:
        return False
    needed_cores = max(2, (max(1, sample.logical_cores) + 2) // 3)
    return (
        sample.cpu_percent >= policy.cpu_threshold
        and sample.busy_cores >= needed_cores
        and sample.gpu_percent >= policy.gpu_threshold
    )


class ActivityGate:
    """Hysteresis that reacts immediately to trusted signals, slowly to load."""

    def __init__(self) -> None:
        self.blocked = False
        self.reason = "Desktop"
        self.high_streak = 0
        self.idle_streak = 0

    def update(self, sample: ActivitySample, policy: SnapshotPolicy) -> GateDecision:
        if not policy.automatic_game_pause:
            self.blocked = False
            self.reason = "Desktop"
            self.high_streak = self.idle_streak = 0
            return self.decision()
        trusted = trusted_game_reason(sample, policy)
        high = load_signal(sample, policy)
        if trusted:
            self.blocked = True
            self.reason = trusted
            self.high_streak = policy.high_samples
            self.idle_streak = 0
        elif high:
            self.high_streak += 1
            self.idle_streak = 0
            if self.high_streak >= policy.high_samples:
                self.blocked = True
                self.reason = "CPU- und GPU-Last"
        else:
            self.high_streak = 0
            if self.blocked:
                self.idle_streak += 1
                if self.idle_streak >= policy.release_samples:
                    self.blocked = False
                    self.reason = "Desktop"
                    self.idle_streak = 0
            else:
                self.idle_streak = 0
        return self.decision()

    def decision(self) -> GateDecision:
        return GateDecision(self.blocked, self.reason, self.high_streak, self.idle_streak)


def manual_block_active(mode: object, until_epoch: object, now: float | None = None) -> bool:
    selected = str(mode or "desktop")
    if selected == "forever":
        return True
    if selected != "until":
        return False
    try:
        deadline = float(until_epoch)
    except (TypeError, ValueError):
        return False
    current = datetime.now(timezone.utc).timestamp() if now is None else float(now)
    return deadline > current


def format_bytes(value: object) -> str:
    try:
        size = max(0, int(value))
    except (TypeError, ValueError):
        return "—"
    for suffix in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or suffix == "TiB":
            return f"{size:.0f} {suffix}" if suffix in {"B", "KiB"} else f"{size:.1f} {suffix}"
        size /= 1024
    return "—"


def parse_snapper_json(payload: object) -> tuple[SnapshotRecord, ...]:
    if not isinstance(payload, dict):
        return ()
    rows = payload.get("snapshots")
    if not isinstance(rows, list):
        rows = payload.get("data")
    if not isinstance(rows, list):
        return ()
    result: list[SnapshotRecord] = []
    for row in rows[:500]:
        if not isinstance(row, dict):
            continue
        number = str(row.get("number", row.get("#", "")))[:32]
        if not number:
            continue
        description = str(row.get("description", ""))[:240]
        source = "ohc" if (
            description.casefold().startswith("[ohc]")
            or "open hardware control" in description.casefold()
        ) else "system"
        if description.casefold().startswith("[ohc]"):
            description = description[5:].lstrip()
        result.append(SnapshotRecord(
            number=number,
            created=str(row.get("date", row.get("created", "")))[:64],
            description=description,
            cleanup=str(row.get("cleanup", ""))[:64],
            source=source,
        ))
    return tuple(result)


def process_match(running: Iterable[str], configured: Iterable[str]) -> tuple[bool, str]:
    names = {Path(str(value)).name.casefold() for value in running}
    if names.intersection({"gamescope", "gamescope-wl"}):
        return True, "Gamescope"
    matches = sorted(names.intersection({str(value).casefold() for value in configured}))
    return (True, matches[0]) if matches else (False, "")
