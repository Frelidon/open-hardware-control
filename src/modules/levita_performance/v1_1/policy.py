#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure safety and polling policy for Levita frame rates and game signals."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


SAFE_LCD_FPS = (5, 10, 15, 20, 24, 25, 30)
EXPERIMENTAL_LCD_FPS = 60
DEFAULT_LCD_FPS = 15
GAME_ACTIVITY_POLL_MS = 10_000
_PROCESS_NAME = re.compile(r"^[A-Za-z0-9_.+:-]{1,96}$")


def normalize_lcd_fps(value: object, *, experimental_60: bool = False) -> int:
    """Clamp persisted or UI input to an explicitly supported choice."""
    try:
        fps = int(value)
    except (TypeError, ValueError):
        return DEFAULT_LCD_FPS
    allowed = SAFE_LCD_FPS + ((EXPERIMENTAL_LCD_FPS,) if experimental_60 else ())
    return fps if fps in allowed else DEFAULT_LCD_FPS


def fallback_lcd_fps(value: object) -> int:
    """Return the next conservative rate after a ticker/backend failure."""
    fps = normalize_lcd_fps(value, experimental_60=True)
    if fps > 30:
        return 30
    if fps > 20:
        return 20
    return 15 if fps > 15 else fps


def normalize_process_names(value: object) -> tuple[str, ...]:
    """Parse a bounded executable-name list without accepting shell syntax."""
    raw = str(value or "").replace(",", "\n").replace(";", "\n")
    result: list[str] = []
    for line in raw.splitlines():
        name = Path(line.strip()).name.casefold()
        if name and _PROCESS_NAME.fullmatch(name) and name not in result:
            result.append(name)
        if len(result) >= 64:
            break
    return tuple(result)


def parse_gamemode_status(output: object, exit_code: int = 0) -> bool:
    """Recognize Feral GameMode's global active response conservatively."""
    text = " ".join(str(output or "").casefold().split())
    if exit_code != 0 or not text:
        return False
    if any(marker in text for marker in ("inactive", "not active", "not running")):
        return False
    return "active" in text or "is running" in text


def process_game_signal(running: Iterable[str], configured: Iterable[str]) -> tuple[bool, str]:
    """Match Gamescope or an explicit executable allow-list."""
    processes = {Path(str(name)).name.casefold() for name in running}
    if processes.intersection({"gamescope", "gamescope-wl"}):
        return True, "Gamescope"
    configured_set = {str(name).casefold() for name in configured}
    matched = sorted(processes.intersection(configured_set))
    return (True, f"Programmliste · {matched[0]}") if matched else (False, "")


@dataclass(frozen=True)
class GameSignals:
    manual: bool = False
    gamemode: bool = False
    gamescope_or_process: bool = False
    process_reason: str = ""


def resolve_game_activity(signals: GameSignals) -> tuple[bool, str]:
    """Resolve deterministic priority without CPU/GPU-load guessing."""
    if signals.manual:
        return True, "Manuell"
    if signals.gamemode:
        return True, "Feral GameMode"
    if signals.gamescope_or_process:
        return True, signals.process_reason or "Gamescope/Programmliste"
    return False, "Desktop"
