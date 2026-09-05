#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure Levita panel and configurable image/notch boundary geometry.

This module is pure geometry. It has no Qt, USB or TRCC dependency so local
coding models can load it alone. The 1600×720 panel keeps a straight vertical
split to the right-hand camera bar. The outer panel corners and the two inner
image corners are separate radii: the latter make the visible content end in
the same modern curve above and below the black camera bar.
"""

from __future__ import annotations

from typing import Any
import math


LEVITA_WIDTH = 1600
LEVITA_HEIGHT = 720
DEFAULT_OUTER_CORNER_RADIUS = 18
DEFAULT_INNER_CORNER_RADIUS = 48
MAX_INNER_CORNER_RADIUS = 240


def bounded_inner_corner_radius(radius: int) -> int:
    return max(0, min(MAX_INNER_CORNER_RADIUS, int(radius)))


def right_notch_left_x(
    y: int,
    *,
    notch_width: int,
    top_radius: int = DEFAULT_INNER_CORNER_RADIUS,
    bottom_radius: int = DEFAULT_INNER_CORNER_RADIUS,
    width: int = LEVITA_WIDTH,
    height: int = LEVITA_HEIGHT,
) -> int:
    """Return the first masked x pixel for one scanline of the right bar."""

    boundary = width - max(1, min(width, int(notch_width)))
    row = max(0, min(height - 1, int(y)))
    top = bounded_inner_corner_radius(top_radius)
    bottom = bounded_inner_corner_radius(bottom_radius)
    if top and row < top:
        dy = top - row
        return round(boundary - top + math.sqrt(max(0, top * top - dy * dy)))
    if bottom and row > height - 1 - bottom:
        dy = row - (height - 1 - bottom)
        return round(boundary - bottom + math.sqrt(max(0, bottom * bottom - dy * dy)))
    return boundary


def fill_right_notch_mask(
    image: Any,
    fill: Any,
    *,
    notch_width: int,
    top_radius: int = DEFAULT_INNER_CORNER_RADIUS,
    bottom_radius: int = DEFAULT_INNER_CORNER_RADIUS,
) -> None:
    """Fill the right bar including its independently rounded inner corners."""

    width, height = image.size
    pixels = image.load()
    for y in range(height):
        start = right_notch_left_x(
            y,
            notch_width=notch_width,
            top_radius=top_radius,
            bottom_radius=bottom_radius,
            width=width,
            height=height,
        )
        for x in range(max(0, start), width):
            pixels[x, y] = fill


def levita_outer_corner_radius(notch_width: int | None = None) -> int:
    if notch_width is None:
        return DEFAULT_OUTER_CORNER_RADIUS
    return min(DEFAULT_OUTER_CORNER_RADIUS, max(1, int(notch_width) // 2))


def pixel_is_outside_levita_panel(
    x: int,
    y: int,
    *,
    radius: int | None = None,
    width: int = LEVITA_WIDTH,
    height: int = LEVITA_HEIGHT,
) -> bool:
    """Return True for pixels in the two outer-right corner bites."""

    if x < 0 or y < 0 or x >= width or y >= height:
        return True
    corner = DEFAULT_OUTER_CORNER_RADIUS if radius is None else max(1, int(radius))
    dx = x - (width - 1 - corner)
    if dx <= 0:
        return False
    if y <= corner:
        dy = corner - y
        return dx * dx + dy * dy > corner * corner
    if y >= height - 1 - corner:
        dy = y - (height - 1 - corner)
        return dx * dx + dy * dy > corner * corner
    return False


def fill_outside_levita_panel(image: Any, fill: Any, *, radius: int | None = None) -> None:
    """Punch the outer-right display corners without touching the inner notch edge."""

    width, height = image.size
    corner = DEFAULT_OUTER_CORNER_RADIUS if radius is None else max(1, int(radius))
    pixels = image.load()
    for y in range(0, corner + 1):
        for x in range(width - corner, width):
            if pixel_is_outside_levita_panel(x, y, radius=corner, width=width, height=height):
                pixels[x, y] = fill
    for y in range(height - corner, height):
        for x in range(width - corner, width):
            if pixel_is_outside_levita_panel(x, y, radius=corner, width=width, height=height):
                pixels[x, y] = fill
