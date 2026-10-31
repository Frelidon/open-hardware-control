"""KWin output checks use compositor data and only target this OHC process."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from modules.window_placement.v1_5 import kwin_bridge, kwin_controller  # noqa: E402


def test_kwin_script_is_scoped_to_pid_caption_and_named_output() -> None:
    service = "io.github.Frelidon.OHC.WindowPlacement.p678.n1234"
    script = kwin_bridge.kwin_script(678, "DP-1", service)
    assert "w.pid === pid" in script
    assert 'Open Hardware Control by Frelidon ' in script
    assert "workspace.sendClientToScreen(own, target)" in script
    assert 'var wanted = "DP-1";' in script
    assert "callDBus(service" in script
    for invalid in ("", "DP-1\nworkspace.sendClientToScreen()", "A" * 81):
        with pytest.raises(ValueError):
            kwin_bridge.kwin_script(678, invalid, service)


class _Signal:
    def __init__(self):
        self.callback = None

    def connect(self, callback):
        self.callback = callback


class _Process:
    class ProcessChannelMode:
        SeparateChannels = 1

    class ProcessState:
        Running = 1
        NotRunning = 0

    created = []

    def __init__(self, _parent):
        self.finished = _Signal()
        self.errorOccurred = _Signal()
        self.output = b""
        self.started = None
        self.deleted = False
        self.created.append(self)

    def setProcessChannelMode(self, _mode):
        pass

    def start(self, program, args):
        self.started = (program, args)

    def readAllStandardOutput(self):
        return self.output

    def deleteLater(self):
        self.deleted = True

    def state(self):
        return self.ProcessState.NotRunning


class _Window:
    def __init__(self):
        self.logs = []

    def isVisible(self):
        return True

    def isMinimized(self):
        return False

    def preferred_window_screen(self):
        return type("Screen", (), {"name": lambda _self: "DP-1"})(), True

    def log_message(self, message):
        self.logs.append(message)


def test_only_kwin_confirmed_output_counts_as_success(monkeypatch) -> None:
    monkeypatch.setattr(kwin_controller, "is_kwin_wayland", lambda: True)
    monkeypatch.setattr(kwin_controller, "QProcess", _Process)
    monkeypatch.setattr(kwin_controller.QTimer, "singleShot", lambda *_args: None)
    _Process.created.clear()
    window = _Window()
    kwin_controller.reset_kwin_confirmation(window)
    kwin_controller.request_kwin_confirmation(window, "Start")
    process = _Process.created[-1]
    assert process.started[1][-1] == "DP-1"
    process.output = json.dumps({"state": "moved", "before": "HDMI-A-1", "after": "DP-1",
                                 "geometry": "1920,0 1600x1000"}).encode()
    process.finished.callback(0, None)
    assert window._kwin_placement_confirmed
    assert "KWin bestätigt=DP-1" in window.logs[-1]
    assert process.deleted


def test_missing_kwin_window_never_claims_success(monkeypatch) -> None:
    monkeypatch.setattr(kwin_controller, "is_kwin_wayland", lambda: True)
    monkeypatch.setattr(kwin_controller, "QProcess", _Process)
    monkeypatch.setattr(kwin_controller.QTimer, "singleShot", lambda *_args: None)
    _Process.created.clear()
    window = _Window()
    kwin_controller.reset_kwin_confirmation(window)
    kwin_controller.request_kwin_confirmation(window, "Start")
    process = _Process.created[-1]
    process.output = b'{"state":"window-missing","before":"","after":""}'
    process.finished.callback(1, None)
    assert not window._kwin_placement_confirmed
    assert "KWin nicht bestätigt" in window.logs[-1]
