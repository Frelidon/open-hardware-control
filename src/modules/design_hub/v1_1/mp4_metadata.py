# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded structural checks for our fast-start H.264 LCD derivatives.

This reads metadata, not video frames. It rejects incomplete cache files and
wrong encoder geometry without launching a subprocess on the GUI thread.
"""
from dataclasses import dataclass
import struct

MAX_METADATA_BYTES = 1024 * 1024
MAX_ATOMS = 512
MAX_DEPTH = 8
CONTAINERS = {b'trak', b'mdia', b'minf', b'stbl', b'dinf', b'edts', b'moov'}


class InvalidMetadata(ValueError):
    pass


@dataclass(frozen=True)
class Atom:
    tag: bytes
    payload: memoryview
    children: tuple = ()


class MetadataReader:
    def __init__(self):
        self.bytes_read = 0
        self.atoms = 0

    def read(self, stream, count):
        if count < 0 or self.bytes_read + count > MAX_METADATA_BYTES:
            raise InvalidMetadata('metadata budget')
        data = stream.read(count)
        self.bytes_read += len(data)
        if len(data) != count:
            raise InvalidMetadata('truncated metadata')
        return data

    def count_atom(self):
        self.atoms += 1
        if self.atoms > MAX_ATOMS:
            raise InvalidMetadata('atom budget')

    def boxes(self, data, start=0, end=None, depth=1):
        if depth > MAX_DEPTH:
            raise InvalidMetadata('atom depth')
        end = len(data) if end is None else end
        result = []
        while start < end:
            self.count_atom()
            if end - start < 8:
                raise InvalidMetadata('truncated atom')
            size, tag = struct.unpack_from('>I4s', data, start)
            header = 8
            if size == 1:
                if end - start < 16:
                    raise InvalidMetadata('truncated extended atom')
                size = struct.unpack_from('>Q', data, start + 8)[0]
                header = 16
            if size < header or size > end - start:
                raise InvalidMetadata('invalid atom extent')
            payload = data[start + header:start + size]
            children = self.boxes(payload, depth=depth + 1) if tag in CONTAINERS else ()
            result.append(Atom(tag, payload, tuple(children)))
            start += size
        return result

    def movie(self, stream, file_size):
        position = 0
        movie = None
        found_ftyp = found_media = False
        while position < file_size:
            self.count_atom()
            if file_size - position < 8:
                raise InvalidMetadata('truncated file atom')
            stream.seek(position)
            size, tag = struct.unpack('>I4s', self.read(stream, 8))
            header = 8
            if size == 1:
                size = struct.unpack('>Q', self.read(stream, 8))[0]
                header = 16
            if size < header or size > file_size - position:
                raise InvalidMetadata('invalid file atom extent')
            if tag == b'ftyp':
                if position or found_ftyp:
                    raise InvalidMetadata('invalid file type position')
                payload = self.read(stream, size - header)
                if len(payload) < 8 or len(payload) % 4:
                    raise InvalidMetadata('invalid file type')
                found_ftyp = True
            elif tag == b'moov':
                if movie is not None:
                    raise InvalidMetadata('duplicate movie')
                movie = self.boxes(memoryview(self.read(stream, size - header)))
            elif tag == b'mdat' and size > header:
                found_media = True
            position += size
        if not found_ftyp or not found_media or movie is None:
            raise InvalidMetadata('missing movie metadata or media')
        return movie


def only(atoms, tag):
    matches = [atom for atom in atoms if atom.tag == tag]
    if len(matches) != 1:
        raise InvalidMetadata('missing or duplicate atom')
    return matches[0]


def video_track(movie):
    tracks = []
    for track in (atom for atom in movie if atom.tag == b'trak'):
        media = only(track.children, b'mdia')
        handler = only(media.children, b'hdlr').payload
        if len(handler) < 24 or handler[0] != 0:
            raise InvalidMetadata('invalid media handler')
        if handler[8:12] == b'vide':
            tracks.append((track, media))
    if len(tracks) != 1:
        raise InvalidMetadata('expected one video track')
    return tracks[0]


def track_geometry(track, width, height):
    data = only(track.children, b'tkhd').payload
    version = data[0] if data else -1
    expected_length = {0: 84, 1: 96}.get(version)
    if len(data) != expected_length:
        raise InvalidMetadata('invalid track header')
    if struct.unpack_from('>II', data, len(data) - 8) != (width << 16, height << 16):
        raise InvalidMetadata('wrong track geometry')


def media_duration(media):
    data = only(media.children, b'mdhd').payload
    version = data[0] if data else -1
    if version == 0 and len(data) == 24:
        timescale, duration = struct.unpack_from('>II', data, 12)
    elif version == 1 and len(data) == 36:
        timescale = struct.unpack_from('>I', data, 20)[0]
        duration = struct.unpack_from('>Q', data, 24)[0]
    else:
        raise InvalidMetadata('invalid media header')
    if not timescale or not 0 < duration <= 35 * timescale:
        raise InvalidMetadata('invalid media duration')


def avc_configuration(data):
    if len(data) < 7 or data[0] != 1 or data[4] & 3 != 3:
        raise InvalidMetadata('invalid H.264 configuration')
    position = 6
    sequence_count = data[5] & 31
    if not sequence_count:
        raise InvalidMetadata('missing H.264 sequence')
    for count in (sequence_count, None):
        if count is None:
            if position >= len(data):
                raise InvalidMetadata('missing H.264 picture count')
            count = data[position]; position += 1
            if not count:
                raise InvalidMetadata('missing H.264 picture')
        for _index in range(count):
            if position + 2 > len(data):
                raise InvalidMetadata('truncated H.264 configuration')
            length = struct.unpack_from('>H', data, position)[0]; position += 2
            if not length or length > len(data) - position:
                raise InvalidMetadata('invalid H.264 parameter extent')
            position += length


def codec_geometry(reader, media, width, height):
    table = only(only(media.children, b'minf').children, b'stbl')
    data = only(table.children, b'stsd').payload
    if len(data) < 8 or bytes(data[:4]) != b'\0\0\0\0':
        raise InvalidMetadata('invalid sample descriptions')
    entries = reader.boxes(data, 8, depth=6)
    if len(entries) != struct.unpack_from('>I', data, 4)[0] or len(entries) != 1:
        raise InvalidMetadata('expected one sample description')
    sample = entries[0]
    if sample.tag != b'avc1' or len(sample.payload) < 78:
        raise InvalidMetadata('expected H.264 visual sample')
    if struct.unpack_from('>HH', sample.payload, 24) != (width, height):
        raise InvalidMetadata('wrong sample geometry')
    children = reader.boxes(sample.payload, 78, depth=7)
    avc_configuration(only(children, b'avcC').payload)


def valid_lcd_mp4(stream, file_size, width, height):
    try:
        reader = MetadataReader()
        track, media = video_track(reader.movie(stream, file_size))
        track_geometry(track, width, height)
        media_duration(media)
        codec_geometry(reader, media, width, height)
        return True
    except (InvalidMetadata, OSError, ValueError, struct.error):
        return False
