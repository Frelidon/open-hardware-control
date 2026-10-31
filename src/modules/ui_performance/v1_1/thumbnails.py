# SPDX-License-Identifier: GPL-3.0-or-later
"""Small source-versioned still thumbnails, never full-resolution card pixmaps."""
from PySide6.QtCore import QIODevice, QSaveFile, QSize, Qt
from PySide6.QtGui import QImageReader, QPixmap
from .cache import cache_budget_mb, preview_cache_path


def card_source(source, settings):
    target = preview_cache_path("levita-still", source, cache_budget_mb(settings), ".png")
    try:
        if target is not None and not target.is_symlink() and target.is_file() and target.stat().st_size < 128_000:
            cached = QPixmap(str(target))
            if not cached.isNull() and cached.size() == QSize(176, 79): return cached
    except OSError:
        pass
    reader = QImageReader(str(source))
    size = reader.size()
    if not size.isValid() or size.width() * size.height() > 64_000_000: return QPixmap()
    scaled = size.scaled(QSize(176, 79), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
    if max(scaled.width(), scaled.height()) > 4096: return QPixmap()
    reader.setScaledSize(scaled)
    reader.setAutoTransform(True)
    pixmap = QPixmap.fromImage(reader.read())
    if pixmap.isNull(): return pixmap
    pixmap = pixmap.scaled(176, 79, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                           Qt.TransformationMode.SmoothTransformation).copy(0, 0, 176, 79)
    if target is not None and not target.is_symlink():
        output = QSaveFile(str(target))
        if output.open(QIODevice.OpenModeFlag.WriteOnly):
            if pixmap.save(output, "PNG"): output.commit()
            else: output.cancelWriting()
    return pixmap
