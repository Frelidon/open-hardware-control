"""Pinned Ubuntu backend preference must fail closed and preserve Fedora."""

from pathlib import Path
import stat
import sys
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.backend_updates.v1_0 import executables, policy


def test_non_ubuntu_keeps_original_commands_without_preferred_path_probe():
    with patch.object(executables, "_trusted_file") as trusted:
        assert executables.resolve_openrgb_executable("/usr/bin/openrgb", ubuntu_runtime=False) == "/usr/bin/openrgb"
        assert executables.resolve_liquidctl_executable("liquidctl", ubuntu_runtime=False) == "liquidctl"
        assert executables.preferred_backend_version("openrgb", ubuntu_runtime=False) == ""
        trusted.assert_not_called()


def test_ubuntu_preference_is_fixed_and_missing_or_untrusted_falls_back(monkeypatch):
    monkeypatch.setenv("OHC_OPENRGB", "/tmp/untrusted/openrgb")
    with patch.object(executables, "_trusted_file", return_value=True):
        assert executables.resolve_openrgb_executable(ubuntu_runtime=True) == "/usr/local/lib/open-hardware-control-backends/openrgb-1.0/openrgb"
        assert executables.resolve_liquidctl_executable(ubuntu_runtime=True) == "/usr/local/lib/open-hardware-control-backends/liquidctl-1.16.0/bin/liquidctl"
    with patch.object(executables, "_trusted_file", return_value=False):
        assert executables.resolve_openrgb_executable(ubuntu_runtime=True) == "openrgb"


def test_trust_rejects_symlinks_user_owned_or_writable_parents():
    target = executables._APPROVED_EXECUTABLES["openrgb"]
    def fake_stat(path):
        return SimpleNamespace(st_mode=(stat.S_IFREG | 0o755) if path == target else (stat.S_IFDIR | 0o755), st_uid=0)
    with patch.object(Path, "lstat", fake_stat), patch.object(executables.os, "access", return_value=True):
        assert executables._trusted_file(target, executable=True)
    for mode, uid in ((stat.S_IFLNK | 0o777, 0), (stat.S_IFREG | 0o775, 0), (stat.S_IFREG | 0o755, 1000)):
        with patch.object(Path, "lstat", return_value=SimpleNamespace(st_mode=mode, st_uid=uid)):
            assert not executables._trusted_file(target, executable=True)
    def writable_parent(path):
        result = fake_stat(path)
        if path == target.parent:
            result.st_mode = stat.S_IFDIR | 0o777
        return result
    with patch.object(Path, "lstat", writable_parent):
        assert not executables._trusted_file(target, executable=True)


def test_version_requires_trusted_matching_manifest_without_guessing(tmp_path):
    with (
        patch.dict(executables._APPROVED_ROOTS, {"openrgb": tmp_path}),
        patch.object(executables, "_trusted_file", return_value=True),
    ):
        manifest = tmp_path / "backend-version.json"
        assert executables.preferred_backend_version("openrgb", ubuntu_runtime=True) == ""
        manifest.write_text('{"component":"openrgb","version":"1.0"}')
        assert executables.preferred_backend_version("openrgb", ubuntu_runtime=True) == "1.0"
        manifest.write_text('{"component":"liquidctl","version":"1.16.0"}')
        assert executables.preferred_backend_version("openrgb", ubuntu_runtime=True) == ""


def test_audit_prefers_verified_pinned_metadata_to_stale_system_package():
    with (
        patch.object(policy, "resolve_openrgb_executable", return_value="/usr/local/lib/open-hardware-control-backends/openrgb-1.0/openrgb"),
        patch.object(policy, "preferred_backend_version", return_value="1.0"),
        patch.object(policy, "_package_version") as package,
    ):
        assert policy._installed_version("openrgb", "openrgb") == "1.0"
        package.assert_not_called()


def test_inline_summary_escapes_metadata_and_does_not_claim_unknown_is_current():
    source = (ROOT / "src/modules/backend_updates/v1_0/controller.py").read_text()
    assert 'elif not item.get("version_known", True):' in source
    assert 'installed=escape(installed), latest=escape(latest), state=escape(state)' in source
    assert "if not isValid(self)" in source


def test_cam_python_uses_only_the_approved_root_owned_venv():
    target = Path("/usr/bin/python3.14")
    with (
        patch.object(executables, "_trusted_file", return_value=True),
        patch.object(Path, "lstat", return_value=SimpleNamespace(st_mode=stat.S_IFLNK | 0o777, st_uid=0)),
        patch.object(Path, "resolve", return_value=target),
    ):
        assert executables.resolve_liquidctl_python("/usr/bin/python3", ubuntu_runtime=True) == "/usr/local/lib/open-hardware-control-backends/liquidctl-1.16.0/bin/python"
        assert executables.resolve_liquidctl_python("/usr/bin/python3", ubuntu_runtime=False) == "/usr/bin/python3"
    with (
        patch.object(executables, "_trusted_file", return_value=True),
        patch.object(Path, "lstat", return_value=SimpleNamespace(st_mode=stat.S_IFLNK | 0o777, st_uid=1000)),
    ):
        assert executables.resolve_liquidctl_python("system-python", ubuntu_runtime=True) == "system-python"
    with (
        patch.object(executables, "_trusted_file", side_effect=lambda path, **kwargs: path != target),
        patch.object(Path, "lstat", return_value=SimpleNamespace(st_mode=stat.S_IFLNK | 0o777, st_uid=0)),
        patch.object(Path, "resolve", return_value=target),
    ):
        assert executables.resolve_liquidctl_python("system-python", ubuntu_runtime=True) == "system-python"
    with patch.object(executables.sys, "frozen", True, create=True):
        assert executables.resolve_liquidctl_python("OHC.exe", ubuntu_runtime=True) == "OHC.exe"
    source = (ROOT / "src/kraken_control.py").read_text()
    assert "self.gif_process.setProgram(resolve_liquidctl_python(sys.executable))" in source
