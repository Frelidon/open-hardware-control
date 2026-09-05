#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Safe Thermalright Levita display integration helpers.

Open Hardware Control deliberately delegates the USB wire protocol to the
separately installed GPL-3.0 ``trcc-linux`` backend.  This module owns only
local media discovery, Levita geometry, validation and bounded CLI argument
construction.  It performs no USB I/O on import and is usable in tests without
PySide6 or connected hardware.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
from typing import Callable, Iterable, Sequence

from modules.lcd_levita.v1_4.panel_geometry import DEFAULT_INNER_CORNER_RADIUS


THERMALRIGHT_DEVICE_KEY = "87ad:70db"
LEVITA_WIDTH = 1600
LEVITA_HEIGHT = 720

# Verified by the upstream TRCC Linux PM=64/SUB=3 variant table.  The Levita
# has an 80 px physical panel cutout on the right edge.  Content may extend
# behind it, but movable information must stay outside this rectangle.
LEVITA_CUTOUT_X = 1520
LEVITA_CUTOUT_Y = 0
LEVITA_CUTOUT_WIDTH = 80
LEVITA_CUTOUT_HEIGHT = 720

# The photographed Levita setup aligns with the protocol table's 80 px right
# edge.  The render mask remains user-adjustable for panel revisions.
DEFAULT_NOTCH_MASK_WIDTH = 80
MAX_NOTCH_MASK_WIDTH = 800
# The physical 1600×720 panel has a small outer-right radius. The independently
# configurable inner image/notch radii live in the versioned Levita module.
DEFAULT_NOTCH_CORNER_RADIUS = 18
DEFAULT_BACKGROUND_OFFSET_X = 0
DEFAULT_BACKGROUND_OFFSET_Y = 0

MEDIA_SCALE_CONTAIN = "contain"
MEDIA_SCALE_COVER = "cover"
MEDIA_SCALE_MODES = frozenset({MEDIA_SCALE_CONTAIN, MEDIA_SCALE_COVER})

# Exact static catalog metadata from TRCC Linux's CzhordeCatalog.  The category
# is encoded in each cloud theme ID; no network access or media-content
# guessing is required to classify an already downloaded local file.
TRCC_CLOUD_CATEGORIES: tuple[tuple[str, str, int], ...] = (
    ("a", "Gallery", 82),
    ("b", "Tech", 25),
    ("c", "HUD", 72),
    ("d", "Light", 55),
    ("e", "Nature", 54),
    ("y", "Aesthetic", 10),
)
TRCC_CLOUD_CATEGORY_LIMITS = {
    prefix: count for prefix, _name, count in TRCC_CLOUD_CATEGORIES
}
MEDIA_CATEGORY_LABELS: dict[str, str] = {
    "ohc": "OHC-Designs",
} | {
    prefix: name for prefix, name, _count in TRCC_CLOUD_CATEGORIES
} | {
    "own": "Eigene Dateien",
}

SUPPORTED_IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".bmp", ".webp"})
SUPPORTED_VIDEO_SUFFIXES = frozenset({".mp4", ".mov", ".webm", ".mkv", ".avi", ".zt"})
SUPPORTED_MEDIA_SUFFIXES = SUPPORTED_IMAGE_SUFFIXES | SUPPORTED_VIDEO_SUFFIXES
MAX_MEDIA_FILES = 2500
MAX_NATIVE_THEME_CONFIG_BYTES = 2_000_000
MIN_LAYER_INTENSITY = 25
MAX_LAYER_INTENSITY = 150


@dataclass(frozen=True, slots=True)
class MediaEntry:
    path: Path
    relative_name: str
    kind: str


@dataclass(frozen=True, slots=True)
class PreparedMedia:
    path: Path
    transformed: bool = False
    warning: str = ""


@dataclass(frozen=True, slots=True)
class OverlaySpec:
    ident: str
    label: str
    kind: str
    metric: str = ""
    source: str = ""
    format: str = "{value}"
    sample: str = ""
    x: int = 0
    y: int = 0
    size: int = 48
    color: str = "#ffffff"
    visible: bool = True
    show_unit: bool = True
    bold: bool = True

    def bounded(self, *, safe_right_x: int = LEVITA_CUTOUT_X) -> "OverlaySpec":
        right = max(1, min(LEVITA_WIDTH, int(safe_right_x)))
        return replace(
            self,
            x=max(0, min(right - 1, int(self.x))),
            y=max(0, min(LEVITA_HEIGHT - 1, int(self.y))),
            size=max(12, min(160, int(self.size))),
            color=normalize_color(self.color),
        )


