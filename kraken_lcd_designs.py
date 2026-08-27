#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Rounded 240 x 240 hardware dashboards for Kraken Control.

The renderer is intentionally independent from Qt and liquidctl.  This keeps
preview generation deterministic and allows every layout to be tested without
connected hardware.
"""

from __future__ import annotations

from datetime import datetime

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageSequence


LCD_SIZE = 240
DEFAULT_ACCENT = "#00c8ff"
DEFAULT_LABEL_COLOR = "#8ba2b5"
DEFAULT_VALUE_COLOR = "#f2f8fc"

COLOR_PRESETS: tuple[tuple[str, str], ...] = (
    ("Eisblau", DEFAULT_ACCENT),
    ("Neongrün", "#39ff88"),
    ("Orange", "#ff9a32"),
    ("Rot", "#ff4058"),
    ("Gold", "#ffd54a"),
    ("Weiß", "#f4f7ff"),
    ("Lila", "#a855f7"),
)

DESIGNS: tuple[tuple[str, str], ...] = (
    ("water_halo", "Wasser · Halo"),
    ("cpu_orbit", "CPU · Orbit"),
    ("gpu_arc", "GPU · Arc"),
    ("cpu_gpu_dual", "CPU + GPU · Dual"),
    ("system_trio", "Wasser + CPU + GPU · Trio"),
    ("neon_grid", "System · Neonraster"),
    ("radar_sweep", "System · Radar"),
    ("liquid_wave", "Wasser · Wellenkern"),
)

LABELS: dict[str, dict[str, str]] = {
    "de": {"water": "WASSER", "cpu": "CPU", "gpu": "GPU", "system": "SYSTEM", "live": "LIVE", "last": "LETZTER WERT"},
    "en": {"water": "LIQUID", "cpu": "CPU", "gpu": "GPU", "system": "SYSTEM", "live": "LIVE", "last": "LAST VALUE"},
    "es": {"water": "LÍQUIDO", "cpu": "CPU", "gpu": "GPU", "system": "SISTEMA", "live": "EN VIVO", "last": "ÚLTIMO VALOR"},
    "fr": {"water": "LIQUIDE", "cpu": "CPU", "gpu": "GPU", "system": "SYSTÈME", "live": "DIRECT", "last": "DERNIÈRE VALEUR"},
}


def normalize_hex_color(value: str) -> str | None:
    """Return a canonical #rrggbb color or None for invalid input."""
    text = value.strip().lower()
    if text and not text.startswith("#"):
        text = "#" + text
    if len(text) != 7:
        return None
    try:
        int(text[1:], 16)
    except ValueError:
        return None
    return text


def _font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    names = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/google-noto/NotoSans-Bold.ttf" if bold else "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
    )
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def _rgb(value: str) -> tuple[int, int, int]:
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]


def _mix(color: tuple[int, int, int], other: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(a + (b - a) * amount) for a, b in zip(color, other))


def _temperature(value: float | None, unit: str = "c") -> str:
    normalized = "f" if str(unit).casefold() == "f" else "c"
    suffix = "°F" if normalized == "f" else "°C"
    if value is None:
        return f"--{suffix}"
    displayed = value * 9.0 / 5.0 + 32.0 if normalized == "f" else value
    return f"{displayed:.0f}{suffix}"


