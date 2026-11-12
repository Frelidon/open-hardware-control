# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded aspect-correct zoom plans; no Qt, subprocess or hardware here."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
from .catalog import validate_pair_media
from .mp4_metadata import valid_lcd_mp4

WIDTH, HEIGHT = 1600, 720
MAX_BYTES = 128 * 1024 * 1024


def valid_zoom(value):
    if type(value) is not int or not 50 <= value <= 200 or value % 5:
        raise ValueError("invalid LCD zoom")
    return value


def zoom_filter(value):
    """Match preview: fit original aspect, zoom both axes, pad/crop centrally."""
    zoom = valid_zoom(value)
    return (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:black,"
        f"scale={WIDTH * zoom // 100}:{HEIGHT * zoom // 100},"
        f"pad=max(iw\\,{WIDTH}):max(ih\\,{HEIGHT}):(ow-iw)/2:(oh-ih)/2:black,"
        f"crop={WIDTH}:{HEIGHT}:(iw-ow)/2:(ih-oh)/2,setsar=1,format=yuv420p"
    )


@dataclass(frozen=True)
class ZoomPlan:
    source: Path
    target: Path
    zoom: int


def zoom_plan(source, cache, zoom):
    source = validate_pair_media(source)
    zoom = valid_zoom(zoom)
    stat = source.stat()
    fingerprint = hashlib.sha256(
        f"{source}:{stat.st_size}:{stat.st_mtime_ns}:{zoom}:paired-zoom-v1".encode()
    ).hexdigest()[:32]
    return ZoomPlan(source, Path(cache).resolve() / f"paired-zoom-{fingerprint}.mp4", zoom)


def valid_output(plan):
    path = plan.target
    try:
        if path.is_symlink() or not path.is_file() or not 4096 <= path.stat().st_size <= MAX_BYTES:
            return False
        with path.open('rb') as stream:
            return valid_lcd_mp4(stream, path.stat().st_size, WIDTH, HEIGHT)
    except OSError:
        return False


def encoder_arguments(plan, temporary):
    return ["-v", "error", "-nostdin", "-n", "-i", str(plan.source),
            "-map", "0:v:0", "-an", "-t", "35", "-vf", zoom_filter(plan.zoom),
            "-c:v", "libx264", "-threads", "2", "-preset", "veryfast", "-crf", "20",
            "-fs", str(MAX_BYTES), "-movflags", "+faststart", str(temporary)]


def validate_prepared(prepared, source, cache, zoom):
    expected = zoom_plan(source, cache, zoom)
    if not isinstance(prepared, ZoomPlan) or prepared != expected or not valid_output(expected):
        raise ValueError("unverified paired-design derivative")
    return expected.target
