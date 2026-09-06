#!/usr/bin/env python3
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openrgb_integration import OpenRGBDevice
from rgb_devices import (
    ApplicationInstanceLock,
    RGBGroup,
    RGB_FAN_MODELS,
    RGBSessionLock,
    auto_arrange_layout_slots,
    canonical_device_name,
    configured_zone_sizes,
    fan_zone_plausibility_warning,
    flori_component_zone_defaults,
    flori_rgb_layout_profile,
    infer_layout_position,
    migrate_flori_component_zones,
    normalize_device_aliases,
    normalize_group_assignments,
    normalize_layout_slots,
    normalize_rgb_groups,
    normalize_zone_configurations,
    prepare_openrgb_devices,
    reorder_layout_device_ids,
    rgb_fan_model,
)


class RGBDeviceInventoryTests(unittest.TestCase):
    def test_ene_aliases_are_removed_without_collapsing_two_real_modules(self):
        devices = [
            OpenRGBDevice(0, "ENE DRAM", device_type="DRAM", leds=("0", "1", "2", "3", "4")),
            OpenRGBDevice(1, "ENE DRAM", device_type="DRAM", leds=("0", "1", "2", "3", "4")),
            OpenRGBDevice(6, "ENE DRAM DRAM", device_type="DRAM", leds=("0", "1", "2", "3", "4")),
            OpenRGBDevice(7, "ENE DRAM DRAM", device_type="DRAM", leds=("0", "1", "2", "3", "4")),
        ]
        result = prepare_openrgb_devices(devices)
        self.assertEqual([device.index for device in result.devices], [0, 1])
        self.assertEqual(len(result.stable_ids), 2)
        self.assertEqual(len(set(result.stable_ids)), 2)
        self.assertEqual(len(result.duplicate_aliases_removed), 2)

    def test_equal_real_names_are_not_deduplicated(self):
        devices = [OpenRGBDevice(0, "ENE DRAM", device_type="DRAM"), OpenRGBDevice(1, "ENE DRAM", device_type="DRAM")]
        self.assertEqual(len(prepare_openrgb_devices(devices).devices), 2)
        self.assertEqual(canonical_device_name("ENE DRAM DRAM"), "ene dram")

    def test_duplicate_enumeration_with_same_hardware_path_is_collapsed(self):
        devices = [
            OpenRGBDevice(0, "ENE DRAM", device_type="DRAM", location="I2C /dev/i2c-3 address 0x70"),
            OpenRGBDevice(1, "ENE DRAM", device_type="DRAM", location="I2C /dev/i2c-3 address 0x71"),
            OpenRGBDevice(7, "ENE DRAM", device_type="DRAM", location="I2C /dev/i2c-3 address 0x70"),
            OpenRGBDevice(8, "ENE DRAM", device_type="DRAM", location="I2C /dev/i2c-3 address 0x71"),
        ]
        result = prepare_openrgb_devices(devices)
        self.assertEqual([device.index for device in result.devices], [0, 1])
        self.assertEqual(result.duplicate_aliases_removed, ("7: ENE DRAM", "8: ENE DRAM"))

    def test_complete_mirrored_rc2_inventory_is_collapsed(self):
        names = ["ENE DRAM", "ENE DRAM", "Sapphire GPU", "MSI MYSTIC LIGHT", "DualSense", "NZXT RGB", "Airgoo"]
        first = [OpenRGBDevice(index, name, leds=("LED",)) for index, name in enumerate(names)]
        second = [OpenRGBDevice(index + 7, name, leds=("LED",)) for index, name in enumerate(names)]
        result = prepare_openrgb_devices([*first, *second])
        self.assertEqual([device.index for device in result.devices], list(range(7)))
        self.assertEqual(len(result.duplicate_aliases_removed), 7)

    def test_groups_and_assignments_are_validated(self):
        groups = normalize_rgb_groups([
            {"id": "fans", "name": "  Meine   Lüfter  "},
            {"id": "fans", "name": "duplicate"},
            {"id": "bad group", "name": "GPU"},
        ])
        self.assertEqual(groups, [RGBGroup("fans", "Meine Lüfter"), RGBGroup("bad-group", "GPU")])
        self.assertEqual(normalize_group_assignments({"dev1": "fans", "dev2": "missing"}, groups), {"dev1": "fans"})

    def test_zone_configuration_multiplies_units_and_leds_per_unit(self):
        raw = {
            "openrgb:hub": {
                "Channel A1": {"units": 2, "leds_per_unit": 20},
                "Channel A2": {"units": 1, "leds_per_unit": 20},
                "Unused": {"units": 0, "leds_per_unit": 0},
            }
        }
        clean = normalize_zone_configurations(raw)
        self.assertEqual(
            configured_zone_sizes(
                ("Channel A1", "Channel A2", "Unused"), clean["openrgb:hub"]
            ),
            (40, 20, 0),
        )
        self.assertIsNone(configured_zone_sizes(("Unknown",), clean["openrgb:hub"]))

    def test_interstellar_v2_profiles_use_24_leds_for_normal_and_reverse(self):
        self.assertEqual(len(RGB_FAN_MODELS), 2)
        self.assertEqual({model.leds_per_fan for model in RGB_FAN_MODELS}, {24})
        self.assertEqual(rgb_fan_model("tzmrit-interstellar-v2-normal").airflow, "normal")
        self.assertEqual(rgb_fan_model("tzmrit-interstellar-v2-reverse").airflow, "reverse")
        self.assertIn("ungewöhnlich hoch", fan_zone_plausibility_warning(3, 90))
        self.assertEqual(fan_zone_plausibility_warning(3, 24), "")
        self.assertEqual(
            flori_component_zone_defaults(("Channel A1", "Channel B6", "Channel B7")),
            {"Channel B6": {"units": 1, "leds_per_unit": 24}},
        )
        empty: dict[str, dict[str, int]] = {}
        self.assertFalse(migrate_flori_component_zones(("Channel B6",), empty))
        self.assertEqual(empty, {})
        configured = {
            "Channel A1": {"units": 2, "leds_per_unit": 24},
            "Channel B6": {"units": 1, "leds_per_unit": 30},
        }
        self.assertTrue(migrate_flori_component_zones(("Channel A1", "Channel B6"), configured))
        self.assertEqual(configured["Channel A1"], {"units": 2, "leds_per_unit": 24})
        self.assertEqual(configured["Channel B6"], {"units": 1, "leds_per_unit": 24})

    def test_session_lock_blocks_second_writer(self):
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "rgb.lock"
            first = RGBSessionLock(path)
            second = RGBSessionLock(path)
            self.assertTrue(first.acquire())
            self.assertFalse(second.acquire())
            first.release()
            self.assertTrue(second.acquire())
            second.release()

    def test_application_lock_is_process_scoped_and_records_owner(self):
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "application.lock"
            first = ApplicationInstanceLock(path)
            second = ApplicationInstanceLock(path)
            self.assertTrue(first.acquire())
            self.assertEqual(first.owner_pid, __import__("os").getpid())
            self.assertEqual(path.read_text(encoding="ascii"), str(first.owner_pid))
            self.assertFalse(second.acquire())
            self.assertEqual(second.last_error, "busy")
            self.assertEqual(second.owner_pid, first.owner_pid)
            first.release()
            self.assertTrue(second.acquire())
            second.release()

    def test_layout_and_aliases_are_bounded_and_flori_profile_is_complete(self):
        groups, slots = flori_rgb_layout_profile()
        self.assertEqual({slot.position for slot in slots}, {"top", "front", "side", "bottom", "rear", "gpu", "gpu-support", "ram", "pump"})
        self.assertTrue(any("B7" in slot.connection and "SYS-FAN6" in slot.connection for slot in slots))
        self.assertTrue(any("B6" in slot.connection for slot in slots))
        self.assertTrue(any(slot.position == "side" and slot.count == 3 and slot.airflow == "intake" for slot in slots))
        self.assertEqual(sum(slot.count for slot in slots if slot.position in {"top", "front", "side", "bottom", "rear"}), 12)
        self.assertTrue(any("Netzteilabdeckung vorne" in slot.name and slot.count == 3 for slot in slots))
        radiator = next(slot for slot in slots if slot.slot_id == "radiator-top")
        self.assertEqual(radiator.device_ids, ("nzxt:led2", "nzxt:led3", "nzxt:led1"))
        support = next(slot for slot in slots if slot.slot_id == "gpu-support")
        self.assertIn("24 LEDs", support.name)
        self.assertIn("B6", support.connection)
        _thermalright_groups, thermalright_slots = flori_rgb_layout_profile("thermalright")
        thermalright_radiator = next(slot for slot in thermalright_slots if slot.slot_id == "radiator-top")
        thermalright_pump = next(slot for slot in thermalright_slots if slot.slot_id == "pump")
        self.assertIn("Thermalright Levita Vision 360", thermalright_radiator.name)
        self.assertEqual(thermalright_radiator.device_ids, ())
        self.assertIn("Thermalright Levita Vision 360", thermalright_pump.name)
        self.assertEqual(
            reorder_layout_device_ids(("nzxt:led1", "nzxt:led2", "nzxt:led3"), 0, 2),
            ("nzxt:led2", "nzxt:led3", "nzxt:led1"),
        )
        self.assertEqual(
            reorder_layout_device_ids(radiator.device_ids, 99, -4),
            ("nzxt:led1", "nzxt:led2", "nzxt:led3"),
        )
        restored = normalize_layout_slots([
            {
                "position": slot.position,
                "name": slot.name,
                "count": slot.count,
                "group_id": slot.group_id,
                "connection": slot.connection,
                "device_ids": list(slot.device_ids),
                "slot_id": slot.slot_id,
                "x": slot.x,
                "y": slot.y,
                "airflow": slot.airflow,
                "size_mm": slot.size_mm,
            }
            for slot in slots
        ], groups)
        self.assertEqual(restored, slots)
        self.assertEqual(normalize_device_aliases({"dev": "  GPU   Halterung  "}), {"dev": "GPU Halterung"})
        front = next(slot for slot in slots if slot.slot_id == "fans-front")
        self.assertEqual(infer_layout_position(front, 0.50, 0.80), "bottom")
        gpu = next(slot for slot in slots if slot.slot_id == "gpu")
        self.assertEqual(infer_layout_position(gpu, 0.90, 0.10), "gpu")
        stacked = [
            type(slot)(slot.position, slot.name, slot.count, slot.group_id, slot.connection,
                       slot.device_ids, slot.slot_id, 0.5, 0.5, slot.airflow, slot.size_mm)
            for slot in slots
        ]
        arranged = auto_arrange_layout_slots(stacked)
        self.assertGreater(len({(slot.x, slot.y) for slot in arranged}), 6)


if __name__ == "__main__":
    unittest.main()
