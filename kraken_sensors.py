#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only Linux temperature sensors shared by the GUI and LCD streamer."""

from __future__ import annotations

from pathlib import Path


def read_amd_cpu_temperature(
    hwmon_root: Path = Path("/sys/class/hwmon"),
) -> tuple[float | None, str]:
    """Read k10temp, preferring Tctl and then Tdie."""
    for hwmon in sorted(hwmon_root.glob("hwmon*")):
        try:
            if (hwmon / "name").read_text(encoding="ascii").strip() != "k10temp":
                continue
            candidates: list[tuple[int, Path, str]] = []
            for input_file in hwmon.glob("temp*_input"):
                label_file = input_file.with_name(input_file.name.replace("_input", "_label"))
                label = (
                    label_file.read_text(encoding="utf-8").strip()
                    if label_file.exists()
                    else input_file.stem
                )
                priority = 0 if label == "Tctl" else 1 if label == "Tdie" else 2
                candidates.append((priority, input_file, label))
            for _priority, input_file, label in sorted(candidates):
                value = float(input_file.read_text(encoding="ascii").strip()) / 1000.0
                if 0.0 < value < 125.0:
                    return value, label
        except (OSError, ValueError):
            continue
    return None, "k10temp nicht gefunden"


def read_amd_gpu_temperature(
    drm_root: Path = Path("/sys/class/drm"),
) -> tuple[float | None, str]:
    """Read amdgpu temperature, preferring the card with the most VRAM.

    AM5 systems can expose both an integrated GPU and a dedicated Radeon.
    Selecting by ``mem_info_vram_total`` keeps the LCD focused on the dGPU
    without depending on unstable card numbers.
    """
    cards: list[tuple[int, int, float, str]] = []
    for card in sorted(drm_root.glob("card[0-9]*")):
        device = card / "device"
        try:
            vendor_file = device / "vendor"
            if (
                vendor_file.exists()
                and vendor_file.read_text(encoding="ascii").strip().lower() != "0x1002"
            ):
                continue
            vram_file = device / "mem_info_vram_total"
            vram = int(vram_file.read_text(encoding="ascii").strip()) if vram_file.exists() else 0
            for hwmon in sorted((device / "hwmon").glob("hwmon*")):
                name_file = hwmon / "name"
                if name_file.exists() and name_file.read_text(encoding="ascii").strip() != "amdgpu":
                    continue
                for input_file in sorted(hwmon.glob("temp*_input")):
                    label_file = input_file.with_name(input_file.name.replace("_input", "_label"))
                    label = (
                        label_file.read_text(encoding="utf-8").strip()
                        if label_file.exists()
                        else input_file.stem
                    )
                    priority = {"edge": 0, "junction": 1, "gpu": 2}.get(label.lower(), 3)
                    value = float(input_file.read_text(encoding="ascii").strip()) / 1000.0
                    if 0.0 < value < 130.0:
                        cards.append((vram, -priority, value, f"amdgpu {card.name} · {label}"))
        except (OSError, ValueError):
            continue
    if not cards:
        return None, "amdgpu nicht gefunden"
    _vram, _priority, value, label = max(cards, key=lambda item: (item[0], item[1]))
    return value, label


