# SPDX-License-Identifier: GPL-3.0-or-later
"""Presentation-only GPU cooler/light shapes for the case diagram.

The records describe original OHC vector drawings.  They do not contain
manufacturer artwork, electrical LED counts or hardware-control assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GpuVisualProfile:
    profile_id: str
    label: str
    fan_count: int
    lighting: str
    tokens: tuple[tuple[str, ...], ...] = ()


GPU_VISUAL_PROFILES = (
    GpuVisualProfile("generic-triple-dark", "3 Lüfter · ohne Beleuchtung", 3, "none"),
    GpuVisualProfile("generic-dual-dark", "2 Lüfter · ohne Beleuchtung", 2, "none"),
    GpuVisualProfile("generic-triple-strip", "3 Lüfter · langer LED-Streifen", 3, "edge-strip"),
    GpuVisualProfile("generic-triple-rings", "3 Lüfter · beleuchtete Lüfterringe", 3, "fan-rings"),
    GpuVisualProfile("generic-triple-hubs", "3 Lüfter · beleuchtete Lüfternaben", 3, "fan-hubs"),
    GpuVisualProfile("generic-quad-indirect", "4 Lüfter · indirekte Beleuchtung", 4, "indirect"),
    GpuVisualProfile(
        "sapphire-nitro-rx9000", "Sapphire NITRO+ RX 9000 · ARGB-Lichtleiste", 3, "edge-strip",
        (("sapphire", "nitro", "9070"), ("sapphire", "nitro", "9060")),
    ),
    GpuVisualProfile(
        "sapphire-pure-rx9000", "Sapphire PURE RX 9000 · beleuchtetes Logo", 3, "logo",
        (("sapphire", "pure", "9070"), ("sapphire", "pure", "9060")),
    ),
    GpuVisualProfile(
        "sapphire-nitro-rx6000", "Sapphire NITRO+ RX 6000 · ARGB-Lüfter", 3, "fan-rings",
        (("sapphire", "nitro", "6700"), ("sapphire", "nitro", "6800"), ("sapphire", "nitro", "6900")),
    ),
    GpuVisualProfile(
        "gigabyte-aorus-rtx50", "Gigabyte AORUS RTX 50 · RGB-Halo", 3, "fan-rings",
        (("gigabyte", "aorus", "rtx 50"), ("aorus", "5090"), ("aorus", "5080"), ("aorus", "5070")),
    ),
    GpuVisualProfile(
        "gigabyte-aorus-rtx40", "Gigabyte AORUS RTX 40 · RGB-Halo", 3, "fan-rings",
        (("gigabyte", "aorus", "rtx 40"), ("aorus", "4090"), ("aorus", "4080"), ("aorus", "4070")),
    ),
    GpuVisualProfile(
        "asus-rog-astral-rtx50", "ASUS ROG Astral RTX 50 · indirektes ARGB", 4, "indirect",
        (("asus", "astral", "rtx 50"), ("rog", "astral", "5090"), ("rog", "astral", "5080")),
    ),
    GpuVisualProfile(
        "zotac-amp-extreme-rtx50", "ZOTAC AMP Extreme RTX 50 · Mehrzonen-RGB", 3, "mixed",
        (("zotac", "amp extreme", "rtx 50"), ("zotac", "amp extreme", "5090"), ("zotac", "amp extreme", "5080")),
    ),
    GpuVisualProfile(
        "msi-suprim-rtx40", "MSI SUPRIM RTX 40 · RGB-Akzente", 3, "indirect",
        (("msi", "suprim", "rtx 40"), ("msi", "suprim", "4090"), ("msi", "suprim", "4080"), ("msi", "suprim", "4070")),
    ),
)

_BY_ID = {profile.profile_id: profile for profile in GPU_VISUAL_PROFILES}


def visual_profile_by_id(profile_id: object) -> GpuVisualProfile | None:
    return _BY_ID.get(str(profile_id))


def detect_gpu_visual(device_name: object) -> GpuVisualProfile | None:
    """Detect only board/cooler families with enough identifying tokens."""

    text = " ".join(str(device_name or "").casefold().replace("+", " plus ").split())
    for profile in GPU_VISUAL_PROFILES:
        if any(all(token in text for token in group) for group in profile.tokens):
            return profile
    return None


def resolve_gpu_visual(profile_id: object, device_name: object) -> GpuVisualProfile:
    selected = visual_profile_by_id(profile_id)
    if selected is not None:
        return selected
    # A chip name alone does not reveal the board partner's lighting topology.
    return detect_gpu_visual(device_name) or _BY_ID["generic-triple-dark"]


def normalize_gpu_visual_id(profile_id: object) -> str:
    clean = str(profile_id or "auto")
    return clean if clean == "auto" or clean in _BY_ID else "auto"
