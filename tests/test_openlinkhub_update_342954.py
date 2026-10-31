#!/usr/bin/env python3
"""Tests for fixed, package-managed OpenLinkHub update plans."""

from pathlib import Path
import subprocess
import sys
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from modules.openlinkhub_update.v1_0 import policy  # noqa: E402
from modules.openlinkhub_update.v1_0 import apply_user_space  # noqa: E402


def test_version_comparison_handles_package_release_suffixes():
    assert policy.update_available("0.8.9-1", "0.9.0")
    assert not policy.update_available("0.9.0-1", "0.9.0")
    assert not policy.update_available("nicht erkannt", "0.9.0")


def test_dnf_plan_uses_only_fixed_existing_package_and_pkexec():
    def which(name: str):
        return {"pkexec": "/usr/bin/pkexec", "dnf": "/usr/bin/dnf"}.get(name)

    def run(args: list[str]):
        if args[-1] == "OpenLinkHub":
            return subprocess.CompletedProcess(args, 0, "0.8.9-1", "")
        return subprocess.CompletedProcess(args, 1, "", "missing")

    with patch.object(policy.shutil, "which", side_effect=which), patch.object(policy, "_run", side_effect=run), patch.object(policy, "package_family", return_value="dnf"):
        plan = policy.update_plan()
    assert plan.automatic and plan.method == "dnf"
    assert plan.commands == (("/usr/bin/pkexec", "/usr/bin/dnf", "upgrade", "--refresh", "-y", "OpenLinkHub"),)


def test_manual_install_never_receives_an_automatic_command(tmp_path):
    with patch.object(policy.shutil, "which", return_value=None), patch.object(policy.Path, "home", return_value=tmp_path):
        plan = policy.update_plan()
    assert not plan.automatic
    assert plan.commands == ()


def test_existing_home_user_service_gets_digest_protected_update_route(tmp_path):
    install = tmp_path / "OpenLinkHub"
    install.mkdir()
    binary = install / "OpenLinkHub"
    binary.write_bytes(b"binary")
    log = install / "stdout.log"
    log.write_text('{"buildVersion":"0.9.0"}\n', encoding="utf-8")
    service_dir = tmp_path / ".config/systemd/user"
    service_dir.mkdir(parents=True)
    (service_dir / "OpenLinkHub.service").write_text(
        f"[Service]\nWorkingDirectory={install}\nExecStart={binary}\n", encoding="utf-8"
    )
    with patch.object(policy.shutil, "which", return_value=None), patch.object(policy.Path, "home", return_value=tmp_path):
        plan = policy.update_plan()
    assert plan.automatic and plan.method == "user-space"
    assert plan.installed_version == "0.9.0"
    assert plan.commands == ()


def test_updater_has_fixed_official_origin_and_bounded_response():
    assert policy.RELEASE_API == "https://api.github.com/repos/jurkovic-nikola/OpenLinkHub/releases/latest"
    assert policy.MAX_RELEASE_BYTES == 512 * 1024
    source = (SRC / "modules/openlinkhub_update/v1_0/policy.py").read_text(encoding="utf-8")
    assert "shell=True" not in source


def test_user_space_apply_preserves_profiles_and_keeps_recoverable_backup(tmp_path):
    install = tmp_path / "OpenLinkHub"
    (install / "database/profiles").mkdir(parents=True)
    (install / "OpenLinkHub").write_bytes(b"old")
    (install / "config.json").write_text('{"custom":true}', encoding="utf-8")
    (install / "database/profiles/user.json").write_text('{"fan":55}', encoding="utf-8")
    service_dir = tmp_path / ".config/systemd/user"
    service_dir.mkdir(parents=True)
    (service_dir / "OpenLinkHub.service").write_text(
        f"[Service]\nWorkingDirectory={install}\nExecStart={install / 'OpenLinkHub'}\n", encoding="utf-8"
    )
    cache = tmp_path / ".cache/ohc"
    stage = cache / "stage-0.9.1"
    (stage / "web").mkdir(parents=True)
    (stage / "database").mkdir()
    (stage / "OpenLinkHub").write_bytes(b"new")
    (stage / "database/new-default.json").write_text("{}", encoding="utf-8")
    with patch.object(apply_user_space.Path, "home", return_value=tmp_path), patch.object(apply_user_space, "_run_systemctl") as systemctl:
        result = apply_user_space.apply_update(stage, cache)
    assert result["installed"] == str(install)
    assert (install / "OpenLinkHub").read_bytes() == b"new"
    assert (install / "config.json").read_text(encoding="utf-8") == '{"custom":true}'
    assert (install / "database/profiles/user.json").is_file()
    assert (install / "database/new-default.json").is_file()
    assert Path(result["backup"]).joinpath("OpenLinkHub").read_bytes() == b"old"
    assert [call.args[0] for call in systemctl.call_args_list] == ["stop", "daemon-reload", "start"]
