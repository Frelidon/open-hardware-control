#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""One-shot KWin Wayland output check for OHC's own main window.

Runs in a short-lived child process so D-Bus and KWin cannot stall the GUI.
The temporary script is scoped to one PID, the OHC main-window caption and
one named output. It is unloaded before this helper exits.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import secrets
import sys
import tempfile

from PySide6.QtCore import QCoreApplication, QObject, QTimer, Slot
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage


_OUTPUT_NAME = re.compile(r"[A-Za-z0-9_.-]{1,80}\Z")
_SERVICE_PREFIX = "io.github.Frelidon.OHC.WindowPlacement"
_OBJECT_PATH = "/WindowPlacement"


def valid_request(pid: object, output: object) -> bool:
    return isinstance(pid, int) and 1 < pid < 2**31 and isinstance(output, str) and bool(_OUTPUT_NAME.fullmatch(output))


def kwin_script(pid: int, output: str, service: str) -> str:
    """Generate only constant, JSON-encoded literals for KWin's JS engine."""
    if not valid_request(pid, output) or not service.startswith(_SERVICE_PREFIX + "."):
        raise ValueError("Invalid KWin placement request")
    return f"""(function() {{
    var pid = {pid};
    var wanted = {json.dumps(output)};
    var service = {json.dumps(service)};
    function report(state, before, after, geometry) {{
        callDBus(service, "{_OBJECT_PATH}", "{_SERVICE_PREFIX}", "Report",
                 state, before, after, geometry);
    }}
    var target = null;
    var outputs = workspace.screens;
    for (var i = 0; i < outputs.length; ++i) {{
        if (outputs[i] && outputs[i].name === wanted) {{ target = outputs[i]; break; }}
    }}
    if (!target) {{ report("output-missing", "", "", ""); return; }}
    var windows = workspace.stackingOrder;
    var own = null;
    for (var j = 0; j < windows.length; ++j) {{
        var w = windows[j];
        if (w && w.pid === pid && !w.specialWindow && !w.transient &&
            String(w.caption).indexOf("Open Hardware Control by Frelidon ") === 0) {{
            own = w; break;
        }}
    }}
    if (!own) {{ report("window-missing", "", "", ""); return; }}
    var before = own.output ? String(own.output.name) : "";
    if (before !== wanted) workspace.sendClientToScreen(own, target);
    var after = own.output ? String(own.output.name) : "";
    var g = own.frameGeometry;
    var geometry = g ? String(g.x) + "," + String(g.y) + " " +
                       String(g.width) + "x" + String(g.height) : "";
    report(after === wanted ? (before === wanted ? "correct" : "moved") : "unconfirmed",
           before, after, geometry);
}})();
"""


class _Receiver(QObject):
    def __init__(self, app: QCoreApplication):
        super().__init__()
        self.app = app
        self.result: dict[str, str] | None = None

    @Slot(str, str, str, str)
    def Report(self, state: str, before: str, after: str, geometry: str) -> None:
        self.result = {"state": state, "before": before, "after": after, "geometry": geometry}
        self.app.quit()


def _call_ok(reply: QDBusMessage) -> bool:
    return reply.type() != QDBusMessage.MessageType.ErrorMessage


def inspect_and_place(pid: int, output: str) -> dict[str, str]:
    """Ask KWin itself; never infer compositor placement from Qt coordinates."""
    if not valid_request(pid, output):
        return {"state": "invalid-request"}
    app = QCoreApplication.instance() or QCoreApplication([])
    bus = QDBusConnection.sessionBus()
    if not bus.isConnected():
        return {"state": "session-bus-unavailable"}
    service = f"{_SERVICE_PREFIX}.p{pid}.n{secrets.token_hex(6)}"
    receiver = _Receiver(app)
    if not bus.registerService(service):
        return {"state": "callback-unavailable"}
    if not bus.registerObject(_OBJECT_PATH, _SERVICE_PREFIX, receiver,
                              QDBusConnection.RegisterOption.ExportAllSlots):
        bus.unregisterService(service)
        return {"state": "callback-unavailable"}
    script_name = f"ohc-placement-{pid}-{secrets.token_hex(4)}"
    script_path: Path | None = None
    loaded = False
    try:
        runtime = Path(os.environ.get("XDG_RUNTIME_DIR") or tempfile.gettempdir())
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix="ohc-kwin-",
                                         suffix=".js", dir=runtime, delete=False) as stream:
            stream.write(kwin_script(pid, output, service))
            script_path = Path(stream.name)
        scripting = QDBusInterface("org.kde.KWin", "/Scripting", "org.kde.kwin.Scripting", bus)
        scripting.setTimeout(1200)
        if not scripting.isValid():
            return {"state": "kwin-unavailable"}
        reply = scripting.call("loadScript", str(script_path), script_name)
        if not _call_ok(reply) or not reply.arguments() or not isinstance(reply.arguments()[0], int):
            return {"state": "load-failed"}
        loaded = True
        script_id = reply.arguments()[0]
        script = QDBusInterface("org.kde.KWin", f"/Scripting/Script{script_id}",
                                "org.kde.kwin.Script", bus)
        script.setTimeout(1200)
        if not script.isValid() or not _call_ok(script.call("run")):
            return {"state": "run-failed"}
        QTimer.singleShot(1800, app.quit)
        app.exec()
        return receiver.result or {"state": "reply-timeout"}
    except (OSError, ValueError):
        return {"state": "bridge-error"}
    finally:
        if loaded:
            scripting.call("unloadScript", script_name)
        if script_path is not None:
            script_path.unlink(missing_ok=True)
        bus.unregisterObject(_OBJECT_PATH)
        bus.unregisterService(service)


def main() -> int:
    if len(sys.argv) != 3:
        result = {"state": "invalid-request"}
    else:
        try:
            pid = int(sys.argv[1])
        except ValueError:
            pid = 0
        result = inspect_and_place(pid, sys.argv[2])
    print(json.dumps(result, separators=(",", ":")), flush=True)
    return 0 if result.get("state") in {"correct", "moved"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
