from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mainboard_fan_control import (
    CurvePolicy,
    CurveState,
    DmiInfo,
    decide_curve_output,
    channel_control_mode,
    channel_control_mode_supported,
    detect_dmi,
    fan_preset,
    MAINBOARD_FAN_PRESETS,
    PrivilegedFanHelperSession,
    recommend_fan_preset,
    discover_hwmon_controllers,
    interpolate_curve,
    percent_to_pwm,
    persistent_fan_authorization_command,
    persistent_fan_authorization_enabled,
    persistent_fan_authorization_path,
    preferred_nct6687_controller,
    pwm_to_percent,
    disarm_fan_control_watchdog,
    restore_firmware_control,
    restore_snapshot,
    select_temperature,
    set_channel_percent,
    set_channel_control_mode,
    set_fan_control_watchdog,
    snapshot_channel,
    update_curve_state,
    validate_curve,
)


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="ascii")


def test_dmi_detects_msi_x870_tomahawk(tmp_path: Path) -> None:
    write(tmp_path / "board_vendor", "Micro-Star International Co., Ltd.\n")
    write(tmp_path / "board_name", "MAG X870 TOMAHAWK WIFI (MS-7E51)\n")
    write(tmp_path / "product_name", "MS-7E51\n")
    info = detect_dmi(tmp_path)
    assert info.is_msi_x870_family
    assert info.is_msi_mag_x870_tomahawk


def test_non_x870_msi_is_not_x870_family() -> None:
    info = DmiInfo(board_vendor="Micro-Star International", board_name="MAG B650 TOMAHAWK WIFI")
    assert not info.is_msi_x870_family
    assert not info.is_msi_mag_x870_tomahawk


def test_hwmon_discovery_finds_pwm_and_rpm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hw = tmp_path / "hwmon11"
    write(hw / "name", "nct6687\n")
    write(hw / "pwm1", "128\n")
    write(hw / "pwm1_enable", "99\n")
    write(hw / "pwm1_mode", "1\n")
    write(hw / "fan1_input", "1050\n")
    write(hw / "fan1_label", "System Fan #1\n")
    write(hw / "pwm6", "200\n")
    write(hw / "pwm6_enable", "1\n")
    monkeypatch.setattr(os, "access", lambda path, mode: True)
    controllers = discover_hwmon_controllers(tmp_path)
    controller = preferred_nct6687_controller(controllers)
    assert controller is not None
    assert controller.name == "nct6687"
    assert [channel.index for channel in controller.channels] == [1, 6]
    assert controller.channels[0].rpm == 1050
    assert controller.channels[0].display_name.startswith("System Fan #1")
    assert controller.channels[0].mode_path == hw / "pwm1_mode"
    assert channel_control_mode(controller.channels[0]) == "pwm"
    assert controller.channels[1].stable_id == "nct6687:pwm6"


@pytest.mark.parametrize(
    ("percent", "expected"),
    [(0, 0), (25, 64), (50, 128), (70, 178), (100, 255), (150, 255), (-2, 0)],
)
def test_percent_to_pwm(percent: int, expected: int) -> None:
    assert percent_to_pwm(percent) == expected


def test_pwm_round_trip_is_close() -> None:
    for percent in range(0, 101, 5):
        assert abs(pwm_to_percent(percent_to_pwm(percent)) - percent) <= 1


def test_temperature_sources() -> None:
    assert select_temperature("cpu", cpu=61.0, gpu=48.0, liquid=34.0) == 61.0
    assert select_temperature("gpu", cpu=61.0, gpu=68.0, liquid=34.0) == 68.0
    assert select_temperature("liquid", cpu=61.0, gpu=68.0, liquid=34.0) == 34.0
    assert select_temperature("max", cpu=61.0, gpu=68.0, liquid=34.0) == 68.0
    assert select_temperature("weighted", cpu=60.0, gpu=40.0, liquid=34.0, cpu_weight=75) == 55.0
    assert select_temperature("weighted", cpu=None, gpu=50.0, liquid=34.0) == 50.0
    assert select_temperature("cpu", cpu=None, gpu=50.0, liquid=34.0) is None


