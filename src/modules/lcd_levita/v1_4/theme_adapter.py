#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only TRCC layout adapter and OHC-owned Levita 1.4 theme staging.

Only the separately installed TRCC backend decodes legacy ``config1.dc``.
OHC never writes that file.  Editable layouts are represented by a generated
``trcc.json`` in OHC's cache and symlink the selected local artwork/media.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Mapping

from .layout_model import EditableLayout, layout_fingerprint, layout_from_config


MODULE_VERSION = "1.4"
LEVITA_WIDTH = 1600
LEVITA_HEIGHT = 720
_STATIC_ASSETS = ("00.png", "01.png", "Theme.png")
_VIDEO_ASSETS = ("Theme.zt", "Theme.mp4", "Theme.mov", "Theme.webm", "Theme.mkv", "Theme.avi")


class ThemeLayoutError(ValueError):
    """The selected layout cannot safely be exposed as an editable layer."""


def read_theme_config(theme_dir: Path) -> dict[str, Any]:
    """Read next-native JSON or delegate legacy DC decoding to TRCC Linux."""
    source = theme_dir.expanduser().resolve()
    if not source.is_dir():
        raise ThemeLayoutError(f"Kein lesbarer Theme-Ordner: {source}")
    json_path = source / "trcc.json"
    if json_path.is_file():
        try:
            value = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ThemeLayoutError(f"Ungültige TRCC-Layoutdatei: {json_path}") from exc
        if not isinstance(value, dict):
            raise ThemeLayoutError(f"TRCC-Layoutwurzel ist kein Objekt: {json_path}")
        return value

    dc_path = source / "config1.dc"
    if not dc_path.is_file():
        raise ThemeLayoutError(f"Weder trcc.json noch config1.dc gefunden: {source}")
    try:
        dc_module = importlib.import_module("trcc.services._dc")
    except (ImportError, AttributeError) as exc:
        raise ThemeLayoutError(
            "Das Legacy-Layout benötigt das separat installierte TRCC-Linux-Backend zum sicheren Lesen"
        ) from exc
    try:
        value = dc_module.File(dc_path).read()
    except Exception as exc:
        # TRCC defines its decoder errors in its own optional package.  Keep
        # that implementation detail outside OHC's stable adapter contract.
        raise ThemeLayoutError(f"TRCC konnte das Legacy-Layout nicht lesen: {dc_path}") from exc
    if not isinstance(value, dict):
        raise ThemeLayoutError(f"TRCC lieferte kein gültiges Layout für {dc_path}")
    return value


def load_editable_layout(theme_dir: Path) -> tuple[EditableLayout, dict[str, Any]]:
    config = read_theme_config(theme_dir)
    layout = layout_from_config(theme_dir, config)
    if not layout.blocks:
        raise ThemeLayoutError("Dieses Theme enthält keine editierbaren Datenblöcke")
    return layout, config


def _asset_fingerprint(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        stat = path.stat()
    except OSError:
        return str(path)
    return f"{path.resolve()}:{stat.st_size}:{stat.st_mtime_ns}"


def _ensure_symlink(source: Path, target: Path) -> None:
    if target.exists() or target.is_symlink():
        return
    target.symlink_to(source.resolve())


def stage_editable_theme(
    theme_dir: Path,
    cache_root: Path,
    layout: EditableLayout,
    base_config: Mapping[str, Any],
    *,
    background_image: Path | None = None,
    background_video: Path | None = None,
    mask_image: Path | None = None,
    include_source_video: bool = False,
    safe_right_x: int = 1520,
) -> Path:
    """Create one immutable TRCC theme carrying all selected layer assets.

    Keeping the external video and generated mask inside the staged theme lets
    TRCC load them during one connected ``load-theme`` process.  This avoids
    repeatedly opening the Levita USB endpoints for separate ``play-video``
    and ``apply-mask`` commands.
    """
    source = theme_dir.expanduser().resolve()
    if layout.source != str(source):
        raise ThemeLayoutError("Layout und ausgewähltes Theme gehören nicht zusammen")
    image = background_image.expanduser().resolve() if background_image is not None else None
    if image is not None and (not image.is_file() or image.suffix.casefold() not in {".png", ".jpg", ".jpeg", ".bmp", ".webp"}):
        raise ThemeLayoutError(f"Kein unterstütztes statisches Hintergrundbild: {image}")
    video = background_video.expanduser().resolve() if background_video is not None else None
    if video is not None and (not video.is_file() or video.suffix.casefold() not in {".zt", ".mp4", ".mov", ".webm", ".mkv", ".avi"}):
        raise ThemeLayoutError(f"Kein unterstütztes Hintergrundvideo: {video}")
    mask = mask_image.expanduser().resolve() if mask_image is not None else None
    if mask is not None and (not mask.is_file() or mask.suffix.casefold() != ".png"):
        raise ThemeLayoutError(f"Keine unterstützte Levita-Maske: {mask}")
    if image is not None and video is not None:
        raise ThemeLayoutError("Ein Cache-Theme darf nicht gleichzeitig Bild- und Videoersatz enthalten")

    config_marker = source / "trcc.json"
    if not config_marker.is_file():
        config_marker = source / "config1.dc"
    combined = (
        f"{layout_fingerprint(layout)}:{_asset_fingerprint(config_marker)}:"
        f"{_asset_fingerprint(image)}:{_asset_fingerprint(video)}:"
        f"{_asset_fingerprint(mask)}:{include_source_video}:{int(safe_right_x)}"
    )
    import hashlib

    fingerprint = hashlib.sha256(combined.encode("utf-8")).hexdigest()[:24]
    target = cache_root.expanduser().resolve() / f"theme-{fingerprint}"
    target.mkdir(parents=True, exist_ok=True)

    for name in _STATIC_ASSETS:
        asset = source / name
        if name == "00.png" and image is not None:
            asset = image
        elif name == "01.png" and mask is not None:
            asset = mask
        if asset.is_file():
            _ensure_symlink(asset, target / name)
    if video is not None:
        _ensure_symlink(video, target / f"Theme{video.suffix.casefold()}")
    elif include_source_video:
        for name in _VIDEO_ASSETS:
            asset = source / name
            if asset.is_file():
                _ensure_symlink(asset, target / name)

    excluded_config_keys = {"elements", "background", "name", "width", "height"}
    if mask is not None:
        # A generated full-canvas mask must be self-contained.  Never retain
        # a source-theme mask path that may point outside this cache theme.
        excluded_config_keys.update({"mask", "mask_position", "mask_visible"})
    config = {
        key: value for key, value in dict(base_config).items()
        if key not in excluded_config_keys
    }
    config.update({
        "name": f"OHC editable · {source.name}",
        "width": LEVITA_WIDTH,
        "height": LEVITA_HEIGHT,
        "overlay_enabled": True,
        "elements": layout.to_trcc_elements(safe_right_x=safe_right_x),
    })
    if mask is not None:
        config.update({
            "mask_position": [LEVITA_WIDTH // 2, LEVITA_HEIGHT // 2],
            "mask_visible": True,
        })
    config_path = target / "trcc.json"
    if not config_path.is_file():
        config_path.write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return target
