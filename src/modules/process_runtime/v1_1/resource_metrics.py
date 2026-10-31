# SPDX-License-Identifier: GPL-3.0-or-later
"""Best-effort own-process Linux CPU/RSS, never summed as unique memory."""
import os
from pathlib import Path
import time


class ResourceMetrics:
    def __init__(self):
        self.previous = {}

    def sample(self, pid):
        try:
            base = Path('/proc') / str(pid)
            fields = (base / 'stat').read_text().rsplit(')', 1)[1].split()
            key = (pid, fields[19])
            ticks = int(fields[11]) + int(fields[12])
            now = time.monotonic()
            previous = self.previous.get(key)
            self.previous[key] = ticks, now
            cpu = None if previous is None else max(0., (ticks - previous[0]) / os.sysconf('SC_CLK_TCK') / max(.001, now - previous[1]) * 100)
            rss = next(int(line.split()[1]) / 1024 for line in (base / 'status').read_text().splitlines() if line.startswith('VmRSS:'))
            return cpu, rss
        except (OSError, ValueError, IndexError, StopIteration):
            return None, None

    def retain(self, pids):
        self.previous = {key: value for key, value in self.previous.items() if key[0] in pids}
