#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded per-header editor using the existing SDK and sole-writer queue."""

import json
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QLabel, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget,
)

from openrgb_integration import OpenRGBError
from rgb_devices import configured_zone_sizes
from .argb_diagnostics import log_argb_zones
from .argb_store import remember_headers
from .header_preview import HeaderPreview
from .led_test_isolation import commands as isolated_test_commands


def configure_gpu_header(host, gpu, source, zone_name):
    if not any(mode.casefold() == "external control" for mode in gpu.modes):
        return
    configure_argb_header(host, source, zone_name, gpu=gpu)


def configure_argb_header(host, source, zone_name, *, gpu=None, on_saved=None, suggested_count=None,
                          suggested_units=None, component_name=None):
    if not source.supports_direct:
        return
    if not host.openrgb_server_reachable or host.openrgb_external_server_detected:
        host.show_error(host.tr_static("Die eigene RGB-Engine muss erreichbar sein."))
        return
    if (gpu is not None and host.openrgb_device_conflict(gpu)) or host.openrgb_device_conflict(source):
        return
    inspector = getattr(host, "case_inspector", None)
    token = inspector.reserve(host.tr_static("ARGB-Anschluss") + f" · {zone_name}") if inspector else None

    def inspected(result):
        if inspector is not None and not inspector.is_current(token): return
        if any(getattr(host, key, False) for key in ("explicit_quit_requested", "session_shutdown_requested")): return
        try:
            if not result.ok:
                raise ValueError(result.combined[:800])
            payload = json.loads(result.stdout.strip())
            zones = payload["zones"]
            if not isinstance(zones, list) or len(zones) > 64:
                raise ValueError()
            show_gpu_header_editor(host, gpu, source, zone_name, zones, on_saved=on_saved,
                                   suggested_count=suggested_count, inline_token=token,
                                   suggested_units=suggested_units, component_name=component_name)
        except (KeyError, TypeError, ValueError) as exc:
            if inspector is not None: inspector.dismiss()
            host.show_error(host.tr_static("Der OpenRGB-Zonenbericht war nicht gültig.") + str(exc)[:160])

    try:
        command = host.openrgb_client.sdk_inspect_command(source.index)
    except (OpenRGBError, ValueError) as exc:
        if inspector is not None: inspector.dismiss()
        host.show_error(str(exc))
        return
    host.backend.run_async(command, callback=inspected, timeout=8, log_output=False)


