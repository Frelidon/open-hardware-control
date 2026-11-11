# SPDX-License-Identifier: GPL-3.0-or-later
"""Wizard lifecycle and short crash leases; never infer wiring from RPM."""
import math
import time
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget
from mainboard_fan_control import (
    FanWriteError, channel_is_chassis_fan, restore_firmware_control,
    set_fan_control_watchdog,
)
from modules.ui_performance.v1_1.compact_panels import Disclosure

STOP_SECONDS = 120
LEASE_SECONDS = 10


def disconnected(host, channel):
    return host.mainboard_fan_profiles.get(channel.stable_id, {}).get("connection") == "disconnected"


def cancel_test(host):
    if getattr(host, "mainboard_calibration_channel_id", ""):
        host.finish_mainboard_fan_calibration(confirm=False)


def mark_disconnected(host):
    cancel_test(host)
    channel = host.selected_mainboard_channel()
    if channel is None or not channel_is_chassis_fan(channel):
        return
    profile = host.mainboard_profile_for(channel)
    if profile.get("enabled"):
        try:
            restore_firmware_control(channel)
        except FanWriteError as exc:
            host.show_error(str(exc)); return
    profile.update(connection="disconnected", enabled=False, calibrated=False)
    host.mainboard_layout_assignments.pop(channel.stable_id, None)
    host.save_mainboard_fan_settings()
    host.refresh_mainboard_fan_table()
    host.refresh_chassis_assistant_summary()
    host.assistant_continue_with_next_fan()


def reactivate(host, channel_id):
    channel = host.mainboard_channels.get(channel_id)
    if channel is None:
        return
    host.mainboard_profile_for(channel).update(connection="connected", calibrated=False, enabled=False)
    host.save_mainboard_fan_settings(); host.refresh_mainboard_fan_table()
    host.start_chassis_fan_assistant()
    combo = getattr(host, "assistant_channel_combo", None)
    if combo is not None:
        combo.setCurrentIndex(combo.findData(channel_id))


def add_unused_section(host, channels):
    unused = [c for c in channels if disconnected(host, c)]
    if not unused:
        return
    body = QWidget(); layout = QVBoxLayout(body)
    box = Disclosure(host.tr_static("Nicht angeschlossene Anschlüsse"), body)
    for channel in unused:
        button = QPushButton(f"{channel.display_name} · {host.tr_static('Erneut zuordnen')}")
        button.setToolTip(host.tr_static("Dieser Anschluss wird bis zur erneuten Zuordnung nicht automatisch geregelt."))
        button.clicked.connect(lambda _checked=False, key=channel.stable_id: reactivate(host, key))
        layout.addWidget(button)
    host.mainboard_fan_cards_layout.addWidget(box)


def begin_stop_lease(host):
    controller = host.mainboard_hwmon_controller
    if controller is None or not set_fan_control_watchdog(controller, LEASE_SECONDS):
        raise FanWriteError(host.tr_static("Der lange Stopptest benötigt die Absturzsicherung des Lüftertreibers."))
    host.fan_stop_lease_refreshed = time.monotonic()


def stop_temperature_safe(host):
    try:
        cpu = float(host.current_cpu_temp)
        gpu = getattr(host, "current_gpu_temp", None)
        return (math.isfinite(cpu) and -40 <= cpu < 90
                and (gpu is None or (math.isfinite(float(gpu)) and -40 <= float(gpu) < 90)))
    except (TypeError, ValueError, OverflowError):
        return False


def refresh_stop_lease(host):
    """False restores now; a crash/hung event loop cannot refresh the kernel."""
    if getattr(host, "mainboard_calibration_target_percent", 70) != 0:
        return True
    if not stop_temperature_safe(host):
        return False
    now = time.monotonic()
    if now - getattr(host, "fan_stop_lease_refreshed", 0) >= 3:
        try:
            begin_stop_lease(host)
        except FanWriteError:
            return False
    return True


def wizard_page_changed(host, page_id):
    if page_id != 1:
        if getattr(host, "mainboard_calibration_channel_id", ""):
            host.finish_mainboard_fan_calibration()
    if page_id == 3:
        host.refresh_chassis_assistant_summary()


def wizard_finished(host):
    cancel_test(host)
    host.restore_rgb_after_chassis_assistant()
    host.refresh_mainboard_fan_table()


def confirmation_text(host, channel, duration, target, contrast, other, method, stop):
    tr = host.tr_static
    text = tr("{channel} wird höchstens {seconds} Sekunden mit {percent} % geprüft. Danach wird der vorherige Zustand wiederhergestellt.").format(channel=channel.stable_id, seconds=duration, percent=target)
    if contrast:
        text += "\n\n" + tr("Andere angeschlossene Gehäuselüfter laufen währenddessen mit {percent} %.").format(percent=other)
    if stop:
        text += "\n\n" + tr("Weiter und Abbrechen stellen die Regelung sofort wieder her. Bei einem Programmabsturz übernimmt die kurze Treiber-Absturzsicherung. Manche Lüfter können hardwarebedingt nicht vollständig stoppen.")
    text += "\n\n" + tr("Beobachte die tatsächliche Lüftergruppe. OHC rät keine Zuordnung anhand von Drehzahlen oder Kanalnummern.")
    if method == "polkit":
        text += "\n\n" + tr("Für den geschützten Lüfterzugriff kann Linux einmalig eine Systemauthentifizierung anfordern.")
    return text + "\n\n" + tr("Test starten?")
