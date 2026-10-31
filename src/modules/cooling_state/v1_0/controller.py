# SPDX-License-Identifier: GPL-3.0-or-later
"""Separate stored startup intent from acquired control; no PWM operations."""


def requested(host):
    return bool(host.mainboard_control_active or getattr(host, "mainboard_startup_pending", False))


def closing(host):
    return any(getattr(host, key, False) for key in (
        "explicit_quit_requested", "session_shutdown_requested", "exit_cleanup_in_progress",
        "exit_hardware_cleanup_done"))


def sync_master(host):
    checkbox = getattr(host, "mainboard_master_enable", None)
    if checkbox is not None:
        blocked = checkbox.blockSignals(True)
        checkbox.setChecked(bool(host.mainboard_control_active))
        checkbox.blockSignals(blocked)
    host.refresh_cooling_dashboard_summary()


def restore_requested(host):
    if not getattr(host, "mainboard_startup_pending", False) or closing(host): return
    if not getattr(host, "cooling_owner_status_known", False):
        host.refresh_cooling_ownership_status(lambda: restore_requested(host))
        return
    if host.cooling_owner_status.coolercontrol_active:
        sync_master(host)
        return  # Preserve intent, but never take over a foreign controller.
    if not host.mainboard_channels or not host.fan_backend_write_ready():
        sync_master(host)
        return
    host.toggle_mainboard_master_control(True, silent=True, owner_checked=True)
    if host.mainboard_control_active: host.mainboard_startup_pending = False
    sync_master(host)


def toggle_dashboard(host):
    host.mainboard_startup_pending = False
    generation = getattr(host, "cooling_dashboard_request", 0) + 1
    host.cooling_dashboard_request = generation
    desired = not host.mainboard_control_active
    sync_master(host)
    def checked_owner():
        if closing(host) or generation != host.cooling_dashboard_request: return
        if desired and host.cooling_owner_status.coolercontrol_active:
            host.show_error(host.tr_static("CoolerControl besitzt die Lüftersteuerung. Bitte zuerst die Steuerung ausdrücklich mit OHC übernehmen."))
            sync_master(host)
            return
        host.toggle_mainboard_master_control(desired, owner_checked=True)
        sync_master(host)
    host.refresh_cooling_ownership_status(checked_owner)


def checked_master(host, *, silent=False):
    """Lower master checkbox follows the same fresh, fail-closed owner check."""
    generation = getattr(host, "cooling_dashboard_request", 0) + 1
    host.cooling_dashboard_request = generation
    sync_master(host)
    def finished():
        if closing(host) or generation != host.cooling_dashboard_request: return
        host.toggle_mainboard_master_control(True, silent=silent, owner_checked=True)
        sync_master(host)
    host.refresh_cooling_ownership_status(finished)
