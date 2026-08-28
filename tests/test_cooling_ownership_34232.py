from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cooling_ownership as co
from mainboard_fan_control import FanChannel, channel_is_chassis_fan


def fake_channel(tmp_path: Path, label: str, index: int = 3) -> FanChannel:
    hw = tmp_path / "hwmon2"
    hw.mkdir(exist_ok=True)
    pwm = hw / f"pwm{index}"
    pwm.write_text("100\n")
    label_path = hw / f"fan{index}_label"
    label_path.write_text(label + "\n")
    return FanChannel(index, hw, "nct6687", pwm, None, None, label_path=label_path)


def test_chassis_filter_keeps_system_fans_and_excludes_cpu_pump(tmp_path: Path):
    assert channel_is_chassis_fan(fake_channel(tmp_path, "System Fan #1", 3)) is True
    assert channel_is_chassis_fan(fake_channel(tmp_path, "CPU Fan", 1)) is False
    assert channel_is_chassis_fan(fake_channel(tmp_path, "Pump Fan", 2)) is False
    assert channel_is_chassis_fan(fake_channel(tmp_path, "Unknown", 4)) is False


def test_owner_status_reports_coolercontrol():
    status = co.CoolingOwnerStatus(True, False)
    assert status.coolercontrol_active is True
    assert status.owner == "coolercontrol"
    assert co.CoolingOwnerStatus(False, False).owner == "available"


def test_detect_uses_service_and_process(monkeypatch):
    monkeypatch.setattr(co.shutil, "which", lambda name: f"/usr/bin/{name}")

    def runner(command, *, timeout=5.0):
        _ = timeout
        rc = 0 if ("systemctl" in command[0] or "pgrep" in command[0]) else 1
        return subprocess.CompletedProcess(command, rc, "", "")

    monkeypatch.setattr(co, "_run", runner)
    status = co.detect_cooling_owner()
    assert status.coolercontrol_service_active is True
    assert status.coolercontrol_process_active is True
    assert status.coolercontrol_service_enabled is True


def test_switch_rejects_unknown_action():
    ok, detail = co._switch_coolercontrol("restart")
    assert ok is False
    assert "Ungültige" in detail


def test_switch_is_fixed_to_coolercontrol_service(monkeypatch):
    calls = []
    monkeypatch.setattr(co.shutil, "which", lambda name: f"/usr/bin/{name}")

    def runner(command, *, timeout=5.0):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(co, "_run", runner)
    ok, detail = co.stop_coolercontrol()
    assert ok is True and detail == ""
    assert calls == [["/usr/bin/pkexec", "/usr/bin/systemctl", "stop", "coolercontrold.service"]]


def test_permanent_switch_is_fixed_to_service_and_uses_now(monkeypatch):
    calls = []
    monkeypatch.setattr(co.shutil, "which", lambda name: f"/usr/bin/{name}")

    def runner(command, *, timeout=5.0):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(co, "_run", runner)
    assert co.disable_coolercontrol() == (True, "")
    assert co.enable_coolercontrol() == (True, "")
    assert calls == [
        ["/usr/bin/pkexec", "/usr/bin/systemctl", "disable", "--now", "coolercontrold.service"],
        ["/usr/bin/pkexec", "/usr/bin/systemctl", "enable", "--now", "coolercontrold.service"],
    ]
