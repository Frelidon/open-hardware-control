"""GPU/support strip continuity, pairing authority and real per-header counts."""
import copy
import json
import os
from pathlib import Path

import pytest
from PySide6.QtWidgets import QCheckBox
from test_slot_argb_routes_342985 import APP, Host, MSI, HUB, SLOT
from openrgb_integration import OpenRGBDevice
from rgb_devices import RGBLayoutSlot
from rgb_effects import RGBEffectConfig, render_effect, render_hex_frame, hex_to_rgb
from localization_catalog import UI_TRANSLATIONS
from modules.rgb_studio.v1_15.gpu_strip_sampling import render_gpu_strip_frame, strip_plan, strip_clock
from modules.rgb_studio.v1_15.gpu_lighting import GpuLightingMixin
from modules.rgb_studio.v1_15.gpu_support_sync import KEY, pair
from modules.rgb_studio.v1_15.led_topology_store import KEY as PATH_KEY
from modules.rgb_studio.v1_15.led_topology import render_physical_frame
from modules.rgb_studio.v1_15.slot_routes import KEY as ROUTE_KEY
from modules.rgb_studio.v1_15.argb_diagnostics import log_effect_plan
from modules.rgb_studio.v1_15.gpu_motion import DEFAULT, KEY as MOTION_KEY, load as load_motion, normalize as normalize_motion, paced_elapsed
from modules.rgb_studio.v1_15.gpu_motion_editor import GpuMotionEditor
from PySide6.QtWidgets import QSlider

GPU = OpenRGBDevice(2, "Sapphire RX 9070 XT", device_type="GPU",
                    modes=("External Control", "Rainbow Wave"), leds=("GPU",))
PATH = dict(kind="line", start="left", end="right", units=1, clockwise=True)


def jump(frames):
    return max(abs(a - b) for first, second in zip(frames, frames[1:])
               for left, right in zip(first, second) for a, b in zip(left, right))


@pytest.mark.parametrize("effect", ["spinner", "comet"])
@pytest.mark.parametrize("speed", [83, 110, 200])
@pytest.mark.parametrize("count", [12, 30, 80])
def test_open_strip_heads_are_smoother_at_25_hz_and_across_cycle_reset(effect, speed, count):
    config = RGBEffectConfig(effect, "000000", "ffffff", speed=speed)
    plan = strip_plan(config, count)
    clock = strip_clock(config, count)
    reset = clock["cycle"] / clock["rate"]
    times = [i / 25 for i in range(260)] + [reset + (i - 20) / 25 for i in range(40)]
    frames = [[hex_to_rgb(c) for c in render_gpu_strip_frame(config, count, t)] for t in times]
    limit = 40 if count <= 30 else 64
    assert jump(frames[:260]) < limit
    assert jump(frames[260:]) < limit
    expected_cycles_per_second = (.18 if effect == "comet" else .24) * speed / 100
    assert clock["rate"] / clock["cycle"] == pytest.approx(expected_cycles_per_second)
    assert all(len(f) == count and all(0 <= c <= 255 for color in f for c in color) for f in frames)
    assert plan["leds_per_second"] <= 7.68


def sync_host(language="de"):
    host = Host(language=language)
    host.rgb_device_display_name = lambda device: device.name
    host.openrgb_devices = [GPU, MSI, HUB]
    host.openrgb_stable_ids[2] = "openrgb:gpu"
    host.rgb_selected_devices = set(host.openrgb_stable_ids.values())
    host.rgb_gpu_routes = {"openrgb:gpu": dict(controller="openrgb:msi", zone="JARGB 1")}
    host.rgb_group_assignments = {"openrgb:gpu": "gpu"}
    host.rgb_group_effect_configs = {"gpu": RGBEffectConfig("comet", speed=83)}
    host.rgb_layout_slots.append(RGBLayoutSlot("gpu-support", "GPU support", 1, "gpu-support",
                                             "", (), "gpu-support", .5, .6))
    host.settings.setValue(ROUTE_KEY, json.dumps({"gpu-support": dict(controller="openrgb:hub", zone="Channel B6")}))
    host.rgb_zone_configurations["openrgb:hub"] = {"Channel A1": dict(units=2, leds_per_unit=8),
                                                  "Channel B6": dict(units=1, leds_per_unit=12)}
    host.log_message = host.calls.append
    return host


