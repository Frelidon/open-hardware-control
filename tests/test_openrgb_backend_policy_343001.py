from openrgb_integration import OpenRGBDevice
from modules.rgb_studio.v1_15.openrgb_backend import choose_control_path, split_control_paths


def _device(*modes, index=0):
    return OpenRGBDevice(index=index, name=f"Device {index}", modes=tuple(modes), leds=("1",))


def test_direct_stream_owns_direct_capable_device_for_exact_ohc_design():
    choice = choose_control_path(_device("Direct", "Chase"), "spinner")
    assert choice.path == "stream"
    assert choice.mode == ""


def test_direct_stream_is_used_when_no_native_mode_exists():
    choice = choose_control_path(_device("Direct"), "depthwave")
    assert choice.path == "stream"
    assert choice.mode == ""


def test_devices_are_sorted_and_each_gets_one_owner():
    choices = split_control_paths((_device("Direct", index=2), _device("Rainbow", index=1)), "rainbow")
    assert [(device.index, choice.path) for device, choice in choices] == [(1, "native"), (2, "stream")]

