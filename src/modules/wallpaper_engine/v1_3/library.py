"""Read-only local Wallpaper Engine library discovery."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path

from modules.ui_performance.v1_1 import cached_catalog_records, save_catalog_records


WORKSHOP_APP_ID = "431960"
VIDEO_SUFFIXES = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v"}
PREVIEW_NAMES = ("preview.jpg", "preview.png", "preview.jpeg", "preview.gif", "preview.webp")
MAX_PROJECT_JSON_BYTES = 2 * 1024 * 1024
MAX_LIBRARY_ITEMS = 3000


def default_steam_library(
    platform: str | None = None,
    *,
    environ: dict[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    """Return the most plausible Steam root without modifying or probing Steam."""

    target = str(platform or os.sys.platform).casefold()
    values = os.environ if environ is None else environ
    user_home = Path.home() if home is None else Path(home)
    if target.startswith("win"):
        candidates = [
            Path(values[key]) / "Steam"
            for key in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA")
            if values.get(key)
        ]
        candidates.append(user_home / "AppData/Local/Steam")
        return next((candidate for candidate in candidates if candidate.is_dir()), candidates[0])
    return user_home / ".local/share/Steam"


@dataclass(frozen=True, slots=True)
class WallpaperEntry:
    ident: str
    title: str
    kind: str
    source_path: Path
    preview_path: Path | None
    project_path: Path | None = None
    tags: tuple[str, ...] = ()

    @property
    def packed_source(self) -> str:
        return f"{self.source_path}+{self.kind}"


def previous_workshop_entry(
    entries: list[WallpaperEntry], current_workshop_id: str
) -> WallpaperEntry | None:
    """Return the previous local entry because CaptSilver v1.4 has no back API."""

    if not entries:
        return None
    current_index = next(
        (index for index, entry in enumerate(entries) if entry.ident == current_workshop_id),
        0,
    )
    return entries[(current_index - 1) % len(entries)]


def workshop_root(steam_library: Path) -> Path:
    return steam_library.expanduser() / "steamapps" / "workshop" / "content" / WORKSHOP_APP_ID


def _safe_child(root: Path, raw_name: object) -> Path | None:
    name = str(raw_name or "").strip()
    if not name or Path(name).is_absolute():
        return None
    candidate = root / name
    try:
        candidate.resolve(strict=False).relative_to(root.resolve())
    except (OSError, ValueError):
        return None
    return candidate if candidate.is_file() and not candidate.is_symlink() else None


def _preview_path(root: Path, configured: object) -> Path | None:
    preview = _safe_child(root, configured)
    if preview is not None:
        return preview
    for name in PREVIEW_NAMES:
        candidate = root / name
        if candidate.is_file() and not candidate.is_symlink():
            return candidate
    return None


def _cached_child(root: Path, raw: object) -> Path | None:
    try:
        candidate = Path(str(raw)).resolve(strict=True)
        candidate.relative_to(root.resolve())
    except (OSError, ValueError):
        return None
    return candidate if candidate.is_file() and not candidate.is_symlink() else None


def scan_workshop_library(steam_library: Path, *, limit: int = MAX_LIBRARY_ITEMS) -> list[WallpaperEntry]:
    """Return validated Workshop projects without modifying Steam content."""

    root = workshop_root(steam_library)
    if not root.is_dir() or root.is_symlink():
        return []
    entries: list[WallpaperEntry] = []
    projects = sorted(
        (path for path in root.iterdir() if path.is_dir() and not path.is_symlink() and path.name.isdigit()),
        key=lambda path: int(path.name),
        reverse=True,
    )
    for project_dir in projects[: max(0, min(int(limit), MAX_LIBRARY_ITEMS))]:
        metadata_path = project_dir / "project.json"
        try:
            if metadata_path.is_symlink() or metadata_path.stat().st_size > MAX_PROJECT_JSON_BYTES:
                continue
            data = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        source = _safe_child(project_dir, data.get("file"))
        kind = str(data.get("type") or "").strip().lower()
        if source is None or kind not in {"scene", "video", "web", "application", "preset"}:
            continue
        raw_tags = data.get("tags", [])
        tags = tuple(str(tag) for tag in raw_tags[:32]) if isinstance(raw_tags, list) else ()
        entries.append(
            WallpaperEntry(
                ident=project_dir.name,
                title=str(data.get("title") or project_dir.name).strip()[:240],
                kind=kind,
                source_path=source,
                preview_path=_preview_path(project_dir, data.get("preview")),
                project_path=metadata_path,
                tags=tags,
            )
        )
    return entries


def cached_workshop_library(
    steam_library: Path, budget_mb: int, *, force: bool = False,
) -> list[WallpaperEntry]:
    """Use a persistent metadata catalog while keeping Steam content read-only."""
    root = workshop_root(steam_library)
    records = cached_catalog_records("wallpaper-workshop", (root,), budget_mb, force=force)
    if records is None:
        entries = scan_workshop_library(steam_library)
        save_catalog_records("wallpaper-workshop", (root,), [
            {
                "ident": item.ident, "title": item.title, "kind": item.kind,
                "source": str(item.source_path),
                "preview": str(item.preview_path) if item.preview_path else "",
                "project": str(item.project_path) if item.project_path else "",
                "tags": list(item.tags),
            }
            for item in entries
        ], budget_mb)
        return entries
    entries: list[WallpaperEntry] = []
    for record in records:
        try:
            source = Path(str(record["source"])).resolve()
            source.relative_to(root.resolve())
            if not source.is_file():
                continue
            preview = _cached_child(root, record.get("preview")) if record.get("preview") else None
            project = _cached_child(root, record.get("project")) if record.get("project") else None
            kind = str(record["kind"])
            if kind not in {"scene", "video", "web", "application", "preset"}:
                continue
            tags = record.get("tags", [])
            entries.append(WallpaperEntry(
                str(record["ident"])[:80], str(record["title"])[:240], kind, source,
                preview, project,
                tuple(str(tag)[:80] for tag in tags[:32]) if isinstance(tags, list) else (),
            ))
        except (KeyError, OSError, ValueError):
            continue
    return entries


def scan_video_folder(folder: Path, *, limit: int = MAX_LIBRARY_ITEMS) -> list[WallpaperEntry]:
    """Return ordinary videos from one explicitly selected local folder."""

    root = folder.expanduser()
    if not root.is_dir() or root.is_symlink():
        return []
    entries: list[WallpaperEntry] = []
    maximum = max(0, min(int(limit), MAX_LIBRARY_ITEMS))
    resolved_root = root.resolve()
    for current, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = sorted(
            name for name in directories if not (Path(current) / name).is_symlink()
        )
        for name in sorted(filenames, key=str.casefold):
            if len(entries) >= maximum:
                return entries
            path = Path(current) / name
            try:
                if path.is_symlink() or path.suffix.lower() not in VIDEO_SUFFIXES:
                    continue
                resolved = path.resolve()
                resolved.relative_to(resolved_root)
            except (OSError, ValueError):
                continue
            entries.append(
                WallpaperEntry(
                    ident=f"video:{_fnv1a_16(str(resolved))}",
                    title=path.stem[:240],
                    kind="video",
                    source_path=resolved,
                    preview_path=None,
                )
            )
    return entries


def _fnv1a_16(value: str) -> str:
    """Match the plugin's stable local-video identifier."""

    result = 0x811C9DC5
    for byte in value.encode("utf-8"):
        result ^= byte
        result = (result * 0x01000193) & 0xFFFFFFFF
    return f"{result:016x}"


def is_unsafe_video_folder(folder: Path, steam_library: Path) -> bool:
    """Reject the old failure mode: recursively scanning a Steam library."""

    try:
        selected = folder.expanduser().resolve()
        steam = steam_library.expanduser().resolve()
    except OSError:
        return True
    if selected in {Path("/"), Path.home().resolve()}:
        return True
    if selected == steam or steam in selected.parents:
        return True
    return (selected / "steamapps").is_dir()
