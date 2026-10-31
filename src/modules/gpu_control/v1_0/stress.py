# SPDX-License-Identifier: GPL-3.0-or-later
"""GPU load selection and conservative LACT telemetry limits."""
from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Any


def benchmark_command(available: dict[str, str], *, size: str = "1600x900",
                      duration_seconds: int = 10,
                      presentation: str = "maximized",
                      output_size: str = "1920x1080") -> tuple[str, list[str]]:
    """Prefer a fill-heavy Vulkan scene with a validated render size."""
    output_match = re.fullmatch(r"([0-9]{3,5})x([0-9]{3,5})", output_size)
    if (size not in {"1600x900", "3840x2160", "7680x4320"}
            or not 5 <= duration_seconds <= 150
            or presentation not in {"maximized", "minimized", "fullscreen"}
            or output_match is None
            or not 640 <= int(output_match.group(1)) <= 16384
            or not 480 <= int(output_match.group(2)) <= 16384):
        return "", []
    vkmark = str(available.get("vkmark") or "")
    if Path(vkmark).is_absolute() and Path(vkmark).name == "vkmark":
        gamescope = str(available.get("gamescope") or "")
        scene = ["--present-mode", "immediate", "--run-forever", "-b",
                 f"shading:shading=phong:duration={duration_seconds}.0"]
        if Path(gamescope).is_absolute() and Path(gamescope).name == "gamescope":
            render_width, render_height = size.split("x", 1)
            output_width, output_height = output_size.split("x", 1)
            args = ["-w", render_width, "-h", render_height,
                    "-W", output_width, "-H", output_height,
                    "-S", "fit", "-F", "linear", "--expose-wayland", "--",
                    vkmark, "--fullscreen", *scene]
            if os.environ.get("XDG_SESSION_TYPE") == "wayland":
                args.extend(("--winsys", "wayland"))
            return gamescope, args
        args = (["--fullscreen"] if presentation == "fullscreen" else ["--size", size]) + scene
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            args.extend(("--winsys", "wayland"))
        return vkmark, args
    glmark = str(available.get("glmark2") or "")
    if Path(glmark).is_absolute() and Path(glmark).name.startswith("glmark2"):
        return glmark, ["--off-screen", "--run-forever", "--benchmark", "refract"]
    return "", []


def benchmark_gpu_environment(gpu_id: str, executable: str) -> dict[str, str]:
    """Select the LACT GPU by PCI vendor/device, never by an unstable ordinal."""
    match = re.match(r"^([0-9a-fA-F]{4}):([0-9a-fA-F]{4})-", gpu_id)
    if match is None:
        raise ValueError("LACT GPU ID has no PCI vendor/device identifier")
    vendor_device = f"{match.group(1).lower()}:{match.group(2).lower()}"
    if Path(executable).name in {"vkmark", "gamescope"}:
        return {"MESA_VK_DEVICE_SELECT": vendor_device + "!"}
    return {"DRI_PRIME": vendor_device}


def command_uses_vkmark(executable: str, arguments: list[str]) -> bool:
    return Path(executable).name == "vkmark" or any(Path(argument).name == "vkmark" for argument in arguments)


def vkmark_reported_gpu(output: str) -> str | None:
    """Read vkmark's actual device IDs from its normal startup banner."""
    vendor = re.search(r"^\s*Vendor ID:\s*0x([0-9a-fA-F]{4})\s*$", output, re.MULTILINE)
    device = re.search(r"^\s*Device ID:\s*0x([0-9a-fA-F]{1,4})\s*$", output, re.MULTILINE)
    if vendor is None or device is None:
        return None
    return f"{vendor.group(1).lower()}:{device.group(1).lower().zfill(4)}"


def load_sample(stats: dict[str, Any]) -> tuple[bool, str, float]:
    """Fail closed on missing/implausible temperature or LACT throttle reports."""
    temps = stats.get("temps")
    if not isinstance(temps, dict):
        return False, "LACT meldet keine GPU-Temperaturen", 0.0
    edge = temps.get("edge")
    edge_value = edge.get("current") if isinstance(edge, dict) else edge
    critical = edge.get("crit") if isinstance(edge, dict) else None
    if not isinstance(edge_value, (int, float)) or isinstance(edge_value, bool) or not 0 <= edge_value <= 125:
        return False, "GPU-Temperatur ist nicht plausibel", 0.0
    limit = min(90.0, float(critical) - 15.0) if isinstance(critical, (int, float)) else 90.0
    if edge_value >= limit:
        return False, f"GPU-Temperatur {edge_value:.0f} °C erreicht die Testgrenze {limit:.0f} °C", 0.0
    busy = stats.get("busy_percent")
    if not isinstance(busy, (int, float)) or isinstance(busy, bool) or not 0 <= busy <= 100:
        return False, "LACT meldet keine plausible GPU-Auslastung", 0.0
    throttles = stats.get("throttle_info")
    if isinstance(throttles, dict) and any(bool(value) for value in throttles.values()):
        return False, "LACT meldet GPU-Drosselung", float(busy)
    return True, "", float(busy)
