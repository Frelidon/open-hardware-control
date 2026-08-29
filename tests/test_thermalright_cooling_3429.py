#!/usr/bin/env python3
"""Regression tests for the safe Levita Vision 360 cooling path."""

from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from thermalright_cooling import (
    LEVITA_COOLER_KEY,
    LEVITA_DISPLAY_NAME,
    aio_channel_role,
    profile_duties,
    suggest_aio_channels,
    thermalright_display_present,
)


def test_exact_model_identity() -> None:
    assert LEVITA_COOLER_KEY == "thermalright-levita-vision-360-argb-black"
    assert LEVITA_DISPLAY_NAME == "Thermalright Levita Vision 360 ARGB Black"


def test_display_usb_detection_is_read_only_and_exact(tmp_path: Path) -> None:
    device = tmp_path / "1-7"
    device.mkdir()
    (device / "idVendor").write_text("87AD\n", encoding="ascii")
    (device / "idProduct").write_text("70DB\n", encoding="ascii")
    assert thermalright_display_present(tmp_path)

    (device / "idProduct").write_text("70dc\n", encoding="ascii")
    assert not thermalright_display_present(tmp_path)


def test_mainboard_labels_suggest_roles_without_board_guessing() -> None:
    assert aio_channel_role("Pump Fan · pwm2") == "pump"
    assert aio_channel_role("CPU_FAN · pwm1") == "radiator"
    assert aio_channel_role("System Fan · pwm3") is None

    @dataclass
    class Channel:
        stable_id: str
        display_name: str
        rpm: int | None = None

    suggestion = suggest_aio_channels(
        [
            Channel("nct6687:pwm1", "CPU Fan · pwm1", 1038),
            Channel("nct6687:pwm2", "Pump Fan · pwm2", 2810),
            Channel("nct6687:pwm3", "System Fan · pwm3", 900),
        ]
    )
    assert suggestion.pump_channel_id == "nct6687:pwm2"
    assert suggestion.radiator_channel_id == "nct6687:pwm1"
    assert suggestion.complete


def test_profiles_keep_pump_and_fans_in_safe_ranges() -> None:
    assert profile_duties("Leise") == (55, 35)
    assert profile_duties("Ausbalanciert") == (70, 50)
    assert profile_duties("Leistung") == (90, 75)
    assert profile_duties("Sicherheit") == (100, 100)
    for name in ("Leise", "Ausbalanciert", "Leistung", "Sicherheit", "unbekannt"):
        pump, radiator = profile_duties(name)
        assert 20 <= pump <= 100
        assert 0 <= radiator <= 100


def test_application_requires_mapping_calibration_and_restores_firmware() -> None:
    main = (ROOT / "kraken_control.py").read_text(encoding="utf-8")
    build = (ROOT / "scripts/build_release.py").read_text(encoding="utf-8")

    assert "Wasserkühlung und PWM-Zuordnung" in main
    assert "Pumpenkanal sicher testen · 70 % / 10 s" in main
    assert "Radiatorkanal sicher testen · 70 % / 10 s" in main
    assert "wurde noch nicht mit dem sicheren 70-%-/10-s-Test bestätigt" in main
    assert "CoolerControl besitzt aktuell die Mainboard-PWM-Steuerung" in main
    assert "restore_thermalright_cooling_on_quit" in main
    assert "restore_mainboard_firmware_control(channel)" in main
    assert "Levita meldet keinen Kühlmittelsensor" in main
    assert '"thermalright_cooling.py"' in build
