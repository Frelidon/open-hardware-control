#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""One-shot KWin state request for the exact monitored benchmark PID."""

from __future__ import annotations

import json
import os
from pathlib import Path
import secrets
import sys
import tempfile

from PySide6.QtCore import QCoreApplication, QObject, QTimer, Slot
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage


MODES = {"maximized", "minimized", "fullscreen"}
SERVICE_PREFIX = "io.github.Frelidon.OHC.GpuStressWindow"
OBJECT_PATH = "/GpuStressWindow"


def valid_request(pid: object, mode: object) -> bool:
    return isinstance(pid, int) and 1 < pid < 2**31 and str(mode) in MODES


def kwin_script(pid: int, mode: str, service: str) -> str:
    if not valid_request(pid, mode) or not service.startswith(SERVICE_PREFIX + "."):
        raise ValueError("Invalid GPU stress window request")
    return f"""(function() {{
    var pid = {pid};
    var mode = {json.dumps(mode)};
    var service = {json.dumps(service)};
    var windows = workspace.stackingOrder;
    var target = null;
    for (var i = 0; i < windows.length; ++i) {{
        var w = windows[i];
        if (w && w.pid === pid && !w.specialWindow && !w.popupWindow) {{ target = w; break; }}
    }}
    if (!target) {{
        callDBus(service, "{OBJECT_PATH}", "{SERVICE_PREFIX}", "Report", "window-missing");
        return;
    }}
    if (mode === "fullscreen") {{
        target.minimized = false;
        target.setMaximize(false, false);
        target.fullScreen = true;
    }} else if (mode === "minimized") {{
        target.fullScreen = false;
        target.setMaximize(false, false);
        target.minimized = true;
    }} else {{
        target.fullScreen = false;
        target.minimized = false;
        target.setMaximize(true, true);
    }}
    callDBus(service, "{OBJECT_PATH}", "{SERVICE_PREFIX}", "Report", "applied");
}})();
"""


class Receiver(QObject):
    def __init__(self, app: QCoreApplication):
        super().__init__()
        self.app = app
        self.state = "reply-timeout"

    @Slot(str)
    def Report(self, state: str) -> None:
        self.state = str(state)
        self.app.quit()


def _call_ok(reply: QDBusMessage) -> bool:
    return reply.type() != QDBusMessage.MessageType.ErrorMessage


def apply_window_state(pid: int, mode: str) -> str:
    if not valid_request(pid, mode):
        return "invalid-request"
    app = QCoreApplication.instance() or QCoreApplication([])
    bus = QDBusConnection.sessionBus()
    if not bus.isConnected():
        return "session-bus-unavailable"
    service = f"{SERVICE_PREFIX}.p{pid}.n{secrets.token_hex(6)}"
    receiver = Receiver(app)
    if not bus.registerService(service) or not bus.registerObject(
        OBJECT_PATH, SERVICE_PREFIX, receiver, QDBusConnection.RegisterOption.ExportAllSlots,
    ):
        return "callback-unavailable"
    script_name = f"ohc-gpu-stress-{pid}-{secrets.token_hex(4)}"
    script_path: Path | None = None
    loaded = False
    try:
        runtime = Path(os.environ.get("XDG_RUNTIME_DIR") or tempfile.gettempdir())
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix="ohc-gpu-stress-", suffix=".js",
            dir=runtime, delete=False,
        ) as stream:
            stream.write(kwin_script(pid, mode, service))
            script_path = Path(stream.name)
        scripting = QDBusInterface("org.kde.KWin", "/Scripting", "org.kde.kwin.Scripting", bus)
        scripting.setTimeout(1200)
        if not scripting.isValid():
            return "kwin-unavailable"
        reply = scripting.call("loadScript", str(script_path), script_name)
        if not _call_ok(reply) or not reply.arguments() or not isinstance(reply.arguments()[0], int):
            return "load-failed"
        loaded = True
        script = QDBusInterface(
            "org.kde.KWin", f"/Scripting/Script{reply.arguments()[0]}",
            "org.kde.kwin.Script", bus,
        )
        script.setTimeout(1200)
        if not script.isValid() or not _call_ok(script.call("run")):
            return "run-failed"
        QTimer.singleShot(1500, app.quit)
        app.exec()
        return receiver.state
    except (OSError, ValueError):
        return "bridge-error"
    finally:
        if loaded:
            scripting.call("unloadScript", script_name)
        if script_path is not None:
            script_path.unlink(missing_ok=True)
        bus.unregisterObject(OBJECT_PATH)
        bus.unregisterService(service)


def main() -> int:
    try:
        pid = int(sys.argv[1])
        mode = sys.argv[2]
    except (IndexError, ValueError):
        pid, mode = 0, ""
    state = apply_window_state(pid, mode)
    print(json.dumps({"state": state}), flush=True)
    return 0 if state == "applied" else 1


if __name__ == "__main__":
    raise SystemExit(main())
