#!/usr/bin/env python3
"""Regression tests for tray autostart and second-launch window activation."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import threading
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from PySide6.QtCore import QCoreApplication  # noqa: E402
from modules.application_activation.v1_0 import (  # noqa: E402
    ApplicationActivationServer,
    request_existing_instance,
    suppress_autostart_startup_feedback,
)


def test_autostart_removes_feedback_tokens_but_manual_start_keeps_them():
    manual = {"DESKTOP_STARTUP_ID": "manual", "XDG_ACTIVATION_TOKEN": "token"}
    assert not suppress_autostart_startup_feedback(["ohc"], manual)
    assert manual == {"DESKTOP_STARTUP_ID": "manual", "XDG_ACTIVATION_TOKEN": "token"}

    automatic = {"DESKTOP_STARTUP_ID": "auto", "XDG_ACTIVATION_TOKEN": "token", "KEEP": "yes"}
    assert suppress_autostart_startup_feedback(["ohc", "--autostart"], automatic)
    assert automatic == {"KEEP": "yes"}


def test_user_local_server_activates_existing_instance(tmp_path: Path):
    app = QCoreApplication.instance() or QCoreApplication(["ohc-activation-test"])
    endpoint = tmp_path / "private" / "activate.sock"
    server = ApplicationActivationServer(endpoint)
    requests: list[str] = []
    server.activation_requested.connect(lambda: requests.append("show"))
    assert server.start()

    result: dict[str, bool] = {}
    worker = threading.Thread(
        target=lambda: result.setdefault("opened", request_existing_instance(endpoint, 1500)),
        daemon=True,
    )
    worker.start()
    deadline = time.monotonic() + 2.0
    while worker.is_alive() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)
    worker.join(timeout=0.2)
    app.processEvents()

    assert result == {"opened": True}
    assert requests == ["show"]
    assert endpoint.parent.stat().st_mode & 0o077 == 0
    server.stop()


def test_main_application_keeps_lock_before_activation_and_hardware_ui():
    source = (SRC / "kraken_control.py").read_text(encoding="utf-8")
    run = source.index("def run_application")
    acquire = source.index("instance_lock.acquire()", run)
    activate = source.index("request_existing_instance(activation_endpoint)", run)
    hardware_ui = source.index("window = KrakenControl()", run)
    assert acquire < activate < hardware_ui
    assert '"StartupNotify=false\\n"' in source
    assert '"X-KDE-StartupNotify=false\\n"' in source
    assert "suppress_autostart_startup_feedback(arguments)" in source
    assert "activation_server.activation_requested.connect(window.show_from_tray)" in source
    desktop = (ROOT / "packaging/kraken-control.desktop.in").read_text(encoding="utf-8")
    assert "StartupNotify=true" in desktop  # normal interactive launches keep feedback
