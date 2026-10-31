#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""One-shot read-only KDE full-screen state query."""

from __future__ import annotations

import json
from pathlib import Path
import secrets
import tempfile

from PySide6.QtCore import QCoreApplication, QObject, QTimer, Slot
from PySide6.QtDBus import QDBusConnection, QDBusInterface, QDBusMessage


SERVICE_PREFIX = "io.github.Frelidon.OHC.SnapshotFullscreen"
OBJECT_PATH = "/SnapshotFullscreen"


def script_source(service: str) -> str:
    return f"""(function() {{
    var w = workspace.activeWindow;
    if (!w) {{ callDBus({json.dumps(service)}, {json.dumps(OBJECT_PATH)}, {json.dumps(SERVICE_PREFIX)}, "Report", false, false, ""); return; }}
    var borderless = false;
    try {{
        var frame = w.frameGeometry;
        var output = w.output ? w.output.geometry : null;
        borderless = !!w.noBorder && !!output &&
            Math.abs(frame.x - output.x) <= 2 && Math.abs(frame.y - output.y) <= 2 &&
            Math.abs(frame.width - output.width) <= 2 && Math.abs(frame.height - output.height) <= 2;
    }} catch (e) {{ borderless = false; }}
    callDBus({json.dumps(service)}, {json.dumps(OBJECT_PATH)}, {json.dumps(SERVICE_PREFIX)}, "Report", !!w.fullScreen, borderless, String(w.caption || ""));
}})();
"""


class Receiver(QObject):
    def __init__(self, app: QCoreApplication):
        super().__init__()
        self.app = app
        self.fullscreen = False
        self.borderless = False
        self.title = ""

    @Slot(bool, bool, str)
    def Report(self, fullscreen: bool, borderless: bool, title: str) -> None:
        self.fullscreen = bool(fullscreen)
        self.borderless = bool(borderless)
        self.title = str(title)[:128]
        self.app.quit()


def _ok(reply: QDBusMessage) -> bool:
    return reply.type() != QDBusMessage.MessageType.ErrorMessage


def query() -> dict[str, object]:
    app = QCoreApplication.instance() or QCoreApplication([])
    bus = QDBusConnection.sessionBus()
    if not bus.isConnected():
        return {"fullscreen": False, "borderless": False, "title": ""}
    token = secrets.token_hex(6)
    service = f"{SERVICE_PREFIX}.{token}"
    receiver = Receiver(app)
    if not bus.registerService(service) or not bus.registerObject(
        OBJECT_PATH, SERVICE_PREFIX, receiver, QDBusConnection.RegisterOption.ExportAllSlots,
    ):
        return {"fullscreen": False, "borderless": False, "title": ""}
    name = f"ohc-snapshot-fullscreen-{token}"
    script_path: Path | None = None
    loaded = False
    scripting = QDBusInterface("org.kde.KWin", "/Scripting", "org.kde.kwin.Scripting", bus)
    try:
        if not scripting.isValid():
            return {"fullscreen": False, "borderless": False, "title": ""}
        runtime = Path(tempfile.gettempdir())
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", prefix="ohc-snapshot-", suffix=".js", dir=runtime, delete=False) as stream:
            stream.write(script_source(service))
            script_path = Path(stream.name)
        reply = scripting.call("loadScript", str(script_path), name)
        if not _ok(reply) or not reply.arguments() or not isinstance(reply.arguments()[0], int):
            return {"fullscreen": False, "borderless": False, "title": ""}
        loaded = True
        script = QDBusInterface("org.kde.KWin", f"/Scripting/Script{reply.arguments()[0]}", "org.kde.kwin.Script", bus)
        if not script.isValid() or not _ok(script.call("run")):
            return {"fullscreen": False, "borderless": False, "title": ""}
        QTimer.singleShot(1200, app.quit)
        app.exec()
        return {
            "fullscreen": receiver.fullscreen,
            "borderless": receiver.borderless,
            "title": receiver.title,
        }
    finally:
        if loaded:
            scripting.call("unloadScript", name)
        if script_path is not None:
            script_path.unlink(missing_ok=True)
        bus.unregisterObject(OBJECT_PATH)
        bus.unregisterService(service)


if __name__ == "__main__":
    print(json.dumps(query(), ensure_ascii=False), flush=True)
