#!/usr/bin/env python3
"""Tests for the original Open Hardware Control RGB effect engine."""

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rgb_effects import BUILTIN_DESIGN_CATEGORIES, BUILTIN_DESIGNS, EFFECTS, RGBEffectConfig, effect_color_count, normalize_hex, render_effect, render_hex_frame


class RGBEffectTests(unittest.TestCase):
    def test_every_effect_renders_bounded_rgb_frames(self):
        for effect in EFFECTS:
            config = RGBEffectConfig(effect.effect_id, "1020ff", "ffeedd", 83, 117, -1)
            frame = render_effect(config, 27, 1.375)
            self.assertEqual(len(frame), 27, effect.effect_id)
            self.assertTrue(all(0 <= channel <= 255 for color in frame for channel in color))
            self.assertEqual(frame, render_effect(config, 27, 1.375), effect.effect_id)

    def test_brightness_and_count_are_clamped(self):
        dark = render_effect(RGBEffectConfig("rainbow", brightness=0), 0, 2.0)
        self.assertEqual(dark, [(0, 0, 0)])
        self.assertEqual(len(render_hex_frame(RGBEffectConfig(), 5000, 0.0)), 4096)

    def test_invalid_values_are_rejected_or_normalized(self):
        with self.assertRaises(ValueError):
            normalize_hex("#xyz")
        config = RGBEffectConfig("unknown", brightness=500, speed=0, direction=0).normalized()
        self.assertEqual(config.effect_id, "static")
        self.assertEqual(config.brightness, 100)
        self.assertEqual(config.speed, 10)
        self.assertEqual(config.direction, 1)

    def test_builtin_designs_reference_known_effects(self):
        known = {effect.effect_id for effect in EFFECTS}
        self.assertGreaterEqual(len(BUILTIN_DESIGNS), 18)
        self.assertEqual(len(BUILTIN_DESIGN_CATEGORIES), len(BUILTIN_DESIGNS))
        self.assertGreaterEqual(len(set(BUILTIN_DESIGN_CATEGORIES)), 5)
        self.assertTrue(all(config.effect_id in known for _title, config in BUILTIN_DESIGNS))
        self.assertEqual(BUILTIN_DESIGNS[0][0], "Feste Farbe")
        self.assertEqual(BUILTIN_DESIGNS[0][1].effect_id, "static")

    def test_modes_expose_only_meaningful_color_fields(self):
        self.assertEqual(effect_color_count("rainbow"), 0)
        self.assertEqual(effect_color_count("static"), 1)
        self.assertEqual(effect_color_count("breathing"), 1)
        for effect_id in ("lightning", "spinner", "comet", "wave", "pulse", "alternating", "sparkle"):
            self.assertEqual(effect_color_count(effect_id), 2, effect_id)


if __name__ == "__main__":
    unittest.main()
