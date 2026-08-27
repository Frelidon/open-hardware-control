#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic local source/asset scan for OHC release candidates."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
VERSION_TEXT = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
SKIP_PARTS = {".git", "dist", "build", "__pycache__", ".pytest_cache", ".venv", "venv"}
RASTER_SUFFIXES = {".png", ".gif", ".jpg", ".jpeg", ".webp"}
SVG_FORBIDDEN = (
    b"<!doctype",
    b"<!entity",
    b"<script",
    b"foreignobject",
    b"javascript:",
    b"vbscript:",
    b"href=\"http:",
    b"href='http:",
    b"href=\"https:",
    b"href='https:",
    b"url(http:",
    b"url(https:",
)
DESKTOP_MODULES = ("desktop_assets.py", "desktop_designs.py", "desktop_shell.py")
RGB_MODULES = ("openrgb_integration.py", "openrgb_sdk.py", "rgb_devices.py", "rgb_effects.py", "nzxt_rgb.py")
TEXT_PRIVACY_SUFFIXES = {".py", ".sh", ".md", ".txt", ".xml", ".json", ".cff", ".in", ".rules", ".yml", ".yaml"}
IPV4_RE = re.compile(r"(?<![0-9])(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![0-9])")
MAC_RE = re.compile(r"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b")
ALLOWED_IPV4_PREFIXES = ((127,), (192, 0, 2), (198, 51, 100), (203, 0, 113))


def known_project_versions() -> set[str]:
    versions = {VERSION_TEXT}
    changelog = ROOT / "CHANGELOG.md"
    try:
        text = changelog.read_text(encoding="utf-8")
    except OSError:
        return versions
    for match in re.finditer(r"(?m)^#{1,6}\s+(\d+\.\d+\.\d+(?:\.\d+)?)\b", text):
        versions.add(match.group(1))
    return versions


KNOWN_PROJECT_VERSIONS = known_project_versions()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files() -> list[Path]:
    return [
        path for path in sorted(ROOT.rglob("*"))
        if path.is_file() and not any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)
    ]


