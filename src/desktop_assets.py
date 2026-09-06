#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate and install the original OHC desktop icon and cursor themes.

The themes in this module are drawn from project-owned source code.  No files
from Microsoft, Apple or a third-party theme archive are downloaded, extracted
or redistributed.  Every output path and file name is fixed by this module.
"""

from __future__ import annotations

import json
import os
import shutil
import struct
import tempfile
from pathlib import Path
from typing import Mapping

try:
    from PIL import Image, ImageDraw
except ImportError:  # handled by the application's dependency helper
    Image = None
    ImageDraw = None


ASSET_SCHEMA_VERSION = 1
ICON_THEMES = {
    "system": {"title": "KDE-Standardsymbole", "theme": "breeze"},
    "ohc-windows11": {"title": "OHC Windowed 11", "theme": "OHC-Windowed-11"},
    "ohc-macos": {"title": "OHC Orchard", "theme": "OHC-Orchard"},
    "ohc-windows8": {"title": "OHC Metro 8", "theme": "OHC-Metro-8"},
}
CURSOR_THEMES = {
    "system": {"title": "KDE-Standardzeiger", "theme": "breeze_cursors"},
    "ohc-windows11": {"title": "OHC Windowed Cursor", "theme": "OHC-Windowed-Cursor"},
    "ohc-macos": {"title": "OHC Orchard Cursor", "theme": "OHC-Orchard-Cursor"},
    "ohc-windows8": {"title": "OHC Metro Cursor", "theme": "OHC-Metro-Cursor"},
}

_ICON_NAMES = (
    "start-here-kde",
    "system-search",
    "document-share",
    "preferences-system",
    "computer",
    "folder",
    "user-home",
    "drive-harddisk",
)
_CURSOR_ALIASES = {
    "left_ptr": ("default", "arrow", "top_left_arrow"),
    "hand2": ("pointer", "hand", "pointing_hand"),
    "xterm": ("text", "ibeam"),
    "watch": ("wait", "progress"),
    "crosshair": ("cross", "tcross"),
    "size_hor": ("ew-resize", "left_side", "right_side"),
    "size_ver": ("ns-resize", "top_side", "bottom_side"),
}


class DesktopAssetError(RuntimeError):
    """Raised when generated desktop assets cannot be installed safely."""


def data_root(env: Mapping[str, str] | None = None) -> Path:
    values = os.environ if env is None else env
    override = values.get("OHC_DESKTOP_ASSET_DATA_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    xdg = values.get("XDG_DATA_HOME", "").strip()
    return Path(xdg).expanduser() if xdg else Path.home() / ".local" / "share"


def icon_theme_name(option: str) -> str:
    try:
        return str(ICON_THEMES[option]["theme"])
    except KeyError as exc:
        raise DesktopAssetError(f"Unbekannte Symbolauswahl: {option}") from exc


def cursor_theme_name(option: str) -> str:
    try:
        return str(CURSOR_THEMES[option]["theme"])
    except KeyError as exc:
        raise DesktopAssetError(f"Unbekannte Mauszeigerauswahl: {option}") from exc


def _safe_theme_destination(root: Path, theme_name: str) -> Path:
    if not theme_name.startswith("OHC-") or "/" in theme_name or "\\" in theme_name:
        raise DesktopAssetError("Unsicherer Theme-Name wurde abgewiesen.")
    icons_root = (root / "icons").resolve()
    destination = icons_root / theme_name
    if destination.parent != icons_root:
        raise DesktopAssetError("Theme-Ziel liegt außerhalb des erlaubten Datenverzeichnisses.")
    if destination.is_symlink():
        raise DesktopAssetError(f"Das Theme-Ziel ist ein symbolischer Link: {destination}")
    return destination


def _svg(theme: str, icon: str) -> str:
    palettes = {
        "OHC-Windowed-11": ("#58a6ff", "#eaf4ff", "#172033"),
        "OHC-Orchard": ("#8e8e93", "#f5f5f7", "#202124"),
        "OHC-Metro-8": ("#00a4ef", "#ffffff", "#12304a"),
    }
    accent, foreground, dark = palettes[theme]
    shapes = {
        "start-here-kde": (
            f'<rect x="5" y="5" width="24" height="24" rx="{6 if theme != "OHC-Metro-8" else 0}" fill="{accent}"/>'
            f'<path d="M10 10h6v6h-6zm8 0h6v6h-6zm-8 8h6v6h-6zm8 0h6v6h-6z" fill="{foreground}"/>'
        ),
        "system-search": f'<circle cx="14" cy="14" r="7" fill="none" stroke="{accent}" stroke-width="3"/><path d="M19 19l8 8" stroke="{dark}" stroke-width="3" stroke-linecap="round"/>',
        "document-share": f'<path d="M9 25V11h8" fill="none" stroke="{dark}" stroke-width="3"/><path d="M15 8l9 0m0 0l-5-5m5 5l-5 5" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
        "preferences-system": f'<circle cx="16" cy="16" r="6" fill="{foreground}" stroke="{dark}" stroke-width="3"/><path d="M16 3v5m0 16v5M3 16h5m16 0h5M7 7l4 4m10 10l4 4M25 7l-4 4M11 21l-4 4" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>',
        "computer": f'<rect x="4" y="5" width="24" height="17" rx="2" fill="{dark}"/><rect x="7" y="8" width="18" height="11" fill="{accent}"/><path d="M11 27h10M16 22v5" stroke="{dark}" stroke-width="2"/>',
        "folder": f'<path d="M3 9h11l3 3h12v15H3z" fill="{accent}"/><path d="M3 9V6h10l3 3" fill="{foreground}" stroke="{dark}" stroke-width="2"/>',
        "user-home": f'<path d="M4 16L16 5l12 11v12H4z" fill="{accent}"/><path d="M12 28v-9h8v9" fill="{foreground}"/>',
        "drive-harddisk": f'<rect x="4" y="7" width="24" height="19" rx="3" fill="{dark}"/><circle cx="10" cy="20" r="2" fill="{accent}"/><path d="M15 20h9" stroke="{foreground}" stroke-width="2"/>',
    }
    body = shapes[icon]
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">'
        + body
        + "</svg>\n"
    )


def _write_icon_theme(destination: Path, title: str) -> None:
    for size in (32, 48, 64, 128):
        directory = destination / f"{size}x{size}" / "apps"
        directory.mkdir(parents=True, exist_ok=True)
        for icon in _ICON_NAMES:
            (directory / f"{icon}.svg").write_text(_svg(title, icon), encoding="utf-8")
    directories = ",".join(f"{size}x{size}/apps" for size in (32, 48, 64, 128))
    sections = []
    for size in (32, 48, 64, 128):
        sections.append(
            f"\n[{size}x{size}/apps]\nSize={size}\nContext=Applications\nType=Scalable\nMinSize=16\nMaxSize=256\n"
        )
    (destination / "index.theme").write_text(
        "[Icon Theme]\n"
        f"Name={title}\n"
        "Comment=Original Open Hardware Control artwork; no vendor assets\n"
        "Inherits=breeze\n"
        f"Directories={directories}\n"
        + "".join(sections),
        encoding="utf-8",
    )


def _cursor_canvas(kind: str, variant: str, size: int):
    if Image is None or ImageDraw is None:
        raise DesktopAssetError("Pillow wird zum Erzeugen der Mauszeiger benötigt.")
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    scale = size / 32.0
    fg = (255, 255, 255, 255) if variant != "OHC-Orchard-Cursor" else (25, 25, 27, 255)
    edge = (20, 30, 46, 255) if variant != "OHC-Orchard-Cursor" else (255, 255, 255, 255)
    accent = (0, 164, 239, 255) if "Metro" in variant else (88, 166, 255, 255)
    if "Orchard" in variant:
        accent = (142, 142, 147, 255)
    sw = max(1, round(2 * scale))
    if kind == "left_ptr":
        points = [(4, 3), (4, 25), (10, 19), (15, 29), (20, 26), (15, 17), (25, 17)]
        points = [(round(x * scale), round(y * scale)) for x, y in points]
        draw.polygon(points, fill=fg, outline=edge)
        draw.line(points + [points[0]], fill=edge, width=sw, joint="curve")
        hot = (round(4 * scale), round(3 * scale))
    elif kind == "hand2":
        draw.rounded_rectangle((9 * scale, 8 * scale, 23 * scale, 28 * scale), radius=4 * scale, fill=fg, outline=edge, width=sw)
        draw.line((13 * scale, 17 * scale, 13 * scale, 3 * scale), fill=edge, width=max(sw, round(4 * scale)))
        draw.line((13 * scale, 3 * scale, 13 * scale, 17 * scale), fill=fg, width=max(1, round(2 * scale)))
        hot = (round(13 * scale), round(3 * scale))
    elif kind == "xterm":
        x = round(16 * scale)
        draw.line((x, 5 * scale, x, 27 * scale), fill=edge, width=max(sw, round(4 * scale)))
        draw.line((10 * scale, 5 * scale, 22 * scale, 5 * scale), fill=edge, width=sw)
        draw.line((10 * scale, 27 * scale, 22 * scale, 27 * scale), fill=edge, width=sw)
        draw.line((x, 6 * scale, x, 26 * scale), fill=accent, width=max(1, round(2 * scale)))
        hot = (x, round(16 * scale))
    elif kind == "watch":
        draw.ellipse((5 * scale, 5 * scale, 27 * scale, 27 * scale), fill=fg, outline=edge, width=sw)
        draw.arc((8 * scale, 8 * scale, 24 * scale, 24 * scale), 275, 65, fill=accent, width=max(sw, round(4 * scale)))
        hot = (round(16 * scale), round(16 * scale))
    elif kind == "crosshair":
        c = round(16 * scale)
        draw.ellipse((9 * scale, 9 * scale, 23 * scale, 23 * scale), outline=edge, width=sw)
        draw.line((c, 2 * scale, c, 30 * scale), fill=accent, width=sw)
        draw.line((2 * scale, c, 30 * scale, c), fill=accent, width=sw)
        hot = (c, c)
    elif kind == "size_hor":
        c = round(16 * scale)
        draw.line((4 * scale, c, 28 * scale, c), fill=edge, width=max(sw, round(3 * scale)))
        draw.polygon([(4 * scale, c), (10 * scale, 10 * scale), (10 * scale, 22 * scale)], fill=accent)
        draw.polygon([(28 * scale, c), (22 * scale, 10 * scale), (22 * scale, 22 * scale)], fill=accent)
        hot = (c, c)
    else:
        c = round(16 * scale)
        draw.line((c, 4 * scale, c, 28 * scale), fill=edge, width=max(sw, round(3 * scale)))
        draw.polygon([(c, 4 * scale), (10 * scale, 10 * scale), (22 * scale, 10 * scale)], fill=accent)
        draw.polygon([(c, 28 * scale), (10 * scale, 22 * scale), (22 * scale, 22 * scale)], fill=accent)
        hot = (c, c)
    return image, hot


def _argb_pixels(image) -> bytes:
    result = bytearray()
    for red, green, blue, alpha in image.getdata():
        # Xcursor stores premultiplied ARGB pixels in little-endian CARD32s.
        red = (red * alpha + 127) // 255
        green = (green * alpha + 127) // 255
        blue = (blue * alpha + 127) // 255
        result.extend(struct.pack("<I", (alpha << 24) | (red << 16) | (green << 8) | blue))
    return bytes(result)


def _xcursor(kind: str, variant: str) -> bytes:
    chunks = []
    for size in (32, 48):
        image, (xhot, yhot) = _cursor_canvas(kind, variant, size)
        header = struct.pack(
            "<9I", 36, 0xFFFD0002, size, 1, size, size,
            min(max(xhot, 0), size - 1), min(max(yhot, 0), size - 1), 50,
        )
        chunks.append((size, header + _argb_pixels(image)))
    position = 16 + 12 * len(chunks)
    toc = bytearray()
    payload = bytearray()
    for size, chunk in chunks:
        toc.extend(struct.pack("<3I", 0xFFFD0002, size, position))
        payload.extend(chunk)
        position += len(chunk)
    return struct.pack("<4I", 0x72756358, 16, 0x00010000, len(chunks)) + bytes(toc) + bytes(payload)


def _write_cursor_theme(destination: Path, title: str) -> None:
    cursors = destination / "cursors"
    cursors.mkdir(parents=True, exist_ok=True)
    for primary, aliases in _CURSOR_ALIASES.items():
        data = _xcursor(primary, title)
        for name in (primary, *aliases):
            (cursors / name).write_bytes(data)
    (destination / "index.theme").write_text(
        "[Icon Theme]\n"
        f"Name={title}\n"
        "Comment=Original Open Hardware Control cursor artwork\n"
        "Inherits=breeze_cursors\n",
        encoding="utf-8",
    )


def _write_notice(destination: Path, title: str, kind: str) -> None:
    (destination / "LICENSE.txt").write_text(
        "SPDX-License-Identifier: GPL-3.0-or-later\n"
        "Copyright (C) 2026 Frelidon contributors\n\n"
        "This theme is original Open Hardware Control artwork. It contains no "
        "Microsoft, Apple or other vendor-owned files.\n",
        encoding="utf-8",
    )
    (destination / "SOURCE.json").write_text(
        json.dumps(
            {
                "schema": ASSET_SCHEMA_VERSION,
                "name": title,
                "kind": kind,
                "generator": "desktop_assets.py",
                "external_downloads": False,
                "vendor_assets": False,
                "license": "GPL-3.0-or-later",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def install_desktop_assets(root: Path | None = None) -> dict[str, object]:
    target_root = data_root() if root is None else root
    icons_root = target_root / "icons"
    icons_root.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    themes = [
        ("OHC-Windowed-11", "icon"),
        ("OHC-Orchard", "icon"),
        ("OHC-Metro-8", "icon"),
        ("OHC-Windowed-Cursor", "cursor"),
        ("OHC-Orchard-Cursor", "cursor"),
        ("OHC-Metro-Cursor", "cursor"),
    ]
    with tempfile.TemporaryDirectory(prefix="ohc-desktop-assets-") as temporary:
        staging_root = Path(temporary)
        for title, kind in themes:
            staging = staging_root / title
            if kind == "icon":
                _write_icon_theme(staging, title)
            else:
                _write_cursor_theme(staging, title)
            _write_notice(staging, title, kind)
            destination = _safe_theme_destination(target_root, title)
            if destination.exists():
                if not destination.is_dir():
                    raise DesktopAssetError(f"Theme-Ziel ist kein Verzeichnis: {destination}")
                shutil.rmtree(destination)
            shutil.copytree(staging, destination)
            installed.append(title)
    return {"ok": True, "installed": installed, "external_downloads": False, "vendor_assets": False}


def desktop_asset_status(root: Path | None = None) -> dict[str, object]:
    target_root = data_root() if root is None else root
    themes = sorted(
        {
            str(item["theme"])
            for item in (*ICON_THEMES.values(), *CURSOR_THEMES.values())
            if str(item["theme"]).startswith("OHC-")
        }
    )
    present = {
        theme: (_safe_theme_destination(target_root, theme) / "SOURCE.json").is_file()
        for theme in themes
    }
    return {
        "ok": True,
        "installed": all(present.values()),
        "themes": present,
        "icon_options": ICON_THEMES,
        "cursor_options": CURSOR_THEMES,
    }

