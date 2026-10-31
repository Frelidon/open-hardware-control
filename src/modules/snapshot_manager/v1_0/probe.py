#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded read-only Linux snapshot and filesystem discovery."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess


COMMAND_TIMEOUT = 3.0
MAX_OUTPUT = 128 * 1024
SNAPPER_TIMERS = ("snapper-timeline.timer", "snapper-cleanup.timer")


def read_os_release(path: Path = Path("/etc/os-release")) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return result
    for line in lines:
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip().strip('"\'')[:256]
    return result


def run_json(command: list[str], *, timeout: float = COMMAND_TIMEOUT) -> object:
    try:
        completed = subprocess.run(
            command, capture_output=True, timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0 or len(completed.stdout) > MAX_OUTPUT:
        return None
    try:
        return json.loads(completed.stdout.decode("utf-8", "replace"))
    except (UnicodeError, json.JSONDecodeError):
        return None


def command_state(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=COMMAND_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return (completed.stdout or completed.stderr).strip().splitlines()[0][:80] if (
        completed.stdout or completed.stderr
    ) else ("active" if completed.returncode == 0 else "inactive")


def filesystem_report() -> list[dict[str, str]]:
    executable = shutil.which("findmnt")
    if not executable:
        return []
    payload = run_json([executable, "-J", "-o", "TARGET,SOURCE,FSTYPE,OPTIONS"])
    if not isinstance(payload, dict) or not isinstance(payload.get("filesystems"), list):
        return []
    result: list[dict[str, str]] = []
    for item in payload["filesystems"][:128]:
        if not isinstance(item, dict):
            continue
        result.append({
            key: str(item.get(key, ""))[:1024]
            for key in ("target", "source", "fstype", "options")
        })
    return result


def snapper_configs() -> list[dict[str, str]]:
    executable = shutil.which("snapper")
    if not executable:
        return []
    payload = run_json([executable, "--jsonout", "list-configs"])
    if not isinstance(payload, dict) or not isinstance(payload.get("configs"), list):
        return []
    result: list[dict[str, str]] = []
    for item in payload["configs"][:64]:
        if not isinstance(item, dict):
            continue
        name = str(item.get("config", ""))[:64]
        subvolume = str(item.get("subvolume", ""))[:512]
        if name:
            result.append({"name": name, "subvolume": subvolume})
    return result


def btrfs_discard_report(root: Path = Path("/sys/fs/btrfs")) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    try:
        candidates = sorted(root.iterdir())
    except OSError:
        return result
    for entry in candidates[:64]:
        discard = entry / "discard"
        if not discard.is_dir():
            continue
        values: dict[str, object] = {"uuid": entry.name}
        for key in ("discardable_bytes", "discardable_extents", "iops_limit", "kbps_limit", "max_discard_size"):
            try:
                values[key] = int((discard / key).read_text(encoding="ascii").strip())
            except (OSError, ValueError):
                values[key] = None
        result.append(values)
    return result


def backend_report(filesystems: list[dict[str, str]]) -> list[dict[str, object]]:
    names = (
        ("snapper", "Snapper"), ("timeshift", "Timeshift"),
        ("btrfs", "Btrfs"), ("zfs", "ZFS"), ("lvs", "LVM"),
    )
    btrfs_active = any(item.get("fstype") == "btrfs" for item in filesystems)
    zfs_active = any(str(item.get("fstype", "")).startswith("zfs") for item in filesystems)
    lvm_active = any(
        str(item.get("source", "")).startswith(("/dev/mapper/", "/dev/dm-"))
        for item in filesystems
    )
    timeshift_active = Path("/etc/timeshift/timeshift.json").is_file() or Path("/timeshift/snapshots").is_dir()
    configs = snapper_configs()
    result: list[dict[str, object]] = []
    for binary, label in names:
        executable = shutil.which(binary)
        active = {
            "snapper": bool(configs), "timeshift": timeshift_active,
            "btrfs": btrfs_active, "zfs": zfs_active, "lvs": lvm_active,
        }.get(binary, False)
        detected = bool(executable) or active
        result.append({
            "id": binary,
            "label": label,
            "available": detected,
            "active": active,
            "path": executable or "",
        })
    return result


def probe() -> dict[str, object]:
    os_release = read_os_release()
    filesystems = filesystem_report()
    configs = snapper_configs()
    timer_states = {
        unit: {
            "active": command_state(["systemctl", "is-active", unit]),
            "enabled": command_state(["systemctl", "is-enabled", unit]),
        }
        for unit in SNAPPER_TIMERS
    }
    return {
        "schema": 1,
        "os": {
            "id": os_release.get("ID", "unknown"),
            "name": os_release.get("PRETTY_NAME", os_release.get("NAME", "Linux")),
            "version": os_release.get("VERSION_ID", ""),
        },
        "filesystems": filesystems,
        "backends": backend_report(filesystems),
        "snapper_configs": configs,
        "timers": timer_states,
        "btrfs_discard": btrfs_discard_report(),
    }


if __name__ == "__main__":
    print(json.dumps(probe(), ensure_ascii=False), flush=True)
