from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import ohc_fan_helper as helper


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="ascii")


def setup_hwmon(tmp_path: Path, channel: int = 3) -> Path:
    hw = tmp_path / "hwmon2"
    write(hw / "name", "nct6687\n")
    write(hw / f"pwm{channel}", "94\n")
    write(hw / f"pwm{channel}_enable", "2\n")
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


def test_helper_refuses_non_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    setup_hwmon(tmp_path)
    monkeypatch.setattr(helper, "HWMON_ROOT", tmp_path)
    monkeypatch.setattr(helper.os, "geteuid", lambda: 1000)
    with pytest.raises(SystemExit) as exc:
        helper.main(["helper", "probe"])
    assert exc.value.code == 77
