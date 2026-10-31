#!/usr/bin/env python3
"""Safety and wiring guards for the guided NCT6687/MOK setup flow."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from modules.mainboard_driver_setup.v1_1 import distribution, model  # noqa: E402


def make_status(**overrides):
    values = {
        "secure_boot": "enabled",
        "certificate_exists": True,
        "enrolled": True,
        "module_loaded": True,
        "module_available": True,
        "module_signer": "DKMS module signing key",
        "mokutil_available": True,
        "dkms_available": True,
        "sudo_available": True,
        "modprobe_available": True,
        "terminal_available": True,
    }
    values.update(overrides)
    return model.MokStatus(**values)


def test_mokutil_keyring_warning_does_not_hide_confirmed_enrollment():
    result = subprocess.CompletedProcess(
        ["mokutil", "--test-key"], 1,
        stdout="/var/lib/dkms/mok.pub is already enrolled\n",
        stderr="Failed to access kernel trusted keyring: Required key not available\n",
    )
    assert model.mok_enrollment_from_result(result) is True
    assert model.mok_enrollment_from_result(
        subprocess.CompletedProcess(["mokutil"], 1, stdout="is not enrolled\n", stderr="")
    ) is False
    assert model.mok_enrollment_from_result(
        subprocess.CompletedProcess(["mokutil"], 1, stdout="", stderr="permission denied")
    ) is None


def test_guided_step_completion_skips_work_that_is_already_done():
    assert model.setup_step_completion(make_status()) == (True, True, True, True)
    assert model.setup_step_completion(make_status(module_loaded=False)) == (True, True, True, False)
    assert model.setup_step_completion(make_status(
        certificate_exists=False, enrolled=False, module_loaded=False, module_available=False,
    )) == (False, False, False, False)
    assert model.setup_step_completion(make_status(
        secure_boot="disabled", certificate_exists=False, enrolled=None, module_loaded=False,
    )) == (True, True, True, False)


def test_mok_actions_are_fixed_and_never_contain_password_or_secure_boot_bypass(monkeypatch):
    paths = {
        "sudo": "/usr/bin/sudo",
        "mokutil": "/usr/bin/mokutil",
        "modprobe": "/usr/sbin/modprobe",
        "dkms": "/usr/sbin/dkms",
        "bash": "/usr/bin/bash",
        "ptyxis": "/usr/bin/ptyxis",
    }
    monkeypatch.setattr(model.shutil, "which", lambda name: paths.get(name))
    monkeypatch.setattr(model, "valid_mok_certificate", lambda: True)

    terminal, arguments = model.privileged_terminal_spec("import")
    command = " ".join(arguments)
    assert terminal == "/usr/bin/ptyxis"
    assert "sudo /usr/bin/mokutil --import /var/lib/dkms/mok.pub" in command
    assert "password" not in command.casefold()
    assert "disable-validation" not in command
    assert "--disable-validation" not in command
    assert model.privileged_terminal_spec("unknown") is None


def test_key_generation_is_only_available_while_certificate_is_missing(monkeypatch):
    paths = {
        "sudo": "/usr/bin/sudo",
        "dkms": "/usr/sbin/dkms",
        "bash": "/usr/bin/bash",
        "xterm": "/usr/bin/xterm",
    }
    monkeypatch.setattr(model.shutil, "which", lambda name: paths.get(name))
    monkeypatch.setattr(model, "valid_mok_certificate", lambda: False)
    spec = model.privileged_terminal_spec("generate")
    assert spec is not None
    assert spec[1][-3:] == ["/usr/bin/sudo", "/usr/sbin/dkms", "generate_mok"]

    monkeypatch.setattr(model, "valid_mok_certificate", lambda: True)
    assert model.privileged_terminal_spec("generate") is None


def test_assistant_requires_physical_enrollment_and_never_reboots_automatically():
    dialog = (SRC / "modules/mainboard_driver_setup/v1_1/dialog.py").read_text(encoding="utf-8")
    main = (SRC / "kraken_control.py").read_text(encoding="utf-8")
    assert "Enroll MOK" in dialog and "Continue" in dialog and "physisch bestätigen" in dialog
    assert "startDetached" in dialog
    assert "reboot" not in dialog.casefold()
    assert "shutdown" not in dialog.casefold()
    assert "show_nct6687_setup_assistant(self)" in main
    assert "class Nct6687SetupDialog(QWizard)" in dialog
    assert "setup_step_completion(status)" in dialog
    assert "action_visible=not certificate_done" in dialog
    assert "action_visible=not load_done" in dialog
    assert 'process.start(sys.executable' in dialog
    assert "5 · Dauerhafte Lüfterberechtigung" in dialog
    assert "persistent_fan_authorization_enabled" in dialog
    assert "set_persistent_mainboard_fan_authorization" in dialog


def test_distribution_detection_and_commands_are_strictly_separated():
    ubuntu = distribution.distribution_from_values({
        "ID": "ubuntu", "ID_LIKE": "debian", "PRETTY_NAME": "Ubuntu 26.04.1 LTS",
    })
    fedora = distribution.distribution_from_values({"ID": "fedora", "PRETTY_NAME": "Fedora Linux 43"})
    arch = distribution.distribution_from_values({"ID": "arch", "PRETTY_NAME": "Arch Linux"})
    unsupported = distribution.distribution_from_values({"ID": "opensuse-tumbleweed"})

    ubuntu_plan = distribution.setup_plan(ubuntu, msi_x870=True)
    fedora_plan = distribution.setup_plan(fedora, msi_x870=True)
    arch_plan = distribution.setup_plan(arch, msi_x870=False)
    assert ubuntu_plan and ubuntu_plan.commands[0] == "sudo apt update"
    assert "apt install" in ubuntu_plan.commands[1] and "&&" not in ubuntu_plan.commands[0]
    assert all("dnf" not in command for command in ubuntu_plan.commands)
    assert fedora_plan and "dnf install" in fedora_plan.commands[0] and "apt" not in fedora_plan.commands[0]
    assert arch_plan and "pacman -S" in arch_plan.commands[0] and "dnf" not in arch_plan.commands[0]
    assert distribution.setup_plan(unsupported, msi_x870=True) is None
    assert all(any("https://github.com/Fred78290/nct6687d.git" in command for command in plan.commands)
               for plan in (ubuntu_plan, fedora_plan, arch_plan))
    assert all(any('git -C "$HOME/nct6687d" pull --ff-only' in command for command in plan.commands)
               for plan in (ubuntu_plan, fedora_plan, arch_plan))


def test_msi_x870_options_are_not_guessed_for_other_mainboards(tmp_path: Path):
    (tmp_path / "board_vendor").write_text("Micro-Star International Co., Ltd.\n", encoding="utf-8")
    (tmp_path / "board_name").write_text("MAG X870 TOMAHAWK WIFI (MS-7E51)\n", encoding="utf-8")
    label, msi_x870 = distribution.detect_board(tmp_path)
    assert "MAG X870 TOMAHAWK WIFI" in label and msi_x870
    ubuntu = distribution.distribution_from_values({"ID": "ubuntu"})
    personal = distribution.setup_plan(ubuntu, msi_x870=msi_x870)
    generic = distribution.setup_plan(ubuntu, msi_x870=False)
    assert personal and any("msi_fan_brute_force=1" in command for command in personal.commands)
    assert generic and not any("msi_fan_brute_force=1" in command for command in generic.commands)