class _Canvas:
    """A 2x supersampled drawing canvas with logical 240 px coordinates."""

    scale = 2

    def __init__(
        self,
        accent: str,
        label_color: str = DEFAULT_LABEL_COLOR,
        value_color: str = DEFAULT_VALUE_COLOR,
        label_scale_percent: int = 125,
        value_scale_percent: int = 125,
        temperature_unit: str = "c",
        phase: float = 0.0,
    ):
        self.accent = _rgb(accent)
        self.label_color = _rgb(label_color)
        self.value_color = _rgb(value_color)
        self.label_scale = max(0.60, min(2.00, label_scale_percent / 100.0))
        self.value_scale = max(0.60, min(2.00, value_scale_percent / 100.0))
        self.temperature_unit = "f" if str(temperature_unit).casefold() == "f" else "c"
        self.phase = phase % 1.0
        self.background = (7, 13, 21)
        self.panel = (14, 25, 37)
        self.muted = (118, 139, 157)
        self.white = (242, 248, 252)
        self.image = Image.new("RGB", (LCD_SIZE * self.scale, LCD_SIZE * self.scale), self.background)
        self.draw = ImageDraw.Draw(self.image)
        self.draw.ellipse(self.box(4, 4, 236, 236), fill=(8, 15, 24), outline=_mix(self.accent, self.background, 0.55), width=2 * self.scale)

    def box(self, x1: float, y1: float, x2: float, y2: float) -> tuple[int, int, int, int]:
        s = self.scale
        return round(x1 * s), round(y1 * s), round(x2 * s), round(y2 * s)

    def text(
        self,
        text: str,
        y: float,
        size: int,
        color: tuple[int, int, int],
        *,
        bold: bool = False,
        center_x: float = 120,
        max_width: float = 210,
        scale_kind: str = "none",
    ) -> None:
        scale = self.label_scale if scale_kind == "label" else self.value_scale if scale_kind == "value" else 1.0
        logical_size = max(7, round(size * scale))
        font = _font(logical_size * self.scale, bold=bold)
        bounds = self.draw.textbbox((0, 0), text, font=font)
        width = bounds[2] - bounds[0]
        while width > max_width * self.scale and logical_size > 7:
            logical_size -= 1
            font = _font(logical_size * self.scale, bold=bold)
            bounds = self.draw.textbbox((0, 0), text, font=font)
            width = bounds[2] - bounds[0]
        self.draw.text((center_x * self.scale - width / 2, y * self.scale), text, font=font, fill=color)

    def label(self, text: str, y: float, *, center_x: float = 120) -> None:
        self.text(text, y, 12, self.label_color, bold=True, center_x=center_x, max_width=82, scale_kind="label")

    def value(self, value: float | None, y: float, *, size: int = 47, center_x: float = 120) -> None:
        self.text(
            _temperature(value, self.temperature_unit),
            y,
            size,
            self.value_color,
            bold=True,
            center_x=center_x,
            max_width=96 if center_x != 120 else 180,
            scale_kind="value",
        )

    def rounded_panel(self, x1: float, y1: float, x2: float, y2: float, radius: float = 18) -> None:
        self.draw.rounded_rectangle(self.box(x1, y1, x2, y2), radius=radius * self.scale, fill=self.panel, outline=_mix(self.accent, self.background, 0.68), width=self.scale)

    def finish(self) -> Image.Image:
        return self.image.resize((LCD_SIZE, LCD_SIZE), Image.Resampling.LANCZOS)


def _draw_focus(
    canvas: _Canvas,
    label: str,
    value: float | None,
    *,
    style: str,
    status: str | None = None,
    status_live: bool = False,
) -> None:
    rotation = canvas.phase * 360.0
    if style == "halo":
        canvas.draw.arc(canvas.box(25, 25, 215, 215), 205 + rotation, 505 + rotation, fill=_mix(canvas.accent, canvas.white, 0.12), width=9 * canvas.scale)
        canvas.draw.arc(canvas.box(38, 38, 202, 202), 212 - rotation * 0.65, 498 - rotation * 0.65, fill=_mix(canvas.accent, canvas.background, 0.48), width=3 * canvas.scale)
    elif style == "orbit":
        canvas.draw.arc(canvas.box(23, 23, 217, 217), 155 + rotation, 385 + rotation, fill=canvas.accent, width=7 * canvas.scale)
        for offset, radius, dot_size in ((0.0, 94.0, 10.0), (0.44, 82.0, 8.0)):
            angle = 2 * math.pi * (canvas.phase + offset)
            x = 120 + math.cos(angle) * radius
            y = 120 + math.sin(angle) * radius
            canvas.draw.ellipse(canvas.box(x - dot_size / 2, y - dot_size / 2, x + dot_size / 2, y + dot_size / 2), fill=canvas.white if offset == 0 else _mix(canvas.accent, canvas.white, 0.3))
    else:
        canvas.draw.arc(canvas.box(24, 24, 216, 216), 200 + rotation, 520 + rotation, fill=canvas.accent, width=8 * canvas.scale)
        canvas.draw.arc(canvas.box(35, 35, 205, 205), 25 - rotation * 0.8, 155 - rotation * 0.8, fill=_mix(canvas.accent, canvas.background, 0.52), width=4 * canvas.scale)
    canvas.label(label, 66)
    canvas.value(value, 91, size=54)


