# SPDX-License-Identifier: GPL-3.0-or-later
"""Legacy setup/start-profile separation; no Qt, user settings or hardware I/O."""

import ast
import copy
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.cooling_state.v1_0.startup_policy import pending_setup_blocks_profile_start
from thermalright_cooling import LEVITA_COOLER_KEY


def policy(pending="quiet", **overrides):
    values = dict(
        ubuntu_runtime=True, thermalright_present=True,
        nzxt_ready=False, cooling_kind=LEVITA_COOLER_KEY,
    )
    values.update(overrides)
    return pending_setup_blocks_profile_start(pending, **values)


@pytest.mark.parametrize("pending", ["quiet", "balanced", "performance", "safe"])
@pytest.mark.parametrize("cooling_kind", ["auto", LEVITA_COOLER_KEY])
def test_known_legacy_presets_do_not_block_confirmed_ubuntu_levita(pending, cooling_kind):
    assert not policy(pending, cooling_kind=cooling_kind)


@pytest.mark.parametrize("override", [
    {"ubuntu_runtime": False},  # Fedora/Arch/non-Ubuntu preserve the old guard.
    {"thermalright_present": False},
    {"nzxt_ready": True},
    {"cooling_kind": "nzxt"},
    {"cooling_kind": "unknown"},
])
@pytest.mark.parametrize("pending", ["quiet", "balanced", "performance", "safe"])
def test_other_platforms_unconfirmed_or_real_nzxt_keep_pending_barrier(override, pending):
    assert policy(pending, **override)


@pytest.mark.parametrize("pending", ["other", "user-cooling-preset", " quiet", "None"])
def test_unknown_pending_intent_is_not_silently_bypassed(pending):
    assert policy(pending)


def test_empty_pending_does_not_introduce_a_new_barrier():
    assert not policy("", ubuntu_runtime=False, thermalright_present=False)


def extracted_methods(namespace):
    """Execute the exact host methods against memory-only test doubles."""
    names = {
        "apply_startup_profile", "startup_profile_has_lcd_payload",
        "apply_profile_by_id", "apply_pending_setup_profile",
    }
    tree = ast.parse((ROOT / "src/kraken_control.py").read_text(encoding="utf-8"))
    host_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "KrakenControl")
    methods = [node for node in host_class.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert len(methods) == len(names)
    exec(compile(ast.Module(body=methods, type_ignores=[]), "host_startup_methods", "exec"), namespace)
    return SimpleNamespace(**{name: namespace[name] for name in names})


class Settings:
    def __init__(self, startup="user-start"):
        self.values = {"profiles/startup": startup, "setup/pending_profile": "quiet"}
        self.writes = []

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.writes.append((key, value))
        self.values[key] = value


def scenario(*, ubuntu=True, thermalright=True, pending="quiet", startup="user-start", nzxt=False):
    namespace = {
        "pending_setup_blocks_profile_start": pending_setup_blocks_profile_start,
        "is_ubuntu_runtime": Mock(return_value=ubuntu),
        "thermalright_display_present": Mock(return_value=thermalright),
    }
    methods = extracted_methods(namespace)
    payload = {
        "rgb": {"studio_autostart_enabled": True, "studio_auto_reclaim_enabled": True},
        "levita_display": {"source": "synthetic-library-design"},
        "cooling": {"pump_mode": "cpu", "fan_mode": "cpu", "pump_curve": [[30, 70], [90, 100]]},
    }
    profiles = [{"id": "user-start", "name": "Synthetic PC", "payload": payload}]
    state = SimpleNamespace(
        settings=Settings(startup), pending_setup_profile=pending,
        devices_ready=nzxt, cooling_hardware_kind=LEVITA_COOLER_KEY,
        kraken_write_busy=False, current_profile_id="user-start",
        all_profiles=lambda: profiles, apply_profile_payload=Mock(), apply_quick_profile=Mock(),
    )
    state.apply_profile_by_id = lambda profile_id, **kwargs: methods.apply_profile_by_id(state, profile_id, **kwargs)
    return methods, state, namespace, payload


@pytest.mark.parametrize("startup", ["last", "user-start"])
def test_real_host_methods_start_only_the_explicit_profile_and_preserve_cooling_intent(startup):
    methods, state, namespace, payload = scenario(startup=startup)
    unchanged_payload = copy.deepcopy(payload)
    methods.apply_pending_setup_profile(state)
    methods.apply_startup_profile(state)
    assert methods.startup_profile_has_lcd_payload(state)
    state.apply_profile_payload.assert_called_once_with(payload, "Synthetic PC", startup=True)
    assert payload == unchanged_payload  # No stripping, manufacturing or reinterpreting cooling intent.
    state.apply_quick_profile.assert_not_called()  # The old NZXT preset never becomes a PWM command.
    assert state.pending_setup_profile == "quiet"
    assert state.settings.writes == []
    assert namespace["thermalright_display_present"].call_count == 2


@pytest.mark.parametrize("ubuntu,thermalright,nzxt", [(False, True, False), (True, False, False), (True, True, True)])
def test_real_host_guards_preserve_fedora_missing_levita_and_real_nzxt(ubuntu, thermalright, nzxt):
    methods, state, _namespace, _payload = scenario(ubuntu=ubuntu, thermalright=thermalright, nzxt=nzxt)
    methods.apply_startup_profile(state)
    assert not methods.startup_profile_has_lcd_payload(state)
    state.apply_profile_payload.assert_not_called()
    assert state.pending_setup_profile == "quiet"
    assert state.settings.writes == []


@pytest.mark.parametrize("pending,startup", [("unknown", "user-start"), ("quiet", "none"), ("", "none")])
def test_unknown_pending_and_no_selected_start_profile_never_acquire_ownership(pending, startup):
    methods, state, _namespace, _payload = scenario(pending=pending, startup=startup)
    methods.apply_startup_profile(state)
    assert not methods.startup_profile_has_lcd_payload(state)
    state.apply_profile_payload.assert_not_called()
    assert state.settings.writes == []


def test_empty_pending_preserves_the_original_fast_path_without_new_probes():
    methods, state, namespace, payload = scenario(pending="")
    methods.apply_startup_profile(state)
    assert methods.startup_profile_has_lcd_payload(state)
    state.apply_profile_payload.assert_called_once_with(payload, "Synthetic PC", startup=True)
    namespace["is_ubuntu_runtime"].assert_not_called()
    namespace["thermalright_display_present"].assert_not_called()


def test_nzxt_assistant_application_is_unchanged_and_consumes_only_its_ready_preset():
    methods, state, _namespace, _payload = scenario(nzxt=True)
    state.cooling_hardware_kind = "nzxt"
    methods.apply_pending_setup_profile(state)
    state.apply_quick_profile.assert_called_once_with("Leise", 45, 35)
    assert state.pending_setup_profile == ""
    assert state.settings.writes == [("setup/pending_profile", "")]


def test_policy_and_host_stay_inside_module_and_orchestrator_budgets():
    main = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
    pure = (ROOT / "src/modules/cooling_state/v1_0/startup_policy.py").read_text(encoding="utf-8")
    assert len(main.splitlines()) <= 23_300
    assert len(pure.splitlines()) <= 600 and len(pure) < 32_000
    assert "PySide" not in pure and "subprocess" not in pure
    assert "settings.setValue" not in pure
