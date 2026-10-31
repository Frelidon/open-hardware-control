from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
THEME_CONTROLLER = (ROOT / "src/modules/ui_themes/v1_0/controller.py").read_text(encoding="utf-8")
THEME_CONTROLLER += "".join((ROOT / "src/modules/ui_themes/v1_0" / name).read_text(encoding="utf-8")
                            for name in ("style_base.py", "style_controls.py"))
RESPONSIVE = (ROOT / "src/modules/responsive_startup/v1_0/controller.py").read_text(encoding="utf-8")
BUILD = (ROOT / "scripts/build_release.py").read_text(encoding="utf-8")
INSTALL = (ROOT / "packaging/install.sh").read_text(encoding="utf-8")


def test_compact_dashboard_and_cards_exist():
    assert 'coolingDashboard' in CODE
    assert 'self.cooling_cpu_summary_label' in CODE
    assert 'self.cooling_case_summary_label' in CODE
    assert 'self.cooling_auto_case_button' in CODE
    assert 'self.mainboard_fan_table.setVisible(False)' in CODE
    assert 'FanCurveMiniPreview' in CODE
    assert 'mainboard_fan_cards_layout' in CODE


def test_kraken_quick_profile_highlight_tracks_confirmed_device_state():
    assert 'self.cooling_quick_profile_buttons' in CODE
    assert 'button.setProperty("profileState", "inactive")' in CODE
    assert 'QPushButton#coolingQuickProfileButton[profileState="active"]' in THEME_CONTROLLER
    assert 'self.update_cooling_quick_profile_state(name)' in CODE
    assert 'self.restore_cooling_quick_profile_state()' in CODE
    assert 'button.setObjectName("profilePrimary")' not in CODE
    assert 'self.cooling_auto_case_button.setProperty("profileState", "inactive")' in CODE
    assert 'self.cooling_auto_case_button.setCheckable(True)' in CODE
    assert 'self.cooling_auto_case_button.setChecked(self.mainboard_control_active)' in CODE
    assert 'state = "active" if self.mainboard_control_active else "inactive"' in CODE


def test_cpu_and_pump_are_excluded_from_chassis_control():
    assert 'mainboard_channel_is_chassis_fan(channel)' in CODE
    assert 'CPU_FAN und PUMP_FAN bleiben im separaten CPU-/Kraken-Bereich' in CODE
    assert 'if not mainboard_channel_is_chassis_fan(channel):\n                continue' in CODE


def test_coolercontrol_ownership_is_exclusive():
    assert 'detect_cooling_owner()' not in CODE
    assert 'CoolingOwnershipProbe' in RESPONSIVE
    assert 'CoolingOwnerStatus(True, True, False)' in RESPONSIVE
    assert 'Lüftersteuerung mit OHC übernehmen' in RESPONSIVE
    assert 'CoolerControl besitzt aktuell die Mainboard-Lüftersteuerung' in CODE
    assert 'stop_coolercontrol()' in RESPONSIVE
    assert 'start_coolercontrol()' in RESPONSIVE
    assert 'CoolerControl dauerhaft deaktivieren' in RESPONSIVE
    assert 'CoolerControl dauerhaft aktivieren' in RESPONSIVE
    assert 'disable_coolercontrol()' in RESPONSIVE
    assert 'enable_coolercontrol()' in RESPONSIVE


def test_guided_assistant_has_safe_contrast_and_layout():
    assert 'Geführten Lüfter-Assistenten starten' in CODE
    assert 'andere Gehäuselüfter 30 %' in CODE
    assert 'Alle Gehäuse-RGB auf Weiß' in CODE
    assert 'CoolingLayoutDiagram' in CODE
    assert 'mainboard_fans/layout_assignments' in CODE
    assert 'restore_mainboard_snapshot(other, other_snapshot)' in CODE


def test_new_runtime_module_is_packaged():
    assert '"cooling_ownership.py"' in BUILD
    assert 'cooling_ownership.py' in INSTALL
    for module in (
        'app_constants.py', 'command_backend.py', 'cooling_widgets.py',
        'cooling_card_state.py', 'localization_catalog.py', 'privacy_logging.py', 'temperature_utils.py',
    ):
        assert f'"{module}"' in BUILD
        assert module in INSTALL
