#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded, read-only Linux/Windows inventory for Hardware Checker 1.0."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import platform

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from modules.hardware_checker.v1_0.model import normalize_board


SYS_PCI = Path("/sys/bus/pci/devices")
SYS_NVME = Path("/sys/class/nvme")


def _text(path: Path, limit: int = 512) -> str:
    try:
        if path.is_symlink() and not path.resolve().exists():
            return ""
        return path.read_text(encoding="utf-8", errors="replace")[:limit].strip()
    except OSError:
        return ""


def _run(arguments: list[str], timeout: int = 4) -> str:
    try:
        environment = dict(os.environ)
        environment["LC_ALL"] = "C"
        result = subprocess.run(
            arguments, capture_output=True, text=True, timeout=timeout,
            check=False, env=environment,
        )
        return result.stdout[:4096].strip() if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def cpu_info() -> dict[str, object]:
    output = _run([shutil.which("lscpu") or "lscpu"], timeout=4)
    fields: dict[str, str] = {}
    for line in output.splitlines()[:256]:
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    model = fields.get("Model name") or _cpuinfo_model()
    threads = _integer(fields.get("Thread(s) per core"))
    cores = _integer(fields.get("Core(s) per socket"))
    sockets = _integer(fields.get("Socket(s)"))
    logical = _integer(fields.get("CPU(s)")) or (os.cpu_count() or 0)
    control = _text(Path("/sys/devices/system/cpu/smt/control"), 32).casefold()
    active = _text(Path("/sys/devices/system/cpu/smt/active"), 8)
    if control == "notsupported":
        smt_state = "unsupported"
    elif control in {"off", "forceoff"} or active == "0":
        smt_state = "disabled"
    elif control == "on" or active == "1" or (threads and threads > 1):
        smt_state = "enabled"
    else:
        smt_state = "unknown"
    cpuinfo = _text(Path("/proc/cpuinfo"), 256 * 1024).casefold()
    flags_match = re.search(r"^(?:flags|features)\s*:\s*(.+)$", cpuinfo, re.M)
    flags = set(flags_match.group(1).split()) if flags_match else set()
    architecture = (fields.get("Architecture") or platform.machine()).casefold()
    if "svm" in flags:
        virtualization_state, virtualization_type = "enabled", "AMD-V / SVM"
    elif "vmx" in flags:
        virtualization_state, virtualization_type = "enabled", "Intel VT-x / VMX"
    elif any(token in architecture for token in ("x86", "amd64", "i386", "i686")):
        virtualization_state, virtualization_type = "disabled", "AMD-V / Intel VT-x"
    else:
        virtualization_state, virtualization_type = "unknown", ""
    return {
        "model": model or "Unbekannt", "threads_per_core": threads,
        "cores": (cores * sockets) if cores and sockets else cores,
        "logical": logical, "smt_state": smt_state, "smt_control": control,
        "virtualization_state": virtualization_state,
        "virtualization_type": virtualization_type,
    }


def _cpuinfo_model() -> str:
    text = _text(Path("/proc/cpuinfo"), 64 * 1024)
    match = re.search(r"^(?:model name|Hardware)\s*:\s*(.+)$", text, re.M)
    return match.group(1).strip()[:240] if match else ""


def _integer(value: object) -> int | None:
    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else None


def pci_components() -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    lspci = shutil.which("lspci")
    for device in sorted(SYS_PCI.glob("*"))[:1024]:
        class_code = _text(device / "class", 16).casefold()
        if not class_code.startswith(("0x0300", "0x0302")):
            continue
        address = device.name
        label = _run([lspci, "-D", "-s", address, "-nn"], 3) if lspci else ""
        label = _friendly_pci_name(label)
        driver = ""
        try:
            driver = (device / "driver").resolve().name if (device / "driver").exists() else ""
        except OSError:
            pass
        result.append(_pci_record(device, label or f"GPU {address}", driver, "gpu"))
    return result


