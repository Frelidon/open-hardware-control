#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Per-zone and PC-block entry points; never infer a GPU's electrical route."""

import re
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget
from .gpu_led_editor import configure_argb_header
from .gpu_routing import normalize_gpu_routes, route_source, route_zone
from .slot_routes import resolve_slot_route
from .slot_route_editor import choose_slot_header


def build_zone_test_controls(host, source, zone, uniform_button, unit_spin, led_spin):
    panel = QWidget()
    layout = QHBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    pixel = QPushButton(host.tr_static("Eine LED testen"))
    pixel.setMinimumHeight(34)
    uniform_button.setMinimumHeight(34)
    layout.addWidget(uniform_button)
    layout.addWidget(pixel)
    def saved(count):
        unit_spin.setValue(1)
        led_spin.setValue(count)
    pixel.clicked.connect(lambda _checked=False: configure_argb_header(
        host, source, zone, on_saved=saved))
    return panel


def slot_header_targets(host, slot):
    explicit = resolve_slot_route(host, slot)
    if explicit is not None:
        return explicit
    devices = {host.openrgb_stable_ids.get(d.index): d for d in host.openrgb_devices}
    targets = []
    routes = normalize_gpu_routes(host.rgb_gpu_routes)
    for device_id in slot.device_ids:
        device = devices.get(device_id)
        if device is None:
            # The Ubuntu-safe inventory deliberately excludes the native
            # Sapphire detector. A saved GPU route remains a physical header
            # declaration, not permission to rediscover or invent that GPU.
            if slot.position == "gpu":
                route = routes.get(device_id, {})
                source = devices.get(route_source(route))
                if source is not None and source.supports_direct and route_zone(route, source):
                    targets.append((source, route_zone(route, source), None))
            continue
        if device.supports_direct:
            targets.extend((device, name, None) for name in device.zones)
        else:
            route = routes.get(device_id, {})
            source = devices.get(route_source(route))
            if source is not None and source.supports_direct and route_zone(route, source):
                targets.append((source, route_zone(route, source), device))
    # A written header name is a hint only within an already assigned controller.
    def canonical(value):
        return re.sub(r"[_\s]", "", re.sub(r"_V2", "", value, flags=re.I)).casefold()
    matched = [t for t in targets if canonical(t[1]) == canonical(slot.connection)]
    return matched or targets


def edit_slot_header(host, slot_id, *, suggested_count=None, suggested_units=None, route_only=False):
    slot = next((s for s in host.rgb_layout_slots if (s.slot_id or s.position) == slot_id), None)
    if slot is None:
        host.show_error(host.tr_static("Bitte zuerst einen Block in der PC-Ansicht anklicken."))
        return
    if slot.position in {"top", "front", "side", "bottom", "rear"}:
        # The component model is the authority for the number of physical
        # fans.  Do not make users enter the same bank size again in the LED
        # path editor.
        suggested_units = suggested_units if suggested_units is not None else slot.count
        if suggested_count is None and hasattr(host, "settings"):
            from .fan_profiles import declared_total, profile_for_slot
            suggested_count = declared_total(profile_for_slot(host, slot), slot.count)
    kwargs = {}
    if suggested_count is not None:
        kwargs["suggested_count"] = suggested_count
    if suggested_units is not None:
        kwargs["suggested_units"] = suggested_units
    targets = slot_header_targets(host, slot)
    if not route_only and len(targets) == 1:
        source, zone, gpu = targets[0]
        configure_argb_header(host, source, zone, gpu=gpu, component_name=slot.name, **kwargs)
        return
    choose_slot_header(host, slot, targets, **kwargs)


def build_slot_led_button(host, slot_id=None, *, led_count=None, unit_count=None):
    button = QPushButton(host.tr_static("LED-Anzahl am ARGB-Anschluss ändern"))
    button.setObjectName("rgbSlotLedEditor")
    button.setMinimumHeight(38)
    button.clicked.connect(lambda _checked=False: edit_slot_header(
        host, slot_id if slot_id is not None else host.rgb_layout_selected_slot_id,
        suggested_count=led_count() if led_count else None,
        suggested_units=unit_count() if unit_count else None))
    return button


def build_slot_route_button(host, slot_id=None):
    button = QPushButton(host.tr_static("ARGB-Anschluss ändern"))
    button.setObjectName("rgbSlotRouteEditor")
    button.setMinimumHeight(38)
    button.clicked.connect(lambda _checked=False: edit_slot_header(
        host, slot_id if slot_id is not None else host.rgb_layout_selected_slot_id,
        route_only=True))
    return button


def build_case_gpu_setup_button(host, slot_id=None):
    button = QPushButton(host.tr_static("Grafikkarte: Steuerweg und LEDs"))
    button.setObjectName("caseGpuSetup")
    button.setMinimumHeight(38)
    button.clicked.connect(lambda _checked=False: open_case_gpu_setup(host, slot_id))
    return button


def external_gpu_setup_slot(host):
    """Use an explicit selection or one unambiguous GPU component, never a name guess."""
    slots = [slot for slot in getattr(host, "rgb_layout_slots", ()) if slot.position == "gpu"]
    selected = getattr(host, "rgb_layout_selected_slot_id", "")
    return next((slot for slot in slots if (slot.slot_id or slot.position) == selected),
                slots[0] if len(slots) == 1 else None)


def open_case_gpu_setup(host, slot_id=None):
    slot_id = slot_id if slot_id is not None else getattr(host, "rgb_layout_selected_slot_id", "")
    slot = next((item for item in host.rgb_layout_slots
                 if (item.slot_id or item.position) == slot_id), None)
    ids = set(slot.device_ids) if slot is not None and slot.position == "gpu" else set()
    target = next((device for device in host.openrgb_devices
                   if host.openrgb_stable_ids.get(device.index) in ids
                   and (device.device_type.casefold() == "gpu" or "sapphire" in device.name.casefold())), None)
    if target is None and slot is not None and slot.position == "gpu":
        edit_slot_header(host, slot.slot_id or slot.position, route_only=True)
        return
    host.configure_gpu_lighting(target)
