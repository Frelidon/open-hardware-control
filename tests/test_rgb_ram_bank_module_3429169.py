"""The extracted bank dialog preserves inspection and ownership boundaries."""
from types import SimpleNamespace

import pytest

from modules.rgb_studio.v1_15.ram_bank import RgbRamBankMixin


def host(*, reachable=True, external=False):
    errors, inspected = [], []
    devices = [SimpleNamespace(index=0), SimpleNamespace(index=1)]
    return SimpleNamespace(
        openrgb_server_reachable=reachable,
        openrgb_external_server_detected=external,
        openrgb_devices=devices,
        is_rgb_ram_device=lambda device: True,
        openrgb_device_conflict=lambda device: False,
        rgb_device_display_name=lambda device: f"RAM {device.index}",
        show_error=errors.append, errors=errors,
        footer_status=SimpleNamespace(setText=lambda text: None),
        show_openrgb_ram_bank_dialog=inspected.append, inspected=inspected,
    )


@pytest.mark.parametrize("reachable,external", [(False, False), (True, True)])
def test_unavailable_or_foreign_engine_cannot_inspect(reachable, external):
    state = host(reachable=reachable, external=external)
    RgbRamBankMixin.configure_openrgb_ram_bank(state)
    assert len(state.errors) == 1
    assert not state.inspected


def test_bank_inspects_each_device_serially_before_opening_dialog():
    state = host()
    calls = []
    state.openrgb_client = SimpleNamespace(sdk_inspect_command=lambda index: [str(index)])
    def inspect(command, *, callback, timeout, log_output):
        calls.append(command)
        callback(SimpleNamespace(ok=True, stdout='{"zones":[{"name":"RAM","current":8}]}'))
    state.backend = SimpleNamespace(run_async=inspect)
    RgbRamBankMixin.configure_openrgb_ram_bank(state)
    assert calls == [["0"], ["1"]]
    assert not state.errors
    assert len(state.inspected) == 1
    assert [device.index for device, payload in state.inspected[0]] == [0, 1]


def test_conflicting_devices_are_not_used_as_a_ram_bank():
    state = host()
    state.openrgb_device_conflict = lambda device: True
    RgbRamBankMixin.configure_openrgb_ram_bank(state)
    assert len(state.errors) == 1
    assert not state.inspected
