# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared blackout prefix for white per-header LED and fan-zone sight tests."""
from .gpu_routing import route_source, route_zone


def commands(host, source, zone, *, gpu=None):
    stable_id = host.openrgb_stable_ids[source.index]
    linked = []
    if gpu is not None:
        linked.append(gpu)
    for device in getattr(host, 'openrgb_devices', ()):
        device_id = host.openrgb_stable_ids.get(device.index, '')
        route = getattr(host, 'rgb_gpu_routes', {}).get(device_id, {})
        if (device not in linked and not device.supports_direct
                and device_id in getattr(host, 'rgb_selected_devices', ())
                and route_source(route) == stable_id and route_zone(route, source) == zone
                and any(mode.casefold() == 'external control' for mode in device.modes)
                and not host.openrgb_device_conflict(device)):
            linked.append(device)
    excluded = {stable_id, *(host.openrgb_stable_ids.get(device.index, '') for device in linked)}
    blackout = getattr(host, 'build_rgb_device_test_commands', None)
    prefix = blackout('', exclude_ids=excluded, only_selected=True)[0] if callable(blackout) else []
    for device in linked:
        prefix.append(host.openrgb_client.native_mode_command(
            device.index, 'External Control', ['ffffff'], 100))
    return prefix
