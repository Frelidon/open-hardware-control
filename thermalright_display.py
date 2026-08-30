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
from pathlib import Path
import re
import shutil
import subprocess
from typing import Callable, Iterable, Sequence


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
    prefix: name for prefix, name, _count in TRCC_CLOUD_CATEGORIES
} | {
    "own": "Eigene Dateien",
}

SUPPORTED_IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".bmp", ".webp"})
SUPPORTED_VIDEO_SUFFIXES = frozenset({".mp4", ".mov", ".webm", ".mkv", ".avi", ".zt"})
SUPPORTED_MEDIA_SUFFIXES = SUPPORTED_IMAGE_SUFFIXES | SUPPORTED_VIDEO_SUFFIXES
MAX_MEDIA_FILES = 2500


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


def find_trcc_executable() -> str | None:
    """Find a system or pipx/user installation without mutating PATH."""
    resolved = shutil.which("trcc")
    if resolved:
        return resolved
    candidate = Path.home() / ".local" / "bin" / "trcc"
    return str(candidate) if candidate.is_file() and candidate.stat().st_mode & 0o111 else None


def scan_media_directory(root: Path, *, limit: int = MAX_MEDIA_FILES) -> list[MediaEntry]:
    """Return supported local media without copying or following symlinks."""
    directory = root.expanduser().resolve()
    if not directory.is_dir():
        raise ValueError(f"Kein lesbarer Designordner: {directory}")
    bounded_limit = max(1, min(MAX_MEDIA_FILES, int(limit)))
    entries: list[MediaEntry] = []
    theme_dirs: set[Path] = set()
    for config in sorted(directory.rglob("config1.dc"), key=lambda item: item.as_posix().casefold()):
        theme_dir = config.parent
        if theme_dir.is_symlink():
            continue
        if any((theme_dir / name).is_file() for name in ("Theme.png", "00.png")):
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


def media_is_supported(path: Path) -> bool:
    if path.is_symlink():
        return False
    if path.is_dir():
        return (path / "config1.dc").is_file() and any((path / name).is_file() for name in ("Theme.png", "00.png"))
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

    theme_id = trcc_cloud_theme_id(entry)
    return theme_id[0] if theme_id else "own"


def media_catalog_sort_key(entry: MediaEntry) -> tuple[int, int, str]:
    """Sort by TRCC category order and numeric theme index, then own files."""

    theme_id = trcc_cloud_theme_id(entry)
    if theme_id:
        prefixes = [prefix for prefix, _name, _count in TRCC_CLOUD_CATEGORIES]
        return prefixes.index(theme_id[0]), int(theme_id[1:]), entry.relative_name.casefold()
    return len(TRCC_CLOUD_CATEGORIES), 0, entry.relative_name.casefold()


def bounded_notch_width(width: int) -> int:
    return max(LEVITA_CUTOUT_WIDTH, min(MAX_NOTCH_MASK_WIDTH, int(width)))


def notch_safe_right_x(width: int, *, visible: bool = True) -> int:
    return LEVITA_WIDTH - bounded_notch_width(width) if visible else LEVITA_CUTOUT_X