def _draw_dual(
    canvas: _Canvas,
    cpu: float | None,
    gpu: float | None,
    labels: dict[str, str],
    *,
    show_sensor_status: bool = False,
) -> None:
    pulse = (math.sin(canvas.phase * math.tau) + 1.0) / 2.0
    canvas.text(labels["system"], 28, 12, canvas.label_color, bold=True, scale_kind="label")
    canvas.rounded_panel(22, 65, 116, 179, 22)
    canvas.rounded_panel(124, 65, 218, 179, 22)
    for index, center_x in enumerate((69, 171)):
        color = canvas.accent if index == 0 else _mix(canvas.accent, canvas.white, 0.35)
        start = -90 + canvas.phase * 360 * (1 if index == 0 else -1)
        canvas.draw.arc(canvas.box(center_x - 35, 92, center_x + 35, 162), start, start + 245, fill=color, width=4 * canvas.scale)
        dot_angle = math.radians(start + 245)
        dot_x = center_x + math.cos(dot_angle) * 35
        dot_y = 127 + math.sin(dot_angle) * 35
        canvas.draw.ellipse(canvas.box(dot_x - 3, dot_y - 3, dot_x + 3, dot_y + 3), fill=canvas.white)
    canvas.label(labels["cpu"], 71, center_x=69)
    canvas.label(labels["gpu"], 71, center_x=171)
    canvas.value(cpu, 109, size=31, center_x=69)
    canvas.value(gpu, 109, size=31, center_x=171)
    bar_width = 44 + 20 * pulse
    canvas.draw.rounded_rectangle(canvas.box(120 - bar_width, 190, 120 + bar_width, 196), radius=3 * canvas.scale, fill=_mix(canvas.accent, canvas.white, 0.18))


def _draw_trio(
    canvas: _Canvas,
    liquid: float | None,
    cpu: float | None,
    gpu: float | None,
    labels: dict[str, str],
    *,
    show_sensor_status: bool = False,
) -> None:
    canvas.text(labels["system"], 22, 12, canvas.label_color, bold=True, scale_kind="label")
    values = ((labels["water"], liquid, 62), (labels["cpu"], cpu, 120), (labels["gpu"], gpu, 178))
    for index, (label, value, center_x) in enumerate(values):
        color = canvas.accent if index != 2 else _mix(canvas.accent, canvas.white, 0.32)
        canvas.draw.ellipse(canvas.box(center_x - 25, 66, center_x + 25, 116), fill=canvas.panel, outline=_mix(color, canvas.background, 0.6), width=2 * canvas.scale)
        rotation = canvas.phase * 360 * (1 if index != 1 else -1) + index * 110
        canvas.draw.arc(canvas.box(center_x - 27, 64, center_x + 27, 118), rotation, rotation + 210, fill=color, width=4 * canvas.scale)
        canvas.text(
            _temperature(value, canvas.temperature_unit), 79, 18, canvas.value_color,
            bold=True, center_x=center_x, max_width=52, scale_kind="value",
        )
        canvas.text(
            label, 126, 9, canvas.label_color, bold=True,
            center_x=center_x, max_width=55, scale_kind="label",
        )
    canvas.rounded_panel(39, 159, 201, 184, 12)
    canvas.draw.rounded_rectangle(canvas.box(49, 168, 191, 175), radius=4 * canvas.scale, fill=_mix(canvas.accent, canvas.background, 0.45))
    travel = 92 * (0.5 - 0.5 * math.cos(canvas.phase * math.tau))
    canvas.draw.rounded_rectangle(canvas.box(49 + travel, 168, 89 + travel, 175), radius=4 * canvas.scale, fill=canvas.accent)


