#!/usr/bin/env python3
"""Regression coverage for backend policy and session temperature history."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.hardware_backends.v1_0 import (  # noqa: E402
    DISPLAY_BACKENDS,
    FAN_BACKENDS,
    normalize_backend_choice,
    resolve_backend,
)
from modules.temperature_history.v1_2 import TemperatureHistoryBuffer  # noqa: E402


def test_backend_resolution_is_fail_closed_and_never_falls_back_from_explicit_choice() -> None:
    assert DISPLAY_BACKENDS == ("trcc_linux",)
    assert FAN_BACKENDS == ("ohc_hwmon",)
    automatic = resolve_backend("auto", FAN_BACKENDS, {"ohc_hwmon": True})
    assert automatic.active == "ohc_hwmon"
    assert automatic.automatic
    unavailable = resolve_backend("ohc_hwmon", FAN_BACKENDS, {"ohc_hwmon": False})
    assert unavailable.active is None
    assert not unavailable.available
    assert not unavailable.automatic
    assert normalize_backend_choice("invented", FAN_BACKENDS) == "auto"


def test_temperature_history_is_bounded_validated_and_session_only() -> None:
    history = TemperatureHistoryBuffer(max_age_seconds=60, max_samples=20)
    assert history.append({"cpu": 50.0, "gpu": None}, timestamp=100.0)
    assert history.append({"cpu": 55.0, "gpu": 60.0}, timestamp=150.0)
    assert history.append({"cpu": 57.0}, timestamp=170.0)
    assert [sample.timestamp for sample in history.samples] == [150.0, 170.0]
    assert [sample.timestamp for sample in history.window(15)] == [170.0]
    assert not history.append({"cpu": float("nan"), "gpu": 999.0}, timestamp=171.0)
    assert not hasattr(history, "save")


def test_ui_wires_profile_fixed_mode_backend_settings_and_history() -> None:
    source = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
    assert '"Profil-Festwert"' in source
    assert '"hardware_backends/display"' in source
    assert '"hardware_backends/fans"' in source
    assert "fan_backend_write_ready" in source
    assert "TemperatureHistoryChart" in source
    assert "record_temperature_history()" in source
