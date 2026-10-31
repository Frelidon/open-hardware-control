#!/usr/bin/env python3
"""Structural and digest checks for the standard-library RPM fallback writer."""

from __future__ import annotations

import gzip
import hashlib
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_rpm_fallback import _package_entries, build_noarch_rpm  # noqa: E402


def header(data: bytes, offset: int) -> tuple[int, dict[int, tuple[int, int, int]], int]:
    assert data[offset:offset + 8] == b"\x8e\xad\xe8\x01\0\0\0\0"
    count, store_size = struct.unpack(">II", data[offset + 8:offset + 16])
    store = offset + 16 + count * 16
    result: dict[int, tuple[int, int, int]] = {}
    for index in range(count):
        tag, value_type, relative, values = struct.unpack(
            ">IIII",
            data[offset + 16 + index * 16:offset + 32 + index * 16],
        )
        result[tag] = (value_type, store + relative, values)
    return store + store_size, result, store


def strings(data: bytes, record: tuple[int, int, int]) -> list[str]:
    _value_type, position, count = record
    values: list[str] = []
    for _ in range(count):
        end = data.index(0, position)
        values.append(data[position:end].decode("utf-8"))
        position = end + 1
    return values


def integer(data: bytes, record: tuple[int, int, int]) -> int:
    _value_type, position, _count = record
    return struct.unpack(">I", data[position:position + 4])[0]


def cpio_files(payload: bytes) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    position = 0
    while position + 110 <= len(payload):
        header_data = payload[position:position + 110]
        assert header_data[:6] == b"070701"
        fields = [int(header_data[6 + index * 8:14 + index * 8], 16) for index in range(13)]
        size = fields[6]
        name_size = fields[11]
        name = payload[position + 110:position + 110 + name_size - 1].decode("utf-8")
        position = (position + 110 + name_size + 3) & ~3
        content = payload[position:position + size]
        position = (position + size + 3) & ~3
        if name == "TRAILER!!!":
            break
        files[name] = content
    return files


def cpio_metadata(payload: bytes) -> dict[str, tuple[int, int, int]]:
    """Actual newc mode, UID and GID, not the RPM writer's model values."""
    entries = {}
    position = 0
    while position + 110 <= len(payload):
        header_data = payload[position:position + 110]
        assert header_data[:6] == b"070701"
        fields = [int(header_data[6 + index * 8:14 + index * 8], 16) for index in range(13)]
        name_size, size = fields[11], fields[6]
        name = payload[position + 110:position + 110 + name_size - 1].decode("utf-8")
        position = ((position + 110 + name_size + 3) & ~3)
        position = ((position + size + 3) & ~3)
        if name == "TRAILER!!!":
            break
        entries[name] = (fields[1] & 0o777, fields[2], fields[3])
    return entries


with tempfile.TemporaryDirectory(prefix="ohc-rpm-writer-test-") as temporary:
    base = Path(temporary)
    package = base / "root"
    app = package / "usr/share/open-hardware-control"
    app.mkdir(parents=True)
    (app / "VERSION").write_text("3.1.0\n", encoding="utf-8")
    bin_dir = package / "usr/bin"
    bin_dir.mkdir(parents=True)
    launcher = bin_dir / "open-hardware-control"
    launcher.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    launcher.chmod(0o755)
    desktop_shell = bin_dir / "open-hardware-control-desktop-shell"
    desktop_shell.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    desktop_shell.chmod(0o755)
    metainfo = package / "usr/share/metainfo/io.github.Frelidon.OpenHardwareControl.metainfo.xml"
    metainfo.parent.mkdir(parents=True)
    metainfo.write_text("<component type=\"desktop-application\"><id>io.github.Frelidon.OpenHardwareControl</id></component>\n", encoding="utf-8")
    fixed_files = {
        "/usr/libexec/open-hardware-control-dmi-memory-helper": (0o755, b"#!/usr/bin/python3 -I\n"),
        "/usr/libexec/open-hardware-control-snapshot-helper": (0o755, b"#!/usr/bin/python3\n# snapshot\n"),
        "/usr/libexec/open-hardware-control-snapshot-admin-helper": (0o755, b"#!/usr/bin/python3\n# snapshot admin\n"),
        "/usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.dmi.policy": (0o644, b"<policyconfig/>\n"),
        "/usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.snapshot.policy": (0o644, b"<policyconfig/>\n"),
    }
    # A partial/fake stage must keep absent optional helpers absent.
    assert not set(fixed_files).intersection(entry.package_path for entry in _package_entries(package, 1))
    for relative, (mode, content) in fixed_files.items():
        target = package / relative.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        target.chmod(mode)
    output = base / "test.rpm"
    build_noarch_rpm(package, output, version="3.1.0", release="0.intern1", channel="INTERN")
    data = output.read_bytes()

    assert data[:4] == b"\xed\xab\xee\xdb"
    signature_end, signature, _signature_store = header(data, 96)
    main_offset = (signature_end + 7) & ~7
    main_end, main, _main_store = header(data, main_offset)
    payload = data[main_end:]
    raw_payload = gzip.decompress(payload)

    assert strings(data, main[1000]) == ["open-hardware-control"]
    assert strings(data, main[1001]) == ["3.1.0"]
    assert strings(data, main[1002]) == ["0.intern1"]
    assert strings(data, main[5092]) == [hashlib.sha256(payload).hexdigest()]
    assert strings(data, main[5097]) == [hashlib.sha256(raw_payload).hexdigest()]
    assert integer(data, signature[1000]) == len(data) - main_offset
    assert integer(data, signature[1007]) == len(raw_payload)
    _type, md5_position, md5_count = signature[1004]
    assert md5_count == 16
    assert data[md5_position:md5_position + 16] == hashlib.md5(data[main_offset:]).digest()
    assert strings(data, signature[269]) == [hashlib.sha1(data[main_offset:main_end]).hexdigest()]
    assert strings(data, signature[273]) == [hashlib.sha256(data[main_offset:main_end]).hexdigest()]

    files = cpio_files(raw_payload)
    assert files["./usr/share/open-hardware-control/VERSION"] == b"3.1.0\n"
    assert files["./usr/bin/open-hardware-control"].startswith(b"#!/usr/bin/env bash")
    assert files["./usr/bin/open-hardware-control-desktop-shell"].startswith(b"#!/usr/bin/env bash")
    assert "./usr/share/metainfo/io.github.Frelidon.OpenHardwareControl.metainfo.xml" in files
    metadata = cpio_metadata(raw_payload)
    _type, position, count = main[1116]
    directory_indexes = struct.unpack(">" + "I" * count, data[position:position + count * 4])
    basenames, directories = strings(data, main[1117]), strings(data, main[1118])
    paths = [directories[index] + name for index, name in zip(directory_indexes, basenames)]
    _type, position, count = main[1030]
    modes = struct.unpack(">" + "H" * count, data[position:position + count * 2])
    users, groups = strings(data, main[1039]), strings(data, main[1040])
    for path, (mode, content) in fixed_files.items():
        index = paths.index(path)
        assert modes[index] & 0o777 == mode
        assert users[index] == groups[index] == "root"
        assert files["." + path] == content
        assert metadata["." + path] == (mode, 0, 0)

print("Standard-library RPM structure, payload and digest checks passed.")
