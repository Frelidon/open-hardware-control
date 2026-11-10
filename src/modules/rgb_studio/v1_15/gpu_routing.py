#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure bounded GPU controller/zone routing and native-mode selection."""

from openrgb_integration import best_native_mode_for_effect
from rgb_effects import render_hex_frame


def normalize_gpu_routes(value: object) -> dict[str, dict[str, str]]:
    """Read legacy controller-only routes without inventing a zone."""
    if not isinstance(value, dict):
        return {}
    result = {}
    for key, raw in list(value.items())[:512]:
        source = raw if isinstance(raw, str) else raw.get("controller") if isinstance(raw, dict) else None
        zone = raw.get("zone", "") if isinstance(raw, dict) else ""
        if (isinstance(key, str) and isinstance(source, str) and isinstance(zone, str)
                and key.startswith("openrgb:") and (source.startswith("openrgb:") or source == "")
                and len(key) <= 96 and len(source) <= 96 and len(zone) <= 96
                and key != source and (source or not zone) and not any(ord(char) < 32 for char in zone)):
            result[key] = {"controller": source, "zone": zone.strip()}
    return result


def route_source(route):
    return route.get("controller", "") if isinstance(route, dict) else route if isinstance(route, str) else ""


def route_zone(route, source):
    name = route.get("zone", "") if isinstance(route, dict) else ""
    return next((zone for zone in source.zones if name and zone.casefold() == name.casefold()), "")


def gpu_mode_for_effect(device, effect_id, stable_ids, routes, direct_devices):
    """Hand an external-capable GPU to the selected OHC Direct signal.

    The Sapphire switch is only a hardware input selector; it does not identify
    which physical mainboard header its cable uses.  A saved route is still used
    for spatial/colour grouping, but it must not be required merely to keep the
    card in External Control while OHC owns at least one Direct source.
    """
    if device.device_type.casefold() != "gpu" and "sapphire" not in device.name.casefold():
        return best_native_mode_for_effect(device, effect_id)
    gpu_id = stable_ids.get(device.index, "")
    route = normalize_gpu_routes(routes).get(gpu_id, {})
    source_id = route_source(route)
    routed_source_ready = source_id and any(
        source.supports_direct and stable_ids.get(source.index) == source_id
        and (not route.get("zone") or route_zone(route, source))
        for source in direct_devices
    )
    if routed_source_ready or (not route and any(source.supports_direct for source in direct_devices)):
        external = next((mode for mode in device.modes
                         if mode.casefold() == "external control"), "")
        if external:
            return external
    return best_native_mode_for_effect(device, effect_id)


def gpu_zone_overrides(host, stable_id, source, config):
    """Reuse the existing explicit, selected and conflict-free GPU authority."""
    overrides = {}
    for gpu in host.openrgb_devices:
        if gpu.device_type.casefold() != "gpu" and "sapphire" not in gpu.name.casefold(): continue
        gpu_id = host.openrgb_stable_ids.get(gpu.index)
        route = host.rgb_gpu_routes.get(gpu_id, {})
        zone = route_zone(route, source)
        if (route_source(route) == stable_id and zone and gpu_id in host.rgb_selected_devices
                and not host.openrgb_device_conflict(gpu)):
            group = host.rgb_group_assignments.get(gpu_id, "ungrouped")
            overrides[zone] = host.rgb_group_effect_configs.get(group, config)
    # An external-only GPU component can use a reported ARGB header without
    # enabling the intentionally disabled native GPU detector. Its settings-only
    # block route (or retained exact GPU route) is the authority, never its name.
    if (source.supports_direct and stable_id in host.rgb_selected_devices
            and not host.openrgb_device_conflict(source)):
        from .slot_routes import slot_routes
        explicit = slot_routes(host)
        retained = normalize_gpu_routes(host.rgb_gpu_routes)
        native_ids = {host.openrgb_stable_ids.get(device.index) for device in host.openrgb_devices
                      if device.device_type.casefold() == "gpu" or "sapphire" in device.name.casefold()}
        external = {}
        for slot in getattr(host, "rgb_layout_slots", ()):
            if slot.position != "gpu" or any(device_id in native_ids for device_id in slot.device_ids):
                continue
            key = slot.slot_id or slot.position
            routes = ([explicit[key]] if key in explicit else
                      [retained[device_id] for device_id in slot.device_ids if device_id in retained])
            if len(routes) != 1:
                continue  # No implicit partner when cached declarations disagree.
            route = routes[0]
            zone = route_zone(route, source)
            if route_source(route) == stable_id and zone:
                external.setdefault(zone, []).append(
                    host.rgb_group_effect_configs.get(slot.group_id, config))
        overrides.update({zone: choices[0] for zone, choices in external.items()
                          if len(choices) == 1 and zone not in overrides})
    return overrides


def render_zone_frame(config, count, sizes, zones, overrides, elapsed, *, paths=None, direction="local", rectangles=None, gpu_zones=(), sync_counts=None, gpu_motion=None, gpu_elapsed=None, gpu_roles=None):
    """Only routed controllers use independent physical strip coordinates."""
    if sizes is None:
        return render_hex_frame(config, count, elapsed)
    if len(sizes) != len(zones) or sum(sizes) != count:
        raise ValueError("RGB_ZONE_SHAPE")
    colors = []
    from .led_topology import render_physical_frame
    from .gpu_strip_sampling import render_gpu_strip_frame
    for name, size in zip(zones, sizes):
        if size:
            rect, horizontal = (rectangles or {}).get(name, ((0., 0., 1., 1.), True))
            try:
                renderer = render_gpu_strip_frame if name in gpu_zones else render_physical_frame
                extra = dict(sync_count=(sync_counts or {}).get(name), tuning=gpu_motion,
                             role=(gpu_roles or {}).get(name, "gpu")) if name in gpu_zones else {}
                zone_elapsed = gpu_elapsed if name in gpu_zones and gpu_elapsed is not None else elapsed
                colors.extend(renderer(overrides.get(name, config), size, zone_elapsed,
                              (paths or {}).get(name), direction, rect, horizontal, **extra))
            except ValueError:
                # Never disguise a GPU renderer failure as the older sharp
                # generic effect; the worker reports the affected device.
                if name in gpu_zones:
                    raise
                # A changed count cannot invalidate other physical headers.
                colors.extend(render_hex_frame(overrides.get(name, config), size, elapsed))
    return colors
