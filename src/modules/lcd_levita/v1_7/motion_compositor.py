#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Cache composition of an OHC Layer-2 motion loop with selected Layer 1."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import shutil
import subprocess


_IMAGES = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
_VIDEOS = {".mp4", ".mov", ".webm", ".mkv", ".avi"}


@dataclass(frozen=True)
class MotionComposition:
    path: Path
    warning: str = ""


def _theme_background(source: Path) -> Path | None:
    if not source.is_dir():
        return source
    for name in ("00.png", "Theme.mp4", "Theme.mov", "Theme.webm", "Theme.mkv", "Theme.avi"):
        candidate = source / name
        if candidate.is_file():
            return candidate
    return None


def compose_motion_video(
    background: Path,
    motion: Path,
    cache_root: Path,
    *,
    fps: int = 15,
    duration: int = 10,
    ffmpeg: str | None = None,
) -> MotionComposition:
    """Screen-blend a bundled black-based motion loop below live text blocks."""
    base = _theme_background(background.expanduser().resolve())
    effect = motion.expanduser().resolve()
    if base is None or not base.is_file() or base.suffix.casefold() not in _IMAGES | _VIDEOS:
        return MotionComposition(background, "Dekor-Animation ist für diesen Hintergrundtyp nicht verfügbar.")
    if not effect.is_file() or effect.suffix.casefold() != ".mp4":
        return MotionComposition(background, "Die lokale OHC-Dekoranimation fehlt.")
    executable = ffmpeg or shutil.which("ffmpeg")
    if not executable:
        return MotionComposition(background, "Dekor-Animation benötigt ffmpeg zur lokalen Ebenenkomposition.")
    rate = max(5, min(60, int(fps)))
    seconds = max(4, min(30, int(duration)))
    signature = ":".join(
        f"{path}:{path.stat().st_size}:{path.stat().st_mtime_ns}" for path in (base, effect)
    )
    fingerprint = hashlib.sha256(
        f"{signature}:{rate}:{seconds}:screen-v1".encode("utf-8")
    ).hexdigest()[:24]
    target_dir = cache_root.expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"layer2-motion-{fingerprint}.mp4"
    if target.is_file() and target.stat().st_size > 4096:
        return MotionComposition(target)
    base_args = ["-loop", "1"] if base.suffix.casefold() in _IMAGES else ["-stream_loop", "-1"]
    command = [
        executable, "-v", "error", "-y", *base_args, "-i", str(base),
        "-stream_loop", "-1", "-i", str(effect),
        "-filter_complex",
        f"[0:v]scale=1600:720,setsar=1,fps={rate}[base];"
        f"[1:v]scale=1600:720,setsar=1,fps={rate}[motion];"
        "[base][motion]blend=all_mode=screen:all_opacity=0.92,format=yuv420p[out]",
        "-map", "[out]", "-t", str(seconds), "-an", "-c:v", "libx264",
        "-preset", "veryfast", "-crf", "18", "-movflags", "+faststart", str(target),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=300, check=False)
    except subprocess.TimeoutExpired:
        return MotionComposition(background, "Lokale Dekor-Komposition hat länger als fünf Minuten gedauert.")
    if completed.returncode != 0 or not target.is_file() or target.stat().st_size <= 4096:
        target.unlink(missing_ok=True)
        detail = (completed.stderr or "ffmpeg-Fehler").strip().splitlines()[-1]
        return MotionComposition(background, f"Dekor-Animation konnte nicht zusammengesetzt werden: {detail}")
    return MotionComposition(target)
