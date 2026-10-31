#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproducibly render the four original OHC Layer-2 motion loops."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PySide6.QtGui import QGuiApplication


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.lcd_levita.v1_7.motion_renderer import (  # noqa: E402
    SUPPORTED_MOTION_THEMES,
    render_layer2_motion_frame,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "src/assets/levita-designs")
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--seconds", type=int, default=6)
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required")
    QGuiApplication.instance() or QGuiApplication([])
    frames = max(1, args.fps * args.seconds)
    with tempfile.TemporaryDirectory(prefix="ohc-levita-motion-") as temporary:
        root = Path(temporary)
        for theme in sorted(SUPPORTED_MOTION_THEMES):
            frame_dir = root / theme
            frame_dir.mkdir()
            for index in range(frames):
                image = render_layer2_motion_frame(theme, index / frames)
                if not image.save(str(frame_dir / f"{index:04d}.png")):
                    raise SystemExit(f"could not write frame for {theme}")
            output = args.output / theme / "motion.mp4"
            output.parent.mkdir(parents=True, exist_ok=True)
            completed = subprocess.run([
                ffmpeg, "-v", "error", "-y", "-framerate", str(args.fps),
                "-i", str(frame_dir / "%04d.png"), "-an", "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", str(output),
            ], check=False)
            if completed.returncode != 0:
                raise SystemExit(f"ffmpeg failed for {theme}")
            print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
