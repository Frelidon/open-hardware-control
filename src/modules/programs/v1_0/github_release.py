# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded GitHub release inspection and atomic asset/source download."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Callable
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


MAX_API_BYTES = 4 * 1024 * 1024
MAX_ASSETS = 100
MAX_FILE_BYTES = 1024 * 1024 * 1024
MAX_TOTAL_BYTES = 4 * 1024 * 1024 * 1024
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}$")
SAFE_NAME_RE = re.compile(r"^[^/\\\x00]{1,240}$")
DOWNLOAD_HOSTS = {
    "api.github.com", "github.com", "codeload.github.com",
    "objects.githubusercontent.com", "release-assets.githubusercontent.com",
}


class GitHubReleaseError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DownloadItem:
    name: str
    url: str
    size: int | None
    kind: str


@dataclass(frozen=True, slots=True)
class ReleasePlan:
    repository: str
    tag: str
    name: str
    published_at: str
    items: tuple[DownloadItem, ...]


def normalize_repository(raw: object) -> str:
    value = str(raw or "").strip()
    for prefix in ("https://github.com/", "http://github.com/"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    value = value.removesuffix(".git").strip("/")
    if REPOSITORY_RE.fullmatch(value) is None or ".." in value:
        raise GitHubReleaseError("Ungültiges GitHub-Projekt. Erwartet wird Besitzer/Repository.")
    return value


def _read_json(response: object) -> object:
    payload = response.read(MAX_API_BYTES + 1)
    if len(payload) > MAX_API_BYTES:
        raise GitHubReleaseError("Die GitHub-Antwort überschreitet die Sicherheitsgrenze.")
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise GitHubReleaseError("GitHub lieferte keine gültigen Release-Metadaten.") from exc


def parse_release(repository: str, payload: object) -> ReleasePlan:
    repository = normalize_repository(repository)
    if not isinstance(payload, dict) or payload.get("draft"):
        raise GitHubReleaseError("GitHub lieferte kein veröffentlichtes Release.")
    tag = str(payload.get("tag_name") or "").strip()[:120]
    if not tag or SAFE_NAME_RE.fullmatch(tag) is None or tag in {".", ".."}:
        raise GitHubReleaseError("Das Release besitzt keine sichere Versionskennung.")
    raw_assets = payload.get("assets")
    if not isinstance(raw_assets, list) or len(raw_assets) > MAX_ASSETS:
        raise GitHubReleaseError("Die Anzahl der Release-Dateien liegt außerhalb der Sicherheitsgrenze.")
    items: list[DownloadItem] = []
    total = 0
    prefix = f"https://github.com/{repository}/releases/download/"
    for raw in raw_assets:
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or "")
        url = str(raw.get("browser_download_url") or "")
        try:
            size = int(raw.get("size") or 0)
        except (TypeError, ValueError):
            size = 0
        if SAFE_NAME_RE.fullmatch(name) is None or name in {".", ".."}:
            raise GitHubReleaseError("Ein Release-Dateiname ist nicht sicher.")
        if not url.startswith(prefix) or not 1 <= size <= MAX_FILE_BYTES:
            raise GitHubReleaseError(f"Ungültige Downloadangaben für {name}.")
        total += size
        items.append(DownloadItem(name, url, size, "asset"))
    for field, filename, kind in (
        ("zipball_url", "source-code.zip", "source-zip"),
        ("tarball_url", "source-code.tar.gz", "source-tar"),
    ):
        url = str(payload.get(field) or "")
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != "api.github.com":
            raise GitHubReleaseError("Die Source-Code-Adresse stammt nicht von der GitHub-API.")
        items.append(DownloadItem(filename, url, None, kind))
    if total > MAX_TOTAL_BYTES:
        raise GitHubReleaseError("Die gemeldete Gesamtgröße überschreitet die Sicherheitsgrenze.")
    return ReleasePlan(repository, tag, str(payload.get("name") or tag)[:200],
                       str(payload.get("published_at") or "")[:40], tuple(items))


