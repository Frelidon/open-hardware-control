#!/usr/bin/env python3
"""Exercise native distribution choices with fake installers and no root writes."""

from pathlib import Path
import os
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.openlinkhub_update.v1_0 import policy  # noqa: E402


def _command(directory: Path, name: str, body: str = "exit 0") -> None:
    target = directory / name
    target.write_text(f"#!/bin/bash\n{body}\n", encoding="utf-8")
    target.chmod(0o755)


def _script_source(name: str, distro: str) -> str:
    source = (ROOT / "packaging" / name).read_text(encoding="utf-8")
    source = source.replace("if [[ -r /etc/os-release ]]; then", "if true; then")
    return source.replace("source /etc/os-release", f"ID={distro}\nID_LIKE=''\nVERSION_ID=26.04")


def _run_source(source: str, mode: str, directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/bin/bash", "-c", source, "--", mode],
        env={**os.environ, "PATH": str(directory)},
        capture_output=True, text=True, check=False, timeout=15,
    )


def _fake_package_environment(directory: Path, *, fail: bool = False) -> None:
    directory.mkdir()
    for name in ("sed", "awk", "sort", "head", "grep"):
        (directory / name).symlink_to(Path("/usr/bin") / name)
    _command(directory, "kdialog")
    _command(directory, "pkexec", 'exec "$@"')
    for manager in ("dnf", "apt-get", "pacman", "zypper"):
        _command(directory, manager, (
            'printf "%s\\n" "$0" "$@" >> "${0%/*}/commands.log"\n'
            + ('exit 42\n' if fail else '')
            + 'for arg in "$@"; do\n'
            '    case "$arg" in vkmark|gamescope)\n'
            '        printf "#!/bin/sh\\nexit 0\\n" > "${0%/*}/$arg"\n'
            '        /bin/chmod 755 "${0%/*}/$arg" ;;\n'
            '    esac\n'
            'done'
        ))


def test_benchmark_install_uses_native_manager_even_with_foreign_managers_present(tmp_path):
    cases = (
        ("ubuntu", "apt-get", ["install", "-y", "vkmark", "gamescope"]),
        ("fedora", "dnf", ["install", "-y", "vkmark", "gamescope"]),
        ("arch", "pacman", ["-S", "--needed", "--noconfirm", "vkmark", "gamescope"]),
    )
    for distro, manager, expected_args in cases:
        directory = tmp_path / distro
        _fake_package_environment(directory)
        source = _script_source("install-dependencies.sh", distro)
        result = _run_source(source, "--check-gpu-benchmark-and-install", directory)
        assert result.returncode == 0, (distro, result.stdout, result.stderr)
        assert (directory / "commands.log").read_text().splitlines() == [
            str(directory / manager), *expected_args,
        ]


def test_failed_apt_install_preserves_error_and_never_reports_success(tmp_path):
    directory = tmp_path / "ubuntu-error"
    _fake_package_environment(directory, fail=True)
    result = _run_source(
        _script_source("install-dependencies.sh", "ubuntu"),
        "--check-gpu-benchmark-and-install", directory,
    )
    assert result.returncode == 42
    assert "wurden installiert" not in result.stdout
    assert not (directory / "vkmark").exists()
    assert not (directory / "gamescope").exists()


def test_openlinkhub_update_uses_only_native_package_database(tmp_path):
    for distro, expected in (("ubuntu", "apt"), ("fedora", "dnf"), ("arch", "manual")):
        os_release = tmp_path / "os-release"
        os_release.write_text(f'ID={distro}\nID_LIKE=""\n', encoding="utf-8")
        queries = []

        def run(args):
            queries.append(args)
            return subprocess.CompletedProcess(args, 0, "0.9.0-1", "")

        def which(name):
            return f"/test/{name}" if name in {"pkexec", "dnf", "apt-get"} else None

        native = policy.package_family(os_release)
        assert native == expected
        with patch.object(policy, "package_family", return_value=native), patch.object(
            policy.shutil, "which", side_effect=which
        ), patch.object(policy, "_run", side_effect=run), patch.object(policy.Path, "home", return_value=tmp_path):
            plan = policy.update_plan()
        assert plan.method == expected
        if expected == "manual":
            assert not queries and not plan.commands
        else:
            assert {query[0] for query in queries} == {"rpm" if expected == "dnf" else "dpkg-query"}
            assert all(command[1] == f"/test/{'dnf' if expected == 'dnf' else 'apt-get'}" for command in plan.commands)


def test_trcc_check_accepts_official_package_rule_and_rejects_missing_or_wrong_usb_id(tmp_path):
    directory = tmp_path / "trcc"
    directory.mkdir()
    for name in ("sort", "head", "grep"):
        (directory / name).symlink_to(Path("/usr/bin") / name)
    _command(directory, "trcc")
    _command(directory, "dpkg-query", 'printf "%s\\n" "9.10.4-1"')
    rules_dir = tmp_path / "package-rules"
    rules_dir.mkdir()
    source = _script_source("install-trcc.sh", "ubuntu")
    real_dirs = "/etc/udev/rules.d /run/udev/rules.d /usr/local/lib/udev/rules.d /usr/lib/udev/rules.d /lib/udev/rules.d"
    assert real_dirs in source
    source = source.replace(real_dirs, f"'{rules_dir}'")
    # This fixture isolates USB rule recognition. Dedicated metadata-helper
    # trust/content verification is covered separately and must stay required
    # in production, without relying on the developer host's installation.
    check_branch = 'if [[ "$mode" == --check ]]; then'
    assert "version_ok && udev_rule_present && dmi_helper_present" in source
    source = source.replace(check_branch, "dmi_helper_present() { return 0; }\n" + check_branch)
    assert _run_source(source, "--check", directory).returncode == 10
    rule = rules_dir / "99-trcc-lcd.rules"
    rule.write_text('SUBSYSTEM=="usb", ATTR{idVendor}=="87cd", ATTR{idProduct}=="70db", MODE="0666"\n')
    assert _run_source(source, "--check", directory).returncode == 10
    rule.write_text('SUBSYSTEM=="usb", ATTR{idVendor}=="87ad", ATTR{idProduct}=="70db", MODE="0666"\n')
    assert _run_source(source, "--check", directory).returncode == 0
    without_helper = source.replace("dmi_helper_present() { return 0; }", "dmi_helper_present() { return 1; }")
    assert _run_source(without_helper, "--check", directory).returncode == 10
