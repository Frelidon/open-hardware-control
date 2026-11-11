"""A transient native failure must not replace the fast writer with SDK."""

from types import SimpleNamespace
from unittest.mock import Mock

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from modules.rgb_studio.v1_15.native_plugin import NativePluginResult
from modules.rgb_studio.v1_15.native_stream import send_native_frame, start_native_stream


OK = NativePluginResult(True, data={"generation": 1})
FAIL = NativePluginResult(False, "temporary socket failure")


def host(monkeypatch):
    monkeypatch.setattr("modules.rgb_studio.v1_15.native_stream.render", lambda *_: ["123456"])
    plugin = SimpleNamespace(available=True, path="/test/native.sock", generation=1,
                             start=Mock(return_value=OK), frame=Mock(return_value=OK),
                             stop=Mock(return_value=OK))
    state = SimpleNamespace(
        native_openrgb_plugin=plugin, openrgb_native_plugin_active=True,
        openrgb_worker_frame_sequence=10, openrgb_worker_coalesced_frames=0,
        openrgb_worker_metrics={}, openrgb_sdk_ready_devices={"gpu"},
        rgb_pending_design_snapshot=None, log_message=Mock(),
        update_openrgb_performance_status=Mock(), mark_rgb_design_transfer_failed=Mock(),
        openrgb_device_write_shape=lambda _: (1, None),
        rgb_worker_render_payload=lambda *_: {"render_plan": {}},
    )
    assert start_native_stream(state, 60)
    return state


ASSIGNMENTS = [("gpu", None, SimpleNamespace(index=2, name="GPU"))]


def test_single_failed_frame_recovers_native_without_sdk_or_stop(monkeypatch):
    state = host(monkeypatch)
    state.native_openrgb_plugin.frame.side_effect = [FAIL, OK]
    assert send_native_frame(state, ASSIGNMENTS, 1., 100., 60)
    assert send_native_frame(state, ASSIGNMENTS, 1.1, 100.1, 60)
    assert state.native_openrgb_plugin.frame.call_count == 1
    assert send_native_frame(state, ASSIGNMENTS, 1.3, 100.3, 60)
    assert state.openrgb_native_plugin_active
    assert state.rgb_native_recovery.failures == 0
    assert state.openrgb_worker_frame_sequence == 11
    state.native_openrgb_plugin.stop.assert_not_called()


def test_repeated_failures_require_confirmed_stop_before_sdk(monkeypatch):
    state = host(monkeypatch)
    state.native_openrgb_plugin.frame.return_value = FAIL
    for now in (100., 101., 102.):
        assert send_native_frame(state, ASSIGNMENTS, now, now, 60)
    state.native_openrgb_plugin.stop.assert_not_called()
    state.native_openrgb_plugin.stop.side_effect = [FAIL, OK]
    assert send_native_frame(state, ASSIGNMENTS, 103., 103., 60)
    assert state.openrgb_native_plugin_active
    assert send_native_frame(state, ASSIGNMENTS, 103.1, 103.1, 60)
    assert state.native_openrgb_plugin.stop.call_count == 1
    assert not send_native_frame(state, ASSIGNMENTS, 105., 105., 60)
    assert not state.openrgb_native_plugin_active
    assert not state.openrgb_sdk_ready_devices


def test_ambiguous_start_is_retried_before_fallback(monkeypatch):
    state = host(monkeypatch)
    state.native_openrgb_plugin.start.side_effect = [FAIL, OK]
    monkeypatch.setattr("modules.rgb_studio.v1_15.native_stream.time.monotonic", lambda: 100.)
    assert start_native_stream(state, 60)
    assert send_native_frame(state, ASSIGNMENTS, 1., 100.1, 60)
    state.native_openrgb_plugin.frame.assert_not_called()
    assert send_native_frame(state, ASSIGNMENTS, 1., 101., 60)
    assert not state.rgb_native_recovery.starting
    assert state.openrgb_native_plugin_active
    state.native_openrgb_plugin.stop.assert_not_called()


def test_missing_plugin_uses_sdk_and_invalid_render_does_not_change_writers(monkeypatch):
    state = host(monkeypatch)
    state.native_openrgb_plugin.available = False
    assert not start_native_stream(state, 60)
    state.native_openrgb_plugin.available = True
    assert start_native_stream(state, 60)
    monkeypatch.setattr("modules.rgb_studio.v1_15.native_stream.render", Mock(side_effect=ValueError("bad plan")))
    assert send_native_frame(state, ASSIGNMENTS, 1., 100., 60)
    assert send_native_frame(state, ASSIGNMENTS, 1.1, 100.1, 60)
    state.mark_rgb_design_transfer_failed.assert_called_once_with("bad plan")
    state.native_openrgb_plugin.frame.assert_not_called()
    state.native_openrgb_plugin.stop.assert_not_called()
