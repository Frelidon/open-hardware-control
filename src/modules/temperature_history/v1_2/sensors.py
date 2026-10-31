#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only discovery of Linux hwmon temperature inputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True, slots=True)
class TemperatureSensorReading:
    key: str
    label: str
    group: str
    value_c: float
    source: str


def _text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return ""


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-") or "sensor"


def _group_for(chip: str, label: str) -> str:
    identity = f"{chip} {label}".casefold()
    if chip in {"k10temp", "coretemp", "zenpower", "fam15h_power"}:
        return "cpu"
    if chip in {"amdgpu", "nouveau", "i915"}:
        return "gpu"
    if chip in {"nvme", "drivetemp", "smart"} or any(token in identity for token in ("ssd", "nvme", "drive")):
        return "storage"
    if chip in {"spd5118", "jc42", "dimmtemp"} or any(token in identity for token in ("dimm", "dram", "memory")):
        return "memory"
    if any(token in identity for token in ("nct", "vrm", "pch", "system", "socket", "acpi")):
        return "mainboard"
    return "other"


def _base_label(group: str, chip: str, label: str) -> str:
    group_names = {
        "cpu": "CPU",
        "gpu": "GPU",
        "storage": "SSD/NVMe",
        "memory": "Arbeitsspeicher",
        "mainboard": "Mainboard",
        "other": chip or "Sensor",
    }
    name = group_names[group]
    cleaned = label.strip()
    if not cleaned or cleaned.casefold() in {"temp", "temperature", "composite"}:
        return name if not cleaned else f"{name} · {cleaned}"
    return f"{name} · {cleaned}"


def read_linux_temperature_sensors(
    hwmon_root: Path = Path("/sys/class/hwmon"),
) -> tuple[TemperatureSensorReading, ...]:
    """Return all plausible readable hwmon temperatures without writing sysfs."""
    candidates: list[tuple[str, str, str, float, str]] = []
    try:
        devices = sorted(hwmon_root.glob("hwmon*"), key=lambda path: str(path.resolve()))
    except OSError:
        return ()
    for hwmon in devices:
        chip = _text(hwmon / "name") or "hwmon"
        for input_file in sorted(hwmon.glob("temp*_input")):
            raw = _text(input_file)
            try:
                value = float(raw) / 1000.0
            except ValueError:
                continue
            if not 0.0 < value <= 150.0:
                continue
            stem = input_file.name.removesuffix("_input")
            label = _text(hwmon / f"{stem}_label") or stem
            group = _group_for(chip.casefold(), label)
            source = f"{chip} · {input_file.name}"
            identity = f"{chip}:{label}:{hwmon.resolve().parent}"
            candidates.append((group, chip, label, value, f"{identity}|{source}"))

    counters: dict[str, int] = {}
    readings: list[TemperatureSensorReading] = []
    for group, chip, label, value, identity_source in sorted(candidates, key=lambda item: item[4]):
        identity, source = identity_source.split("|", 1)
        base = f"hwmon:{_slug(group)}:{_slug(chip)}:{_slug(label)}"
        counters[base] = counters.get(base, 0) + 1
        ordinal = counters[base]
        key = base if ordinal == 1 else f"{base}:{ordinal}"
        display = _base_label(group, chip, label)
        if ordinal > 1:
            display = f"{display} {ordinal}"
        readings.append(TemperatureSensorReading(key, display, group, value, source))
    return tuple(readings)