def _draw_neon_grid(
    canvas: _Canvas,
    cpu: float | None,
    gpu: float | None,
    labels: dict[str, str],
) -> None:
    horizon = 142
    for row in range(6):
        y = horizon + row * row * 2.4
        canvas.draw.line(
            (28 * canvas.scale, y * canvas.scale, 212 * canvas.scale, y * canvas.scale),
            fill=_mix(canvas.accent, canvas.background, 0.62),
            width=canvas.scale,
        )
    travel = (canvas.phase * 34.0) % 17.0
    for column in range(-6, 7):
        bottom_x = 120 + column * 24 + travel
        canvas.draw.line((120 * canvas.scale, horizon * canvas.scale, bottom_x * canvas.scale, 224 * canvas.scale), fill=_mix(canvas.accent, canvas.background, 0.68), width=canvas.scale)
    canvas.text(labels["system"], 27, 11, canvas.label_color, bold=True, scale_kind="label")
    canvas.rounded_panel(38, 57, 202, 132, 18)
    canvas.label(labels["cpu"], 65, center_x=79)
    canvas.label(labels["gpu"], 65, center_x=161)
    canvas.value(cpu, 86, size=26, center_x=79)
    canvas.value(gpu, 86, size=26, center_x=161)
    scan_y = 146 + (canvas.phase * 70.0)
    canvas.draw.line((42 * canvas.scale, scan_y * canvas.scale, 198 * canvas.scale, scan_y * canvas.scale), fill=canvas.accent, width=2 * canvas.scale)


def _draw_radar(
    canvas: _Canvas,
    cpu: float | None,
    gpu: float | None,
    labels: dict[str, str],
) -> None:
    center = (120, 112)
    for radius in (30, 56, 82):
        canvas.draw.ellipse(canvas.box(120 - radius, 112 - radius, 120 + radius, 112 + radius), outline=_mix(canvas.accent, canvas.background, 0.72), width=canvas.scale)
    for angle in (0, math.pi / 2, math.pi, math.pi * 1.5):
        canvas.draw.line((120 * canvas.scale, 112 * canvas.scale, (120 + math.cos(angle) * 82) * canvas.scale, (112 + math.sin(angle) * 82) * canvas.scale), fill=_mix(canvas.accent, canvas.background, 0.78), width=canvas.scale)
    angle = canvas.phase * math.tau - math.pi / 2
    tip = (120 + math.cos(angle) * 82, 112 + math.sin(angle) * 82)
    canvas.draw.line((center[0] * canvas.scale, center[1] * canvas.scale, tip[0] * canvas.scale, tip[1] * canvas.scale), fill=canvas.accent, width=4 * canvas.scale)
    canvas.draw.ellipse(canvas.box(tip[0] - 4, tip[1] - 4, tip[0] + 4, tip[1] + 4), fill=canvas.white)
    canvas.text(labels["cpu"] + " " + _temperature(cpu, canvas.temperature_unit), 198, 10, canvas.value_color, bold=True, center_x=70, max_width=90, scale_kind="value")
    canvas.text(labels["gpu"] + " " + _temperature(gpu, canvas.temperature_unit), 198, 10, canvas.value_color, bold=True, center_x=170, max_width=90, scale_kind="value")


def _draw_liquid_wave(
    canvas: _Canvas,
    liquid: float | None,
    labels: dict[str, str],
) -> None:
    canvas.label(labels["water"], 49)
    canvas.value(liquid, 72, size=52)
    for band in range(5):
        points: list[tuple[int, int]] = []
        for x in range(22, 219, 4):
            y = 160 + band * 10 + math.sin((x / 36.0) + canvas.phase * math.tau + band * 0.7) * (8 - band)
            points.append((x * canvas.scale, round(y * canvas.scale)))
        color = _mix(canvas.accent, canvas.background, min(0.72, 0.18 + band * 0.13))
        canvas.draw.line(points, fill=color, width=max(canvas.scale, (5 - band) * canvas.scale))


