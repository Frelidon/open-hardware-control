# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded, local-only LACT JSON socket client and reversible tuning preview."""
from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
import socket
from typing import Any


class LactError(RuntimeError):
    pass


class LactClient:
    def __init__(self, path: Path = Path("/run/lactd.sock"), timeout: float = 1.5):
        self.path = Path(path)
        self.timeout = max(0.2, min(240.0, float(timeout)))

    def request(self, command: str, args: dict[str, Any] | None = None) -> Any:
        if command not in {
            "ping", "system_info", "list_devices", "device_info", "device_stats", "device_clocks_info",
            "get_gpu_config", "set_gpu_config", "confirm_pending_config", "enable_overdrive",
        }:
            raise LactError("Unsupported LACT command")
        payload = {"command": command}
        if args is not None:
            payload["args"] = args
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.settimeout(self.timeout)
                connection.connect(str(self.path))
                connection.sendall(json.dumps(payload, separators=(",", ":")).encode() + b"\n")
                response = bytearray()
                while b"\n" not in response:
                    chunk = connection.recv(65536)
                    if not chunk:
                        break
                    response.extend(chunk)
                    if len(response) > 2 * 1024 * 1024:
                        raise LactError("LACT response exceeded the size limit")
            decoded = json.loads(bytes(response).split(b"\n", 1)[0])
        except (OSError, TimeoutError, UnicodeError, ValueError) as exc:
            raise LactError(f"LACT connection failed: {type(exc).__name__}") from exc
        if not isinstance(decoded, dict) or decoded.get("status") != "ok":
            detail = decoded.get("data") if isinstance(decoded, dict) else "Invalid response"
            raise LactError(f"LACT rejected {command}: {str(detail)[:240]}")
        return decoded.get("data")

    def devices(self) -> list[dict[str, Any]]:
        rows = self.request("list_devices")
        if not isinstance(rows, list):
            raise LactError("LACT returned an invalid GPU list")
        return [row for row in rows if isinstance(row, dict) and isinstance(row.get("id"), str)]

    def config(self, gpu_id: str) -> dict[str, Any]:
        value = self.request("get_gpu_config", {"id": gpu_id})
        # LACT returns JSON null until the first per-GPU override is saved.
        # An empty config is the documented default profile, not a socket error.
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise LactError("LACT returned an invalid GPU configuration")
        return value

    def overdrive_enabled(self) -> bool | None:
        info = self.request("system_info")
        if not isinstance(info, dict):
            raise LactError("LACT returned invalid system information")
        value = info.get("amdgpu_overdrive_enabled")
        return value if isinstance(value, bool) else None

    def prepare_overdrive(self) -> None:
        """Ask LACT to prepare its own boot configuration; a reboot is separate."""
        self.require_supported_version()
        if self.overdrive_enabled() is not False:
            raise LactError("LACT does not report Overdrive as disabled")
        self.request("enable_overdrive")

    def stats(self, gpu_id: str) -> dict[str, Any]:
        value = self.request("device_stats", {"id": gpu_id})
        if not isinstance(value, dict):
            raise LactError("LACT returned invalid GPU measurements")
        return value

    def clocks(self, gpu_id: str) -> dict[str, Any]:
        value = self.request("device_clocks_info", {"id": gpu_id})
        if not isinstance(value, dict):
            raise LactError("LACT returned invalid GPU clock information")
        return value

    def set_config(self, gpu_id: str, config: dict[str, Any]) -> float:
        self.require_supported_version()
        remaining = self.request("set_gpu_config", {"id": gpu_id, "config": config})
        if not isinstance(remaining, (int, float)) or not math.isfinite(remaining) or remaining <= 0:
            raise LactError("LACT did not provide a rollback deadline")
        return float(remaining)

    def pending(self, action: str) -> None:
        if action not in {"confirm", "revert"}:
            raise LactError("Invalid confirmation action")
        self.request("confirm_pending_config", {"command": action})

    @staticmethod
    def require_supported_version() -> None:
        """0.10.1 fixes known local authorization and snapshot issues."""
        from .version import require_supported_version
        require_supported_version()


TUNING_FIELDS = ("power_cap", "max_core_clock", "max_memory_clock", "gpu_clock_offset_0",
                 "fan_control_enabled", "fan_control_settings")


