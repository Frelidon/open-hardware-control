#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small standard-library RPM writer used when rpmbuild is unavailable.

The generated package is an unsigned RPM v3 container with a SHA-256 file
digest table, compressed/uncompressed payload digests and the usual RPM header
and payload signature digests.  It intentionally supports only the noarch,
gzip/newc package shape used by Open Hardware Control.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import os
import stat
import struct
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


RPM_INT16 = 3
RPM_INT32 = 4
RPM_STRING = 6
RPM_BIN = 7
RPM_STRING_ARRAY = 8
RPM_I18NSTRING = 9
RPM_HEADER_MAGIC = b"\x8e\xad\xe8\x01\x00\x00\x00\x00"
RPM_LEAD_MAGIC = b"\xed\xab\xee\xdb"


@dataclass(frozen=True)
class PayloadEntry:
    package_path: str
    source: Path
    mode: int
    size: int
    mtime: int
    digest: str
    inode: int


def _encoded_value(value_type: int, value: object) -> tuple[bytes, int]:
    if value_type in {RPM_STRING, RPM_I18NSTRING}:
        return str(value).encode("utf-8") + b"\0", 1
    if value_type == RPM_STRING_ARRAY:
        values = list(value)  # type: ignore[arg-type]
        return b"".join(str(item).encode("utf-8") + b"\0" for item in values), len(values)
    if value_type == RPM_INT16:
        values = [int(item) & 0xFFFF for item in value]  # type: ignore[arg-type]
        return struct.pack(">" + "H" * len(values), *values), len(values)
    if value_type == RPM_INT32:
        values = [int(item) & 0xFFFFFFFF for item in value]  # type: ignore[arg-type]
        return struct.pack(">" + "I" * len(values), *values), len(values)
    if value_type == RPM_BIN:
        data = bytes(value)  # type: ignore[arg-type]
        return data, len(data)
    raise ValueError(f"Unsupported RPM data type: {value_type}")


def _alignment(value_type: int) -> int:
    return 4 if value_type == RPM_INT32 else 2 if value_type == RPM_INT16 else 1


def build_header(tags: dict[int, tuple[int, object]], region_tag: int) -> bytes:
    store = bytearray()
    encoded: list[tuple[int, int, int, int]] = []
    for tag in sorted(tags):
        value_type, value = tags[tag]
        alignment = _alignment(value_type)
        store.extend(b"\0" * ((-len(store)) % alignment))
        offset = len(store)
        data, count = _encoded_value(value_type, value)
        store.extend(data)
        encoded.append((tag, value_type, offset, count))

    region_offset = len(store)
    entry_count = len(encoded) + 1
    store.extend(struct.pack(">IIiI", region_tag, RPM_BIN, -16 * entry_count, 16))
    indices = [(region_tag, RPM_BIN, region_offset, 16), *encoded]
    index_data = b"".join(struct.pack(">IIII", *entry) for entry in indices)
    return RPM_HEADER_MAGIC + struct.pack(">II", entry_count, len(store)) + index_data + bytes(store)


def _package_entries(package_root: Path, epoch: int) -> list[PayloadEntry]:
    explicit = (
        "usr/bin/kraken-control",
        "usr/bin/open-hardware-control",
        "usr/bin/open-hardware-control-desktop-shell",
        "usr/bin/open-hardware-control-diagnostics",
        "usr/lib/udev/rules.d/71-nzxt-kraken-2023.rules",
        "usr/libexec/open-hardware-control-fan-helper",
        "usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.fan.policy",
        "usr/share/applications/open-hardware-control.desktop",
        "usr/share/icons/hicolor/scalable/apps/open-hardware-control.svg",
        "usr/share/metainfo/io.github.Frelidon.OpenHardwareControl.metainfo.xml",
    )
    candidates: list[Path] = []
    for relative in explicit:
        path = package_root / relative
        if path.exists():
            candidates.append(path)
    app_root = package_root / "usr/share/open-hardware-control"
    if not app_root.is_dir():
        raise ValueError("RPM payload is missing usr/share/open-hardware-control")
    candidates.append(app_root)
    candidates.extend(sorted(app_root.rglob("*"), key=lambda item: item.as_posix()))
    candidates = sorted(set(candidates), key=lambda item: item.relative_to(package_root).as_posix())

    entries: list[PayloadEntry] = []
    for inode, path in enumerate(candidates, start=1):
        relative = "/" + path.relative_to(package_root).as_posix()
        file_stat = path.stat()
        if path.is_dir():
            mode = stat.S_IFDIR | 0o755
            size = 0
            digest = ""
        elif path.is_file():
            mode = stat.S_IFREG | stat.S_IMODE(file_stat.st_mode)
            size = file_stat.st_size
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            raise ValueError(f"Unsupported RPM payload entry: {relative}")
        entries.append(PayloadEntry(relative, path, mode, size, epoch, digest, inode))
    return entries


