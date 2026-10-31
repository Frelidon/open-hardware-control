# SPDX-License-Identifier: GPL-3.0-or-later
"""SDK4/5/6 packet fixtures only: no live OpenRGB discovery or hardware writes."""

from dataclasses import replace
import struct
from unittest.mock import patch

import pytest

from test_openrgb_sdk import controller_payload, sdk_mode, sdk_string
from openrgb_sdk import (
    OpenRGBInventoryChanged, OpenRGBPersistentSession, OpenRGBSDKError,
    SDK_HEADER, SDKPacket, SDKZone, negotiate_connection, parse_controller_data,
    receive_response, write_device_colors,
)
from modules.rgb_studio.v1_15 import sdk_v6


class FakeServer:
    """In-memory published packet endpoint with a deliberately non-index UUID."""
    def __init__(self, version=6):
        self.server_version = version
        self.protocol = 0
        self.uuid = 0xF0010234
        self.colors = ["000000", "000000"]
        self.active_mode = 1
        self.buffer = bytearray()
        self.received = []
        self.timeout = 1.0
        self.closed = False

    def queue(self, packet_type, payload=b"", device=0):
        self.buffer += SDKPacket(device, packet_type, payload).pack()

    def gettimeout(self):
        return self.timeout

    def settimeout(self, value):
        self.timeout = value

    def recv(self, amount):
        result = bytes(self.buffer[:amount])
        del self.buffer[:amount]
        return result

    def shutdown(self, _mode):
        pass

    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()

    def sendall(self, raw):
        _magic, device, kind, size = SDK_HEADER.unpack(raw[:16])
        payload = raw[16:]
        assert len(payload) == size
        self.received.append(SDKPacket(device, kind, payload))
        if kind == 40:
            self.protocol = min(self.server_version, struct.unpack("<I", payload)[0])
            if self.protocol >= 6:
                self.queue(51, b"OpenRGB\0")
                self.queue(55, b"test-host\0")
                self.queue(53, struct.pack("<I", 1))
            self.queue(40, struct.pack("<I", self.server_version))
        elif kind == 0:
            ids = struct.pack("<I", self.uuid) if self.protocol >= 6 else b""
            self.queue(0, struct.pack("<I", 1) + ids)
        elif kind == 1:
            assert device == (self.uuid if self.protocol >= 6 else 0)
            self.queue(1, controller_payload(self.protocol, self.active_mode, self.colors), device)
        elif kind == 1100:
            self.active_mode = 0
        elif kind == 1050:
            assert device == (self.uuid if self.protocol >= 6 else 0)
            assert struct.unpack_from("<I", payload)[0] == len(payload)
            count = struct.unpack_from("<H", payload, 4)[0]
            self.colors = [bytes(payload[6 + i * 4:9 + i * 4]).hex() for i in range(count)]
        elif kind == 1051:
            assert device == (self.uuid if self.protocol >= 6 else 0)
            zone = struct.unpack_from("<I", payload, 4)[0]
            self.colors[zone] = bytes(payload[10:13]).hex()
        elif kind != 50:
            raise AssertionError(f"Unknown outgoing packet {kind}")
        if self.protocol >= 6:
            self.queue(10, struct.pack("<II", kind, 0), device)
            if kind == 1050:
                # The callback can follow its ACK and must be drained before
                # the following cached frame instead of accumulating forever.
                self.queue(1150, struct.pack("<II", 8, 0), device)


@pytest.mark.parametrize("version", [4, 5, 6])
def test_controller_fixtures_preserve_format_by_negotiated_version(version):
    parsed = parse_controller_data(controller_payload(version, 0, ["112233", "445566"]), version)
    assert parsed.direct_active and parsed.supports_direct
    assert parsed.colors == ("112233", "445566")
    assert parsed.zones[0].display_name == ("Zone 1 display" if version == 6 else "")
    assert parsed.display_name == ("Controller display" if version == 6 else "")


@pytest.mark.parametrize("server_version,client_max,negotiated", [
    (4, 6, 4), (5, 6, 5), (6, 6, 6), (6, 5, 5), (7, 6, 6),
])
def test_client_server_minimum_and_uuid_write_mapping(server_version, client_max, negotiated):
    server = FakeServer(server_version)
    with patch("openrgb_sdk.socket.create_connection", return_value=server), patch(
        "openrgb_sdk.select.select", side_effect=lambda *_args: ([server] if server.buffer else [], [], []),
    ):
        result = write_device_colors("127.0.0.1", 6742, 0, 2, ["112233", "445566"], max_protocol=client_max)
    assert result.protocol_version == negotiated
    assert result.device_id == 0
    assert server.colors == ["112233", "445566"]
    for packet in server.received:
        if packet.packet_type in {1, 1050, 1051, 1100}:
            assert packet.device_id == (server.uuid if negotiated == 6 else 0)


