#!/usr/bin/env python3
"""Regression guards for CPU startup defaults and complete PC PWM profiles."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from modules.cooling_state.v1_0.cpu_defaults import (  # noqa: E402
    AUTO_ORIGIN, USER_ORIGIN, infer_origin, should_load_detected_defaults,
)
from modules.pc_case_profiles.v1_5.case_page import slot_supports_pwm  # noqa: E402
from rgb_devices import RGBLayoutSlot  # noqa: E402


def test_cpu_defaults_load_only_until_the_user_owns_the_curve() -> None:
    pump = [(30, 50), (90, 100)]
    fan = [(30, 25), (90, 100)]
    assert infer_origin("", pump, fan, pump, fan) == AUTO_ORIGIN
    assert infer_origin("", [(30, 55), (90, 100)], fan, pump, fan) == USER_ORIGIN
    assert should_load_detected_defaults(True, AUTO_ORIGIN)
    assert not should_load_detected_defaults(True, USER_ORIGIN)
    assert not should_load_detected_defaults(False, AUTO_ORIGIN)


def test_case_mapper_accepts_radiator_and_pump_positions() -> None:
    radiator = RGBLayoutSlot("top", "Radiator", 3, "cooling", slot_id="radiator-top", size_mm=120)
    pump = RGBLayoutSlot("pump", "Pumpenkopf", 1, "cooling", slot_id="pump", size_mm=0)
    decorative = RGBLayoutSlot("gpu", "Grafikkarte", 1, "hardware", slot_id="gpu", size_mm=0)
    assert slot_supports_pwm(radiator)
    assert slot_supports_pwm(pump)
    assert not slot_supports_pwm(decorative)


def test_main_window_places_cpu_automation_below_ownership_and_persists_policy() -> None:
    code = (SRC / "kraken_control.py").read_text(encoding="utf-8")
    ownership = code.index('ownership_box = QGroupBox("Steuerungsbesitz · Konfliktschutz")')
    cpu_position = code.index("mb_layout.addWidget(cpu_box)", ownership)
    assistant = code.index("mb_layout.addWidget(fan_auth_box)", ownership)
    assert ownership < cpu_position < assistant
    assert "mb_layout.addWidget(ownership_box)\n        mb_layout.addWidget(cpu_box)" in code
    assert 'self.settings.setValue("cpu/auto_detect_curves", self.cpu_curve_auto_detect_enabled)' in code
    assert 'self.settings.setValue("cpu/curve_origin", self.cpu_curve_origin)' in code
    assert "self.detect_and_select_cpu(silent=True)" in code


def test_case_profile_controller_keeps_cpu_and_pump_connectors_settings_only() -> None:
    controller = (SRC / "modules/pc_case_profiles/v1_5/controller.py").read_text(encoding="utf-8")
    page = (SRC / "modules/pc_case_profiles/v1_5/case_page.py").read_text(encoding="utf-8")
    assert "def case_mappable_mainboard_channels" in controller
    assert '"CPU Fan": "radiator-top"' in controller
    assert '"Pump Fan": "pump"' in controller
    assert "sync_selected_rgb_case_profile_pwm_assignments" in controller
    assert "set_mainboard_channel_percent" not in controller
    assert "host.case_mappable_mainboard_channels()" in page
    assert "host.sync_selected_rgb_case_profile_pwm_assignments()" in page
