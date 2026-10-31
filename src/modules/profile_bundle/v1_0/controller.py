# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit complete-package UI and owned, bounded background file worker."""
import json
from pathlib import Path
import sys
import tempfile
import uuid
from PySide6.QtCore import QObject, QProcess, QTimer
from PySide6.QtWidgets import QFileDialog, QLabel, QMessageBox, QPushButton
from app_constants import APP_VERSION
from .archive import json_bytes
from .restore import PENDING_KEY
from .values import encode


def snapshot(host):
    # These existing functions only persist OHC metadata, never touch hardware.
    host.save_settings(); host.save_rgb_workspace()
    settings = {k: encode(host.settings.value(k)) for k in host.settings.allKeys()
                if k != PENDING_KEY and not k.startswith("profile_bundle/")}
    selected = host.selected_profile() or dict(name=host.tr_static("Gesamt"))
    current = dict(id="user-complete-" + uuid.uuid4().hex, name=str(selected.get("name", "")) + " · " + host.tr_static("Gesamt"),
                   builtin=False, category="Gesamt", payload=host.capture_profile_payload("Gesamt"))
    profiles = json.loads(json.dumps(host.user_profiles, ensure_ascii=False)) + [current]
    return dict(version=APP_VERSION, settings=settings, profiles=profiles,
                lcd_store=str(host.lcd_profile_store.root))


class BundleController(QObject):
    def __init__(self, host):
        super().__init__(host)
        self.host = host
        self.process = QProcess(self)
        self.process.finished.connect(self.finished)
        self.process.errorOccurred.connect(self.process_error)
        self.deadline = QTimer(self); self.deadline.setSingleShot(True)
        self.deadline.timeout.connect(self.cancel)
        self.spec = self.action = None
        self.buttons = []

    def export(self):
        if self.process.state() != QProcess.ProcessState.NotRunning: return
        tr = self.host.tr_static
        path, _ = QFileDialog.getSaveFileName(self.host, tr("Komplettpaket exportieren"),
                             str(Path.home() / "ohc-complete-profile.zip"), "OHC ZIP (*.zip)")
        if not path: return
        if not path.casefold().endswith(".zip"): path += ".zip"
        try:
            state = snapshot(self.host)
            self.start(dict(action="export", path=path, snapshot=state, extra_roots=[state["lcd_store"]]))
        except (OSError, ValueError, TypeError) as exc: self.show_error(exc)

    def import_package(self):
        if self.process.state() != QProcess.ProcessState.NotRunning: return
        tr = self.host.tr_static
        path, _ = QFileDialog.getOpenFileName(self.host, tr("Komplettpaket importieren"), str(Path.home()), "OHC ZIP (*.zip)")
        if not path: return
        answer = QMessageBox.question(self.host, tr("Komplettpaket wiederherstellen?"), tr(
            "Nach Neustart werden alle App-Einstellungen und Profile übernommen. Eine Rückfallkopie bleibt erhalten. Hardwareautomatik und PWM-Bestätigung müssen neu aktiviert werden."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes: return
        try:
            base = self.host.app_config_dir / "profile-imports"
            base.mkdir(parents=True, exist_ok=True, mode=0o700)
            self.start(dict(action="import", path=path, stage=str(base / ("package-" + uuid.uuid4().hex))))
        except (OSError, ValueError) as exc: self.show_error(exc)

    def start(self, job):
        data = json_bytes(job)
        fd, name = tempfile.mkstemp(prefix="ohc-package-job-", suffix=".json")
        import os
        with os.fdopen(fd, "wb") as out: out.write(data)
        self.spec, self.action = Path(name), job["action"]
        for button in self.buttons: button.setEnabled(False)
        self.host.footer_status.setText(self.host.tr_static("Komplettpaket wird verarbeitet …"))
        self.process.start(sys.executable, [str(Path(__file__).with_name("worker.py")), str(self.spec)])
        self.deadline.start(600_000)

    def process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart: self.finished(-1)

    def finished(self, exit_code, _status=None):
        if self.spec is None: return
        self.deadline.stop()
        raw = bytes(self.process.readAllStandardOutput())
        self.spec.unlink(missing_ok=True); self.spec = None
        for button in self.buttons: button.setEnabled(True)
        if getattr(self.host, "explicit_quit_requested", False) or getattr(self.host, "session_shutdown_requested", False): return
        try:
            if len(raw) > 512 * 1024: raise ValueError("BUNDLE_WORKER_OUTPUT")
            result = json.loads(raw)
            if exit_code != 0 or not result["ok"]: raise ValueError(result.get("error", "BUNDLE_WORKER_FAILED"))
            if self.action == "import":
                self.host.settings.setValue(PENDING_KEY, json.dumps(result["result"]))
                self.host.settings.sync()
                caption = "Komplettpaket importiert – bitte neu starten"
            else:
                caption = "Komplettpaket gespeichert"
            self.host.footer_status.setText(self.host.tr_static(caption))
            missing = result["result"].get("missing", [])
            if missing:
                QMessageBox.warning(self.host, self.host.tr_static(caption),
                                    self.host.tr_static("Nicht mehr vorhandene Mediendateien fehlen im Paket.") + f" ({len(missing)})")
        except (OSError, ValueError, TypeError, KeyError) as exc: self.show_error(exc)

    def show_error(self, exc):
        self.host.show_error(self.host.tr_static("Komplettpaket fehlgeschlagen.") + "\n" + str(exc)[:350])

    def cancel(self):
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()  # Only this owned, non-hardware file worker.
            self.process.waitForFinished(700)


def build_bundle_controls(host, layout):
    controller = BundleController(host)
    host.profile_bundle_controller = controller
    for caption, name, action in (("Komplettpaket exportieren", "profileBundleExport", controller.export),
                                   ("Komplettpaket importieren", "profileBundleImport", controller.import_package)):
        button = QPushButton(caption)
        button.setObjectName(name); button.setMinimumHeight(36)
        button.clicked.connect(action); layout.addWidget(button); controller.buttons.append(button)
    note = QLabel("Alle Einstellungen, Gehäusepositionen, RGB/PWM-Zuordnungen, Lüftermodelle und zugehörige Medien. Das private ZIP enthält persönliche Dateipfade; keine Logs oder fremden App-Einstellungen.")
    note.setWordWrap(True); layout.addWidget(note)
    if host.settings.value("profile_bundle/restore_error_v1", ""):
        warning = QLabel("Komplettpaket konnte beim Neustart nicht übernommen werden; bisherige Einstellungen bleiben erhalten.")
        warning.setWordWrap(True); layout.addWidget(warning)
