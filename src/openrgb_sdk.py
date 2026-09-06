#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded, loopback-only OpenRGB SDK writer for Open Hardware Control.

The separately installed OpenRGB process continues to own discovery and all
controller-specific hardware protocols. This helper implements only the
published SDK 4/5 packet formats needed to inspect one controller and write a
bounded color frame. Direct colors are always sent as one complete device
frame. During the first Direct-mode initialization a complete zone map is also
sent once as a compatibility fallback for drivers that only implement the
zone update callback. This avoids the OpenRGB CLI ``ApplyOptions`` crash path
and lets OHC verify the server-side color state before reporting success.

The optional JSON-lines worker keeps one SDK connection open while an OHC
animation is running.  It prepares every selected controller once and then
sends one complete frame for all Direct devices per request.  No hardware
driver is implemented here; OpenRGB remains the controller owner and the
worker remains restricted to the configured loopback endpoint.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import struct
import sys
import time
from dataclasses import dataclass
from typing import Iterable, TextIO


SDK_MAGIC = b"ORGB"
# OHC deliberately negotiates no newer than revision 5. Protocol 6 changes
# device IDs from list indexes to stable IDs and is not needed for Fedora's
# OpenRGB 1.0-rc2 backend.
SDK_MIN_PROTOCOL_VERSION = 4
SDK_PROTOCOL_VERSION = 5
SDK_HEADER = struct.Struct("<4sIII")
PACKET_REQUEST_CONTROLLER_COUNT = 0
PACKET_REQUEST_CONTROLLER_DATA = 1
PACKET_REQUEST_PROTOCOL_VERSION = 40
PACKET_SET_CLIENT_NAME = 50
PACKET_DEVICE_LIST_UPDATED = 100
PACKET_RESIZE_ZONE = 1000
PACKET_UPDATE_LEDS = 1050
PACKET_UPDATE_ZONE_LEDS = 1051
PACKET_SET_CUSTOM_MODE = 1100
MAX_DEVICE_ID = 4096
MAX_LED_COUNT = 4096
MAX_MODE_COUNT = 512
MAX_ZONE_COUNT = 4096
MAX_PACKET_SIZE = 4 * 1024 * 1024
MAX_WORKER_REQUEST_SIZE = 2 * 1024 * 1024
MAX_WORKER_DEVICES = 64
ZONE_FLAG_RESIZE_EFFECTS_ONLY = 1 << 0


class OpenRGBSDKError(RuntimeError):
    """A validated local SDK transaction could not be completed."""


@dataclass(frozen=True)
class SDKPacket:
    device_id: int
    packet_type: int
    payload: bytes

    def pack(self) -> bytes:
        if not 0 <= int(self.device_id) <= MAX_DEVICE_ID:
            raise ValueError("Ungültige OpenRGB-Gerätenummer.")
        if not 0 <= len(self.payload) <= MAX_PACKET_SIZE:
            raise ValueError("Ungültige OpenRGB-SDK-Paketgröße.")
        return SDK_HEADER.pack(
            SDK_MAGIC,
            int(self.device_id),
            int(self.packet_type),
            len(self.payload),
        ) + self.payload


@dataclass(frozen=True)
class SDKZone:
    name: str
    zone_type: int
    leds_min: int
    leds_max: int
    led_count: int
    flags: int = 0

    @property
    def effective_led_count(self) -> int:
        if self.flags & ZONE_FLAG_RESIZE_EFFECTS_ONLY and self.led_count > 1:
            return 1
        return self.led_count

    @property
    def resizable(self) -> bool:
        return self.leds_min != self.leds_max


@dataclass(frozen=True)
class SDKController:
    name: str
    modes: tuple[str, ...]
    active_mode: int
    zones: tuple[SDKZone, ...]
    led_count: int
    colors: tuple[str, ...]

    @property
    def active_mode_name(self) -> str:
        if 0 <= self.active_mode < len(self.modes):
            return self.modes[self.active_mode]
        return ""

    @property
    def direct_active(self) -> bool:
        return self.active_mode_name.casefold() in {"direct", "custom"}

    @property
    def supports_direct(self) -> bool:
        return any(mode.casefold() == "direct" for mode in self.modes)


@dataclass(frozen=True)
class SDKWriteResult:
    protocol_version: int
    device_id: int
    led_count: int
    zone_count: int
    write_path: str
    custom_mode_changed: bool


