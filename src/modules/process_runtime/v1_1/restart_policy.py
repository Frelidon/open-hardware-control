# SPDX-License-Identifier: GPL-3.0-or-later
"""Retry budget renewed only by confirmed progress in a stable generation."""
from dataclasses import dataclass


@dataclass
class RestartBudget:
    attempts: int = 0
    stable_seconds: float = 30.0
    max_attempts: int = 3

    def progress(self, started: float, now: float):
        if now - started >= self.stable_seconds:
            self.attempts = 0

    def failure(self):
        if self.attempts >= self.max_attempts:
            return None
        delay = 1000 * 2 ** self.attempts
        self.attempts += 1
        return delay
