# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded, local-only, atomic complete configuration ZIP packages."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tempfile
import zipfile
from .values import decode, relocate, strings

FORMAT = "ohc-complete-profile"
MAX_FILES = 8192
MAX_TOTAL = 4 * 1024 ** 3
MAX_FILE = 1024 ** 3
MAX_META = 8 * 1024 ** 2
ASSET_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg", ".mp4", ".webm",
                  ".mkv", ".mov", ".avi", ".zt", ".dc", ".json", ".ttf", ".otf"}


def json_bytes(value):
    data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    if len(data) > MAX_META: raise ValueError("BUNDLE_METADATA_SIZE")
    return data


def safe_name(name):
    if not isinstance(name, str): raise ValueError("BUNDLE_PATH")
    parts = PurePosixPath(name).parts
    if (not isinstance(name, str) or not parts or len(name) > 1024 or name.startswith("/") or "\\" in name
            or PurePosixPath(name).as_posix() != name
            or any(p in {".", ".."} for p in name.split("/"))
            or any(ord(c) < 32 or ord(c) == 127 for c in name)):
        raise ValueError("BUNDLE_PATH")
    return name


def strict_path(path):
    if not path.is_absolute() or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("BUNDLE_SOURCE_LINK")
    return path.resolve(strict=True)


def referenced_roots(snapshot, extra_roots=()):
    roots, missing = set(), set()
    for text in set(strings(snapshot)) | set(map(str, extra_roots)):
        if not isinstance(text, str) or not text.startswith("/"): continue
        p = Path(text)
        if p == Path.home() or len(p.parts) < 4 or p.parts[1] in {"sys", "proc", "dev", "etc", "usr", "bin", "var"}:
            continue  # No system data or recursive home/system backup.
        if p.name.casefold() in {"steam", ".steam", ".git"}: continue
        if not p.exists():
            if p.suffix.casefold() in ASSET_SUFFIXES: missing.add(text)
            continue
        if p.is_symlink() and p.is_file(): p = p.resolve(strict=True)
        p = strict_path(p)
        if p.parts[1] in {"sys", "proc", "dev", "etc", "usr", "bin", "var"}: raise ValueError("BUNDLE_SOURCE_BOUNDARY")
        if p.is_dir() or p.suffix.casefold() in ASSET_SUFFIXES: roots.add(p)
    # Keep parent themes/media roots together; no duplicate copies of files.
    roots = sorted(roots, key=lambda p: (len(p.parts), str(p)))
    result = []
    for p in roots:
        if not any(p.is_relative_to(r) for r in result if r.is_dir()): result.append(p)
    return result, sorted(missing)[:512]


def source_files(root):
    if root.is_file():
        yield root
        return
    visited = 0
    for base, dirs, names in os.walk(root, followlinks=False):
        visited += len(dirs) + len(names)
        if visited > MAX_FILES * 4: raise ValueError("BUNDLE_SOURCE_COUNT")
        dirs[:] = sorted(d for d in dirs if d not in {".git", "__pycache__"})
        for name in sorted([*dirs, *names]):
            p = Path(base) / name
            if p.is_symlink() and p.is_dir(): raise ValueError("BUNDLE_SOURCE_LINK")
        for name in sorted(names):
            p = Path(base) / name
            if p.suffix.casefold() in ASSET_SUFFIXES:
                if not p.is_file(): raise ValueError("BUNDLE_SOURCE_TYPE")
                yield p


