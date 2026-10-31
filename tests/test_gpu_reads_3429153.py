"""Ubuntu GPU navigation is read-only, asynchronous and cancellable."""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QCoreApplication, QEvent, QSettings, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from modules.gpu_control.v1_0.client import LactClient, LactError
from modules.gpu_control.v1_0.page import GpuControlPage
from modules.gpu_control.v1_0.read_probe import GpuReadProbe
from modules.gpu_control.v1_0.read_worker import read_device


def wait_until(app, predicate, seconds=4):
    deadline = time.monotonic() + seconds
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(.005)
    assert predicate(), "GPU probe did not finish in its bounded test window"


class Server:
    def __init__(self, path, delay=.18):
        self.path = path
        self.delay = delay
        self.commands = []
        self.done = threading.Event()
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(str(path))
        self.socket.listen()
        self.socket.settimeout(.05)
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        while not self.done.is_set():
            try:
                connection, _ = self.socket.accept()
            except socket.timeout:
                continue
            with connection:
                connection.settimeout(1)
                payload = bytearray()
                while b"\n" not in payload:
                    payload.extend(connection.recv(4096))
                request = json.loads(payload)
                self.commands.append(request["command"])
                time.sleep(self.delay)
                values = {"list_devices": [{"id": "10de:1234", "name": "Fake GPU"}],
                          "device_stats": {"temps": {"edge": 42}},
                          "device_info": {"name": "Fake GPU"},
                          "device_clocks_info": {}, "get_gpu_config": {}}
                try:
                    connection.sendall(json.dumps({"status": "ok", "data": values.get(request["command"])}).encode() + b"\n")
                except BrokenPipeError:
                    pass  # expected when a request is cancelled

    def close(self):
        self.done.set()
        self.thread.join(timeout=2)
        self.socket.close()


def test_slow_lact_does_not_block_qt_and_uses_only_reads(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setenv("OHC_DISABLE_HARDWARE_IO", "0")
    server = Server(tmp_path / "lact.sock")
    probe = GpuReadProbe()
    complete, failures, beats = [], [], []
    probe.completed.connect(lambda *args: complete.append(args))
    probe.failed.connect(lambda *args: failures.append(args))
    timer = QTimer()
    timer.setInterval(10)
    timer.timeout.connect(lambda: beats.append(1))
    timer.start()
    try:
        started = time.monotonic()
        probe.request("device", server.path, "10de:1234")
        assert time.monotonic() - started < .1
        wait_until(app, lambda: complete or failures)
        assert not failures
        assert len(beats) >= 8
        assert complete[0][1]["stats"] == {"temps": {"edge": 42}}
        assert server.commands == ["device_stats", "device_clocks_info", "device_info", "get_gpu_config"]
    finally:
        timer.stop()
        probe.cancel()
        server.close()
        probe.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_replaced_and_cancelled_probe_never_delivers_old_result(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setenv("OHC_DISABLE_HARDWARE_IO", "0")
    server = Server(tmp_path / "lact.sock", .22)
    probe = GpuReadProbe()
    complete, failures = [], []
    probe.completed.connect(lambda *args: complete.append(args))
    probe.failed.connect(lambda *args: failures.append(args))
    try:
        probe.request("inventory", server.path)
        wait_until(app, lambda: bool(server.commands))
        probe.request("metrics", server.path, "new-gpu")
        wait_until(app, lambda: bool(complete or failures))
        assert not failures
        assert [row[0] for row in complete] == ["metrics"]
        assert complete[0][1]["gpu_id"] == "new-gpu"
        probe.request("inventory", server.path)
        probe.cancel()
        for _ in range(5):
            app.processEvents()
        assert len(complete) == 1 and not failures
        assert probe.process is None and not probe.timeout.isActive()
    finally:
        probe.cancel()
        server.close()
        probe.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_probe_deadline_reports_failure_once(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    monkeypatch.setenv("OHC_DISABLE_HARDWARE_IO", "0")
    server = Server(tmp_path / "lact.sock", .2)
    probe = GpuReadProbe()
    failures = []
    probe.failed.connect(lambda *args: failures.append(args))
    try:
        probe.timeout.setInterval(30)
        probe.request("inventory", server.path)
        wait_until(app, lambda: bool(failures))
        assert len(failures) == 1
        assert probe.process is None
    finally:
        probe.cancel()
        server.close()
        probe.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_optional_clock_failure_is_a_warning_not_a_second_stats_query():
    calls = []
    class Client:
        def stats(self, _id): calls.append("stats"); return {}
        def clocks(self, _id): raise LactError("Clock table unavailable")
        def request(self, *args): return None
        def config(self, _id): return {}
        def overdrive_enabled(self): return False
    data = read_device(Client(), "1002:1234", ownership_reader=lambda: (True, "unverified"))
    assert calls == ["stats"] and data["clocks"] == {}
    assert data["overdrive"] is False and data["ownership"] == [True, "unverified"]
    assert "Clock table unavailable" in data["warnings"][0]


def test_worker_respects_disabled_io_before_contacting_socket(tmp_path):
    worker = Path(__file__).resolve().parents[1] / "src/modules/gpu_control/v1_0/read_worker.py"
    result = subprocess.run([sys.executable, str(worker)],
                            input=json.dumps({"kind": "inventory", "socket": str(tmp_path / "unused")}),
                            text=True, capture_output=True, timeout=4,
                            env={**os.environ, "OHC_DISABLE_HARDWARE_IO": "1"})
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"ok": False, "error": "Hardware I/O disabled"}


def test_distribution_lane_and_selection_only_query_once(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    class Host(QWidget):
        def __init__(self):
            super().__init__()
            self.settings = QSettings(str(tmp_path / "gpu.ini"), QSettings.Format.IniFormat)
        def make_module_hero(self, *_args): return QLabel("GPU")
        def tr_static(self, source): return source
    monkeypatch.setattr("modules.gpu_control.v1_0.read_ui.detect_distribution", lambda: SimpleNamespace(family="fedora"))
    host = Host()
    page = GpuControlPage(host)
    assert not page._ubuntu_async_reads
    calls = []
    monkeypatch.setattr(page, "_select_device", lambda *_: calls.append(1))
    page._populate_gpu_devices([{"id": "integrated"}, {"id": "dedicated", "device_type": "Dedicated"}])
    assert page.devices.currentData() == "dedicated" and calls == [1]
    monkeypatch.setattr(page, "client", LactClient(tmp_path / "fake"))
    monkeypatch.setattr(page.gpu_read_probe, "request", lambda *args: calls.append(args))
    assert page._request_gpu_read("inventory") is False
    page._ubuntu_async_reads = True
    assert page._request_gpu_read("inventory") is True
    assert calls[-1] == ("inventory", tmp_path / "fake", "")
    host.control_authority = {"gpu": "external"}
    assert not page._write_allowed()
    host.control_authority = {"gpu": "ohc_lact"}
    host.feature_enabled = lambda _key: False
    assert not page._write_allowed()
    page.shutdown()
    host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
