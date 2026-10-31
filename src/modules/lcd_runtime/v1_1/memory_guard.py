# SPDX-License-Identifier: GPL-3.0-or-later
"""Bound runaway TRCC memory without restarting every stable large video."""
from pathlib import Path

MIB = 1024 * 1024
SOFT_LIMIT = 1024 * MIB
HARD_LIMIT = 3 * 1024 * MIB


def available_memory(proc_root=Path('/proc')):
    try:
        for line in (proc_root / 'meminfo').read_text().splitlines():
            if line.startswith('MemAvailable:'):
                return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    return None


class MemoryGuard:
    def __init__(self):
        self.reset()

    def reset(self):
        self.pid = 0
        self.baseline = self.previous = 0
        self.growing = 0

    def reason(self, sample, available=None):
        if sample is None:
            self.reset()
            return ''
        rss = sample.rss_bytes
        if sample.pid != self.pid:
            self.pid, self.baseline, self.previous = sample.pid, rss, rss
            self.growing = 0
        if rss >= HARD_LIMIT:
            return 'hard-rss-limit'
        if rss >= SOFT_LIMIT and available is not None and available < 256 * MIB:
            return 'system-memory-pressure'
        if rss >= self.previous + 64 * MIB:
            self.growing += 1
        else:
            self.growing = 0
        self.previous = rss
        if rss < self.baseline:
            self.baseline = rss
        if rss >= SOFT_LIMIT and self.growing >= 3 and rss >= self.baseline + 256 * MIB:
            return 'sustained-rss-growth'
        return ''
