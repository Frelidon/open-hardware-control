#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded JSON helpers for local user-created PC layout profiles."""

from __future__ import annotations

import json
import re
import time


def _clean_string_map(raw: object, *, values_max: int = 96) -> dict[str, str]:
    if not isinstance(raw, dict) or not raw:
        return {}
    result: dict[str, str] = {}
    for raw_key, raw_value in list(raw.items())[:512]:
        key, value = str(raw_key)[:96], str(raw_value)[:values_max]
        if key and value and not any(ord(char) < 32 for char in key + value):
            result[key] = value
    return result


def normalize_hardware_snapshot(raw: object) -> dict[str, object]:
    """Validate the settings-only hardware topology embedded in a PC profile.

    Loading this data changes no RGB, fan or GPU value.  Stable device/header
    identifiers deliberately fail closed when the corresponding hardware is
    absent instead of falling back to another controller.
    """

    if not isinstance(raw, dict) or not raw:
        return {}
    from rgb_devices import normalize_device_aliases, normalize_zone_configurations
    from modules.rgb_studio.v1_15.fan_profiles import normalize_profiles
    from modules.rgb_studio.v1_15.gpu_routing import normalize_gpu_routes
    from modules.rgb_studio.v1_15.led_topology import DIRECTIONS, normalize_path
    from modules.rgb_studio.v1_15.slot_routes import normalize_slot_routes

    routes = normalize_slot_routes(raw.get("slot_routes", {}))
    fan_profiles = normalize_profiles(raw.get("fan_profiles", {}))
    zone_configurations = normalize_zone_configurations(raw.get("zone_configurations", {}))
    gpu_routes = normalize_gpu_routes(raw.get("gpu_routes", {}))

    led_paths: dict[str, dict[str, dict[str, object]]] = {}
    source_paths = raw.get("led_paths", {})
    if isinstance(source_paths, dict):
        for source, zones in list(source_paths.items())[:512]:
            if (not isinstance(source, str) or not source.startswith("openrgb:")
                    or len(source) > 96 or not isinstance(zones, dict)):
                continue
            clean_zones: dict[str, dict[str, object]] = {}
            for zone, value in list(zones.items())[:64]:
                clean = normalize_path(value)
                if (isinstance(zone, str) and 0 < len(zone) <= 96 and clean is not None
                        and not any(ord(char) < 32 for char in zone)):
                    movement = value.get("direction", "local") if isinstance(value, dict) else "local"
                    clean["direction"] = movement if movement in {"local", *DIRECTIONS} else "local"
                    clean_zones[zone] = clean
            if clean_zones:
                led_paths[source] = clean_zones

    manual_headers: dict[str, list[str]] = {}
    source_headers = raw.get("manual_headers", {})
    if isinstance(source_headers, dict):
        for source, names in list(source_headers.items())[:512]:
            if not isinstance(source, str) or len(source) > 96 or not isinstance(names, list):
                continue
            clean_names = list(dict.fromkeys(
                name for name in names[:64]
                if isinstance(name, str) and 0 < len(name) <= 96
                and not any(ord(char) < 32 for char in name)
            ))
            if clean_names:
                manual_headers[source] = clean_names

    selected_devices = raw.get("selected_devices", [])
    selected = list(dict.fromkeys(
        device for device in selected_devices[:512]
        if isinstance(device, str) and 0 < len(device) <= 96
        and not any(ord(char) < 32 for char in device)
    )) if isinstance(selected_devices, list) else []
    direction = str(raw.get("case_direction", "local"))
    result: dict[str, object] = {
        "slot_routes": routes,
        "fan_profiles": fan_profiles,
        "zone_configurations": zone_configurations,
        "gpu_routes": gpu_routes,
        "led_paths": led_paths,
        "manual_headers": manual_headers,
        "group_assignments": _clean_string_map(raw.get("group_assignments", {}), values_max=48),
        "device_aliases": normalize_device_aliases(raw.get("device_aliases", {})),
        "selected_devices": selected,
        "pwm_assignments": _clean_string_map(raw.get("pwm_assignments", {}), values_max=96),
        "case_direction": direction if direction in {"local", *DIRECTIONS} else "local",
    }
    # Presence distinguishes a current profile with deliberately empty roles
    # from a legacy profile whose roles may be recovered from its own slots.
    if "aio_channels" in raw:
        roles = _clean_string_map(raw.get("aio_channels", {}))
        pump, radiator = roles.get("pump", ""), roles.get("radiator", "")
        result["aio_channels"] = {
            "pump": pump,
            "radiator": radiator if radiator != pump else "",
        }
    return result


def new_profile_id(name: object) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(name).casefold()).strip("-")[:36] or "pc"
    return f"user-{slug}-{int(time.time())}"


def decode_profiles(raw: object) -> list[dict[str, object]]:
    try:
        source = json.loads(str(raw or "[]"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return []
    if not isinstance(source, list):
        return []
    result: list[dict[str, object]] = []
    used: set[str] = set()
    for item in source[:32]:
        if not isinstance(item, dict):
            continue
        ident = str(item.get("id", ""))[:64]
        name = " ".join(str(item.get("name", "")).split())[:64]
        case_id = str(item.get("case_id", ""))[:64]
        slots = item.get("slots", [])
        groups = item.get("groups", [])
        if not ident.startswith("user-") or ident in used or not name or not isinstance(slots, list):
            continue
        used.add(ident)
        profile = {
            "id": ident,
            "name": name,
            "case_id": case_id,
            "cooling_visual": str(item.get("cooling_visual", "auto"))
            if str(item.get("cooling_visual", "auto")) in {"auto", "aio", "air"} else "auto",
            "slots": slots[:64],
            "groups": groups[:32] if isinstance(groups, list) else [],
        }
        hardware = normalize_hardware_snapshot(item.get("hardware", {}))
        if hardware:
            profile["hardware"] = hardware
        result.append(profile)
    return result


def encode_profiles(profiles: list[dict[str, object]]) -> str:
    return json.dumps(decode_profiles(json.dumps(profiles, ensure_ascii=False)), ensure_ascii=False, sort_keys=True)
