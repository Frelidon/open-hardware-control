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
from modules.rgb_studio.v1_15.effect_sampling import averaged_pixel, motion_scale, moving_head_strength, smooth_fraction

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
    EffectDefinition("converge", "3D-Fusion", "Zwei Lichtfronten laufen aus Gegenrichtungen zur Mitte."),
    EffectDefinition("crossflow", "3D-Kreuzstrom", "Zwei gegenläufige Lichtkörper durchqueren den LED-Pfad."),
    EffectDefinition("depthwave", "3D-Tiefenwelle", "Gestaffelte Lichtflächen wandern durch den Gehäuseraum."),
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
    ("Nebula Pulse", RGBEffectConfig("pulse", "6428ff", "ff4fd8", 92, 68, 1, 41011)),
    ("Liquid Metal", RGBEffectConfig("wave", "15202b", "d9f4ff", 88, 54, -1, 41023)),
    ("Ember Flow", RGBEffectConfig("comet", "6e0900", "ff9b28", 96, 83, 1, 41039)),
    ("Arctic Halo", RGBEffectConfig("spinner", "0077ff", "d8ffff", 90, 62, -1, 41047)),
    ("Center Fusion", RGBEffectConfig("converge", "08152f", "f4fbff", 96, 76, 1, 51101)),
    ("Crimson Convergence", RGBEffectConfig("converge", "34000b", "ffcc92", 100, 112, -1, 51103)),
    ("Orbital Crossflow", RGBEffectConfig("crossflow", "00a8ff", "ff35c8", 94, 84, 1, 51109)),
    ("Dual Vector", RGBEffectConfig("crossflow", "172cff", "f8faff", 92, 128, -1, 51113)),
    ("Deep Space Sweep", RGBEffectConfig("depthwave", "041a36", "39e6ff", 88, 64, 1, 51121)),
    ("Vertical Reactor", RGBEffectConfig("depthwave", "2b075f", "ffda58", 96, 102, -1, 51131)),
    ("Prism Drift", RGBEffectConfig("crossflow", "744cff", "39e6ff", 94, 67, 1, 62001)),
    ("Twin Wyrm Orbit", RGBEffectConfig("converge", "ff9b32", "38a8ff", 96, 88, -1, 62003)),
    ("Neon Particle Garden", RGBEffectConfig("sparkle", "0c382f", "ff62ba", 90, 58, 1, 62011)),
    ("Circuit Chase", RGBEffectConfig("comet", "24ddff", "ff3da8", 100, 124, 1, 62017)),
)

