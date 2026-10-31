#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validated, atomic iCUE NEXUS profile import for OpenLinkHub user installs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any


PROFILE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
IMAGE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".webp"})
MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_BUTTONS = 12


@dataclass(frozen=True, slots=True)
class NexusInstallResult:
    profile_id: str
    name: str
    root: Path
    backup: Path


def discover_openlinkhub_root(home: Path | None = None) -> Path | None:
    base = (home or Path.home()).expanduser().resolve()
    candidates = (base / "OpenLinkHub", base / ".local/share/OpenLinkHub")
    for candidate in candidates:
        if _valid_root(candidate, base):
            return candidate.resolve()
    return None


def _valid_root(root: Path, home: Path | None = None) -> bool:
    expanded = root.expanduser()
    if expanded.is_symlink():
        return False
    try:
        resolved = expanded.resolve(strict=True)
        owner = (home or Path.home()).expanduser().resolve(strict=True)
    except OSError:
        return False
    return (
        resolved != owner
        and resolved.is_relative_to(owner)
        and not resolved.is_symlink()
        and (resolved / "OpenLinkHub").is_file()
        and (resolved / "database/nexus/nexus.json").is_file()
        and not (resolved / "database").is_symlink()
        and not (resolved / "database/nexus").is_symlink()
    )


def _load_database(root: Path) -> tuple[Path, dict[str, Any]]:
    database = root / "database/nexus/nexus.json"
    if database.is_symlink() or database.stat().st_size > 1024 * 1024:
        raise ValueError("Die OpenLinkHub-Nexus-Datenbank ist nicht sicher lesbar.")
    payload = json.loads(database.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("profiles"), dict):
        raise ValueError("Die OpenLinkHub-Nexus-Datenbank hat ein unbekanntes Format.")
    return database, payload


def list_nexus_profiles(root: Path | None, *, home: Path | None = None) -> tuple[tuple[str, str], ...]:
    if root is None or not _valid_root(root, home):
        return ()
    try:
        _database, payload = _load_database(root)
    except (OSError, ValueError, json.JSONDecodeError):
        return ()
    result: list[tuple[str, str]] = []
    for profile_id, raw in list(payload["profiles"].items())[:128]:
        if not isinstance(profile_id, str) or not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or profile_id).replace("\n", " ").strip()[:80]
        result.append((profile_id, name or profile_id))
    return tuple(sorted(result, key=lambda item: item[1].casefold()))


def _color(value: object, field: str) -> dict[str, int]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} muss eine RGB-Farbe enthalten.")
    result: dict[str, int] = {}
    for component in ("red", "green", "blue"):
        raw = value.get(component)
        if isinstance(raw, bool) or not isinstance(raw, int) or not 0 <= raw <= 255:
            raise ValueError(f"{field}.{component} liegt außerhalb 0–255.")
        result[component] = raw
    return result


def _buttons(value: object) -> dict[str, dict[str, object]]:
    if value in (None, {}):
        return {}
    if not isinstance(value, dict) or len(value) > MAX_BUTTONS:
        raise ValueError("Ein Nexus-Design darf höchstens zwölf Schaltflächen enthalten.")
    result: dict[str, dict[str, object]] = {}
    touch_ranges: list[tuple[int, int]] = []
    for number, (_key, raw) in enumerate(value.items()):
        if not isinstance(raw, dict):
            raise ValueError("Ungültige Nexus-Schaltfläche.")
        def integer(name: str, minimum: int, maximum: int, default: int = 0) -> int:
            candidate = raw.get(name, default)
            if isinstance(candidate, bool) or not isinstance(candidate, int) or not minimum <= candidate <= maximum:
                raise ValueError(f"Ungültiger Nexus-Wert: {name}.")
            return candidate
        action = integer("actionCode", 1, 146)
        width = integer("width", 1, 640)
        height = integer("height", 1, 48)
        x = integer("offsetX", 0, 639)
        y = integer("offsetY", 0, 47)
        if x + width > 640 or y + height > 48:
            raise ValueError("Eine Nexus-Schaltfläche liegt außerhalb der 640×48-Anzeige.")
        touch_min = integer("touchPositionMin", 0, 639)
        # Upstream uses lower-case touchPositionMax and inclusive ranges.
        # Accept the older OHC manifest spelling, but never export it.
        if "touchPositionMax" not in raw and "TouchPositionMax" in raw:
            raw = dict(raw, touchPositionMax=raw["TouchPositionMax"])
        touch_max = min(639, integer("touchPositionMax", touch_min, 640))
        if any(touch_min <= old_max and old_min <= touch_max for old_min, old_max in touch_ranges):
            raise ValueError("Die Berührungsbereiche von Nexus-Schaltflächen dürfen sich nicht überschneiden.")
        touch_ranges.append((touch_min, touch_max))
        text = str(raw.get("text") or "").replace("\n", " ").strip()[:32]
        result[str(number)] = {
            "actionCode": action, "text": text, "textSize": integer("textSize", 8, 48, 18),
            "width": width, "height": height, "background": _color(raw.get("background", {"red": 20, "green": 20, "blue": 24}), "background"),
            "border": integer("border", 0, 8, 1), "borderColor": _color(raw.get("borderColor", {"red": 0, "green": 200, "blue": 255}), "borderColor"),
            "showIcon": False, "icon": "", "iconWidth": 0, "iconHeight": 0,
            "iconOffsetX": 0, "iconOffsetY": 0, "offsetX": x, "offsetY": y,
            "touchPositionMin": touch_min, "touchPositionMax": touch_max,
            "textColor": _color(raw.get("textColor", {"red": 255, "green": 255, "blue": 255}), "textColor"),
        }
    return result


