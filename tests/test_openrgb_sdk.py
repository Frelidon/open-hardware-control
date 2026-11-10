#!/usr/bin/env python3
"""Protocol-shape tests for OHC's bounded local OpenRGB SDK writer."""

import socket
import struct
import sys
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openrgb_sdk import (
    OpenRGBPersistentSession,
    OpenRGBSDKError,
    PACKET_REQUEST_CONTROLLER_COUNT,
    PACKET_REQUEST_CONTROLLER_DATA,
    PACKET_RESIZE_ZONE,
    PACKET_SET_CLIENT_NAME,
    PACKET_SET_CUSTOM_MODE,
    PACKET_UPDATE_LEDS,
    PACKET_UPDATE_ZONE_LEDS,
    SDK_HEADER,
    SDK_MAGIC,
    SDKPacket,
    color_payload,
    normalize_colors,
    parse_controller_data,
    process_worker_frame,
    process_worker_frame_parallel,
    receive_packet,
    validate_loopback,
    write_device_colors,
)


def test_stale_zone_request_cannot_reenable_packet_path():
    class Session:
        def write_frame(self, device, count, colors, **kwargs):
            assert "zone_updates" not in kwargs
            return {"ok": True, "device": device, "led_count": count,
                    "prepared": False, "write_path": "device", "protocol": 5}

    response = process_worker_frame(Session(), {"id": 1, "devices": [
        {"key": "gpu", "device": 3, "led_count": 2,
         "colors": ["112233", "445566"], "zone_updates": True}
    ]})
    assert response["ok"] is True
    assert response["devices"][0]["write_path"] == "device"


def test_bad_render_plan_is_contained_to_one_device_and_worker_frame_continues():
    calls = []

    class Session:
        def write_frame(self, device, count, colors, **kwargs):
            calls.append((device, count, colors, kwargs))
            return {"ok": True, "device": device, "led_count": count,
                    "prepared": False, "write_path": "device", "protocol": 5}

    response = process_worker_frame(Session(), {"id": 7, "devices": [
        {"key": "broken-render", "device": 1, "led_count": 2,
         "zone_sizes": [2], "render_plan": {"schema": 999}},
        {"key": "healthy-device", "device": 2, "led_count": 2,
         "colors": ["112233", "445566"]},
    ]})
    assert response["ok"] is False
    assert response["devices"][0]["ok"] is False
    assert response["devices"][1]["ok"] is True
    assert calls == [(2, 2, ["112233", "445566"], {
        "zone_sizes": None, "force_prepare": False,
    })]


def test_parallel_worker_uses_one_session_per_controller_without_serial_delay():
    sessions = {}

    class Session:
        def __init__(self, device):
            self.device = device

        def write_frame(self, device, count, colors, **_kwargs):
            assert device == self.device
            time.sleep(0.08)
            return {"ok": True, "device": device, "led_count": count,
                    "prepared": False, "write_path": "device", "protocol": 6}

    def session_for(device):
        return sessions.setdefault(device, Session(device))

    request = {"id": 9, "devices": [
        {"key": f"device-{device}", "device": device, "led_count": 1, "colors": ["112233"]}
        for device in (1, 2, 3)
    ]}
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=3) as executor:
        response = process_worker_frame_parallel(session_for, executor, request)
    elapsed = time.monotonic() - started
    assert response["ok"] is True
    assert [item["device"] for item in response["devices"]] == [1, 2, 3]
    assert set(sessions) == {1, 2, 3}
    assert elapsed < 0.18


def sdk_string(value: str) -> bytes:
    encoded = value.encode("utf-8") + b"\0"
    return struct.pack("<H", len(encoded)) + encoded


def sdk_mode(value: str, protocol: int) -> bytes:
    data = bytearray(sdk_string(value))
    if protocol < 6:
        data += struct.pack("<i", 0)
    data += struct.pack("<III", 1, 0, 0)
    if protocol >= 3:
        data += struct.pack("<II", 0, 100)
    data += struct.pack("<III", 0, 4096, 0)
    if protocol >= 3:
        data += struct.pack("<I", 100)
    data += struct.pack("<IIH", 0, 2, 0)
    return bytes(data)


def sdk_zone(
    value: str,
    count: int,
    protocol: int,
    minimum: int | None = None,
    maximum: int | None = None,
) -> bytes:
    data = bytearray(sdk_string(value))
    lower = count if minimum is None else minimum
    upper = count if maximum is None else maximum
    data += struct.pack("<iIIIH", 0, lower, upper, count, 0)
    if protocol >= 4:
        data += struct.pack("<H", 0)
    if protocol >= 5:
        data += struct.pack("<I", 0)
    if protocol >= 6:
        data += struct.pack("<iH", -1, 0)
        data += sdk_string(value + " display")
    return bytes(data)


