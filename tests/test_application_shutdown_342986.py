"""Reproduce denied root-helper signals and verify every real exit entrypoint."""
import ast
import io
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("OHC_DISABLE_HARDWARE_IO", "1")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mainboard_fan_control import PrivilegedFanHelperSession
from modules.application_shutdown.v1_1 import process_cleanup
from modules.application_shutdown.v1_1.sequence import ShutdownSequence, stop_owned_timers
from modules.application_shutdown.v1_1.restart import process_starttime, relaunch_command, wait_and_exec
from command_backend import Backend, PendingCommand
from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QWidget

APP = QApplication.instance() or QApplication([])


class Process:
    def __init__(self, mode="eof"):
        self.stdin = io.StringIO()
        self.mode = mode
        self.finished = False
        self.calls = []
    def poll(self): return 0 if self.finished else None
    def wait(self, *, timeout):
        self.calls.append(("wait", timeout))
        assert self.stdin.closed
        if self.mode == "eof" or self.finished:
            self.finished = True
            return 0
        raise subprocess.TimeoutExpired("owned helper", timeout)
    def terminate(self):
        self.calls.append("terminate")
        if self.mode in {"denied", "race"}:
            if self.mode == "race": self.finished = True
            raise PermissionError(1, "Operation not permitted")
        if self.mode == "terminate": self.finished = True
    def kill(self):
        self.calls.append("kill")
        if self.mode != "timeout": self.finished = True


def test_root_helper_exits_on_eof_before_any_signal():
    p = Process()
    assert process_cleanup.stop_pipe_bound_process(p)
    assert p.calls == [("wait", 1.0)]


@pytest.mark.parametrize("mode,expected", [("denied", False), ("race", True), ("terminate", True),
                                          ("kill", True), ("timeout", False)])
def test_denied_signals_and_timeouts_do_not_escape_cleanup(monkeypatch, mode, expected):
    logs = []
    monkeypatch.setattr(process_cleanup, "append_startup_event", logs.append)
    p = Process(mode)
    assert process_cleanup.stop_pipe_bound_process(p) is expected
    assert p.stdin.closed
    assert len([call for call in p.calls if isinstance(call, tuple)]) <= 3
    assert bool(logs) is not expected


def test_session_stop_reproduces_original_permission_error_without_aborting(monkeypatch):
    monkeypatch.setattr(process_cleanup, "append_startup_event", lambda text: None)
    session = PrivilegedFanHelperSession()
    session.process = Process("denied")
    session.stop()
    assert session.process is None
    session.stop()  # Idempotent; no root process lookup/signaling.


