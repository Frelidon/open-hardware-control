#!/usr/bin/env python3
"""Regression guards for the official backend update overview."""

from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.backend_updates.v1_0 import policy  # noqa: E402


def test_versions_distinguish_stable_from_release_candidate() -> None:
    assert policy.version_is_newer("1.0~rc2-3.fc44", "1.0")
    assert policy.version_is_newer("0.9.0", "0.9.2")
    assert not policy.version_is_newer("9.10.4-1.fc44", "v9.10.4")
    assert not policy.version_is_newer("nicht installiert", "1.0")


def test_openrgb_selects_only_a_stable_official_release() -> None:
    payload = '<h3>Release Candidate 1.1rc1 (October 1, 2026)</h3><h3>Release 1.0 (September 11, 2026)</h3><h3>Release 0.9 (July 9, 2023)</h3>'
    with patch.object(policy, "_read_text", return_value=payload):
        version, url = policy._openrgb_latest(1.0)
    assert version == "1.0"
    assert url == "https://codeberg.org/OpenRGB/OpenRGB/releases/tag/release_1.0"


def test_backend_audit_keeps_failures_local_and_read_only() -> None:
    with (
        patch.object(policy, "_installed_version", return_value="1.0~rc2-3.fc44"),
        patch.object(policy, "_github_latest", side_effect=OSError("offline")),
        patch.object(policy, "_github_tag_latest", side_effect=OSError("offline")),
        patch.object(policy, "_coolercontrol_latest", side_effect=OSError("offline")),
        patch.object(policy, "_openrgb_latest", return_value=("1.0", policy.OPENRGB_RELEASES_URL)),
        patch.object(policy, "openlinkhub_update_plan") as openlinkhub,
    ):
        openlinkhub.return_value.installed_version = "0.9.0"
        openlinkhub.return_value.automatic = True
        result = policy.collect_backend_updates(timeout=0.1)
    assert result["ok"] is True
    assert len(result["components"]) == 12
    openrgb = next(item for item in result["components"] if item["name"] == "OpenRGB")
    assert openrgb["update_available"] is True
    source = (ROOT / "src/modules/backend_updates/v1_0/policy.py").read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "dnf install" not in source


def test_ubuntu_installed_version_uses_installed_dpkg_state_only() -> None:
    import subprocess
    with (
        patch.object(policy.shutil, "which", side_effect=lambda name: "/usr/bin/dpkg-query" if name == "dpkg-query" else None),
        patch.object(policy, "_run", return_value=subprocess.CompletedProcess([], 0, "installed\t1:0.10.1-0", "")) as run,
    ):
        assert policy._installed_version("lact", "lact") == "1:0.10.1-0"
        assert run.call_args.args[0] == ["dpkg-query", "-W", "-f=${db:Status-Status}\t${Version}", "lact"]
    with (
        patch.object(policy.shutil, "which", side_effect=lambda name: "/usr/bin/dpkg-query" if name == "dpkg-query" else None),
        patch.object(policy, "_run", return_value=subprocess.CompletedProcess([], 0, "config-files\t1.0", "")),
        patch.object(policy, "resolve_openrgb_executable", return_value=""),
    ):
        assert policy._installed_version("openrgb", "openrgb") == policy.NOT_INSTALLED


def test_fedora_metadata_and_untracked_install_are_not_changed_or_hardware_probed() -> None:
    with (
        patch.object(policy.shutil, "which", side_effect=lambda name: "/usr/bin/rpm" if name == "rpm" else None),
        patch.object(policy, "_rpm_version", return_value="0.9.0-1.fc44") as rpm,
        patch.object(policy, "resolve_openrgb_executable", return_value=""),
    ):
        assert policy._installed_version("openrgb", "openrgb") == "0.9.0-1.fc44"
        rpm.assert_called_once_with("openrgb")
    with (
        patch.object(policy.shutil, "which", side_effect=lambda name: "/opt/trcc" if name == "trcc" else None),
        patch.object(policy, "_package_version", return_value=policy.NOT_INSTALLED),
        patch.object(policy, "_run") as run,
    ):
        assert policy._installed_version("trcc", "trcc-linux") == policy.UNKNOWN_VERSION
        run.assert_not_called()


def test_tag_only_releases_skip_candidates_and_sort_numerically() -> None:
    with patch.object(policy, "_read_json", return_value=[
        {"name": "3.16.9"}, {"name": "3.16.28"}, {"name": "3.17.0-rc1"}, {"name": "steam-2026-09"},
    ]):
        version, url = policy._github_tag_latest("ValveSoftware/gamescope", 0.1)
    assert version == "3.16.28"
    assert url.endswith("/3.16.28")
    with patch.object(policy, "_read_text", return_value="## [Unreleased]\n## [5.0.1] - 2026-09-16\n## [5.0.0] - 2026-09-06\n"):
        assert policy._coolercontrol_latest(0.1)[0] == "5.0.1"