def controller_payload(
    protocol: int,
    active_mode: int,
    colors: list[str],
    zone_counts: list[int] | None = None,
    zone_limits: list[tuple[int, int]] | None = None,
) -> bytes:
    data = bytearray(b"\0\0\0\0")
    data += struct.pack("<i", 0)
    data += sdk_string("Test Controller")
    data += sdk_string("Test Vendor")
    data += sdk_string("Test Description")
    data += sdk_string("1")
    data += sdk_string("")
    data += sdk_string("usb:test")
    data += struct.pack("<Hi", 2, active_mode)
    data += sdk_mode("Direct", protocol)
    data += sdk_mode("Static", protocol)
    counts = zone_counts if zone_counts is not None else [1] * len(colors)
    limits = zone_limits if zone_limits is not None else [(count, count) for count in counts]
    data += struct.pack("<H", len(counts))
    for index, (count, (minimum, maximum)) in enumerate(zip(counts, limits)):
        data += sdk_zone(f"Zone {index + 1}", count, protocol, minimum, maximum)
    data += struct.pack("<H", len(colors))
    for index in range(len(colors)):
        data += sdk_string(f"LED {index + 1}")
        if protocol < 6:
            data += struct.pack("<I", index)
    data += struct.pack("<H", len(colors))
    for color in colors:
        data += struct.pack(
            "<BBBx",
            int(color[0:2], 16),
            int(color[2:4], 16),
            int(color[4:6], 16),
        )
    if protocol >= 5:
        data += struct.pack("<HI", 0, 0)
    if protocol >= 6:
        data += sdk_string("Controller display")
        data += struct.pack("<I", 3) + b"{}\0"
    data[0:4] = struct.pack("<I", len(data))
    return bytes(data)