def test_gpu_and_support_ignore_both_saved_zone_packet_experiments():
    host = sync_host()
    config = RGBEffectConfig("spinner", "0000ff", "ffffff")
    host.settings.setValue("rgb_studio/gpu_zone_packets_v1", True)
    host.settings.setValue("rgb_studio/gpu_zone_packets_v2", True)
    host.settings.setValue("rgb_studio/support_zone_packets_v2", True)
    msi = GpuLightingMixin.rgb_worker_render_payload(host, "openrgb:msi", MSI, config, 46, [30, 8, 8], 1.)
    hub = GpuLightingMixin.rgb_worker_render_payload(host, "openrgb:hub", HUB, config, 28, [16, 12], 1.)
    assert "zone_updates" not in msi and "zone_updates" not in hub
    host.close()


def test_case_preview_animates_routed_fans_gpu_support_and_ram():
    from modules.pc_case_profiles.v1_5.case_animation import build_specs, frame
    from modules.pc_case_profiles.v1_5.diagram import PCLayoutDiagram
    host = sync_host()
    host.rgb_layout_slots.append(RGBLayoutSlot("gpu", "GPU", 1, "gpu", "", ("openrgb:gpu",), "gpu", .5, .5))
    ram_a = OpenRGBDevice(6, "ENE A", modes=("Direct",), zones=("Unknown",))
    ram_b = OpenRGBDevice(7, "ENE B", modes=("Direct",), zones=("Unknown",))
    host.openrgb_devices.extend((ram_a, ram_b))
    host.openrgb_stable_ids.update({6: "openrgb:ram-a", 7: "openrgb:ram-b"})
    host.rgb_zone_configurations.update({"openrgb:ram-a": {"Unknown": {"units": 1, "leds_per_unit": 8}},
                                         "openrgb:ram-b": {"Unknown": {"units": 1, "leds_per_unit": 8}}})
    host.rgb_layout_slots.append(RGBLayoutSlot("ram", "RAM", 2, "ram", "",
                                                ("openrgb:ram-a", "openrgb:ram-b"), "ram", .5, .3))
    config = RGBEffectConfig("spinner", "0000ff", "ffffff", speed=100)
    host.openrgb_effect_assignments = {key: config for key in ("openrgb:msi", "openrgb:hub", "openrgb:ram-a", "openrgb:ram-b")}
    host.openrgb_effect_active = True
    host.rgb_last_sent_elapsed = host.rgb_gpu_visual_elapsed = 4.
    routes = {"gpu-support": dict(controller="openrgb:hub", zone="Channel B6"),
              "front-slot": dict(controller="openrgb:hub", zone="Channel A1")}
    host.settings.setValue(ROUTE_KEY, json.dumps(routes))
    fan_path = dict(kind="ring", start="top", end="bottom", units=2, clockwise=True)
    specs = build_specs(host, host.rgb_layout_slots, {"front-slot": (fan_path, 16)})
    assert {"front-slot", "gpu", "gpu-support", "ram"} <= specs.keys()
    before = {key: frame(host, specs[key]) for key in ("front-slot", "gpu", "gpu-support", "ram")}
    assert tuple(map(len, before.values())) == (16, 30, 12, 16)
    diagram = PCLayoutDiagram()
    diagram.set_slots(host.rgb_layout_slots)
    diagram.set_led_animations(specs, host)
    diagram.show(); APP.processEvents()
    assert diagram.animation_timer.isActive()
    assert not diagram.grab().isNull()
    host.rgb_last_sent_elapsed = host.rgb_gpu_visual_elapsed = 5.
    after = {key: frame(host, specs[key]) for key in before}
    assert all(after[key] != before[key] for key in before)
    diagram.hide(); APP.processEvents()
    assert not diagram.animation_timer.isActive()
    host.openrgb_effect_active = False
    assert frame(host, specs["gpu"]) == ()
    host.close()


