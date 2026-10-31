#!/usr/bin/python3 -I
# SPDX-License-Identifier: GPL-3.0-or-later
"""Root-owned, argument-free reader of non-identifying RAM DMI fields.

Never expose dmidecode's general CLI through a passwordless Polkit action:
its --dump-bin option can write arbitrary root-owned files. This helper runs
one fixed, read-only request with a clean environment and strips identifiers.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import sys


SYSTEM_DMIDECODE = (Path("/usr/sbin/dmidecode"), Path("/usr/bin/dmidecode"))
MAX_OUTPUT_BYTES = 131_072
MEMORY_FIELDS = frozenset({
    "Manufacturer", "Part Number", "Type", "Speed", "Configured Memory Speed",
    "Size", "Locator", "Bank Locator", "Form Factor", "Rank", "Data Width",
    "Total Width", "Configured Voltage", "Minimum Voltage", "Maximum Voltage",
    "Memory Technology",
})


def trusted_executable(path: Path) -> bool:
    """Only a fixed system file with root-owned, non-writable ancestry."""
    try:
        info = path.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != 0
                or info.st_mode & 0o022 or not info.st_mode & 0o111):
            return False
        for parent in path.parents:
            info = parent.lstat()
            if (not stat.S_ISDIR(info.st_mode) or info.st_uid != 0
                    or info.st_mode & 0o022):
                return False
    except OSError:
        return False
    return True


def filter_memory_fields(output: str) -> str:
    """Retain the upstream Memory Device parser contract, not serials/UUIDs."""
    lines = []
    in_memory_device = False
    for raw in output.splitlines():
        line = raw.strip()
        if line.startswith("Handle "):
            in_memory_device = False
        elif line == "Memory Device":
            in_memory_device = True
            lines.append("Memory Device")
        elif in_memory_device:
            key, separator, value = line.partition(":")
            if separator and key in MEMORY_FIELDS:
                lines.append(f"\t{key}: {value.strip()}")
    return "\n".join(lines) + ("\n" if lines else "")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("This helper accepts no arguments.", file=sys.stderr)
        return 64
    if os.geteuid() != 0:
        print("This helper requires its dedicated Polkit action.", file=sys.stderr)
        return 77
    executable = next((path for path in SYSTEM_DMIDECODE if trusted_executable(path)), None)
    if executable is None:
        print("No trusted system dmidecode executable is installed.", file=sys.stderr)
        return 69
    try:
        result = subprocess.run(
            [str(executable), "-t", "memory"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5, check=False,
            env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C", "LC_ALL": "C"},
            cwd="/", stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError):
        print("The fixed memory-information read failed.", file=sys.stderr)
        return 74
    if result.returncode != 0:
        print("Memory information is unavailable.", file=sys.stderr)
        return 74
    if len(result.stdout.encode("utf-8")) > MAX_OUTPUT_BYTES:
        print("Memory-information response exceeds the limit.", file=sys.stderr)
        return 74
    sys.stdout.write(filter_memory_fields(result.stdout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
