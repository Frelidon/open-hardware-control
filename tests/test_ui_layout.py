#!/usr/bin/env python3
"""Tests for persistent, user-reorderable page and dashboard layouts."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ui_layout import (
    DASHBOARD_CARD_DEFAULTS,
    SECTION_DEFAULTS,
    dashboard_card_hardware_available,
    sanitize_dashboard_cards,
    sanitize_section_order,
)
from dashboard_layout import (
    DASHBOARD_HINT_FAULT,
    DASHBOARD_HINT_OK,
    dashboard_status_hints,
)


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

    def test_water_temperature_requires_a_connected_kraken_and_real_value(self):
        self.assertFalse(
            dashboard_card_hardware_available(
                "water_temperature", kraken_connected=False, liquid_temperature=None
            )
        )
        self.assertFalse(
            dashboard_card_hardware_available(
                "water_temperature", kraken_connected=True, liquid_temperature=None
            )
        )
        self.assertTrue(
            dashboard_card_hardware_available(
                "water_temperature", kraken_connected=True, liquid_temperature=31.5
            )
        )
        self.assertTrue(
            dashboard_card_hardware_available(
                "cpu_temperature", kraken_connected=False, liquid_temperature=None
            )
        )

    def test_levita_overview_hints_switch_after_confirmed_pwm_tests(self):
        pending = dashboard_status_hints(
            thermalright=True,
            cooling_ready=False,
            kraken_connected=False,
            sensors_ok=True,
        )
        cooling = pending[0]
        self.assertEqual(cooling.key, "cooling")
        self.assertEqual(cooling.title, "Levita erkannt")
        self.assertIn("PWM-Tests", cooling.detail)
        self.assertFalse(cooling.ok)
        self.assertEqual(cooling.badge_text, DASHBOARD_HINT_FAULT)
        self.assertEqual(cooling.object_name, "healthCritical")

        ready = dashboard_status_hints(
            thermalright=True,
            cooling_ready=True,
            kraken_connected=False,
            sensors_ok=True,
        )
        cooling = ready[0]
        self.assertEqual(cooling.title, "Levita-Kühlung bestätigt")
        self.assertIn("steuerbar", cooling.detail)
        self.assertTrue(cooling.ok)
        self.assertEqual(cooling.badge_text, DASHBOARD_HINT_OK)
        self.assertEqual(cooling.object_name, "healthGood")
        self.assertTrue(all(row.ok for row in ready))
        self.assertEqual([row.badge_text for row in ready], [DASHBOARD_HINT_OK] * 4)

    def test_overview_hints_use_fault_badge_when_sensors_fail(self):
        rows = {row.key: row for row in dashboard_status_hints(
            thermalright=True,
            cooling_ready=True,
            kraken_connected=False,
            sensors_ok=False,
        )}
        self.assertTrue(rows["cooling"].ok)
        self.assertFalse(rows["sensors"].ok)
        self.assertEqual(rows["sensors"].badge_text, DASHBOARD_HINT_FAULT)
        self.assertTrue(rows["profiles"].ok)
        self.assertTrue(rows["privacy"].ok)


if __name__ == "__main__":
    unittest.main()
