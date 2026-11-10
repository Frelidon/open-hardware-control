# SPDX-License-Identifier: GPL-3.0-or-later
"""OpenRGB 1.0 CLI inventory regressions, without hardware or subprocess I/O."""

import ast
import copy
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openrgb_integration import OpenRGBClient, OpenRGBError, parse_device_listing
from rgb_devices import prepare_openrgb_devices


def fixture_listing(*, detailed):
    # Shapes observed in the owner's report; all identities are synthetic.
    devices = (
        ("ENE DRAM", "DRAM", 8, ("Unknown",)),
        ("ENE DRAM", "DRAM", 8, ("Unknown",)),
        ("MSI MYSTIC LIGHT", "Motherboard", 30, ("JAF", "JARGB 1", "JARGB 2", "JARGB 3")),
        ("Airgoo AG-DRGB16", "LED Strip", 114, ("Channel A1", "Channel B8")),
        ("Sony DualSense", "Gamepad", 6, ("Lightbar", "Player LEDs")),
    )
    lines = []
    for index in range(10):
        name, kind, count, zones = devices[index % 5]
        lines.append(f"{index}: {name}")
        if detailed:
            lines.extend((
                f"  Type: {kind}",
                "  Description: Synthetic inventory fixture",
                f"  Location: Fixture hardware path {index % 5}",
                "  Modes: [Direct] Static Breathing",
                "  Zones: " + " ".join(repr(zone) for zone in zones),
                "  LEDs: " + " ".join(f"LED{led}" for led in range(count)),
            ))
    return "\n".join(lines)


@pytest.mark.parametrize("ubuntu,version,expected", [
    (True, "1.0", "--list-detailed"),
    (True, "1.1-qt6.11-ohc-native", "--list-detailed"),
    (True, "0.9", "--list-devices"),
    (True, "", "--list-devices"),
    (False, "1.0", "--list-devices"),
])
def test_inventory_option_matches_trusted_backend_without_changing_fedora(tmp_path, ubuntu, version, expected):
    executable = tmp_path / "openrgb"
    executable.touch()
    client = OpenRGBClient(str(executable), ubuntu_runtime=ubuntu)
    with patch("openrgb_integration.resolve_openrgb_executable", return_value=str(executable)), patch(
        "openrgb_integration.preferred_backend_version", return_value=version,
    ), patch.object(client, "server_reachable", return_value=True):
        command = client.list_command()
    assert command == [str(executable), "--client", "127.0.0.1:6742", *(["--nodetect"] if ubuntu else []), expected]
    # 1.0 --noautoconnect also disables its explicit client connection.
    assert "--noautoconnect" not in command


def test_explicit_old_executable_is_not_upgraded_by_another_installed_backend(tmp_path):
    executable = tmp_path / "old-openrgb"
    executable.touch()
    client = OpenRGBClient(str(executable), ubuntu_runtime=True)
    with patch("openrgb_integration.resolve_openrgb_executable", return_value="/trusted/openrgb-1.0"), patch(
        "openrgb_integration.preferred_backend_version", return_value="1.0",
    ) as version, patch.object(client, "server_reachable", return_value=True):
        assert client.list_command()[-1] == "--list-devices"
    version.assert_not_called()


def test_detailed_inventory_retains_counts_modes_and_stable_identity_after_mirror_merge():
    listing = fixture_listing(detailed=True)
    prepared = prepare_openrgb_devices(parse_device_listing(listing, require_details=True))
    assert [device.reported_led_count for device in prepared.devices] == [8, 8, 30, 114, 6]
    assert all(device.supports_direct and device.zones for device in prepared.devices)
    assert len(prepared.duplicate_aliases_removed) == 5
    # The 0.9 detailed format and 1.0 --list-detailed retain the same schema.
    previous = prepare_openrgb_devices(parse_device_listing(listing))
    assert prepared.stable_ids == previous.stable_ids
    compact = prepare_openrgb_devices(parse_device_listing(fixture_listing(detailed=False)))
    assert compact.stable_ids != prepared.stable_ids


@pytest.mark.parametrize("output", [fixture_listing(detailed=False), "0: Complete\n  Type: Unknown\n1: Incomplete"])
def test_strict_inventory_rejects_all_or_partially_missing_details(output):
    with pytest.raises(OpenRGBError):
        parse_device_listing(output, require_details=True)
    assert parse_device_listing("", require_details=True) == []


