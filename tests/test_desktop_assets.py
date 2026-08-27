#!/usr/bin/env python3
"""Checks for locally generated, vendor-independent icon/cursor themes."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from PIL import Image

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import desktop_assets as assets


with tempfile.TemporaryDirectory(prefix="ohc-assets-test-") as temporary:
    root = Path(temporary)
    result = assets.install_desktop_assets(root)
    assert result["ok"] is True
    assert result["external_downloads"] is False
    assert result["vendor_assets"] is False
    status = assets.desktop_asset_status(root)
    assert status["installed"] is True
    for theme in status["themes"]:
        directory = root / "icons" / theme
        metadata = json.loads((directory / "SOURCE.json").read_text(encoding="utf-8"))
        assert metadata["vendor_assets"] is False
        assert metadata["external_downloads"] is False
        assert (directory / "LICENSE.txt").is_file()
    cursor = root / "icons" / "OHC-Metro-Cursor" / "cursors" / "left_ptr"
    assert cursor.read_bytes()[:4] == b"Xcur"
    assert Image is not None

try:
    assets.icon_theme_name("../../unsafe")
except assets.DesktopAssetError:
    pass
else:
    raise AssertionError("unsafe icon option accepted")

print("Desktop asset generation checks passed.")