@dataclass(frozen=True)
class PreparedDevice:
    requested_led_count: int
    led_count: int
    zone_sizes: tuple[int, ...]
    name: str
    write_path: str


class PayloadReader:
    """Bounds-checked parser for one SDK controller-description payload."""

    def __init__(self, payload: bytes):
        self.payload = payload
        self.offset = 0

    @property
    def remaining(self) -> int:
        return len(self.payload) - self.offset

    def take(self, amount: int) -> bytes:
        size = int(amount)
        if size < 0 or size > self.remaining:
            raise OpenRGBSDKError("Die OpenRGB-Gerätebeschreibung ist abgeschnitten.")
        start = self.offset
        self.offset += size
        return self.payload[start:self.offset]

    def value(self, fmt: str) -> int:
        shape = struct.Struct("<" + fmt)
        return int(shape.unpack(self.take(shape.size))[0])

    def string(self) -> str:
        size = self.value("H")
        raw = self.take(size)
        if raw.endswith(b"\0"):
            raw = raw[:-1]
        return raw.decode("utf-8", "replace")


def validate_loopback(address: str) -> str:
    parsed = ipaddress.ip_address(str(address))
    if not parsed.is_loopback:
        raise ValueError("OpenRGB darf nur über eine lokale Loopback-Adresse angesprochen werden.")
    return str(parsed)


def normalize_colors(colors: Iterable[str], led_count: int) -> tuple[str, ...]:
    count = int(led_count)
    if not 1 <= count <= MAX_LED_COUNT:
        raise ValueError("Die OpenRGB-LED-Anzahl ist ungültig.")
    clean = tuple(str(color).strip().lstrip("#").casefold() for color in colors)
    if not clean:
        raise ValueError("Mindestens eine RGB-Farbe ist erforderlich.")
    if any(len(color) != 6 or any(char not in "0123456789abcdef" for char in color) for color in clean):
        raise ValueError("Ungültige RGB-Farbe.")
    if len(clean) == 1:
        return clean * count
    if len(clean) != count:
        raise ValueError("Die Farbliste muss genau zur gemeldeten LED-Anzahl passen.")
    return clean


