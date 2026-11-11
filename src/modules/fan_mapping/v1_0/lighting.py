# SPDX-License-Identifier: GPL-3.0-or-later
"""Scoped automatic white identification, using existing owned RGB writers."""
from PySide6.QtCore import QProcess, QTimer
from modules.rgb_studio.v1_15.header_preview import HeaderPreview


def status(host, text):
    host.fan_assistant_lighting_status_source = text
    if hasattr(host, "assistant_rgb_status"):
        host.assistant_rgb_status.setText(host.tr_static(text))


def begin(host):
    if getattr(host, "fan_assistant_preview", None) is not None:
        return
    if not host.openrgb_write_enabled or getattr(host, "hardware_io_disabled", False):
        status(host, "Weiße Beleuchtung benötigt die bereits freigegebene RGB-Steuerung.")
        return
    commands = host.build_chassis_white_rgb_commands()
    if not commands:
        status(host, "Keine zugeordneten Lüfter-RGBs verfügbar; die Zuordnung bleibt möglich.")
        return
    # A STOP ACK is the ownership barrier before a one-shot SDK write.
    if getattr(host, "openrgb_native_plugin_active", False):
        result = host.native_openrgb_plugin.stop()
        if not result.ok:
            status(host, "RGB-Testhilfe wartet auf die Freigabe der Animation.")
            return
        host.openrgb_native_plugin_active = False
    preview = HeaderPreview(host)
    host.fan_assistant_preview = preview
    host.stop_openrgb_effect(host.tr_static("Lüfterzuordnung: Animation pausiert"))
    preview.start()
    status(host, "Lüfterbeleuchtung wird automatisch weiß eingestellt …")
    dispatch(host, preview, commands)


def dispatch(host, preview, commands, attempts=0):
    if preview.closed:
        preview.complete(False)
        return
    process = getattr(host, "openrgb_effect_process", None)
    if (getattr(host, "rgb_manual_write_active", False)
            or (process is not None and process.state() != QProcess.ProcessState.NotRunning)):
        if attempts >= 67:
            complete(host, preview, False)
        else:
            QTimer.singleShot(30, host, lambda: dispatch(host, preview, commands, attempts + 1))
        return
    host.run_rgb_command_sequence(
        commands, host.tr_static("Lüfterbeleuchtung: Weiß mit voller Helligkeit"),
        finished=lambda ok: complete(host, preview, ok),
    )


def complete(host, preview, ok):
    preview.complete(ok)
    status(host, "Lüfterbeleuchtung: Weiß mit voller Helligkeit" if ok else "RGB-Weißtest teilweise fehlgeschlagen · siehe Log")


def finish(host):
    preview = getattr(host, "fan_assistant_preview", None)
    host.fan_assistant_preview = None
    if preview is not None:
        preview.close()