def export_bundle(destination, snapshot, extra_roots=()):
    destination = Path(destination)
    if destination.is_symlink(): raise ValueError("BUNDLE_DESTINATION_LINK")
    roots, missing = referenced_roots(snapshot, extra_roots)
    references, directories, files, planned, total = {}, [], [], [], 0
    for root in roots:
        prefix = "assets/" + hashlib.sha256(str(root).encode()).hexdigest()[:24]
        if root.is_dir():
            references[str(root)] = prefix
            directories.append(prefix)
        for p in source_files(root):
            if p == destination.resolve(): raise ValueError("BUNDLE_RECURSIVE_EXPORT")
            rel = p.relative_to(root).as_posix() if root.is_dir() else p.name
            name = safe_name(prefix + "/" + rel)
            actual = strict_path(p.resolve(strict=True))
            if actual.parts[1] in {"sys", "proc", "dev", "etc", "usr", "bin", "var"}: raise ValueError("BUNDLE_SOURCE_BOUNDARY")
            info = actual.stat()
            if info.st_size > MAX_FILE: raise ValueError("BUNDLE_FILE_SIZE")
            total += info.st_size
            if total > MAX_TOTAL or len(planned) >= MAX_FILES - 1: raise ValueError("BUNDLE_SIZE")
            references[str(p)] = name
            references.setdefault(str(actual), name)
            planned.append((actual, name, info))
    for original in strings(snapshot):
        if isinstance(original, str) and original.startswith("/"):
            p = Path(original)
            if p.is_dir() and not p.is_symlink():
                for root in roots:
                    if root.is_dir() and p.is_relative_to(root):
                        prefix = references[str(root)]
                        target = prefix if p == root else safe_name(prefix + "/" + p.relative_to(root).as_posix())
                        references[original] = target
                        if target not in directories: directories.append(target)
                        break
            if p.is_symlink() and p.is_file() and str(p.resolve()) in references:
                references[original] = references[str(p.resolve())]
    manifest = dict(format=FORMAT, schema=1, snapshot=snapshot, references=references,
                    files=files, directories=directories, missing=missing)
    # Validate metadata before touching the selected output file.
    json_bytes(manifest)
    fd, temporary = tempfile.mkstemp(prefix=".ohc-export-", suffix=".zip", dir=destination.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_STORED) as archive:
            for p, name, before in planned:
                digest, copied = hashlib.sha256(), 0
                source_fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW)
                with os.fdopen(source_fd, "rb") as source, archive.open(name, "w", force_zip64=True) as output:
                    opened = os.fstat(source.fileno())
                    if (opened.st_dev, opened.st_ino, opened.st_size) != (before.st_dev, before.st_ino, before.st_size):
                        raise ValueError("BUNDLE_SOURCE_CHANGED")
                    for chunk in iter(lambda: source.read(1024 ** 2), b""):
                        copied += len(chunk)
                        if copied > before.st_size: raise ValueError("BUNDLE_SOURCE_CHANGED")
                        digest.update(chunk); output.write(chunk)
                    after = os.fstat(source.fileno())
                    if copied != before.st_size or after.st_mtime_ns != before.st_mtime_ns:
                        raise ValueError("BUNDLE_SOURCE_CHANGED")
                files.append(dict(path=name, size=copied, sha256=digest.hexdigest()))
            archive.writestr("manifest.json", json_bytes(manifest))
        os.replace(temporary, destination)
    finally:
        if Path(temporary).exists(): Path(temporary).unlink()
    return dict(files=len(files), bytes=total, missing=missing)