@pytest.mark.parametrize("output,count,direct", [
    ("0: Empty Controller\n  Type: Unknown", 0, False),
    ("0: Empty Header\n  Type: Motherboard\n  Modes: [Direct]", 0, True),
    ("0: Zonaless Hardware Light\n  Type: LED Strip\n  Modes: [Static]\n  LEDs: Logo", 1, False),
])
def test_legitimate_empty_or_zoneless_detailed_controllers_are_not_name_only(output, count, direct):
    # Official 0.9 and 1.0 CLI omit list fields whose count is zero; only
    # Type is unconditional. Absence must not be replaced by invented LEDs.
    device = parse_device_listing(output, require_details=True)[0]
    assert device.reported_led_count == count
    assert device.zones == () and device.supports_direct == direct


def test_read_devices_does_not_return_successful_names_only_inventory(tmp_path):
    executable = tmp_path / "openrgb"
    executable.touch()
    client = OpenRGBClient(str(executable), ubuntu_runtime=False)
    completed = subprocess.CompletedProcess([], 0, fixture_listing(detailed=False), "")
    with patch.object(client, "server_reachable", return_value=True), patch(
        "openrgb_integration.subprocess.run", return_value=completed,
    ), pytest.raises(OpenRGBError):
        client.read_devices()


def test_actual_refresh_discards_compact_result_before_settings_routes_or_design_actions():
    tree = ast.parse((ROOT / "src/kraken_control.py").read_text(encoding="utf-8"))
    window = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "KrakenControl")
    method = next(node for node in window.body if isinstance(node, ast.FunctionDef) and node.name == "refresh_rgb_studio")
    namespace = {
        "CommandResult": object, "OpenRGBError": OpenRGBError,
        "parse_device_listing": parse_device_listing,
        "prepare_openrgb_devices": lambda *_args: pytest.fail("Incomplete metadata reached identity preparation"),
        "running_ckb_next_process_ids": lambda: (),
    }
    exec(compile(ast.Module([method], type_ignores=[]), "actual_inventory_refresh", "exec"), namespace)
    previous = prepare_openrgb_devices(parse_device_listing(fixture_listing(detailed=True)))
    persisted = {
        "selected_devices": list(previous.stable_ids),
        "slot_routes": {"gpu": {"controller_id": previous.stable_ids[2], "zone_name": "JARGB 1"}},
        "active_pc_profile": {"hardware": {"selected_devices": list(previous.stable_ids)}},
    }
    before = copy.deepcopy(persisted)
    logs, saves, actions = [], [], []
    label = SimpleNamespace(setText=lambda _text: None)
    result = SimpleNamespace(ok=True, stdout=fixture_listing(detailed=False))
    state = SimpleNamespace(
        hardware_io_disabled=False, openrgb_status_busy=False, openrgb_discovery_generation=7,
        openrgb_client=SimpleNamespace(installed=True, endpoint="127.0.0.1:6742", server_reachable=lambda: True, list_command=lambda: ["fixture"]),
        openrgb_engine_owned=True, conflicting_openrgb_process_ids=lambda: (),
        openrgb_server_label=label, openrgb_device_count_label=label,
        openrgb_devices=list(previous.devices), openrgb_stable_ids=dict(enumerate(previous.stable_ids)),
        rgb_selected_devices=set(previous.stable_ids), rgb_slot_routes=persisted["slot_routes"],
        settings=SimpleNamespace(setValue=lambda *args: saves.append(args)),
        backend=SimpleNamespace(run_async=lambda _command, *, callback, **_kwargs: callback(result)),
        log_message=logs.append, openrgb_write_enable_pending=True, rgb_profile_autostart_pending=True,
        finish_pending_rgb_write_action=lambda: actions.append("write"),
        populate_openrgb_devices=lambda: actions.append("rebuild"),
        update_main_connection_summary=lambda: actions.append("summary"),
    )
    namespace["refresh_rgb_studio"](state, background=True)
    assert state.openrgb_devices == list(previous.devices)
    assert state.openrgb_stable_ids == dict(enumerate(previous.stable_ids))
    assert state.rgb_selected_devices == set(previous.stable_ids)
    assert persisted == before and saves == actions == []
    assert state.openrgb_write_enable_pending and state.rgb_profile_autostart_pending
    assert not state.openrgb_status_busy
    assert any("incomplete-inventory=discarded" in text for text in logs)
