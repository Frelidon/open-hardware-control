#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project-owned application branding widgets and icon selection."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QLabel


def branding_icon_path(app_dir: Path) -> Path:
    preferred = app_dir / "assets" / "branding" / "open-hardware-control-icon.png"
    if preferred.is_file():
        return preferred
    flat_svg = app_dir / "kraken-control.svg"
    return flat_svg if flat_svg.is_file() else app_dir / "packaging" / "kraken-control.svg"


def application_icon(app_dir: Path) -> QIcon:
    icon_path = branding_icon_path(app_dir)
    return QIcon(str(icon_path)) if icon_path.is_file() else QIcon.fromTheme("preferences-system-cooling")


def system_tray_icon(app_dir: Path) -> QIcon:
    """Return the project emblem at Plasma tray-native raster sizes."""
    icon = QIcon()
    icon_dir = app_dir / "assets" / "branding" / "icons"
    for size in (22, 32, 48, 64):
        path = icon_dir / f"open-hardware-control-{size}.png"
        if path.is_file():
            icon.addFile(
                str(path), QSize(size, size), QIcon.Mode.Normal, QIcon.State.Off,
            )
    return icon if not icon.isNull() else application_icon(app_dir)


def create_sidebar_branding(app_dir: Path) -> tuple[QLabel | None, QLabel]:
    logo = QLabel()
    logo.setObjectName("brandLogo")
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    logo.setAccessibleName("Logo von Open Hardware Control")
    pixmap = QPixmap(str(app_dir / "assets" / "branding" / "open-hardware-control-logo.png"))
    if pixmap.isNull():
        logo = None
    else:
        logo.setPixmap(pixmap.scaled(
            190, 190, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))
        logo.setFixedHeight(190)
    title = QLabel("Open Hardware\nControl")
    title.setWordWrap(True)
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setObjectName("brandLabel")
    return logo, title
