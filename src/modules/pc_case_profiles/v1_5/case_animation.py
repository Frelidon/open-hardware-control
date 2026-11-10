# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only LED frames for GPU, support and RAM in the case schematic."""
from __future__ import annotations

import time

from rgb_effects import render_hex_frame
from modules.rgb_studio.v1_15.gpu_motion import configured_count, load
from modules.rgb_studio.v1_15.gpu_strip_sampling import render_gpu_strip_frame
from modules.rgb_studio.v1_15.gpu_support_sync import enabled as support_sync_enabled
from modules.rgb_studio.v1_15.gpu_routing import gpu_zone_overrides
from modules.rgb_studio.v1_15.led_topology import render_physical_frame
from modules.rgb_studio.v1_15.led_topology_store import case_rectangles, direction
from modules.gpu_profiles.v1_0.visual_catalog import resolve_gpu_visual
from .topology_labels import display_header_targets

FAN_ROLES = {"top", "front", "side", "bottom", "rear"}


def _preview_elapsed(host):
    """Return the independent UI clock, with a legacy-fixture fallback."""
    started = float(getattr(host, "openrgb_effect_started", 0.0) or 0.0)
    if started > 0.0:
        return max(0.0, time.monotonic() - started), True
    return max(0.0, float(getattr(host, "rgb_last_sent_elapsed", 0.0) or 0.0)), False


def _gpu_identity(host, slot):
    """Return the assigned GPU id and its full OpenRGB board name."""

    routes = getattr(host, "rgb_gpu_routes", {})
    devices = {getattr(item, "index", -1): item for item in getattr(host, "openrgb_devices", ())}
    stable_ids = getattr(host, "openrgb_stable_ids", {})
    by_id = {stable_ids.get(index, ""): item for index, item in devices.items()}
    gpu_id = next((device_id for device_id in slot.device_ids if device_id in routes), "")
    if not gpu_id:
        gpu_id = next((
            device_id for device_id in slot.device_ids
            if str(getattr(by_id.get(device_id), "device_type", "")).casefold() == "gpu"
        ), "")
    device = by_id.get(gpu_id)
    return gpu_id, str(getattr(device, "name", "") or slot.name)


def build_specs(host, slots, paths):
    """Use reported routes and declared counts; an absent path stays schematic."""
    specs = {}
    rectangles = {}
    for slot in slots[:64]:
        if slot.position not in {"gpu", "gpu-support", "ram", *FAN_ROLES}:
            continue
        gpu_id, gpu_name = _gpu_identity(host, slot) if slot.position == "gpu" else ("", "")
        gpu_visual = resolve_gpu_visual(slot.gpu_visual, gpu_name) if slot.position == "gpu" else None
        targets = []
        seen = set()
        for source, zone, _gpu in display_header_targets(host, slot):
            controller = host.openrgb_stable_ids.get(source.index, "")
            key = controller, zone
            if key in seen:
                continue
            seen.add(key)
            count = configured_count(host, controller, zone)
            if count:
                targets.append((controller, zone, count))
        # A natively controlled GPU can report only one logical OpenRGB LED and
        # has no routed Direct header.  Keep a presentation-only strip for its
        # known cooler profile; hardware output remains owned by the existing
        # GPU writer.
        native_gpu_preview = bool(
            slot.position == "gpu" and gpu_id and gpu_visual is not None
            and gpu_visual.lighting != "none" and not targets
        )
        if (not targets and not native_gpu_preview) or sum(item[2] for item in targets) > 512:
            continue
        if slot.position == "gpu-support" and len(targets) != 1:
            continue
        if slot.position == "gpu" and targets and len(targets) != 1:
            continue
        key = slot.slot_id or slot.position
        # A reported single header is sufficient for a schematic preview.
        # A physical LED path refines that preview, but its absence must not
        # hide otherwise configured fan lighting. Multiple headers remain
        # ambiguous; never choose the first one as a fan's electrical route.
        if slot.position in FAN_ROLES and len(targets) != 1:
            continue
        path = paths.get(key)
        bounds = None
        if slot.position in FAN_ROLES and path and path[0].get("direction", direction(host)) != "local":
            controller, zone, _count = targets[0]
            if controller not in rectangles:
                rectangles[controller] = case_rectangles(host, controller)
            bounds = rectangles[controller].get(zone)
        specs[key] = {"role": slot.position, "targets": tuple(targets),
                      "path": path, "gpu_id": gpu_id,
                      "rectangle": bounds[0] if bounds else (0., 0., 1., 1.),
                      "horizontal": bounds[1] if bounds else slot.position in {"top", "bottom"},
                      "gpu_lighting": gpu_visual.lighting if gpu_visual else "",
                      "preview_count": targets[0][2] if slot.position == "gpu" and targets else (
                          30 if gpu_visual and gpu_visual.lighting in {
                              "edge-strip", "mixed", "indirect", "logo"
                          } else max(1, getattr(gpu_visual, "fan_count", 1))
                      )}
    if support_sync_enabled(host):
        gpu = next((item for item in specs.values() if item["role"] == "gpu"), None)
        support = next((item for item in specs.values() if item["role"] == "gpu-support"), None)
        if gpu and support and support["targets"]:
            gpu_count = gpu["targets"][0][2] if gpu["targets"] else gpu["preview_count"]
            count = max(gpu_count, support["targets"][0][2])
            gpu["sync_count"] = support["sync_count"] = count
    return specs