def _friendly_pci_name(label: str) -> str:
    """Remove the duplicated address/class and trailing numeric PCI ID."""
    value = re.sub(r"^\S+\s+[^:]+:\s*", "", label.strip())
    value = re.sub(r"\s+\[[0-9a-fA-F]{4}:[0-9a-fA-F]{4}\](?:\s+\(rev\s+[^)]+\))?$", "", value)
    return value[:300]


def nvme_components() -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for controller in sorted(SYS_NVME.glob("nvme[0-9]*"))[:64]:
        device = controller / "device"
        try:
            resolved = device.resolve()
        except OSError:
            continue
        if not resolved.exists():
            continue
        model = _text(controller / "model", 240) or controller.name
        record = _pci_record(resolved, model, "nvme", "nvme")
        record["controller"] = controller.name
        result.append(record)
    return result


def _pci_record(path: Path, name: str, driver: str, kind: str) -> dict[str, object]:
    return {
        "kind": kind, "address": path.name, "name": name[:300], "driver": driver,
        "current_speed": _text(path / "current_link_speed", 64),
        "current_width": _integer(_text(path / "current_link_width", 16)) or 0,
        "max_speed": _text(path / "max_link_speed", 64),
        "max_width": _integer(_text(path / "max_link_width", 16)) or 0,
        "boot_vga": _text(path / "boot_vga", 8) == "1",
    }


def memory_total() -> str:
    text = _text(Path("/proc/meminfo"), 4096)
    match = re.search(r"^MemTotal:\s+(\d+)\s+kB", text, re.M)
    if not match:
        return "Unbekannt"
    gib = int(match.group(1)) / (1024 * 1024)
    return f"{gib:.1f} GiB"


def board_info() -> dict[str, str]:
    vendor = _text(Path("/sys/class/dmi/id/board_vendor"), 120)
    name = _text(Path("/sys/class/dmi/id/board_name"), 160)
    version = _text(Path("/sys/class/dmi/id/board_version"), 120)
    return normalize_board(vendor, name, version)


