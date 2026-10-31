# SPDX-License-Identifier: GPL-3.0-or-later
"""One-time owner-confirmed wiring corrections; no hardware/PWM operations."""
import json
import re
from dataclasses import replace
from .argb_store import remember_headers
from .fan_profiles import remember_profile
from .slot_routes import KEY as ROUTES_KEY, slot_routes

KEY = "rgb_studio/flori_wiring_20260913_v1"
COUNTS_KEY = KEY + "/counts"
# Physical SYS_FAN labels are notes, not internal pwmN identities.
WIRING = {
    "fans-front": ("A1", 2, 8, "SYS-FAN4"),
    "fans-psu-shroud": ("B7", 3, 8, "SYS-FAN6"),
    "fan-rear": ("B8", 1, 8, "SYS-FAN1"),
    "radiator-top": ("A8", 3, 10, ""),
    "gpu-support": ("B6", 1, 12, ""),
}


def canonical(value):
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


def migrate_personal_wiring(host):
    if str(host.settings.value("rgb_studio/layout_profile", "")) != "flori":
        return False
    if not host.is_thermalright_cooling():
        return False  # Never route NZXT's integrated radiator to Airgoo.
    candidates = [d for d in host.openrgb_devices
                  if "airgoo" in canonical(d.name) and "drgb16" in canonical(d.name)
                  and d.supports_direct and len(d.zones) <= 64]
    if len(candidates) != 1:
        return False
    source = candidates[0]
    source_id = host.openrgb_stable_ids.get(source.index, "")
    zones = {canonical(n): n for n in source.zones}
    if (not isinstance(source_id, str) or not source_id.startswith("openrgb:") or len(source_id) > 96
            or any(ord(c) < 32 or ord(c) == 127 for c in source_id)
            or any(not isinstance(n, str) or not 1 <= len(n) <= 96
                   or any(ord(c) < 32 or ord(c) == 127 for c in n) for n in source.zones)
            or len(zones) != len(source.zones)
            or not all("channel" + w[0].lower() in zones for w in WIRING.values())):
        return False  # Missing/ambiguous inventory must not invent a port.
    changed = False
    slots = {s.slot_id: s for s in host.rgb_layout_slots}
    if not host.settings.value(KEY, False):
        routes = slot_routes(host)
        if not all(key in slots for key in WIRING) or len(set(routes) | set(WIRING)) > 128:
            return False
        updated = []
        for slot in host.rgb_layout_slots:
            if slot.slot_id not in WIRING:
                updated.append(slot)
                continue
            port, count, leds, pwm = WIRING[slot.slot_id]
            zone = zones["channel" + port.lower()]
            routes[slot.slot_id] = dict(controller=source_id, zone=zone)
            note = f"RGB-Hub {port}" + (f" · PWM {pwm}" if pwm else "")
            note += f" · {count}× {leds} LEDs"
            name = re.sub(r"\b\d+ LEDs\b", f"{leds} LEDs", slot.name)
            updated.append(replace(slot, name=name, count=count, connection=note))
            if slot.slot_id != "gpu-support":
                remember_profile(host, slot.slot_id, dict(
                    brand="Thermalright" if slot.slot_id == "radiator-top" else "TZMRIT",
                    model="Levita Vision 360 · Radiator" if slot.slot_id == "radiator-top" else "Interstellar-V2",
                    color="black", leds_per_fan=leds))
        host.rgb_layout_slots = updated
        host.settings.setValue(ROUTES_KEY, json.dumps(routes, ensure_ascii=False))
        host.settings.setValue(KEY, True)
        changed = True
    if not host.settings.value(COUNTS_KEY, False):
        configuration = host.rgb_zone_configurations.get(source_id, {})
        # Do not turn a complete server buffer into a partial guessed shape.
        if configuration and all(n in configuration for n in source.zones):
            configuration = {n: dict(v) for n, v in configuration.items()}
            pins = []
            for port, count, leds, _pwm in WIRING.values():
                zone = zones["channel" + port.lower()]
                configuration[zone] = dict(units=count, leds_per_unit=leds)
                pins.append(zone)
            host.rgb_zone_configurations[source_id] = configuration
            remember_headers(host, source_id, pins)
            host.openrgb_sdk_ready_devices.discard(source_id)
            host.settings.setValue(COUNTS_KEY, True)
            changed = True
    if changed:
        host.save_rgb_workspace()
        host.settings.sync()
        for key, (port, count, leds, pwm) in WIRING.items():
            host.log_message(f"ARGB-DIAG: op=personal-wiring-migration · block={key} · controller={source_id} · "
                             f"zone={zones['channel' + port.lower()]} · declared={count}x{leds}={count * leds} · "
                             f"pwm_note={pwm or '—'} · settings-only · physical_readback=unavailable")
    return changed