def _manifest(source: Path) -> tuple[str, str, Path, dict[str, dict[str, object]]]:
    if source.suffix.casefold() in IMAGE_SUFFIXES:
        stem = re.sub(r"[^a-z0-9]+", "-", source.stem.casefold()).strip("-")[:32] or "design"
        return f"ohc-{stem}", source.stem[:80] or "OHC Nexus Design", source, {}
    if source.suffix.casefold() != ".json":
        raise ValueError("Bitte ein Bild oder ein .ohcnexus.json-Manifest auswählen.")
    if source.stat().st_size > 256 * 1024:
        raise ValueError("Das Nexus-Manifest ist zu groß.")
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError("Das Nexus-Manifest benötigt Schema 1.")
    ident = str(data.get("profile_id") or "")
    if not PROFILE_ID_RE.fullmatch(ident) or not ident.startswith("ohc-"):
        raise ValueError("Die Profilkennung muss mit ohc- beginnen und darf nur Kleinbuchstaben/Zahlen enthalten.")
    name = str(data.get("name") or "").replace("\n", " ").strip()[:80]
    background_name = str(data.get("background") or "")
    if not name or Path(background_name).name != background_name:
        raise ValueError("Name oder Hintergrund im Nexus-Manifest ist ungültig.")
    requested_background = source.parent / background_name
    if requested_background.is_symlink():
        raise ValueError("Der Nexus-Hintergrund darf kein symbolischer Link sein.")
    background = requested_background.resolve()
    if background.parent != source.parent.resolve() or background.suffix.casefold() not in IMAGE_SUFFIXES:
        raise ValueError("Der Nexus-Hintergrund muss neben dem Manifest liegen.")
    return ident, name, background, _buttons(data.get("buttons"))


def install_nexus_design(
    source: Path, root: Path | None = None, *, home: Path | None = None,
) -> NexusInstallResult:
    requested_source = source.expanduser()
    if requested_source.is_symlink():
        raise ValueError("Die Nexus-Designquelle darf kein symbolischer Link sein.")
    source = requested_source.resolve(strict=True)
    if not source.is_file() or source.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("Die Nexus-Designquelle ist ungültig oder zu groß.")
    install_root = (root or discover_openlinkhub_root())
    if install_root is None or not _valid_root(install_root, home):
        raise ValueError("Keine unterstützte OpenLinkHub-Benutzerinstallation gefunden.")
    install_root = install_root.resolve()
    profile_id, name, background, buttons = _manifest(source)
    if background.is_symlink() or not background.is_file() or background.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("Der Nexus-Hintergrund ist ungültig oder zu groß.")
    database, payload = _load_database(install_root)
    target = install_root / "database/nexus" / f"{profile_id}.jpg"
    if target.is_symlink():
        raise ValueError("Der Zielpfad des Nexus-Hintergrunds ist unsicher.")
    try:
        from PIL import Image
        with Image.open(background) as image:
            image.verify()
        with Image.open(background) as image:
            frame = image.convert("RGB")
            frame.thumbnail((640, 48), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (640, 48), (8, 12, 18))
            canvas.paste(frame, ((640 - frame.width) // 2, (48 - frame.height) // 2))
            with tempfile.NamedTemporaryFile(prefix="ohc-nexus-", suffix=".jpg", dir=target.parent, delete=False) as stream:
                temporary_image = Path(stream.name)
            canvas.save(temporary_image, format="JPEG", quality=94, optimize=True)
    except Exception as exc:
        raise ValueError(f"Der Nexus-Hintergrund konnte nicht sicher vorbereitet werden: {exc}") from exc
    profiles = payload["profiles"]
    profiles[profile_id] = {
        "name": name,
        "background": f"/database/nexus/{target.name}",
        "fontPath": "/static/fonts/teko.ttf",
        "textColor": {"red": 255, "green": 255, "blue": 255},
        "buttons": buttons,
        "keyboard": bool(buttons),
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # Unique O_EXCL-created files cannot follow a predictable temporary or
    # backup symlink and also preserve separate imports within one second.
    with tempfile.NamedTemporaryFile(prefix=f"nexus.json.ohc-backup-{stamp}-", dir=database.parent, delete=False) as stream:
        backup = Path(stream.name)
    shutil.copy2(database, backup)
    with tempfile.NamedTemporaryFile(prefix="nexus.json.ohc-tmp-", dir=database.parent, delete=False) as stream:
        temporary_database = Path(stream.name)
    old_image: Path | None = None
    if target.exists():
        with tempfile.NamedTemporaryFile(prefix=f"{profile_id}.ohc-backup-", suffix=".jpg", dir=target.parent, delete=False) as stream:
            old_image = Path(stream.name)
        shutil.copy2(target, old_image)
    try:
        temporary_database.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary_image.replace(target)
        temporary_database.replace(database)
    except Exception:
        temporary_database.unlink(missing_ok=True)
        temporary_image.unlink(missing_ok=True)
        # Database has not been replaced if its atomic replace failed.
        if old_image is not None:
            shutil.copy2(old_image, target)
        else:
            target.unlink(missing_ok=True)
        raise
    return NexusInstallResult(profile_id, name, install_root, backup)