def color_bytes(colors: Iterable[str]) -> bytes:
    return b"".join(
        struct.pack("<BBBx", int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
        for color in colors
    )


def color_payload(colors: Iterable[str], led_count: int) -> bytes:
    clean = normalize_colors(colors, led_count)
    data = struct.pack("<H", len(clean)) + color_bytes(clean)
    # OpenRGB wraps variable-length lists in a uint32 size field that includes
    # the size field itself.
    return struct.pack("<I", len(data) + 4) + data


def zone_color_payload(zone_index: int, colors: Iterable[str]) -> bytes:
    clean = tuple(colors)
    if not clean or len(clean) > MAX_LED_COUNT:
        raise ValueError("Ungültige OpenRGB-Zonenfarbliste.")
    data = struct.pack("<IH", int(zone_index), len(clean)) + color_bytes(clean)
    return struct.pack("<I", len(data) + 4) + data


def remap_colors(colors: Iterable[str], expected_count: int, actual_count: int) -> tuple[str, ...]:
    source = normalize_colors(colors, expected_count)
    target_count = int(actual_count)
    if not 1 <= target_count <= MAX_LED_COUNT:
        raise OpenRGBSDKError("OpenRGB meldet keine gültige Zahl steuerbarer Farben.")
    if len(source) == target_count:
        return source
    # Device data from the SDK is authoritative. When the CLI listing was
    # stale, resample a generated frame deterministically rather than writing
    # past the controller's real color buffer.
    return tuple(source[min(len(source) - 1, (idx * len(source)) // target_count)] for idx in range(target_count))


def recv_exact(connection: socket.socket, amount: int) -> bytes:
    chunks: list[bytes] = []
    remaining = amount
    while remaining:
        chunk = connection.recv(remaining)
        if not chunk:
            raise OpenRGBSDKError("Der lokale OpenRGB-SDK-Server hat die Verbindung vorzeitig beendet.")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def receive_packet(connection: socket.socket) -> SDKPacket:
    raw_header = recv_exact(connection, SDK_HEADER.size)
    magic, device_id, packet_type, size = SDK_HEADER.unpack(raw_header)
    if magic != SDK_MAGIC or size > MAX_PACKET_SIZE:
        raise OpenRGBSDKError("Der lokale Dienst lieferte kein gültiges OpenRGB-SDK-Paket.")
    return SDKPacket(device_id, packet_type, recv_exact(connection, size))


def receive_response(connection: socket.socket, packet_type: int, device_id: int | None = None) -> SDKPacket:
    # Protocol 1+ may notify connected clients about an inventory refresh at
    # any time. Ignore only that documented notification, never arbitrary
    # unexpected packets.
    for _attempt in range(8):
        packet = receive_packet(connection)
        if packet.packet_type == PACKET_DEVICE_LIST_UPDATED:
            continue
        if packet.packet_type != packet_type:
            raise OpenRGBSDKError(
                f"Unerwartete OpenRGB-SDK-Antwort {packet.packet_type}; erwartet wurde {packet_type}."
            )
        if device_id is not None and packet.device_id != int(device_id):
            raise OpenRGBSDKError("Die OpenRGB-SDK-Antwort gehört zu einem anderen Gerät.")
        return packet
    raise OpenRGBSDKError("Zu viele OpenRGB-Gerätelistenänderungen während des Schreibvorgangs.")


def _skip_mode(reader: PayloadReader, protocol_version: int) -> str:
    name = reader.string()
    reader.value("i")  # mode_value exists through protocol 5
    reader.value("I")  # flags
    reader.value("I")  # speed_min
    reader.value("I")  # speed_max
    if protocol_version >= 3:
        reader.value("I")  # brightness_min
        reader.value("I")  # brightness_max
    reader.value("I")  # colors_min
    reader.value("I")  # colors_max
    reader.value("I")  # speed
    if protocol_version >= 3:
        reader.value("I")  # brightness
    reader.value("I")  # direction
    reader.value("I")  # color_mode
    mode_colors = reader.value("H")
    if mode_colors > MAX_LED_COUNT:
        raise OpenRGBSDKError("OpenRGB meldet zu viele Modusfarben.")
    reader.take(mode_colors * 4)
    return name


def _parse_zone(reader: PayloadReader, protocol_version: int) -> SDKZone:
    name = reader.string()
    zone_type = reader.value("i")
    leds_min = reader.value("I")
    leds_max = reader.value("I")
    led_count = reader.value("I")
    if any(value > MAX_LED_COUNT for value in (leds_min, leds_max, led_count)):
        raise OpenRGBSDKError("OpenRGB meldet eine zu große RGB-Zone.")
    if leds_min > leds_max or (led_count != 0 and not leds_min <= led_count <= leds_max):
        raise OpenRGBSDKError("OpenRGB meldet ungültige Grenzen für eine RGB-Zone.")
    matrix_size = reader.value("H")
    reader.take(matrix_size)
    if protocol_version >= 4:
        segment_count = reader.value("H")
        if segment_count > MAX_ZONE_COUNT:
            raise OpenRGBSDKError("OpenRGB meldet zu viele Zonensegmente.")
        for _segment in range(segment_count):
            reader.string()
            reader.value("i")
            reader.value("I")
            reader.value("I")
    flags = reader.value("I") if protocol_version >= 5 else 0
    return SDKZone(name, zone_type, leds_min, leds_max, led_count, flags)


def parse_controller_data(payload: bytes, protocol_version: int) -> SDKController:
    if protocol_version not in {4, 5}:
        raise OpenRGBSDKError("Die OpenRGB-Gerätebeschreibung verwendet eine nicht unterstützte Version.")
    reader = PayloadReader(payload)
    declared_size = reader.value("I")
    if declared_size != len(payload):
        raise OpenRGBSDKError("Die OpenRGB-Gerätebeschreibung meldet eine falsche Größe.")
    reader.value("i")  # device_type
    name = reader.string()
    reader.string()  # vendor, protocol 1+
    reader.string()  # description
    reader.string()  # version
    reader.string()  # serial
    reader.string()  # location
    mode_count = reader.value("H")
    if mode_count > MAX_MODE_COUNT:
        raise OpenRGBSDKError("OpenRGB meldet zu viele Gerätemodi.")
    active_mode = reader.value("i")
    modes = tuple(_skip_mode(reader, protocol_version) for _mode in range(mode_count))
    zone_count = reader.value("H")
    if zone_count > MAX_ZONE_COUNT:
        raise OpenRGBSDKError("OpenRGB meldet zu viele RGB-Zonen.")
    zones = tuple(_parse_zone(reader, protocol_version) for _zone in range(zone_count))
    led_count = reader.value("H")
    if led_count > MAX_LED_COUNT:
        raise OpenRGBSDKError("OpenRGB meldet zu viele LEDs.")
    for _led in range(led_count):
        reader.string()
        reader.value("I")  # led_value exists through protocol 5
    color_count = reader.value("H")
    if color_count > MAX_LED_COUNT:
        raise OpenRGBSDKError("OpenRGB meldet zu viele steuerbare Gerätefarben.")
    colors: list[str] = []
    for _color in range(color_count):
        red, green, blue, _padding = struct.unpack("<BBBB", reader.take(4))
        colors.append(f"{red:02x}{green:02x}{blue:02x}")
    if protocol_version >= 5:
        display_name_count = reader.value("H")
        if display_name_count > MAX_LED_COUNT:
            raise OpenRGBSDKError("OpenRGB meldet zu viele LED-Anzeigenamen.")
        for _display_name in range(display_name_count):
            reader.string()
        reader.value("I")  # controller flags
    if reader.remaining:
        raise OpenRGBSDKError("Die OpenRGB-Gerätebeschreibung enthält unerwartete Zusatzdaten.")
    return SDKController(name, modes, active_mode, zones, led_count, tuple(colors))


def request_controller_data(
    connection: socket.socket,
    device_id: int,
    protocol_version: int,
) -> SDKController:
    connection.sendall(
        SDKPacket(device_id, PACKET_REQUEST_CONTROLLER_DATA, struct.pack("<I", protocol_version)).pack()
    )
    reply = receive_response(connection, PACKET_REQUEST_CONTROLLER_DATA, device_id)
    return parse_controller_data(reply.payload, protocol_version)


def negotiate_connection(connection: socket.socket) -> int:
    connection.sendall(
        SDKPacket(0, PACKET_REQUEST_PROTOCOL_VERSION, struct.pack("<I", SDK_PROTOCOL_VERSION)).pack()
    )
    reply = receive_response(connection, PACKET_REQUEST_PROTOCOL_VERSION)
    if len(reply.payload) != 4:
        raise OpenRGBSDKError("Der OpenRGB-SDK-Server beantwortete die Versionsabfrage ungültig.")
    server_version = struct.unpack("<I", reply.payload)[0]
    negotiated = min(server_version, SDK_PROTOCOL_VERSION)
    if negotiated < SDK_MIN_PROTOCOL_VERSION:
        raise OpenRGBSDKError(
            "Nicht unterstützte OpenRGB-SDK-Protokollversion "
            f"{server_version}; mindestens erforderlich ist {SDK_MIN_PROTOCOL_VERSION}."
        )
    connection.sendall(SDKPacket(0, PACKET_SET_CLIENT_NAME, b"Open Hardware Control\0").pack())
    return negotiated


def synchronized_controller(
    connection: socket.socket,
    device_id: int,
    protocol_version: int,
) -> SDKController:
    connection.sendall(SDKPacket(0, PACKET_REQUEST_CONTROLLER_COUNT, b"").pack())
    count_reply = receive_response(connection, PACKET_REQUEST_CONTROLLER_COUNT)
    if len(count_reply.payload) != 4:
        raise OpenRGBSDKError("OpenRGB lieferte keine gültige Geräteanzahl.")
    controller_count = struct.unpack("<I", count_reply.payload)[0]
    if device_id >= controller_count:
        raise OpenRGBSDKError(
            f"OpenRGB-Gerät {device_id} ist nicht mehr vorhanden; aktuell werden {controller_count} Geräte gemeldet."
        )
    return request_controller_data(connection, device_id, protocol_version)


def inspect_device(
    address: str,
    port: int,
    device_id: int,
    *,
    timeout: float = 2.0,
) -> tuple[int, SDKController]:
    host = validate_loopback(address)
    service_port = int(port)
    if not 1024 <= service_port <= 65535:
        raise ValueError("Der OpenRGB-Port muss zwischen 1024 und 65535 liegen.")
    device = int(device_id)
    if not 0 <= device <= MAX_DEVICE_ID:
        raise ValueError("Ungültige OpenRGB-Gerätenummer.")
    socket_timeout = max(0.1, min(5.0, timeout))
    with socket.create_connection((host, service_port), timeout=socket_timeout) as connection:
        connection.settimeout(socket_timeout)
        negotiated = negotiate_connection(connection)
        return negotiated, synchronized_controller(connection, device, negotiated)


def resize_controller_zones(
    connection: socket.socket,
    device_id: int,
    protocol_version: int,
    controller: SDKController,
    requested_sizes: Iterable[int],
    timeout: float,
) -> SDKController:
    sizes = tuple(int(value) for value in requested_sizes)
    if len(sizes) != len(controller.zones):
        raise OpenRGBSDKError(
            f"Zonenkonfiguration unvollständig: erwartet {len(controller.zones)}, erhalten {len(sizes)}."
        )
    for index, (zone, size) in enumerate(zip(controller.zones, sizes)):
        if not 0 <= size <= MAX_LED_COUNT:
            raise OpenRGBSDKError(f"Zone „{zone.name or index}“ hat eine ungültige LED-Anzahl.")
        if size != zone.led_count and not zone.leds_min <= size <= zone.leds_max:
            raise OpenRGBSDKError(
                f"Zone „{zone.name or index}“ erlaubt {zone.leds_min}–{zone.leds_max} LEDs; angefordert wurden {size}."
            )
        if size != zone.led_count and not zone.resizable:
            raise OpenRGBSDKError(f"Zone „{zone.name or index}“ ist laut OpenRGB nicht vergrößerbar.")
    changed = False
    for index, (zone, size) in enumerate(zip(controller.zones, sizes)):
        if size == zone.led_count:
            continue
        connection.sendall(
            SDKPacket(device_id, PACKET_RESIZE_ZONE, struct.pack("<ii", index, size)).pack()
        )
        changed = True
    if not changed:
        return controller

    deadline = time.monotonic() + timeout
    current = controller
    while time.monotonic() < deadline:
        time.sleep(0.02)
        current = request_controller_data(connection, device_id, protocol_version)
        if tuple(zone.led_count for zone in current.zones) == sizes:
            return current
    actual = tuple(zone.led_count for zone in current.zones)
    raise OpenRGBSDKError(
        f"OpenRGB hat die Zonengrößen nicht bestätigt (angefordert {sizes}, gemeldet {actual})."
    )


def prepare_controller_write(
    connection: socket.socket,
    device: int,
    protocol_version: int,
    led_count: int,
    colors: Iterable[str],
    *,
    timeout: float,
    set_custom_mode: bool,
    zone_sizes: Iterable[int] | None,
) -> tuple[SDKWriteResult, PreparedDevice]:
    """Prepare one Direct controller and confirm its first complete frame."""

    requested_colors = tuple(colors)
    controller = synchronized_controller(connection, device, protocol_version)
    if not controller.supports_direct:
        raise OpenRGBSDKError(
            f"{controller.name or f'Gerät {device}'} meldet im SDK keinen Direct Mode."
        )
    requested_zone_sizes = tuple(int(value) for value in zone_sizes) if zone_sizes is not None else None
    if requested_zone_sizes is not None:
        controller = resize_controller_zones(
            connection,
            device,
            protocol_version,
            controller,
            requested_zone_sizes,
            timeout,
        )

    custom_changed = False
    # Prime Direct/Custom mode exactly once for a freshly prepared controller
    # when requested by the persistent worker.  ENE-based DRAM can report
    # Direct as active while the physical LEDs are still latched to the
    # firmware rainbow state after boot.  Re-entering Direct once when a new
    # worker session claims the device wakes that hardware up; cached frames
    # never repeat this packet, so we avoid the old per-frame reset problem.
    if set_custom_mode or not controller.direct_active:
        connection.sendall(SDKPacket(device, PACKET_SET_CUSTOM_MODE, b"").pack())
        custom_changed = True
        controller = request_controller_data(connection, device, protocol_version)
        if not controller.direct_active:
            raise OpenRGBSDKError(
                f"{controller.name or f'Gerät {device}'} hat den Direct Mode nicht bestätigt."
            )

    if not controller.colors:
        zone_state = ", ".join(
            f"{zone.name or index}={zone.led_count} ({zone.leds_min}–{zone.leds_max})"
            for index, zone in enumerate(controller.zones)
        ) or "keine Zonen"
        raise OpenRGBSDKError(
            "KONFIGURATION_ERFORDERLICH: OpenRGB meldet 0 angelegte LEDs. "
            f"Zonengrößen: {zone_state}. Bitte Lüfter und LEDs je Kanal in OHC einrichten."
        )

    target = remap_colors(requested_colors, int(led_count), len(controller.colors))
    effective_zone_sizes = tuple(zone.effective_led_count for zone in controller.zones)
    complete_zone_map = bool(effective_zone_sizes) and sum(effective_zone_sizes) == len(target)
    connection.sendall(
        SDKPacket(device, PACKET_UPDATE_LEDS, color_payload(target, len(target))).pack()
    )
    written_zones = 0
    write_path = "device"
    if custom_changed and complete_zone_map and sum(size > 0 for size in effective_zone_sizes) > 1:
        offset = 0
        for zone_index, zone_size in enumerate(effective_zone_sizes):
            if zone_size <= 0:
                continue
            connection.sendall(
                SDKPacket(
                    device,
                    PACKET_UPDATE_ZONE_LEDS,
                    zone_color_payload(zone_index, target[offset:offset + zone_size]),
                ).pack()
            )
            offset += zone_size
            written_zones += 1
        write_path = "device+zones"

    deadline = time.monotonic() + timeout
    confirmed: SDKController | None = None
    while time.monotonic() < deadline:
        time.sleep(0.02)
        current = request_controller_data(connection, device, protocol_version)
        if current.colors == target and current.direct_active:
            confirmed = current
            break
    if confirmed is None:
        raise OpenRGBSDKError(
            f"{controller.name or f'Gerät {device}'} hat die gesendeten Farben nicht bestätigt."
        )
    result = SDKWriteResult(
        protocol_version,
        device,
        len(target),
        written_zones,
        write_path,
        custom_changed,
    )
    prepared = PreparedDevice(
        int(led_count),
        len(target),
        tuple(zone.led_count for zone in confirmed.zones),
        confirmed.name or controller.name,
        write_path,
    )
    return result, prepared


class OpenRGBPersistentSession:
    """One reconnecting loopback SDK session for bounded animation frames."""

    def __init__(self, address: str, port: int, *, timeout: float = 2.0):
        self.address = validate_loopback(address)
        self.port = int(port)
        if not 1024 <= self.port <= 65535:
            raise ValueError("Der OpenRGB-Port muss zwischen 1024 und 65535 liegen.")
        self.timeout = max(0.1, min(5.0, float(timeout)))
        self.connection: socket.socket | None = None
        self.protocol_version = 0
        self.prepared: dict[int, PreparedDevice] = {}

    def connect(self) -> None:
        if self.connection is not None:
            return
        connection = socket.create_connection((self.address, self.port), timeout=self.timeout)
        try:
            connection.settimeout(self.timeout)
            protocol = negotiate_connection(connection)
        except BaseException:
            connection.close()
            raise
        self.connection = connection
        self.protocol_version = protocol

    def close(self) -> None:
        connection = self.connection
        self.connection = None
        self.protocol_version = 0
        self.prepared.clear()
        if connection is not None:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()

    def write_frame(
        self,
        device_id: int,
        led_count: int,
        colors: Iterable[str],
        *,
        zone_sizes: Iterable[int] | None = None,
        force_prepare: bool = False,
    ) -> dict[str, object]:
        device = int(device_id)
        if not 0 <= device <= MAX_DEVICE_ID:
            raise ValueError("Ungültige OpenRGB-Gerätenummer.")
        requested_count = int(led_count)
        requested_zone_sizes = tuple(int(value) for value in zone_sizes) if zone_sizes is not None else ()
        requested_colors = tuple(colors)
        self.connect()
        assert self.connection is not None
        cached = self.prepared.get(device)
        shape_changed = cached is not None and (
            cached.requested_led_count != requested_count
            or (requested_zone_sizes and cached.zone_sizes != requested_zone_sizes)
        )
        if force_prepare or cached is None or shape_changed:
            result, prepared = prepare_controller_write(
                self.connection,
                device,
                self.protocol_version,
                requested_count,
                requested_colors,
                timeout=self.timeout,
                set_custom_mode=True,
                zone_sizes=requested_zone_sizes or None,
            )
            self.prepared[device] = prepared
            return {
                "ok": True,
                "device": device,
                "led_count": result.led_count,
                "prepared": True,
                "write_path": result.write_path,
                "protocol": result.protocol_version,
            }
        target = remap_colors(requested_colors, requested_count, cached.led_count)
        self.connection.sendall(
            SDKPacket(device, PACKET_UPDATE_LEDS, color_payload(target, len(target))).pack()
        )
        return {
            "ok": True,
            "device": device,
            "led_count": len(target),
            "prepared": False,
            "write_path": "device",
            "protocol": self.protocol_version,
        }


def process_worker_frame(
    session: OpenRGBPersistentSession,
    request: dict[str, object],
) -> dict[str, object]:
    """Validate and execute one latest-frame-wins worker request."""

    request_id = max(0, int(request.get("id", 0)))
    raw_devices = request.get("devices")
    if not isinstance(raw_devices, list) or not 1 <= len(raw_devices) <= MAX_WORKER_DEVICES:
        raise ValueError("Ein Worker-Frame benötigt 1–64 Geräte.")
    seen: set[int] = set()
    results: list[dict[str, object]] = []
    started = time.monotonic()
    for raw_device in raw_devices:
        if not isinstance(raw_device, dict):
            raise ValueError("Ungültiger Geräteauftrag im Worker-Frame.")
        key = str(raw_device.get("key", ""))[:128]
        device_id = int(raw_device.get("device", -1))
        if device_id in seen:
            raise ValueError("Ein OpenRGB-Gerät darf pro Frame nur einmal vorkommen.")
        seen.add(device_id)
        colors = raw_device.get("colors")
        if not isinstance(colors, list):
            raise ValueError("Die Worker-Farben müssen als Liste übertragen werden.")
        zone_sizes_value = raw_device.get("zone_sizes")
        if zone_sizes_value is not None and not isinstance(zone_sizes_value, list):
            raise ValueError("Die Worker-Zonengrößen müssen als Liste übertragen werden.")
        device_started = time.monotonic()
        try:
            result = session.write_frame(
                device_id,
                int(raw_device.get("led_count", 0)),
                [str(color) for color in colors],
                zone_sizes=[int(value) for value in zone_sizes_value] if zone_sizes_value is not None else None,
                force_prepare=bool(raw_device.get("prepare", False)),
            )
            result["key"] = key
            result["duration_ms"] = round((time.monotonic() - device_started) * 1000.0, 3)
            results.append(result)
        except (OSError, ValueError, OpenRGBSDKError) as exc:
            results.append({
                "ok": False,
                "key": key,
                "device": device_id,
                "error": str(exc)[:800],
                "duration_ms": round((time.monotonic() - device_started) * 1000.0, 3),
            })
            # A short/invalid socket transaction leaves packet boundaries
            # uncertain. Reconnect before the next device instead of risking
            # a write to the wrong controller.
            if isinstance(exc, OSError) or "Verbindung" in str(exc) or "Antwort" in str(exc):
                session.close()
    return {
        "type": "frame",
        "id": request_id,
        "ok": all(bool(item.get("ok")) for item in results),
        "duration_ms": round((time.monotonic() - started) * 1000.0, 3),
        "devices": results,
    }


def run_worker(
    address: str,
    port: int,
    *,
    input_stream: TextIO = sys.stdin,
    output_stream: TextIO = sys.stdout,
) -> int:
    """Run the bounded JSON-lines worker until stdin closes or stop arrives."""

    session = OpenRGBPersistentSession(address, port)
    print(json.dumps({"type": "ready", "protocol_max": SDK_PROTOCOL_VERSION}), file=output_stream, flush=True)
    try:
        for raw_line in input_stream:
            if len(raw_line) > MAX_WORKER_REQUEST_SIZE:
                response: dict[str, object] = {"type": "error", "error": "Worker-Auftrag ist zu groß."}
            else:
                try:
                    request = json.loads(raw_line)
                    if not isinstance(request, dict):
                        raise ValueError("Worker-Auftrag muss ein JSON-Objekt sein.")
                    operation = str(request.get("op", "frame"))
                    if operation == "stop":
                        print(json.dumps({"type": "stopped"}), file=output_stream, flush=True)
                        return 0
                    if operation != "frame":
                        raise ValueError("Unbekannter Worker-Auftrag.")
                    response = process_worker_frame(session, request)
                except (TypeError, ValueError, json.JSONDecodeError, OpenRGBSDKError) as exc:
                    response = {"type": "error", "id": 0, "error": str(exc)[:800]}
            print(json.dumps(response, ensure_ascii=False), file=output_stream, flush=True)
    finally:
        session.close()
    return 0


def write_device_colors(
    address: str,
    port: int,
    device_id: int,
    led_count: int,
    colors: Iterable[str],
    *,
    timeout: float = 2.0,
    set_custom_mode: bool = True,
    zone_sizes: Iterable[int] | None = None,
) -> SDKWriteResult:
    host = validate_loopback(address)
    service_port = int(port)
    if not 1024 <= service_port <= 65535:
        raise ValueError("Der OpenRGB-Port muss zwischen 1024 und 65535 liegen.")
    device = int(device_id)
    if not 0 <= device <= MAX_DEVICE_ID:
        raise ValueError("Ungültige OpenRGB-Gerätenummer.")
    requested_colors = tuple(colors)
    socket_timeout = max(0.1, min(5.0, timeout))
    with socket.create_connection((host, service_port), timeout=socket_timeout) as connection:
        connection.settimeout(socket_timeout)
        negotiated = negotiate_connection(connection)
        result, _prepared = prepare_controller_write(
            connection,
            device,
            negotiated,
            int(led_count),
            requested_colors,
            timeout=socket_timeout,
            set_custom_mode=set_custom_mode,
            zone_sizes=zone_sizes,
        )
        time.sleep(0.03)
        return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lokaler OpenRGB-SDK-Schreibhelfer")
    parser.add_argument("--address", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6742)
    parser.add_argument("--device", type=int)
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--led-count", type=int)
    parser.add_argument("--colors", help="Kommagetrennte RRGGBB-Farben")
    parser.add_argument("--zone-sizes", help="Kommagetrennte LED-Anzahl je OpenRGB-Zone")
    parser.add_argument("--no-custom-mode", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.worker:
            if arguments.inspect or arguments.device is not None or arguments.colors:
                raise ValueError("Der Worker-Modus kann nicht mit Einzelgeräteoptionen kombiniert werden.")
            return run_worker(arguments.address, arguments.port)
        if arguments.device is None:
            raise ValueError("Für Einzelgeräteaufträge wird --device benötigt.")
        if arguments.inspect:
            protocol, controller = inspect_device(
                arguments.address, arguments.port, arguments.device
            )
            print(json.dumps({
                "protocol": protocol,
                "device": arguments.device,
                "name": controller.name,
                "active_mode": controller.active_mode_name,
                "supports_direct": controller.supports_direct,
                "led_count": controller.led_count,
                "color_count": len(controller.colors),
                "zones": [
                    {
                        "index": index,
                        "name": zone.name,
                        "type": zone.zone_type,
                        "minimum": zone.leds_min,
                        "maximum": zone.leds_max,
                        "current": zone.led_count,
                        "flags": zone.flags,
                        "resizable": zone.resizable,
                    }
                    for index, zone in enumerate(controller.zones)
                ],
            }, ensure_ascii=False))
            return 0
        if arguments.led_count is None or not arguments.colors:
            raise ValueError("Für einen Schreibauftrag werden --led-count und --colors benötigt.")
        requested_zone_sizes = None
        if arguments.zone_sizes is not None:
            requested_zone_sizes = tuple(
                int(value.strip()) for value in arguments.zone_sizes.split(",") if value.strip()
            )
        result = write_device_colors(
            arguments.address,
            arguments.port,
            arguments.device,
            arguments.led_count,
            arguments.colors.split(","),
            set_custom_mode=not arguments.no_custom_mode,
            zone_sizes=requested_zone_sizes,
        )
    except (OSError, ValueError, OpenRGBSDKError) as exc:
        print(f"OpenRGB-SDK: {exc}", file=sys.stderr)
        return 1
    if result.write_path == "device+zones":
        path = f"Geräteframe + {result.zone_count} Zonen-Fallback(s)"
    else:
        path = "vollständiger Geräteframe"
    print(
        f"OpenRGB-SDK: Serverzustand bestätigt · Gerät {result.device_id} · {result.led_count} LED(s) · "
        f"{path} · Protokoll {result.protocol_version} · physische ARGB-Ausgabe nicht rücklesbar"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
