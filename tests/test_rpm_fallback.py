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
from build_rpm_fallback import build_noarch_rpm  # noqa: E402


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

print("Standard-library RPM structure, payload and digest checks passed.")
