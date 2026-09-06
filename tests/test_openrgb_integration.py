#!/usr/bin/env python3
"""Tests for the loopback-only OpenRGB SDK/CLI adapter."""

import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openrgb_integration import (
    OpenRGBClient,
    OpenRGBDevice,
    best_native_mode_for_effect,
    is_suspicious_inventory_drop,
    is_confirmed_small_inventory_shrink,
    is_openrgb_apply_options_crash,
    is_openrgb_configuration_error,
    openrgb_subprocess_environment,
    parse_device_listing,
    preferred_reset_mode,
    running_openrgb_process_ids,
    running_ckb_next_process_ids,
)


LISTING = """
Attempting to connect to local OpenRGB server.
Connected to server
0: Example RGB Fan Hub
  Type: LED Strip
  Description: Example Controller
  Version: 1.2.3
  Location: HID: /dev/hidraw9
  Serial: SAFE123
  Modes: [Direct] Static Breathing 'Rainbow Wave'
  Zones: 'Fan 1' 'Fan 2'
  LEDs: 'LED 1' 'LED 2' 'LED 3' 'LED 4'
1: Example Keyboard
  Type: Keyboard
  Modes: Direct Static
  Zones: Keyboard
  LEDs: Key_A Key_B
"""


class OpenRGBIntegrationTests(unittest.TestCase):
    def test_every_direct_openrgb_process_is_forced_offscreen(self):
        environment = openrgb_subprocess_environment({"DISPLAY": ":0", "QT_QPA_PLATFORM": "xcb"})
        self.assertEqual(environment["DISPLAY"], ":0")
        self.assertEqual(environment["QT_QPA_PLATFORM"], "offscreen")

    def test_listing_parser_preserves_device_capabilities(self):
        devices = parse_device_listing(LISTING)
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0].name, "Example RGB Fan Hub")
        self.assertEqual(devices[0].device_type, "LED Strip")
        self.assertEqual(devices[0].led_count, 4)
        self.assertEqual(devices[0].reported_led_count, 4)
        self.assertEqual(devices[0].zones, ("Fan 1", "Fan 2"))
        self.assertIn("Rainbow Wave", devices[0].modes)
        self.assertTrue(devices[0].supports_direct)

    def test_non_loopback_addresses_are_rejected(self):
        with self.assertRaises(ValueError):
            OpenRGBClient(address="192.0.2.4")

    def test_commands_are_explicit_clients_and_validated(self):
        with tempfile.TemporaryDirectory() as temp_name:
            executable = Path(temp_name) / "openrgb"
            executable.touch()
            client = OpenRGBClient(str(executable))
            with patch.object(client, "server_reachable", return_value=True):
                command = client.color_command(3, ["00aaff", "ffffff"], direct=True)
                self.assertEqual(command[1:3], ["--client", "127.0.0.1:6742"])
                self.assertEqual(command[-2:], ["--color", "00aaff,ffffff"])
                self.assertIn("direct", command)
                native = client.native_mode_command(3, "Rainbow Wave", ["112233"], 72)
                self.assertIn("Rainbow Wave", native)
                self.assertEqual(native[-1], "72")
                with self.assertRaises(ValueError):
                    client.color_command(3, ["not-a-color"])
                with self.assertRaises(ValueError):
                    client.native_mode_command(3, "bad;mode", ["ffffff"])
                sdk = client.sdk_color_command(3, ["00aaff"], 24, zone_sizes=(16, 8))
                self.assertEqual(Path(sdk[1]).name, "openrgb_sdk.py")
                self.assertEqual(sdk[sdk.index("--device") + 1], "3")
                self.assertEqual(sdk[sdk.index("--led-count") + 1], "24")
                self.assertNotIn("--no-custom-mode", sdk)
                self.assertEqual(sdk[sdk.index("--zone-sizes") + 1], "16,8")
                inspect = client.sdk_inspect_command(3)
                self.assertIn("--inspect", inspect)
                self.assertNotIn("--colors", inspect)

    def test_managed_server_and_device_commands_are_serialized(self):
        with tempfile.TemporaryDirectory() as temp_name:
            executable = Path(temp_name) / "openrgb"
            executable.touch()
            config = Path(temp_name) / "private-config"
            client = OpenRGBClient(str(executable))
            server = client.managed_server_command(config)
            self.assertIn("--server", server)
            self.assertIn("--noautoconnect", server)
            self.assertIn(str(config), server)
            with patch.object(client, "server_reachable", return_value=True):
                commands = client.color_commands([(1, ["112233"]), (7, ["abcdef", "000000"])], direct=True)
                self.assertEqual(len(commands), 2)
                self.assertTrue(all(command.count("--device") == 1 for command in commands))
                self.assertTrue(all(command.count("--mode") == 1 for command in commands))
                with self.assertRaises(ValueError):
                    client.multi_color_command([(1, ["112233"]), (7, ["abcdef"])], direct=True)
                with self.assertRaises(ValueError):
                    client.color_commands([(1, ["112233"]), (1, ["abcdef"])])
                sdk_commands = client.sdk_color_commands([
                    (1, ["112233"], 8), (7, ["abcdef"], 16)
                ])
                self.assertEqual(len(sdk_commands), 2)
                self.assertTrue(all("openrgb_sdk.py" in command[1] for command in sdk_commands))

    def test_reset_mode_is_only_selected_from_reported_modes(self):
        device = OpenRGBDevice(1, "Demo", modes=("Direct", "Hardware", "Static"))
        self.assertEqual(preferred_reset_mode(device), "Hardware")
        self.assertEqual(preferred_reset_mode(OpenRGBDevice(2, "Demo", modes=("Direct",))), "")

    def test_native_fallback_uses_selected_or_matching_reported_mode(self):
        device = OpenRGBDevice(3, "GPU", modes=("Static", "Random Flicker", "Rainbow Wave"))
        self.assertEqual(best_native_mode_for_effect(device, "lightning"), "Random Flicker")
        self.assertEqual(best_native_mode_for_effect(device, "rainbow"), "Rainbow Wave")
        self.assertEqual(best_native_mode_for_effect(device, "rainbow", "Random Flicker"), "Random Flicker")

    def test_fedora_rc2_apply_options_assertion_is_recognized(self):
        detail = (
            "/usr/include/c++/16/bits/stl_vector.h:1253: "
            "std::vector<unsigned int>::operator[](size_type): "
            "Assertion '__n < this->size()' failed.\n"
            "ApplyOptions"
        )
        self.assertTrue(is_openrgb_apply_options_crash(6, detail))
        self.assertTrue(is_openrgb_apply_options_crash(134, detail))
        self.assertTrue(is_openrgb_apply_options_crash(-6, detail.splitlines()[0]))
        self.assertFalse(is_openrgb_apply_options_crash(0, detail))
        self.assertFalse(is_openrgb_apply_options_crash(1, "Connection refused"))
        self.assertFalse(is_openrgb_apply_options_crash(1, "ApplyOptions returned an ordinary error"))

    def test_running_openrgb_processes_are_detected_without_matching_other_names(self):
        with tempfile.TemporaryDirectory() as temp_name:
            proc_root = Path(temp_name)
            for pid, name in (("41", "OpenRGB\n"), ("42", "openrgb\n"), ("43", "openrgb-helper\n")):
                process = proc_root / pid
                process.mkdir()
                (process / "comm").write_text(name, encoding="utf-8")
            (proc_root / "self").mkdir()
            self.assertEqual(running_openrgb_process_ids(proc_root), (41, 42))

    def test_ckb_next_processes_and_safe_configuration_errors_are_detected(self):
        with tempfile.TemporaryDirectory() as temp_name:
            proc_root = Path(temp_name)
            for pid, name in (("51", "ckb-next\n"), ("52", "ckb-next-daemon\n"), ("53", "ckb-helper\n")):
                process = proc_root / pid
                process.mkdir()
                (process / "comm").write_text(name, encoding="utf-8")
            self.assertEqual(running_ckb_next_process_ids(proc_root), (51, 52))
        self.assertTrue(is_openrgb_configuration_error("KONFIGURATION_ERFORDERLICH: 0 LEDs"))
        self.assertTrue(is_openrgb_configuration_error("Zonengrößen nicht bestätigt"))
        self.assertFalse(is_openrgb_configuration_error("USB write failed"))

    def test_large_temporary_inventory_drop_is_retried_but_hotplug_is_not(self):
        self.assertTrue(is_suspicious_inventory_drop(7, 7, 2))
        self.assertTrue(is_suspicious_inventory_drop(0, 7, 2))
        self.assertTrue(is_suspicious_inventory_drop(8, 8, 3))
        self.assertFalse(is_suspicious_inventory_drop(7, 7, 5))
        self.assertFalse(is_suspicious_inventory_drop(2, 2, 1))
        self.assertFalse(is_suspicious_inventory_drop(7, 7, 7))
        self.assertFalse(is_confirmed_small_inventory_shrink(7, 6, 2.49))
        self.assertTrue(is_confirmed_small_inventory_shrink(7, 6, 2.5))
        self.assertTrue(is_confirmed_small_inventory_shrink(7, 5, 4.0))
        self.assertFalse(is_confirmed_small_inventory_shrink(7, 2, 10.0))


if __name__ == "__main__":
    unittest.main()
