#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproducibly render the original OHC directional light-band loops."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.display_effects.v1_11.light_bands_renderer import (  # noqa: E402
    DIRECTION_ANGLES,
    render_light_bands_frame,
)


def render(output: Path, direction: str, frames: int = 96, fps: int = 24) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.part.mp4")
    command = [
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", "1600x720",
        "-framerate", str(fps), "-i", "-", "-an", "-c:v", "libx264",
        "-preset", "slow", "-tune", "animation", "-crf", "10", "-pix_fmt", "yuv420p",
        "-threads", "2", "-movflags", "+faststart", str(temporary),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        assert process.stdin is not None
        for frame in range(frames):
            source = render_light_bands_frame(direction, frame / frames, width=4800, height=2160)
            image = source.scaled(
                1600, 720, Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            process.stdin.write(bytes(image.constBits()))
            if frame == frames // 6:
                image.save(str(output.with_suffix(".jpg")), "JPG", 98)
        process.stdin.close()
        error = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
        if process.wait(timeout=180) != 0:
            raise RuntimeError(error.strip() or "ffmpeg failed")
        temporary.replace(output)
    finally:
        if process.poll() is None:
            process.kill()
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "src/assets/display-effects",
    )
    args = parser.parse_args()
    QGuiApplication.instance() or QGuiApplication([sys.argv[0], "-platform", "offscreen"])
    for direction in DIRECTION_ANGLES:
        target = args.output_dir / f"ohc-light-bands-{direction}.mp4"
        render(target, direction)
        print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
