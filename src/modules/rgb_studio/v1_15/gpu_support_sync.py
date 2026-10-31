# SPDX-License-Identifier: GPL-3.0-or-later
"""Settings-only pairing of explicitly wired, selected GPU and support strips."""
from .gpu_routing import gpu_zone_overrides, route_source, route_zone
from .slot_routes import slot_routes
from .led_topology_store import paths, direction

KEY = "rgb_studio/gpu_support_sync_v1"


def enabled(host):
    settings = getattr(host, "settings", None)
    raw = settings.value(KEY, True) if settings is not None else False
    return raw is True or isinstance(raw, str) and raw.casefold() == "true"


def _count(host, controller, zone):
    raw = host.rgb_zone_configurations.get(controller, {}).get(zone, {})
    units, leds = raw.get("units"), raw.get("leds_per_unit")
    if type(units) is not int or type(leds) is not int or units < 1 or leds < 1: return None
    return units * leds if units * leds <= 4096 else None


def pair(host, default_config):
    if not enabled(host): return None
    supports = [s for s in host.rgb_layout_slots if s.slot_id == "gpu-support"]
    if len(supports) != 1: return None
    support_route = slot_routes(host).get("gpu-support", {})
    support_id = route_source(support_route)
    selected = host.rgb_selected_devices
    source = next((d for d in host.openrgb_devices if host.openrgb_stable_ids.get(d.index) == support_id
                   and d.supports_direct and support_id in selected and not host.openrgb_device_conflict(d)), None)
    if source is None: return None
    support_zone = route_zone(support_route, source)
    support_count = _count(host, support_id, support_zone)
    if support_count is None: return None
    candidates = []
    for device in host.openrgb_devices:
        device_id = host.openrgb_stable_ids.get(device.index)
        if not device.supports_direct or device_id not in selected or host.openrgb_device_conflict(device): continue
        for zone, config in gpu_zone_overrides(host, device_id, device, default_config).items():
            count = _count(host, device_id, zone)
            if count is not None and (device_id, zone) != (support_id, support_zone):
                candidates.append((device_id, zone, config, count))
    if len(candidates) != 1: return None  # Never guess a partner with multiple GPUs.
    gpu_id, gpu_zone, config, count = candidates[0]
    declared = paths(host)
    if any(declared.get(d, {}).get(z, {}).get("kind") == "ring"
           for d, z in ((gpu_id, gpu_zone), (support_id, support_zone))): return None
    return dict(gpu=(gpu_id, gpu_zone), support=(support_id, support_zone),
                count=max(count, support_count), config=config, direction=direction(host))