class OpenRGBSDKTests(unittest.TestCase):
    def test_packet_header_is_the_bounded_openrgb_shape(self):
        packet = SDKPacket(6, PACKET_SET_CUSTOM_MODE, b"").pack()
        self.assertEqual(len(packet), 16)
        self.assertEqual(SDK_HEADER.unpack(packet), (SDK_MAGIC, 6, PACKET_SET_CUSTOM_MODE, 0))

    def test_color_payload_repeats_one_color_for_reported_led_count(self):
        payload = color_payload(["4c00e6"], 2)
        self.assertEqual(struct.unpack("<I", payload[:4])[0], len(payload))
        self.assertEqual(struct.unpack("<H", payload[4:6])[0], 2)
        self.assertEqual(payload[6:], b"\x4c\x00\xe6\x00" * 2)
        packet = SDKPacket(6, PACKET_UPDATE_LEDS, payload).pack()
        self.assertEqual(SDK_HEADER.unpack(packet[:16])[3], len(payload))

    def test_colors_and_endpoint_are_strictly_validated(self):
        self.assertEqual(normalize_colors(["#00AAff"], 3), ("00aaff",) * 3)
        with self.assertRaises(ValueError):
            normalize_colors(["ffffff", "000000"], 3)
        with self.assertRaises(ValueError):
            normalize_colors(["not-rgb"], 1)
        self.assertEqual(validate_loopback("127.0.0.1"), "127.0.0.1")
        self.assertEqual(validate_loopback("::1"), "::1")
        with self.assertRaises(ValueError):
            validate_loopback("192.0.2.1")

    def test_protocol_5_controller_description_exposes_direct_zones_and_colors(self):
        parsed = parse_controller_data(controller_payload(5, 1, ["000000", "102030"]), 5)
        self.assertEqual(parsed.name, "Test Controller")
        self.assertEqual(parsed.active_mode_name, "Static")
        self.assertTrue(parsed.supports_direct)
        self.assertEqual([zone.led_count for zone in parsed.zones], [1, 1])
        self.assertEqual(parsed.colors, ("000000", "102030"))

    def test_protocol_5_controller_description_keeps_empty_resizable_zones(self):
        parsed = parse_controller_data(
            controller_payload(5, 1, [], [0, 0], [(0, 255), (0, 255)]),
            5,
        )
        self.assertEqual(parsed.colors, ())
        self.assertEqual([zone.led_count for zone in parsed.zones], [0, 0])
        self.assertTrue(all(zone.resizable for zone in parsed.zones))

    def test_empty_hub_zones_are_resized_before_direct_color_write(self):
        received = []
        errors = []
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]

        def serve() -> None:
            try:
                with listener:
                    connection, _address = listener.accept()
                    with connection:
                        packet = receive_packet(connection)
                        received.append(packet)
                        connection.sendall(SDKPacket(0, 40, struct.pack("<I", 5)).pack())
                        received.append(receive_packet(connection))  # client name
                        received.append(receive_packet(connection))  # controller count
                        connection.sendall(
                            SDKPacket(0, PACKET_REQUEST_CONTROLLER_COUNT, struct.pack("<I", 7)).pack()
                        )
                        received.append(receive_packet(connection))  # initial data request
                        connection.sendall(
                            SDKPacket(
                                6,
                                PACKET_REQUEST_CONTROLLER_DATA,
                                controller_payload(5, 1, [], [0, 0], [(0, 255), (0, 255)]),
                            ).pack()
                        )
                        for expected_index, expected_size in ((0, 2), (1, 1)):
                            packet = receive_packet(connection)
                            received.append(packet)
                            self.assertEqual(packet.packet_type, PACKET_RESIZE_ZONE)
                            self.assertEqual(struct.unpack("<ii", packet.payload), (expected_index, expected_size))
                        received.append(receive_packet(connection))  # resized data request
                        colors = ["000000"] * 3
                        connection.sendall(
                            SDKPacket(
                                6,
                                PACKET_REQUEST_CONTROLLER_DATA,
                                controller_payload(5, 1, colors, [2, 1], [(0, 255), (0, 255)]),
                            ).pack()
                        )
                        received.append(receive_packet(connection))  # set custom
                        received.append(receive_packet(connection))  # direct data request
                        connection.sendall(
                            SDKPacket(
                                6,
                                PACKET_REQUEST_CONTROLLER_DATA,
                                controller_payload(5, 0, colors, [2, 1], [(0, 255), (0, 255)]),
                            ).pack()
                        )
                        packet = receive_packet(connection)
                        received.append(packet)
                        self.assertEqual(packet.packet_type, PACKET_UPDATE_LEDS)
                        for offset in range(3):
                            red, green, blue, _padding = struct.unpack(
                                "<BBBB", packet.payload[6 + offset * 4:10 + offset * 4]
                            )
                            colors[offset] = f"{red:02x}{green:02x}{blue:02x}"
                        for expected_zone, zone_count in ((0, 2), (1, 1)):
                            packet = receive_packet(connection)
                            received.append(packet)
                            self.assertEqual(packet.packet_type, PACKET_UPDATE_ZONE_LEDS)
                            self.assertEqual(struct.unpack("<I", packet.payload[4:8])[0], expected_zone)
                            for offset in range(zone_count):
                                red, green, blue, _padding = struct.unpack(
                                    "<BBBB", packet.payload[10 + offset * 4:14 + offset * 4]
                                )
                                colors[sum((2, 1)[:expected_zone]) + offset] = f"{red:02x}{green:02x}{blue:02x}"
                        received.append(receive_packet(connection))  # confirmation request
                        connection.sendall(
                            SDKPacket(
                                6,
                                PACKET_REQUEST_CONTROLLER_DATA,
                                controller_payload(5, 0, colors, [2, 1], [(0, 255), (0, 255)]),
                            ).pack()
                        )
            except BaseException as exc:
                errors.append(exc)

        server = threading.Thread(target=serve, daemon=True)
        server.start()
        try:
            result = write_device_colors(
                "127.0.0.1", port, 6, 3, ["4c00e6"], zone_sizes=(2, 1)
            )
        finally:
            server.join(timeout=2)
            self.assertFalse(server.is_alive())
        if errors:
            raise errors[0]
        self.assertEqual(result.led_count, 3)
        self.assertEqual(result.zone_count, 2)
        self.assertEqual(
            [packet.packet_type for packet in received],
            [40, 50, 0, 1, 1000, 1000, 1, 1100, 1, 1050, 1051, 1051, 1],
        )

    def run_local_transaction(
        self,
        server_version: int,
        *,
        expect_writes: bool = True,
        set_custom_mode: bool = True,
        max_protocol: int = 5,
    ):
        received = []
        errors = []
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]

        def serve() -> None:
            try:
                with listener:
                    connection, _address = listener.accept()
                    with connection:
                        packet = receive_packet(connection)
                        received.append(packet)
                        connection.sendall(SDKPacket(0, 40, struct.pack("<I", server_version)).pack())
                        if not expect_writes:
                            return
                        protocol = min(server_version, struct.unpack("<I", packet.payload)[0])
                        wire_device = 0xF0010234 if protocol >= 6 else 6
                        def acknowledge(request):
                            if protocol >= 6:
                                connection.sendall(SDKPacket(request.device_id, 10, struct.pack("<II", request.packet_type, 0)).pack())
                        active_mode = 1 if set_custom_mode else 0
                        colors = ["000000", "000000"]

                        packet = receive_packet(connection)
                        received.append(packet)
                        self.assertEqual(packet.packet_type, PACKET_SET_CLIENT_NAME)
                        acknowledge(packet)

                        packet = receive_packet(connection)
                        received.append(packet)
                        self.assertEqual(packet.packet_type, PACKET_REQUEST_CONTROLLER_COUNT)
                        connection.sendall(
                            SDKPacket(0, PACKET_REQUEST_CONTROLLER_COUNT, struct.pack("<I", 7)
                                      + (struct.pack("<7I", 10, 11, 12, 13, 14, 15, wire_device) if protocol >= 6 else b"")).pack()
                        )
                        acknowledge(packet)

                        packet = receive_packet(connection)
                        received.append(packet)
                        self.assertEqual(packet.packet_type, PACKET_REQUEST_CONTROLLER_DATA)
                        self.assertEqual(packet.device_id, wire_device)
                        connection.sendall(
                            SDKPacket(wire_device, PACKET_REQUEST_CONTROLLER_DATA, controller_payload(protocol, active_mode, colors)).pack()
                        )
                        acknowledge(packet)

                        if set_custom_mode:
                            packet = receive_packet(connection)
                            received.append(packet)
                            self.assertEqual(packet.packet_type, PACKET_SET_CUSTOM_MODE)
                            active_mode = 0
                            acknowledge(packet)

                            packet = receive_packet(connection)
                            received.append(packet)
                            self.assertEqual(packet.packet_type, PACKET_REQUEST_CONTROLLER_DATA)
                            connection.sendall(
                                SDKPacket(wire_device, PACKET_REQUEST_CONTROLLER_DATA, controller_payload(protocol, active_mode, colors)).pack()
                            )
                            acknowledge(packet)

                        packet = receive_packet(connection)
                        received.append(packet)
                        self.assertEqual(packet.packet_type, PACKET_UPDATE_LEDS)
                        for offset in range(2):
                            red, green, blue, _padding = struct.unpack(
                                "<BBBB", packet.payload[6 + offset * 4:10 + offset * 4]
                            )
                            colors[offset] = f"{red:02x}{green:02x}{blue:02x}"
                        acknowledge(packet)

                        if set_custom_mode:
                            for expected_zone in range(2):
                                packet = receive_packet(connection)
                                received.append(packet)
                                self.assertEqual(packet.packet_type, PACKET_UPDATE_ZONE_LEDS)
                                self.assertEqual(struct.unpack("<I", packet.payload[4:8])[0], expected_zone)
                                red, green, blue, _padding = struct.unpack("<BBBB", packet.payload[10:14])
                                colors[expected_zone] = f"{red:02x}{green:02x}{blue:02x}"
                                acknowledge(packet)

                        packet = receive_packet(connection)
                        received.append(packet)
                        self.assertEqual(packet.packet_type, PACKET_REQUEST_CONTROLLER_DATA)
                        connection.sendall(
                            SDKPacket(wire_device, PACKET_REQUEST_CONTROLLER_DATA, controller_payload(protocol, active_mode, colors)).pack()
                        )
                        acknowledge(packet)
            except BaseException as exc:  # propagate thread failures to the test
                errors.append(exc)

        server = threading.Thread(target=serve, daemon=True)
        server.start()
        try:
            result = write_device_colors(
                "127.0.0.1",
                port,
                6,
                2,
                ["4c00e6", "102030"],
                set_custom_mode=set_custom_mode,
                max_protocol=max_protocol,
            )
        finally:
            server.join(timeout=2)
            self.assertFalse(server.is_alive())
        if errors:
            raise errors[0]
        return received, result

    def test_complete_local_transaction_accepts_protocol_5_and_confirms_zone_writes(self):
        received, result = self.run_local_transaction(5)
        self.assertEqual(
            [packet.packet_type for packet in received],
            [40, 50, 0, 1, 1100, 1, 1050, 1051, 1051, 1],
        )
        self.assertEqual(struct.unpack("<I", received[0].payload)[0], 5)
        self.assertEqual(result.write_path, "device+zones")
        self.assertEqual(result.zone_count, 2)

    def test_protocol_6_server_negotiates_legacy_protocol_5(self):
        received, result = self.run_local_transaction(6)
        self.assertEqual(struct.unpack("<I", received[0].payload)[0], 5)
        self.assertEqual(result.protocol_version, 5)
        self.assertEqual(result.write_path, "device+zones")

    def test_complete_local_transaction_remains_compatible_with_protocol_4(self):
        received, result = self.run_local_transaction(4)
        self.assertEqual(received[-1].packet_type, PACKET_REQUEST_CONTROLLER_DATA)
        self.assertEqual(result.protocol_version, 4)

    def test_explicit_protocol_6_opt_in_maps_uuid_and_confirms_write_acks(self):
        received, result = self.run_local_transaction(6, max_protocol=6)
        self.assertEqual(struct.unpack("<I", received[0].payload)[0], 6)
        self.assertEqual(result.protocol_version, 6)
        self.assertEqual(result.device_id, 6)  # OHC still reports its inventory index
        self.assertEqual(result.write_path, "device+zones")
        self.assertTrue(all(packet.device_id == 0xF0010234 for packet in received
                            if packet.packet_type in {1, 1100, 1050, 1051}))

    def test_followup_frame_updates_whole_device_without_repeating_zone_fallback(self):
        received, result = self.run_local_transaction(5, set_custom_mode=False)
        self.assertEqual(
            [packet.packet_type for packet in received],
            [40, 50, 0, 1, 1050, 1],
        )
        self.assertEqual(result.write_path, "device")
        self.assertFalse(result.custom_mode_changed)

    def test_protocol_older_than_supported_range_is_rejected_before_writing(self):
        with self.assertRaisesRegex(OpenRGBSDKError, "mindestens erforderlich ist 4"):
            self.run_local_transaction(3, expect_writes=False)

    def test_persistent_session_reuses_one_connection_and_only_prepares_once(self):
        received = []
        errors = []
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]

        def serve() -> None:
            try:
                with listener:
                    connection, _address = listener.accept()
                    with connection:
                        packet = receive_packet(connection)
                        received.append(packet)
                        connection.sendall(SDKPacket(0, 40, struct.pack("<I", 5)).pack())
                        received.append(receive_packet(connection))  # client name
                        received.append(receive_packet(connection))  # controller count
                        connection.sendall(
                            SDKPacket(0, PACKET_REQUEST_CONTROLLER_COUNT, struct.pack("<I", 7)).pack()
                        )
                        colors = ["000000", "000000"]
                        received.append(receive_packet(connection))  # controller data
                        connection.sendall(
                            SDKPacket(6, PACKET_REQUEST_CONTROLLER_DATA, controller_payload(5, 1, colors)).pack()
                        )
                        received.append(receive_packet(connection))  # custom mode
                        received.append(receive_packet(connection))  # controller data
                        connection.sendall(
                            SDKPacket(6, PACKET_REQUEST_CONTROLLER_DATA, controller_payload(5, 0, colors)).pack()
                        )
                        first = receive_packet(connection)
                        received.append(first)
                        for offset in range(2):
                            red, green, blue, _padding = struct.unpack(
                                "<BBBB", first.payload[6 + offset * 4:10 + offset * 4]
                            )
                            colors[offset] = f"{red:02x}{green:02x}{blue:02x}"
                        received.append(receive_packet(connection))  # zone 1
                        received.append(receive_packet(connection))  # zone 2
                        received.append(receive_packet(connection))  # confirmation data
                        connection.sendall(
                            SDKPacket(6, PACKET_REQUEST_CONTROLLER_DATA, controller_payload(5, 0, colors)).pack()
                        )
                        received.append(receive_packet(connection))  # second frame, device path
                        received.append(receive_packet(connection))  # third frame, device path
            except BaseException as exc:
                errors.append(exc)

        server = threading.Thread(target=serve, daemon=True)
        server.start()
        session = OpenRGBPersistentSession("127.0.0.1", port)
        try:
            first = session.write_frame(6, 2, ["102030", "405060"])
            second = session.write_frame(6, 2, ["a0b0c0", "d0e0f0"])
            third = session.write_frame(6, 2, ["010203", "040506"])
        finally:
            session.close()
            server.join(timeout=2)
            self.assertFalse(server.is_alive())
        if errors:
            raise errors[0]
        self.assertTrue(first["prepared"])
        self.assertFalse(second["prepared"])
        self.assertEqual(second["write_path"], "device")
        self.assertEqual(third["write_path"], "device")
        self.assertEqual(
            [packet.packet_type for packet in received],
            [40, 50, 0, 1, 1100, 1, 1050, 1051, 1051, 1, 1050, 1050],
        )


if __name__ == "__main__":
    unittest.main()
