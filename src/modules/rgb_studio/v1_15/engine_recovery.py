# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit recovery only; never restart crash loops or signal foreign engines."""
from PySide6.QtCore import QProcess, QTimer


def manual_engine_recovery(host):
    if host.hardware_io_disabled or getattr(host, "explicit_quit_requested", False):
        return
    # Old inventory completion cannot overwrite a newer manual restart or leave
    # its busy flag latched. The existing callback rejects stale generations.
    host.openrgb_discovery_generation += 1
    host.openrgb_status_busy = False
    host.rgb_engine_disabled_by_reset = False
    host.openrgb_engine_crash_quarantined = False
    host.rgb_reinitialize_pending = False
    host.rgb_reinitialize_refreshing = False
    host.openrgb_sdk_ready_devices.clear()
    if getattr(host, "openrgb_write_enabled", False):
        host.rgb_direct_apply_pending = True
        host.openrgb_write_enable_pending = True
    host.stop_openrgb_effect(host.tr_static("↻ RGB-Steuerung neu übernehmen"))
    if host.openrgb_engine_owned and host.openrgb_server_process.state() != QProcess.ProcessState.NotRunning:
        host.rgb_engine_restart_pending = True
        host.stop_managed_rgb_engine()
        timer = QTimer(host)
        timer.setSingleShot(True)
        def finish_owned_stop():
            if (host.rgb_engine_restart_pending and host.openrgb_engine_stop_requested
                    and host.openrgb_server_process.state() != QProcess.ProcessState.NotRunning):
                host.openrgb_server_process.kill()
            timer.deleteLater()
        timer.timeout.connect(finish_owned_stop)
        timer.start(1800)
    else:
        host.rgb_engine_restart_pending = False
        host.refresh_rgb_studio()
    host.log_message("RGB-ENGINE: manual-recovery · stale-inventory=invalidated · foreign-processes=untouched")