def _newc_field(value: int) -> bytes:
    return f"{value & 0xFFFFFFFF:08x}".encode("ascii")


def _append_newc_entry(output: bytearray, name: str, mode: int, mtime: int, data: bytes, inode: int) -> None:
    encoded_name = name.encode("utf-8") + b"\0"
    fields = (
        inode,
        mode,
        0,
        0,
        2 if stat.S_ISDIR(mode) else 1,
        mtime,
        len(data),
        0,
        1,
        0,
        0,
        len(encoded_name),
        0,
    )
    output.extend(b"070701" + b"".join(_newc_field(value) for value in fields))
    output.extend(encoded_name)
    output.extend(b"\0" * ((-len(output)) % 4))
    output.extend(data)
    output.extend(b"\0" * ((-len(output)) % 4))


def build_cpio(entries: list[PayloadEntry], epoch: int) -> bytes:
    output = bytearray()
    for entry in entries:
        data = entry.source.read_bytes() if stat.S_ISREG(entry.mode) else b""
        _append_newc_entry(output, "." + entry.package_path, entry.mode, entry.mtime, data, entry.inode)
    _append_newc_entry(output, "TRAILER!!!", 0, epoch, b"", len(entries) + 1)
    return bytes(output)


def _split_paths(entries: list[PayloadEntry]) -> tuple[list[int], list[str], list[str]]:
    directories: list[str] = []
    directory_indexes: list[int] = []
    basenames: list[str] = []
    for entry in entries:
        pure = PurePosixPath(entry.package_path)
        directory = pure.parent.as_posix().rstrip("/") + "/"
        if directory not in directories:
            directories.append(directory)
        directory_indexes.append(directories.index(directory))
        basenames.append(pure.name)
    return directory_indexes, basenames, directories


def _lead(name: str) -> bytes:
    encoded_name = name.encode("ascii", errors="replace")[:65]
    encoded_name += b"\0" * (66 - len(encoded_name))
    return struct.pack(">4sBBHH66sHH16s", RPM_LEAD_MAGIC, 3, 0, 0, 1, encoded_name, 1, 5, b"\0" * 16)


