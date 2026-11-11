import json
import socket
import threading
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.rgb_studio.v1_15.native_plugin import NativeOpenRGBPluginClient, NativePluginResult, record_native_status


@pytest.mark.parametrize("reply", [b"[]\n", b"null\n", b"42\n", b'"bad"\n'])
def test_non_object_native_reply_is_a_transport_failure_not_an_exception(reply):
    client = NativeOpenRGBPluginClient("/unused")
    client._socket = Mock(recv=Mock(return_value=reply))
    assert not client.frame(1, []).ok
    client.close()


def test_failed_socket_connect_closes_the_unassigned_descriptor(monkeypatch, tmp_path):
    path = tmp_path / "native.sock"
    path.touch()
    sock = Mock(connect=Mock(side_effect=OSError("not ready")))
    monkeypatch.setattr("modules.rgb_studio.v1_15.native_plugin.socket.socket", lambda *_: sock)
    client = NativeOpenRGBPluginClient(str(path))
    assert not client.connect()
    assert client._socket is None
    sock.close.assert_called_once()


def test_openrgb_plugin_exposes_a_real_container_widget() -> None:
    header = (
        Path(__file__).resolve().parents[1]
        / "src" / "native" / "openrgb" / "OHCNativePlugin.h"
    ).read_text(encoding="utf-8")
    assert "QWidget* GetWidget() override { return new QWidget(); }" in header


def test_native_color_codec_preserves_rgb_channels_and_rejects_invalid_values(tmp_path):
    compiler = shutil.which("g++")
    if compiler is None:
        pytest.skip("C++ compiler unavailable")
    root = Path(__file__).resolve().parents[1]
    executable = tmp_path / "color-test"
    subprocess.run([compiler, "-std=c++17", "-I", str(root / "src/native/openrgb"),
                    str(root / "tests/fixtures/native_color_codec.cpp"),
                    "-o", str(executable)], check=True, timeout=30)
    subprocess.run([str(executable)], check=True, timeout=5)


def test_slow_controller_cannot_stall_fast_controller_and_stop_drains(tmp_path) -> None:
    compiler = shutil.which("g++")
    if compiler is None:
        pytest.skip("C++ compiler unavailable")
    source = Path(__file__).parent / "fixtures" / "native_frame_worker.cpp"
    include = Path(__file__).resolve().parents[1] / "src" / "native" / "openrgb"
    executable = tmp_path / "worker-test"
    subprocess.run([compiler, "-std=c++17", "-pthread", "-I", str(include),
                    str(source), "-o", str(executable)], check=True, timeout=30)
    subprocess.run([str(executable)], check=True, timeout=5)


def test_native_plugin_client_uses_json_lines_and_closes(tmp_path):
    path = str(tmp_path / "ohc.sock")
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        server.bind(path)
    except PermissionError:
        pytest.skip("sandbox does not permit Unix-domain sockets")
    server.listen(1)
    received = []

    def serve():
        conn, _ = server.accept()
        with conn:
            buffer = b""
            while len(received) < 2:
                buffer += conn.recv(4096)
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    received.append(json.loads(line))
                    conn.sendall(b'{"ok":true}\n')
                    if len(received) >= 2:
                        return

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    client = NativeOpenRGBPluginClient(path)
    assert client.start(60).ok
    assert client.frame(1, [{"device": 0, "colors": ["ff0000"]}]).ok
    client.close()
    thread.join(timeout=1)
    server.close()
    assert received == [
        {"op": "start", "fps": 60},
        {"op": "frame", "id": 1, "devices": [{"device": 0, "colors": ["ff0000"]}]},
    ]


def test_queue_ack_and_old_generation_cannot_confirm_a_design():
    confirmed = []
    host = SimpleNamespace(
        native_openrgb_plugin=SimpleNamespace(generation=2),
        openrgb_worker_metrics={}, openrgb_sdk_ready_devices=set(),
        rgb_pending_design_snapshot="new-design",
        acknowledge_rgb_design_part=lambda *args: confirmed.append(args),
        log_message=lambda *_args: None,
    )
    assignments = [("ram", None, SimpleNamespace(index=0)), ("fan", None, SimpleNamespace(index=5))]
    def reply(generation, ram, fan):
        return NativePluginResult(True, data={"generation": generation, "devices": [
            {"device": 0, "id": 8, "submitted": ram},
            {"device": 5, "id": 8, "submitted": fan},
        ]})
    record_native_status(host, reply(1, 3, 3), assignments, 10.)
    record_native_status(host, reply(2, 0, 0), assignments, 10.)
    record_native_status(host, reply(2, 1, 0), assignments, 10.)
    assert not confirmed
    record_native_status(host, reply(2, 1, 1), assignments, 10.1)
    assert confirmed == [("direct", "new-design")]
    record_native_status(host, reply(2, 1, 1), assignments, 10.2)
    assert len(host.openrgb_worker_metrics["fan"]["success_times"]) == 1
