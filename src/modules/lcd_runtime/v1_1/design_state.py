# SPDX-License-Identifier: GPL-3.0-or-later
"""Separate explicit startup persistence, preview and accepted hardware intent."""
from dataclasses import dataclass
from copy import deepcopy


@dataclass(frozen=True)
class DesignRequest:
    sequence: tuple
    animated: bool
    hardware: bool
    gpu_clock_block: object


class DesignState:
    def __init__(self, settings):
        self.settings = settings
        self.generation = 0
        self.desired = None

    def has_standard(self):
        # Retain a missing file too: an unrelated profile must not hide the
        # missing-file error or reactivate a deliberately disabled standard.
        return bool(str(self.settings.value('thermalright/start_media', '') or ''))

    def invalidate_startup(self):
        self.generation += 1

    def capture(self, sequence, animated, *, hardware=False, layout=None):
        block = next((item for item in layout.blocks if item.metric == 'gpu:primary:clock'), None) if layout else None
        self.desired = DesignRequest(tuple((tuple(args), bool(tolerate))
                                          for args, tolerate in sequence), bool(animated),
                                     bool(hardware), deepcopy(block))

    def recover(self, host):
        request = self.desired
        if request is None or host.shutdown_started or host.test_mode.isChecked():
            return False
        # Reuse the immutable prepared assets and serialized command intent;
        # browsing another video cannot alter a daemon recovery.
        host.pending_apply_sequence = list(request.sequence)
        host.pending_apply_animated = request.animated
        host.pending_apply_warning = ''
        host.apply_retry_remaining = 1
        host.apply_start_timer.start()
        return True
