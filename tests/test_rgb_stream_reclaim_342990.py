"""Precautionary RAM commands must not reset unrelated strip/fan clocks."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
import time
import sys
import pytest
from PySide6.QtCore import QProcess
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from modules.rgb_studio.v1_15.stream_reclaim import begin, release
from modules.rgb_studio.v1_15.ene_start_recovery import EneDramStartRecoveryMixin
from modules.rgb_studio.v1_15.gpu_lighting import GpuLightingMixin

def host():
    devices = [SimpleNamespace(index=i, supports_direct=True, ram=i == 0) for i in range(3)]
    return SimpleNamespace(openrgb_devices=devices, rgb_selected_devices={"ram", "gpu", "support"},
                           openrgb_stable_ids={0: "ram", 1: "gpu", 2: "support"},
                           is_ene_dram_device=lambda device: device.ram,
                           openrgb_sdk_ready_devices={"ram", "gpu", "support"},
                           openrgb_worker_frame_sequence=42)


def test_only_selected_actual_ram_ids_are_excluded():
    state = host(); lease = begin(state, ("ram", "gpu", "missing", "support"))
    assert lease == {"ram"} and state.rgb_reclaim_drain_sequence == 42
    release(state, lease)
    assert not state.rgb_reclaim_stream_exclusions
    assert state.openrgb_sdk_ready_devices == {"gpu", "support"}


def test_unselected_ram_never_enters_a_lease():
    state = host(); state.rgb_selected_devices.remove("ram")
    assert not begin(state, ("ram",))


@pytest.mark.parametrize("invalidate", ["stop", "new"])
def test_stale_lease_cannot_restore_reset_or_new_intent(invalidate):
    state = host(); lease = begin(state, ("ram",))
    state.rgb_reclaim_stream_exclusions = frozenset() if invalidate == "stop" else frozenset({"new"})
    release(state, lease)
    assert state.openrgb_sdk_ready_devices == {"ram", "gpu", "support"}
    assert state.rgb_reclaim_stream_exclusions == (set() if invalidate == "stop" else {"new"})


def test_actual_frames_continue_gpu_and_support_at_the_same_elapsed_clock():
    tree = ast.parse((ROOT / "src/kraken_control.py").read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "KrakenControl")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "send_openrgb_effect_frame")
    namespace = {"time": time, "json": json, "QProcess": QProcess, "OpenRGBError": ValueError}
    exec(compile(ast.Module([method], type_ignores=[]), "actual-frame", "exec"), namespace)
    state = host(); begin(state, ("ram",))
    state.openrgb_effect_active = True
    state.openrgb_process_check_at = time.monotonic() + 100
    state.openrgb_effect_started = time.monotonic() - 10
    started = state.openrgb_effect_started
    state.openrgb_effect_assignments = {"ram": object(), "gpu": object(), "support": object()}
    assignments = dict(state.openrgb_effect_assignments)
    payloads, elapsed = [], []
    state.openrgb_effect_process = SimpleNamespace(state=lambda: QProcess.ProcessState.Running,
                                                  write=lambda data: payloads.append(json.loads(data)) or len(data))
    state.openrgb_device_conflict = lambda _device: False
    state.openrgb_worker_ready = True
    state.openrgb_native_plugin_active = False
    state.openrgb_worker_frame_inflight = False
    state.rgb_pending_design_snapshot = None
    state.openrgb_device_write_shape = lambda _device: (30, None)
    state.render_gpu_controller_frame = lambda *_args: elapsed.append(_args[-1]) or ["112233"] * 30
    state.update_rgb_gpu_visual_elapsed = lambda wall: GpuLightingMixin.update_rgb_gpu_visual_elapsed(state, wall)
    namespace["send_openrgb_effect_frame"](state)
    assert {device["key"] for device in payloads[0]["devices"]} == {"gpu", "support"}
    assert len(elapsed) == 2 and elapsed[0] == elapsed[1] == 0
    assert state.rgb_visual_elapsed == 0
    assert state.rgb_gpu_visual_elapsed == 0.
    assert state.openrgb_effect_started == started and state.openrgb_effect_assignments == assignments
    state.openrgb_worker_frame_inflight = False
    release(state, state.rgb_reclaim_stream_exclusions)
    namespace["send_openrgb_effect_frame"](state)
    assert 0. <= state.rgb_visual_elapsed == state.rgb_gpu_visual_elapsed <= .06
    assert {device["key"] for device in payloads[1]["devices"]} == {"ram", "gpu", "support"}
    assert next(device for device in payloads[1]["devices"] if device["key"] == "ram")["prepare"]


def test_running_retry_does_not_reapply_or_reset_design_phase():
    state = host(); events = []
    for key in ("openrgb_write_enabled", "openrgb_server_reachable", "openrgb_effect_active"):
        setattr(state, key, True)
    for key in ("openrgb_external_server_detected", "rgb_reset_in_progress", "ene_dram_cli_prime_in_progress"):
        setattr(state, key, False)
    state.ene_dram_post_start_retry_index = 0
    state.ene_dram_cli_prime_done = {"ram"}
    state.rgb_active_design_title = "Neon"
    state.ene_dram_post_start_retry_timer = SimpleNamespace(start=lambda ms: events.append(ms), stop=lambda: None)
    state.selected_openrgb_devices = lambda: state.openrgb_devices[:1]
    state.log_message = lambda _message: None
    state.request_rgb_direct_apply = lambda _ms: pytest.fail("full effect reset")
    state.prime_ene_dram_cold_start = lambda callback: callback()
    EneDramStartRecoveryMixin._retry_ene_dram_profile_start(state)
    assert events == [120_000] and state.ene_dram_post_start_retry_index == 1
    assert not state.ene_dram_post_start_preserve_stream


def test_actual_reclaim_drains_only_last_ram_frame_without_starving_other_frames():
    tree = ast.parse((ROOT / "src/kraken_control.py").read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "KrakenControl")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "run_rgb_command_sequence")
    queued, commands, stopped, results = [], [], [], []
    namespace = {"Path": Path, "QTimer": SimpleNamespace(singleShot=lambda ms, callback: queued.append((ms, callback))),
                 "OpenRGBError": ValueError, "CommandResult": object}
    exec(compile(ast.Module([method], type_ignores=[]), "actual-reclaim", "exec"), namespace)
    state = host()
    state.run_rgb_command_sequence = namespace["run_rgb_command_sequence"].__get__(state)
    state.openrgb_write_enabled = state.openrgb_effect_active = True
    state.openrgb_worker_frame_inflight = True
    state.openrgb_effect_assignments = {"ram": object(), "gpu": object(), "support": object()}
    state.openrgb_effect_started = 123.5
    state.conflicting_openrgb_process_ids = lambda: []
    state.capture_rgb_scroll_position = lambda: (0, 0, 0)
    state.openrgb_effect_timer = SimpleNamespace(stop=lambda: stopped.append(True), start=lambda: None)
    state.backend = SimpleNamespace(run_async=lambda command, **kw: commands.append((command, kw["callback"])))
    state.footer_status = state.openrgb_effect_status = SimpleNamespace(setText=lambda _text: None)
    state.log_message = state.update_openrgb_control_state = state.update_rgb_selection_summary = lambda *_args: None
    state.restore_rgb_scroll_position = lambda *_args, **_kw: None
    state.rgb_direct_apply_pending = False
    state.openrgb_device_from_command = lambda _command: ("", None)
    state.rgb_device_id_from_command = lambda _command: ""
    state.rgb_device_aliases = {}; state.rgb_device_last_results = {}
    state.run_rgb_command_sequence([["synthetic-openrgb", "direct"]], "retry", finished=results.append,
                                   stream_exclusions=("ram",))
    assert state.rgb_reclaim_stream_exclusions == {"ram"} and not commands and not stopped
    assert queued[0][0] == 30
    # ACK 42 completed; a new GPU/support-only frame 43 may already be in flight.
    state.openrgb_worker_frame_sequence = 43
    queued.pop(0)[1]()
    assert len(commands) == 1 and not stopped and state.rgb_manual_write_active
    commands.pop()[1](SimpleNamespace(ok=True, stdout=""))
    assert results == [True] and not state.rgb_manual_write_active
    assert state.openrgb_effect_started == 123.5 and state.rgb_reclaim_stream_exclusions == {"ram"}
    assert queued[0][0] == 320
    queued.pop(0)[1]()
    assert not state.rgb_reclaim_stream_exclusions and state.openrgb_sdk_ready_devices == {"gpu", "support"}