_WINDOWS_INVENTORY_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
$cpu = @(Get-CimInstance Win32_Processor | Select-Object -First 1 Name,NumberOfCores,NumberOfLogicalProcessors,SocketDesignation,VirtualizationFirmwareEnabled)
$board = @(Get-CimInstance Win32_BaseBoard | Select-Object -First 1 Manufacturer,Product,Version)
$gpus = @(Get-CimInstance Win32_VideoController | Select-Object Name,PNPDeviceID,DriverVersion)
$disks = @(Get-CimInstance Win32_DiskDrive | Where-Object {$_.Model -match 'NVMe|NVM Express' -or $_.InterfaceType -eq 'NVMe'} | Select-Object Model,PNPDeviceID,InterfaceType)
$memory = @(Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer,PartNumber,Capacity,Speed,ConfiguredClockSpeed,DeviceLocator)
$system = @(Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory)
[ordered]@{cpu=$cpu;board=$board;gpus=$gpus;nvmes=$disks;memory=$memory;system=$system} | ConvertTo-Json -Compress -Depth 5
""".strip()


def _records(value: object) -> list[dict[str, object]]:
    if isinstance(value, dict):
        return [value]
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def normalize_windows_inventory(payload: object) -> dict[str, object]:
    """Normalize non-sensitive CIM JSON into the regular checker schema."""

    data = payload if isinstance(payload, dict) else {}
    cpu_rows = _records(data.get("cpu"))
    board_rows = _records(data.get("board"))
    system_rows = _records(data.get("system"))
    cpu = cpu_rows[0] if cpu_rows else {}
    board = board_rows[0] if board_rows else {}
    system = system_rows[0] if system_rows else {}
    logical = _integer(cpu.get("NumberOfLogicalProcessors")) or (os.cpu_count() or 0)
    cores = _integer(cpu.get("NumberOfCores"))
    smt = "enabled" if cores and logical > cores else "disabled" if cores and logical == cores else "unknown"
    total_bytes = _integer(system.get("TotalPhysicalMemory")) or 0
    memory = []
    for item in _records(data.get("memory"))[:256]:
        capacity = _integer(item.get("Capacity")) or 0
        memory.append({
            "locator": str(item.get("DeviceLocator") or "")[:120],
            "size": f"{capacity / (1024 ** 3):.1f} GiB" if capacity else "Unbekannt",
            "type": "",
            "manufacturer": str(item.get("Manufacturer") or "")[:120],
            "part": str(item.get("PartNumber") or "")[:160].strip(),
            "speed_mts": _integer(item.get("Speed")),
            "configured_mts": _integer(item.get("ConfiguredClockSpeed")),
        })
    gpus = [{
        "kind": "gpu", "name": str(item.get("Name") or "GPU")[:300],
        "driver": str(item.get("DriverVersion") or "")[:120],
        "address": "", "current_speed": "", "current_width": 0,
        "max_speed": "", "max_width": 0, "boot_vga": index == 0,
    } for index, item in enumerate(_records(data.get("gpus"))[:32])]
    nvmes = [{
        "kind": "nvme", "name": str(item.get("Model") or "NVMe")[:300],
        "driver": str(item.get("InterfaceType") or "NVMe")[:80],
        "address": "", "current_speed": "", "current_width": 0,
        "max_speed": "", "max_width": 0,
    } for item in _records(data.get("nvmes"))[:64]]
    return {
        "cpu": {
            "model": str(cpu.get("Name") or platform.processor() or "Unbekannt")[:240],
            "threads_per_core": (logical // cores) if cores else None,
            "cores": cores, "logical": logical, "smt_state": smt,
            "smt_control": "cim",
            "virtualization_state": "enabled" if cpu.get("VirtualizationFirmwareEnabled") else "unknown",
            "virtualization_type": "Firmware / Hyper-V",
        },
        "gpus": gpus, "nvmes": nvmes,
        "memory_total": f"{total_bytes / (1024 ** 3):.1f} GiB" if total_bytes else "Unbekannt",
        "memory_modules": memory,
        "socket": str(cpu.get("SocketDesignation") or "Nicht gemeldet")[:80],
        "socket_source": "Windows CIM",
        "board": normalize_board(board.get("Manufacturer"), board.get("Product"), board.get("Version")),
        "tools": {"powershell": shutil.which("powershell.exe") or shutil.which("pwsh.exe") or ""},
    }


def windows_collect() -> dict[str, object]:
    executable = shutil.which("powershell.exe") or shutil.which("pwsh.exe")
    if not executable:
        return normalize_windows_inventory({})
    raw = _run([executable, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", _WINDOWS_INVENTORY_SCRIPT], 12)
    try:
        return normalize_windows_inventory(json.loads(raw.lstrip("\ufeff")))
    except (json.JSONDecodeError, TypeError):
        return normalize_windows_inventory({})


def collect() -> dict[str, object]:
    if sys.platform.startswith("win"):
        return windows_collect()
    return {
        "cpu": cpu_info(), "gpus": pci_components(), "nvmes": nvme_components(),
        "memory_total": memory_total(), "board": board_info(),
        "tools": {
            "pkexec": shutil.which("pkexec") or "",
            "dmidecode": shutil.which("dmidecode") or "",
            "vkmark": shutil.which("vkmark") or "",
            "glmark2": next((shutil.which(name) for name in (
                "glmark2", "glmark2-wayland", "glmark2-x11", "glmark2-es2-wayland"
            ) if shutil.which(name)), ""),
            "vkcube": shutil.which("vkcube") or "",
        },
    }


def main(arguments: list[str]) -> int:
    if arguments != ["--json"]:
        return 2
    print(json.dumps(collect(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
