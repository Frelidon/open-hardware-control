# SPDX-License-Identifier: GPL-3.0-or-later
"""Lease only selected ENE devices out of the existing SDK stream; no I/O."""


def validated_exclusions(host, keys):
    selected = set(host.rgb_selected_devices)
    return frozenset(host.openrgb_stable_ids.get(d.index) for d in host.openrgb_devices
                     if host.is_ene_dram_device(d)
                     and host.openrgb_stable_ids.get(d.index) in selected
                     and host.openrgb_stable_ids.get(d.index) in keys)


def begin(host, keys):
    lease = validated_exclusions(host, keys)
    host.rgb_reclaim_stream_exclusions = lease
    host.rgb_reclaim_drain_sequence = getattr(host, "openrgb_worker_frame_sequence", 0)
    return lease


def release(host, lease):
    # A reset/exit/new intent may already have invalidated this exact lease.
    if getattr(host, "rgb_reclaim_stream_exclusions", None) is lease:
        host.rgb_reclaim_stream_exclusions = frozenset()
        host.openrgb_sdk_ready_devices.difference_update(lease)
