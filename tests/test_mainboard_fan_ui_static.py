from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
WORKFLOW_CODE = (ROOT / "src/modules/pc_case_profiles/v1_5/controller.py").read_text(encoding="utf-8")


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
    assert 'QPushButton("Automatische Regelung")' in CODE[automatic_start:]
    assert 'self.cooling_auto_case_button.setCheckable(True)' in CODE[automatic_start:]
    assert 'button.setChecked(self.mainboard_control_active)' in CODE[automatic_start:]
    assert '"100-%-Override für alle bestätigten, aktiven Gehäuselüfter"' in CODE
    assert "QTimer.singleShot(0, self.update_mainboard_fan_control)" in CODE
    assert "def apply_matching_case_fan_profile" in CODE
    assert CODE.count("KrakenControl.apply_matching_case_fan_profile(self, name)") == 4
    assert '"leistung": "performance"' in CODE


def test_each_case_fan_card_exposes_bounded_stop_test_and_bios_mode_explanation() -> None:
    assert 'QPushButton(self.tr_static("0 % / 10 s testen"))' in CODE
    assert "def test_mainboard_channel_stop_from_card" in CODE
    assert "self.start_mainboard_fan_calibration(stop_test=True)" in CODE
    assert 'self.tr_static("PWM/DC wird im BIOS festgelegt")' in CODE
    assert "Der Kernel stellt kein pwmN_mode bereit" in CODE


def test_mainboard_master_control_remains_calibration_gated() -> None:
    assert 'bool(self.mainboard_fan_profiles.get(channel_id, {}).get("calibrated", False))' in CODE
    assert 'bool(self.mainboard_fan_profiles.get(channel_id, {}).get("enabled", False))' in CODE
    assert 'set_mainboard_fan_watchdog(self.mainboard_hwmon_controller, 10)' in CODE


def test_channel_automation_button_names_the_click_action() -> None:
    assert '"Automatik ausschalten" if enabled else "Automatik einschalten"' in CODE
    assert '"Automatik aktiv" if enabled else "Automatik aus"' not in CODE


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


def test_assignments_can_be_safely_reset_and_wizard_can_continue() -> None:
    reset = WORKFLOW_CODE[WORKFLOW_CODE.index("    def reset_chassis_fan_assignments"):WORKFLOW_CODE.index("    def select_cooling_layout_slot")]
    assert 'QPushButton("Alle Lüfterzuordnungen zurücksetzen")' in CODE
    assert "self.toggle_mainboard_master_control(False, silent=True)" in reset
    assert 'profile["calibrated"] = False' in reset
    assert 'profile["enabled"] = False' in reset
    assert "self.mainboard_layout_assignments.clear()" in reset
    assert "Kurven erhalten" in reset
    assert "def assistant_continue_with_next_fan" in WORKFLOW_CODE
    assert 'QPushButton(self.tr_static("Nächsten Lüfter zuordnen"))' in CODE
    assert "wizard.setCurrentId(1)" in WORKFLOW_CODE
