"""The calibration preview isolates LEDs and restores the running design."""
import time

import pytest

from test_gpu_strip_smoothing_342989 import GPU, HUB, MSI, sync_host
from rgb_effects import RGBEffectConfig
from modules.rgb_studio.v1_15.gpu_motion import DEFAULT, RANGES
from modules.rgb_studio.v1_15.gpu_motion_editor import GpuMotionEditor
from modules.rgb_studio.v1_15.gpu_motion_wizard import GpuMotionWizard, prepare, smoother
from modules.rgb_studio.v1_15.render_plan import build, render


def running_host():
    host = sync_host()
    config = RGBEffectConfig('spinner', 'ff0000', '00ff00', speed=100)
    host.rgb_group_effect_configs['gpu'] = config
    host.openrgb_effect_assignments = {'openrgb:msi': config, 'openrgb:hub': config}
    host.openrgb_effect_active = True
    host.openrgb_write_enabled = True
    host.openrgb_external_server_detected = False
    host.openrgb_server_reachable = True
    host.rgb_header_preview_depth = 0
    host.openrgb_worker_metrics = {}
    host.openrgb_worker_frame_sequence = 4
    host.selected_openrgb_devices = lambda: [GPU, MSI, HUB]
    host.selected_nzxt_rgb_channels = lambda: []
    host.openrgb_device_write_shape = lambda device: ((46, (30, 8, 8)) if device is MSI else (28, (16, 12)))
    host.start_openrgb_effect = lambda: host.calls.append('restore-design')
    host.rgb_last_effect_request_signature = 'original'
    return host


def test_smoother_steps_are_bounded_and_preserve_support_and_brightness():
    candidate = dict(DEFAULT)
    for _ in range(20):
        next_candidate = smoother(candidate)
        if next_candidate is None:
            break
        assert next_candidate['tempo'] <= candidate['tempo']
        assert next_candidate['gpu_lead'] >= candidate['gpu_lead']
        assert next_candidate['gpu_tail'] >= candidate['gpu_tail']
        assert {key: next_candidate[key] for key in ('gpu_peak', 'support_lead', 'support_tail')} == {
            key: DEFAULT[key] for key in ('gpu_peak', 'support_lead', 'support_tail')}
        candidate = next_candidate
    assert candidate['tempo'] == RANGES['tempo'][0]
    assert smoother(candidate) is None


def test_other_controller_zones_go_black_only_during_calibration():
    host = running_host()
    config = host.openrgb_effect_assignments['openrgb:msi']
    normal_gpu = render(build(host, 'openrgb:msi', MSI, config, 4.), 46, [30, 8, 8])
    normal_support = render(build(host, 'openrgb:hub', HUB, config, 4.), 28, [16, 12])
    host.rgb_gpu_calibration_targets = {'openrgb:msi': {'JARGB 1'}, 'openrgb:hub': {'Channel B6'}}
    gpu = render(build(host, 'openrgb:msi', MSI, config, 4.), 46, [30, 8, 8])
    support = render(build(host, 'openrgb:hub', HUB, config, 4.), 28, [16, 12])
    assert gpu[:30] != normal_gpu[:30] and gpu[30:] == ['000000'] * 16
    assert support[:16] == ['000000'] * 16 and support[16:] != normal_support[16:]
    assert build(host, 'openrgb:msi', MSI, config, 4.)['overrides']['JARGB 1']['primary'] == '0000ff'
    assert build(host, 'openrgb:hub', HUB, config, 4.)['overrides']['Channel B6']['secondary'] == 'ffffff'
    with pytest.raises(ValueError, match='RENDER_CALIBRATION_SHAPE'):
        render(build(host, 'openrgb:msi', MSI, config, 4.), 46, None)
    host.rgb_gpu_calibration_targets = None
    assert render(build(host, 'openrgb:msi', MSI, config, 4.), 46, [30, 8, 8]) == normal_gpu
    host.close()


def test_wizard_waits_for_both_frames_and_ten_seconds_then_cancel_restores():
    host = running_host()
    editor = GpuMotionEditor(host, 'openrgb:gpu')
    editor.set_route('openrgb:msi', 'JARGB 1')
    plan, reason = prepare(host, editor)
    assert reason == '' and plan[1] == {'openrgb:msi', 'openrgb:hub'}
    wizard = GpuMotionWizard(editor, plan)
    wizard.timer.stop()
    assert not wizard.again.isEnabled() and not wizard.accept_button.isEnabled()
    assert host.rgb_gpu_calibration_targets == plan[0]
    host.openrgb_worker_metrics = {key: {'last_success': time.monotonic(), 'last_frame_id': 5}
                                   for key in plan[1]}
    wizard.tick()
    assert not wizard.again.isEnabled()
    wizard.hold_at -= 10.2
    wizard.tick()
    assert wizard.again.isEnabled() and wizard.accept_button.isEnabled()
    wizard.again.click()
    assert editor.values()['tempo'] == 90 and not wizard.accept_button.isEnabled()
    wizard.reject()
    assert editor.values() == DEFAULT
    assert host.rgb_gpu_calibration_targets is None
    assert host.rgb_header_preview_depth == 0
    assert host.calls.count('restore-design') == 1
    editor.close(); host.close()


def test_wizard_refuses_missing_active_pair_without_changing_leds():
    host = running_host()
    editor = GpuMotionEditor(host, 'openrgb:gpu')
    editor.set_route('openrgb:msi', 'JARGB 1')
    host.openrgb_effect_assignments.pop('openrgb:hub')
    plan, reason = prepare(host, editor)
    assert plan is None and reason
    assert not hasattr(host, 'rgb_gpu_calibration_targets')
    editor.close(); host.close()


def test_wizard_prepares_blackout_for_other_selected_ohc_leds():
    host = running_host()
    editor = GpuMotionEditor(host, 'openrgb:gpu')
    editor.set_route('openrgb:msi', 'JARGB 1')
    seen = []
    def blackout(_target='', *, exclude_ids=(), only_selected=False):
        seen.append((set(exclude_ids), only_selected))
        return [['other-controller-black']], ['unwritable device']
    host.build_rgb_device_test_commands = blackout
    plan, reason = prepare(host, editor)
    assert not reason and plan[2] == [['other-controller-black']]
    assert seen == [({'openrgb:msi', 'openrgb:hub', 'openrgb:gpu'}, True)]
    assert any('unwritable device' in message for message in host.calls)
    editor.close(); host.close()
