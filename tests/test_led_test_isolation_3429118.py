"""A GPU connected to the tested ARGB header must remain in External Control."""
from types import SimpleNamespace

from test_gpu_strip_smoothing_342989 import GPU, MSI, sync_host
from modules.rgb_studio.v1_15.led_test_isolation import commands


def test_linked_gpu_is_rearmed_after_other_devices_are_darkened():
    host = sync_host()
    host.openrgb_client = SimpleNamespace(native_mode_command=lambda *args: ['external', *args])
    seen = []
    def blackout(target_id='', *, exclude_ids=(), only_selected=False):
        seen.append((target_id, set(exclude_ids), only_selected))
        return [['other-leds', '000000']], []
    host.build_rgb_device_test_commands = blackout
    prefix = commands(host, MSI, 'JARGB 1')
    assert seen == [('', {'openrgb:msi', 'openrgb:gpu'}, True)]
    assert prefix == [['other-leds', '000000'], ['external', GPU.index, 'External Control', ['ffffff'], 100]]
    host.close()


def test_unrelated_header_does_not_switch_gpu_to_external_control():
    host = sync_host()
    host.openrgb_client = SimpleNamespace(native_mode_command=lambda *args: ['external', *args])
    host.build_rgb_device_test_commands = lambda _target='', *, exclude_ids=(), only_selected=False: ([['other-leds', '000000']], [])
    assert commands(host, MSI, 'JARGB 2') == [['other-leds', '000000']]
    host.close()
