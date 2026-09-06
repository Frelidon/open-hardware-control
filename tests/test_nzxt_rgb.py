#!/usr/bin/env python3
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from nzxt_rgb import (
    NZXT_EFFECTS,
    build_nzxt_effect_arguments,
    closest_nzxt_mode,
    coalesce_selected_channels,
    effect_channels,
)


class NZXTRGBTests(unittest.TestCase):
    def test_wings_sync_is_applied_per_physical_fan_channel(self):
        commands = build_nzxt_effect_arguments(["liquidctl"], "sync", "wings", ["55007f"], "normal")
        self.assertEqual(len(commands), 3)
        self.assertEqual([command[2] for command in commands], ["led1", "led2", "led3"])
        self.assertTrue(all("--direction" not in command for command in commands))

    def test_non_topology_sensitive_effect_keeps_sync(self):
        commands = build_nzxt_effect_arguments(["liquidctl"], "sync", "rainbow-flow", [], "faster", "backward")
        self.assertEqual(len(commands), 1)
        self.assertIn("sync", commands[0])
        self.assertEqual(commands[0][-2:], ["--direction", "backward"])

    def test_all_selected_channels_use_the_proven_sync_route(self):
        self.assertEqual(coalesce_selected_channels(["led3", "led1", "led2"]), ("sync",))
        self.assertEqual(coalesce_selected_channels(["led2", "led1"]), ("led1", "led2"))

    def test_validation_and_effect_mapping(self):
        self.assertNotIn("alternating-4", {effect.mode for effect in NZXT_EFFECTS})
        self.assertEqual(closest_nzxt_mode("alternating"), "fading")
        self.assertEqual(closest_nzxt_mode("sparkle"), "starry-night")
        self.assertEqual(closest_nzxt_mode("comet"), "pulse")
        self.assertEqual(closest_nzxt_mode("spinner"), "rainbow-flow")
        with self.assertRaises(ValueError):
            build_nzxt_effect_arguments(["liquidctl"], "led9", "fixed", ["ffffff"])
        with self.assertRaises(ValueError):
            build_nzxt_effect_arguments(["liquidctl"], "led1", "wings", [])


if __name__ == "__main__":
    unittest.main()
