#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Visible, local-only camera window for an explicitly started chat diagnosis.

The camera is never opened during construction.  The user must press the
visible start button; stopping the camera immediately tears down the capture
session.  No network code is used and recordings stay at the chosen local
path until the user attaches them manually.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl, Qt, Signal
from PySide6.QtGui import QCloseEvent, QFont, QPixmap
from PySide6.QtMultimedia import (
    QCamera,
    QImageCapture,
    QMediaCaptureSession,
    QMediaDevices,
    QMediaRecorder,
    QVideoSink,
)
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LiveCameraWindow(QMainWindow):
    """A large, unambiguous local camera preview with an emergency stop."""

    stopped = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Live-Kamera für Chat-Diagnose")
        self.resize(1100, 760)
        self.setMinimumSize(760, 560)
        self.camera: QCamera | None = None
        self.capture = QMediaCaptureSession()
        self.image_capture: QImageCapture | None = None
        self.recorder: QMediaRecorder | None = None
        self.video = QLabel("Kamera ist AUS")
        self.video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video.setMinimumSize(640, 420)
        self.video.setStyleSheet("background:#070707; border:0;")
        self.video_sink = QVideoSink(self)
        self.video_sink.videoFrameChanged.connect(self._show_frame)
        self.capture.setVideoSink(self.video_sink)
        self.camera_combo = QComboBox()
        self.start_button = QPushButton("▶  Kamera starten")
        self.stop_button = QPushButton("■  SOFORT ABBRECHEN")
        self.snapshot_button = QPushButton("📷 Snapshot speichern")
        self.record_button = QPushButton("● Aufnahme starten")
        self.status = QLabel("Kamera ist AUS. Es wird nichts aufgenommen.")
        self.indicator = QLabel("●  KAMERA AUS")
        self._record_path: Path | None = None
        self._build_ui()
        self._populate_cameras()
        self._set_active(False)

    def _show_frame(self, frame) -> None:
        image = frame.toImage()
        if image.isNull():
            return
        self.video.setPixmap(QPixmap.fromImage(image).scaled(
            self.video.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(20, 20, 20, 20)
        title = QLabel("LIVE-KAMERA FÜR CHAT-DIAGNOSE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Sans", 22, QFont.Weight.Bold))
        explanation = QLabel(
            "Nur nach deinem Klick sichtbar aktiv · lokal auf diesem Rechner · "
            "zum Chat wird erst übertragen, was du selbst anhängst"
        )
        explanation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        explanation.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(explanation)
        border = QFrame()
        border.setObjectName("liveBorder")
        border_layout = QVBoxLayout(border)
        border_layout.setContentsMargins(8, 8, 8, 8)
        border_layout.addWidget(self.indicator)
        border_layout.addWidget(self.video, 1)
        layout.addWidget(border, 1)
        row = QHBoxLayout()
        row.addWidget(QLabel("Kamera:"))
        row.addWidget(self.camera_combo, 1)
        row.addWidget(self.start_button)
        row.addWidget(self.stop_button)
        layout.addLayout(row)
        actions = QHBoxLayout()
        actions.addWidget(self.snapshot_button)
        actions.addWidget(self.record_button)
        layout.addLayout(actions)
        layout.addWidget(self.status)
        self.setStyleSheet(
            "QMainWindow{background:#171717;color:#f3f3f3;} QLabel{color:#f3f3f3;} "
            "QComboBox,QPushButton{padding:9px;font-size:14px;} "
            "#liveBorder{border:10px solid #333;border-radius:12px;background:#070707;} "
            "#liveBorder[active='true']{border-color:#e00020;}"
        )
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.snapshot_button.clicked.connect(self.save_snapshot)
        self.record_button.clicked.connect(self.toggle_recording)

    def _populate_cameras(self) -> None:
        self.camera_combo.clear()
        for device in QMediaDevices.videoInputs():
            self.camera_combo.addItem(device.description(), device)
        if not self.camera_combo.count():
            self.camera_combo.addItem("Keine Kamera erkannt")
            self.start_button.setEnabled(False)

    def _set_active(self, active: bool) -> None:
        self.indicator.setText("●  KAMERA LIVE – sichtbar aktiv" if active else "●  KAMERA AUS")
        self.indicator.setStyleSheet(
            "font-size:18px;font-weight:bold;color:#ff2747;" if active
            else "font-size:18px;font-weight:bold;color:#aaaaaa;"
        )
        self.findChild(QFrame, "liveBorder").setProperty("active", active)
        self.findChild(QFrame, "liveBorder").style().unpolish(self.findChild(QFrame, "liveBorder"))
        self.findChild(QFrame, "liveBorder").style().polish(self.findChild(QFrame, "liveBorder"))
        self.stop_button.setEnabled(active)
        self.snapshot_button.setEnabled(active)
        self.record_button.setEnabled(active)
        self.start_button.setEnabled(not active and self.camera_combo.count() > 0)

    def start_camera(self) -> None:
        if self.camera is not None or not self.camera_combo.currentData():
            return
        answer = QMessageBox.question(
            self,
            "Kamera ausdrücklich freigeben?",
            "Soll das Live-Kamerabild jetzt sichtbar für diese Chat-Diagnose geöffnet werden?\n\n"
            "Die Kamera startet erst nach deiner Bestätigung. Es wird nichts automatisch übertragen.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.status.setText("Kamerastart abgebrochen. Die Kamera bleibt AUS.")
            return
        self.camera = QCamera(self.camera_combo.currentData())
        self.image_capture = QImageCapture(self.camera)
        self.recorder = QMediaRecorder(self.camera)
        self.capture.setCamera(self.camera)
        self.capture.setImageCapture(self.image_capture)
        self.capture.setRecorder(self.recorder)
        self.camera.errorOccurred.connect(
            lambda _error, message: self._show_error(f"Kamera: {message}")
        )
        self.camera.start()
        self.status.setText("Kamera läuft sichtbar. Zum Beenden jederzeit den roten Abbrechen-Button drücken.")
        self._set_active(True)

    def stop_camera(self, *, confirm: bool = True) -> None:
        was_active = self.camera is not None
        if self.recorder and self.recorder.recorderState() != QMediaRecorder.RecorderState.StoppedState:
            self.recorder.stop()
        if self.camera is not None:
            self.camera.stop()
        self.capture.setCamera(None)
        self.capture.setImageCapture(None)
        self.capture.setRecorder(None)
        self.camera = None
        self.image_capture = None
        self.recorder = None
        self._set_active(False)
        self.status.setText("Kamera ist AUS. Es wird nichts aufgenommen.")
        self.stopped.emit()
        if confirm and was_active:
            QMessageBox.information(
                self,
                "Kamera beendet",
                "Die Kamera wurde beendet. Livebild und Aufnahme sind abgebrochen.",
            )

    def save_snapshot(self) -> None:
        if self.image_capture is None:
            return
        target, _ = QFileDialog.getSaveFileName(
            self, "Snapshot lokal speichern", "chat-camera-snapshot.jpg", "JPEG (*.jpg);;PNG (*.png)"
        )
        if target:
            self.image_capture.captureToFile(target)
            self.status.setText(f"Snapshot lokal gespeichert: {target}")

    def toggle_recording(self) -> None:
        if self.recorder is None:
            return
        if self.recorder.recorderState() == QMediaRecorder.RecorderState.RecordingState:
            self.recorder.stop()
            self.record_button.setText("● Aufnahme starten")
            self.status.setText(f"Aufnahme lokal gespeichert: {self._record_path}")
            return
        target, _ = QFileDialog.getSaveFileName(
            self, "Clip lokal speichern", "chat-camera-clip.mp4", "MP4 (*.mp4);;WebM (*.webm)"
        )
        if not target:
            return
        self._record_path = Path(target)
        self.recorder.setOutputLocation(QUrl.fromLocalFile(str(self._record_path)))
        self.recorder.record()
        self.record_button.setText("■ Aufnahme stoppen")
        self.status.setText("Aufnahme läuft lokal. Sie endet erst beim Stoppen oder Abbrechen.")

    def _show_error(self, message: str) -> None:
        self.status.setText(message)
        QMessageBox.warning(self, "Kamera", message)
        self.stop_camera(confirm=False)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.stop_camera(confirm=False)
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    window = LiveCameraWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