def build_noarch_rpm(
    package_root: Path,
    output: Path,
    *,
    version: str,
    release: str,
    channel: str,
) -> Path:
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "1786838400"))
    entries = _package_entries(package_root, epoch)
    raw_payload = build_cpio(entries, epoch)
    compressed_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed_buffer, mode="wb", compresslevel=9, mtime=0) as archive:
        archive.write(raw_payload)
    payload = compressed_buffer.getvalue()
    directory_indexes, basenames, directories = _split_paths(entries)
    file_count = len(entries)
    installed_size = sum(entry.size for entry in entries)
    requires = [
        "/usr/bin/env",
        "liquidctl",
        "polkit",
        "python3",
        "python3-pillow",
        "python3-pyside6",
        "qt6-qtsvg",
        "rpmlib(CompressedFileNames)",
        "rpmlib(FileDigests)",
        "rpmlib(PayloadFilesHavePrefix)",
    ]
    provide_version = f"{version}-{release}"
    main_tags: dict[int, tuple[int, object]] = {
        100: (RPM_STRING_ARRAY, ["C"]),
        1000: (RPM_STRING, "open-hardware-control"),
        1001: (RPM_STRING, version),
        1002: (RPM_STRING, release),
        1004: (RPM_I18NSTRING, "NZXT Kraken, Corsair/OpenLinkHub and RGB Studio for Linux"),
        1005: (RPM_I18NSTRING, "Open-source Linux GUI for Kraken LCD, pump, fan and RGB control, Corsair devices through OpenLinkHub and optional local OpenRGB SDK devices."),
        1006: (RPM_INT32, [epoch]),
        1007: (RPM_STRING, "open-hardware-control-internal-builder"),
        1009: (RPM_INT32, [installed_size]),
        1014: (RPM_STRING, "GPL-3.0-or-later"),
        1016: (RPM_I18NSTRING, "Unspecified"),
        1020: (RPM_STRING, "https://github.com/Frelidon/open-hardware-control"),
        1021: (RPM_STRING, "linux"),
        1022: (RPM_STRING, "noarch"),
        1028: (RPM_INT32, [entry.size for entry in entries]),
        1030: (RPM_INT16, [entry.mode for entry in entries]),
        1033: (RPM_INT16, [0] * file_count),
        1034: (RPM_INT32, [entry.mtime for entry in entries]),
        1035: (RPM_STRING_ARRAY, [entry.digest for entry in entries]),
        1036: (RPM_STRING_ARRAY, [""] * file_count),
        1037: (RPM_INT32, [0] * file_count),
        1039: (RPM_STRING_ARRAY, ["root"] * file_count),
        1040: (RPM_STRING_ARRAY, ["root"] * file_count),
        1044: (RPM_STRING, f"open-hardware-control-{version}-{release}.src.rpm"),
        1045: (RPM_INT32, [0xFFFFFFFF] * file_count),
        1047: (RPM_STRING_ARRAY, ["application()", "application(open-hardware-control.desktop)", "open-hardware-control"]),
        1048: (RPM_INT32, [16384, 0, 0, 0, 0, 0, 0, 16777226, 16777226, 16777226]),
        1049: (RPM_STRING_ARRAY, requires),
        1050: (RPM_STRING_ARRAY, ["", "", "", "", "", "", "", "3.0.4-1", "4.6.0-1", "4.0-1"]),
        1064: (RPM_STRING, "4.18.2"),
        1080: (RPM_INT32, [epoch]),
        1081: (RPM_STRING_ARRAY, [f"Frelidon <noreply@github.com> - {version}-{release}"]),
        1082: (RPM_STRING_ARRAY, [f"- Open Hardware Control {version} {channel}"]),
        1095: (RPM_INT32, [1] * file_count),
        1096: (RPM_INT32, [entry.inode for entry in entries]),
        1097: (RPM_STRING_ARRAY, [""] * file_count),
        1112: (RPM_INT32, [32768, 32768, 8]),
        1113: (RPM_STRING_ARRAY, ["", "", provide_version]),
        1116: (RPM_INT32, directory_indexes),
        1117: (RPM_STRING_ARRAY, basenames),
        1118: (RPM_STRING_ARRAY, directories),
        1122: (RPM_STRING, "-O2"),
        1124: (RPM_STRING, "cpio"),
        1125: (RPM_STRING, "gzip"),
        1126: (RPM_STRING, "9"),
        1132: (RPM_STRING, "noarch-linux"),
        1140: (RPM_INT32, [0] * file_count),
        5011: (RPM_INT32, [8]),
        5062: (RPM_STRING, "utf-8"),
        5092: (RPM_STRING_ARRAY, [hashlib.sha256(payload).hexdigest()]),
        5093: (RPM_INT32, [8]),
        5097: (RPM_STRING_ARRAY, [hashlib.sha256(raw_payload).hexdigest()]),
    }
    main_header = build_header(main_tags, 63)
    signed_part = main_header + payload
    signature_tags: dict[int, tuple[int, object]] = {
        269: (RPM_STRING, hashlib.sha1(main_header).hexdigest()),
        273: (RPM_STRING, hashlib.sha256(main_header).hexdigest()),
        1000: (RPM_INT32, [len(signed_part)]),
        1004: (RPM_BIN, hashlib.md5(signed_part).digest()),
        1007: (RPM_INT32, [len(raw_payload)]),
        1008: (RPM_BIN, b"\0" * 4128),
    }
    signature_header = build_header(signature_tags, 62)
    signature_padding = b"\0" * ((-(96 + len(signature_header))) % 8)
    package_name = f"open-hardware-control-{version}-{release}"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(_lead(package_name) + signature_header + signature_padding + signed_part)
    return output
