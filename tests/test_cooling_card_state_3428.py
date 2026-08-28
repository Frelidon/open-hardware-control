#!/usr/bin/env python3
"""Regression tests for collapsed/single-expanded chassis-fan cards."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cooling_card_state import normalize_expanded_channel, toggle_expanded_channel


channels = ("hwmon5:pwm2", "hwmon5:pwm3", "hwmon5:pwm4")

assert normalize_expanded_channel("", channels) == ""
assert normalize_expanded_channel("hwmon5:pwm3", channels) == "hwmon5:pwm3"
assert normalize_expanded_channel("missing", channels) == ""

assert toggle_expanded_channel("", "hwmon5:pwm2", channels) == "hwmon5:pwm2"
assert toggle_expanded_channel("hwmon5:pwm2", "hwmon5:pwm3", channels) == "hwmon5:pwm3"
assert toggle_expanded_channel("hwmon5:pwm3", "hwmon5:pwm3", channels) == ""
assert toggle_expanded_channel("hwmon5:pwm2", "missing", channels) == "hwmon5:pwm2"

code = (ROOT / "kraken_control.py").read_text(encoding="utf-8")
assert 'self.mainboard_expanded_channel_id = ""' in code
assert 'expanded = channel.stable_id == self.mainboard_expanded_channel_id' in code
assert '"Kurve & Details schließen" if expanded else "Kurve & Details bearbeiten"' in code
assert "def toggle_mainboard_fan_card_details" in code
assert "self.mainboard_expanded_channel_id = normalize_expanded_channel" in code
assert "self.mainboard_expanded_channel_id = channels[0].stable_id" not in code

print("3.4.28 collapsed and single-expanded chassis-fan card guards passed.")