def config_equivalent(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    """Accept only LACT's omission of documented zero fan-hysteresis defaults."""
    if not isinstance(expected, dict) or not isinstance(actual, dict):
        return False
    left, right = deepcopy(expected), deepcopy(actual)
    fan_left, fan_right = left.pop("fan_control_settings", None), right.pop("fan_control_settings", None)
    if left != right:
        return False
    if not isinstance(fan_left, dict) or not isinstance(fan_right, dict):
        return fan_left == fan_right
    for fan in (fan_left, fan_right):
        fan.setdefault("spindown_delay_ms", 0)
        fan.setdefault("change_threshold", 0)
        curve = fan.get("curve")
        if isinstance(curve, dict):
            fan["curve"] = {str(key): value for key, value in curve.items()}
    return fan_left == fan_right


def clock_controls(baseline: dict[str, Any], clocks: dict[str, Any]) -> dict[str, tuple[int, int, int]]:
    """Use LACT's live AMD overdrive table when unset fields are omitted from config."""
    table = clocks.get("table")
    if not isinstance(table, dict) or table.get("type") != "amd":
        return {}
    value = table.get("value")
    if not isinstance(value, dict) or value.get("kind") != "rdna":
        return {}
    data = value.get("data")
    if not isinstance(data, dict):
        return {}
    limits = data.get("od_range")
    if not isinstance(limits, dict):
        return {}
    controls: dict[str, tuple[int, int, int]] = {}
    for field, limit_key, current_key in (
        ("max_core_clock", "sclk", "current_sclk_range"),
        ("max_memory_clock", "mclk", "current_mclk_range"),
    ):
        bounds, current = limits.get(limit_key), data.get(current_key)
        if not isinstance(bounds, dict) or not isinstance(current, dict):
            continue
        lower, upper = bounds.get("min"), bounds.get("max")
        original = baseline.get(field, current.get("max"))
        if all(isinstance(number, (int, float)) and not isinstance(number, bool)
               and math.isfinite(number) for number in (lower, upper, original)):
            low, high, initial = int(lower), int(upper), int(original)
            if 0 < low <= initial <= high:
                controls[field] = (initial, low, high)
    bounds = limits.get("sclk_offset")
    offsets = baseline.get("gpu_clock_offsets")
    saved = offsets.get("0", offsets.get(0)) if isinstance(offsets, dict) else None
    original = saved if saved is not None else data.get("sclk_offset")
    if isinstance(bounds, dict):
        lower, upper = bounds.get("min"), bounds.get("max")
        if all(isinstance(number, (int, float)) and not isinstance(number, bool)
               and math.isfinite(number) for number in (lower, upper, original)):
            low, high, initial = int(lower), int(upper), int(original)
            if low <= initial <= high:
                controls["gpu_clock_offset_0"] = (initial, low, high)
    return controls


def proposed_config(baseline: dict[str, Any], changes: dict[str, Any],
                    stats: dict[str, Any], clocks: dict[str, Any] | None = None) -> dict[str, Any]:
    """Change only documented LACT fields, bounded by current reported limits."""
    result = deepcopy(baseline)
    if not changes or set(changes) - set(TUNING_FIELDS):
        raise LactError("No supported tuning change selected")
    power = stats.get("power") if isinstance(stats.get("power"), dict) else {}
    controls = clock_controls(baseline, clocks or {})
    if "fan_control_settings" in changes:
        from .fan_profile import proposed_fan_settings, proposed_static_fan_settings
        requested = changes["fan_control_settings"]
        try:
            if isinstance(requested, dict) and requested.get("mode") == "static":
                if set(requested) != {"mode", "speed"}:
                    raise ValueError("Invalid static GPU fan fields")
                result["fan_control_settings"] = proposed_static_fan_settings(
                    baseline, requested["speed"], stats)
            elif isinstance(requested, (list, tuple)):
                points = tuple(tuple(point) for point in requested)
                result["fan_control_settings"] = proposed_fan_settings(baseline, points, stats)
            else:
                raise ValueError("Invalid GPU fan settings")
        except (ValueError, TypeError) as exc:
            raise LactError(f"Invalid GPU fan settings: {exc}") from exc
    for field, raw in changes.items():
        if field == "fan_control_settings":
            continue
        if field == "fan_control_enabled":
            if not isinstance(raw, bool):
                raise LactError("Invalid GPU fan setting")
            if raw and not isinstance(result.get("fan_control_settings"), dict):
                raise LactError("LACT has no verified GPU fan curve")
            result[field] = raw
            continue
        if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(raw):
            raise LactError(f"Invalid {field} value")
        value = float(raw)
        if field == "power_cap":
            lower, upper = power.get("cap_min"), power.get("cap_max")
            if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in (lower, upper)):
                raise LactError("LACT did not report power limits")
            if not float(lower) <= value <= float(upper):
                raise LactError("Power limit is outside the device range")
        elif field == "gpu_clock_offset_0":
            offsets = baseline.get("gpu_clock_offsets")
            control = controls.get(field)
            old = control[0] if control else (offsets.get("0", offsets.get(0)) if isinstance(offsets, dict) else None)
            if not isinstance(old, (int, float)):
                raise LactError("LACT did not report a GPU clock offset baseline")
            if control and not control[1] <= value <= control[2]:
                raise LactError("GPU clock offset is outside the LACT device range")
            if abs(value - float(old)) > 100:
                raise LactError("GPU clock offset change exceeds the 100 MHz trial bound")
            result["gpu_clock_offsets"] = deepcopy(offsets) if isinstance(offsets, dict) else {}
            key = "0" if not isinstance(offsets, dict) or "0" in offsets else 0
            result["gpu_clock_offsets"][key] = int(value)
            continue
        else:
            control = controls.get(field)
            old = control[0] if control else baseline.get(field)
            if not isinstance(old, (int, float)) or old <= 0:
                raise LactError(f"LACT did not report a baseline for {field}")
            if control and not control[1] <= value <= control[2]:
                raise LactError(f"{field} is outside the LACT device range")
            if abs(value - float(old)) > min(100.0, float(old) * 0.05):
                raise LactError(f"{field} change exceeds the 5%/100 MHz trial bound")
            value = int(value)
        result[field] = value
    if result == baseline:
        raise LactError("Tuning values have not changed")
    return result


def healthy_stats(stats: dict[str, Any]) -> tuple[bool, str]:
    """A short smoke check: daemon responds, readings are plausible, no throttle flag."""
    busy = stats.get("busy_percent")
    if busy is not None and (not isinstance(busy, (int, float)) or not 0 <= busy <= 100):
        return False, "LACT reported an implausible GPU load"
    throttles = stats.get("throttle_info")
    if isinstance(throttles, dict) and any(bool(value) for value in throttles.values()):
        return False, "LACT reported GPU throttling"
    if not isinstance(stats.get("temps"), dict) or not stats["temps"]:
        return False, "LACT did not report GPU temperatures"
    return True, "LACT measurements responded without a reported fault"
