#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validated NZXT 2023 RGB Controller effect definitions."""

from __future__ import annotations

from dataclasses import dataclass

VALID_SPEEDS = {"slowest", "slower", "normal", "faster", "fastest"}
VALID_DIRECTIONS = {"forward", "backward"}
VALID_CHANNELS = {"sync", "led1", "led2", "led3"}
HEX = set("0123456789abcdef")


@dataclass(frozen=True)
class NZXTEffect:
    title: str
    mode: str
    min_colors: int
    max_colors: int
    supports_speed: bool = True
    supports_direction: bool = False
    channel_sensitive: bool = False


NZXT_EFFECTS: tuple[NZXTEffect, ...] = (
    NZXTEffect("Aus", "off", 0, 0, False),
    NZXTEffect("Statisch", "fixed", 1, 1, False),
    NZXTEffect("Überblenden", "fading", 2, 8),
    NZXTEffect("Pulsieren", "pulse", 1, 8),
    NZXTEffect("Atmen", "breathing", 1, 8),
    NZXTEffect("Kerze", "candle", 1, 1),
    NZXTEffect("Sternennacht", "starry-night", 1, 1),
    NZXTEffect("Spektrum-Welle", "spectrum-wave", 0, 0, True, True),
    NZXTEffect("Regenbogenfluss", "rainbow-flow", 0, 0, True, True),
    NZXTEffect("Super-Regenbogen", "super-rainbow", 0, 0, True, True),
    NZXTEffect("Regenbogen-Puls", "rainbow-pulse", 0, 0, True, True),
    # Do not expose the generic SmartDevice ``alternating-[3-6]`` aliases
    # here.  The dedicated NZXT 2023 RGB Controller driver in liquidctl 1.16
    # raises KeyError for them on real hardware.  OHC's alternating software
    # design uses the proven two-colour fading mode as its hardware fallback.
    # On multiple F120/F140 fans the firmware produces the intended mirrored
    # wing shape per physical channel.  Treating sync as one long strip makes
    # the midpoint fall between devices and was the visible 3.3.0 defect.
    NZXTEffect("Flügel", "wings", 1, 1, True, False, True),
)

NZXT_EFFECT_BY_TITLE = {effect.title: effect for effect in NZXT_EFFECTS}
NZXT_EFFECT_BY_MODE = {effect.mode: effect for effect in NZXT_EFFECTS}


def _color(value: object) -> str:
    clean = str(value or "").strip().lstrip("#").casefold()
    if len(clean) != 6 or any(char not in HEX for char in clean):
        raise ValueError("Ungültige NZXT-RGB-Farbe.")
    return clean


def effect_channels(channel: str, mode: str) -> tuple[str, ...]:
    if channel not in VALID_CHANNELS:
        raise ValueError("Ungültiger NZXT-RGB-Kanal.")
    effect = NZXT_EFFECT_BY_MODE.get(mode)
    if effect is None:
        raise ValueError("Nicht unterstützter NZXT-RGB-Effekt.")
    if channel == "sync" and effect.channel_sensitive:
        return ("led1", "led2", "led3")
    return (channel,)


def coalesce_selected_channels(channels: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    """Use the controller's proven sync path when all three ports are selected."""
    clean = tuple(dict.fromkeys(str(channel) for channel in channels))
    if any(channel not in {"led1", "led2", "led3"} for channel in clean):
        raise ValueError("Ungültige NZXT-RGB-Kanalauswahl.")
    if set(clean) == {"led1", "led2", "led3"}:
        return ("sync",)
    return tuple(channel for channel in ("led1", "led2", "led3") if channel in clean)


def build_nzxt_effect_arguments(
    prefix: list[str],
    channel: str,
    mode: str,
    colors: list[str],
    speed: str = "normal",
    direction: str = "forward",
) -> list[list[str]]:
    effect = NZXT_EFFECT_BY_MODE.get(mode)
    if effect is None:
        raise ValueError("Nicht unterstützter NZXT-RGB-Effekt.")
    clean_colors = [_color(value) for value in colors]
    if not effect.min_colors <= len(clean_colors) <= effect.max_colors:
        raise ValueError(
            f"Der NZXT-Effekt {effect.title} benötigt {effect.min_colors} bis {effect.max_colors} Farbe(n)."
        )
    if speed not in VALID_SPEEDS:
        raise ValueError("Ungültige NZXT-RGB-Geschwindigkeit.")
    if direction not in VALID_DIRECTIONS:
        raise ValueError("Ungültige NZXT-RGB-Richtung.")
    commands: list[list[str]] = []
    for target in effect_channels(channel, mode):
        command = [*prefix, "set", target, "color", mode, *clean_colors]
        if effect.supports_speed:
            command.extend(["--speed", speed])
        if effect.supports_direction:
            command.extend(["--direction", direction])
        commands.append(command)
    return commands


def closest_nzxt_mode(effect_id: str) -> str:
    return {
        "static": "fixed",
        "breathing": "breathing",
        "rainbow": "rainbow-flow",
        "lightning": "pulse",
        "spinner": "rainbow-flow",
        "comet": "pulse",
        "wave": "spectrum-wave",
        "pulse": "pulse",
        "alternating": "fading",
        "sparkle": "starry-night",
    }.get(str(effect_id), "fixed")
