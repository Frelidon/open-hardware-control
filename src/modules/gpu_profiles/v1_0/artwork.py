# SPDX-License-Identifier: GPL-3.0-or-later
"""Import transparent user-owned GPU artwork into OHC's private config area."""

from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path

from PySide6.QtGui import QImageReader


MAX_ARTWORK_BYTES = 12 * 1024 * 1024
MAX_ARTWORK_SIDE = 8192


def import_transparent_artwork(source: Path, managed_directory: Path) -> Path:
    source = Path(source)
    if (not source.is_file() or source.is_symlink()
            or source.suffix.casefold() not in {".png", ".webp"}
            or source.stat().st_size <= 0 or source.stat().st_size > MAX_ARTWORK_BYTES):
        raise ValueError("GPU image must be a bounded PNG or WebP file")
    reader = QImageReader(str(source))
    reader.setAutoTransform(True)
    size = reader.size()
    if (not size.isValid() or size.width() > MAX_ARTWORK_SIDE
            or size.height() > MAX_ARTWORK_SIDE):
        raise ValueError("GPU image dimensions are invalid")
    image = reader.read()
    if image.isNull() or not image.hasAlphaChannel():
        raise ValueError("GPU image needs a transparent alpha channel")
    payload = source.read_bytes()
    if managed_directory.is_symlink():
        raise ValueError("Managed GPU image directory is not safe")
    managed_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not managed_directory.is_dir() or managed_directory.is_symlink():
        raise ValueError("Managed GPU image directory is not safe")
    os.chmod(managed_directory, 0o700)
    name = "gpu-art-" + sha256(payload).hexdigest()[:20] + ".png"
    destination = managed_directory / name
    if destination.is_symlink():
        raise ValueError("Managed GPU image path is not safe")
    if not image.save(str(destination), "PNG"):
        raise ValueError("GPU image could not be normalized")
    os.chmod(destination, 0o600)
    return destination


def remove_managed_artwork(path: Path, managed_directory: Path) -> bool:
    """Delete only a regular OHC-managed GPU artwork file."""
    candidate = Path(path)
    root = managed_directory.resolve()
    try:
        parent = candidate.parent.resolve()
    except OSError:
        return False
    if (parent != root or candidate.is_symlink() or not candidate.is_file()
            or not candidate.name.startswith("gpu-art-") or candidate.suffix != ".png"):
        return False
    try:
        candidate.unlink()
        return True
    except OSError:
        return False
