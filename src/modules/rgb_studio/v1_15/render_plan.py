# SPDX-License-Identifier: GPL-3.0-or-later
"""Transfer bounded pure effect plans to the existing sole-writer SDK worker."""
from dataclasses import asdict, replace
import math
from rgb_effects import RGBEffectConfig
from .gpu_routing import gpu_zone_overrides, render_zone_frame
from .gpu_support_sync import pair
from .led_topology_store import paths, direction, case_rectangles
from .gpu_motion import load as load_gpu_motion


def build(host, stable_id, device, config, elapsed):
    overrides = gpu_zone_overrides(host, stable_id, device, config)
    gpu_zones, sync_counts = set(overrides), {}
    gpu_roles = {zone: 'gpu' for zone in overrides}
    linked = pair(host, config)
    if linked is not None:
        for role, (controller, zone) in (('gpu', linked['gpu']), ('support', linked['support'])):
            if controller == stable_id:
                overrides[zone] = linked['config']
                gpu_zones.add(zone); sync_counts[zone] = linked['count']
                gpu_roles[zone] = role
    declared = paths(host).get(stable_id, {})
    movement = direction(host)
    calibration = getattr(host, 'rgb_gpu_calibration_targets', None)
    visible = sorted(calibration.get(stable_id, ())) if isinstance(calibration, dict) else None
    if visible is not None:
        for zone in visible:
            if zone in overrides:
                overrides[zone] = replace(overrides[zone], primary='0000ff', secondary='ffffff')
    return dict(schema=1, config=asdict(config.normalized()), elapsed=elapsed,
                zones=list(device.zones), overrides={z: asdict(c.normalized()) for z, c in overrides.items()},
                paths=declared, direction=movement, gpu_zones=sorted(gpu_zones), sync_counts=sync_counts,
                rectangles=case_rectangles(host, stable_id) if any(
                    path.get('direction', movement) != 'local' for path in declared.values()) else {},
                gpu_motion=getattr(host, 'rgb_gpu_motion_preview', None) or load_gpu_motion(host), gpu_roles=gpu_roles,
                gpu_elapsed=getattr(host, 'rgb_gpu_visual_elapsed', elapsed),
                calibration_visible_zones=visible)


def render(raw, count, sizes):
    try:
        return _render(raw, count, sizes)
    except (KeyError, TypeError, AttributeError, OverflowError) as exc:
        raise ValueError('RENDER_PLAN') from exc


def _render(raw, count, sizes):
    if not isinstance(raw, dict) or raw.get('schema') != 1: raise ValueError('RENDER_SCHEMA')
    if type(count) is not int or not 1 <= count <= 4096: raise ValueError('RENDER_COUNT')
    elapsed = raw.get('elapsed')
    if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0: raise ValueError('RENDER_TIME')
    zones = raw.get('zones')
    if not isinstance(zones, list) or len(zones) > 4096 or any(not isinstance(z, str) or len(z) > 512 for z in zones):
        raise ValueError('RENDER_ZONES')
    if sizes is not None and (not isinstance(sizes, list) or any(type(s) is not int or not 0 <= s <= 4096 for s in sizes)):
        raise ValueError('RENDER_SHAPE')
    config = RGBEffectConfig(**raw['config']).normalized()
    overrides = raw.get('overrides', {})
    if not isinstance(overrides, dict) or len(overrides) > 4096: raise ValueError('RENDER_OVERRIDES')
    overrides = {z: RGBEffectConfig(**c).normalized() for z, c in overrides.items() if z in zones}
    for key in ('paths', 'rectangles', 'sync_counts'):
        value = raw.get(key, {})
        if not isinstance(value, dict) or len(value) > 64: raise ValueError('RENDER_MAPPING')
    if not isinstance(raw.get('gpu_zones', []), list) or len(raw.get('gpu_zones', [])) > 64:
        raise ValueError('RENDER_GPU_ZONES')
    if any(type(v) is not int or not 1 <= v <= 4096 for v in raw.get('sync_counts', {}).values()):
        raise ValueError('RENDER_SYNC_COUNT')
    roles = raw.get('gpu_roles', {})
    if not isinstance(roles, dict) or len(roles) > 64 or any(
            zone not in zones or role not in {'gpu', 'support'} for zone, role in roles.items()):
        raise ValueError('RENDER_GPU_ROLES')
    from .gpu_motion import normalize as normalize_gpu_motion
    tuning = raw.get('gpu_motion')
    if tuning is not None and normalize_gpu_motion(tuning) != tuning: raise ValueError('RENDER_GPU_MOTION')
    gpu_elapsed = raw.get('gpu_elapsed', elapsed)
    if type(gpu_elapsed) not in (int, float) or not math.isfinite(gpu_elapsed) or gpu_elapsed < 0:
        raise ValueError('RENDER_GPU_TIME')
    colors = render_zone_frame(config, count, sizes, zones, overrides, elapsed,
                             paths=raw.get('paths'), direction=raw.get('direction', 'local'),
                             rectangles=raw.get('rectangles'), gpu_zones=raw.get('gpu_zones', ()),
                             sync_counts=raw.get('sync_counts'), gpu_motion=tuning,
                             gpu_elapsed=gpu_elapsed, gpu_roles=roles)
    visible = raw.get('calibration_visible_zones')
    if visible is None:
        return colors
    if not isinstance(visible, list) or len(visible) > 64 or any(
            not isinstance(zone, str) or zone not in zones for zone in visible):
        raise ValueError('RENDER_CALIBRATION_ZONES')
    if sizes is None or len(sizes) != len(zones) or sum(sizes) != count:
        raise ValueError('RENDER_CALIBRATION_SHAPE')
    offset = 0
    for zone, size in zip(zones, sizes):
        if zone not in visible:
            colors[offset:offset + size] = ['000000'] * size
        offset += size
    return colors
