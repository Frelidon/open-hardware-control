# SPDX-License-Identifier: GPL-3.0-or-later
"""Recognize legacy frame acknowledgements and daemon-owned TRCC playback."""
import re

SENT = re.compile(r'^\s*sent ([0-9]{1,12}) bytes \(theme=')
DAEMON_PLAYBACK = re.compile(
    r"\bthe daemon is playing [0-9a-f]{4}:[0-9a-f]{4}\s+[^\n]*"
    r"it keeps the panel updated\.",
    re.IGNORECASE,
)


def daemon_owns_playback(text: str) -> bool:
    """Accept only TRCC's explicit successful hand-off sentence."""
    return bool(DAEMON_PLAYBACK.search(str(text or "")))


class DisplayProgress:
    def __init__(self):
        self.started = self.last_sent = 0.0
        self.frames = 0
        self.buffer = ''

    def reset(self, now):
        self.started, self.last_sent, self.frames, self.buffer = now, 0.0, 0, ''

    def feed(self, text, now):
        self.buffer += text
        advanced = False
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            match = SENT.match(line)
            if match and int(match[1]) > 0:
                self.last_sent = now
                self.frames += 1
                advanced = True
        self.buffer = self.buffer[-4096:]
        return advanced

    def timeout(self, now):
        # Startup includes RestoreDeviceState; subsequent silence includes IPC/USB.
        limit = 15 if self.frames else 45
        return now - (self.last_sent if self.frames else self.started) >= limit