def compose_hardware_layer(
    background: Image.Image,
    overlay: Image.Image,
    *,
    opacity_percent: int = 82,
    scale_percent: int = 88,
    x_percent: int = 50,
    y_percent: int = 50,
) -> Image.Image:
    """Place a hardware dashboard over a 240×240 background image."""
    base = background.convert("RGBA").resize((LCD_SIZE, LCD_SIZE), Image.Resampling.LANCZOS)
    scale = max(40, min(125, int(scale_percent))) / 100.0
    size = max(48, round(LCD_SIZE * scale))
    layer = overlay.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    opacity = max(10, min(100, int(opacity_percent))) / 100.0
    alpha = layer.getchannel("A").point(lambda value: round(value * opacity))
    layer.putalpha(alpha)
    center_x = round(max(0, min(100, int(x_percent))) / 100.0 * LCD_SIZE)
    center_y = round(max(0, min(100, int(y_percent))) / 100.0 * LCD_SIZE)
    base.alpha_composite(layer, (center_x - size // 2, center_y - size // 2))
    return base.convert("RGB")


def overlay_clock_on_frame(
    image: Image.Image,
    *,
    enabled: bool = False,
    use_24h: bool = True,
    show_date: bool = True,
    font_size: int = 64,
    text_color_hex: str = "#ffffff",
    background_color_hex: str = "#10141c",
    now: datetime | None = None,
) -> Image.Image:
    """Add a compact clock layer to an already composed animated LCD frame."""
    if not enabled:
        return image.convert("RGB")
    now = now or datetime.now()
    base = image.convert("RGBA")
    draw = ImageDraw.Draw(base, "RGBA")
    text_color = normalize_hex_color(text_color_hex) or "#ffffff"
    bg_color = normalize_hex_color(background_color_hex) or "#10141c"
    tc = tuple(int(text_color[i:i+2], 16) for i in (1, 3, 5))
    bc = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
    main_size = max(24, min(58, int(round(font_size * 0.62))))
    date_size = max(12, int(round(main_size * 0.38)))
    try:
        main_font = ImageFont.truetype("DejaVuSans-Bold.ttf", main_size)
        date_font = ImageFont.truetype("DejaVuSans.ttf", date_size)
    except OSError:
        main_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
    if use_24h:
        clock_text = now.strftime("%H:%M")
    else:
        clock_text = now.strftime("%I:%M %p").lstrip("0")
    date_text = now.strftime("%d.%m.%Y")
    cb = draw.textbbox((0, 0), clock_text, font=main_font)
    cw, ch = cb[2] - cb[0], cb[3] - cb[1]
    db = draw.textbbox((0, 0), date_text, font=date_font)
    dw, dh = db[2] - db[0], db[3] - db[1]
    total_h = ch + (dh + 3 if show_date else 0)
    box_w = min(LCD_SIZE - 16, max(cw, dw if show_date else 0) + 22)
    box_h = total_h + 14
    left = (LCD_SIZE - box_w) // 2
    top = 8
    draw.rounded_rectangle((left, top, left + box_w, top + box_h), radius=10, fill=(*bc, 150), outline=(*tc, 65), width=1)
    tx = LCD_SIZE / 2 - cw / 2 - cb[0]
    ty = top + 6 - cb[1]
    draw.text((tx, ty), clock_text, font=main_font, fill=(*tc, 255))
    if show_date:
        dx = LCD_SIZE / 2 - dw / 2 - db[0]
        dy = top + 7 + ch + 2 - db[1]
        draw.text((dx, dy), date_text, font=date_font, fill=(*tc, 220))
    return base.convert("RGB")


def render_hardware_frame(
    design_id: str,
    accent_hex: str,
    liquid: float | None,
    cpu: float | None,
    gpu: float | None,
    *,
    language: str = "de",
    font_scale_percent: int = 125,
    label_color_hex: str = DEFAULT_LABEL_COLOR,
    value_color_hex: str = DEFAULT_VALUE_COLOR,
    label_scale_percent: int | None = None,
    value_scale_percent: int | None = None,
    temperature_unit: str = "c",
    phase: float = 0.0,
    live_sensor_status: bool = False,
) -> Image.Image:
    """Render one static or animated hardware frame."""
    accent = normalize_hex_color(accent_hex)
    if accent is None:
        raise ValueError("accent_hex must be a color in #RRGGBB format")
    valid_designs = {identifier for identifier, _label in DESIGNS}
    if design_id not in valid_designs:
        raise ValueError(f"unknown hardware design: {design_id}")
    label_color = normalize_hex_color(label_color_hex)
    value_color = normalize_hex_color(value_color_hex)
    if label_color is None or value_color is None:
        raise ValueError("label/value colors must use #RRGGBB")
    labels = LABELS.get(language, LABELS["de"])
    canvas = _Canvas(
        accent,
        label_color,
        value_color,
        font_scale_percent if label_scale_percent is None else label_scale_percent,
        font_scale_percent if value_scale_percent is None else value_scale_percent,
        temperature_unit,
        phase,
    )
    if design_id == "water_halo":
        _draw_focus(canvas, labels["water"], liquid, style="halo", status=labels["last"] if live_sensor_status else None)
    elif design_id == "cpu_orbit":
        _draw_focus(canvas, labels["cpu"], cpu, style="orbit", status=labels["live"] if live_sensor_status else None, status_live=live_sensor_status)
    elif design_id == "gpu_arc":
        _draw_focus(canvas, labels["gpu"], gpu, style="arc", status=labels["live"] if live_sensor_status else None, status_live=live_sensor_status)
    elif design_id == "cpu_gpu_dual":
        _draw_dual(canvas, cpu, gpu, labels, show_sensor_status=live_sensor_status)
    elif design_id == "system_trio":
        _draw_trio(canvas, liquid, cpu, gpu, labels, show_sensor_status=live_sensor_status)
    elif design_id == "neon_grid":
        _draw_neon_grid(canvas, cpu, gpu, labels)
    elif design_id == "radar_sweep":
        _draw_radar(canvas, cpu, gpu, labels)
    else:
        _draw_liquid_wave(canvas, liquid, labels)
    return canvas.finish()


def render_hardware_design(
    design_id: str,
    accent_hex: str,
    liquid: float | None,
    cpu: float | None,
    gpu: float | None,
    output_path: str | Path,
    *,
    language: str = "de",
    font_scale_percent: int = 125,
    label_color_hex: str = DEFAULT_LABEL_COLOR,
    value_color_hex: str = DEFAULT_VALUE_COLOR,
    label_scale_percent: int | None = None,
    value_scale_percent: int | None = None,
    temperature_unit: str = "c",
) -> Path:
    """Render a localized hardware dashboard and return its PNG path."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    render_hardware_frame(
        design_id,
        accent_hex,
        liquid,
        cpu,
        gpu,
        language=language,
        font_scale_percent=font_scale_percent,
        label_color_hex=label_color_hex,
        value_color_hex=value_color_hex,
        label_scale_percent=label_scale_percent,
        value_scale_percent=value_scale_percent,
        temperature_unit=temperature_unit,
    ).save(destination, format="PNG", optimize=True)
    return destination


def render_hardware_animation(
    design_id: str,
    accent_hex: str,
    liquid: float | None,
    cpu: float | None,
    gpu: float | None,
    output_path: str | Path,
    *,
    language: str = "de",
    font_scale_percent: int = 125,
    label_color_hex: str = DEFAULT_LABEL_COLOR,
    value_color_hex: str = DEFAULT_VALUE_COLOR,
    label_scale_percent: int | None = None,
    value_scale_percent: int | None = None,
    temperature_unit: str = "c",
    fps: int = 25,
    seconds: float = 1.0,
) -> Path:
    """Generate a seamless animated GIF for the existing CAM-raw streamer."""
    fps = max(10, min(25, int(fps)))
    frame_count = max(12, round(fps * max(0.6, min(2.0, seconds))))
    frames = [
        render_hardware_frame(
            design_id,
            accent_hex,
            liquid,
            cpu,
            gpu,
            language=language,
            font_scale_percent=font_scale_percent,
            label_color_hex=label_color_hex,
            value_color_hex=value_color_hex,
            label_scale_percent=label_scale_percent,
            value_scale_percent=value_scale_percent,
            temperature_unit=temperature_unit,
            phase=index / frame_count,
        )
        for index in range(frame_count)
    ]
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        destination,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / fps),
        loop=0,
        disposal=2,
        optimize=False,
    )
    return destination


def render_layered_hardware_animation(
    background_path: str | Path,
    design_id: str,
    accent_hex: str,
    liquid: float | None,
    cpu: float | None,
    gpu: float | None,
    output_path: str | Path,
    *,
    language: str = "de",
    label_color_hex: str = DEFAULT_LABEL_COLOR,
    value_color_hex: str = DEFAULT_VALUE_COLOR,
    label_scale_percent: int = 125,
    value_scale_percent: int = 125,
    temperature_unit: str = "c",
    fps: int = 25,
    overlay_animated: bool = True,
    opacity_percent: int = 82,
    scale_percent: int = 88,
    x_percent: int = 50,
    y_percent: int = 50,
    clock_enabled: bool = False,
    clock_use_24h: bool = True,
    clock_show_date: bool = True,
    clock_font_size: int = 64,
    clock_text_color_hex: str = "#ffffff",
    clock_background_color_hex: str = "#10141c",
) -> Path:
    """Generate a short preview of an image/GIF plus hardware-data layer."""
    fps = max(10, min(25, int(fps)))
    source_frames: list[tuple[Image.Image, int]] = []
    with Image.open(background_path) as source:
        if source.width * source.height > 50_000_000:
            raise ValueError("Das Ebenen-Hintergrundbild ist zu groß (maximal 50 Megapixel).")
        default_duration = max(20, int(source.info.get("duration", 100) or 100))
        for index, frame in enumerate(ImageSequence.Iterator(source)):
            if index >= 250:
                break
            rgba = frame.convert("RGBA")
            side = min(rgba.size)
            left = (rgba.width - side) // 2
            top = (rgba.height - side) // 2
            prepared = rgba.crop((left, top, left + side, top + side)).resize(
                (LCD_SIZE, LCD_SIZE), Image.Resampling.LANCZOS
            )
            source_frames.append((prepared, max(20, int(frame.info.get("duration", default_duration) or default_duration))))
    if not source_frames:
        raise ValueError("Der Ebenen-Hintergrund enthält kein lesbares Bild.")
    total_ms = max(1000, min(4000, sum(duration for _frame, duration in source_frames)))
    frame_count = max(12, round(total_ms / 1000.0 * fps))
    starts: list[int] = []
    cursor = 0
    for _frame, duration in source_frames:
        starts.append(cursor)
        cursor += duration
    source_total = max(1, cursor)
    frames: list[Image.Image] = []
    for index in range(frame_count):
        time_ms = round(index / fps * 1000) % source_total
        source_index = max(0, min(len(starts) - 1, sum(1 for start in starts if start <= time_ms) - 1))
        overlay = render_hardware_frame(
            design_id,
            accent_hex,
            liquid,
            cpu,
            gpu,
            language=language,
            label_color_hex=label_color_hex,
            value_color_hex=value_color_hex,
            label_scale_percent=label_scale_percent,
            value_scale_percent=value_scale_percent,
            temperature_unit=temperature_unit,
            phase=(index / fps) % 1.0 if overlay_animated else 0.0,
            live_sensor_status=True,
        )
        composed = compose_hardware_layer(
            source_frames[source_index][0],
            overlay,
            opacity_percent=opacity_percent,
            scale_percent=scale_percent,
            x_percent=x_percent,
            y_percent=y_percent,
        )
        composed = overlay_clock_on_frame(
            composed, enabled=clock_enabled, use_24h=clock_use_24h, show_date=clock_show_date,
            font_size=clock_font_size, text_color_hex=clock_text_color_hex,
            background_color_hex=clock_background_color_hex,
        )
        frames.append(composed)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        destination,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / fps),
        loop=0,
        disposal=2,
        optimize=False,
    )
    return destination
