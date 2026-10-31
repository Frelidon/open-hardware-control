# SPDX-License-Identifier: GPL-3.0-or-later
"""GPU cockpit composition and responsive presentation, without hardware I/O."""
from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMenu, QPushButton, QSlider,
    QSpinBox, QVBoxLayout, QWidget)

class GpuCockpitUiMixin:
    def _build_tuning(self) -> None:
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(8, 8, 8, 8)
        form.setVerticalSpacing(6)
        self.tuning_form = form
        self.tuning_gpu_name = QLabel(self.tr("Grafikkarte"))
        self.tuning_gpu_name.setObjectName("gpuDeviceHeading")
        form.addRow(self.tuning_gpu_name)
        self.tuning_gpu_art = QLabel()
        self.tuning_gpu_art.setObjectName("gpuCockpitArtwork")
        self.tuning_gpu_art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tuning_gpu_art.setMinimumHeight(80)
        self.tuning_gpu_art.setMaximumHeight(105)
        form.addRow(self.tuning_gpu_art)
        artwork_actions = QWidget()
        artwork_row = QHBoxLayout(artwork_actions)
        artwork_row.setContentsMargins(0, 0, 0, 0)
        import_artwork = QPushButton(self.tr("Eigenes GPU-Bild importieren"))
        import_artwork.clicked.connect(self.import_gpu_profile_artwork)
        reset_artwork = QPushButton(self.tr("GPU-Bild zurücksetzen"))
        reset_artwork.clicked.connect(self.remove_gpu_profile_artwork)
        artwork_row.addWidget(import_artwork)
        artwork_row.addWidget(reset_artwork)
        form.addRow(artwork_actions)
        self.power = QDoubleSpinBox()
        self.power.setDecimals(1)
        self.power.setSuffix(" W")
        self.power.setRange(0, 1000)
        self.core = QSpinBox()
        self.core.setSuffix(" MHz")
        self.core.setRange(0, 10000)
        self.core.setSpecialValueText(self.tr("Nicht verfügbar"))
        self.memory = QSpinBox()
        self.memory.setSuffix(" MHz")
        self.memory.setRange(0, 10000)
        self.offset = QSpinBox()
        self.offset.setSuffix(" MHz")
        self.offset.setRange(-1000, 1000)
        power_row, self.power_slider = self._tuning_row("Leistungsgrenze", self.power, factor=10)
        core_row, self.core_slider = self._tuning_row("Maximaler GPU-Takt", self.core)
        memory_row, self.memory_slider = self._tuning_row("Maximaler Speichertakt", self.memory)
        offset_row, self.offset_slider = self._tuning_row("GPU-Taktversatz (RDNA4)", self.offset)
        form.addRow(power_row)
        self._build_power_guard(form)
        form.addRow(core_row)
        form.addRow(memory_row)
        form.addRow(offset_row)
        self.tuning_base_note = self.tr(
            "Nur von LACT gemeldete Basiswerte sind änderbar. Der Kurztest läuft unter Last und wird durch LACT automatisch zurückgestellt. Erst danach ist dauerhaftes Speichern möglich. Ein Kurztest beweist keine Langzeitstabilität."
        )
        self.tuning_note = QLabel(self.tuning_base_note)
        self.tuning_note.setWordWrap(True)
        self.tuning_note.setMaximumHeight(34)
        self.tuning_note.setToolTip(self.tuning_base_note)
        actions = QWidget()
        row = QGridLayout(actions)
        row.setContentsMargins(0, 0, 0, 0)
        self.test_button = QPushButton("Änderung kurz testen")
        self.test_button.setToolTip(self.tuning_base_note)
        self.test_button.clicked.connect(self.start_preview)
        self.preview_install = QPushButton(self.tr("vkmark installieren"))
        self.preview_install.clicked.connect(self.install_stress_tool)
        self.preview_cancel = QPushButton(self.tr("Abbrechen"))
        self.preview_cancel.clicked.connect(lambda: self._finish_preview(failure="Vom Nutzer abgebrochen"))
        self.preview_cancel.setEnabled(False)
        self.save_button = QPushButton("Getestete Änderung dauerhaft speichern")
        self.save_button.clicked.connect(self.save_tested)
        self.release_button = QPushButton("Vorherige Werte wiederherstellen")
        self.release_button.clicked.connect(self.restore_baseline)
        self.discard_button = QPushButton(self.tr("Eingaben verwerfen"))
        self.discard_button.clicked.connect(self.discard_gpu_inputs)
        self.factory_button = QPushButton(self.tr("LACT-Werte zurücksetzen"))
        self.factory_button.clicked.connect(self.reset_lact_profile)
        self.more_tuning_actions = QPushButton(self.tr("Weitere Aktionen"))
        more_menu = QMenu(self.more_tuning_actions)
        self.discard_menu_action = more_menu.addAction(self.discard_button.text(), self.discard_gpu_inputs)
        self.release_menu_action = more_menu.addAction(self.release_button.text(), self.restore_baseline)
        self.factory_menu_action = more_menu.addAction(self.factory_button.text(), self.reset_lact_profile)
        self.install_menu_action = more_menu.addAction(self.preview_install.text(), self.install_stress_tool)
        self.more_tuning_actions.setMenu(more_menu)
        self.test_button.setObjectName("gpuPrimaryAction")
        self.save_button.setObjectName("gpuCommitAction")
        row.addWidget(self.test_button, 0, 0)
        row.addWidget(self.save_button, 0, 1)
        row.addWidget(self.preview_cancel, 1, 0)
        row.addWidget(self.more_tuning_actions, 1, 1)
        form.addRow(actions)
        self.tuning_page = page
        self.sections.addTab(page, "Tuning")
        for widget in (self.power, self.core, self.memory, self.offset):
            widget.valueChanged.connect(self._invalidate_test)
        self._sync_buttons()

    def _tuning_row(self, title: str, spin, *, factor: int = 1) -> tuple[QFrame, QSlider]:
        row = QFrame(objectName="gpuTuningRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        label = QLabel(self.tr(title), objectName="gpuTuningLabel")
        label.setMinimumWidth(130)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setObjectName("gpuTuningSlider")
        slider.setMinimumWidth(105)
        spin.setObjectName("gpuTuningSpin")
        spin.setMinimumWidth(105)
        slider.setRange(round(spin.minimum() * factor), round(spin.maximum() * factor))
        slider.setValue(round(spin.value() * factor))
        slider.valueChanged.connect(
            lambda value, field=spin, scale=factor: field.setValue(
                value / scale if isinstance(field, QDoubleSpinBox) else value // scale
            )
        )
        spin.valueChanged.connect(lambda value, control=slider, scale=factor: control.setValue(round(value * scale)))
        layout.addWidget(label)
        layout.addWidget(slider, 1)
        layout.addWidget(spin)
        return row, slider

    def _sync_tuning_sliders(self) -> None:
        for spin, slider, factor in (
            (self.power, self.power_slider, 10),
            (self.core, self.core_slider, 1),
            (self.memory, self.memory_slider, 1),
            (self.offset, self.offset_slider, 1),
        ):
            slider.blockSignals(True)
            slider.setRange(round(spin.minimum() * factor), round(spin.maximum() * factor))
            slider.setValue(round(spin.value() * factor))
            slider.setEnabled(spin.isEnabled())
            slider.blockSignals(False)

    def _update_tuning_artwork(self) -> None:
        if not hasattr(self, "tuning_gpu_art"):
            return
        path = None
        if hasattr(self, "gpu_profile_artwork"):
            try:
                path = self._profile_art_path()
            except (OSError, RuntimeError):
                path = None
        if path is None:
            filename = "gpu-family-nvidia-green.png" if self.gpu_vendor == "NVIDIA" else "gpu-family-amd-red.png"
            path = Path(__file__).resolve().parents[3] / "assets" / "gpu" / filename
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            self.tuning_gpu_art.clear()
            return
        target = self.tuning_gpu_art.size()
        if target.width() < 100:
            target.setWidth(430)
            target.setHeight(190)
        self.tuning_gpu_art.setPixmap(pixmap.scaled(
            target, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation,
        ))

    def _assemble_control_cockpit(self) -> None:
        """Present the three primary GPU jobs together, like a hardware cockpit."""
        pages = (self.tuning_page, self.fan_page, self.stress_page)
        self.gpu_hero_card.show()
        self.gpu_metrics_panel.setParent(self.tuning_page)
        self.tuning_form.insertRow(1, self.gpu_metrics_panel)
        for page in pages:
            index = self.sections.indexOf(page)
            if index >= 0:
                self.sections.removeTab(index)

        cockpit = QWidget()
        cockpit.setObjectName("gpuCockpit")
        self.gpu_cockpit_layout = QGridLayout(cockpit)
        self.gpu_cockpit_layout.setContentsMargins(0, 12, 0, 0)
        self.gpu_cockpit_layout.setHorizontalSpacing(12)
        self.gpu_cockpit_layout.setVerticalSpacing(12)

        self.gpu_cockpit_columns = []
        for title, page in (("Übersicht && Taktung", self.tuning_page),
                            (self.tr("Lüfter"), self.fan_page),
                            ("Lasttest && Darstellung", self.stress_page)):
            column = QGroupBox(title)
            column.setObjectName("gpuWorkspaceColumn")
            column.setMinimumWidth(250)
            column_layout = QVBoxLayout(column)
            column_layout.setContentsMargins(10, 16, 10, 10)
            column_layout.addWidget(page)
            page.show()
            self.gpu_cockpit_columns.append(column)
        self.sections.insertTab(0, cockpit, "Steuerung")
        self.sections.setCurrentWidget(cockpit)
        self.gpu_cockpit_page = cockpit
        QTimer.singleShot(0, self, self._layout_gpu_cockpit)

    def _layout_gpu_cockpit(self) -> None:
        layout = getattr(self, "gpu_cockpit_layout", None)
        columns = getattr(self, "gpu_cockpit_columns", ())
        if layout is None or not columns:
            return
        while layout.count():
            layout.takeAt(0)
        width = self.viewport().width()
        if width >= 900:
            positions = ((0, 0, 1, 1), (0, 1, 1, 1), (0, 2, 1, 1))
        elif width >= 620:
            positions = ((0, 0, 1, 1), (0, 1, 1, 1), (1, 0, 1, 2))
        else:
            positions = ((0, 0, 1, 1), (1, 0, 1, 1), (2, 0, 1, 1))
        for column, position in zip(columns, positions):
            layout.addWidget(column, *position)
        for column_index in range(3):
            layout.setColumnStretch(column_index, 1 if width >= 900 else 0)
        # Fixed-height subcards silently clipped translated fan captions.
        # Retain the whole editor and permit scrolling only when necessary.
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        QTimer.singleShot(0, self, self._layout_fan_controls)

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().resizeEvent(event)
        if hasattr(self, "gpu_cockpit_layout"):
            self._layout_gpu_cockpit()
            self._update_tuning_artwork()

    def _build_metrics(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.metrics = self._table()
        layout.addWidget(self.metrics)
        button = QPushButton("GPU-Messwerte aktualisieren")
        button.clicked.connect(self.refresh_metrics)
        layout.addWidget(button)
        self.rgb_note = QLabel(self.tr(
            "Native GPU-Effekte benötigen kein Kabel. Manuelle LED-Zahlen gehören zum angeschlossenen 5-V-ARGB-Kanal."
        ))
        self.rgb_note.setWordWrap(True)
        layout.addWidget(self.rgb_note)
        self.rgb_devices = QComboBox()
        layout.addWidget(self.rgb_devices)
        rgb_button = QPushButton("Grafikkarte: Steuerweg und LEDs")
        rgb_button.clicked.connect(self.open_rgb_lighting)
        layout.addWidget(rgb_button)
        self.sections.addTab(page, "GPU")

    def _build_hardware(self) -> None:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.hardware = self._table()
        layout.addWidget(self.hardware)
        check = QPushButton("PCIe und PC-System im Hardware-Checker prüfen")
        check.clicked.connect(lambda: self.host.tabs.setCurrentIndex(self.host.hardware_checker_page_index))
        layout.addWidget(check)
        self.sections.addTab(page, "Hardware")
