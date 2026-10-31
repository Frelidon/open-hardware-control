#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded offline exporter for procedural Levita display effects."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from PySide6.QtGui import QGuiApplication

SOURCE_ROOT = Path(__file__).resolve().parents[3]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from modules.display_effects.v1_11.model import SmokeSettings
from modules.display_effects.v1_11.smoke_renderer import render_smoke_frame


FRAME_COUNT = 96
FRAME_RATE = 24
WIDTH = 1600
HEIGHT = 720


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return True


def export_smoke(settings_path: Path, output_path: Path, cache_root: Path) -> None:
    root = cache_root.resolve()
    source = settings_path.resolve()
    target = output_path.resolve()
    if not _inside(source, root) or not _inside(target, root):
        raise ValueError("effect input and output must stay inside the private OHC cache")
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 64_000:
        raise ValueError("invalid effect settings file")
    if target.suffix.casefold() != ".mp4":
        raise ValueError("effect output must be an MP4 file")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to export a display effect")
    values = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(values, dict):
        raise ValueError("effect settings must be a JSON object")
    settings = SmokeSettings.from_mapping(values)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{os.getpid()}.part.mp4")
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", f"{WIDTH}x{HEIGHT}",
        "-framerate", str(FRAME_RATE), "-i", "-", "-an", "-c:v", "libx264",
        "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(temporary),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        assert process.stdin is not None
        for frame in range(FRAME_COUNT):
            image = render_smoke_frame(settings, frame / FRAME_COUNT, width=WIDTH, height=HEIGHT)
            process.stdin.write(bytes(image.constBits()))
        process.stdin.close()
        error = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
        result = process.wait(timeout=180)
        if result != 0:
            raise RuntimeError(error.strip().splitlines()[-1] if error.strip() else "ffmpeg export failed")
        if not temporary.is_file() or temporary.stat().st_size < 4096:
            raise RuntimeError("ffmpeg did not create a usable effect video")
        temporary.replace(target)
    finally:
        if process.poll() is None:
            process.kill()
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache-root", required=True, type=Path)
    args = parser.parse_args()
    QGuiApplication.instance() or QGuiApplication([sys.argv[0], "-platform", "offscreen"])
    try:
        export_smoke(args.settings, args.output, args.cache_root)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(str(args.output.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
