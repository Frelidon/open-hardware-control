#!/usr/bin/env python3
"""Windows preview contracts for the next OHC build."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.control_authority.v1_0.model import authority_choices, ohc_may_write  # noqa: E402
from modules.hardware_checker.v1_0.probe import normalize_windows_inventory  # noqa: E402
from modules.platform_support.v1_0 import current_platform, platform_display_name  # noqa: E402


def test_windows_automatic_authority_is_fail_closed():
    assert not ohc_may_write("rgb", "auto", "win32")
    assert ohc_may_write("rgb", "ohc_openrgb", "win32")
    auto = authority_choices("rgb", "win32")[0]
    assert "Konfliktschutz" in auto.label
    assert not auto.ohc_writes


def test_platform_labels_are_not_hardcoded_to_linux():
    assert current_platform("win32") == "windows"
    assert platform_display_name("win32") == "Windows"
    assert platform_display_name("linux") == "Linux"
    main = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
    assert '— {platform_display_name()}' in main


def test_windows_cim_inventory_maps_to_hardware_checker_schema():
    report = normalize_windows_inventory({
        "cpu": {"Name": "AMD Ryzen Test", "NumberOfCores": 8,
                "NumberOfLogicalProcessors": 16, "SocketDesignation": "AM5",
                "VirtualizationFirmwareEnabled": True},
        "board": {"Manufacturer": "Micro-Star International Co., Ltd.",
                  "Product": "MAG X870 TOMAHAWK WIFI (MS-7E51)", "Version": "1.0"},
        "gpus": [{"Name": "AMD Radeon Test", "DriverVersion": "1.2.3"}],
        "nvmes": [{"Model": "Fast NVMe", "InterfaceType": "NVMe"}],
        "memory": [{"Manufacturer": "Memory Co", "PartNumber": "TEST-6000",
                    "Capacity": 17179869184, "Speed": 6000,
                    "ConfiguredClockSpeed": 6000, "DeviceLocator": "DIMM A2"}],
        "system": {"TotalPhysicalMemory": 34359738368},
    })
    assert report["cpu"]["model"] == "AMD Ryzen Test"
    assert report["cpu"]["smt_state"] == "enabled"
    assert report["socket"] == "AM5"
    assert report["board"]["vendor"] == "MSI"
    assert report["gpus"][0]["name"] == "AMD Radeon Test"
    assert report["memory_modules"][0]["configured_mts"] == 6000
    assert report["memory_total"] == "32.0 GiB"


def test_windows_packaging_scaffold_exists():
    for relative in (
        "packaging/windows/OpenHardwareControl.spec",
        "packaging/windows/requirements-windows.txt",
        "scripts/build_windows.ps1",
        ".github/workflows/windows-preview.yml",
    ):
        assert (ROOT / relative).is_file(), relative


def test_wallpaper_engine_has_a_safe_windows_handoff():
    page = (ROOT / "src/modules/wallpaper_engine/v1_3/page.py").read_text(encoding="utf-8")
    assert "default_steam_library" in page
    assert 'QUrl("steam://rungameid/431960")' in page
    assert "if self.windows_mode:" in page
    assert "build_select_script" in page


def test_background_profile_restore_errors_are_inline_not_modal():
    main = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
    start = main.index("def report_profile_apply_error")
    body = main[start:main.index("\n\ndef install_session_signal_handlers", start)]
    assert "self.log_message" in body
    assert "self.footer_status.setText" in body
    assert "QMessageBox" not in body
    assert main.count("self.report_profile_apply_error(name, str(exc), component=\"Levita-Kühlung\")") >= 2


def test_linux_desktop_entry_uses_short_favorites_name():
    desktop = (ROOT / "packaging/kraken-control.desktop.in").read_text(encoding="utf-8")
    assert "Name=OHC\n" in desktop
    assert "GenericName=Open Hardware Control by Frelidon\n" in desktop
