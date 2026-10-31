# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit block wiring, independent of design/position/PWM snapshots."""
import json

KEY = "rgb_studio/slot_argb_routes_v1"


def normalize_slot_routes(raw):
    if not isinstance(raw, dict):
        return {}
    result = {}
    for key, route in list(raw.items())[:128]:
        if not isinstance(key, str) or not key or len(key) > 96 or not isinstance(route, dict):
            continue
        source, zone = route.get("controller"), route.get("zone")
        if not isinstance(source, str) or not isinstance(zone, str):
            continue
        if len(source) > 96 or len(zone) > 96 or any(ord(c) < 32 for c in key + source + zone):
            continue
        if (source.startswith("openrgb:") and zone.strip()) or (source == zone == ""):
            result[key] = {"controller": source, "zone": zone.strip()}
    return result


def slot_routes(host):
    settings = getattr(host, "settings", None)
    if settings is None:
        return {}
    try:
        return normalize_slot_routes(json.loads(str(settings.value(KEY, "{}"))))
    except (TypeError, ValueError):
        return {}


def reported_sources(host):
    """Reported Direct inventory for settings-only wiring, even while offline.

    Hardware actions independently enforce reachability and ownership. An
    unavailable engine must not erase all choices in the wiring dropdown.
    """
    return [d for d in host.openrgb_devices
            if d.supports_direct and d.zones
            and str(host.openrgb_stable_ids.get(d.index, "")).startswith("openrgb:")
            and not getattr(host, "openrgb_wiring_conflict", host.openrgb_device_conflict)(d)]


def resolve_slot_route(host, slot):
    key = slot.slot_id or slot.position
    routes = slot_routes(host)
    if key not in routes:
        return None  # Legacy assignments remain readable only without an override.
    route = routes[key]
    # A block such as the RAM bank may represent several directly addressable
    # OpenRGB devices.  A legacy one-device route must not narrow that bank to
    # one DIMM; the device_ids list below is the complete authority instead.
    if len(slot.device_ids) > 1 and route["controller"] in slot.device_ids:
        return None
    source = next((d for d in host.openrgb_devices
                   if host.openrgb_stable_ids.get(d.index) == route["controller"]
                   and d.supports_direct and route["zone"] in d.zones), None)
    if source is None:
        return []  # Removed devices/headers must not silently select another port.
    gpu = next((d for d in host.openrgb_devices
                if host.openrgb_stable_ids.get(d.index) in slot.device_ids
                and (d.device_type.casefold() == "gpu" or "sapphire" in d.name.casefold())
                and any(m.casefold() == "external control" for m in d.modes)), None)
    return [(source, route["zone"], gpu)]


def remember_slot_route(host, key, controller, zone):
    """Settings-only commit; revalidate live inventory before accepting a choice."""
    slot = next((s for s in host.rgb_layout_slots if (s.slot_id or s.position) == key), None)
    if slot is None:
        return False
    route = normalize_slot_routes({key: {"controller": controller, "zone": zone}})
    if key not in route:
        return False
    if controller and not any(host.openrgb_stable_ids.get(d.index) == controller
                              and zone in d.zones for d in reported_sources(host)):
        return False
    routes = slot_routes(host)
    if key not in routes and len(routes) >= 128:
        return False
    routes[key] = route[key]
    # A GPU's physical sync route must agree with its newly chosen block header.
    gpu_route = False
    for d in host.openrgb_devices:
        gpu_id = host.openrgb_stable_ids.get(d.index)
        if (gpu_id in slot.device_ids and (d.device_type.casefold() == "gpu" or "sapphire" in d.name.casefold())
                and any(m.casefold() == "external control" for m in d.modes)):
            host.rgb_gpu_routes[gpu_id] = route[key].copy()
            gpu_route = True
    if gpu_route:
        # GPU setup already owns its authoritative routing; don't create a rival.
        routes.pop(key, None)
        host.select_gpu_route_sources()
    elif slot.position == "gpu" and controller:
        # Explicit external-only GPU wiring selects the physical controller,
        # never a fabricated native GPU id and never hardware write authority.
        selected = getattr(host, "rgb_selected_devices", None)
        if isinstance(selected, set):
            selected.add(controller)
    host.settings.setValue(KEY, json.dumps(routes, ensure_ascii=False))
    host.save_rgb_workspace()
    host.settings.sync()
    host.rebuild_rgb_workspace()
    if hasattr(host, "append_log"):
        host.append_log(f"ARGB: block-route-save · block={key} · controller={controller or '—'} · zone={zone or '—'} · settings-only")
    return True