def test_gpu_and_support_use_same_clock_config_and_retain_other_header_frames():
    host = sync_host()
    config = RGBEffectConfig("spinner", primary="ff0000")
    before = copy.deepcopy((host.settings.data, host.rgb_zone_configurations, host.mainboard_layout_assignments))
    linked = pair(host, config)
    assert linked["count"] == 30 and linked["config"] == host.rgb_group_effect_configs["gpu"]
    gpu = GpuLightingMixin.render_gpu_controller_frame(host, "openrgb:msi", MSI, config, 46, [30, 8, 8], 1.4)
    support = GpuLightingMixin.render_gpu_controller_frame(host, "openrgb:hub", HUB, config, 28, [16, 12], 1.4)
    assert gpu[:30] == render_gpu_strip_frame(linked["config"], 30, 1.4, sync_count=30,
                                               tuning=load_motion(host))
    assert gpu[30:] == render_hex_frame(config, 8, 1.4) * 2
    assert support[:16] == render_hex_frame(config, 16, 1.4)
    assert support[16:] == render_gpu_strip_frame(linked["config"], 12, 1.4, sync_count=30,
                                                  tuning=load_motion(host), role="support")
    assert (host.settings.data, host.rgb_zone_configurations, host.mainboard_layout_assignments) == before
    assert host.calls == []
    host.settings.setValue(PATH_KEY, json.dumps({"openrgb:hub": {
        "Channel A1": {**PATH, "kind": "ring", "units": 2, "direction": "top-bottom"},
        "Channel B6": {**PATH, "direction": "left-right"},
    }}))
    log_effect_plan(host, HUB, config)
    assert any("count=12 · clock_count=30" in line and "support_sync=1" in line for line in host.calls)
    assert any("zone=Channel A1" in line and "layout=Ring" in line
               and "case_direction=top-bottom" in line for line in host.calls)
    host.close()


def test_motion_editor_shows_real_counts_and_saves_only_on_commit(monkeypatch):
    from PySide6.QtWidgets import QDialog, QPushButton
    host = sync_host()
    host.build_gpu_lighting_dialog = lambda *args: GpuLightingMixin.build_gpu_lighting_dialog(host, *args)
    dialog, *_ = host.build_gpu_lighting_dialog(GPU, "openrgb:gpu", [MSI, HUB])
    editor = dialog.findChild(GpuMotionEditor, "gpuMotionEditor")
    assert editor.gpu_count == 30 and editor.support_count == 12
    host.openrgb_effect_active = True
    host.rgb_gpu_visual_elapsed = 4.25
    assert editor.elapsed() == 4.25
    host.openrgb_effect_active = False
    assert "30 LEDs" in editor.gpu_label.text() and "12 LEDs" in editor.support_label.text()
    host.openrgb_worker_metrics = {"openrgb:msi": {"success_times": [1., 1.05, 1.1]},
                                   "openrgb:hub": {"success_times": [1., 1.1, 1.2]}}
    editor.refresh()
    assert "20.0 Hz" in editor.transport.text() and "10.0 Hz" in editor.transport.text()
    dialog.findChild(QSlider, "gpuMotionGpuLead").setValue(45)
    assert load_motion(host)["gpu_lead"] == 40
    assert host.rgb_gpu_motion_preview["gpu_lead"] == 45
    assert host.rgb_gpu_motion_preview["gpu_peak"] == 65
    dialog.findChild(QSlider, "gpuMotionGpuPeak").setValue(55)
    assert host.rgb_gpu_motion_preview["gpu_peak"] == 55
    reset = next(button for button in dialog.findChildren(QPushButton)
                 if button.objectName() == "gpuMotionReset")
    reset.click()
    assert editor.values() == DEFAULT and host.rgb_gpu_motion_preview == DEFAULT
    dialog.reject()
    assert load_motion(host)["gpu_lead"] == 40
    assert host.rgb_gpu_motion_preview is None

    def commit(active):
        active.findChild(QSlider, "gpuMotionGpuLead").setValue(45)
        next(button for button in active.findChildren(QPushButton)
             if button.text() == "Steuerweg speichern").click()
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(QDialog, "exec", commit)
    GpuLightingMixin.configure_gpu_lighting(host, GPU)
    assert load_motion(host)["gpu_lead"] == 45
    assert host.rgb_gpu_motion_preview is None
    assert load_motion(host)["support_lead"] == 32
    assert MOTION_KEY in host.settings.data
    host.close()