DEFAULT_OVERLAYS: tuple[OverlaySpec, ...] = (
    OverlaySpec("ohc-cpu-temp", "CPU-Temperatur", "metric", "cpu:temp", format="CPU {value:.0f}°C", sample="CPU 51 °C", x=200, y=540, size=38, color="#32c5ff", show_unit=True),
    OverlaySpec("ohc-cpu-load", "CPU-Auslastung", "metric", "cpu:usage", format="CPU {value:.0f}%", sample="CPU 18 %", x=200, y=630, size=38, color="#32c5ff", show_unit=True),
    OverlaySpec("ohc-gpu-temp", "GPU-Temperatur", "metric", "gpu:primary:temp", format="GPU {value:.0f}°C", sample="GPU 47 °C", x=600, y=540, size=38, color="#44d7b6", show_unit=True),
    OverlaySpec("ohc-gpu-load", "GPU-Auslastung", "metric", "gpu:primary:usage", format="GPU {value:.0f}%", sample="GPU 32 %", x=600, y=630, size=38, color="#44d7b6", show_unit=True),
    OverlaySpec("ohc-memory", "Arbeitsspeicher", "metric", "memory:percent", format="RAM {value:.0f}%", sample="RAM 41 %", x=1000, y=540, size=38, color="#6dd401", show_unit=True),
    OverlaySpec("ohc-clock", "Uhrzeit", "clock", source="time", format="{value}", sample="13:38", x=1000, y=630, size=38, color="#ffffff"),
)


@dataclass(frozen=True, slots=True)
class CommandResult:
    ok: bool
    args: tuple[str, ...]
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0

    @property
    def message(self) -> str:
        return (self.stdout or self.stderr).strip()


def normalize_color(value: str) -> str:
    text = str(value).strip().lower()
    if not text.startswith("#"):
        text = "#" + text
    if not re.fullmatch(r"#[0-9a-f]{6}", text):
        return "#ffffff"
    return text


def bounded_layer_intensity(value: object, default: int = 100) -> int:
    """Return the user-facing layer emphasis within the supported range."""
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        parsed = int(default)
    return max(MIN_LAYER_INTENSITY, min(MAX_LAYER_INTENSITY, parsed))


def adjust_rgb_intensity(color: str, percent: int) -> str:
    """Dim or brighten an RGB colour while preserving its hue."""
    value = normalize_color(color)
    level = bounded_layer_intensity(percent)
    channels = [int(value[index:index + 2], 16) for index in (1, 3, 5)]
    if level <= 100:
        channels = [round(channel * level / 100.0) for channel in channels]
    else:
        blend = (level - 100) / 100.0
        channels = [round(channel + (255 - channel) * blend) for channel in channels]
    return "#" + "".join(f"{max(0, min(255, channel)):02x}" for channel in channels)


def find_trcc_executable() -> str | None:
    """Find a system or pipx/user installation without mutating PATH."""
    resolved = shutil.which("trcc")
    if resolved:
        return resolved
    candidate = Path.home() / ".local" / "bin" / "trcc"
    return str(candidate) if candidate.is_file() and candidate.stat().st_mode & 0o111 else None


def default_trcc_design_directory(home: Path | None = None) -> Path | None:
    """Return TRCC Linux's installed 1600x720 landscape design directory.

    The verified Levita PM=64/SUB=3 profile uses this exact geometry.  Other
    TRCC theme folders (for example 480x480 or portrait 720x1600) must not be
    offered as drop-in Levita layouts because their saved value positions do
    not match this display.
    """

    base = (home or Path.home()).expanduser()
    candidate = base / ".trcc" / "data" / "theme1600720l"
    if candidate.is_symlink() or not candidate.is_dir():
        return None
    for child in candidate.iterdir():
        if child.is_symlink() or not child.is_dir():
            continue
        config = child / "config1.dc"
        artwork = tuple(child / name for name in ("Theme.png", "00.png"))
        if (
            config.is_file()
            and not config.is_symlink()
            and any(item.is_file() and not item.is_symlink() for item in artwork)
        ):
            return candidate.resolve()
    return None


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    """Read a PNG's IHDR dimensions without loading the complete image."""

    try:
        with path.open("rb") as stream:
            header = stream.read(24)
    except OSError:
        return None
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def levita_theme_has_matching_geometry(theme_dir: Path, scan_root: Path) -> bool:
    """Reject TRCC layouts for square/portrait panels in broad imports."""

    try:
        relative_parts = theme_dir.resolve().relative_to(scan_root.resolve()).parts
    except ValueError:
        relative_parts = theme_dir.resolve().parts
    geometry_parts = (*scan_root.resolve().parts[-2:], *relative_parts)
    if any("1600720l" in part.casefold() for part in geometry_parts):
        return True
    for name in ("Theme.png", "00.png"):
        dimensions = _png_dimensions(theme_dir / name)
        if dimensions == (LEVITA_WIDTH, LEVITA_HEIGHT):
            return True
    return False


