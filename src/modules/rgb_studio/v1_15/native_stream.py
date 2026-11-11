# SPDX-License-Identifier: GPL-3.0-or-later
"""Native stream priority and confirmed, exclusive SDK fallback handoff."""

from dataclasses import dataclass
import time

from .native_plugin import record_native_status
from .render_plan import render
from openrgb_integration import OpenRGBError


@dataclass
class NativeRecovery:
    failures: int = 0
    retry_at: float = 0.0
    starting: bool = False
    draining: bool = False
    stop_failures: int = 0


def start_native_stream(host, fps: int) -> bool:
    """Prefer native; an ambiguous START must drain before SDK takes ownership."""
    state = host.rgb_native_recovery = NativeRecovery()
    plugin = host.native_openrgb_plugin
    if not plugin.available:
        host.log_message(f"RGB-NATIVE: unavailable · socket={plugin.path} · SDK fallback")
        return False
    result = plugin.start(fps)
    if not result.ok:
        state.starting = True
        state.failures = 1
        state.retry_at = time.monotonic() + 0.25
        host.log_message(f"RGB-NATIVE: START retry pending · {result.detail}")
    else:
        host.log_message(f"RGB-NATIVE: active · target_hz={fps} · latest-frame-wins")
    return True


def _drain_before_fallback(host, state, now: float) -> bool:
    result = host.native_openrgb_plugin.stop()
    if not result.ok:
        state.stop_failures += 1
        state.retry_at = now + min(5.0, 0.5 * 2 ** min(state.stop_failures, 4))
        if state.stop_failures == 1:
            host.log_message(f"RGB-NATIVE: STOP unconfirmed · SDK blocked · {result.detail}")
        return True
    host.openrgb_native_plugin_active = False
    # A native Direct ACK cannot prepare a new SDK connection's controller state.
    host.openrgb_sdk_ready_devices.clear()
    host.log_message("RGB-NATIVE: STOP confirmed after repeated failures · SDK fallback")
    return False


def send_native_frame(host, assignments, elapsed: float, now: float, fps: int) -> bool:
    """True means native still owns output, including a bounded recovery wait."""
    state = host.rgb_native_recovery
    if now < state.retry_at:
        return True
    if state.draining:
        return _drain_before_fallback(host, state, now)
    if state.starting:
        result = host.native_openrgb_plugin.start(fps)
        if result.ok:
            state.starting = False
    else:
        try:
            devices = []
            for stable_id, config, device in assignments:
                count, sizes = host.openrgb_device_write_shape(device)
                payload = host.rgb_worker_render_payload(stable_id, device, config, count, sizes, elapsed)
                colors = render(payload["render_plan"], count, list(sizes) if sizes is not None else None)
                devices.append({"device": device.index, "name": device.name,
                                "mode": "Direct", "colors": colors})
        except (OpenRGBError, ValueError, KeyError, TypeError) as exc:
            # Invalid render data is not evidence that the native transport failed.
            state.retry_at = now + 0.5
            host.mark_rgb_design_transfer_failed(str(exc)[:160])
            return True
        result = host.native_openrgb_plugin.frame(host.openrgb_worker_frame_sequence + 1, devices)
        if result.ok:
            host.openrgb_worker_frame_sequence += 1
            host.openrgb_worker_coalesced_frames = 0
            record_native_status(host, result, assignments, now)
            host.update_openrgb_performance_status()
    if result.ok:
        if state.failures:
            host.log_message("RGB-NATIVE: recovered · native transport retained")
        state.failures = 0
        state.retry_at = 0.0
        return True
    state.failures += 1
    state.draining = state.failures >= 3
    state.retry_at = now + 0.25 * state.failures
    host.log_message(f"RGB-NATIVE: transient failure {state.failures}/3 · {result.detail}")
    return True