def test_slow_transport_keeps_wall_time_and_both_physical_counts_share_tuning():
    from modules.rgb_studio.v1_15.render_plan import build, render
    host = sync_host()
    config = RGBEffectConfig("spinner", "000000", "ffffff", speed=110)
    host.settings.setValue(MOTION_KEY, json.dumps({"gpu_lead": 45, "gpu_tail": 45,
                                                    "support_lead": 32, "support_tail": 36,
                                                    "tempo": 70}))
    GpuLightingMixin.update_rgb_gpu_visual_elapsed(host, .01)
    GpuLightingMixin.update_rgb_gpu_visual_elapsed(host, .21)
    # A 200-ms multi-device batch must not turn into only 60 ms of visual
    # progress. That old clamp accumulated permanent slow motion in both the
    # physical LEDs and the Case preview whenever OpenRGB missed 25 Hz.
    assert host.rgb_gpu_visual_elapsed == pytest.approx(.20)
    assert paced_elapsed(.06, .04) == pytest.approx(.10)
    assert paced_elapsed(.20, .40) == pytest.approx(.60)
    assert load_motion(host)["tempo"] == 70
    gpu = GpuLightingMixin.render_gpu_controller_frame(host, "openrgb:msi", MSI, config, 46, [30, 8, 8], .21)
    support = GpuLightingMixin.render_gpu_controller_frame(host, "openrgb:hub", HUB, config, 28, [16, 12], .21)
    assert len(gpu[:30]) == 30 and len(support[16:]) == 12
    assert gpu[:30] == render_gpu_strip_frame(host.rgb_group_effect_configs["gpu"], 30, .20,
                                               sync_count=30, tuning=load_motion(host))
    assert support[16:] == render_gpu_strip_frame(host.rgb_group_effect_configs["gpu"], 12, .20,
                                                  sync_count=30, tuning=load_motion(host), role="support")
    assert render(build(host, "openrgb:msi", MSI, config, .21), 46, [30, 8, 8]) == gpu
    assert render(build(host, "openrgb:hub", HUB, config, .21), 28, [16, 12]) == support
    clock = strip_clock(host.rgb_group_effect_configs["gpu"], 30, load_motion(host))
    host.rgb_gpu_visual_elapsed = (clock["padding"] + .5) / clock["rate"]
    bright_gpu = GpuLightingMixin.render_gpu_controller_frame(host, "openrgb:msi", MSI, config, 46, [30, 8, 8], .21)
    bright_support = GpuLightingMixin.render_gpu_controller_frame(host, "openrgb:hub", HUB, config, 28, [16, 12], .21)
    updated = dict(load_motion(host), gpu_lead=50)
    host.settings.setValue(MOTION_KEY, json.dumps(updated))
    changed_gpu = GpuLightingMixin.render_gpu_controller_frame(host, "openrgb:msi", MSI, config, 46, [30, 8, 8], .21)
    unchanged_support = GpuLightingMixin.render_gpu_controller_frame(host, "openrgb:hub", HUB, config, 28, [16, 12], .21)
    assert changed_gpu[:30] != bright_gpu[:30]
    assert unchanged_support == bright_support
    host.close()


def test_live_gpu_slider_reaches_existing_worker_plan_and_cancel_restores_saved_frame():
    from modules.rgb_studio.v1_15.render_plan import build, render
    host = sync_host()
    config = RGBEffectConfig("spinner", "0000ff", "ffffff", speed=100)
    host.rgb_group_effect_configs["gpu"] = config
    host.rgb_gpu_visual_elapsed = 10.
    stored = render(build(host, "openrgb:msi", MSI, config, 10.), 46, [30, 8, 8])
    dialog, *_ = GpuLightingMixin.build_gpu_lighting_dialog(host, GPU, "openrgb:gpu", [MSI, HUB])
    dialog.findChild(QSlider, "gpuMotionGpuPeak").setValue(40)
    live = render(build(host, "openrgb:msi", MSI, config, 10.), 46, [30, 8, 8])
    assert live[:30] != stored[:30] and live[30:] == stored[30:]
    assert load_motion(host)["gpu_peak"] == 65
    dialog.reject()
    restored = render(build(host, "openrgb:msi", MSI, config, 10.), 46, [30, 8, 8])
    assert restored == stored and host.rgb_gpu_motion_preview is None
    host.close()