def test_persistent_sdk6_uses_confirmed_uuid_and_reaps_acks_and_callbacks():
    server = FakeServer()
    session = OpenRGBPersistentSession("127.0.0.1", 6742, max_protocol=6)
    with patch("openrgb_sdk.socket.create_connection", return_value=server), patch(
        "openrgb_sdk.select.select", side_effect=lambda *_args: ([server] if server.buffer else [], [], []),
    ):
        first = session.write_frame(0, 2, ["112233", "445566"])
        second = session.write_frame(0, 2, ["778899", "aabbcc"])
        third = session.write_frame(0, 2, ["102030", "405060"])
    assert first["prepared"] and not second["prepared"] and not third["prepared"]
    assert [packet.packet_type for packet in server.received].count(0) == 1
    assert [packet.packet_type for packet in server.received].count(1100) == 1
    assert server.colors == ["102030", "405060"]
    assert all(packet.device_id == server.uuid for packet in server.received if packet.packet_type == 1050)
    session.close()


def test_profile_change_callback_is_consumed_before_own_write_ack():
    server = FakeServer()
    server.queue(157, b"temporary-profile\0")
    server.queue(10, struct.pack("<II", 1050, 0), server.uuid)
    response = receive_response(
        server, 10, server.uuid, protocol_version=6, ack_packet_id=1050,
    )
    assert response.packet_type == 10


def test_changed_inventory_stops_cached_writes_until_worker_restarts():
    server = FakeServer()
    session = OpenRGBPersistentSession("127.0.0.1", 6742, max_protocol=6)
    with patch("openrgb_sdk.socket.create_connection", return_value=server), patch(
        "openrgb_sdk.select.select", side_effect=lambda *_args: ([server] if server.buffer else [], [], []),
    ):
        session.write_frame(0, 2, ["112233"])
        sent_before = len(server.received)
        server.queue(100)
        with pytest.raises(OpenRGBInventoryChanged):
            session.write_frame(0, 2, ["ffffff"])
        with pytest.raises(OpenRGBInventoryChanged):
            session.write_frame(0, 2, ["ffffff"])
    assert len(server.received) == sent_before
    assert server.closed and session.inventory_invalidated


@pytest.mark.parametrize("kind,payload", [
    (10, struct.pack("<II", 1050, 5)), (10, b"broken"), (999, b""),
    (1150, struct.pack("<II", 99, 0)), (53, b"x"), (51, b"unterminated"),
    (157, b"unterminated"),
])
def test_failed_ack_malformed_callback_or_unknown_packet_is_not_ignored(kind, payload):
    server = FakeServer()
    server.queue(kind, payload)
    server.queue(0, struct.pack("<II", 1, server.uuid))
    with pytest.raises(OpenRGBSDKError):
        receive_response(server, 0, protocol_version=6)


def test_unsolicited_callback_flood_is_bounded():
    server = FakeServer()
    for _index in range(sdk_v6.MAX_PENDING_PACKETS):
        server.queue(51, b"OpenRGB\0")
    with pytest.raises(OpenRGBSDKError, match="Zu viele"):
        receive_response(server, 0, protocol_version=6)


@pytest.mark.parametrize("payload", [b"", struct.pack("<II", 2, 9), struct.pack("<III", 2, 9, 9), struct.pack("<I", 4098)])
def test_uuid_list_is_exact_bounded_and_unique(payload):
    with pytest.raises(ValueError):
        sdk_v6.controller_ids(payload, 4097)


def test_sdk6_zone_modes_are_parsed_and_override_global_direct_state():
    def zone_with_modes(value, count, protocol, minimum=None, maximum=None):
        matrix = struct.pack("<IIII", 1, 2, 0, 1)
        data = sdk_string(value) + struct.pack("<iIIIH", 2, count, count, count, len(matrix)) + matrix
        data += struct.pack("<H", 1) + sdk_string("Segment") + struct.pack("<iIIH", 2, 0, count, len(matrix)) + matrix
        data += struct.pack("<IIiH", 0, 1, 1, 2)  # segment flags, zone flags, active mode, mode count
        return data + sdk_mode("Direct", 6) + sdk_mode("Rainbow", 6) + sdk_string("Zone custom name")
    with patch("test_openrgb_sdk.sdk_zone", side_effect=zone_with_modes):
        payload = controller_payload(6, 0, ["112233", "445566"], zone_counts=[2])
    parsed = parse_controller_data(payload, 6)
    assert parsed.zones[0].modes == ("Direct", "Rainbow")
    assert parsed.zones[0].display_name == "Zone custom name"
    assert parsed.zones[0].effective_led_count == 1  # effects-only flag remains authoritative
    assert not parsed.direct_active
    assert replace(parsed, zones=(replace(parsed.zones[0], active_mode=0),)).direct_active
    for truncated in (payload[:-1], payload[:50]):
        with pytest.raises(OpenRGBSDKError):
            parse_controller_data(truncated, 6)
