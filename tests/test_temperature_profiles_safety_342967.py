#!/usr/bin/env python3
"""Regression coverage for the 3.4.29.71 cooling/history/profile work."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from modules.cooling_safety.v1_0 import clamp_cooling_duty, cooling_duty_policy  # noqa: E402
from modules.temperature_history.v1_2 import (  # noqa: E402
    TemperatureHistoryBuffer,
    read_linux_temperature_sensors,
)


def _sensor(root: Path, number: int, chip: str, label: str, value: int) -> None:
    directory = root / f"hwmon{number}"
    directory.mkdir()
    (directory / "name").write_text(chip, encoding="ascii")
    (directory / "temp1_input").write_text(str(value), encoding="ascii")
    if label:
        (directory / "temp1_label").write_text(label, encoding="utf-8")


def test_hwmon_sensor_discovery_groups_memory_storage_and_vrm(tmp_path: Path) -> None:
    _sensor(tmp_path, 0, "nvme", "Composite", 39_850)
    _sensor(tmp_path, 1, "spd5118", "", 40_000)
    _sensor(tmp_path, 2, "nct6687", "VRM MOS", 45_000)
    readings = read_linux_temperature_sensors(tmp_path)
    assert {reading.group for reading in readings} == {"storage", "memory", "mainboard"}
    assert {round(reading.value_c, 1) for reading in readings} == {39.9, 40.0, 45.0}
    assert all(reading.key.startswith("hwmon:") for reading in readings)


def test_temperature_statistics_follow_selected_window() -> None:
    history = TemperatureHistoryBuffer(max_age_seconds=3600, max_samples=100)
    history.append({"ssd": 30}, timestamp=100)
    history.append({"ssd": 40}, timestamp=200)
    history.append({"ssd": 35}, timestamp=300)
    assert history.statistics("ssd") == (35.0, 30.0, 40.0)
    assert history.statistics("ssd", 150) == (35.0, 35.0, 40.0)


def test_levita_has_a_conservative_fail_closed_pwm_floor() -> None:
    key = "thermalright-levita-vision-360-argb-black"
    policy = cooling_duty_policy(key)
    assert policy.pump_minimum == 50
    assert policy.fan_minimum == 25
    assert policy.pump_rated_max_rpm == 3000
    assert policy.manufacturer_minimum_published is False
    assert clamp_cooling_duty(key, "pump", 0) == 50
    assert clamp_cooling_duty(key, "fan", 10) == 25
    assert clamp_cooling_duty(key, "pump", 84) == 84


def test_profile_table_width_and_detailed_editor_regression() -> None:
    source = (SRC / "kraken_control.py").read_text(encoding="utf-8")
    assert "resizeColumnsToContents()" not in source[source.index("def refresh_profiles_table"):source.index("def apply_profile_by_id")]
    assert "QHeaderView.ResizeMode.Stretch" in (ROOT / "src/modules/profiles_workspace/v1_0/page.py").read_text()
    assert 'QGroupBox("Gespeicherter Profilinhalt")' in (ROOT / "src/modules/profiles_workspace/v1_0/page.py").read_text()
    assert "profile_section_checks" in source
    assert 'addTab(self.make_temperature_recording_page(), "Temperaturaufzeichnung")' in source


def test_temperature_sampler_is_read_only_by_construction() -> None:
    source = (SRC / "modules/temperature_history/v1_2/sensors.py").read_text(encoding="utf-8")
    assert ".write_text(" not in source
    assert "subprocess" not in source
    assert "open(" not in source