def test_untrusted_motion_preferences_fall_back_and_invalid_clock_fails_closed():
    assert normalize_motion({"gpu_lead": True, "gpu_tail": 40, "tempo": 70}) == DEFAULT
    assert normalize_motion({"gpu_lead": 45, "gpu_tail": 45, "tempo": 70})["gpu_lead"] == 45
    assert normalize_motion({"gpu_lead": 45, "gpu_tail": 45, "tempo": 70})["gpu_peak"] == 65
    for value in (-1., float("nan")):
        with pytest.raises(ValueError):
            paced_elapsed(0., value)


@pytest.mark.parametrize("case", ["off", "missing-binding", "missing-gpu", "unselected-gpu", "unselected-support",
                                 "conflict-gpu", "conflict-support", "invalid-count", "ring"])
def test_pairing_never_selects_or_guesses_missing_blocked_or_unassigned_devices(case):
    host = sync_host()
    if case == "off": host.settings.setValue(KEY, False)
    elif case == "missing-binding": host.settings.setValue(ROUTE_KEY, "{}")
    elif case == "missing-gpu": host.rgb_gpu_routes = {}
    elif case == "unselected-gpu": host.rgb_selected_devices.remove("openrgb:gpu")
    elif case == "unselected-support": host.rgb_selected_devices.remove("openrgb:hub")
    elif case == "conflict-gpu": host.blocked.add(2)
    elif case == "conflict-support": host.blocked.add(4)
    elif case == "invalid-count": host.rgb_zone_configurations["openrgb:hub"]["Channel B6"]["leds_per_unit"] = True
    else: host.settings.setValue(PATH_KEY, json.dumps({"openrgb:hub": {"Channel B6": {**PATH, "kind": "ring"}}}))
    before = copy.deepcopy((host.settings.data, host.rgb_selected_devices))
    assert pair(host, RGBEffectConfig("comet")) is None
    assert (host.settings.data, host.rgb_selected_devices) == before and host.calls == []
    host.close()


def test_strip_direction_paths_ring_and_nonmoving_fallbacks():
    config = RGBEffectConfig("comet", "000000", "ffffff")
    down = render_gpu_strip_frame(config, 30, 1.5, PATH, "left-right")
    reverse = {**PATH, "start": "right", "end": "left"}
    assert render_gpu_strip_frame(config, 30, 1.5, reverse, "left-right") == down[::-1]
    for effect in ("static", "breathing", "rainbow", "wave", "lightning", "sparkle", "pulse", "alternating"):
        cfg = RGBEffectConfig(effect)
        assert render_gpu_strip_frame(cfg, 30, .7) == render_hex_frame(cfg, 30, .7)
    ring = {**PATH, "kind": "ring", "units": 3}
    assert render_gpu_strip_frame(config, 30, .7, ring, "left-right") == render_physical_frame(config, 30, .7, ring, "left-right")
    assert render_gpu_strip_frame(RGBEffectConfig("comet", brightness=0), 30, 1) == ["000000"] * 30
    for bad in (True, 0, 4097):
        with pytest.raises(ValueError): render_gpu_strip_frame(config, bad, 1)


def test_gpu_renderer_errors_do_not_silently_revert_to_sharp_generic_effect():
    from modules.rgb_studio.v1_15.gpu_routing import render_zone_frame
    config = RGBEffectConfig("spinner", "0000ff", "ffffff")
    with pytest.raises(ValueError):
        render_zone_frame(config, 30, [30], ["JARGB 1"], {}, 1.,
                          paths={"JARGB 1": PATH}, direction="invalid",
                          gpu_zones={"JARGB 1"})


