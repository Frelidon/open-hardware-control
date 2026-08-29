#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""PySide6 editor for Thermalright Levita media and metric overlays."""

from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from typing import Callable, Iterable

from PySide6.QtCore import QPointF, QProcess, QTimer, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from thermalright_display import (
    DEFAULT_OVERLAYS,
    LEVITA_CUTOUT_HEIGHT,
    LEVITA_CUTOUT_WIDTH,
    LEVITA_CUTOUT_X,
    LEVITA_CUTOUT_Y,
    LEVITA_HEIGHT,
    LEVITA_WIDTH,
    MediaEntry,
    OverlaySpec,
    SUPPORTED_IMAGE_SUFFIXES,
    ThermalrightCli,
    build_apply_sequence,
    clamp_overlay_outside_cutout,
    parse_detect_output,
    scan_media_directory,
)


class _MovableOverlayItem(QGraphicsSimpleTextItem):
    def __init__(self, spec: OverlaySpec, moved: Callable[[str, int, int], None]) -> None:
        super().__init__(spec.sample or spec.label)
        self.ident = spec.ident
        self._moved = moved
        font = QFont()
        font.setPixelSize(spec.size)
        font.setBold(spec.bold)
        self.setFont(font)
        self.setBrush(QColor(spec.color))
        self.setPen(QPen(QColor(0, 0, 0, 210), max(1, spec.size // 18)))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        rect = self.boundingRect()
        self.setPos(spec.x - rect.width() / 2, spec.y - rect.height() / 2)
        self.setToolTip(f"{spec.label} · mit der Maus verschieben")

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: object) -> object:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and isinstance(value, QPointF):
            rect = self.boundingRect()
            x = max(0.0, min(float(LEVITA_CUTOUT_X) - rect.width() - 8.0, value.x()))
            y = max(0.0, min(float(LEVITA_HEIGHT) - rect.height(), value.y()))
            return QPointF(x, y)
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            rect = self.boundingRect()
            center_x = round(self.pos().x() + rect.width() / 2)
            center_y = round(self.pos().y() + rect.height() / 2)
            self._moved(self.ident, center_x, center_y)
        return super().itemChange(change, value)


class ThermalrightCanvas(QGraphicsView):
    """1600×720 design surface with an exact Levita cutout guide."""

    def __init__(self, moved: Callable[[str, int, int], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(0, 0, LEVITA_WIDTH, LEVITA_HEIGHT, self)
        self.setScene(self._scene)
        self._moved = moved
        self._background = QPixmap()
        self._specs: tuple[OverlaySpec, ...] = tuple(DEFAULT_OVERLAYS)
        self._split_mode = 0
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setBackgroundBrush(QColor("#07111d"))
        self.setMinimumHeight(315)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setToolTip("Hardwarewerte direkt auf der 1600×720-Fläche verschieben")
        self.rebuild()

    def set_background(self, pixmap: QPixmap) -> None:
        self._background = pixmap
        self.rebuild()

    def set_specs(self, specs: Iterable[OverlaySpec]) -> None:
        self._specs = tuple(specs)
        self.rebuild()

    def set_split_mode(self, mode: int) -> None:
        self._split_mode = max(0, min(3, int(mode)))
        self.rebuild()

    def rebuild(self) -> None:
        self._scene.clear()
        if self._background.isNull():
            background = QGraphicsRectItem(0, 0, LEVITA_WIDTH, LEVITA_HEIGHT)
            background.setBrush(QColor("#07111d"))
            background.setPen(QPen(QColor("#315a78"), 3))
            background.setZValue(-20)
            self._scene.addItem(background)
            placeholder = self._scene.addSimpleText("Lokales Bild, Video oder TRCC-Layout auswählen")
            placeholder.setBrush(QColor("#8ba2b5"))
            font = QFont()
            font.setPixelSize(42)
            placeholder.setFont(font)
            placeholder.setPos(LEVITA_WIDTH / 2 - placeholder.boundingRect().width() / 2, 270)
        else:
            item = self._scene.addPixmap(self._background)
            item.setZValue(-20)

        if self._split_mode:
            widths = {1: 360, 2: 480, 3: 620}
            guide_width = widths.get(self._split_mode, 480)
            guide = QGraphicsRectItem((LEVITA_WIDTH - guide_width) / 2, 18, guide_width, 76)
            guide.setBrush(QColor(0, 200, 255, 34))
            guide.setPen(QPen(QColor(0, 200, 255, 170), 3, Qt.PenStyle.DashLine))
            guide.setZValue(5)
            self._scene.addItem(guide)
            label = self._scene.addSimpleText(f"Dynamic Island {chr(64 + self._split_mode)}")
            label.setBrush(QColor("#00c8ff"))
            label.setPos((LEVITA_WIDTH - label.boundingRect().width()) / 2, 43)
            label.setZValue(6)

        cutout = QGraphicsRectItem(
            LEVITA_CUTOUT_X, LEVITA_CUTOUT_Y, LEVITA_CUTOUT_WIDTH, LEVITA_CUTOUT_HEIGHT,
        )
        cutout.setBrush(QColor(0, 0, 0, 235))
        cutout.setPen(QPen(QColor("#ff526f"), 4, Qt.PenStyle.DashLine))
        cutout.setZValue(30)
        cutout.setToolTip("Physische Levita-Aussparung · 80 px · keine Hardwarewerte hier platzieren")
        self._scene.addItem(cutout)
        cutout_label = self._scene.addSimpleText("NOTCH")
        cutout_label.setBrush(QColor("#ff526f"))
        cutout_label.setRotation(-90)
        cutout_label.setPos(1560, 390)
        cutout_label.setZValue(31)

        for spec in self._specs:
            if spec.visible:
                self._scene.addItem(_MovableOverlayItem(clamp_overlay_outside_cutout(spec), self._moved))
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().resizeEvent(event)
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


class ThermalrightDisplayStudio(QGroupBox):
    """Integrated local-first Levita design editor and TRCC CLI frontend."""

    def __init__(
        self,
        settings,
        cache_dir: Path,
        *,
        log_callback: Callable[[str], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Thermalright Levita Vision · Display-Studio", parent)
        self.settings = settings
        self.cache_dir = cache_dir / "thermalright-preview"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_callback = log_callback
        # The LCD page is built before the main Log page. Restoring a saved
        # media directory renders its first preview synchronously, so logging
        # must stay muted until this widget has finished constructing.
        self.log_ready = False
        self.cli = ThermalrightCli()
        self.media_entries: list[MediaEntry] = []
        self.overlay_specs = self._load_overlays()
        self.overlay_controls: dict[str, dict[str, QWidget]] = {}
        self.command_queue: list[tuple[tuple[str, ...], bool]] = []
        self.command_outputs: list[str] = []
        self.current_tolerates_failure = False
        self.queue_done: Callable[[bool, str], None] | None = None
        self.play_process: QProcess | None = None
        self.test_colors = [QColor("#ef3340"), QColor("#16c172"), QColor("#2878ff"), QColor("#000000")]
        self.test_color_index = 0

        self.command_process = QProcess(self)
        self.command_process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.command_process.finished.connect(self._on_command_finished)
        self.test_timer = QTimer(self)
        self.test_timer.setInterval(450)
        self.test_timer.timeout.connect(self._next_test_color)

        self._build_ui()
        saved_dir = str(self.settings.value("thermalright/media_directory", "") or "")
        if saved_dir and Path(saved_dir).is_dir():
            self.load_media_directory(Path(saved_dir), quiet=True)
        self.refresh_backend_status()
        self.log_ready = True

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setSpacing(12)
        intro = QLabel(
            "Lokale Thermalright-Designs importieren, CPU/GPU/RAM/Uhr frei verschieben und zuerst vollständig "
            "ohne USB-Zugriff testen. Die Levita-Aussparung rechts (80 px) ist als gesperrte Zone markiert."
        )
        intro.setWordWrap(True)
        intro.setObjectName("infoText")
        outer.addWidget(intro)

        status_row = QHBoxLayout()
        self.test_mode = QCheckBox("Testmodus · nur Vorschau, keine USB-Schreibzugriffe")
        self.test_mode.setChecked(self.settings.value("thermalright/test_mode", True, type=bool))
        self.test_mode.toggled.connect(self._on_test_mode_changed)
        self.backend_status = QLabel()
        self.backend_status.setWordWrap(True)
        self.backend_status.setObjectName("muted")
        detect_button = QPushButton("Backend & Gerät prüfen")
        detect_button.clicked.connect(self.detect_backend_and_device)
        status_row.addWidget(self.test_mode)
        status_row.addWidget(self.backend_status, 1)
        status_row.addWidget(detect_button)
        outer.addLayout(status_row)

        media_row = QHBoxLayout()
        import_button = QPushButton("Designordner importieren")
        import_button.clicked.connect(self.choose_media_directory)
        self.media_combo = QComboBox()
        self.media_combo.setMinimumContentsLength(36)
        self.media_combo.currentIndexChanged.connect(self.update_preview)
        self.media_filter = QLineEdit()
        self.media_filter.setPlaceholderText("Designs filtern …")
        self.media_filter.textChanged.connect(self._apply_media_filter)
        media_row.addWidget(import_button)
        media_row.addWidget(self.media_filter)
        media_row.addWidget(self.media_combo, 1)
        outer.addLayout(media_row)

        self.media_directory_label = QLabel("Noch kein lokaler Designordner importiert")
        self.media_directory_label.setObjectName("muted")
        self.media_directory_label.setWordWrap(True)
        outer.addWidget(self.media_directory_label)

        self.canvas = ThermalrightCanvas(self._overlay_moved)
        outer.addWidget(self.canvas)

        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Notch / Dynamic Island"))
        self.split_mode = QComboBox()
        self.split_mode.addItem("Aus · nur physische rechte Aussparung", 0)
        self.split_mode.addItem("Stil A", 1)
        self.split_mode.addItem("Stil B · empfohlen", 2)
        self.split_mode.addItem("Stil C", 3)
        saved_split = max(0, min(3, int(self.settings.value("thermalright/split_mode", 2) or 2)))
        self.split_mode.setCurrentIndex(saved_split)
        self.split_mode.currentIndexChanged.connect(self._split_mode_changed)
        options_row.addWidget(self.split_mode)
        options_row.addStretch()
        self.preview_status = QLabel("Vorschau bereit")
        self.preview_status.setObjectName("muted")
        options_row.addWidget(self.preview_status)
        outer.addLayout(options_row)

        overlays_box = QGroupBox("Verschiebbare Hardware-Infos")
        grid = QGridLayout(overlays_box)
        for column, title in enumerate(("Ein", "Element", "X", "Y", "Größe", "Farbe")):
            grid.addWidget(QLabel(title), 0, column)
        for row, spec in enumerate(self.overlay_specs, start=1):
            visible = QCheckBox()
            visible.setChecked(spec.visible)
            label = QLabel(spec.label)
            x_spin = QSpinBox()
            x_spin.setRange(0, LEVITA_CUTOUT_X - 1)
            x_spin.setValue(spec.x)
            y_spin = QSpinBox()
            y_spin.setRange(0, LEVITA_HEIGHT - 1)
            y_spin.setValue(spec.y)
            size_spin = QSpinBox()
            size_spin.setRange(12, 160)
            size_spin.setValue(spec.size)
            color_button = QPushButton(spec.color)
            color_button.setStyleSheet(f"color: {spec.color};")
            controls: dict[str, QWidget] = {
                "visible": visible, "x": x_spin, "y": y_spin,
                "size": size_spin, "color": color_button,
            }
            self.overlay_controls[spec.ident] = controls
            visible.toggled.connect(lambda checked, ident=spec.ident: self._overlay_control_changed(ident, visible=checked))
            x_spin.valueChanged.connect(lambda value, ident=spec.ident: self._overlay_control_changed(ident, x=value))
            y_spin.valueChanged.connect(lambda value, ident=spec.ident: self._overlay_control_changed(ident, y=value))
            size_spin.valueChanged.connect(lambda value, ident=spec.ident: self._overlay_control_changed(ident, size=value))
            color_button.clicked.connect(lambda _checked=False, ident=spec.ident: self._choose_overlay_color(ident))
            for column, widget in enumerate((visible, label, x_spin, y_spin, size_spin, color_button)):
                grid.addWidget(widget, row, column)
        reset_button = QPushButton("Hardware-Infos zurücksetzen")
        reset_button.clicked.connect(self.reset_overlays)
        grid.addWidget(reset_button, len(self.overlay_specs) + 1, 0, 1, 6)
        outer.addWidget(overlays_box)

        action_row = QHBoxLayout()
        preview_button = QPushButton("Vorschau neu laden")
        preview_button.clicked.connect(self.update_preview)
        apply_button = QPushButton("Design anwenden")
        apply_button.clicked.connect(self.apply_design)
        test_button = QPushButton("Display-Test · Rot/Grün/Blau/Schwarz")
        test_button.clicked.connect(self.run_display_test)
        stop_button = QPushButton("Übertragung anhalten")
        stop_button.clicked.connect(self.stop_display)
        action_row.addWidget(preview_button)
        action_row.addWidget(apply_button)
        action_row.addWidget(test_button)
        action_row.addWidget(stop_button)
        outer.addLayout(action_row)

        safety = QLabel(
            "Hardwarezugriff erfolgt ausschließlich über das separat installierte GPL-Backend TRCC Linux. "
            "OHC lädt keine Herstellerdesigns aus dem Internet und liefert die importierten Dateien nicht mit aus."
        )
        safety.setWordWrap(True)
        safety.setObjectName("warningText")
        outer.addWidget(safety)
        self.canvas.set_specs(self.overlay_specs)
        self.canvas.set_split_mode(saved_split)

    def _load_overlays(self) -> list[OverlaySpec]:
        raw = str(self.settings.value("thermalright/overlays", "") or "")
        if not raw:
            return list(DEFAULT_OVERLAYS)
        try:
            values = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return list(DEFAULT_OVERLAYS)
        defaults = {item.ident: item for item in DEFAULT_OVERLAYS}
        loaded: list[OverlaySpec] = []
        if isinstance(values, list):
            for value in values:
                if not isinstance(value, dict) or value.get("ident") not in defaults:
                    continue
                base = defaults[str(value["ident"])]
                loaded.append(replace(
                    base,
                    x=int(value.get("x", base.x)), y=int(value.get("y", base.y)),
                    size=int(value.get("size", base.size)), color=str(value.get("color", base.color)),
                    visible=bool(value.get("visible", base.visible)),
                ).bounded())
        by_id = {item.ident: item for item in loaded}
        return [by_id.get(item.ident, item) for item in DEFAULT_OVERLAYS]

    def _save_overlays(self) -> None:
        self.settings.setValue("thermalright/overlays", json.dumps([asdict(item) for item in self.overlay_specs]))

    def _log(self, message: str) -> None:
        if self.log_ready and self.log_callback:
            self.log_callback(f"THERMALRIGHT: {message}")

    def _status(self, message: str, *, error: bool = False) -> None:
        self.preview_status.setText(message)
        self.preview_status.setObjectName("warningText" if error else "muted")
        self.preview_status.style().unpolish(self.preview_status)
        self.preview_status.style().polish(self.preview_status)
        self._log(message)

    def refresh_backend_status(self) -> None:
        self.cli = ThermalrightCli()
        if self.cli.available:
            self.backend_status.setText("TRCC-Linux-Backend gefunden · Gerät noch nicht geprüft")
        else:
            self.backend_status.setText("TRCC-Linux-Backend fehlt · Testmodus und Designimport funktionieren trotzdem")

    def _on_test_mode_changed(self, checked: bool) -> None:
        self.settings.setValue("thermalright/test_mode", checked)
        self._status("Testmodus aktiv · keine USB-Schreibzugriffe" if checked else "Hardwaremodus freigegeben · Aktionen benötigen TRCC Linux")

    def choose_media_directory(self) -> None:
        current = str(self.settings.value("thermalright/media_directory", str(Path.home())) or Path.home())
        selected = QFileDialog.getExistingDirectory(self, "Thermalright-Designordner auswählen", current)
        if selected:
            self.load_media_directory(Path(selected))

    def load_media_directory(self, directory: Path, *, quiet: bool = False) -> None:
        try:
            self.media_entries = scan_media_directory(directory)
        except ValueError as exc:
            self._status(str(exc), error=True)
            return
        self.settings.setValue("thermalright/media_directory", str(directory.resolve()))
        self.media_directory_label.setText(f"{directory.resolve()} · {len(self.media_entries)} lokale Designs")
        self._populate_media_combo(self.media_entries)
        if not quiet:
            self._status(f"{len(self.media_entries)} Designs lokal eingelesen · keine Dateien kopiert")

    def _populate_media_combo(self, entries: Iterable[MediaEntry]) -> None:
        current_path = self.current_media_path()
        self.media_combo.blockSignals(True)
        self.media_combo.clear()
        selected_index = -1
        for entry in entries:
            icon = "▣" if entry.kind == "theme" else "▶" if entry.kind == "video" else "▧"
            self.media_combo.addItem(f"{icon}  {entry.relative_name}", str(entry.path))
            if current_path and entry.path == current_path:
                selected_index = self.media_combo.count() - 1
        self.media_combo.blockSignals(False)
        if self.media_combo.count():
            self.media_combo.setCurrentIndex(max(0, selected_index))
            self.update_preview()

    def _apply_media_filter(self, text: str) -> None:
        needle = text.strip().casefold()
        self._populate_media_combo(
            entry for entry in self.media_entries if not needle or needle in entry.relative_name.casefold()
        )

    def current_media_path(self) -> Path | None:
        raw = self.media_combo.currentData() if hasattr(self, "media_combo") else None
        return Path(str(raw)) if raw else None

    def _preview_source(self, media: Path) -> Path | None:
        if media.is_dir():
            for name in ("Theme.png", "00.png"):
                candidate = media / name
                if candidate.is_file():
                    return candidate
            return None
        if media.suffix.casefold() in SUPPORTED_IMAGE_SUFFIXES:
            return media
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            return None
        fingerprint = hashlib.sha256(f"{media}:{media.stat().st_mtime_ns}".encode("utf-8")).hexdigest()[:20]
        target = self.cache_dir / f"{fingerprint}.jpg"
        if not target.is_file():
            completed = subprocess.run(
                [ffmpeg, "-v", "error", "-ss", "0.2", "-i", str(media), "-frames:v", "1", "-q:v", "3", str(target)],
                capture_output=True, text=True, timeout=20, check=False,
            )
            if completed.returncode != 0:
                return None
        return target

    @staticmethod
    def _fit_pixmap(source: Path) -> QPixmap:
        pixmap = QPixmap(str(source))
        if pixmap.isNull():
            return QPixmap()
        scaled = pixmap.scaled(
            LEVITA_WIDTH, LEVITA_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = max(0, (scaled.width() - LEVITA_WIDTH) // 2)
        y = max(0, (scaled.height() - LEVITA_HEIGHT) // 2)
        return scaled.copy(x, y, LEVITA_WIDTH, LEVITA_HEIGHT)

    def update_preview(self) -> None:
        media = self.current_media_path()
        if not media:
            self.canvas.set_background(QPixmap())
            return
        source = self._preview_source(media)
        pixmap = self._fit_pixmap(source) if source else QPixmap()
        self.canvas.set_background(pixmap)
        self.canvas.set_specs(self.overlay_specs)
        self.canvas.set_split_mode(int(self.split_mode.currentData() or 0))
        if pixmap.isNull():
            self._status("Datei erkannt, aber Vorschau konnte nicht erzeugt werden", error=True)
        else:
            self._status(f"Vorschau: {media.name}")

    def _split_mode_changed(self) -> None:
        mode = int(self.split_mode.currentData() or 0)
        self.settings.setValue("thermalright/split_mode", mode)
        self.canvas.set_split_mode(mode)

    def _overlay_index(self, ident: str) -> int:
        return next(index for index, item in enumerate(self.overlay_specs) if item.ident == ident)

    def _overlay_control_changed(self, ident: str, **changes: object) -> None:
        index = self._overlay_index(ident)
        self.overlay_specs[index] = clamp_overlay_outside_cutout(replace(self.overlay_specs[index], **changes))
        self._sync_overlay_controls(ident)
        self._save_overlays()
        self.canvas.set_specs(self.overlay_specs)

    def _overlay_moved(self, ident: str, x: int, y: int) -> None:
        index = self._overlay_index(ident)
        updated = clamp_overlay_outside_cutout(replace(self.overlay_specs[index], x=x, y=y))
        if updated.x == self.overlay_specs[index].x and updated.y == self.overlay_specs[index].y:
            return
        self.overlay_specs[index] = updated
        self._sync_overlay_controls(ident)
        self._save_overlays()

    def _sync_overlay_controls(self, ident: str) -> None:
        spec = self.overlay_specs[self._overlay_index(ident)]
        controls = self.overlay_controls.get(ident, {})
        for name, value in (("visible", spec.visible), ("x", spec.x), ("y", spec.y), ("size", spec.size)):
            widget = controls.get(name)
            if widget is None:
                continue
            widget.blockSignals(True)
            if isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value))
            widget.blockSignals(False)
        color_button = controls.get("color")
        if isinstance(color_button, QPushButton):
            color_button.setText(spec.color)
            color_button.setStyleSheet(f"color: {spec.color};")

    def _choose_overlay_color(self, ident: str) -> None:
        spec = self.overlay_specs[self._overlay_index(ident)]
        color = QColorDialog.getColor(QColor(spec.color), self, f"Farbe für {spec.label}")
        if color.isValid():
            self._overlay_control_changed(ident, color=color.name())

    def reset_overlays(self) -> None:
        self.overlay_specs = list(DEFAULT_OVERLAYS)
        for spec in self.overlay_specs:
            self._sync_overlay_controls(spec.ident)
        self._save_overlays()
        self.canvas.set_specs(self.overlay_specs)
        self._status("Hardware-Infos auf sichere Standardpositionen zurückgesetzt")

    def detect_backend_and_device(self) -> None:
        self.refresh_backend_status()
        if not self.cli.available:
            self._status("TRCC Linux ist nicht installiert; die lokale Vorschau bleibt vollständig nutzbar", error=True)
            return
        self._start_queue([(self.cli.version_args(), False), (self.cli.detect_args(), False)], self._detect_finished)
        self._status("Backend und Thermalright-Gerät werden gelesen …")

    def _detect_finished(self, ok: bool, output: str) -> None:
        detected = ok and parse_detect_output(output)
        if detected:
            self.backend_status.setText("TRCC Linux bereit · Thermalright 87ad:70db erkannt")
            self._status("Thermalright-Display erkannt · Hardwaremodus kann verwendet werden")
        else:
            self.backend_status.setText("TRCC Linux gefunden · Thermalright 87ad:70db nicht erkannt")
            self._status("Backend vorhanden, aber das Display wurde nicht erkannt oder ist bereits belegt", error=True)

    def apply_design(self) -> None:
        self.update_preview()
        media = self.current_media_path()
        if not media:
            self._status("Zuerst einen Designordner importieren und ein Design auswählen", error=True)
            return
        if self.test_mode.isChecked():
            self._status("Testmodus: Design und Hardware-Infos nur in der Vorschau angewendet")
            return
        self.refresh_backend_status()
        if not self.cli.available:
            self._status("Hardwaremodus benötigt das separat installierte TRCC-Linux-Backend", error=True)
            return
        try:
            sequence = build_apply_sequence(
                self.cli, media, self.overlay_specs,
                split_mode=int(self.split_mode.currentData() or 0),
            )
        except (RuntimeError, ValueError) as exc:
            self._status(str(exc), error=True)
            return
        self._stop_play_process()
        self._start_queue(sequence, self._apply_finished)
        self._status("Design, Notch-Modus und Hardware-Infos werden übertragen …")

    def _apply_finished(self, ok: bool, output: str) -> None:
        if not ok:
            detail = output.strip().splitlines()[-1] if output.strip() else "unbekannter Backendfehler"
            self._status(f"Übertragung fehlgeschlagen: {detail}", error=True)
            return
        try:
            args = self.cli.play_args(0.15)
        except RuntimeError as exc:
            self._status(str(exc), error=True)
            return
        self.play_process = QProcess(self)
        self.play_process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.play_process.finished.connect(self._play_finished)
        self.play_process.start(args[0], list(args[1:]))
        self._status("Levita-Design aktiv · Hintergrund und Hardwarewerte werden live aktualisiert")

    def run_display_test(self) -> None:
        if self.test_mode.isChecked():
            self.test_color_index = 0
            self.test_timer.start()
            self._next_test_color()
            self._status("Testmodus: lokaler Farbtest läuft · keine USB-Daten gesendet")
            return
        self.refresh_backend_status()
        if not self.cli.available:
            self._status("Display-Test benötigt das TRCC-Linux-Backend", error=True)
            return
        self._stop_play_process()
        self._start_queue([(self.cli.test_args(0.5), False)], self._test_finished)
        self._status("Sicherer Display-Farbtest läuft …")

    def _next_test_color(self) -> None:
        if self.test_color_index >= len(self.test_colors):
            self.test_timer.stop()
            self.update_preview()
            return
        pixmap = QPixmap(LEVITA_WIDTH, LEVITA_HEIGHT)
        pixmap.fill(self.test_colors[self.test_color_index])
        self.canvas.set_background(pixmap)
        self.test_color_index += 1

    def _test_finished(self, ok: bool, output: str) -> None:
        self._status("Display-Farbtest abgeschlossen" if ok else f"Display-Farbtest fehlgeschlagen: {output.strip()}", error=not ok)

    def stop_display(self) -> None:
        self.test_timer.stop()
        self._stop_play_process()
        if self.test_mode.isChecked() or not self.cli.available:
            self.update_preview()
            self._status("Test-/Vorschaumodus angehalten")
            return
        self._start_queue([(self.cli.stop_video_args(), True)], lambda _ok, _out: self._status("Thermalright-Übertragung angehalten"))

    def _stop_play_process(self) -> None:
        if self.play_process and self.play_process.state() != QProcess.ProcessState.NotRunning:
            self.play_process.terminate()
            if not self.play_process.waitForFinished(1200):
                self.play_process.kill()
                self.play_process.waitForFinished(600)
        self.play_process = None

    def _play_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        process = self.sender()
        if process is not self.play_process:
            return
        if exit_code != 0:
            detail = bytes(process.readAllStandardError()).decode("utf-8", errors="replace").strip()
            self._status(f"Thermalright-Livestream beendet: {detail or 'Backendfehler'}", error=True)
        self.play_process = None

    def _start_queue(
        self,
        commands: Iterable[tuple[tuple[str, ...], bool]],
        done: Callable[[bool, str], None],
    ) -> None:
        if self.command_process.state() != QProcess.ProcessState.NotRunning:
            self.command_process.kill()
            self.command_process.waitForFinished(500)
        self.command_queue = list(commands)
        self.command_outputs = []
        self.queue_done = done
        self._start_next_command()

    def _start_next_command(self) -> None:
        if not self.command_queue:
            done, self.queue_done = self.queue_done, None
            if done:
                done(True, "\n".join(self.command_outputs))
            return
        args, self.current_tolerates_failure = self.command_queue.pop(0)
        self.command_process.start(args[0], list(args[1:]))

    def _on_command_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        stdout = bytes(self.command_process.readAllStandardOutput()).decode("utf-8", errors="replace")
        stderr = bytes(self.command_process.readAllStandardError()).decode("utf-8", errors="replace")
        output = (stdout + "\n" + stderr).strip()
        if output:
            self.command_outputs.append(output)
        if exit_code != 0 and not self.current_tolerates_failure:
            self.command_queue.clear()
            done, self.queue_done = self.queue_done, None
            if done:
                done(False, "\n".join(self.command_outputs))
            return
        self._start_next_command()

    def closeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self.shutdown()
        super().closeEvent(event)

    def shutdown(self) -> None:
        """Stop child processes without issuing a new hardware command."""
        self.test_timer.stop()
        self._stop_play_process()
        if self.command_process.state() != QProcess.ProcessState.NotRunning:
            self.command_process.kill()
            self.command_process.waitForFinished(500)
