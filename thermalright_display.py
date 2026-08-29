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

    def bounded(self) -> "OverlaySpec":
        return replace(
            self,
            x=max(0, min(LEVITA_CUTOUT_X - 1, int(self.x))),
            y=max(0, min(LEVITA_HEIGHT - 1, int(self.y))),
            size=max(12, min(160, int(self.size))),
            color=normalize_color(self.color),
        )


DEFAULT_OVERLAYS: tuple[OverlaySpec, ...] = (
    OverlaySpec("ohc-cpu-temp", "CPU-Temperatur", "metric", "cpu:temp", format="CPU {value:.0f}°C", sample="CPU 51 °C", x=240, y=590, size=52, color="#32c5ff"),
    OverlaySpec("ohc-cpu-load", "CPU-Auslastung", "metric", "cpu:usage", format="CPU {value:.0f}%", sample="CPU 18 %", x=520, y=590, size=44, color="#32c5ff"),
    OverlaySpec("ohc-gpu-temp", "GPU-Temperatur", "metric", "gpu:primary:temp", format="GPU {value:.0f}°C", sample="GPU 47 °C", x=820, y=590, size=52, color="#44d7b6"),
    OverlaySpec("ohc-gpu-load", "GPU-Auslastung", "metric", "gpu:primary:usage", format="GPU {value:.0f}%", sample="GPU 32 %", x=1110, y=590, size=44, color="#44d7b6"),
    OverlaySpec("ohc-memory", "Arbeitsspeicher", "metric", "memory:percent", format="RAM {value:.0f}%", sample="RAM 41 %", x=1370, y=590, size=40, color="#6dd401"),
    OverlaySpec("ohc-clock", "Uhrzeit", "clock", source="time", format="{value}", sample="13:38", x=1360, y=90, size=56, color="#ffffff"),
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


def parse_detect_output(output: str) -> bool:
    return bool(re.search(r"(?i)(?<![0-9a-f])87ad\s*:\s*70db(?![0-9a-f])", output or ""))


def overlay_intersects_cutout(spec: OverlaySpec, *, estimated_width: int | None = None) -> bool:
    """Conservatively test a centered text element against the right cutout."""
    item = spec.bounded()
    width = estimated_width if estimated_width is not None else max(item.size * 2, len(item.sample) * item.size // 2)
    return item.x + max(1, int(width)) // 2 >= LEVITA_CUTOUT_X


def clamp_overlay_outside_cutout(spec: OverlaySpec, *, estimated_width: int | None = None) -> OverlaySpec:
    item = spec.bounded()
    width = estimated_width if estimated_width is not None else max(item.size * 2, len(item.sample) * item.size // 2)
    half = max(1, int(width)) // 2
    return replace(item, x=min(item.x, max(0, LEVITA_CUTOUT_X - half - 8)))


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

    def overlay_add_args(self, spec: OverlaySpec) -> tuple[str, ...]:
        item = clamp_overlay_outside_cutout(spec)
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
) -> list[tuple[tuple[str, ...], bool]]:
    """Build the deterministic apply sequence; bool marks tolerated failures.

    TRCC Linux 9.9.11 and its current Qt renderer crash when a persisted
    decorative split mode is active with newer PySide6 releases. Always
    neutralise that external state *before* loading media. The real 80 px
    Levita cutout is physical and remains protected by our overlay bounds.
    ``split_mode`` is retained for preview/settings compatibility, but is not
    sent to the affected backend.
    """
    items = [item.bounded() for item in overlays]
    # Keep settings input bounded even while hardware split modes are disabled.
    _requested_split_mode = max(0, min(3, int(split_mode)))
    commands: list[tuple[tuple[str, ...], bool]] = [
        (cli.split_mode_args(0), False),
        (cli.load_media_args(media), False),
    ]
    for item in items:
        commands.append((cli.overlay_delete_args(item.ident), True))
    for item in items:
        if item.visible:
            commands.append((cli.overlay_add_args(item), False))
    commands.append((cli.overlay_enabled_args(any(item.visible for item in items)), False))
    return commands


def command_display(args: Sequence[str]) -> str:
    """Human-readable command without shell quoting or execution."""
    return " ".join(str(part) for part in args)
