#!/usr/bin/env python3
"""Hardware Fix .149 identity, privacy, and fixed-action regressions."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.hardware_fix.v1_0.profile import (  # noqa: E402
    ASSET_ROOT, CORRECTED_EDID_SHA256, MSI_VRR_PROFILE, ORIGINAL_EDID_SHA256,
    os_family, runner_argv, validate_profile_assets,
)
from modules.hardware_fix.v1_0.status import _is_profile_monitor  # noqa: E402


def test_model_is_explicit_and_profile_has_no_serial_field() -> None:
    assert MSI_VRR_PROFILE.title == "MSI MAG 274QPF X30MV – VRR"
    assert MSI_VRR_PROFILE.product == "MAG 274 X30MV"
    assert not hasattr(MSI_VRR_PROFILE, "serial")


def test_edids_are_anonymized_and_differ_only_by_vrr_flag_and_checksum() -> None:
    original = (ASSET_ROOT / "EDID/original.bin").read_bytes()
    corrected = (ASSET_ROOT / "EDID/vrr-korrigiert.bin").read_bytes()
    assert len(original) == len(corrected) == 384
    assert hashlib.sha256(original).hexdigest() == ORIGINAL_EDID_SHA256
    assert hashlib.sha256(corrected).hexdigest() == CORRECTED_EDID_SHA256
    assert all(sum(original[index:index + 128]) % 256 == 0 for index in range(0, 384, 128))
    assert all(sum(corrected[index:index + 128]) % 256 == 0 for index in range(0, 384, 128))
    assert original[72:77] == corrected[72:77] == bytes.fromhex("0000001000")
    assert not any(original[77:90]) and not any(corrected[77:90])
    assert {index for index, pair in enumerate(zip(original, corrected)) if pair[0] != pair[1]} == {0x64, 0x7F}
    assert original[0x64] == 0 and corrected[0x64] == 1
    assert _is_profile_monitor(original) and _is_profile_monitor(corrected)


def test_resources_and_actions_are_allowlisted() -> None:
    assert validate_profile_assets() == (True, "Profilressourcen geprüft.")
    assert runner_argv("install")
    assert runner_argv("game-test")
    assert runner_argv("anything-else") is None


def test_os_family_is_pure_and_bounded() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        release = Path(temporary) / "os-release"
        release.write_text('ID=linuxmint\nID_LIKE="ubuntu debian"\n', encoding="utf-8")
        assert os_family(release) == "ubuntu"
        release.write_text('ID=nobara\nID_LIKE="fedora"\n', encoding="utf-8")
        assert os_family(release) == "fedora"
        release.write_text('ID=arch\n', encoding="utf-8")
        assert os_family(release) == "unsupported"


def test_new_module_contains_no_personal_identifiers() -> None:
    private_serial = ("cf0h" + "0162" + "00165").encode("ascii")
    forbidden = (private_serial, b"/home/")
    for path in (ROOT / "src/modules/hardware_fix/v1_0").rglob("*"):
        if not path.is_file() or path.suffix == ".pyc":
            continue
        data = path.read_bytes().lower()
        for value in forbidden:
            assert value not in data, (path, value)


def test_hardware_checker_embeds_hardware_fix_subpage() -> None:
    page = (ROOT / "src/modules/hardware_checker/v1_0/page.py").read_text(encoding="utf-8")
    assert 'self.section_tabs.addTab(self.hardware_fix_panel, "Hardware Fix")' in page
    fix_page = (ROOT / "src/modules/hardware_fix/v1_0/page.py").read_text(encoding="utf-8")
    assert "Unterstützter Monitor: MSI MAG 274QPF X30MV" in fix_page
    assert "Die persönliche Monitor-Seriennummer ist nicht enthalten." in fix_page


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print("PASS", test.__name__)