def test_curve_interpolation_and_validation() -> None:
    curve = validate_curve([(35, 30), (45, 40), (60, 55), (75, 75), (85, 100)])
    assert interpolate_curve(curve, 20) == 30
    assert interpolate_curve(curve, 85) == 100
    assert interpolate_curve(curve, 52.5) == pytest.approx(47.5)
    with pytest.raises(ValueError):
        validate_curve([(40, 20), (40, 30)])
    with pytest.raises(ValueError):
        validate_curve([(40, 20)])
    with pytest.raises(ValueError):
        validate_curve([(40, 10), (60, 101)])
    with pytest.raises(ValueError):
        validate_curve([(35, 50), (60, 40), (85, 100)])
    with pytest.raises(ValueError):
        validate_curve([(35, 30), (60, 55), (85, 90)])


def test_curve_decision_initial_hysteresis_delay_and_emergency() -> None:
    policy = CurvePolicy(
        points=[(30, 25), (60, 55), (85, 100)],
        minimum_percent=30,
        hysteresis_c=2.0,
        response_delay_s=3.0,
        emergency_temp_c=90,
    )
    state = CurveState()
    first = decide_curve_output(policy, state, 40.0, now=10.0)
    assert first.should_write and first.percent == 35 and first.reason == "initial"
    update_curve_state(state, 40.0, first.percent, now=10.0)
    hysteresis = decide_curve_output(policy, state, 41.0, now=20.0)
    assert not hysteresis.should_write and hysteresis.reason == "hysteresis"
    delay = decide_curve_output(policy, state, 50.0, now=11.0)
    assert not delay.should_write and delay.reason == "response-delay"
    changed = decide_curve_output(policy, state, 50.0, now=14.0)
    assert changed.should_write and changed.percent == 45
    emergency = decide_curve_output(policy, state, 92.0, now=10.1)
    assert emergency.should_write and emergency.percent == 100 and emergency.reason == "emergency"


def test_sysfs_write_snapshot_restore_and_firmware_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hw = tmp_path / "hwmon4"
    write(hw / "name", "nct6687\n")
    write(hw / "pwm3", "210\n")
    write(hw / "pwm3_enable", "99\n")
    write(hw / "pwm3_mode", "1\n")
    monkeypatch.setattr(os, "access", lambda path, mode: True)
    channel = discover_hwmon_controllers(tmp_path)[0].channels[0]
    snapshot = snapshot_channel(channel)
    set_channel_percent(channel, 70)
    assert (hw / "pwm3_enable").read_text().strip() == "1"
    assert int((hw / "pwm3").read_text().strip()) == percent_to_pwm(70)
    restore_snapshot(channel, snapshot)
    # Automatic mode is restored through pwm_enable=2; on current NCT6687
    # the driver restores its saved firmware/MSI curve rather than requiring
    # userspace to replay the instantaneous cached pwm value.
    assert (hw / "pwm3_enable").read_text().strip() == "2"
    set_channel_percent(channel, 55)
    restore_firmware_control(channel)
    assert (hw / "pwm3_enable").read_text().strip() == "2"


