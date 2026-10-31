#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure restart policy for the long-running TRCC video ticker."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StreamRestartPolicy:
    """Bound rapid failures while allowing recovery after a stable run."""

    max_attempts: int = 3
    base_delay_ms: int = 1_000
    stable_seconds: float = 30.0
    attempts: int = 0

    def next_delay_ms(self, runtime_seconds: float) -> int | None:
        if max(0.0, float(runtime_seconds)) >= self.stable_seconds:
            self.attempts = 0
        if self.attempts >= self.max_attempts:
            return None
        delay = self.base_delay_ms * (2 ** self.attempts)
        self.attempts += 1
        return delay

    def reset(self) -> None:
        self.attempts = 0