def test_30_led_gpu_strip_keeps_blue_body_around_compact_white_head():
    config = RGBEffectConfig("spinner", "0000ff", "ffffff", speed=100)
    clock = strip_clock(config, 30)
    elapsed = (clock["padding"] + .5) / clock["rate"]
    frame = [hex_to_rgb(value) for value in render_gpu_strip_frame(config, 30, elapsed)]
    assert len(frame) == 30
    assert min(color[2] for color in frame) >= 45
    assert sum(min(color) >= 170 for color in frame) <= 8


@pytest.mark.parametrize("effect", ["spinner", "comet"])
def test_approaching_gpu_pixels_and_departing_pixels_fade_before_stepping(effect):
    config = RGBEffectConfig(effect, "000000", "ffffff", speed=100)
    clock = strip_clock(config, 30)
    elapsed = (clock["padding"] + .5) / clock["rate"]
    frame = [hex_to_rgb(value)[0] for value in render_gpu_strip_frame(config, 30, elapsed)]
    assert frame[6] > frame[0] and frame[22] > frame[-1]
    assert max(abs(a - b) for a, b in zip(frame, frame[1:])) <= 45
    assert sum(value >= 170 for value in frame) <= 8


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
def test_sync_checkbox_localized_cancel_read_only_and_rendered(language):
    host = sync_host(language)
    before = copy.deepcopy(host.settings.data)
    dialog, *_ = GpuLightingMixin.build_gpu_lighting_dialog(host, GPU, "openrgb:gpu", [MSI, HUB])
    checkbox = dialog.findChild(QCheckBox, "gpuSupportSync")
    assert checkbox.isChecked() and checkbox.text() == UI_TRANSLATIONS[language]["GPU und Halterung synchronisieren"]
    assert dialog.findChild(QCheckBox, "gpuZonePackets") is None
    assert dialog.findChild(QCheckBox, "supportZonePackets") is None
    checkbox.setChecked(False)
    assert dialog.findChild(GpuMotionEditor, "gpuMotionEditor").rows[1].isHidden()
    assert host.settings.data == before
    if os.environ.get("OHC_UI_RENDER_DIR"):
        dialog.show(); APP.processEvents()
        assert dialog.grab().save(str(Path(os.environ["OHC_UI_RENDER_DIR"]) / f"gpu-sync-{language}.png"))
    dialog.reject()
    assert host.settings.data == before
    host.close()


def test_pair_checkbox_commit_persists_and_does_not_modify_led_counts(monkeypatch):
    from PySide6.QtWidgets import QDialog, QPushButton
    host = sync_host()
    host.build_gpu_lighting_dialog = lambda *args: GpuLightingMixin.build_gpu_lighting_dialog(host, *args)
    counts = copy.deepcopy(host.rgb_zone_configurations)
    def save(dialog):
        dialog.findChild(QCheckBox, "gpuSupportSync").setChecked(False)
        next(b for b in dialog.findChildren(QPushButton) if b.text() == "Steuerweg speichern").click()
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(QDialog, "exec", save)
    GpuLightingMixin.configure_gpu_lighting(host, GPU)
    assert host.settings.value(KEY) is False and host.rgb_zone_configurations == counts
    reopened, *_ = host.build_gpu_lighting_dialog(GPU, "openrgb:gpu", [MSI, HUB])
    assert not reopened.findChild(QCheckBox, "gpuSupportSync").isChecked()
    reopened.reject(); host.close()


@pytest.mark.parametrize("effect", ["static", "breathing", "rainbow", "wave", "lightning", "sparkle", "pulse", "alternating"])
def test_paired_nonmoving_effects_share_virtual_clock_without_resizing_headers(effect):
    config = RGBEffectConfig(effect)
    gpu = render_gpu_strip_frame(config, 30, .7, sync_count=30)
    support = render_gpu_strip_frame(config, 12, .7, sync_count=30)
    assert len(gpu) == 30 and len(support) == 12
    assert support[0] == gpu[0] and support[-1] == gpu[-1]
