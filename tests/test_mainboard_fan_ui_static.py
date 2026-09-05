from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = (ROOT / "kraken_control.py").read_text(encoding="utf-8")


def test_profile_presets_are_exposed_in_ui_without_bypassing_calibration() -> None:
    assert '"quiet", "balanced", "performance"' in CODE
    assert 'Profilvorlage' in CODE
    assert 'Vorlage übernehmen' in CODE
    assert 'Die Vorlage aktiviert keinen unbestätigten PWM-Kanal.' in CODE
    assert 'if enabled and not bool(profile.get("calibrated", False))' in CODE


def test_case_profiles_match_cpu_card_and_keep_automation_separate() -> None:
    summary_start = CODE.index('self.cooling_case_summary_label = QLabel')
    profile_start = CODE.index('self.cooling_case_profile_buttons', summary_start)
    automatic_start = CODE.index('automatic_row = QHBoxLayout()', profile_start)
    assert summary_start < profile_start < automatic_start
    assert 'objectName="coolingQuickProfileButton"' in CODE[profile_start:automatic_start]
    assert 'self.apply_mainboard_fan_preset_to_all_channels(key)' in CODE[profile_start:automatic_start]
    assert 'QLabel("Automatische Regelung")' in CODE[automatic_start:]


def test_mainboard_master_control_remains_calibration_gated() -> None:
    assert 'bool(self.mainboard_fan_profiles.get(channel_id, {}).get("calibrated", False))' in CODE
    assert 'bool(self.mainboard_fan_profiles.get(channel_id, {}).get("enabled", False))' in CODE
    assert 'set_mainboard_fan_watchdog(self.mainboard_hwmon_controller, 10)' in CODE


def test_ene_reinitialize_button_is_present() -> None:
    assert 'ENE-RAM erneut initialisieren' in CODE
    assert 'RGB-ENE-WAKE' in CODE


def test_341231_calibration_uses_polkit_and_ten_second_rpm_observation() -> None:
    assert 'Kanal sicher testen · 70 % / 10 s' in CODE
    assert 'mainboard_channel_can_control(channel)' in CODE
    assert 'mainboard_channel_control_method(channel)' in CODE
    assert 'mainboard_calibration_sample_timer' in CODE
    assert 'RPM vor Test' in CODE
    assert 'self.mainboard_calibration_timer.start(10000)' in CODE


def test_persistent_fan_authorization_has_grant_and_revoke_controls() -> None:
    assert 'Dauerhafte Berechtigung erteilen' in CODE
    assert 'Dauerhafte Berechtigung entfernen' in CODE
    assert 'persistent_fan_authorization_command(enabled)' in CODE
    assert 'kein Passwort gespeichert' in CODE
