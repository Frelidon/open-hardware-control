#!/usr/bin/env python3
"""Tests for persistent, user-reorderable page and dashboard layouts."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ui_layout import DASHBOARD_CARD_DEFAULTS, SECTION_DEFAULTS, sanitize_dashboard_cards, sanitize_section_order


class UILayoutTests(unittest.TestCase):
    def test_rgb_default_order_matches_product_request(self):
        self.assertEqual(
            SECTION_DEFAULTS["rgb"],
            ("engine", "devices_effects", "pc_layout", "groups"),
        )

    def test_saved_order_is_sanitized_and_completed(self):
        self.assertEqual(
            sanitize_section_order("rgb", ["groups", "engine", "groups", "removed"]),
            ["groups", "engine", "devices_effects", "pc_layout"],
        )
        self.assertEqual(sanitize_section_order("cooling", None), list(SECTION_DEFAULTS["cooling"]))

    def test_dashboard_visibility_preserves_an_explicit_empty_selection(self):
        self.assertEqual(sanitize_dashboard_cards(None), list(DASHBOARD_CARD_DEFAULTS))
        self.assertEqual(sanitize_dashboard_cards([]), [])
        self.assertEqual(
            sanitize_dashboard_cards(["gpu_model", "gpu_model", "unknown", "cpu_model"]),
            ["gpu_model", "cpu_model"],
        )


if __name__ == "__main__":
    unittest.main()
