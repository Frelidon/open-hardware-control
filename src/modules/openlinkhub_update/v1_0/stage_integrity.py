# SPDX-License-Identifier: GPL-3.0-or-later
"""Detect damaged or stale prepared payloads before stopping the live backend."""
import hashlib
import json
from pathlib import Path

MANIFEST=".ohc-release-integrity.json"


def seal(stage: Path, digest: str) -> None:
    files={}
    for path in stage.rglob("*"):
        if path.is_symlink():raise ValueError("symlink in prepared OpenLinkHub payload")
        if path.is_file() and path.name!=MANIFEST:
            with path.open("rb") as stream:files[path.relative_to(stage).as_posix()]=hashlib.file_digest(stream,"sha256").hexdigest()
    (stage/MANIFEST).write_text(json.dumps({"archive_sha256":digest,"files":files},sort_keys=True),encoding="utf-8")


def verify(stage: Path, expected_digest: str | None=None) -> None:
    manifest=stage/MANIFEST
    if manifest.is_symlink() or manifest.stat().st_size>2_097_152:raise ValueError("unsafe OpenLinkHub integrity manifest")
    data=json.loads(manifest.read_text(encoding="utf-8"))
    if expected_digest is not None and data.get("archive_sha256")!=expected_digest:
        raise ValueError("prepared OpenLinkHub release identity changed")
    files=data.get("files")
    if not isinstance(files,dict) or not files or len(files)>10000:raise ValueError("invalid OpenLinkHub integrity manifest")
    actual=set()
    for path in stage.rglob("*"):
        if path.is_symlink():raise ValueError("symlink in prepared OpenLinkHub payload")
        if path.is_file() and path.name!=MANIFEST:
            relative=path.relative_to(stage).as_posix();actual.add(relative)
            with path.open("rb") as stream:digest=hashlib.file_digest(stream,"sha256").hexdigest()
            if files.get(relative)!=digest:raise ValueError("prepared OpenLinkHub payload changed")
    if actual!=set(files):raise ValueError("prepared OpenLinkHub payload is incomplete")