def header_configuration(zones, stored, target, count, topology_units=None):
    """Fill missing server zones; only the chosen header's declared count changes."""
    result = {}
    for zone in zones:
        name = str(zone["name"])
        current = int(zone["current"])
        minimum, maximum = int(zone["minimum"]), int(zone["maximum"])
        if not 0 <= minimum <= maximum <= 4096 or not 0 <= current <= 4096:
            raise ValueError("RGB_ZONE_BOUNDS")
        values = next((dict(value) for key, value in stored.items()
                       if key.casefold() == name.casefold()), None)
        if name == target:
            if not 1 <= count <= min(512, maximum) or count < minimum:
                raise ValueError("RGB_LED_COUNT")
            if count != current and not bool(zone.get("resizable", minimum != maximum)):
                raise ValueError("RGB_FIXED_ZONE")
            # Preserve the declared device/fan structure whenever possible.
            # Flattening 3 x 30 to 1 x 90 made spatial effects illuminate a
            # complete fan bank like one block after every editor save.
            previous_units = values.get("units", 1) if isinstance(values, dict) else 1
            preferred_units = topology_units if topology_units is not None else previous_units
            units = (preferred_units if type(preferred_units) is int
                     and 1 <= preferred_units <= 64 and count % preferred_units == 0 else 1)
            values = {"units": units, "leds_per_unit": count // units}
        elif values is None:
            units = next((n for n in range(1, 65) if current % n == 0 and current // n <= 512), None)
            if units is None:
                raise ValueError("RGB_ZONE_SIZE")
            values = {"units": units if current else 0, "leds_per_unit": current // units}
        total = values["units"] * values["leds_per_unit"]
        if total != current and (not minimum <= total <= maximum or not bool(zone.get("resizable", minimum != maximum))):
            raise ValueError("RGB_ZONE_SIZE")
        result[name] = values
    if target not in result or sum(v["units"] * v["leds_per_unit"] for v in result.values()) > 4096:
        raise ValueError("RGB_ZONE_SHAPE")
    return result


def show_gpu_header_editor(host, gpu, source, zone_name, zones, *, on_saved=None, suggested_count=None,
                           suggested_units=None, inline_token=None, component_name=None):
    tr = host.tr_static
    if tuple(str(zone["name"]) for zone in zones) != tuple(source.zones):
        raise ValueError("RGB_INVENTORY_CHANGED")
    zone = next((zone for zone in zones if zone["name"] == zone_name), None)
    if zone is None:
        raise ValueError("RGB_ZONE_MISSING")
    stable_id = host.openrgb_stable_ids[source.index]
    stored = host.rgb_zone_configurations.get(stable_id, {})
    values = next((value for key, value in stored.items() if key.casefold() == zone_name.casefold()), {})
    initial = values.get("units", 0) * values.get("leds_per_unit", 0) or int(zone["current"])
    if suggested_count is not None:
        # Do not silently clamp model totals or write a different physical size.
        header_configuration(zones, stored, zone_name, suggested_count)
        initial = suggested_count
    if (suggested_units is not None and
            (type(suggested_units) is not int or not 1 <= suggested_units <= 64)):
        raise ValueError("RGB_UNIT_COUNT")
    saved = False
    log_argb_zones(host, source, zones, "inspect", stored)
    dialog = QDialog(host)
    dialog.setWindowTitle(f'{tr("ARGB-Anschluss")} · {source.name} · {zone_name}')
    dialog.setMinimumWidth(570)
    root = QVBoxLayout(dialog)
    context = QLabel(f'{tr("Komponente")}: {component_name or (gpu.name if gpu is not None else source.name)}')
    context.setObjectName("argbEditedComponent")
    context.setTextFormat(Qt.TextFormat.PlainText)
    context.setWordWrap(True)
    root.addWidget(context)
    tabs = QTabWidget()
    root.addWidget(tabs)
    basic = QWidget()
    tabs.addTab(basic, tr("LEDs"))
    layout = QVBoxLayout(basic)
    note = QLabel(tr("Die LED-Anzahl ist manuell; OHC erkennt die physische Länge nicht. Nur dieser Anschluss wird geändert."))
    note.setWordWrap(True)
    layout.addWidget(note)
    layout.addWidget(QLabel(tr("LED-Anzahl am ARGB-Anschluss ändern")))
    count = QSpinBox()
    count.setObjectName("argbLedCount")
    if max(1, int(zone["minimum"])) > min(512, int(zone["maximum"])):
        raise ValueError("RGB_HEADER_UNAVAILABLE")
    count.setRange(max(1, int(zone["minimum"])), min(512, int(zone["maximum"])))
    count.setValue(initial)
    layout.addWidget(count)
    layout.addWidget(QLabel(tr("LED-Index für Sichttest (ab 1)")))
    index = QSpinBox()
    index.setObjectName("argbTestIndex")
    index.setRange(1, count.value())
    count.valueChanged.connect(lambda value: index.setMaximum(value))
    layout.addWidget(index)
    test = QPushButton(tr("Eine LED testen"))
    layout.addWidget(test)
    warning = QLabel(tr("Sichttest: Nur die gewählte LED oder Zone leuchtet weiß; andere OHC-LEDs werden schwarz. Beim Schließen kehrt das Design zurück."))
    warning.setWordWrap(True)
    layout.addWidget(warning)
    from .led_topology_editor import LedTopologyEditor
    units = suggested_units or values.get("units", 1) or 1
    topology = LedTopologyEditor(host, source, zone_name, count, index, units,
                                 fan_units=suggested_units)
    tabs.addTab(topology, tr("LED-Verlauf"))
    buttons = QDialogButtonBox()
    save = buttons.addButton(tr("Speichern"), QDialogButtonBox.ButtonRole.AcceptRole)
    buttons.addButton(tr("Abbrechen"), QDialogButtonBox.ButtonRole.RejectRole)
    buttons.rejected.connect(dialog.reject)
    root.addWidget(buttons)
    preview = HeaderPreview(host)

    def configuration():
        # The spatial path is the stronger source for an existing fan bank.
        # Releases before .121 could flatten the matching zone to 1 x N while
        # leaving e.g. the 3-ring path intact. Saving once repairs it to 3 x N.
        path_units = topology.values()["units"] if topology.group.isChecked() else None
        return header_configuration(zones, stored, zone_name, count.value(), path_units)

    def save_count():
        nonlocal saved
        try:
            configuration_value = configuration()
        except (TypeError, ValueError) as exc:
            host.show_error(tr("Der OpenRGB-Zonenbericht war nicht gültig.") + f" ({exc})")
            return
        if not topology.commit():
            tabs.setCurrentWidget(topology)
            return
        host.rgb_zone_configurations[stable_id] = configuration_value
        remember_headers(host, stable_id, [zone_name])
        log_argb_zones(host, source, zones, "save", configuration_value, target=zone_name)
        host.openrgb_sdk_ready_devices.discard(stable_id)
        if on_saved is not None:
            on_saved(count.value())
        host.save_rgb_workspace()
        host.rebuild_rgb_workspace()
        saved = True
        dialog.accept()

    def test_led():
        if preview.pending or getattr(host, "rgb_manual_write_active", False):
            return
        if not getattr(host, "openrgb_server_reachable", True) or getattr(host, "openrgb_engine_crash_quarantined", False):
            host.show_error(tr("Die eigene RGB-Engine muss erreichbar sein."))
            return
        if not host.openrgb_write_enabled:
            host.show_error(tr("Bitte zuerst die RGB-Hardwaresteuerung aktivieren."))
            return
        if host.openrgb_external_server_detected or (gpu is not None and host.openrgb_device_conflict(gpu)) or host.openrgb_device_conflict(source):
            return
        try:
            sizes = configured_zone_sizes(source.zones, configuration())
            colors = ["000000"] * sum(sizes)
            offset = sum(sizes[:source.zones.index(zone_name)])
            colors[offset + index.value() - 1] = "ffffff"
            commands = isolated_test_commands(host, source, zone_name, gpu=gpu)
            commands.append(host.openrgb_client.sdk_color_command(source.index, colors, len(colors), direct=True, zone_sizes=sizes))
        except (OpenRGBError, TypeError, ValueError) as exc:
            host.show_error(tr("Der OpenRGB-Zonenbericht war nicht gültig.") + f" ({exc})")
            return
        host.stop_openrgb_effect(tr("Eine LED testen"))
        preview.start()
        test.setEnabled(False)
        values, pixel_value = configuration(), index.value()
        log_argb_zones(host, source, zones, "pixel-test-request", values, target=zone_name, pixel=pixel_value)
        def finished(ok):
            log_argb_zones(host, source, zones, "pixel-test-sdk-ok" if ok else "pixel-test-sdk-failed", values, target=zone_name, pixel=pixel_value)
            preview.complete(ok)
            from shiboken6 import isValid
            if isValid(test): test.setEnabled(ok and getattr(host, "openrgb_server_reachable", True))
        host.run_rgb_command_sequence(commands, f'{tr("Eine LED testen")} · {zone_name} · {pixel_value}', finished=finished)

    save.clicked.connect(save_count)
    test.clicked.connect(test_led)
    from modules.pc_case_profiles.v1_5.inline_editor import present_editor
    if getattr(host, "case_inspector", None) is not None:
        dialog.finished.connect(lambda _result: preview.close(saved))
        present_editor(host, dialog, token=inline_token)
        return
    try:
        dialog.exec()
    finally:
        preview.close(saved)
