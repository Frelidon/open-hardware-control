#!/usr/bin/env python3
"""Original OHC code-rain study. No SignalRGB artwork or source is used.

Rebuilds the original seamless 1600x720 LCD background.
No sensor values, hardware access or third-party effect code.
"""
from pathlib import Path
import json
import math
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "src/assets/display-effects"
WIDTH, HEIGHT, CELL, SECONDS, FPS = 1600, 720, 24, 12, 30
COLS, ROWS = math.ceil(WIDTH / CELL), HEIGHT // CELL
FONT_ROOT = Path('/usr/share/fonts/truetype/dejavu')
GLYPHS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ:+-=<>[]{}/*'
rng = np.random.default_rng(20261111)


def font(size, bold=False):
    name = 'DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf'
    return ImageFont.truetype(str(FONT_ROOT / name), size)


def glyph_atlas():
    result = []
    for char in GLYPHS:
        tile = Image.new('L', (CELL, CELL))
        ImageDraw.Draw(tile).text((CELL / 2, CELL / 2), char, font=font(19),
                                  fill=255, anchor='mm')
        result.append(np.asarray(tile, dtype=np.float32) / 255)
    return np.stack(result)


ATLAS = glyph_atlas()
INDEX_A = rng.integers(0, len(GLYPHS), (ROWS, COLS))
INDEX_B = rng.integers(0, len(GLYPHS), (ROWS, COLS))
OFFSET = rng.random(COLS) * ROWS
CYCLES = rng.choice([1, 1, 1, 2], COLS)
LENGTH = rng.uniform(8, 19, COLS)
DEPTH = rng.uniform(.36, 1, COLS)
TWINKLE = rng.random((ROWS, COLS))
SWITCH = rng.choice([1, 2], (ROWS, COLS))
Y, X = np.mgrid[0:ROWS, 0:COLS]
QUIET = 1 - .43 * np.exp(-((X - COLS / 2) / 20) ** 4
                          - ((Y - ROWS * .64) / 7) ** 4)


def render_background(phase):
    """Pure periodic frame. Phase 0 and 1 are exactly identical."""
    phase = phase % 1.0
    head = (OFFSET + phase * ROWS * CYCLES) % ROWS
    distance = (head[None, :] - Y + ROWS / 2) % ROWS - ROWS / 2
    # Overlapping periodic Gaussian glyphs fade in before the head crosses
    # a row. A modulo-truncated exponential would pop each character on.
    tail = np.zeros((ROWS, COLS), dtype=np.float64)
    for step in range(15):
        delta = (distance - step + ROWS / 2) % ROWS - ROWS / 2
        tail += np.exp(-.5 * (delta / .82) ** 2) * np.exp(-step / (LENGTH[None, :] * .26))
    tail *= .68
    brightness = (.009 + tail) * DEPTH[None, :] * QUIET
    brightness *= .87 + .13 * np.cos(2 * math.pi * (phase + TWINKLE))
    mix = (.5 - .5 * np.cos(2 * math.pi * (phase * SWITCH + TWINKLE)))
    masks = ATLAS[INDEX_A] * (1 - mix[:, :, None, None])
    masks += ATLAS[INDEX_B] * mix[:, :, None, None]
    mask = masks.transpose(0, 2, 1, 3).reshape(HEIGHT, COLS * CELL)[:, :WIDTH]
    light = np.repeat(np.repeat(brightness, CELL, axis=0), CELL, axis=1)[:, :WIDTH]
    lead = np.exp(-distance * distance / .8) * DEPTH[None, :]
    lead = np.repeat(np.repeat(lead, CELL, axis=0), CELL, axis=1)[:, :WIDTH]
    rgb = np.empty((HEIGHT, WIDTH, 3), dtype=np.float32)
    rgb[:, :, 0] = 1 + mask * (light * 24 + lead * 105)
    rgb[:, :, 1] = 5 + mask * (light * 208 + lead * 42)
    rgb[:, :, 2] = 3 + mask * (light * 77 + lead * 92)
    image = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    glow = image.resize((400, 180)).filter(ImageFilter.GaussianBlur(1.4))
    glow = glow.resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
    # A restrained halo adds depth without obscuring the character shapes.
    return Image.blend(image, glow, .20)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'ohc-code-rain-original.mp4')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WIDTH}x{HEIGHT}',
        '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264', '-threads', '2',
        '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart', str(args.output),
    ], stdin=subprocess.PIPE)
    frames = SECONDS * FPS
    first = last = previous = None
    differences = []
    assert np.array_equal(np.asarray(render_background(0)), np.asarray(render_background(1)))
    try:
        for index in range(frames):
            frame = render_background(index / frames)
            pixels = np.asarray(frame).astype(float)
            if first is None: first = pixels.copy()
            if previous is not None: differences.append(float(np.mean(np.abs(pixels - previous))))
            previous = last = pixels
            process.stdin.write(frame.tobytes())
            if index == 72: frame.save(args.output.with_suffix('.jpg'), quality=95)
            if index % 90 == 0: print(f'Rendered {index}/{frames}', flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0: raise RuntimeError('video encoder failed')
    seam = float(np.mean(np.abs(first - last)))
    assert seam <= max(differences) * 1.2
    print(json.dumps(dict(size=[WIDTH, HEIGHT], frames=frames, fps=FPS, seconds=SECONDS,
        exact_periodicity=True, seam=seam, max_adjacent=max(differences), sensor_values=False)), flush=True)


if __name__ == '__main__':
    main()