def scan_python(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    ast.parse(source, filename=str(path))
    if path.name in DESKTOP_MODULES:
        if "shell=True" in source:
            raise ValueError(f"shell execution is forbidden in {path.name}")
        if path.name in {"desktop_assets.py", "desktop_shell.py"}:
            for token in ("import requests", "import urllib", "http.client", "aiohttp", "socket.socket"):
                if token in source:
                    raise ValueError(f"network token {token!r} in {path.name}")
        if path.name == "desktop_shell.py" and ("http://" in source or "https://" in source):
            raise ValueError("network URL in desktop_shell.py")
    if path.name == "nzxt_esc_profiles.py":
        for token in ("shell=True", "import requests", "import urllib", "http.client", "aiohttp", "socket.socket"):
            if token in source:
                raise ValueError(f"network/shell token {token!r} in independent preset importer")

    if path.name in RGB_MODULES:
        if "shell=True" in source:
            raise ValueError(f"shell execution is forbidden in {path.name}")
        if path.name == "rgb_effects.py":
            for token in ("subprocess", "socket", "urllib", "requests", "http://", "https://"):
                if token in source:
                    raise ValueError(f"I/O token {token!r} in pure effect module")
        if path.name == "openrgb_integration.py":
            for required in (
                "ipaddress", "is_loopback", '"--client"', "server_reachable",
                "managed_server_command", '"--noautoconnect"', "multi_color_command", "color_commands",
            ):
                if required not in source:
                    raise ValueError(f"missing OpenRGB safety token {required!r}")
        if path.name == "openrgb_sdk.py":
            for required in (
                "ipaddress", "is_loopback", "SDK_MIN_PROTOCOL_VERSION", "SDK_PROTOCOL_VERSION", "MAX_LED_COUNT",
                "PACKET_REQUEST_PROTOCOL_VERSION", "PACKET_UPDATE_LEDS", "settimeout",
            ):
                if required not in source:
                    raise ValueError(f"missing OpenRGB SDK safety token {required!r}")


def scan_svg(path: Path) -> None:
    data = path.read_bytes()
    lowered = data.lower()
    for token in SVG_FORBIDDEN:
        if token in lowered:
            raise ValueError(f"forbidden SVG token {token!r} in {path.relative_to(ROOT)}")
    root = ET.fromstring(data)
    if not root.tag.endswith("svg"):
        raise ValueError(f"unexpected SVG root in {path.relative_to(ROOT)}")
    for element in root.iter():
        for key, value in element.attrib.items():
            if key.lower().endswith("href") and value and not value.startswith("#"):
                raise ValueError(f"external SVG reference in {path.relative_to(ROOT)}")


def scan_privacy_text(path: Path) -> None:
    """Reject personal-machine traces that must never ship in release sources."""
    if path.suffix.casefold() not in TEXT_PRIVACY_SUFFIXES and path.name not in {"VERSION", "BUILD_CHANNEL"}:
        return
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    rel = path.relative_to(ROOT).as_posix()
    lowered = text.casefold()
    # Frelidon is the intentional public project identity; private real-name
    # traces and typo variants are not release metadata.
    for token in ("flo" + "rian", "fre" + "ddy don", "fre" + "ddy-don", "fre" + "ddy_don"):
        if token in lowered:
            raise ValueError(f"personal/test identity token {token!r} in {rel}")
    for match in re.finditer(r"/home/([A-Za-z0-9._-]+)", text):
        user = match.group(1)
        if user not in {"[USER]", "exampleuser"}:
            raise ValueError(f"personal home path /home/{user} in {rel}")
    for match in IPV4_RE.finditer(text):
        value = match.group(0)
        octets = tuple(int(part) for part in value.split("."))
        if any(octets[:len(prefix)] == prefix for prefix in ALLOWED_IPV4_PREFIXES):
            continue
        # 0.0.0.0 is a generic bind address rather than a host identity.
        if value == "0.0.0.0":
            continue
        # Four-component project versions can look syntactically like IPv4
        # addresses. Only versions explicitly declared as changelog headings
        # (plus the current VERSION file) are allowed, so arbitrary addresses
        # elsewhere in source/docs are still rejected.
        if value in KNOWN_PROJECT_VERSIONS:
            continue
        raise ValueError(f"non-documentation IPv4 literal {value} in {rel}")
    # Literal MACs are almost never required in source. Use symbolic placeholders
    # in tests/documentation so a captured hardware address cannot slip through.
    if MAC_RE.search(text):
        raise ValueError(f"literal MAC address in {rel}")


def scan_raster(path: Path) -> None:
    with Image.open(path) as image:
        width, height = image.size
        if width <= 0 or height <= 0 or width * height > 64_000_000:
            raise ValueError(f"unsafe image dimensions in {path.relative_to(ROOT)}")
        image.verify()
    with Image.open(path) as image:
        image.seek(0)
        image.load()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    files = source_files()
    python_files = [path for path in files if path.suffix == ".py"]
    svg_files = [path for path in files if path.suffix.casefold() == ".svg"]
    raster_files = [path for path in files if path.suffix.casefold() in RASTER_SUFFIXES]
    for path in python_files:
        scan_python(path)
    for path in svg_files:
        scan_svg(path)
    for path in raster_files:
        scan_raster(path)
    for path in files:
        scan_privacy_text(path)
    for path in files:
        if path.suffix.casefold() not in RASTER_SUFFIXES and path.suffix.casefold() != ".rpm":
            magic = path.read_bytes()[:4]
            if magic.startswith(b"\x7fELF") or magic[:2] == b"MZ":
                raise ValueError(f"unexpected executable binary: {path.relative_to(ROOT)}")
    kwin = (ROOT / "assets/desktop-designs/kwin/ohc-charms/contents/code/main.js").read_text(encoding="utf-8")
    for forbidden in ("eval(", "executeCommand", "Qt.openUrlExternally", "XMLHttpRequest", "fetch("):
        if forbidden in kwin:
            raise ValueError(f"forbidden KWin token: {forbidden}")
    report = {
        "schema": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "root": ROOT.name,
        "result": "passed",
        "source_files": len(files),
        "python_files_parsed": len(python_files),
        "svg_files_parsed": len(svg_files),
        "raster_files_verified": len(raster_files),
        "unexpected_executables": 0,
        "external_svg_references": 0,
        "desktop_network_downloads": 0,
        "desktop_modules": {name: sha256(ROOT / name) for name in DESKTOP_MODULES},
        "rgb_modules": {name: sha256(ROOT / name) for name in RGB_MODULES},
        "openrgb_remote_hosts": 0,
        "openrgb_shell_execution": 0,
        "privacy_text_files_checked": sum(1 for path in files if path.suffix.casefold() in TEXT_PRIVACY_SUFFIXES or path.name in {"VERSION", "BUILD_CHANNEL"}),
        "personal_identity_tokens": 0,
        "personal_network_identifiers": 0,
        "virus_total_upload": False,
        "virus_total_note": "No automatic file upload; standard submissions may be shared.",
    }
    if args.report:
        output = args.report.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.chmod(output, 0o644)
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