def inspect_release(repository: object, version: object = "", *, opener=urlopen) -> ReleasePlan:
    normalized = normalize_repository(repository)
    requested = str(version or "").strip()
    suffix = f"releases/tags/{quote(requested, safe='')}" if requested else "releases/latest"
    request = Request(
        f"https://api.github.com/repos/{normalized}/{suffix}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "Open-Hardware-Control"},
    )
    with opener(request, timeout=20) as response:
        return parse_release(normalized, _read_json(response))


def _safe_target(base: Path, repository: str, tag: str) -> Path:
    owner, project = repository.split("/", 1)
    target = base / owner / project / tag
    if any(part.is_symlink() for part in (base, base / owner, base / owner / project, target) if part.exists()):
        raise GitHubReleaseError("Der Zielpfad enthält eine symbolische Verknüpfung.")
    return target


def downloaded_appimages(plan: ReleasePlan, base_folder: Path) -> tuple[Path, ...]:
    """Return only downloaded AppImage assets from the inspected release.

    The release plan remains the authority for filenames and byte counts.  A
    profile may therefore select a file only after the atomic release folder
    exists and the exact regular, non-symlink asset still has GitHub's reported
    size.  Header validation remains part of the later installation plan.
    """

    base = Path(base_folder).expanduser()
    if not base.is_absolute():
        return ()
    destination = _safe_target(base, plan.repository, plan.tag)
    matches: list[Path] = []
    for item in plan.items:
        if item.kind != "asset" or not item.name.casefold().endswith(".appimage"):
            continue
        candidate = destination / item.name
        try:
            if candidate.is_symlink() or not candidate.is_file():
                continue
            if item.size is None or candidate.stat().st_size != item.size:
                continue
        except OSError:
            continue
        matches.append(candidate)
    return tuple(matches)


def _download(item: DownloadItem, target: Path, *, opener=urlopen,
              cancelled: Callable[[], bool] | None = None) -> tuple[int, str]:
    request = Request(item.url, headers={"Accept": "application/octet-stream", "User-Agent": "Open-Hardware-Control"})
    digest, written = hashlib.sha256(), 0
    with opener(request, timeout=90) as response, target.open("xb") as stream:
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.hostname not in DOWNLOAD_HOSTS:
            raise GitHubReleaseError("GitHub leitete eine Datei auf einen nicht erlaubten Server um.")
        while True:
            if cancelled is not None and cancelled():
                raise GitHubReleaseError("Download abgebrochen.")
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > MAX_FILE_BYTES:
                raise GitHubReleaseError(f"{item.name} überschreitet die Sicherheitsgrenze.")
            digest.update(chunk); stream.write(chunk)
    if item.size is not None and written != item.size:
        raise GitHubReleaseError(f"Die Größe von {item.name} stimmt nicht mit GitHub überein.")
    return written, digest.hexdigest()


def download_release(plan: ReleasePlan, base_folder: Path, *, opener=urlopen,
                     cancelled: Callable[[], bool] | None = None) -> Path:
    base = Path(base_folder).expanduser()
    if not base.is_absolute():
        raise GitHubReleaseError("Der Grundordner muss absolut sein.")
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    destination = _safe_target(base, plan.repository, plan.tag)
    if destination.exists():
        raise GitHubReleaseError("Der Versionsordner existiert bereits; vorhandene Dateien werden nicht überschrieben.")
    parent = destination.parent; parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{plan.tag}-partial-", dir=parent))
    records: list[dict[str, object]] = []
    try:
        total = 0
        for item in plan.items:
            size, digest = _download(item, stage / item.name, opener=opener, cancelled=cancelled)
            total += size
            if total > MAX_TOTAL_BYTES:
                raise GitHubReleaseError("Die heruntergeladene Gesamtgröße überschreitet die Sicherheitsgrenze.")
            records.append({"name": item.name, "kind": item.kind, "size": size, "sha256": digest})
        (stage / "SHA256SUMS").write_text("".join(f"{row['sha256']}  {row['name']}\n" for row in records), encoding="ascii")
        manifest = {"schema": 1, "repository": plan.repository, "tag": plan.tag,
                    "release_name": plan.name, "published_at": plan.published_at, "files": records}
        (stage / "release-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(stage, destination)
        return destination
    except Exception:
        for child in stage.iterdir():
            try: child.unlink()
            except OSError: pass
        try: stage.rmdir()
        except OSError: pass
        raise
