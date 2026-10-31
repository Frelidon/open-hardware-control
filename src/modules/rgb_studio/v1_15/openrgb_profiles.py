#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded private library for user-supplied OpenRGB profiles."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil


MAX_PROFILE_BYTES = 32 * 1024 * 1024
LEGACY_HEADER = b"OPENRGB_PROFILE"


@dataclass(frozen=True, slots=True)
class ImportedOpenRGBProfile:
    path: Path
    title: str
    format: str
    device_names: tuple[str, ...] = ()

    @property
    def supports_device_filter(self) -> bool:
        return self.format == "json-v6"


def inspect_openrgb_profile(path: Path) -> ImportedOpenRGBProfile:
    requested = path.expanduser()
    if requested.is_symlink():
        raise ValueError("OpenRGB-Profile dürfen keine symbolischen Links sein.")
    source = requested.resolve(strict=True)
    if not source.is_file() or source.stat().st_size > MAX_PROFILE_BYTES:
        raise ValueError("Das OpenRGB-Profil ist ungültig oder größer als 32 MiB.")
    if source.suffix.casefold() == ".orp":
        with source.open("rb") as stream:
            header = stream.read(20)
        if len(header) != 20 or not header.startswith(LEGACY_HEADER + b"\0"):
            raise ValueError("Die Datei ist kein gültiges binäres OpenRGB-Profil.")
        return ImportedOpenRGBProfile(source, source.stem[:96], "legacy-orp")
    if source.suffix.casefold() != ".json":
        raise ValueError("OpenRGB-Profile müssen .orp oder .json verwenden.")
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("profile_version"), int):
        raise ValueError("Das OpenRGB-JSON-Profil besitzt keine gültige Profilversion.")
    controllers = payload.get("controllers", [])
    if not isinstance(controllers, list) or len(controllers) > 128:
        raise ValueError("Das OpenRGB-JSON-Profil enthält eine ungültige Controllerliste.")
    names: list[str] = []
    for controller in controllers:
        if not isinstance(controller, dict):
            raise ValueError("Das OpenRGB-JSON-Profil enthält ungültige Controllerdaten.")
        lowered = {str(key).casefold(): value for key, value in controller.items()}
        name = str(lowered.get("name") or lowered.get("description") or "").strip()[:96]
        if name:
            names.append(name)
    title = str(payload.get("profile_name") or source.stem).replace("\n", " ").strip()[:96]
    return ImportedOpenRGBProfile(source, title or source.stem[:96], "json-v6", tuple(names))


def import_openrgb_profile(source: Path, library: Path) -> ImportedOpenRGBProfile:
    inspected = inspect_openrgb_profile(source)
    target_root = library.expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)
    if target_root.is_symlink() or not target_root.is_dir():
        raise ValueError("Die private OpenRGB-Profilbibliothek ist nicht sicher beschreibbar.")
    digest = hashlib.sha256(inspected.path.read_bytes()).hexdigest()[:12]
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", inspected.path.stem).strip(".-")[:64] or "profile"
    target = target_root / f"{stem}-{digest}{inspected.path.suffix.casefold()}"
    temporary = target.with_suffix(target.suffix + ".tmp")
    with inspected.path.open("rb") as source_stream, temporary.open("wb") as target_stream:
        shutil.copyfileobj(source_stream, target_stream, length=1024 * 1024)
    temporary.replace(target)
    return inspect_openrgb_profile(target)


def list_openrgb_profiles(library: Path) -> tuple[ImportedOpenRGBProfile, ...]:
    root = library.expanduser().resolve()
    if not root.is_dir() or root.is_symlink():
        return ()
    result: list[ImportedOpenRGBProfile] = []
    for candidate in sorted(root.iterdir(), key=lambda item: item.name.casefold())[:256]:
        try:
            result.append(inspect_openrgb_profile(candidate))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
    return tuple(result)
