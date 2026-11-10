"""Persistent exit lighting must run before RGB ownership is released."""

from pathlib import Path
from types import SimpleNamespace
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openrgb_integration import OpenRGBDevice  # noqa: E402
from modules.rgb_studio.v1_15.shutdown_lighting import (  # noqa: E402
    COLOR_KEY,
    MODE_KEY,
    RAINBOW,
    STATIC,
    ShutdownLightingMixin,
    load,
    normalize_color,
    normalize_mode,
)


class Settings:
    def __init__(self, values=None):
        self.values = dict(values or {})

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value

    def sync(self):
        pass


DIRECT = OpenRGBDevice(0, "Direct", modes=("Direct", "Rainbow Wave"), zones=("ARGB",), leds=("1", "2", "3"))
NATIVE = OpenRGBDevice(1, "Native", modes=("Static", "Rainbow"), leds=("1",))


def host(mode=STATIC, color="ffffff"):
    state = SimpleNamespace(
        settings=Settings({MODE_KEY: mode, COLOR_KEY: color}),
        rgb_shutdown_lighting_mode=mode,
        rgb_shutdown_lighting_color=color,
        openrgb_write_enabled=True,
        openrgb_external_server_detected=False,
        openrgb_server_reachable=True,
        selected_openrgb_devices=lambda: [DIRECT, NATIVE],
        selected_nzxt_rgb_channels=lambda: ["led1"],
        openrgb_device_conflict=lambda _device: "",
        openrgb_device_write_shape=lambda _device: (3, (3,)),
        rgb_device_display_name=lambda device: device.name,
        log=[],
    )
    state.log_message = state.log.append
    state.openrgb_client = SimpleNamespace(
        sdk_color_command=lambda device, colors, count, **kwargs: [
            "sdk", str(device), ",".join(colors), str(count), str(kwargs.get("zone_sizes"))
        ],
        native_mode_command=lambda device, native, colors, brightness: [
            "native", str(device), native, ",".join(colors), str(brightness)
        ],
    )
    state._openrgb_static_shutdown_command = ShutdownLightingMixin._openrgb_static_shutdown_command.__get__(state)
    state._openrgb_shutdown_commands = ShutdownLightingMixin._openrgb_shutdown_commands.__get__(state)
    state._run_rgb_shutdown_command = lambda command, **_kwargs: (state.commands.append(command) or True, "")
    state.commands = []
    state.tr_static = lambda text: text
    return state


def test_default_is_white_static_and_invalid_values_fail_closed():
    assert load(SimpleNamespace(settings=Settings())) == (STATIC, "ffffff")
    assert normalize_mode("unknown") == STATIC
    assert normalize_color("#12ABef") == "12abef"
    assert normalize_color("not-a-colour") == "ffffff"


def test_static_exit_uses_direct_sdk_native_static_and_nzxt_fixed():
    state = host(STATIC, "aabbcc")
    ShutdownLightingMixin.apply_rgb_shutdown_lighting_sync(state, "manuelles Programmende")
    assert state.commands[0][:4] == ["sdk", "0", "aabbcc,aabbcc,aabbcc", "3"]
    assert state.commands[1][:4] == ["native", "1", "Static", "aabbcc"]
    assert any("fixed" in command and "aabbcc" in command for command in state.commands)
    assert any("erfolgreich=3" in message for message in state.log)


def test_rainbow_exit_uses_only_reported_native_modes_and_nzxt_hardware_effect():
    state = host(RAINBOW, "ffffff")
    ShutdownLightingMixin.apply_rgb_shutdown_lighting_sync(state, "manuelles Programmende")
    assert state.commands[0][2] == "Rainbow Wave"
    assert state.commands[1][2] == "Rainbow"
    assert any("rainbow-flow" in command for command in state.commands)


def test_restart_and_missing_write_consent_never_write():
    state = host()
    ShutdownLightingMixin.apply_rgb_shutdown_lighting_sync(state, "Programmneustart")
    assert not state.commands
    state.openrgb_write_enabled = False
    ShutdownLightingMixin.apply_rgb_shutdown_lighting_sync(state, "manuelles Programmende")
    assert not state.commands


def test_exit_phase_precedes_lock_and_engine_release():
    source = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
    start = source.index("def perform_orderly_hardware_exit")
    finish = source.index("def request_application_restart", start)
    method = source[start:finish]
    assert method.index('run.run("rgb-effect"') < method.index('run.run("rgb-shutdown-light"')
    assert method.index('run.run("rgb-shutdown-light"') < method.index('run.run("rgb-lock"')
    assert method.index('run.run("rgb-lock"') < method.index('run.run("rgb-engine"')
