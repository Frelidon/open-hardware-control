#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure distribution and board detection for fixed NCT6687 setup plans."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shlex


OS_RELEASE = Path("/etc/os-release")
DMI_ROOT = Path("/sys/class/dmi/id")
SOURCE_URL = "https://github.com/Fred78290/nct6687d.git"


@dataclass(frozen=True, slots=True)
class DistributionInfo:
    distro_id: str
    pretty_name: str
    family: str

    @property
    def supported(self) -> bool:
        return self.family in {"fedora", "ubuntu", "arch"}

    @property
    def command_label(self) -> str:
        return {"fedora": "Fedora", "ubuntu": "Ubuntu", "arch": "Arch Linux"}.get(
            self.family, self.pretty_name or self.distro_id or "Linux"
        )


@dataclass(frozen=True, slots=True)
class SetupPlan:
    family: str
    label: str
    commands: tuple[str, ...]
    msi_x870: bool


def parse_os_release(text: str) -> dict[str, str]:
    """Parse the small freedesktop os-release format without executing it."""
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        if not key.replace("_", "").isalnum():
            continue
        try:
            parts = shlex.split(raw_value, posix=True)
        except ValueError:
            continue
        values[key] = (parts[0] if parts else "")[:240]
    return values


def distribution_from_values(values: dict[str, str]) -> DistributionInfo:
    distro_id = values.get("ID", "").strip().casefold()
    id_like = {item.casefold() for item in values.get("ID_LIKE", "").split()}
    family = "unsupported"
    if distro_id == "ubuntu" or "ubuntu" in id_like:
        family = "ubuntu"
    elif distro_id == "fedora":
        family = "fedora"
    elif distro_id == "arch":
        family = "arch"
    pretty_name = values.get("PRETTY_NAME", "") or values.get("NAME", "") or distro_id or "Linux"
    return DistributionInfo(distro_id, pretty_name[:160], family)


def detect_distribution(path: Path = OS_RELEASE) -> DistributionInfo:
    try:
        values = parse_os_release(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        values = {}
    return distribution_from_values(values)


def detect_board(root: Path = DMI_ROOT) -> tuple[str, bool]:
    def read(name: str) -> str:
        try:
            return (root / name).read_text(encoding="utf-8", errors="replace").strip()[:160]
        except OSError:
            return ""

    vendor = read("board_vendor")
    board = read("board_name") or read("product_name")
    identity = f"{vendor} {board}".upper()
    msi_x870 = "X870" in identity and ("MICRO-STAR" in identity or "MSI" in identity)
    label = " · ".join(part for part in (vendor, board) if part) or "Unbekannt"
    return label, msi_x870


def setup_plan(distribution: DistributionInfo, *, msi_x870: bool) -> SetupPlan | None:
    """Return one fixed, reviewable command list for a supported distribution."""
    dependencies = {
        "ubuntu": (
            "sudo apt update",
            "sudo apt install -y git build-essential linux-headers-$(uname -r) "
            "dkms dh-dkms openssl mokutil",
        ),
        "fedora": ((
            "sudo dnf install -y git make automake gcc gcc-c++ kernel-devel "
            "kernel-headers dkms openssl mokutil"
        ),),
        "arch": ((
            "sudo pacman -S --needed git make automake linux-firmware linux-headers "
            "dkms base-devel openssl mokutil"
        ),),
    }.get(distribution.family)
    if dependencies is None:
        return None
    source_step = (
        'if [ -d "$HOME/nct6687d/.git" ]; then '
        'git -C "$HOME/nct6687d" pull --ff-only; '
        'elif [ -e "$HOME/nct6687d" ]; then '
        'printf "%s\\n" "Abbruch: $HOME/nct6687d existiert, ist aber kein Git-Checkout." >&2; exit 2; '
        f'else git clone {SOURCE_URL} "$HOME/nct6687d"; fi'
    )
    commands = [
        *dependencies,
        source_step,
        'cd "$HOME/nct6687d" && sudo make dkms/install',
    ]
    if msi_x870:
        commands.extend((
            'echo "blacklist nct6683" | sudo tee /etc/modprobe.d/nct6683_blacklist.conf',
            'echo "options nct6687 msi_fan_brute_force=1" | sudo tee /etc/modprobe.d/nct6687_msi.conf',
        ))
    commands.append('echo "nct6687" | sudo tee /etc/modules-load.d/nct6687.conf')
    return SetupPlan(distribution.family, distribution.command_label, tuple(commands), msi_x870)
