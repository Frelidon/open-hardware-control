#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded, regenerable SSD cache shared by media-heavy OHC pages."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from typing import Iterable


DEFAULT_CACHE_MB = 2048
CACHE_BUDGETS_MB = (0, 512, 1024, 2048, 4096)
MAX_CATALOG_BYTES = 12 * 1024 * 1024
MAX_CATALOG_RECORDS = 3000


def cache_budget_mb(settings: object) -> int:
    """Return one supported cache budget without trusting arbitrary settings."""
    try:
        raw = int(settings.value("performance/ssd_cache_mb", DEFAULT_CACHE_MB))
    except (AttributeError, TypeError, ValueError):
        raw = DEFAULT_CACHE_MB
    return raw if raw in CACHE_BUDGETS_MB else DEFAULT_CACHE_MB


def cache_root() -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")).expanduser()
    return base / "open-hardware-control" / "performance-cache-v1"


def _safe_namespace(namespace: str) -> str:
    value = str(namespace).strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", value):
        raise ValueError("invalid cache namespace")
    return value


def _source_signature(roots: Iterable[Path]) -> str:
    """Fingerprint roots and their direct children without a recursive rescan."""
    digest = hashlib.sha256()
    for raw_root in roots:
        root = raw_root.expanduser().resolve()
        digest.update(str(root).encode("utf-8", "surrogateescape"))
        try:
            stat = root.stat()
            digest.update(f":{stat.st_mtime_ns}:{stat.st_size}".encode())
            children = sorted(root.iterdir(), key=lambda item: item.name.casefold())[:4096]
        except OSError:
            digest.update(b":missing")
            continue
        for child in children:
            try:
                child_stat = child.stat(follow_symlinks=False)
            except OSError:
                continue
            digest.update(
                f"\0{child.name}:{child_stat.st_mtime_ns}:{child_stat.st_size}:{child_stat.st_mode}".encode(
                    "utf-8", "surrogateescape"
                )
            )
    return digest.hexdigest()


def _catalog_path(namespace: str) -> Path:
    return cache_root() / "catalogs" / f"{_safe_namespace(namespace)}.json"


def cached_catalog_records(
    namespace: str, roots: Iterable[Path], budget_mb: int, *, force: bool = False,
) -> list[dict[str, object]] | None:
    """Read a matching bounded catalog; return ``None`` for a safe rescan."""
    if budget_mb <= 0 or force:
        return None
    path = _catalog_path(namespace)
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_CATALOG_BYTES:
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != 1 or payload.get("signature") != _source_signature(roots):
            return None
        records = payload.get("records")
        if not isinstance(records, list) or len(records) > MAX_CATALOG_RECORDS:
            return None
        clean = [record for record in records if isinstance(record, dict)]
        if len(clean) != len(records):
            return None
        os.utime(path, None, follow_symlinks=False)
        return clean
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None


def save_catalog_records(
    namespace: str, roots: Iterable[Path], records: list[dict[str, object]], budget_mb: int,
) -> None:
    """Atomically persist small metadata only when the cache is enabled."""
    if budget_mb <= 0 or len(records) > MAX_CATALOG_RECORDS:
        return
    path = _catalog_path(namespace)
    payload = {"schema": 1, "signature": _source_signature(roots), "records": records}
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > MAX_CATALOG_BYTES:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(encoded)
        temporary.chmod(0o600)
        temporary.replace(path)
    except OSError:
        return


def preview_cache_path(namespace: str, source: Path, budget_mb: int, suffix: str = ".jpg") -> Path | None:
    """Return a content-versioned path for a regenerable scaled preview."""
    if budget_mb <= 0 or not re.fullmatch(r"\.[a-z0-9]{1,8}", suffix.lower()):
        return None
    try:
        resolved = source.expanduser().resolve(strict=True)
        stat = resolved.stat()
    except OSError:
        return None
    fingerprint = hashlib.sha256(
        f"{resolved}:{stat.st_size}:{stat.st_mtime_ns}".encode("utf-8", "surrogateescape")
    ).hexdigest()[:28]
    directory = cache_root() / "previews" / _safe_namespace(namespace)
    try:
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    except OSError:
        return None
    return directory / f"{fingerprint}{suffix.lower()}"
