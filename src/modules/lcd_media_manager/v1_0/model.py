#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded persistence and display names for user-owned LCD media."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re


IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"})
VIDEO_SUFFIXES = frozenset({".mp4", ".mov", ".webm", ".mkv", ".avi", ".zt"})
SUPPORTED_SUFFIXES = IMAGE_SUFFIXES | VIDEO_SUFFIXES
TRCC_CATEGORY_NAMES = {
    "a": "Galerie", "b": "Technik", "c": "HUD",
    "d": "Licht", "e": "Natur", "y": "Ästhetik",
}


@dataclass(frozen=True, slots=True)
class DesignLibraryState:
    folders: tuple[Path, ...] = ()
    files: tuple[Path, ...] = ()
    aliases: dict[str, str] = field(default_factory=dict)
    excluded: tuple[Path, ...] = ()

    @property
    def has_sources(self) -> bool:
        return bool(self.folders or self.files)


def _clean_path(value: object, *, directory: bool) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        path = Path(value).expanduser().resolve()
    except OSError:
        return None
    if path.is_symlink() or (not path.is_dir() if directory else not path.is_file()):
        return None
    if not directory and path.suffix.casefold() not in SUPPORTED_SUFFIXES:
        return None
    return path


def _unique_paths(values: object, *, directory: bool, limit: int) -> tuple[Path, ...]:
    if not isinstance(values, list):
        return ()
    result: list[Path] = []
    seen: set[Path] = set()
    for value in values[:limit]:
        path = _clean_path(value, directory=directory)
        if path is not None and path not in seen:
            seen.add(path)
            result.append(path)
    return tuple(result)


def _unique_media_items(values: object, limit: int = 2500) -> tuple[Path, ...]:
    if not isinstance(values, list):
        return ()
    result: list[Path] = []
    for value in values[:limit]:
        if not isinstance(value, str):
            continue
        try:
            path = Path(value).expanduser().resolve()
        except OSError:
            continue
        is_theme = path.is_dir() and any((path / marker).is_file() for marker in ("config1.dc", "trcc.json"))
        is_media = path.is_file() and path.suffix.casefold() in SUPPORTED_SUFFIXES
        if not path.is_symlink() and (is_theme or is_media) and path not in result:
            result.append(path)
    return tuple(result)


def load_library_state(raw: object, legacy_folder: Path | None = None) -> DesignLibraryState:
    try:
        payload = json.loads(str(raw)) if raw else {}
    except (TypeError, json.JSONDecodeError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    folders = list(_unique_paths(payload.get("folders"), directory=True, limit=32))
    legacy = _clean_path(str(legacy_folder), directory=True) if legacy_folder else None
    if legacy is not None and legacy not in folders:
        folders.insert(0, legacy)
    files = _unique_paths(payload.get("files"), directory=False, limit=500)
    excluded = _unique_media_items(payload.get("excluded"))
    def belongs_to_library(path: Path) -> bool:
        return path in files or any(path == folder or path.is_relative_to(folder) for folder in folders)
    aliases: dict[str, str] = {}
    raw_aliases = payload.get("aliases")
    if isinstance(raw_aliases, dict):
        for key, value in list(raw_aliases.items())[:2500]:
            clean = str(value).replace("\n", " ").replace("\r", " ").strip()[:96]
            candidate = _clean_path(key, directory=Path(key).is_dir()) if isinstance(key, str) else None
            if candidate is not None and clean and belongs_to_library(candidate):
                aliases[str(candidate)] = clean
    return DesignLibraryState(
        tuple(folders[:32]), files, aliases,
        tuple(path for path in excluded if belongs_to_library(path)),
    )


def save_library_state(state: DesignLibraryState) -> str:
    payload = {
        "schema": 1,
        "folders": [str(path) for path in state.folders[:32]],
        "files": [str(path) for path in state.files[:500]],
        "aliases": dict(list(state.aliases.items())[:2500]),
        "excluded": [str(path) for path in state.excluded[:2500]],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def friendly_media_name(path: Path, alias: str = "") -> str:
    """Create a stable display label without changing the user's source file."""

    clean_alias = str(alias).replace("\n", " ").replace("\r", " ").strip()[:96]
    if clean_alias:
        return clean_alias
    stem = path.stem if path.is_file() else path.name
    cloud = re.match(r"(?i)^([abcdey])(\d{3})(?:$|[^0-9])", stem)
    if cloud:
        return f"{TRCC_CATEGORY_NAMES[cloud.group(1).casefold()]} {int(cloud.group(2)):03d}"
    theme = re.fullmatch(r"(?i)theme[ _-]?(\d+)", stem)
    if theme:
        return f"TRCC-Layout {int(theme.group(1))}"
    words = re.sub(r"(?i)^chatgpt[- _]*image[- _]*", "Cyber ", stem)
    words = re.sub(r"[-_]+", " ", words)
    words = re.sub(r"\s+", " ", words).strip()
    return words[:96] or "Eigenes Design"


def library_media_items(state: DesignLibraryState, limit: int = 2500) -> tuple[Path, ...]:
    """Return the bounded, de-duplicated visible content of every source."""

    excluded = set(state.excluded)
    result: list[Path] = []
    seen: set[Path] = set()
    theme_roots: set[Path] = set()
    for folder in state.folders:
        try:
            candidates = sorted(folder.rglob("*"), key=lambda item: item.as_posix().casefold())
        except OSError:
            continue
        for path in candidates:
            if path.is_symlink() or any(root in path.parents for root in theme_roots):
                continue
            resolved = path.resolve()
            is_theme = path.is_dir() and any((path / marker).is_file() for marker in ("config1.dc", "trcc.json"))
            is_media = path.is_file() and path.suffix.casefold() in SUPPORTED_SUFFIXES
            if is_theme:
                theme_roots.add(resolved)
            if (is_theme or is_media) and resolved not in excluded and resolved not in seen:
                seen.add(resolved)
                result.append(resolved)
                if len(result) >= max(1, min(2500, int(limit))):
                    return tuple(result)
    for path in state.files:
        if path not in excluded and path not in seen:
            seen.add(path)
            result.append(path)
            if len(result) >= max(1, min(2500, int(limit))):
                break
    return tuple(result)