def scan_media_directory(root: Path, *, limit: int = MAX_MEDIA_FILES) -> list[MediaEntry]:
    """Return supported local media without copying or following symlinks."""
    directory = root.expanduser().resolve()
    if not directory.is_dir():
        raise ValueError(f"Kein lesbarer Designordner: {directory}")
    bounded_limit = max(1, min(MAX_MEDIA_FILES, int(limit)))
    entries: list[MediaEntry] = []
    theme_dirs: set[Path] = set()
    config_candidates = {
        *directory.rglob("config1.dc"),
        *directory.rglob("trcc.json"),
    }
    for config in sorted(config_candidates, key=lambda item: item.as_posix().casefold()):
        theme_dir = config.parent
        if (
            config.is_symlink()
            or theme_dir.is_symlink()
            or theme_dir.resolve() in theme_dirs
            or _theme_import_contains_symlink(theme_dir)
        ):
            continue
        if (
            trcc_theme_is_supported(theme_dir)
            and levita_theme_has_matching_geometry(theme_dir, directory)
        ):
            entries.append(MediaEntry(
                path=theme_dir.resolve(),
                relative_name=theme_dir.relative_to(directory).as_posix() + " · TRCC-Layout",
                kind="theme",
            ))
            theme_dirs.add(theme_dir.resolve())
            if len(entries) >= bounded_limit:
                return entries
    for path in sorted(directory.rglob("*"), key=lambda item: item.as_posix().casefold()):
        if len(entries) >= bounded_limit:
            break
        if path.is_symlink() or not path.is_file():
            continue
        if path.parent.resolve() in theme_dirs:
            continue
        suffix = path.suffix.casefold()
        if suffix not in SUPPORTED_MEDIA_SUFFIXES:
            continue
        entries.append(MediaEntry(
            path=path.resolve(),
            relative_name=path.relative_to(directory).as_posix(),
            kind="image" if suffix in SUPPORTED_IMAGE_SUFFIXES else "video",
        ))
    return entries


def _theme_import_contains_symlink(theme_dir: Path) -> bool:
    """Keep directory imports from following linked TRCC theme inputs.

    This is deliberately an import-boundary rule. OHC's own editable cache
    links already validated source artwork into a private staging directory,
    so the runtime theme validator must be able to consume those links.
    """

    names = (
        "config1.dc", "trcc.json", "Theme.png", "00.png", "01.png",
        "Theme.zt", "Theme.mp4", "Theme.mov", "Theme.webm", "Theme.mkv",
        "Theme.avi",
    )
    return any((theme_dir / name).is_symlink() for name in names)


def trcc_theme_is_supported(path: Path) -> bool:
    """Accept legacy TRCC themes and validated next-native JSON themes.

    OHC's editable cache deliberately contains ``trcc.json`` instead of a
    rewritten ``config1.dc``.  TRCC Linux supports both marker formats; this
    validation mirrors that public backend contract before constructing a
    shell-free ``load-theme`` command.
    """
    if path.is_symlink() or not path.is_dir():
        return False
    assets = ("Theme.png", "00.png", "01.png", "Theme.zt", "Theme.mp4", "Theme.mov", "Theme.webm", "Theme.mkv", "Theme.avi")
    asset_paths = tuple(path / name for name in assets)
    if not any(asset.is_file() for asset in asset_paths):
        return False
    legacy_config = path / "config1.dc"
    if legacy_config.is_symlink():
        return False
    if legacy_config.is_file():
        return True
    config_path = path / "trcc.json"
    try:
        if config_path.is_symlink() or not config_path.is_file() or config_path.stat().st_size > MAX_NATIVE_THEME_CONFIG_BYTES:
            return False
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(config, dict) or not isinstance(config.get("elements"), list):
        return False
    width = config.get("width", LEVITA_WIDTH)
    height = config.get("height", LEVITA_HEIGHT)
    try:
        return int(width) == LEVITA_WIDTH and int(height) == LEVITA_HEIGHT
    except (TypeError, ValueError):
        return False


def media_is_supported(path: Path) -> bool:
    if path.is_symlink():
        return False
    if path.is_dir():
        return trcc_theme_is_supported(path)
    return path.is_file() and path.suffix.casefold() in SUPPORTED_MEDIA_SUFFIXES


def trcc_cloud_theme_id(entry: MediaEntry) -> str | None:
    """Return an exact, in-range TRCC cloud ID encoded by a local filename."""

    name = entry.path.stem if entry.path.is_file() else entry.path.name
    match = re.match(r"(?i)^([abcdey])(\d{3})(?:$|[^0-9])", name)
    if not match:
        return None
    prefix = match.group(1).casefold()
    index = int(match.group(2))
    if not 1 <= index <= TRCC_CLOUD_CATEGORY_LIMITS[prefix]:
        return None
    return f"{prefix}{index:03d}"


def media_category_key(entry: MediaEntry) -> str:
    """Classify local media exactly as TRCC does, using its cloud theme ID."""

    if entry.relative_name.casefold().startswith("ohc-designs /"):
        return "ohc"
    theme_id = trcc_cloud_theme_id(entry)
    return theme_id[0] if theme_id else "own"


def media_catalog_sort_key(entry: MediaEntry) -> tuple[int, int, str]:
    """Sort by TRCC category order and numeric theme index, then own files."""

    if media_category_key(entry) == "ohc":
        return -1, 0, entry.relative_name.casefold()
    theme_id = trcc_cloud_theme_id(entry)
    if theme_id:
        prefixes = [prefix for prefix, _name, _count in TRCC_CLOUD_CATEGORIES]
        return prefixes.index(theme_id[0]), int(theme_id[1:]), entry.relative_name.casefold()
    return len(TRCC_CLOUD_CATEGORIES), 0, entry.relative_name.casefold()


def media_duplicate_name_key(entry: MediaEntry) -> tuple[str, str]:
    """Identify catalog duplicates by complete basename, including suffix.

    Linux permits the same filename in many nested backup folders.  OHC keeps
    those user files untouched but presents one catalog card per name.  Theme
    directories and ordinary files use separate namespaces.
    """

    namespace = "theme" if entry.kind == "theme" else "file"
    return namespace, entry.path.name.casefold()


