#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Render OHC's bundled 1600x720 Levita Layer-2 themes.

Five themes use small CC0 components from Kenney packs; four are original OHC
drawings.  The generated ``01.png`` stays transparent so live hardware values
from ``trcc.json`` remain readable over every Layer-1 background.  The three
Nebula Drift layouts retain the original faint translucent artwork and add
small dark backings only immediately behind their live values.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


WIDTH, HEIGHT, SAFE_RIGHT = 1600, 720, 1520
# Empirical correction from a photographed 1600x720 Levita: TRCC's physical
# font is about 22% wider and 12% taller than the Noto/DejaVu preview metrics.
# The bitmap pill therefore reserves calibrated device space automatically for
# every configured value instead of depending on a hand-sized rectangle.
TRCC_TEXT_WIDTH_FACTOR = 1.22
TRCC_TEXT_HEIGHT_FACTOR = 1.12
VALUE_PILL_HORIZONTAL_PADDING = 56
VALUE_PILL_VERTICAL_PADDING = 36
MIN_VALUE_PILL_WIDTH = 168
MIN_VALUE_PILL_HEIGHT = 76
TRCC_FONT_FAMILY = "DejaVu Sans"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "src" / "assets" / "levita-designs"
FONT_CANDIDATES = {
    False: (
        Path("/usr/share/fonts/google-noto/NotoSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ),
    True: (
        Path("/usr/share/fonts/google-noto/NotoSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ),
}


@dataclass(frozen=True)
class ThemeSpec:
    directory: str
    title: str
    style: str
    accent: str
    secondary: str
    elements: tuple[dict[str, Any], ...]
    source_pack: str = ""
    source_url: str = ""
    source_asset: str = ""


@dataclass(frozen=True)
class NebulaSpec:
    directory: str
    title: str
    elements: tuple[dict[str, Any], ...]


def metric(ident: str, x: int, y: int, key: str, fmt: str, color: str, size: int = 34) -> dict[str, Any]:
    return {
        "id": ident, "type": "metric", "x": x, "y": y, "metric": key,
        "format": fmt, "color": color, "size": size, "bold": True,
        "name": TRCC_FONT_FAMILY, "show_unit": True,
    }


def clock(ident: str, x: int, y: int, color: str, size: int = 66) -> dict[str, Any]:
    return {
        "id": ident, "type": "clock", "x": x, "y": y, "source": "time",
        "format": "{value}", "color": color, "size": size, "bold": True,
        "name": TRCC_FONT_FAMILY,
    }


THEMES = (
    ThemeSpec(
        "kenney-space-console", "Space Console", "space_console", "#42d7ff", "#826dff",
        (clock("clock", 760, 118, "#ffffff", 62),
         metric("cpu-temp", 270, 280, "cpu:temp", "CPU  {value:.0f}°C", "#65e6ff", 38),
         metric("cpu-load", 270, 370, "cpu:usage", "LOAD  {value:.0f}%", "#ffffff", 30),
         metric("gpu-temp", 1240, 280, "gpu:primary:temp", "GPU  {value:.0f}°C", "#aa9cff", 38),
         metric("gpu-load", 1240, 370, "gpu:primary:usage", "LOAD  {value:.0f}%", "#ffffff", 30),
         metric("ram", 760, 600, "memory:percent", "RAM  {value:.0f}%", "#85f5d5", 32)),
        "Kenney UI Pack: Sci-Fi", "https://kenney.nl/assets/ui-pack-sci-fi",
        "ui-sci-fi/PNG/Blue/Double/crosshair_color_a.png",
    ),
    ThemeSpec(
        "kenney-orbital-reticle", "Orbital Reticle", "orbital_reticle", "#7df4ff", "#ff8dd7",
        (clock("clock", 760, 105, "#ffffff", 58),
         metric("cpu", 390, 335, "cpu:usage", "CPU  {value:.0f}%", "#7df4ff", 42),
         metric("cpu-temp", 390, 420, "cpu:temp", "{value:.0f}°C", "#ffffff", 30),
         metric("gpu", 1110, 335, "gpu:primary:usage", "GPU  {value:.0f}%", "#ff8dd7", 42),
         metric("gpu-temp", 1110, 420, "gpu:primary:temp", "{value:.0f}°C", "#ffffff", 30),
         metric("power", 760, 605, "cpu:power", "CPU POWER  {value:.0f} W", "#bba7ff", 28)),
        "Kenney Crosshair Pack", "https://kenney.nl/assets/crosshair-pack",
        "crosshair/PNG/Outline (2×)/crosshair-190.png",
    ),
    ThemeSpec(
        "kenney-navigator-grid", "Navigator Grid", "navigator_grid", "#74ffc8", "#55aaff",
        (clock("clock", 245, 105, "#ffffff", 54),
         metric("cpu-temp", 250, 270, "cpu:temp", "CPU  {value:.0f}°C", "#74ffc8", 38),
         metric("gpu-temp", 250, 375, "gpu:primary:temp", "GPU  {value:.0f}°C", "#75b9ff", 38),
         metric("ram", 250, 480, "memory:percent", "RAM  {value:.0f}%", "#ffffff", 34),
         metric("net-down", 1130, 580, "net:down", "DOWN  {value:.0f}", "#74ffc8", 27),
         metric("net-up", 1360, 580, "net:up", "UP  {value:.0f}", "#75b9ff", 27)),
        "Kenney Minimap Pack", "https://kenney.nl/assets/minimap-pack",
        "minimap/Tiles/Style C/tile_0012.png",
    ),
    ThemeSpec(
        "kenney-ambient-glow", "Ambient Glow", "ambient_glow", "#5ce7ff", "#9c7cff",
        (clock("clock", 760, 250, "#ffffff", 92),
         metric("cpu", 330, 565, "cpu:temp", "CPU  {value:.0f}°C", "#5ce7ff", 38),
         metric("gpu", 760, 565, "gpu:primary:temp", "GPU  {value:.0f}°C", "#9c7cff", 38),
         metric("ram", 1190, 565, "memory:percent", "RAM  {value:.0f}%", "#70ffd1", 38)),
        "Kenney Light Masks", "https://kenney.nl/assets/light-masks",
        "light-masks/Transparent/water_caustics_a.png",
    ),
    ThemeSpec(
        "kenney-clean-telemetry", "Clean Telemetry", "clean_telemetry", "#34c8ff", "#7c95ff",
        (clock("clock", 760, 92, "#ffffff", 50),
         metric("cpu-temp", 260, 255, "cpu:temp", "CPU  {value:.0f}°C", "#60dcff", 34),
         metric("cpu-load", 260, 390, "cpu:usage", "LOAD  {value:.0f}%", "#ffffff", 30),
         metric("gpu-temp", 760, 255, "gpu:primary:temp", "GPU  {value:.0f}°C", "#9aaaff", 34),
         metric("gpu-load", 760, 390, "gpu:primary:usage", "LOAD  {value:.0f}%", "#ffffff", 30),
         metric("ram", 1260, 255, "memory:percent", "RAM  {value:.0f}%", "#72f4cf", 34),
         metric("disk", 1260, 390, "disk:activity", "DISK  {value:.0f}%", "#ffffff", 30)),
        "Kenney UI Pack", "https://kenney.nl/assets/ui-pack",
        "ui-pack/PNG/Blue/Double/button_rectangle_depth_border.png",
    ),
    ThemeSpec(
        "ohc-orbit", "OHC Orbit", "ohc_orbit", "#56e5ff", "#a47cff",
        (clock("clock", 760, 106, "#ffffff", 58),
         metric("cpu", 380, 338, "cpu:temp", "CPU  {value:.0f}°C", "#56e5ff", 40),
         metric("cpu-load", 380, 425, "cpu:usage", "{value:.0f}% LOAD", "#ffffff", 28),
         metric("gpu", 1140, 338, "gpu:primary:temp", "GPU  {value:.0f}°C", "#a47cff", 40),
         metric("gpu-load", 1140, 425, "gpu:primary:usage", "{value:.0f}% LOAD", "#ffffff", 28),
         metric("ram", 760, 607, "memory:percent", "RAM  {value:.0f}%", "#73ffd5", 30)),
    ),
    ThemeSpec(
        "ohc-aqua-pulse", "OHC Aqua Pulse", "aqua_pulse", "#46f0ef", "#2f80ff",
        (clock("clock", 760, 105, "#ffffff", 58),
         metric("cpu-temp", 285, 290, "cpu:temp", "CPU  {value:.0f}°C", "#46f0ef", 38),
         metric("gpu-temp", 285, 405, "gpu:primary:temp", "GPU  {value:.0f}°C", "#76aaff", 38),
         metric("cpu-power", 1170, 290, "cpu:power", "CPU  {value:.0f} W", "#46f0ef", 32),
         metric("gpu-power", 1170, 405, "gpu:primary:power", "GPU  {value:.0f} W", "#76aaff", 32),
         metric("ram", 760, 595, "memory:percent", "MEMORY  {value:.0f}%", "#ffffff", 30)),
    ),
    ThemeSpec(
        "ohc-horizon-glass", "OHC Horizon Glass", "horizon_glass", "#8ee8ff", "#ffb469",
        (clock("clock", 760, 150, "#ffffff", 78),
         metric("cpu", 300, 510, "cpu:temp", "CPU  {value:.0f}°C", "#8ee8ff", 36),
         metric("gpu", 700, 510, "gpu:primary:temp", "GPU  {value:.0f}°C", "#b4a7ff", 36),
         metric("ram", 1100, 510, "memory:percent", "RAM  {value:.0f}%", "#ffbf7d", 36),
         metric("disk", 1400, 610, "disk:activity", "SSD  {value:.0f}%", "#ffffff", 25)),
    ),
    ThemeSpec(
        "ohc-split-core", "OHC Split Core", "split_core", "#45d9ff", "#ff5da8",
        (clock("clock", 760, 100, "#ffffff", 54),
         metric("cpu-temp", 340, 285, "cpu:temp", "CPU  {value:.0f}°C", "#45d9ff", 42),
         metric("cpu-clock", 340, 410, "cpu:freq", "{value:.0f} MHz", "#ffffff", 28),
         metric("gpu-temp", 1130, 285, "gpu:primary:temp", "GPU  {value:.0f}°C", "#ff5da8", 42),
         metric("gpu-clock", 1130, 410, "gpu:primary:clock", "{value:.0f} MHz", "#ffffff", 28),
         metric("ram", 760, 600, "memory:percent", "RAM  {value:.0f}%", "#a99cff", 30)),
    ),
    ThemeSpec(
        "ohc-spectrum-ring", "OHC Spectrum Ring", "spectrum_ring", "#36e7ff", "#ff4fcb",
        (metric("cpu-temp", 760, 315, "cpu:temp", "{value:.0f}°C", "#ffffff", 96),
         metric("cpu-load", 760, 415, "cpu:usage", "CPU  {value:.0f}%", "#8ff7ff", 30),
         metric("gpu-temp", 260, 335, "gpu:primary:temp", "GPU  {value:.0f}°C", "#ff72d5", 38),
         metric("ram", 1260, 335, "memory:percent", "RAM  {value:.0f}%", "#8cff78", 38),
         clock("clock", 760, 605, "#ffe08a", 42)),
    ),
    ThemeSpec(
        "ohc-neon-double-arc", "OHC Neon Double Arc", "neon_double_arc", "#21e7ff", "#ff43b7",
        (metric("cpu-temp", 400, 310, "cpu:temp", "{value:.0f}°C", "#ffffff", 78),
         metric("cpu-load", 400, 405, "cpu:usage", "CPU  {value:.0f}%", "#72efff", 30),
         metric("gpu-temp", 1110, 310, "gpu:primary:temp", "{value:.0f}°C", "#ffffff", 78),
         metric("gpu-load", 1110, 405, "gpu:primary:usage", "GPU  {value:.0f}%", "#ff82d1", 30),
         metric("ram", 755, 585, "memory:percent", "RAM  {value:.0f}%", "#91ff78", 34),
         clock("clock", 755, 100, "#ffffff", 42)),
    ),
    ThemeSpec(
        "ohc-prism-segments", "OHC Prism Segments", "prism_segments", "#8b65ff", "#ffba43",
        (metric("cpu-load", 760, 305, "cpu:usage", "{value:.0f}%", "#ffffff", 92),
         metric("cpu-temp", 760, 405, "cpu:temp", "CPU  {value:.0f}°C", "#79efff", 30),
         metric("gpu-temp", 260, 235, "gpu:primary:temp", "GPU  {value:.0f}°C", "#ff78d5", 36),
         metric("gpu-power", 260, 470, "gpu:primary:power", "GPU  {value:.0f} W", "#ffba62", 30),
         metric("cpu-power", 1260, 235, "cpu:power", "CPU  {value:.0f} W", "#72eaff", 30),
         metric("ram", 1260, 470, "memory:percent", "RAM  {value:.0f}%", "#8dff73", 36),
         clock("clock", 760, 620, "#d8c7ff", 38)),
    ),
    ThemeSpec(
        "ohc-aurora-radar", "OHC Aurora Radar", "aurora_radar", "#4bffe1", "#b65cff",
        (clock("clock", 760, 92, "#ffffff", 44),
         metric("cpu-temp", 420, 300, "cpu:temp", "CPU  {value:.0f}°C", "#63f5e3", 42),
         metric("cpu-load", 420, 390, "cpu:usage", "LOAD  {value:.0f}%", "#ffffff", 29),
         metric("gpu-temp", 1090, 300, "gpu:primary:temp", "GPU  {value:.0f}°C", "#c987ff", 42),
         metric("gpu-load", 1090, 390, "gpu:primary:usage", "LOAD  {value:.0f}%", "#ffffff", 29),
         metric("ram", 760, 585, "memory:percent", "MEMORY  {value:.0f}%", "#9dff75", 34)),
    ),
)


NEBULA_THEMES = (
    NebulaSpec(
        "ohc-nebula-drift", "OHC Nebula Drift · System",
        (clock("clock", 760, 245, "#ffffff", 92),
         metric("cpu-temp", 430, 505, "cpu:temp", "CPU  {value:.0f}°C", "#5ee7ff", 38),
         metric("gpu-temp", 760, 505, "gpu:primary:temp", "GPU  {value:.0f}°C", "#8ca7ff", 38),
         metric("ram", 1090, 505, "memory:percent", "RAM  {value:.0f}%", "#c79cff", 38)),
    ),
    NebulaSpec(
        "ohc-nebula-drift-minimal", "OHC Nebula Drift · Minimal",
        (clock("clock", 760, 178, "#ffffff", 92),
         metric("cpu-temp", 410, 570, "cpu:temp", "CPU  {value:.0f}°C", "#5ee7ff", 40),
         metric("gpu-temp", 1110, 570, "gpu:primary:temp", "GPU  {value:.0f}°C", "#b39aff", 40)),
    ),
    NebulaSpec(
        "ohc-nebula-drift-performance", "OHC Nebula Drift · Leistung",
        (clock("clock", 760, 82, "#ffffff", 48),
         metric("cpu-load", 310, 230, "cpu:usage", "CPU  {value:.0f}%", "#5ee7ff", 34),
         metric("cpu-temp", 310, 350, "cpu:temp", "TEMP  {value:.0f}°C", "#ffffff", 30),
         metric("cpu-clock", 310, 470, "cpu:freq", "{value:.0f} MHz", "#8ddfff", 28),
         metric("gpu-load", 1210, 230, "gpu:primary:usage", "GPU  {value:.0f}%", "#b39aff", 34),
         metric("gpu-temp", 1210, 350, "gpu:primary:temp", "TEMP  {value:.0f}°C", "#ffffff", 30),
         metric("gpu-clock", 1210, 470, "gpu:primary:clock", "{value:.0f} MHz", "#c6adff", 28),
         metric("ram", 760, 625, "memory:percent", "RAM  {value:.0f}%", "#87f1d0", 30)),
    ),
)


def rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    color = hex_color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16), alpha


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES[bool(bold)]:
        try:
            return ImageFont.truetype(str(path), size)
        except OSError:
            continue
    return ImageFont.load_default()


def tint_asset(path: Path, size: tuple[int, int], color: str, alpha: int = 180) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    source.thumbnail(size, Image.Resampling.LANCZOS)
    mask = source.getchannel("A")
    if mask.getextrema() == (255, 255):
        mask = ImageOps.grayscale(source)
    mask = mask.point(lambda value: value * alpha // 255)
    result = Image.new("RGBA", source.size, rgba(color, 255))
    result.putalpha(mask)
    return result


def paste_center(canvas: Image.Image, asset: Image.Image, x: int, y: int) -> None:
    canvas.alpha_composite(asset, (x - asset.width // 2, y - asset.height // 2))


def draw_clock_card(
    draw: ImageDraw.ImageDraw,
    element: dict[str, Any],
    accent: str,
    secondary: str,
) -> None:
    """Give floating clocks a compact layered-glass frame."""

    x, y = int(element["x"]), int(element["y"])
    size = int(element["size"])
    width = max(176, round(size * 3.35))
    height = max(76, round(size * 1.28))
    left, top = x - width // 2, y - height // 2
    right, bottom = x + width // 2, y + height // 2
    radius = min(32, height // 2)
    draw.rounded_rectangle(
        (left - 5, top - 5, right + 5, bottom + 5), radius + 4,
        fill=(2, 7, 18, 36), outline=rgba(secondary, 48), width=2,
    )
    draw.rounded_rectangle(
        (left, top, right, bottom), radius,
        fill=(1, 7, 18, 174), outline=rgba(accent, 155), width=2,
    )
    draw.line((left + radius, top + 5, right - radius, top + 5), fill=rgba("#ffffff", 58), width=1)
    draw.line((left + 24, bottom - 6, left + width // 3, bottom - 6), fill=rgba(accent, 150), width=3)
    draw.line((right - width // 3, bottom - 6, right - 24, bottom - 6), fill=rgba(secondary, 150), width=3)


def draw_overlay(spec: ThemeSpec, kenney_root: Path | None) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    a, b = spec.accent, spec.secondary
    draw.rounded_rectangle((28, 24, SAFE_RIGHT - 28, HEIGHT - 24), 34, outline=rgba(a, 115), width=2)
    draw.line((80, 62, 530, 62), fill=rgba(a, 170), width=3)
    draw.line((990, 62, 1440, 62), fill=rgba(b, 170), width=3)

    if spec.style == "space_console":
        for x in (80, 560, 1040):
            draw.rounded_rectangle((x, 175, x + 400, 470), 28, fill=(2, 12, 25, 82), outline=rgba(a if x < 800 else b, 155), width=3)
        draw.line((180, 530, 1340, 530), fill=rgba(a, 100), width=2)
    elif spec.style == "clean_telemetry":
        draw.rounded_rectangle((115, 65, 1405, 135), 26, fill=(2, 11, 23, 112), outline=rgba(a, 135), width=2)
        for x, color in ((80, a), (560, a), (1040, b)):
            draw.rounded_rectangle((x, 190, x + 400, 445), 18, fill=(2, 10, 20, 105), outline=rgba(color, 110), width=2)
            draw.line((x + 26, 235, x + 374, 235), fill=rgba(color, 170), width=2)
            draw.line((x + 26, 420, x + 150, 420), fill=rgba(color, 105), width=3)
    elif spec.style == "orbital_reticle":
        for x, color in ((390, a), (1110, b)):
            draw.ellipse((x - 185, 150, x + 185, 520), outline=rgba(color, 135), width=4)
            draw.arc((x - 145, 190, x + 145, 480), 22, 158, fill=rgba(color, 225), width=7)
            draw.arc((x - 145, 190, x + 145, 480), 202, 338, fill=rgba(color, 225), width=7)
        draw.line((570, 335, 930, 335), fill=rgba("#ffffff", 80), width=2)
    elif spec.style == "ohc_orbit":
        draw.ellipse((585, 190, 935, 540), outline=rgba("#ffffff", 42), width=2)
        draw.arc((510, 115, 1010, 615), 205, 342, fill=rgba(a, 205), width=7)
        draw.arc((510, 115, 1010, 615), 25, 162, fill=rgba(b, 205), width=7)
        draw.ellipse((728, 328, 792, 392), fill=(3, 14, 30, 155), outline=rgba("#ffffff", 170), width=2)
        for x, color in ((380, a), (1140, b)):
            draw.rounded_rectangle((x - 205, 240, x + 205, 492), 58, fill=(2, 11, 26, 112), outline=rgba(color, 145), width=3)
            draw.arc((x - 170, 275, x + 170, 455), 190, 350, fill=rgba(color, 210), width=5)
        draw.rounded_rectangle((590, 560, 930, 650), 36, fill=(2, 12, 26, 118), outline=rgba(a, 115), width=2)
    elif spec.style == "navigator_grid":
        for x in range(520, 1460, 94):
            draw.line((x, 160, x, 520), fill=rgba(a, 48), width=1)
        for y in range(160, 521, 72):
            draw.line((520, y, 1460, y), fill=rgba(b, 48), width=1)
        draw.rectangle((90, 165, 410, 535), fill=(2, 16, 22, 92), outline=rgba(a, 155), width=3)
        draw.line((520, 545, 1460, 545), fill=rgba(a, 135), width=3)
    elif spec.style == "ambient_glow":
        for x, y, radius, color in ((260, 260, 220, a), (760, 310, 280, b), (1260, 260, 220, a)):
            for step in range(10, 0, -1):
                r = radius * step // 10
                draw.ellipse((x-r, y-r, x+r, y+r), outline=rgba(color, 8 + step * 5), width=5)
        draw.rounded_rectangle((130, 500, 1390, 650), 42, fill=(1, 15, 26, 76), outline=rgba(a, 120), width=2)
    elif spec.style == "aqua_pulse":
        for inset, alpha in ((0, 165), (35, 110), (70, 70)):
            draw.arc((130 + inset, 120 + inset // 2, 1390 - inset, 650 - inset // 3), 198, 342, fill=rgba(a, alpha), width=5)
            draw.arc((130 + inset, 65 + inset // 3, 1390 - inset, 595 - inset // 2), 18, 162, fill=rgba(b, alpha), width=4)
        for x, color in ((285, a), (1170, b)):
            draw.rounded_rectangle((x - 190, 220, x + 190, 470), 72, fill=(0, 20, 30, 105), outline=rgba(color, 155), width=3)
            draw.line((x - 130, 350, x + 130, 350), fill=rgba(color, 95), width=2)
        draw.rounded_rectangle((555, 545, 965, 642), 44, fill=(1, 17, 28, 118), outline=rgba(a, 125), width=2)
    elif spec.style == "horizon_glass":
        draw.rounded_rectangle((120, 330, 1410, 610), 48, fill=(6, 18, 32, 96), outline=rgba(a, 125), width=3)
        draw.line((170, 455, 1360, 455), fill=rgba(b, 115), width=2)
        for x in (500, 900):
            draw.line((x, 480, x, 575), fill=rgba("#ffffff", 45), width=2)
    elif spec.style == "split_core":
        draw.polygon(((80, 150), (675, 150), (610, 535), (80, 535)), fill=(3, 22, 36, 90), outline=rgba(a, 170))
        draw.polygon(((840, 150), (1450, 150), (1450, 535), (905, 535)), fill=(30, 5, 24, 76), outline=rgba(b, 170))
        draw.line((728, 160, 675, 525), fill=rgba(a, 180), width=4)
        draw.line((790, 160, 845, 525), fill=rgba(b, 180), width=4)
    elif spec.style == "spectrum_ring":
        palette = ("#ff466f", "#ff9f3f", "#ffe44d", "#65ef70", "#34dcff", "#6978ff", "#c15cff", "#ff4fc4")
        bounds = (480, 70, 1040, 630)
        for index, color in enumerate(palette):
            start = -92 + index * 45
            draw.arc(bounds, start + 4, start + 39, fill=rgba(color, 72), width=12)
            glow = tuple(value + 18 for value in bounds)
            draw.arc(glow, start + 6, start + 37, fill=rgba(color, 34), width=6)
        draw.ellipse((555, 145, 965, 555), fill=(2, 7, 19, 174), outline=rgba("#ffffff", 48), width=2)
        for x, color in ((260, "#ff72d5"), (1260, "#8cff78")):
            draw.rounded_rectangle((x - 190, 260, x + 190, 420), 54, fill=(3, 9, 24, 142), outline=rgba(color, 170), width=3)
    elif spec.style == "neon_double_arc":
        palette = ("#ff4d7a", "#ffb347", "#f7f75a", "#50ef8b", "#3ee6ff", "#7c72ff", "#de58ff")
        for center, reverse in ((400, False), (1110, True)):
            bounds = (center - 235, 105, center + 235, 575)
            draw.ellipse((center - 174, 166, center + 174, 514), fill=(2, 8, 23, 166), outline=rgba("#ffffff", 38), width=2)
            for index, color in enumerate(palette):
                shade = palette[-index - 1] if reverse else color
                start = -205 + index * 51
                draw.arc(bounds, start + 5, start + 44, fill=rgba(shade, 230), width=17)
        draw.line((640, 340, 870, 340), fill=rgba("#ffffff", 62), width=2)
        draw.rounded_rectangle((590, 535, 920, 635), 38, fill=(3, 10, 25, 146), outline=rgba("#91ff78", 150), width=2)
    elif spec.style == "prism_segments":
        palette = ("#4ce8ff", "#6675ff", "#a65dff", "#f34fc1", "#ff666e", "#ffb448", "#e9f45b", "#66ee83")
        center = (760, 350)
        for ring, width, alpha in ((270, 18, 235), (230, 7, 105)):
            bounds = (center[0] - ring, center[1] - ring, center[0] + ring, center[1] + ring)
            for index, color in enumerate(palette):
                start = -90 + index * 45
                draw.arc(bounds, start + 7, start + 38, fill=rgba(color, alpha), width=width)
        draw.polygon(((760, 125), (950, 240), (900, 490), (760, 575), (620, 490), (570, 240)), fill=(3, 7, 23, 157), outline=rgba("#b580ff", 125))
        for x, y, color in ((260, 235, "#ff78d5"), (260, 470, "#ffba62"), (1260, 235, "#72eaff"), (1260, 470, "#8dff73")):
            draw.rounded_rectangle((x - 175, y - 58, x + 175, y + 58), 32, fill=(2, 9, 24, 138), outline=rgba(color, 145), width=2)
    elif spec.style == "aurora_radar":
        palette = ("#49ffe0", "#44c7ff", "#716cff", "#c258ff", "#ff55bf", "#ff9e55", "#c8f95a")
        for radius, alpha in ((300, 190), (250, 120), (200, 75)):
            bounds = (760 - radius, 355 - radius, 760 + radius, 355 + radius)
            for index, color in enumerate(palette):
                start = 198 + index * 24
                draw.arc(bounds, start, start + 17, fill=rgba(color, alpha), width=max(4, radius // 30))
        draw.line((760, 150, 760, 535), fill=rgba("#ffffff", 38), width=1)
        draw.line((555, 355, 965, 355), fill=rgba("#ffffff", 38), width=1)
        for x, color in ((420, "#4bffe1"), (1090, "#b65cff")):
            draw.rounded_rectangle((x - 205, 230, x + 205, 455), 64, fill=(2, 9, 25, 142), outline=rgba(color, 165), width=3)
        draw.rounded_rectangle((565, 540, 955, 635), 40, fill=(2, 9, 24, 148), outline=rgba("#9dff75", 145), width=2)

    for element in spec.elements:
        if element.get("type") == "clock":
            draw_clock_card(draw, element, a, b)

    if kenney_root is not None and spec.source_asset:
        asset_path = kenney_root / spec.source_asset
        if not asset_path.is_file():
            raise FileNotFoundError(f"Missing Kenney source asset: {asset_path}")
        if spec.style == "space_console":
            asset = tint_asset(asset_path, (130, 130), a, 210)
            paste_center(image, asset, 760, 335)
        elif spec.style == "orbital_reticle":
            asset = tint_asset(asset_path, (245, 245), "#ffffff", 155)
            paste_center(image, asset, 390, 335)
            paste_center(image, asset, 1110, 335)
        elif spec.style == "navigator_grid":
            asset = tint_asset(asset_path, (280, 280), a, 115)
            for x, y in ((670, 270), (950, 340), (1230, 245), (760, 465), (1320, 455)):
                paste_center(image, asset, x, y)
        elif spec.style == "ambient_glow":
            asset = tint_asset(asset_path, (720, 600), a, 32)
            paste_center(image, asset, 480, 330)
            paste_center(image, asset.transpose(Image.Transpose.FLIP_LEFT_RIGHT), 1090, 330)
        elif spec.style == "clean_telemetry":
            asset = tint_asset(asset_path, (360, 120), a, 125)
            for x in (280, 760, 1240):
                paste_center(image, asset, x, 320)
    return image


def preview_text(element: dict[str, Any]) -> str:
    if element["type"] == "clock":
        return "13:38"
    samples = {
        "cpu:temp": 52, "cpu:usage": 31, "cpu:freq": 4850, "cpu:power": 92,
        "gpu:primary:temp": 48, "gpu:primary:usage": 44, "gpu:primary:clock": 2715,
        "gpu:primary:power": 188, "memory:percent": 42, "disk:activity": 18,
        "net:down": 850, "net:up": 120,
    }
    return str(element.get("format", "{value}")).format(value=samples.get(str(element.get("metric")), 42))


def draw_preview(overlay: Image.Image, spec: ThemeSpec) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), "#030914")
    bg = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        bg.line((0, y, WIDTH, y), fill=(3 + y // 90, 9 + y // 55, 20 + y // 38, 255))
    image.alpha_composite(overlay)
    draw = ImageDraw.Draw(image)
    for element in spec.elements:
        text = preview_text(element)
        draw.text(
            (int(element["x"]), int(element["y"])), text,
            font=font(int(element["size"]), bool(element.get("bold"))),
            fill=str(element["color"]), anchor="mm", stroke_width=1, stroke_fill="#06101d",
        )
    draw.rectangle((SAFE_RIGHT, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 200))
    return image.convert("RGB")


def write_theme(output: Path, spec: ThemeSpec, overlay: Image.Image) -> None:
    target = output / spec.directory
    target.mkdir(parents=True, exist_ok=True)
    overlay.save(target / "01.png", optimize=True)
    draw_preview(overlay, spec).save(target / "Theme.png", optimize=True)
    payload = {
        "name": spec.title, "width": WIDTH, "height": HEIGHT,
        "overlay_enabled": True, "elements": list(spec.elements),
    }
    (target / "trcc.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if spec.source_pack:
        provenance = (
            f"Decorative component: {spec.source_pack}\n\n"
            f"Source: {spec.source_url}\n\nLicense: CC0 1.0 Universal\n\n"
            f"Source asset used by the renderer: `{spec.source_asset}`\n"
        )
    else:
        provenance = "Artwork and layout: original Open Hardware Control design, GPL-3.0-or-later.\n"
    (target / "README.md").write_text(
        f"# {spec.title}\n\nBundled 1600×720 Layer-2 theme for the Thermalright Levita display.\n\n{provenance}",
        encoding="utf-8",
    )


def _nebula_backings(spec: NebulaSpec) -> Image.Image:
    """Draw value-sized glass pills while leaving all other pixels clear."""

    surface = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(surface)
    for element in spec.elements:
        sample = preview_text(element)
        text_font = font(int(element["size"]), bool(element.get("bold")))
        left, top, right, bottom = draw.textbbox(
            (0, 0), sample, font=text_font, anchor="mm", stroke_width=2,
        )
        preview_width = right - left
        preview_height = bottom - top
        pill_width = max(
            MIN_VALUE_PILL_WIDTH,
            math.ceil(preview_width * TRCC_TEXT_WIDTH_FACTOR) + VALUE_PILL_HORIZONTAL_PADDING,
        )
        pill_height = max(
            MIN_VALUE_PILL_HEIGHT,
            math.ceil(preview_height * TRCC_TEXT_HEIGHT_FACTOR) + VALUE_PILL_VERTICAL_PADDING,
        )
        half_width = math.ceil(pill_width / 2)
        half_height = math.ceil(pill_height / 2)
        x, y = int(element["x"]), int(element["y"])
        accent = str(element["color"])
        draw.rounded_rectangle(
            (x - half_width, y - half_height, x + half_width, y + half_height),
            radius=min(28, half_height), fill=(0, 3, 12, 154),
            outline=rgba(accent, 145), width=2,
        )
    return surface


def _nebula_preview(overlay: Image.Image, spec: NebulaSpec, background_path: Path) -> Image.Image:
    """Composite a bundled video thumbnail behind the translucent layer."""

    if background_path.is_file():
        background = Image.open(background_path).convert("RGB").resize(
            (WIDTH, HEIGHT), Image.Resampling.LANCZOS,
        )
        preview = background.convert("RGBA")
    else:
        preview = Image.new("RGBA", (WIDTH, HEIGHT), "#071323")
    preview.alpha_composite(overlay)
    draw = ImageDraw.Draw(preview)
    for element in spec.elements:
        draw.text(
            (int(element["x"]), int(element["y"])), preview_text(element),
            font=font(int(element["size"]), bool(element.get("bold"))),
            fill=str(element["color"]), anchor="mm", stroke_width=2, stroke_fill="#020711",
        )
    draw.rectangle((SAFE_RIGHT, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 205))
    return preview.convert("RGB")


def render_nebula_drift(output: Path, requested: set[str]) -> int:
    """Build three layouts from the preserved original translucent artwork."""

    source = output / "ohc-nebula-drift" / "source-overlay.png"
    if not source.is_file():
        raise FileNotFoundError("Nebula Drift source-overlay.png is missing")
    artwork = Image.open(source).convert("RGBA")
    if artwork.size != (WIDTH, HEIGHT):
        raise ValueError(f"Nebula Drift source must be {WIDTH}x{HEIGHT}, got {artwork.size}")
    if artwork.getchannel("A").getextrema()[0] != 0:
        raise ValueError("Nebula Drift source must retain transparent pixels")
    background = (
        PROJECT_ROOT / "src" / "assets" / "display-effects"
        / "landscape-steens-mountain-original.jpg"
    )
    rendered = 0
    for spec in NEBULA_THEMES:
        if spec.directory not in requested:
            continue
        target = output / spec.directory
        target.mkdir(parents=True, exist_ok=True)
        overlay = Image.alpha_composite(artwork, _nebula_backings(spec))
        overlay.save(target / "01.png", optimize=True)
        _nebula_preview(overlay, spec, background).save(target / "Theme.png", optimize=True)
        payload = {
            "name": spec.title, "width": WIDTH, "height": HEIGHT,
            "overlay_enabled": True, "elements": list(spec.elements),
        }
        (target / "trcc.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
        )
        (target / "README.md").write_text(
            f"# {spec.title}\n\n"
            "Bundled 1600×720 Layer-2 theme for the Thermalright Levita display.\n\n"
            "The faint translucent Nebula Drift artwork and layout are original Open Hardware "
            "Control assets, GPL-3.0-or-later. Small dark pills sit only behind live values; "
            "the selected Layer-1 video remains visible everywhere else.\n",
            encoding="utf-8",
        )
        rendered += 1
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kenney-root", type=Path, help="Directory containing the five extracted Kenney pack folders")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--theme", action="append",
        choices=tuple(spec.directory for spec in THEMES) + tuple(spec.directory for spec in NEBULA_THEMES),
        help="Render only the named theme; repeat to render several themes",
    )
    parser.add_argument(
        "--preview-only", action="store_true",
        help="Rebuild Theme.png from the existing 01.png without source-pack access",
    )
    args = parser.parse_args()
    kenney_root = args.kenney_root.resolve() if args.kenney_root else None
    requested = set(args.theme or (spec.directory for spec in THEMES))
    rendered = 0
    for spec in THEMES:
        if spec.directory not in requested:
            continue
        if args.preview_only:
            overlay_path = args.output.resolve() / spec.directory / "01.png"
            if not overlay_path.is_file():
                raise FileNotFoundError(f"Existing overlay is missing: {overlay_path}")
            draw_preview(Image.open(overlay_path).convert("RGBA"), spec).save(
                args.output.resolve() / spec.directory / "Theme.png", optimize=True,
            )
        else:
            if spec.source_pack and kenney_root is None:
                raise SystemExit("--kenney-root is required for the five CC0-derived themes")
            write_theme(args.output.resolve(), spec, draw_overlay(spec, kenney_root))
        rendered += 1
    if requested.intersection(spec.directory for spec in NEBULA_THEMES):
        rendered += render_nebula_drift(args.output.resolve(), requested)
    print(f"Rendered {rendered} Levita Layer-2 themes in {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
