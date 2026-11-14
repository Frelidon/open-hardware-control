"""LCD cache metadata checks stay bounded and require actual H.264 geometry."""
from dataclasses import replace
import io
from pathlib import Path
import shutil
import struct
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from modules.design_hub.v1_1.catalog import PAIRS, pair_media
from modules.design_hub.v1_1.mp4_metadata import MAX_METADATA_BYTES, valid_lcd_mp4
from modules.design_hub.v1_1.scaling import valid_output, zoom_plan


def box(tag, payload=b'', *, extended=False):
    return (struct.pack('>I4sQ', 1, tag, len(payload) + 16) if extended else
            struct.pack('>I4s', len(payload) + 8, tag)) + payload


def metadata_fixture(*, width=1600, height=720, sample_width=None, codec=b'avc1',
                     duration=1000, handler=b'vide', extended=False):
    """Structural fixture only: real encoded video is exercised separately."""
    tkhd = bytearray(84)
    struct.pack_into('>II', tkhd, 76, width << 16, height << 16)
    mdhd = bytearray(24)
    struct.pack_into('>II', mdhd, 12, 1000, duration)
    hdlr = bytes(8) + handler + bytes(12)
    visual = bytearray(78)
    struct.pack_into('>HH', visual, 24, sample_width or width, height)
    avcc = bytes.fromhex('0164001fffe1000267780100026878')
    sample = box(codec, bytes(visual) + box(b'avcC', avcc, extended=extended), extended=extended)
    stsd = box(b'stsd', bytes(4) + struct.pack('>I', 1) + sample)
    media = box(b'mdia', box(b'mdhd', bytes(mdhd)) + box(b'hdlr', hdlr) +
                box(b'minf', box(b'stbl', stsd)))
    movie = box(b'moov', box(b'trak', box(b'tkhd', bytes(tkhd)) + media), extended=extended)
    return box(b'ftyp', b'isom' + bytes(4) + b'isomavc1') + movie + box(b'mdat', bytes(4096))


def checked(data):
    return valid_lcd_mp4(io.BytesIO(data), len(data), 1600, 720)


def test_fake_ftyp_and_invalid_geometry_never_become_reusable_cache(tmp_path):
    plan = zoom_plan(pair_media(PAIRS[0]), tmp_path, 150)
    plan.target.write_bytes(b'\0\0\0\x18ftypisom' + bytes(5000))
    assert not valid_output(plan)
    for options in ({'width': 320, 'height': 180}, {'sample_width': 1599},
                    {'codec': b'mp4v'}, {'handler': b'soun'}, {'duration': 35001}):
        plan.target.write_bytes(metadata_fixture(**options))
        assert not valid_output(plan), options
    plan.target.write_bytes(metadata_fixture())
    assert valid_output(plan)
    alias = tmp_path / 'alias.mp4'; alias.symlink_to(plan.target)
    assert not valid_output(replace(plan, target=alias))


def test_metadata_atom_lengths_are_strict_for_32_and_64_bit_boxes():
    assert checked(metadata_fixture())
    assert checked(metadata_fixture(extended=True))
    for tail in (struct.pack('>I4s', 7, b'free'),
                 struct.pack('>I4s', 0, b'free'),
                 struct.pack('>I4s', 4096, b'free'),
                 struct.pack('>I4sQ', 1, b'free', 15),
                 struct.pack('>I4sQ', 1, b'free', 2**64 - 1), b'partial'):
        assert not checked(metadata_fixture() + tail)
    # A child must remain inside its declared parent even if more bytes follow.
    data = metadata_fixture()
    index = data.index(b'tkhd') - 4
    malformed = data[:index] + struct.pack('>I', 4096) + data[index + 4:]
    assert not checked(malformed)


def test_metadata_byte_atom_and_depth_budgets_do_not_read_video_payload():
    data = metadata_fixture()
    class CountedStream(io.BytesIO):
        def __init__(self, value): super().__init__(value); self.total_read = 0
        def read(self, count=-1):
            result = super().read(count); self.total_read += len(result); return result
    stream = CountedStream(data)
    assert valid_lcd_mp4(stream, len(data), 1600, 720)
    assert stream.total_read < 1024  # mdat is skipped, never decoded on this path.
    oversize = box(b'ftyp', b'isom' + bytes(4)) + box(b'moov', bytes(MAX_METADATA_BYTES + 1))
    stream = CountedStream(oversize)
    assert not valid_lcd_mp4(stream, len(oversize), 1600, 720)
    assert stream.total_read <= MAX_METADATA_BYTES
    assert not checked(data + box(b'free') * 513)
    nested = box(b'free')
    for _index in range(9): nested = box(b'moov', nested)
    assert not checked(box(b'ftyp', b'isom' + bytes(4)) + nested + box(b'mdat', b'video'))


@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='local encoder unavailable')
def test_real_h264_with_wrong_resolution_is_rejected(tmp_path):
    plan = zoom_plan(pair_media(PAIRS[0]), tmp_path, 150)
    subprocess.run([shutil.which('ffmpeg'), '-v', 'error', '-nostdin', '-n', '-f', 'lavfi',
                    '-i', 'testsrc2=size=320x180:rate=12:duration=0.5', '-an', '-c:v',
                    'libx264', '-threads', '2', '-pix_fmt', 'yuv420p', '-movflags',
                    '+faststart', str(plan.target)], check=True, capture_output=True, timeout=15)
    assert plan.target.stat().st_size >= 4096
    assert not valid_output(plan)
