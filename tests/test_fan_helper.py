from pathlib import Path
import io
import os
import pwd
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import ohc_fan_helper as helper


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="ascii")


def setup_hwmon(tmp_path: Path, channel: int = 3) -> Path:
    hw = tmp_path / "hwmon2"
    write(hw / "name", "nct6687\n")
    write(hw / f"pwm{channel}", "94\n")
    write(hw / f"pwm{channel}_enable", "2\n")
    write(hw / f"pwm{channel}_mode", "1\n")
    write(hw / f"fan{channel}_input", "909\n")
    write(hw / "fan_control_watchdog", "0\n")
    return hw


def test_helper_set_percent_and_restore_firmware(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    hw = setup_hwmon(tmp_path)
    monkeypatch.setattr(helper, "HWMON_ROOT", tmp_path)
    monkeypatch.setattr(helper.os, "geteuid", lambda: 0)
    assert helper.main(["helper", "set-percent", "3", "70"]) == 0
    assert (hw / "pwm3_enable").read_text().strip() == "1"
    assert (hw / "pwm3").read_text().strip() == "178"
    assert helper.main(["helper", "restore-firmware", "3"]) == 0
    assert (hw / "pwm3_enable").read_text().strip() == "2"
    assert '"ok": true' in capsys.readouterr().out


def test_helper_snapshot_auto_does_not_replay_cached_pwm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hw = setup_hwmon(tmp_path)
    monkeypatch.setattr(helper, "HWMON_ROOT", tmp_path)
    monkeypatch.setattr(helper.os, "geteuid", lambda: 0)
    write(hw / "pwm3", "178\n")
    write(hw / "pwm3_enable", "1\n")
    helper.main(["helper", "restore-snapshot", "3", "94", "2"])
    assert (hw / "pwm3_enable").read_text().strip() == "2"
    assert (hw / "pwm3").read_text().strip() == "178"


def test_authenticated_session_handles_multiple_bounded_writes_without_reauth(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    hw = setup_hwmon(tmp_path)
    monkeypatch.setattr(helper, "HWMON_ROOT", tmp_path)
    monkeypatch.setattr(helper.os, "geteuid", lambda: 0)
    monkeypatch.setattr(
        helper.sys,
        "stdin",
        io.StringIO('["set-percent", "3", "70"]\n["restore-firmware", "3"]\n'),
    )
    assert helper.main(["helper", "session"]) == 0
    output = capsys.readouterr().out
    assert '"session": "ready"' in output
    assert output.count('"ok": true') == 3
    assert (hw / "pwm3_enable").read_text().strip() == "2"


def test_helper_rejects_arbitrary_channel_and_percent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    setup_hwmon(tmp_path)
    monkeypatch.setattr(helper, "HWMON_ROOT", tmp_path)
    monkeypatch.setattr(helper.os, "geteuid", lambda: 0)
    with pytest.raises(SystemExit):
        helper.main(["helper", "set-percent", "9", "70"])
    with pytest.raises(SystemExit):
        helper.main(["helper", "set-percent", "3", "101"])


def test_helper_watchdog_is_bounded_and_fixed_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    hw = setup_hwmon(tmp_path)
    monkeypatch.setattr(helper, "HWMON_ROOT", tmp_path)
    monkeypatch.setattr(helper.os, "geteuid", lambda: 0)
    helper.main(["helper", "watchdog", "10"])
    assert (hw / "fan_control_watchdog").read_text().strip() == "10"
    with pytest.raises(SystemExit):
        helper.main(["helper", "watchdog", "301"])


def test_helper_switches_only_exposed_bounded_pwm_dc_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    hw = setup_hwmon(tmp_path)
    monkeypatch.setattr(helper, "HWMON_ROOT", tmp_path)
    monkeypatch.setattr(helper.os, "geteuid", lambda: 0)
    helper.main(["helper", "set-mode", "3", "0"])
    assert (hw / "pwm3_mode").read_text().strip() == "0"
    helper.main(["helper", "set-mode", "3", "1"])
    assert (hw / "pwm3_mode").read_text().strip() == "1"
    with pytest.raises(SystemExit):
        helper.main(["helper", "set-mode", "3", "2"])


def test_helper_refuses_non_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    setup_hwmon(tmp_path)
    monkeypatch.setattr(helper, "HWMON_ROOT", tmp_path)
    monkeypatch.setattr(helper.os, "geteuid", lambda: 1000)
    with pytest.raises(SystemExit) as exc:
        helper.main(["helper", "probe"])
    assert exc.value.code == 77


def test_helper_grants_and_revokes_exact_pkexec_user_rule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    uid = os.getuid()
    if uid == 0:
        pytest.skip("test requires a non-root account identity")
    username = pwd.getpwuid(uid).pw_name
    rules = tmp_path / "rules"
    states = tmp_path / "states"
    monkeypatch.setattr(helper, "PERSISTENT_RULES_DIR", rules)
    monkeypatch.setattr(helper, "PERSISTENT_STATE_DIR", states)
    monkeypatch.setattr(helper.os, "geteuid", lambda: 0)
    monkeypatch.setenv("PKEXEC_UID", str(uid))
    assert helper.main(["helper", "grant-persistent"]) == 0
    rule = helper.persistent_rule_path(uid)
    content = rule.read_text(encoding="ascii")
    assert helper.POLKIT_ACTION_ID in content
    assert username in content
    assert "polkit.Result.YES" in content
    assert rule.stat().st_mode & 0o777 == 0o644
    marker = helper.persistent_state_path(uid)
    assert marker.is_file()
    assert f'"uid": {uid}' in marker.read_text(encoding="ascii")
    assert helper.main(["helper", "revoke-persistent"]) == 0
    assert not rule.exists()
    assert not marker.exists()
    assert capsys.readouterr().out.count('"ok": true') == 2


def test_helper_rejects_persistent_rule_change_without_pkexec_caller(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(helper, "PERSISTENT_RULES_DIR", tmp_path)
    monkeypatch.setattr(helper, "PERSISTENT_STATE_DIR", tmp_path / "states")
    monkeypatch.setattr(helper.os, "geteuid", lambda: 0)
    monkeypatch.delenv("PKEXEC_UID", raising=False)
    with pytest.raises(SystemExit):
        helper.main(["helper", "grant-persistent"])
