#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Original RGB effect engine for Open Hardware Control.

The algorithms in this module were written for Open Hardware Control.  They do
not contain code or assets copied from OpenRGB or the OpenRGB Effects Plugin.
OpenRGB may be used separately as the local hardware/SDK backend.
"""

from __future__ import annotations

import colorsys
import math
import random
import re
from dataclasses import dataclass

RGB = tuple[int, int, int]
HEX_COLOR_RE = re.compile(r"^[0-9a-fA-F]{6}$")


@dataclass(frozen=True)
class EffectDefinition:
    effect_id: str
    title: str
    description: str
    uses_secondary: bool = True


EFFECTS: tuple[EffectDefinition, ...] = (
    EffectDefinition("static", "Statisch", "Eine gleichmäßige Farbe ohne Bewegung.", False),
    EffectDefinition("breathing", "Atmen", "Weiches Ein- und Ausblenden der Hauptfarbe.", False),
    EffectDefinition("rainbow", "Rainbow", "Ein vollständiges, fließendes Farbspektrum.", False),
    EffectDefinition("lightning", "Blitze", "Unregelmäßige Lichtblitze mit wanderndem Einschlag."),
    EffectDefinition("spinner", "Kreisel", "Ein heller Lichtkeil läuft kreisförmig über die LEDs."),
    EffectDefinition("comet", "Komet", "Lichtkopf mit weich auslaufendem Schweif."),
    EffectDefinition("wave", "Farbwelle", "Zwei Farben laufen als weiche Welle über das Gerät."),
    EffectDefinition("pulse", "Doppelpuls", "Zwei kurze Pulse wechseln zwischen den Farben."),
    EffectDefinition("alternating", "Abwechselnd", "Zwei Farben tauschen rhythmisch ihre Positionen."),
    EffectDefinition("sparkle", "Funkeln", "Zufällige Lichtpunkte glitzern auf der Grundfarbe."),
)
EFFECT_BY_ID = {effect.effect_id: effect for effect in EFFECTS}


def effect_color_count(effect_id: object) -> int:
    """Return how many editable colors are meaningful for an OHC effect."""

    normalized = str(effect_id or "static")
    if normalized == "rainbow":
        return 0
    if normalized in {"static", "breathing"}:
        return 1
    return 2


@dataclass(frozen=True)
class RGBEffectConfig:
    effect_id: str = "static"
    primary: str = "00aaff"
    secondary: str = "ffffff"
    brightness: int = 100
    speed: int = 100
    direction: int = 1
    seed: int = 7331

    def normalized(self) -> "RGBEffectConfig":
        effect_id = self.effect_id if self.effect_id in EFFECT_BY_ID else "static"
        return RGBEffectConfig(
            effect_id=effect_id,
            primary=normalize_hex(self.primary),
            secondary=normalize_hex(self.secondary),
            brightness=max(0, min(100, int(self.brightness))),
            speed=max(10, min(200, int(self.speed))),
            direction=-1 if int(self.direction) < 0 else 1,
            seed=max(0, min(2**31 - 1, int(self.seed))),
        )


BUILTIN_DESIGNS: tuple[tuple[str, RGBEffectConfig], ...] = (
    ("Feste Farbe", RGBEffectConfig("static", "00aaff", "ffffff", 90, 100)),
    ("Eisblau", RGBEffectConfig("static", "00aaff", "ffffff", 90, 100)),
    ("Mondweiß", RGBEffectConfig("breathing", "dbefff", "ffffff", 72, 48)),
    ("Tiefsee-Atmen", RGBEffectConfig("breathing", "0060b8", "55e8ff", 88, 66)),
    ("Rainbow-Ring", RGBEffectConfig("rainbow", "ff0040", "00aaff", 90, 80)),
    ("Prisma-Sprint", RGBEffectConfig("rainbow", "ff0040", "00aaff", 100, 145, -1)),
    ("Elektrischer Blitz", RGBEffectConfig("lightning", "267dff", "ffffff", 100, 125)),
    ("Plasma-Blitz", RGBEffectConfig("lightning", "8b24ff", "ff91f4", 92, 160, -1, 8117)),
    ("Neon-Kreisel", RGBEffectConfig("spinner", "7a28ff", "00f0ff", 100, 110)),
    ("Solar-Kreisel", RGBEffectConfig("spinner", "ff3b18", "ffe266", 96, 82, -1)),
    ("Polarlicht", RGBEffectConfig("wave", "00d890", "645cff", 80, 55)),
    ("Ozeanwelle", RGBEffectConfig("wave", "0048a8", "40ffe2", 82, 72)),
    ("Glut-Komet", RGBEffectConfig("comet", "ff3b18", "ffb000", 90, 75)),
    ("Cyber-Komet", RGBEffectConfig("comet", "ff1ab8", "27e8ff", 100, 118, -1)),
    ("Doppelimpuls", RGBEffectConfig("pulse", "4520c8", "e3d9ff", 92, 86)),
    ("Synth-Wechsel", RGBEffectConfig("alternating", "ff1678", "13d8ff", 88, 112)),
    ("Sternenstaub", RGBEffectConfig("sparkle", "102a4f", "ffffff", 85, 70)),
    ("Glühwürmchen", RGBEffectConfig("sparkle", "062b16", "76ff82", 82, 52, 1, 11939)),
    ("Aurora-Vortex", RGBEffectConfig("spinner", "126dff", "b35cff", 92, 74, 1, 24091)),
    ("Galaxie-Komet", RGBEffectConfig("comet", "081a52", "5de8ff", 96, 92, -1, 30917)),
)

# Categories are presentation metadata only.  Keeping them separate preserves
# the original pair-shaped BUILTIN_DESIGNS API used by saved profiles/tests.
BUILTIN_DESIGN_CATEGORIES: tuple[str, ...] = (
    "Ruhig", "Ruhig", "Ruhig", "Ruhig", "Spektrum", "Spektrum", "Energie", "Energie",
    "Bewegung", "Bewegung", "Spektrum", "Spektrum", "Bewegung", "Bewegung",
    "Impuls", "Impuls", "Energie", "Energie", "Spektrum", "Bewegung",
)


def normalize_hex(value: object) -> str:
    text = str(value).strip().lstrip("#")
    if not HEX_COLOR_RE.fullmatch(text):
        raise ValueError("RGB-Farben müssen aus genau sechs Hex-Zeichen bestehen.")
    return text.lower()


def hex_to_rgb(value: object) -> RGB:
    color = normalize_hex(value)
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_to_hex(color: RGB) -> str:
    return "{:02x}{:02x}{:02x}".format(*(max(0, min(255, int(channel))) for channel in color))


def _mix(left: RGB, right: RGB, amount: float) -> RGB:
    amount = max(0.0, min(1.0, amount))
    return tuple(round(a + (b - a) * amount) for a, b in zip(left, right))  # type: ignore[return-value]


def _scale(color: RGB, amount: float) -> RGB:
    return tuple(round(channel * max(0.0, min(1.0, amount))) for channel in color)  # type: ignore[return-value]


def _wheel(position: float) -> RGB:
    red, green, blue = colorsys.hsv_to_rgb(position % 1.0, 1.0, 1.0)
    return round(red * 255), round(green * 255), round(blue * 255)


def render_effect(config: RGBEffectConfig, led_count: int, elapsed_seconds: float) -> list[RGB]:
    """Render one deterministic frame with a bounded LED count.

    ``elapsed_seconds`` is monotonic effect time.  Random-looking effects derive
    their state from a time bucket and the stored seed, so previews and hardware
    frames stay aligned without global random state.
    """

    cfg = config.normalized()
    count = max(1, min(4096, int(led_count)))
    primary = hex_to_rgb(cfg.primary)
    secondary = hex_to_rgb(cfg.secondary)
    phase = max(0.0, float(elapsed_seconds)) * (cfg.speed / 100.0) * cfg.direction
    indices = [index / count for index in range(count)]

    if cfg.effect_id == "static":
        frame = [primary] * count
    elif cfg.effect_id == "breathing":
        strength = 0.12 + 0.88 * (0.5 + 0.5 * math.sin(phase * math.tau - math.pi / 2))
        frame = [_scale(primary, strength)] * count
    elif cfg.effect_id == "rainbow":
        frame = [_wheel(position + phase * 0.16) for position in indices]
    elif cfg.effect_id == "lightning":
        bucket = math.floor(abs(phase) * 11)
        rng = random.Random(cfg.seed + bucket)
        strike = rng.randrange(count)
        flash = 1.0 if rng.random() < 0.24 else 0.06 + rng.random() * 0.10
        frame = []
        for index in range(count):
            distance = min((index - strike) % count, (strike - index) % count)
            bolt = max(0.0, 1.0 - distance / max(1.0, count * 0.17)) * flash
            frame.append(_mix(_scale(primary, 0.05), secondary, bolt))
    elif cfg.effect_id == "spinner":
        head = (phase * 0.24) % 1.0
        frame = []
        for position in indices:
            distance = (head - position) % 1.0
            strength = max(0.04, 1.0 - distance * 7.0)
            frame.append(_mix(_scale(primary, 0.04), secondary, strength))
    elif cfg.effect_id == "comet":
        head = (phase * 0.18) % 1.0
        frame = []
        for position in indices:
            distance = (head - position) % 1.0
            strength = max(0.02, (1.0 - min(1.0, distance * 5.5)) ** 2)
            frame.append(_mix(_scale(primary, 0.03), secondary, strength))
    elif cfg.effect_id == "wave":
        frame = [
            _mix(primary, secondary, 0.5 + 0.5 * math.sin((position * 2.0 - phase * 0.30) * math.tau))
            for position in indices
        ]
    elif cfg.effect_id == "pulse":
        local = (abs(phase) * 0.44) % 1.0
        strength = max(0.05, math.exp(-55 * (local - 0.12) ** 2), math.exp(-55 * (local - 0.34) ** 2))
        base, flash_color = (primary, secondary) if int(abs(phase) * 0.44) % 2 == 0 else (secondary, primary)
        frame = [_mix(_scale(base, 0.06), flash_color, strength)] * count
    elif cfg.effect_id == "alternating":
        offset = math.floor(abs(phase) * 2.0)
        frame = [primary if (index + offset) % 2 == 0 else secondary for index in range(count)]
    elif cfg.effect_id == "sparkle":
        bucket = math.floor(abs(phase) * 8)
        rng = random.Random(cfg.seed + bucket)
        frame = []
        for _index in range(count):
            sparkle = rng.random()
            amount = sparkle**12
            frame.append(_mix(_scale(primary, 0.18), secondary, amount))
    else:  # normalized() currently makes this unreachable
        frame = [primary] * count

    brightness = cfg.brightness / 100.0
    return [_scale(color, brightness) for color in frame]


def render_hex_frame(config: RGBEffectConfig, led_count: int, elapsed_seconds: float) -> list[str]:
    return [rgb_to_hex(color) for color in render_effect(config, led_count, elapsed_seconds)]
