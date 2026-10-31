# SPDX-License-Identifier: GPL-3.0-or-later
"""Restore the selected design after closing an explicit LED preview."""


class HeaderPreview:
    def __init__(self, host):
        self.host = host
        snapshot = getattr(host, "current_rgb_design_snapshot", None)
        self.snapshot = snapshot() if snapshot else None
        self.selection = set(getattr(host, "rgb_selected_devices", ()))
        host.rgb_header_preview_depth = getattr(host, "rgb_header_preview_depth", 0) + 1
        self.pending = 0
        self.touched = self.closed = self.failed = self.scheduled = False

    def start(self):
        self.touched = True
        self.pending += 1

    def complete(self, ok):
        self.pending = max(0, self.pending - 1)
        self.failed = self.failed or not ok
        self._schedule()

    def close(self, saved=False):
        if not self.closed:
            self.host.rgb_header_preview_depth = max(0, self.host.rgb_header_preview_depth - 1)
        self.closed = True
        self.touched = self.touched or saved
        self._schedule()

    def _schedule(self):
        if self.closed and self.touched and not self.pending and not self.scheduled and self.snapshot is not None:
            self.scheduled = True
            # Do not leave a Python-bound Qt timer behind when the editor has
            # already destroyed its transient dialog.  On PySide 6.9 that
            # callback could race QObject teardown and segfault before Python
            # had a chance to raise an exception.  Completion callbacks and
            # QDialog.finished already run on the GUI thread, so restoration
            # is safe and deterministic here without a delayed Qt callback.
            self.restore()

    def restore(self):
        host = self.host
        if (getattr(host, "rgb_header_preview_depth", 0)
                or getattr(host, "explicit_quit_requested", False)
                or getattr(host, "session_shutdown_requested", False)
                or getattr(host, "exit_hardware_cleanup_in_progress", False)
                or getattr(host, "exit_hardware_cleanup_done", False)
                or getattr(host.backend, "_shutting_down", False)
                or not host.openrgb_write_enabled
                or not host.openrgb_server_reachable
                or host.openrgb_external_server_detected
                or getattr(host, "openrgb_engine_crash_quarantined", False)
                or host.current_rgb_design_snapshot() != self.snapshot
                or set(host.rgb_selected_devices) != self.selection):
            return
        host.log_message("ARGB: preview-restore · selected-design · selected-devices · owned-engine"
                         + (" · after failed test" if self.failed else ""))
        host.rgb_direct_apply_pending = False
        host.rgb_last_effect_request_signature = None
        if host.current_rgb_studio_config().effect_id == "static":
            host.apply_openrgb_static()
        else:
            host.start_openrgb_effect()