def validate_manifest(value):
    if not isinstance(value, dict) or value.get("format") != FORMAT or value.get("schema") != 1:
        raise ValueError("BUNDLE_FORMAT")
    snapshot = value.get("snapshot")
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("settings"), dict) or len(snapshot["settings"]) > 8192:
        raise ValueError("BUNDLE_SETTINGS")
    if any(not isinstance(k, str) or not k or len(k) > 256 or any(ord(c) < 32 for c in k) for k in snapshot["settings"]):
        raise ValueError("BUNDLE_SETTINGS_KEY")
    for encoded in snapshot["settings"].values(): decode(encoded)
    if not isinstance(snapshot.get("profiles"), list) or len(snapshot["profiles"]) > 2048:
        raise ValueError("BUNDLE_PROFILES")
    if not all(isinstance(p, dict) and isinstance(p.get("payload"), dict) for p in snapshot["profiles"]):
        raise ValueError("BUNDLE_PROFILES")
    refs, records = value.get("references"), value.get("files")
    if not isinstance(refs, dict) or not isinstance(records, list) or len(records) > MAX_FILES - 1:
        raise ValueError("BUNDLE_FILES")
    directories = value.get("directories", [])
    if not isinstance(directories, list) or len(directories) > MAX_FILES:
        raise ValueError("BUNDLE_DIRECTORIES")
    for name in directories:
        if not isinstance(name, str) or not name.startswith("assets/"): raise ValueError("BUNDLE_DIRECTORIES")
        safe_name(name)
    names = set()
    for row in records:
        if (not isinstance(row, dict) or not isinstance(row.get("path"), str)
                or not row["path"].startswith("assets/") or type(row.get("size")) is not int
                or not 0 <= row["size"] <= MAX_FILE or not isinstance(row.get("sha256"), str)
                or len(row["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in row["sha256"])):
            raise ValueError("BUNDLE_FILE_RECORD")
        safe_name(row["path"])
        if PurePosixPath(row["path"]).suffix.casefold() not in ASSET_SUFFIXES:
            raise ValueError("BUNDLE_ASSET_TYPE")
        if row["path"] in names: raise ValueError("BUNDLE_DUPLICATE")
        names.add(row["path"])
    if len(set(directories)) != len(directories): raise ValueError("BUNDLE_DUPLICATE")
    for name in [*names, *directories]:
        if name in names and name in directories: raise ValueError("BUNDLE_PATH_CONFLICT")
        if any(parent.as_posix() in names for parent in PurePosixPath(name).parents):
            raise ValueError("BUNDLE_PATH_CONFLICT")
    for original, target in refs.items():
        if not isinstance(original, str) or not original.startswith("/") or not isinstance(target, str):
            raise ValueError("BUNDLE_REFERENCE")
        safe_name(target)
        if target not in names and target not in directories and not any(n.startswith(target + "/") for n in names):
            raise ValueError("BUNDLE_REFERENCE")
    return value


def import_bundle(source, stage):
    """Stage only into a new private directory; never extract into live settings."""
    stage = Path(stage)
    if stage.exists(): raise ValueError("BUNDLE_STAGE_EXISTS")
    strict_path(stage.parent)
    with zipfile.ZipFile(source) as archive:
        entries = archive.infolist()
        if len(entries) > MAX_FILES or sum(i.file_size for i in entries) > MAX_TOTAL + MAX_META:
            raise ValueError("BUNDLE_SIZE")
        names = set()
        for info in entries:
            safe_name(info.filename)
            kind = stat.S_IFMT(info.external_attr >> 16)
            if info.is_dir() or kind not in {0, stat.S_IFREG} or info.flag_bits & 1:
                raise ValueError("BUNDLE_MEMBER_TYPE")
            if info.filename in names: raise ValueError("BUNDLE_DUPLICATE")
            names.add(info.filename)
        info = archive.getinfo("manifest.json")
        if info.file_size > MAX_META: raise ValueError("BUNDLE_METADATA_SIZE")
        manifest = validate_manifest(json.loads(archive.read(info)))
        if names != {"manifest.json", *(r["path"] for r in manifest["files"])}:
            raise ValueError("BUNDLE_UNLISTED_FILE")
        for row in manifest["files"]:
            if archive.getinfo(row["path"]).file_size != row["size"]: raise ValueError("BUNDLE_FILE_SIZE")
        stage.mkdir(mode=0o700)
        try:
            for name in manifest.get("directories", []): (stage / name).mkdir(parents=True, exist_ok=True, mode=0o700)
            for row in manifest["files"]:
                dest = stage / row["path"]
                dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                digest, size = hashlib.sha256(), 0
                with archive.open(row["path"]) as inp, dest.open("xb") as out:
                    os.chmod(dest, 0o600)
                    for chunk in iter(lambda: inp.read(1024 ** 2), b""):
                        size += len(chunk)
                        if size > row["size"]: raise ValueError("BUNDLE_FILE_SIZE")
                        digest.update(chunk); out.write(chunk)
                if size != row["size"] or digest.hexdigest() != row["sha256"]:
                    raise ValueError("BUNDLE_CHECKSUM")
            mapping = {old: str(stage / new) for old, new in manifest["references"].items()}
            snapshot = relocate(manifest["snapshot"], mapping)
            # Local JSON themes/indexes may themselves contain absolute asset paths.
            for row in manifest["files"]:
                dest = stage / row["path"]
                if dest.suffix == ".json" and row["size"] <= MAX_META:
                    try:
                        raw = json.loads(dest.read_text(encoding="utf-8"))
                        updated = relocate(raw, mapping)
                        if updated != raw: dest.write_bytes(json_bytes(updated))
                    except (UnicodeDecodeError, json.JSONDecodeError): pass
            ready = json_bytes(snapshot)
            (stage / "ready.json").write_bytes(ready)
            return dict(stage=str(stage), sha256=hashlib.sha256(ready).hexdigest(), files=len(manifest["files"]))
        except Exception:
            # Only this exact new staging directory is ours, never user sources.
            import shutil
            shutil.rmtree(stage)
            raise
