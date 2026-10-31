#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure bounded history model for the visible OHC runtime log."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import time


LOG_RETENTION_SECONDS = 60 * 60
LOG_MAX_CHARACTERS = 4 * 1024 * 1024
LOG_MAX_ENTRIES = 30_000


@dataclass(frozen=True, slots=True)
class LogEntry:
    observed_at: float
    line: str


class RollingLogBuffer:
    """Keep at least the recent time window with hard memory safety bounds."""

    def __init__(
        self,
        *,
        window_seconds: float = LOG_RETENTION_SECONDS,
        max_characters: int = LOG_MAX_CHARACTERS,
        max_entries: int = LOG_MAX_ENTRIES,
    ) -> None:
        self.window_seconds = max(1.0, float(window_seconds))
        self.max_characters = max(1, int(max_characters))
        self.max_entries = max(1, int(max_entries))
        self._entries: deque[LogEntry] = deque()
        self._characters = 0

    def append(
        self,
        line: str,
        *,
        now: float | None = None,
        prune_expired: bool = True,
    ) -> int:
        clean = str(line).rstrip("\r\n")
        if not clean:
            return 0
        observed_at = time.monotonic() if now is None else float(now)
        self._entries.append(LogEntry(observed_at, clean))
        self._characters += len(clean) + 1
        removed = self.prune(observed_at) if prune_expired else 0
        while (
            len(self._entries) > self.max_entries
            or self._characters > self.max_characters
        ):
            removed += self._remove_oldest()
        return removed

    def prune(self, now: float | None = None) -> int:
        observed_at = time.monotonic() if now is None else float(now)
        cutoff = observed_at - self.window_seconds
        removed = 0
        while self._entries and self._entries[0].observed_at < cutoff:
            removed += self._remove_oldest()
        return removed

    def _remove_oldest(self) -> int:
        if not self._entries:
            return 0
        entry = self._entries.popleft()
        self._characters = max(0, self._characters - len(entry.line) - 1)
        return 1

    def clear(self) -> None:
        self._entries.clear()
        self._characters = 0

    @property
    def line_count(self) -> int:
        return len(self._entries)

    @property
    def character_count(self) -> int:
        return max(0, self._characters - (1 if self._entries else 0))

    def text(self) -> str:
        return "\n".join(entry.line for entry in self._entries)


_ERROR_MARKERS = (
    "fehler",
    "absturz",
    "crash",
    "unerwartet beendet",
    "fehlgeschlagen",
    "timeout",
    "ausgeschöpft",
    "out of memory",
    "oom-kill",
)


def is_error_log_message(message: str) -> bool:
    """Return whether a shared-log line belongs in the durable error log."""
    lowered = str(message).casefold()
    return any(marker in lowered for marker in _ERROR_MARKERS)