def media_duplicate_preference(entry: MediaEntry) -> tuple[int, int, int, int, str]:
    """Prefer installed/normal paths over nested backup copies deterministically."""

    relative = entry.relative_name.casefold()
    source_rank = 0 if relative.startswith(("trcc-standard /", "ohc-designs /")) else 1
    parts = tuple(part.casefold() for part in entry.path.parts)
    backup_markers = ("backup", "sicherung", "kopie", "copy", "archive", "archiv")
    backup_rank = sum(
        1 for part in parts
        if part in {"alt", "old"} or any(marker in part for marker in backup_markers)
    )
    return source_rank, backup_rank, len(parts), len(relative), relative


def deduplicate_media_entries(
    entries: Iterable[MediaEntry],
) -> tuple[list[MediaEntry], dict[Path, Path]]:
    """Return one deterministic catalog entry per case-insensitive basename.

    The returned mapping points every hidden duplicate path to the retained
    path so a previously saved selection can migrate without user input.
    """

    groups: dict[tuple[str, str], list[MediaEntry]] = {}
    order: list[tuple[str, str]] = []
    for entry in entries:
        key = media_duplicate_name_key(entry)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(entry)
    retained: list[MediaEntry] = []
    replacements: dict[Path, Path] = {}
    for key in order:
        candidates = groups[key]
        winner = min(candidates, key=media_duplicate_preference)
        retained.append(winner)
        for candidate in candidates:
            if candidate.path != winner.path:
                replacements[candidate.path.resolve()] = winner.path.resolve()
    return retained, replacements


def bounded_notch_width(width: int) -> int:
    return max(LEVITA_CUTOUT_WIDTH, min(MAX_NOTCH_MASK_WIDTH, int(width)))


def notch_safe_right_x(width: int, *, visible: bool = True) -> int:
    return LEVITA_WIDTH - bounded_notch_width(width) if visible else LEVITA_CUTOUT_X