# Categories are presentation metadata only.  Keeping them separate preserves
# the original pair-shaped BUILTIN_DESIGNS API used by saved profiles/tests.
BUILTIN_DESIGN_CATEGORIES: tuple[str, ...] = (
    "Ruhig", "Ruhig", "Ruhig", "Ruhig", "Spektrum", "Spektrum", "Energie", "Energie",
    "Bewegung", "Bewegung", "Spektrum", "Spektrum", "Bewegung", "Bewegung",
    "Impuls", "Impuls", "Energie", "Energie", "Spektrum", "Bewegung",
    "Impuls", "Ruhig", "Energie", "Bewegung",
    "Räumlich", "Räumlich", "Räumlich", "Räumlich", "Räumlich", "Räumlich",
    "OHC Originale", "OHC Originale", "OHC Originale", "OHC Originale",
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

    if cfg.effect_id == "static":
        frame = [primary] * count
    elif cfg.effect_id == "breathing":
        strength = 0.12 + 0.88 * (0.5 + 0.5 * math.sin(phase * math.tau - math.pi / 2))
        frame = [_scale(primary, strength)] * count
    elif cfg.effect_id == "rainbow":
        frame = [averaged_pixel(index, count, lambda p: _wheel(p + phase * .16)) for index in range(count)]
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
        head = (phase * .24 * motion_scale(count)) % 1.0
        frame = [averaged_pixel(index, count, lambda p: _mix(_scale(primary, .04), secondary,
                 max(.04, moving_head_strength(p, head, count)))) for index in range(count)]
    elif cfg.effect_id == "comet":
        head = (phase * .18 * motion_scale(count)) % 1.0
        frame = [averaged_pixel(index, count, lambda p: _mix(_scale(primary, .03), secondary,
                 max(.02, moving_head_strength(p, head, count, comet=True)))) for index in range(count)]
    elif cfg.effect_id == "wave":
        frame = [averaged_pixel(index, count, lambda p: _mix(primary, secondary,
                 .5 + .5 * math.sin((p * 2 - phase * .30) * math.tau))) for index in range(count)]
    elif cfg.effect_id == "pulse":
        local = (abs(phase) * 0.44) % 1.0
        strength = max(0.05, math.exp(-55 * (local - 0.12) ** 2), math.exp(-55 * (local - 0.34) ** 2))
        left, right = (primary, secondary) if int(abs(phase) * .44) % 2 == 0 else (secondary, primary)
        transition = smooth_fraction(max(0.0, min(1.0, (local - .70) / .30)))
        base, flash_color = _mix(left, right, transition), _mix(right, left, transition)
        frame = [_mix(_scale(base, 0.06), flash_color, strength)] * count
    elif cfg.effect_id == "alternating":
        amount = .5 + .5 * math.cos(abs(phase) * 2 * math.pi)
        frame = [_mix(primary, secondary, amount if index % 2 else 1 - amount) for index in range(count)]
    elif cfg.effect_id == "sparkle":
        bucket = math.floor(abs(phase) * 8)
        rng = random.Random(cfg.seed + bucket)
        next_rng = random.Random(cfg.seed + bucket + 1)
        blend = smooth_fraction(abs(phase) * 8 - bucket)
        frame = []
        for _index in range(count):
            sparkle = rng.random()
            amount = sparkle**12 * (1 - blend) + next_rng.random()**12 * blend
            frame.append(_mix(_scale(primary, 0.18), secondary, amount))
    elif cfg.effect_id == "converge":
        local = (phase * 0.22) % 1.0
        travel = smooth_fraction(min(1.0, local / 0.78))
        left_head, right_head = 0.5 * travel, 1.0 - 0.5 * travel
        width = max(0.035, 1.8 / count)
        burst = smooth_fraction(max(0.0, min(1.0, (local - 0.78) / 0.22)))
        frame = []
        for index in range(count):
            position = (index + 0.5) / count
            distance = min(abs(position - left_head), abs(position - right_head))
            head = math.exp(-0.5 * (distance / width) ** 2)
            centre = math.exp(-0.5 * ((position - 0.5) / max(width, 0.09)) ** 2) * burst
            frame.append(_mix(_scale(primary, 0.10 + 0.16 * centre), secondary, max(head, centre)))
    elif cfg.effect_id == "crossflow":
        left_head = (phase * 0.16) % 1.0
        right_head = (-phase * 0.13) % 1.0
        width = max(0.045, 2.2 / count)
        frame = []
        for index in range(count):
            position = (index + 0.5) / count
            left_distance = min(abs(position - left_head), 1.0 - abs(position - left_head))
            right_distance = min(abs(position - right_head), 1.0 - abs(position - right_head))
            left = math.exp(-0.5 * (left_distance / width) ** 2)
            right = math.exp(-0.5 * (right_distance / width) ** 2)
            frame.append(_mix(_scale(primary, 0.08 + 0.92 * left), secondary, right))
    elif cfg.effect_id == "depthwave":
        frame = [averaged_pixel(index, count, lambda position: _mix(
            _scale(primary, 0.10 + 0.20 * (0.5 + 0.5 * math.sin((position * 3.0 + phase * 0.12) * math.tau))),
            secondary,
            smooth_fraction(0.5 + 0.5 * math.sin((position * 1.35 - phase * 0.20) * math.tau)),
        )) for index in range(count)]
    else:  # normalized() currently makes this unreachable
        frame = [primary] * count

    brightness = cfg.brightness / 100.0
    return [_scale(color, brightness) for color in frame]


def render_hex_frame(config: RGBEffectConfig, led_count: int, elapsed_seconds: float) -> list[str]:
    return [rgb_to_hex(color) for color in render_effect(config, led_count, elapsed_seconds)]
