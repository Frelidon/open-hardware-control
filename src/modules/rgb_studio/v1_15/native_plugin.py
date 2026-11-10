"""Local transport for the OpenRGB native OHC plugin.

The transport deliberately uses a latest-frame-wins queue.  A slow controller
must never make the Qt animation timer wait for an older frame.
"""

from __future__ import annotations

import json
import os
import socket
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


DEFAULT_SOCKET = "/tmp/ohc-openrgb-native.sock"
MAX_MESSAGE_BYTES = 2_000_000


def default_socket_path() -> str:
    runtime = os.environ.get("XDG_RUNTIME_DIR", "").strip()
    return str(Path(runtime) / "ohc-openrgb-native.sock") if runtime else DEFAULT_SOCKET


@dataclass(frozen=True)
class NativePluginResult:
    ok: bool
    detail: str = ""
    data: dict[str, object] = field(default_factory=dict)


class NativeOpenRGBPluginClient:
    """Small, bounded JSON-lines client for the in-process OpenRGB plugin."""

    def __init__(self, path: str | None = None, timeout: float = 0.12):
        self.path = path or default_socket_path()
        self.timeout = max(0.02, min(1.0, float(timeout)))
        self._socket: socket.socket | None = None
        self.generation = 0

    @property
    def available(self) -> bool:
        return bool(self.path and Path(self.path).exists())

    def connect(self) -> bool:
        if self._socket is not None:
            return True
        if not self.available:
            return False
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect(self.path)
            self._socket = sock
            return True
        except OSError:
            self.close()
            return False

    def close(self) -> None:
        sock, self._socket = self._socket, None
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass

    def _send(self, payload: dict[str, object], *, control: bool = False) -> NativePluginResult:
        if not self.connect():
            return NativePluginResult(False, "native OpenRGB plugin is not reachable")
        raw = (json.dumps(payload, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
        if len(raw) > MAX_MESSAGE_BYTES:
            return NativePluginResult(False, "native frame exceeds message limit")
        try:
            assert self._socket is not None
            self._socket.settimeout(2.0 if control else self.timeout)
            self._socket.sendall(raw)
            reply = b""
            while b"\n" not in reply and len(reply) <= 8192:
                chunk = self._socket.recv(8192)
                if not chunk:
                    raise OSError("plugin closed socket")
                reply += chunk
            message = json.loads(reply.split(b"\n", 1)[0].decode("utf-8"))
            if not isinstance(message, dict) or message.get("ok") is False:
                return NativePluginResult(False, str(message.get("error", "plugin rejected request")))
            return NativePluginResult(True, str(message.get("detail", "")), message)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self.close()
            return NativePluginResult(False, str(exc))
        finally:
            if self._socket is not None:
                self._socket.settimeout(self.timeout)

    def start(self, fps: int = 60) -> NativePluginResult:
        result = self._send({"op": "start", "fps": max(1, min(120, int(fps)))}, control=True)
        if result.ok:
            self.generation = int(result.data.get("generation", 0))
        return result

    def frame(self, frame_id: int, devices: Iterable[dict[str, object]]) -> NativePluginResult:
        return self._send({"op": "frame", "id": int(frame_id), "devices": list(devices)})

    def stop(self) -> NativePluginResult:
        # A mode handoff must wait for an already executing controller write.
        # Only stop may use a longer timeout; animation frames stay bounded.
        try:
            return self._send({"op": "stop"}, control=True)
        finally:
            self.close()


def record_native_status(host, result: NativePluginResult, assignments, now: float) -> None:
    """Record completed API submissions, never mistake a queue ACK for a write."""
    if result.data.get("generation") != host.native_openrgb_plugin.generation:
        return
    by_index = {device.index: stable_id for stable_id, _config, device in assignments}
    ready = set()
    for raw in result.data.get("devices", ()):
        if not isinstance(raw, dict) or raw.get("device") not in by_index:
            continue
        stable_id = by_index[raw["device"]]
        if raw.get("error") or not int(raw.get("submitted", 0)):
            continue
        ready.add(stable_id)
        metrics = host.openrgb_worker_metrics.setdefault(stable_id, {})
        sequence = int(raw.get("id", 0))
        if sequence != metrics.get("last_frame_id"):
            times = metrics.setdefault("success_times", [])
            times.append(now)
            times[:] = [stamp for stamp in times[-300:] if now - stamp <= 5.0]
            metrics.update(last_frame_id=sequence, last_success=now,
                           last_duration_ms=float(raw.get("duration_ms", 0)),
                           submitted_hz=float(raw.get("submitted_hz", 0)), errors=0)
        host.openrgb_sdk_ready_devices.add(stable_id)
    if ready == set(by_index.values()) and ready and host.rgb_pending_design_snapshot is not None:
        host.acknowledge_rgb_design_part("direct", host.rgb_pending_design_snapshot)
    if now >= getattr(host, "openrgb_native_metrics_log_at", 0.0):
        host.openrgb_native_metrics_log_at = now + 10.0
        for raw in result.data.get("devices", ()):
            if isinstance(raw, dict) and raw.get("device") in by_index:
                host.log_message(
                    f"RGB-NATIVE: device={raw['device']} · submitted_hz={float(raw.get('submitted_hz', 0)):.1f}"
                    f" · submit_ms={float(raw.get('duration_ms', 0)):.2f}"
                    f" · replaced={raw.get('replaced', 0)} · errors={raw.get('errors', 0)}"
                    " · stage=OpenRGB-API · physical_readback=unavailable"
                )