def frame(host, spec):
    """Return only colours already selected for a running OHC Direct design."""
    if not getattr(host, "openrgb_effect_active", False):
        return ()
    assignments = getattr(host, "openrgb_effect_assignments", {})
    # The case view is a presentation clock, not hardware readback.  Tying it
    # to the last completed USB/I2C write makes the local preview stutter when
    # a controller is slow or the SDK worker coalesces frames.  Use the same
    # monotonic start time as the renderer so every 16 ms paint advances even
    # while the hardware path applies only the newest queued frame.
    elapsed, independent_clock = _preview_elapsed(host)
    gpu_elapsed = elapsed if independent_clock else max(
        0.0, float(getattr(host, "rgb_gpu_visual_elapsed", elapsed) or 0.0)
    )
    gpu_id = spec.get("gpu_id")
    if spec["role"] == "gpu" and gpu_id:
        if gpu_id not in getattr(host, "rgb_selected_devices", set()):
            return ()
        group = getattr(host, "rgb_group_assignments", {}).get(gpu_id, "ungrouped")
        fallback = next((assignments.get(controller) for controller, _zone, _count in spec["targets"]
                         if controller in assignments), None)
        config = getattr(host, "rgb_group_effect_configs", {}).get(group, fallback)
        if config is None:
            return ()
        # Thirty presentation samples make a long cooler light guide visibly
        # fluid even when OpenRGB exposes the board as one logical LED.
        return tuple(render_gpu_strip_frame(
            config, int(spec.get("preview_count", 30)),
            gpu_elapsed,
            path=spec.get("path", (None,))[0] if spec.get("path") else None,
            sync_count=spec.get("sync_count"),
            tuning=getattr(host, "rgb_gpu_motion_preview", None) or load(host),
            role="gpu",
        ))
    if not any(controller in assignments for controller, _zone, _count in spec["targets"]):
        return ()
    if spec["role"] == "ram":
        return tuple(color for controller, _zone, count in spec["targets"]
                     if controller in assignments
                     for color in render_hex_frame(assignments[controller], count, elapsed))
    controller, _zone, count = spec["targets"][0]
    if controller not in assignments:
        return ()
    config = assignments[controller]
    if spec["role"] == "gpu":
        source = next((device for device in getattr(host, "openrgb_devices", ())
                       if host.openrgb_stable_ids.get(device.index) == controller), None)
        if source is not None:
            config = gpu_zone_overrides(host, controller, source, config).get(_zone, config)
    if spec["role"] == "gpu-support" and spec.get("sync_count"):
        from modules.rgb_studio.v1_15.gpu_support_sync import pair
        linked = pair(host, config)
        gpu = next((device_id for device_id in getattr(host, "rgb_gpu_routes", {})
                    if device_id in getattr(host, "rgb_selected_devices", set())), "")
        group = getattr(host, "rgb_group_assignments", {}).get(gpu, "ungrouped")
        config = linked["config"] if linked else getattr(host, "rgb_group_effect_configs", {}).get(group, config)
    path = spec.get("path")
    if spec["role"] in FAN_ROLES:
        return tuple(render_physical_frame(
            config, count, elapsed, path[0] if path else None, direction(host),
            rect=spec.get("rectangle", (0., 0., 1., 1.)),
            horizontal=bool(spec.get("horizontal", True)),
        ))
    return tuple(render_gpu_strip_frame(
        config, count, gpu_elapsed,
        path=path[0] if path else None, sync_count=spec.get("sync_count"),
        tuning=getattr(host, "rgb_gpu_motion_preview", None) or load(host),
        role="support" if spec["role"] == "gpu-support" else "gpu",
    ))