def test_real_owned_pipe_child_is_reaped_after_eof():
    p = subprocess.Popen([sys.executable, "-c", "import sys; sys.stdin.read()"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        assert process_cleanup.stop_pipe_bound_process(p)
        assert p.poll() == 0
    finally:
        if p.poll() is None:
            p.kill()
            p.wait(timeout=2)
        p.stdout.close()
        p.stderr.close()


def exit_host(fail=""):
    """Compile actual production methods without constructing hardware discovery."""
    source = ast.parse((ROOT / "src/kraken_control.py").read_text())
    main_class = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == "KrakenControl")
    methods = [n for n in main_class.body if isinstance(n, ast.FunctionDef)
               and n.name in {"perform_orderly_hardware_exit", "quit_app", "request_session_shutdown",
                              "minimize_to_tray", "closeEvent"}]
    calls, logs = [], []
    def action(name):
        def call(*args, **kwargs):
            calls.append(name)
            if fail == name: raise PermissionError(1, "Operation not permitted")
        return call
    request = SimpleNamespace(request_id=1)
    def request_usb(*args, **kwargs):
        action("request")()
        return request
    namespace = {"ShutdownSequence": ShutdownSequence, "stop_owned_timers": stop_owned_timers,
                 "RequestPriority": SimpleNamespace(CRITICAL=1), "QCloseEvent": QCloseEvent,
                 "QApplication": SimpleNamespace(exit=action("exit"), quit=action("quit")),
                 "QTimer": SimpleNamespace(singleShot=lambda delay, callback: callback()),
                 "QSystemTrayIcon": SimpleNamespace(isSystemTrayAvailable=lambda: True),
                 "DISPLAY_NAME": "OHC", "stop_mainboard_fan_helper_session": action("helper"),
                 "restore_mainboard_snapshot": action("calibration")}
    cls = ast.ClassDef(name="ExitHost", bases=[], keywords=[], body=methods, decorator_list=[])
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])), "actual-exit", "exec"), namespace)
    host = namespace["ExitHost"]()
    host.log_message = logs.append
    host.exit_hardware_cleanup_done = False
    host.session_shutdown_requested = False
    host.explicit_quit_requested = False
    host.rgb_engine_restart_pending = True
    host.rgb_profile_autostart_pending = True
    host.openrgb_write_enable_pending = True
    host.findChildren = lambda timer_type: [SimpleNamespace(stop=action("timer"))]
    host.display_effects_page = SimpleNamespace(shutdown=action("effects"))
    host.thermalright_display_studio = SimpleNamespace(shutdown=action("levita"))
    host.usb_coordinator = SimpleNamespace(request=request_usb, begin=action("begin"), complete=action("complete"))
    host.mainboard_calibration_channel_id = "fan"
    host.mainboard_calibration_snapshot = object()
    host.mainboard_channels = {"fan": object()}
    host.mainboard_control_active = True
    host.tray = SimpleNamespace(hide=action("tray"), isVisible=lambda: True,
                                showMessage=action("message"), geometry=lambda: SimpleNamespace(isValid=lambda: True))
    host.tray_quit_action = SimpleNamespace(setEnabled=action("tray-action"))
    host.tray_checkbox = SimpleNamespace(isChecked=lambda: False)
    host.settings = SimpleNamespace(setValue=lambda *args: None, sync=lambda: None)
    host.backend = SimpleNamespace(shutdown=action("backend"))
    host.hide = action("hide")
    host.showMinimized = action("minimize")
    host.tabs = SimpleNamespace(currentIndex=lambda: 0)
    host.sync_active_page_performance = lambda _index: calls.append("presentation-sync")
    host.rgb_session_lock = SimpleNamespace(release=action("lock"))
    for name, key in {"shutdown_responsive_startup": "probes", "restore_all_mainboard_fans_to_firmware": "fans",
                      "restore_thermalright_cooling_on_quit": "cooling", "shutdown_gif_stream_sync": "stream",
                      "restore_original_lcd_sync_on_quit": "lcd", "restore_safe_hardware_fallback_sync_on_quit": "safety",
                      "stop_openrgb_effect": "rgb", "stop_managed_rgb_engine": "engine", "mark_clean_shutdown": "marker",
                      "save_settings": "save"}.items():
        setattr(host, name, action(key))
    return host, calls, logs


@pytest.mark.parametrize("fail", ["effects", "levita", "probes", "request", "begin", "calibration", "fans",
                                "cooling", "helper", "stream", "lcd", "complete", "safety", "rgb", "lock", "engine"])
def test_individual_failure_does_not_skip_remaining_phases_or_mark_clean(fail):
    host, calls, logs = exit_host(fail)
    host.quit_app()
    assert "engine" in calls and "backend" in calls and calls[-1] == "exit"
    assert "marker" not in calls
    assert host.exit_hardware_cleanup_done and not host.exit_cleanup_in_progress
    assert not host.exit_cleanup_success
    assert not host.rgb_engine_restart_pending and not host.rgb_profile_autostart_pending
    assert any("state=failed" in line for line in logs)


def test_successful_exit_preserves_restore_order_and_completes_once():
    host, calls, logs = exit_host()
    host.quit_app()
    assert calls.index("stream") < calls.index("lcd") < calls.index("rgb") < calls.index("engine")
    assert calls.index("engine") < calls.index("marker") < calls.index("backend") < calls.index("exit")
    before = calls.copy()
    host.perform_orderly_hardware_exit("again")
    assert calls == before and host.exit_cleanup_success


def test_owned_package_cancel_failure_still_quiesces_timers_and_completes_exit():
    host, calls, logs = exit_host()
    def fail_cancel():
        calls.append("package-cancel")
        raise OSError("owned worker unavailable")
    host.profile_bundle_controller = SimpleNamespace(cancel=fail_cancel)
    host.quit_app()
    assert calls.index("timer") < calls.index("package-cancel") < calls.index("engine")
    assert calls[-1] == "exit" and "backend" in calls and "marker" not in calls
    assert not host.rgb_engine_restart_pending and not host.rgb_profile_autostart_pending
    assert any("state=failed" in line for line in logs)