def test_pwm_dc_switch_requires_exposed_driver_node(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hw = tmp_path / "hwmon4"
    write(hw / "name", "nct6687\n")
    write(hw / "pwm3", "128\n")
    write(hw / "pwm3_enable", "2\n")
    write(hw / "pwm3_mode", "1\n")
    monkeypatch.setattr(os, "access", lambda path, mode: True)
    channel = discover_hwmon_controllers(tmp_path)[0].channels[0]
    assert channel_control_mode_supported(channel)
    set_channel_control_mode(channel, "dc")
    assert (hw / "pwm3_mode").read_text().strip() == "0"
    assert channel_control_mode(channel) == "dc"
    channel.mode_path = None
    assert not channel_control_mode_supported(channel)
    with pytest.raises(Exception):
        set_channel_control_mode(channel, "pwm")


def test_nct6687_driver_watchdog_arm_refresh_and_disarm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hw = tmp_path / "hwmon9"
    write(hw / "name", "nct6687\n")
    write(hw / "pwm1", "128\n")
    write(hw / "pwm1_enable", "2\n")
    write(hw / "fan_control_watchdog", "0\n")
    monkeypatch.setattr(os, "access", lambda path, mode: True)
    controller = discover_hwmon_controllers(tmp_path)[0]
    assert controller.watchdog_path == hw / "fan_control_watchdog"
    assert set_fan_control_watchdog(controller, 10)
    assert (hw / "fan_control_watchdog").read_text().strip() == "10"
    assert set_fan_control_watchdog(controller, 500)  # bounded by driver API
    assert (hw / "fan_control_watchdog").read_text().strip() == "300"
    assert disarm_fan_control_watchdog(controller)
    assert (hw / "fan_control_watchdog").read_text().strip() == "0"


def test_watchdog_is_optional(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hw = tmp_path / "hwmon2"
    write(hw / "name", "nct6687\n")
    write(hw / "pwm1", "128\n")
    monkeypatch.setattr(os, "access", lambda path, mode: True)
    controller = discover_hwmon_controllers(tmp_path)[0]
    assert controller.watchdog_path is None
    assert not set_fan_control_watchdog(controller, 10)


def test_unwritable_channel_is_never_written(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hw = tmp_path / "hwmon1"
    write(hw / "name", "nct6687\n")
    write(hw / "pwm2", "100\n")
    monkeypatch.setattr(os, "access", lambda path, mode: False)
    channel = discover_hwmon_controllers(tmp_path)[0].channels[0]
    assert not channel.writable
    with pytest.raises(Exception):
        set_channel_percent(channel, 70)
    assert (hw / "pwm2").read_text().strip() == "100"


def test_curve_force_and_minimum_clamp() -> None:
    policy = CurvePolicy(points=[(30, 10), (60, 50), (85, 100)], minimum_percent=25, response_delay_s=10)
    state = CurveState(last_temperature_c=40, last_percent=30, last_write_monotonic=100)
    forced = decide_curve_output(policy, state, 35, now=101, force=True)
    assert forced.should_write
    assert forced.percent == 25


def test_mainboard_presets_are_safe_monotonic_and_end_at_full_speed() -> None:
    assert set(MAINBOARD_FAN_PRESETS) == {"quiet", "balanced", "performance"}
    for key, preset in MAINBOARD_FAN_PRESETS.items():
        validated = validate_curve(preset.points, 0)
        assert validated[-1][1] == 100
        assert 20 <= preset.minimum_percent <= 50
        assert preset.source in {"cpu", "gpu", "liquid", "max", "weighted"}
        assert fan_preset(key) == preset


def test_preset_recommendation_is_conservative_and_never_maps_pwm() -> None:
    assert recommend_fan_preset(channel_name="System Fan #2", board_name="MAG X870 TOMAHAWK WIFI") == "balanced"
    assert recommend_fan_preset(channel_name="Radiator oben", board_name="MAG X870 TOMAHAWK WIFI") == "performance"
    assert recommend_fan_preset(channel_name="Pump Fan", board_name="Other") == "performance"
    assert recommend_fan_preset(channel_name="Leise Gehäuselüfter", board_name="Other") == "quiet"
    assert fan_preset("unknown").key == "balanced"


def test_polkit_helper_path_is_used_for_unprivileged_nct6687(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import mainboard_fan_control as mfc
    hw = tmp_path / "hwmon2"
    write(hw / "name", "nct6687\n")
    write(hw / "pwm3", "100\n")
    write(hw / "pwm3_enable", "2\n")
    write(hw / "fan3_input", "900\n")
    channel = discover_hwmon_controllers(tmp_path)[0].channels[0]
    monkeypatch.setattr(mfc, "privileged_fan_helper_available", lambda: True)
    monkeypatch.setattr(os, "access", lambda path, mode: False)
    calls = []
    monkeypatch.setattr(mfc, "_run_privileged_helper", lambda *args, **kwargs: calls.append(args) or {"ok": True})
    assert mfc.channel_can_control(channel)
    assert mfc.channel_control_method(channel) == "polkit"
    mfc.set_channel_percent(channel, 70)
    mfc.restore_firmware_control(channel)
    assert calls == [("set-percent", "3", "70"), ("restore-firmware", "3")]


def test_privileged_helper_session_reuses_one_authenticated_child(monkeypatch: pytest.MonkeyPatch) -> None:
    import mainboard_fan_control as mfc

    class FakeInput:
        def __init__(self) -> None:
            self.writes: list[str] = []
        def write(self, value: str) -> int:
            self.writes.append(value)
            return len(value)
        def flush(self) -> None:
            return None

    class FakeProcess:
        def __init__(self) -> None:
            self.stdin = FakeInput()
            self.stdout = object()
            self.stderr = object()
        def poll(self):
            return None

    process = FakeProcess()
    launches: list[list[str]] = []
    monkeypatch.setattr(mfc, "privileged_fan_helper_available", lambda: True)
    monkeypatch.setattr(
        mfc.subprocess,
        "Popen",
        lambda command, **_kwargs: launches.append(command) or process,
    )
    session = PrivilegedFanHelperSession()
    monkeypatch.setattr(session, "_reply", lambda _timeout: {"ok": True})
    session.request(("set-percent", "2", "52"))
    session.request(("set-percent", "2", "54"))
    assert len(launches) == 1
    assert launches[0][-1] == "session"
    assert len(process.stdin.writes) == 2


def test_persistent_authorization_uses_fixed_per_user_rule_and_helper_command(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import mainboard_fan_control as mfc

    monkeypatch.setattr(mfc, "PERSISTENT_FAN_RULES_DIR", tmp_path)
    monkeypatch.setattr(mfc, "PERSISTENT_FAN_STATE_DIR", tmp_path / "states")
    monkeypatch.setattr(mfc, "privileged_fan_helper_available", lambda: True)
    uid = os.getuid()
    assert persistent_fan_authorization_path(uid) == tmp_path / f"49-open-hardware-control-fan-{uid}.rules"
    assert not persistent_fan_authorization_enabled(uid)
    marker = mfc.PERSISTENT_FAN_STATE_DIR / str(uid)
    write(marker, "enabled\n")
    assert persistent_fan_authorization_enabled(uid)
    assert persistent_fan_authorization_command(True)[-1] == "grant-persistent"
    assert persistent_fan_authorization_command(False)[-1] == "revoke-persistent"


def test_polkit_snapshot_auto_uses_firmware_restore(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import mainboard_fan_control as mfc
    hw = tmp_path / "hwmon2"
    write(hw / "name", "nct6687\n")
    write(hw / "pwm4", "128\n")
    write(hw / "pwm4_enable", "2\n")
    channel = discover_hwmon_controllers(tmp_path)[0].channels[0]
    monkeypatch.setattr(mfc, "privileged_fan_helper_available", lambda: True)
    monkeypatch.setattr(os, "access", lambda path, mode: False)
    calls = []
    monkeypatch.setattr(mfc, "_run_privileged_helper", lambda *args, **kwargs: calls.append(args) or {"ok": True})
    mfc.restore_snapshot(channel, mfc.CalibrationSnapshot(pwm=128, enable=2))
    assert calls == [("restore-firmware", "4")]