def create_black_notch_mask(
    cache_dir: Path,
    width: int,
    *,
    top_radius: int = DEFAULT_INNER_CORNER_RADIUS,
    bottom_radius: int = DEFAULT_INNER_CORNER_RADIUS,
) -> Path:
    """Create the right bar with separate inner image and outer panel radii."""
    from PIL import Image

    from modules.lcd_levita.v1_4.panel_geometry import (
        bounded_inner_corner_radius,
        fill_outside_levita_panel,
        fill_right_notch_mask,
    )

    bounded_width = bounded_notch_width(width)
    top = bounded_inner_corner_radius(top_radius)
    bottom = bounded_inner_corner_radius(bottom_radius)
    corner_radius = min(DEFAULT_NOTCH_CORNER_RADIUS, bounded_width // 2)
    directory = cache_dir.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (
        f"ohc-levita-notch-{LEVITA_WIDTH}x{LEVITA_HEIGHT}"
        f"-w{bounded_width}-inner-v2-t{top}-b{bottom}-outer-r{corner_radius}.png"
    )
    if target.is_file():
        return target
    image = Image.new("RGBA", (LEVITA_WIDTH, LEVITA_HEIGHT), (0, 0, 0, 0))
    fill_right_notch_mask(
        image,
        (0, 0, 0, 255),
        notch_width=bounded_width,
        top_radius=top,
        bottom_radius=bottom,
    )
    fill_outside_levita_panel(image, (0, 0, 0, 0), radius=corner_radius)
    image.save(target, format="PNG")
    return target


def create_layered_mask(
    cache_dir: Path,
    *,
    hardware_design: Path | None,
    notch_width: int,
    notch_visible: bool,
    notch_top_radius: int = DEFAULT_INNER_CORNER_RADIUS,
    notch_bottom_radius: int = DEFAULT_INNER_CORNER_RADIUS,
    layer_intensity: int = 100,
) -> Path | None:
    """Combine a TRCC design's visual mask with the Levita right bar.

    TRCC has one mask surface.  Applying the Levita cutout mask after a theme
    would otherwise replace the theme's own ``01.png`` (frames, gradients and
    labels).  Alpha-compositing both locally keeps the hardware-data design as
    the upper layer while the image/video remains the background layer.
    """
    from PIL import Image

    theme_mask: Path | None = None
    if hardware_design is not None:
        design = hardware_design.expanduser().resolve()
        candidate = design / "01.png"
        if candidate.is_file():
            theme_mask = candidate
    if not notch_visible and theme_mask is None:
        return None
    if theme_mask is None:
        return create_black_notch_mask(
            cache_dir,
            notch_width,
            top_radius=notch_top_radius,
            bottom_radius=notch_bottom_radius,
        )
    intensity = bounded_layer_intensity(layer_intensity)
    if not notch_visible and intensity == 100:
        return theme_mask

    bounded_width = bounded_notch_width(notch_width)
    try:
        stat = theme_mask.stat()
    except OSError as exc:
        raise ValueError(f"Designmaske ist nicht lesbar: {theme_mask}") from exc
    fingerprint = hashlib.sha256(
        f"{theme_mask}:{stat.st_size}:{stat.st_mtime_ns}:{bounded_width}:"
        f"{int(notch_top_radius)}:{int(notch_bottom_radius)}:{intensity}:v6".encode("utf-8")
    ).hexdigest()[:24]
    directory = cache_dir.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"ohc-levita-layered-mask-{fingerprint}.png"
    if target.is_file():
        return target

    try:
        with Image.open(theme_mask) as opened:
            layer = opened.convert("RGBA")
            if layer.size != (LEVITA_WIDTH, LEVITA_HEIGHT):
                layer = layer.resize((LEVITA_WIDTH, LEVITA_HEIGHT), Image.Resampling.LANCZOS)
            rgb = layer.convert("RGB")
            from PIL import ImageEnhance
            factor = intensity / 100.0
            rgb = ImageEnhance.Brightness(rgb).enhance(factor)
            if intensity > 100:
                rgb = ImageEnhance.Color(rgb).enhance(1.0 + (intensity - 100) / 125.0)
                rgb = ImageEnhance.Contrast(rgb).enhance(1.0 + (intensity - 100) / 250.0)
            rgb.putalpha(layer.getchannel("A").point(lambda alpha: round(alpha * min(1.0, factor))))
            layer = rgb
        if not notch_visible:
            layer.save(target, format="PNG")
            return target
        with Image.open(create_black_notch_mask(
            directory,
            bounded_width,
            top_radius=notch_top_radius,
            bottom_radius=notch_bottom_radius,
        )) as opened:
            notch = opened.convert("RGBA")
        Image.alpha_composite(layer, notch).save(target, format="PNG")
    except OSError as exc:
        raise ValueError(f"Designmaske konnte nicht kombiniert werden: {theme_mask}") from exc
    return target


def create_hardware_design_preview(hardware_design: Path, cache_dir: Path) -> Path | None:
    """Extract the visible top layer from a classic TRCC theme preview.

    ``Theme.png`` is the manufacturer's composed preview and ``00.png`` its
    background.  Their difference gives the mask + example sensor values,
    which can be shown over OHC's independently selected video frame without
    parsing or rewriting the proprietary ``config1.dc`` file.
    """
    from PIL import Image, ImageChops

    design = hardware_design.expanduser().resolve()
    preview = design / "Theme.png"
    background = design / "00.png"
    if not preview.is_file() or not background.is_file():
        return None
    try:
        preview_stat = preview.stat()
        background_stat = background.stat()
    except OSError:
        return None
    fingerprint = hashlib.sha256(
        (
            f"{preview}:{preview_stat.st_size}:{preview_stat.st_mtime_ns}:"
            f"{background}:{background_stat.st_size}:{background_stat.st_mtime_ns}:v1"
        ).encode("utf-8")
    ).hexdigest()[:24]
    directory = cache_dir.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"hardware-layer-{fingerprint}.png"
    if target.is_file():
        return target

    try:
        with Image.open(preview) as preview_image, Image.open(background) as background_image:
            top = preview_image.convert("RGBA")
            base = background_image.convert("RGBA")
            if top.size != base.size:
                return None
            difference = ImageChops.difference(top.convert("RGB"), base.convert("RGB"))
            alpha = difference.convert("L").point(
                lambda value: 0 if value <= 3 else min(255, value * 4),
            )
            top.putalpha(alpha)
            top.save(target, format="PNG")
    except OSError:
        return None
    return target


def prepare_shifted_media(
    media: Path,
    cache_dir: Path,
    *,
    offset_x: int = 0,
    offset_y: int = 0,
    scale_mode: str = MEDIA_SCALE_CONTAIN,
    ffmpeg: str | None = None,
    intensity_percent: int = 100,
) -> PreparedMedia:
    """Render a 1600×720 aspect-correct copy without modifying the source."""
    source = media.expanduser().resolve()
    x = max(-600, min(600, int(offset_x)))
    y = max(-300, min(300, int(offset_y)))
    mode = str(scale_mode).casefold()
    intensity = bounded_layer_intensity(intensity_percent)
    if mode not in MEDIA_SCALE_MODES:
        raise ValueError(f"Unbekannter Skalierungsmodus: {scale_mode}")
    if source.is_dir() or source.suffix.casefold() == ".zt":
        if x == 0 and y == 0 and mode == MEDIA_SCALE_CONTAIN and intensity == 100:
            return PreparedMedia(source)
        return PreparedMedia(
            source,
            warning="Skalierung, Intensität und Hintergrundverschiebung sind bei kompletten TRCC-Layouts und .zt-Dateien noch nicht möglich.",
        )
    if not media_is_supported(source):
        raise ValueError(f"Nicht unterstützte oder fehlende Mediendatei: {source}")

    directory = cache_dir.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    stat = source.stat()
    fingerprint = hashlib.sha256(
        f"{source}:{stat.st_size}:{stat.st_mtime_ns}:{x}:{y}:{mode}:{intensity}:outer-right-v2".encode("utf-8")
    ).hexdigest()[:24]

    if source.suffix.casefold() in SUPPORTED_IMAGE_SUFFIXES:
        from PIL import Image, ImageEnhance

        target = directory / f"shifted-{fingerprint}.png"
        if not target.is_file():
            with Image.open(source) as opened:
                image = opened.convert("RGB")
                factors = (LEVITA_WIDTH / image.width, LEVITA_HEIGHT / image.height)
                scale = min(factors) if mode == MEDIA_SCALE_CONTAIN else max(factors)
                fitted = image.resize(
                    (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
                    Image.Resampling.LANCZOS,
                )
                canvas = Image.new("RGB", (LEVITA_WIDTH, LEVITA_HEIGHT), (0, 0, 0))
                left = (LEVITA_WIDTH - fitted.width) // 2 + x
                top = (LEVITA_HEIGHT - fitted.height) // 2 + y
                canvas.paste(fitted, (left, top))
                factor = intensity / 100.0
                canvas = ImageEnhance.Brightness(canvas).enhance(factor)
                if intensity > 100:
                    canvas = ImageEnhance.Color(canvas).enhance(1.0 + (intensity - 100) / 125.0)
                    canvas = ImageEnhance.Contrast(canvas).enhance(1.0 + (intensity - 100) / 250.0)
                from modules.lcd_levita.v1_4.panel_geometry import fill_outside_levita_panel

                fill_outside_levita_panel(canvas, (0, 0, 0), radius=DEFAULT_NOTCH_CORNER_RADIUS)
                canvas.save(target, format="PNG")
        return PreparedMedia(target, transformed=True)

    executable = ffmpeg or shutil.which("ffmpeg")
    if not executable:
        return PreparedMedia(source, warning="Für die unverzerrte Video-Skalierung wird ffmpeg benötigt.")
    target = directory / f"shifted-{fingerprint}.mp4"
    if not target.is_file():
        aspect = "decrease" if mode == MEDIA_SCALE_CONTAIN else "increase"
        video_effect = ""
        if intensity != 100:
            brightness = (intensity - 100) / 250.0
            saturation = 1.0 + max(0, intensity - 100) / 125.0
            video_effect = f"eq=brightness={brightness:.3f}:saturation={saturation:.3f},"
        filter_graph = (
            f"scale={LEVITA_WIDTH}:{LEVITA_HEIGHT}:force_original_aspect_ratio={aspect},"
            f"pad=iw+1200:ih+600:600+{x}:300+{y}:black,"
            f"crop={LEVITA_WIDTH}:{LEVITA_HEIGHT}:(iw-{LEVITA_WIDTH})/2:(ih-{LEVITA_HEIGHT})/2,"
            f"{video_effect}setsar=1,format=yuv420p"
        )
        try:
            completed = subprocess.run(
                [
                    executable, "-v", "error", "-y", "-i", str(source),
                    "-vf", filter_graph, "-an", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "18", "-movflags", "+faststart", str(target),
                ],
                capture_output=True, text=True, timeout=300, check=False,
            )
        except subprocess.TimeoutExpired:
            return PreparedMedia(source, warning="Die lokale Video-Verschiebung hat länger als fünf Minuten gedauert.")
        if completed.returncode != 0 or not target.is_file():
            target.unlink(missing_ok=True)
            detail = (completed.stderr or "ffmpeg-Fehler").strip().splitlines()[-1]
            return PreparedMedia(source, warning=f"Video konnte nicht verschoben werden: {detail}")
    return PreparedMedia(target, transformed=True)


def parse_detect_output(output: str) -> bool:
    return bool(re.search(r"(?i)(?<![0-9a-f])87ad\s*:\s*70db(?![0-9a-f])", output or ""))


def overlay_intersects_cutout(
    spec: OverlaySpec,
    *,
    estimated_width: int | None = None,
    safe_right_x: int = LEVITA_CUTOUT_X,
) -> bool:
    """Conservatively test a centered text element against the right cutout."""
    item = spec.bounded(safe_right_x=safe_right_x)
    width = estimated_width if estimated_width is not None else max(item.size * 2, len(item.sample) * item.size // 2)
    return item.x + max(1, int(width)) // 2 >= safe_right_x


def clamp_overlay_outside_cutout(
    spec: OverlaySpec,
    *,
    estimated_width: int | None = None,
    safe_right_x: int = LEVITA_CUTOUT_X,
) -> OverlaySpec:
    right = max(1, min(LEVITA_WIDTH, int(safe_right_x)))
    item = spec.bounded(safe_right_x=right)
    width = estimated_width if estimated_width is not None else max(item.size * 2, len(item.sample) * item.size // 2)
    half = max(1, int(width)) // 2
    return replace(item, x=min(item.x, max(0, right - half - 8)))


class ThermalrightCli:
    """Bounded command adapter for the external ``trcc-linux`` backend."""

    def __init__(
        self,
        executable: str | None = None,
        *,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        self.executable = executable or find_trcc_executable()
        self._runner = runner

    @property
    def available(self) -> bool:
        return bool(self.executable)

    def _command(self, *parts: object) -> tuple[str, ...]:
        if not self.executable:
            raise RuntimeError("TRCC-Linux-Backend ist nicht installiert.")
        return (self.executable, *(str(part) for part in parts))

    def run(self, *parts: object, timeout: float = 20.0) -> CommandResult:
        args = self._command(*parts)
        completed = self._runner(
            list(args), capture_output=True, text=True, timeout=timeout, check=False,
        )
        return CommandResult(
            ok=completed.returncode == 0,
            args=args,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            returncode=int(completed.returncode),
        )

    def version_args(self) -> tuple[str, ...]:
        return self._command("--version")

    def detect_args(self) -> tuple[str, ...]:
        return self._command("detect")

    def disconnect_args(self) -> tuple[str, ...]:
        return self._command("device", "disconnect", THERMALRIGHT_DEVICE_KEY)

    def connect_args(self) -> tuple[str, ...]:
        return self._command("device", "connect", THERMALRIGHT_DEVICE_KEY)

    def reconnect_sequence(self) -> list[tuple[tuple[str, ...], bool]]:
        """Replace a daemon device whose cached handshake outlived USB.

        TRCC's current ``Device.is_connected`` reflects its cached handshake,
        not whether the underlying transport is still open. After unplugging,
        EnsureConnected can therefore incorrectly no-op. A tolerated detach
        followed by a mandatory connect also replaces the stale send worker.
        """

        return [
            (self.disconnect_args(), True),
            (self.connect_args(), False),
        ]

    def test_args(self, seconds: float = 0.5) -> tuple[str, ...]:
        hold = max(0.1, min(5.0, float(seconds)))
        return self._command("display", "test", "--seconds", f"{hold:g}", THERMALRIGHT_DEVICE_KEY)

    def split_mode_args(self, mode: int) -> tuple[str, ...]:
        value = max(0, min(3, int(mode)))
        return self._command("display", "split-mode", THERMALRIGHT_DEVICE_KEY, value)

    def brightness_args(self, percent: int) -> tuple[str, ...]:
        return self._command(
            "display", "set-brightness", THERMALRIGHT_DEVICE_KEY,
            max(0, min(100, int(percent))),
        )

    def orientation_args(self, degrees: int) -> tuple[str, ...]:
        value = int(degrees)
        if value not in (0, 90, 180, 270):
            raise ValueError("Ausrichtung muss 0, 90, 180 oder 270 Grad betragen")
        return self._command("display", "set-orientation", THERMALRIGHT_DEVICE_KEY, value)

    def load_media_args(self, path: Path) -> tuple[str, ...]:
        source = path.expanduser().resolve()
        if not media_is_supported(source):
            raise ValueError(f"Nicht unterstützte oder fehlende Mediendatei: {source}")
        if source.is_dir():
            verb = "load-theme"
        else:
            verb = "load-image" if source.suffix.casefold() in SUPPORTED_IMAGE_SUFFIXES else "load-video"
        return self._command("display", verb, THERMALRIGHT_DEVICE_KEY, source)

    def play_video_args(self, path: Path) -> tuple[str, ...]:
        """Override only the active theme background, preserving its layout."""
        source = path.expanduser().resolve()
        if (
            source.is_symlink()
            or not source.is_file()
            or source.suffix.casefold() not in SUPPORTED_VIDEO_SUFFIXES
        ):
            raise ValueError(f"Kein unterstütztes Hintergrundvideo: {source}")
        return self._command("display", "play-video", THERMALRIGHT_DEVICE_KEY, source)

    def overlay_delete_args(self, ident: str) -> tuple[str, ...]:
        if not re.fullmatch(r"ohc-[a-z0-9-]{1,48}", ident):
            raise ValueError("Ungültige OHC-Ebenenkennung")
        return self._command("display", "overlay-delete", THERMALRIGHT_DEVICE_KEY, ident)

    def overlay_update_format_args(
        self, ident: str, format_text: str, *, show_unit: bool = True,
    ) -> tuple[str, ...]:
        """Update one live block through the already running TRCC daemon."""
        if not re.fullmatch(r"ohc-[a-z0-9-]{1,48}", ident):
            raise ValueError("Ungültige OHC-Ebenenkennung")
        safe_format = str(format_text).replace("\n", " ").replace("\r", " ").strip()[:160]
        if not safe_format:
            raise ValueError("Leeres OHC-Anzeigeformat")
        return self._command(
            "display", "overlay-update", THERMALRIGHT_DEVICE_KEY, ident,
            "--format", safe_format,
            "--show-unit" if show_unit else "--hide-unit",
        )

    def apply_mask_args(self, path: Path) -> tuple[str, ...]:
        source = path.expanduser().resolve()
        if not source.is_file() or source.suffix.casefold() not in SUPPORTED_IMAGE_SUFFIXES:
            raise ValueError(f"Nicht unterstützte oder fehlende Maskendatei: {source}")
        return self._command("display", "apply-mask", THERMALRIGHT_DEVICE_KEY, source)

    def mask_position_args(self, x: int = 0, y: int = 0) -> tuple[str, ...]:
        return self._command(
            "display", "mask-position", THERMALRIGHT_DEVICE_KEY,
            max(0, min(LEVITA_WIDTH, int(x))), max(0, min(LEVITA_HEIGHT, int(y))),
        )

    def mask_visible_args(self, visible: bool) -> tuple[str, ...]:
        return self._command("display", "mask-visible", THERMALRIGHT_DEVICE_KEY, "on" if visible else "off")

    def overlay_add_args(self, spec: OverlaySpec, *, safe_right_x: int = LEVITA_CUTOUT_X) -> tuple[str, ...]:
        item = clamp_overlay_outside_cutout(spec, safe_right_x=safe_right_x)
        args: list[object] = [
            "display", "overlay-add", THERMALRIGHT_DEVICE_KEY, item.kind,
            "--x", item.x, "--y", item.y, "--color", item.color,
            "--size", item.size, "--id", item.ident,
        ]
        if item.kind == "metric":
            args.extend(("--metric", item.metric, "--format", item.format or "{value}"))
            args.append("--show-unit" if item.show_unit else "--hide-unit")
        elif item.kind == "clock":
            args.extend(("--source", item.source or "time"))
        else:
            raise ValueError(f"Nicht unterstützter Ebenentyp: {item.kind}")
        if item.bold:
            args.append("--bold")
        return self._command(*args)

    def overlay_enabled_args(self, enabled: bool) -> tuple[str, ...]:
        return self._command("display", "overlay", THERMALRIGHT_DEVICE_KEY, "on" if enabled else "off")

    def play_args(self, interval: float = 0.15) -> tuple[str, ...]:
        refresh = max(0.10, min(5.0, float(interval)))
        return self._command("display", "play", "--interval", f"{refresh:g}", THERMALRIGHT_DEVICE_KEY)

    def stop_video_args(self) -> tuple[str, ...]:
        return self._command("display", "stop-video", THERMALRIGHT_DEVICE_KEY)

    def stop_video_now(self, *, timeout: float = 1.5) -> CommandResult:
        """Synchronously clear playback through the single-owner TRCC daemon.

        This bounded path is reserved for controlled application shutdown,
        where Qt's asynchronous process queue may no longer receive events.
        """

        args = self.stop_video_args()
        environment = os.environ.copy()
        environment["TRCC_DAEMON"] = "1"
        environment["QT_QPA_PLATFORM"] = "offscreen"
        completed = self._runner(
            list(args),
            capture_output=True,
            text=True,
            timeout=max(0.25, min(3.0, float(timeout))),
            check=False,
            env=environment,
        )
        return CommandResult(
            ok=completed.returncode == 0,
            args=args,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            returncode=int(completed.returncode),
        )


def build_apply_sequence(
    cli: ThermalrightCli,
    media: Path,
    overlays: Iterable[OverlaySpec],
    *,
    split_mode: int,
    mask_path: Path | None = None,
    safe_right_x: int = LEVITA_CUTOUT_X,
    hardware_design: Path | None = None,
    replace_hardware_background: bool | None = None,
    brightness: int | None = None,
    orientation: int | None = None,
) -> list[tuple[tuple[str, ...], bool]]:
    """Build the deterministic apply sequence; bool marks tolerated failures.

    TRCC Linux 9.9.11 and its current Qt renderer crash when a persisted
    decorative split mode is active with newer PySide6 releases. Always
    neutralise that external state *before* loading media. The real 80 px
    Levita cutout is physical and remains protected by our overlay bounds.
    ``split_mode`` is retained for preview/settings compatibility, but is not
    sent to the affected backend.
    """
    right = max(1, min(LEVITA_WIDTH, int(safe_right_x)))
    items = [item.bounded(safe_right_x=right) for item in overlays]
    # Keep settings input bounded even while hardware split modes are disabled.
    _requested_split_mode = max(0, min(3, int(split_mode)))
    commands = cli.reconnect_sequence()
    commands.append((cli.split_mode_args(0), False))
    if brightness is not None:
        commands.append((cli.brightness_args(brightness), False))
    if orientation is not None:
        commands.append((cli.orientation_args(orientation), False))
    if hardware_design is not None:
        design = hardware_design.expanduser().resolve()
        if not media_is_supported(design) or not design.is_dir():
            raise ValueError(f"Kein vollständiges TRCC-Hardwaredesign: {design}")
        # Layer 2 first: LoadTheme adopts legacy config1.dc or OHC's validated
        # next-native trcc.json as the working sensor layout. Layer 1 second:
        # PlayVideo replaces only its background and preserves that layout.
        commands.append((cli.load_media_args(design), False))
        # Selecting a complete installed TRCC layout as both layers means
        # "use this design as-is": its own background and live values are
        # adopted directly.  A different selected video activates the
        # true two-layer path and replaces only that background afterwards.
        should_replace_background = (
            media.expanduser().resolve() != design
            if replace_hardware_background is None
            else bool(replace_hardware_background)
        )
        if should_replace_background:
            commands.append((cli.play_video_args(media), False))
    else:
        commands.append((cli.load_media_args(media), False))
    if mask_path is not None:
        commands.extend((
            (cli.apply_mask_args(mask_path), False),
            (cli.mask_position_args(0, 0), False),
            (cli.mask_visible_args(True), False),
        ))
    else:
        commands.append((cli.mask_visible_args(False), False))
    if hardware_design is None:
        for item in items:
            commands.append((cli.overlay_delete_args(item.ident), True))
        for item in items:
            if item.visible:
                commands.append((cli.overlay_add_args(item, safe_right_x=right), False))
        overlay_enabled = any(item.visible for item in items)
    else:
        # The selected TRCC layout owns the complete upper layer. LoadTheme has
        # already replaced any previous OHC working layout, so appending the
        # six custom elements here would duplicate values on the display.
        overlay_enabled = True
    commands.append((cli.overlay_enabled_args(overlay_enabled), False))
    return commands


def command_display(args: Sequence[str]) -> str:
    """Human-readable command without shell quoting or execution."""
    return " ".join(str(part) for part in args)