def create_black_notch_mask(cache_dir: Path, width: int) -> Path:
    """Create a full-canvas transparent PNG with an opaque right-hand bar."""
    from PIL import Image, ImageDraw

    bounded_width = bounded_notch_width(width)
    directory = cache_dir.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"ohc-levita-notch-{LEVITA_WIDTH}x{LEVITA_HEIGHT}-w{bounded_width}.png"
    if target.is_file():
        return target
    image = Image.new("RGBA", (LEVITA_WIDTH, LEVITA_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle(
        (LEVITA_WIDTH - bounded_width, 0, LEVITA_WIDTH - 1, LEVITA_HEIGHT - 1),
        fill=(0, 0, 0, 255),
    )
    image.save(target, format="PNG")
    return target


def prepare_shifted_media(
    media: Path,
    cache_dir: Path,
    *,
    offset_x: int = 0,
    offset_y: int = 0,
    scale_mode: str = MEDIA_SCALE_CONTAIN,
    ffmpeg: str | None = None,
) -> PreparedMedia:
    """Render a 1600×720 aspect-correct copy without modifying the source."""
    source = media.expanduser().resolve()
    x = max(-600, min(600, int(offset_x)))
    y = max(-300, min(300, int(offset_y)))
    mode = str(scale_mode).casefold()
    if mode not in MEDIA_SCALE_MODES:
        raise ValueError(f"Unbekannter Skalierungsmodus: {scale_mode}")
    if source.is_dir() or source.suffix.casefold() == ".zt":
        if x == 0 and y == 0 and mode == MEDIA_SCALE_CONTAIN:
            return PreparedMedia(source)
        return PreparedMedia(
            source,
            warning="Skalierung und Hintergrundverschiebung sind bei kompletten TRCC-Layouts und .zt-Dateien noch nicht möglich.",
        )
    if not media_is_supported(source):
        raise ValueError(f"Nicht unterstützte oder fehlende Mediendatei: {source}")

    directory = cache_dir.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    stat = source.stat()
    fingerprint = hashlib.sha256(
        f"{source}:{stat.st_size}:{stat.st_mtime_ns}:{x}:{y}:{mode}:v2".encode("utf-8")
    ).hexdigest()[:24]

    if source.suffix.casefold() in SUPPORTED_IMAGE_SUFFIXES:
        from PIL import Image

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
                canvas.save(target, format="PNG")
        return PreparedMedia(target, transformed=True)

    executable = ffmpeg or shutil.which("ffmpeg")
    if not executable:
        return PreparedMedia(source, warning="Für die unverzerrte Video-Skalierung wird ffmpeg benötigt.")
    target = directory / f"shifted-{fingerprint}.mp4"
    if not target.is_file():
        aspect = "decrease" if mode == MEDIA_SCALE_CONTAIN else "increase"
        filter_graph = (
            f"scale={LEVITA_WIDTH}:{LEVITA_HEIGHT}:force_original_aspect_ratio={aspect},"
            f"pad=iw+1200:ih+600:600+{x}:300+{y}:black,"
            f"crop={LEVITA_WIDTH}:{LEVITA_HEIGHT}:(iw-{LEVITA_WIDTH})/2:(ih-{LEVITA_HEIGHT})/2,"
            "setsar=1,format=yuv420p"
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

    def test_args(self, seconds: float = 0.5) -> tuple[str, ...]:
        hold = max(0.1, min(5.0, float(seconds)))
        return self._command("display", "test", "--seconds", f"{hold:g}", THERMALRIGHT_DEVICE_KEY)

    def split_mode_args(self, mode: int) -> tuple[str, ...]:
        value = max(0, min(3, int(mode)))
        return self._command("display", "split-mode", THERMALRIGHT_DEVICE_KEY, value)

    def load_media_args(self, path: Path) -> tuple[str, ...]:
        source = path.expanduser().resolve()
        if not media_is_supported(source):
            raise ValueError(f"Nicht unterstützte oder fehlende Mediendatei: {source}")
        if source.is_dir():
            verb = "load-theme"
        else:
            verb = "load-image" if source.suffix.casefold() in SUPPORTED_IMAGE_SUFFIXES else "load-video"
        return self._command("display", verb, THERMALRIGHT_DEVICE_KEY, source)

    def overlay_delete_args(self, ident: str) -> tuple[str, ...]:
        if not re.fullmatch(r"ohc-[a-z0-9-]{1,48}", ident):
            raise ValueError("Ungültige OHC-Ebenenkennung")
        return self._command("display", "overlay-delete", THERMALRIGHT_DEVICE_KEY, ident)

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


def build_apply_sequence(
    cli: ThermalrightCli,
    media: Path,
    overlays: Iterable[OverlaySpec],
    *,
    split_mode: int,
    mask_path: Path | None = None,
    safe_right_x: int = LEVITA_CUTOUT_X,
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
    commands: list[tuple[tuple[str, ...], bool]] = [
        (cli.split_mode_args(0), False),
        (cli.load_media_args(media), False),
    ]
    if mask_path is not None:
        commands.extend((
            (cli.apply_mask_args(mask_path), False),
            (cli.mask_position_args(0, 0), False),
            (cli.mask_visible_args(True), False),
        ))
    else:
        commands.append((cli.mask_visible_args(False), False))
    for item in items:
        commands.append((cli.overlay_delete_args(item.ident), True))
    for item in items:
        if item.visible:
            commands.append((cli.overlay_add_args(item, safe_right_x=right), False))
    commands.append((cli.overlay_enabled_args(any(item.visible for item in items)), False))
    return commands


def command_display(args: Sequence[str]) -> str:
    """Human-readable command without shell quoting or execution."""
    return " ".join(str(part) for part in args)