class SystemMetricSampler:
    """Read-only Linux system metrics for imported LCD profiles.

    Values are best-effort and intentionally never write sysfs. Missing metrics
    are returned as ``None`` so the renderer can display an em dash.
    """

    def __init__(self) -> None:
        self._last_cpu_total: int | None = None
        self._last_cpu_idle: int | None = None

    @staticmethod
    def _read_number(path: Path, divisor: float = 1.0) -> float | None:
        try:
            return float(path.read_text(encoding="ascii").strip()) / divisor
        except (OSError, ValueError, ZeroDivisionError):
            return None

    def cpu_load(self) -> float | None:
        try:
            fields = Path("/proc/stat").read_text(encoding="ascii").splitlines()[0].split()
            if not fields or fields[0] != "cpu":
                return None
            values = [int(value) for value in fields[1:]]
        except (OSError, ValueError, IndexError):
            return None
        if len(values) < 4:
            return None
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        total = sum(values)
        previous_total, previous_idle = self._last_cpu_total, self._last_cpu_idle
        self._last_cpu_total, self._last_cpu_idle = total, idle
        if previous_total is None or previous_idle is None:
            return None
        total_delta = total - previous_total
        idle_delta = idle - previous_idle
        if total_delta <= 0:
            return None
        return max(0.0, min(100.0, (total_delta - idle_delta) * 100.0 / total_delta))

    @staticmethod
    def cpu_clock_mhz() -> float | None:
        values: list[float] = []
        for path in sorted(Path("/sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq/scaling_cur_freq")):
            value = SystemMetricSampler._read_number(path, 1000.0)
            if value and value > 0:
                values.append(value)
        if values:
            return sum(values) / len(values)
        try:
            for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.casefold().startswith("cpu mhz") and ":" in line:
                    value = float(line.split(":", 1)[1].strip())
                    if value > 0:
                        values.append(value)
        except (OSError, ValueError):
            pass
        return sum(values) / len(values) if values else None

    @staticmethod
    def memory_metrics() -> tuple[float | None, float | None, float | None]:
        values: dict[str, float] = {}
        try:
            for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
                if ":" not in line:
                    continue
                key, rest = line.split(":", 1)
                number = rest.strip().split()[0]
                values[key] = float(number) / (1024.0 * 1024.0)  # kB -> GiB
        except (OSError, ValueError, IndexError):
            return None, None, None
        total = values.get("MemTotal")
        available = values.get("MemAvailable")
        if not total or total <= 0:
            return None, None, None
        used = total - available if available is not None else None
        load = used * 100.0 / total if used is not None else None
        return load, used, total

    @staticmethod
    def _amd_cards(drm_root: Path = Path("/sys/class/drm")) -> list[tuple[int, Path]]:
        cards: list[tuple[int, Path]] = []
        for card in sorted(drm_root.glob("card[0-9]*")):
            device = card / "device"
            try:
                vendor = (device / "vendor").read_text(encoding="ascii").strip().casefold()
                if vendor != "0x1002":
                    continue
                vram_path = device / "mem_info_vram_total"
                vram = int(vram_path.read_text(encoding="ascii").strip()) if vram_path.exists() else 0
                cards.append((vram, device))
            except (OSError, ValueError):
                continue
        return sorted(cards, key=lambda item: item[0], reverse=True)

    @classmethod
    def gpu_metrics(cls) -> tuple[float | None, float | None, float | None]:
        cards = cls._amd_cards()
        if not cards:
            return None, None, None
        device = cards[0][1]
        load = cls._read_number(device / "gpu_busy_percent")
        clock: float | None = None
        try:
            dpm = (device / "pp_dpm_sclk").read_text(encoding="ascii")
            for line in dpm.splitlines():
                if "*" in line:
                    match = __import__("re").search(r"([0-9]+(?:\.[0-9]+)?)\s*Mhz", line, __import__("re").I)
                    if match:
                        clock = float(match.group(1))
                        break
        except (OSError, ValueError):
            pass
        power: float | None = None
        for hwmon in sorted((device / "hwmon").glob("hwmon*")):
            for filename in ("power1_average", "power1_input"):
                value = cls._read_number(hwmon / filename, 1_000_000.0)
                if value is not None and value >= 0:
                    power = value
                    break
            if power is not None:
                break
        return load, clock, power

    @staticmethod
    def cpu_power_w(hwmon_root: Path = Path("/sys/class/hwmon")) -> float | None:
        # Some kernels expose CPU package power through hwmon. This is optional;
        # no extra privileged driver is installed or loaded by OHC.
        for hwmon in sorted(hwmon_root.glob("hwmon*")):
            try:
                name = (hwmon / "name").read_text(encoding="ascii").strip().casefold()
            except OSError:
                continue
            if name not in {"k10temp", "zenpower", "fam15h_power"}:
                continue
            for filename in ("power1_average", "power1_input"):
                value = SystemMetricSampler._read_number(hwmon / filename, 1_000_000.0)
                if value is not None and value >= 0:
                    return value
        return None

    def sample(self) -> dict[str, float | None]:
        ram_load, ram_used, ram_total = self.memory_metrics()
        gpu_load, gpu_clock, gpu_power = self.gpu_metrics()
        return {
            "cpuLoad": self.cpu_load(),
            "cpuClock": self.cpu_clock_mhz(),
            "cpuPower": self.cpu_power_w(),
            "gpuLoad": gpu_load,
            "gpuClock": gpu_clock,
            "gpuPower": gpu_power,
            "ramLoad": ram_load,
            "ramUsed": ram_used,
            "ramTotal": ram_total,
        }
