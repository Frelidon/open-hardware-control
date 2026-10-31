#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded semantic ARGB diagnostics; never log every animation frame."""


def log_argb_zones(host, source, zones, operation, configuration=None, *, target="", pixel=None):
    logger = getattr(host, "log_message", None)
    if logger is None:
        return
    stored = configuration if configuration is not None else host.rgb_zone_configurations.get(
        host.openrgb_stable_ids.get(source.index), {})
    offset = 0
    for zone in zones[:64]:
        name = str(zone.get("name", ""))[:96]
        values = next((v for k, v in stored.items() if k.casefold() == name.casefold()), None)
        current = int(zone.get("current", 0))
        count = int(values["units"]) * int(values["leds_per_unit"]) if values else current
        declared = f'{values["units"]}x{values["leds_per_unit"]}={count}' if values else "unset"
        detail = f" · pixel_1based={pixel} · frame_0based={offset + pixel - 1}" if pixel is not None and name == target else ""
        logger(f"ARGB-DIAG: op={operation} · controller={source.name[:128]} · device_index={source.index} · zone={name}"
               f" · server_buffer={current} · declared={declared} · bounds={zone.get('minimum')}..{zone.get('maximum')}"
               f" · resizable={int(bool(zone.get('resizable', zone.get('minimum') != zone.get('maximum'))))}"
               f" · frame_offset={offset} · active={int(name == target)}{detail} · physical_readback=unavailable")
        offset += count


def log_effect_plan(host, source, config):
    from .effect_sampling import sampling_plan, motion_scale
    from .led_topology_store import paths
    logger = getattr(host, "log_message", None)
    if logger is None:
        return
    stable_id = host.openrgb_stable_ids.get(source.index)
    stored = host.rgb_zone_configurations.get(stable_id, {})
    declared_paths = paths(host).get(stable_id, {})
    for name in source.zones[:64]:
        values = next((v for k, v in stored.items() if k.casefold() == name.casefold()), None)
        if values is None:
            continue
        count = values["units"] * values["leds_per_unit"]
        path = next((v for k, v in declared_paths.items() if k.casefold() == name.casefold()), None)
        topology = ""
        if path is not None:
            layout = "Reihe" if path["kind"] == "line" else "Ring"
            topology = (f" · layout={layout} · led1={path['start']} · last={path['end']}"
                        f" · clockwise={path['clockwise']} · reverse_units={path.get('reverse_units', False)}"
                        f" · case_direction={path.get('direction', 'local')}")
        logger(f"ARGB-DIAG: op=effect-plan · controller={source.name[:128]} · zone={name[:96]}"
               f" · declared={values['units']}x{values['leds_per_unit']}={count} · effect={config.effect_id}"
               f" · area_samples={sampling_plan(count) if count else 0} · motion_scale={motion_scale(count) if count else 0:.3f}"
               f"{topology} · target_hz=25 · measured_hz=transfer-status · physical_readback=unavailable")
    from .gpu_routing import gpu_zone_overrides
    from .gpu_support_sync import pair
    from .gpu_strip_sampling import strip_plan, strip_clock, TEMPORAL_SAMPLES
    from .gpu_motion import load as load_gpu_motion
    candidates = gpu_zone_overrides(host, stable_id, source, config)
    linked = pair(host, config)
    sync_counts = {}
    roles = {}
    if linked:
        for role, (controller, zone) in (("gpu", linked["gpu"]), ("support", linked["support"])):
            if controller == stable_id:
                candidates[zone] = linked["config"]
                sync_counts[zone] = linked["count"]
                roles[zone] = role
    declared = declared_paths
    for name, effect in candidates.items():
        values = stored.get(name)
        if (values is None or effect.effect_id not in {"spinner", "comet"}
                or declared.get(name, {}).get("kind") == "ring"): continue
        count = values["units"] * values["leds_per_unit"]
        if not count: continue
        reference = sync_counts.get(name, count)
        plan = strip_plan(effect, reference, load_gpu_motion(host), roles.get(name, "gpu"))
        clock = strip_clock(effect, reference, load_gpu_motion(host))
        logger(f"ARGB-DIAG: op=strip-motion-plan · controller={source.name[:128]} · zone={name[:96]}"
               f" · renderer=gpu-open-strip · count={count} · clock_count={reference} · effect={effect.effect_id}"
               f" · cycles_per_s={clock['rate'] / clock['cycle']:.4f} · leading_fraction={plan['leading']:.3f}"
               f" · tail_fraction={plan['tail']:.3f} · time_samples={TEMPORAL_SAMPLES} · blend=cubic · open_ends=1"
               f" · support_sync={int(name in sync_counts)} · target_hz=25 · physical_readback=unavailable")