@pytest.mark.parametrize("entry", ["quit_app", "request_session_shutdown"])
def test_all_real_exit_entrypoints_survive_helper_failure(entry):
    host, calls, logs = exit_host("helper")
    getattr(host, entry)()
    assert calls[-1] in {"exit", "quit"}
    assert "lcd" in calls and "engine" in calls and "backend" in calls


@pytest.mark.parametrize("tray_checkbox_enabled", [False, True])
def test_window_close_keeps_app_running_in_tray_regardless_of_minimize_preference(tray_checkbox_enabled):
    host, calls, logs = exit_host()
    host.tray_checkbox = SimpleNamespace(isChecked=lambda: tray_checkbox_enabled)
    host.closeEvent(SimpleNamespace(ignore=lambda: calls.append("ignored")))
    assert "ignored" in calls and "hide" in calls
    assert "helper" not in calls and "lcd" not in calls and "backend" not in calls
    assert "quit" not in calls and "exit" not in calls


def test_window_close_minimizes_without_tray_and_never_shuts_down():
    host, calls, logs = exit_host()
    host.closeEvent.__globals__["QSystemTrayIcon"] = SimpleNamespace(isSystemTrayAvailable=lambda: False)
    host.closeEvent(SimpleNamespace(ignore=lambda: calls.append("ignored")))
    assert "ignored" in calls and "minimize" in calls
    assert "helper" not in calls and "backend" not in calls and "quit" not in calls


def test_explicit_minimize_hides_in_tray_without_hardware_cleanup():
    host, calls, logs = exit_host()
    host.tray_checkbox = SimpleNamespace(isChecked=lambda: True)
    host.minimize_to_tray()
    assert "save" in calls and "hide" in calls and "presentation-sync" in calls
    assert "helper" not in calls and "lcd" not in calls and "backend" not in calls
    assert logs[-1] == "INFOBEREICH: Fenster auf ausdrückliches Minimieren ausgeblendet"


def test_minimize_falls_back_to_visible_taskbar_when_tray_is_not_visible():
    host, calls, logs = exit_host()
    host.tray_checkbox = SimpleNamespace(isChecked=lambda: True)
    host.tray = SimpleNamespace(isVisible=lambda: False)
    host.minimize_to_tray()
    assert "minimize" in calls and "hide" not in calls


def test_owned_timers_stop_but_unrelated_timer_remains_active():
    host = QWidget()
    own = QTimer(host)
    own.start(1000)
    unrelated = QTimer()
    unrelated.start(1000)
    stop_owned_timers(host)
    assert not own.isActive() and unrelated.isActive()
    unrelated.stop()
    host.close()


def test_backend_shutdown_completion_never_runs_cancelled_callback():
    backend = Backend()
    calls = []
    backend._current = PendingCommand(["unused"], calls.append, lambda error: calls.append(error), 1, False, False)
    backend._shutting_down = True
    backend._complete(9, "", "cancelled")
    assert calls == [] and backend.is_idle()


def test_signal_handler_does_not_clear_marker_before_actual_cleanup():
    source = (ROOT / "src/kraken_control.py").read_text()
    handler = source[source.index("def install_session_signal_handlers"):source.index("def run_application")]
    assert "mark_clean_shutdown" not in handler
    assert "window.request_session_shutdown" in handler


def test_restart_relaunch_command_drops_only_tray_autostart_flag(tmp_path):
    entry = tmp_path / "kraken_control.py"
    entry.write_text("# entry\n", encoding="utf-8")
    command = relaunch_command([str(entry), "--autostart", "--safe-test"])
    assert command[:2] == [sys.executable, str(entry.resolve())]
    assert command[2:] == ["--safe-test"]


def test_restart_waiter_refuses_to_exec_while_original_pid_identity_lives(monkeypatch):
    own_starttime = process_starttime(os.getpid())
    assert own_starttime
    called = []
    monkeypatch.setattr(os, "execv", lambda *args: called.append(args))
    assert wait_and_exec(os.getpid(), own_starttime, [sys.executable], timeout=0.01) == 1
    assert called == []
