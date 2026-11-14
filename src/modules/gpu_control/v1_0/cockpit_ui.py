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
        self.tuning_gpu_art = QLabel()
        self.tuning_gpu_art.setObjectName("gpuCockpitArtwork")
        self.tuning_gpu_art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        artwork_actions = self.tuning_artwork_actions = QWidget()
        artwork_row = QHBoxLayout(artwork_actions)
        artwork_row.setContentsMargins(0, 0, 0, 0)
        import_artwork = QPushButton(self.tr("Eigenes GPU-Bild importieren"))
        import_artwork.clicked.connect(self.import_gpu_profile_artwork)
        reset_artwork = QPushButton(self.tr("GPU-Bild zurücksetzen"))
        reset_artwork.clicked.connect(self.remove_gpu_profile_artwork)
        artwork_row.addWidget(import_artwork)
        artwork_row.addWidget(reset_artwork)
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
        self.tuning_note.setToolTip(self.tuning_base_note)
        form.addRow(self.tuning_note)
        actions = QWidget()
        row = QGridLayout(actions)
        self.tuning_actions_grid = row
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
        layout = QGridLayout(row)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        label = QLabel(self.tr(title), objectName="gpuTuningLabel")
        label.setWordWrap(True)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setObjectName("gpuTuningSlider")
        slider.setMinimumWidth(80)
        spin.setObjectName("gpuTuningSpin")
        spin.setMinimumWidth(95)
        slider.setRange(round(spin.minimum() * factor), round(spin.maximum() * factor))
        slider.setValue(round(spin.value() * factor))
        slider.valueChanged.connect(
            lambda value, field=spin, scale=factor: field.setValue(
                value / scale if isinstance(field, QDoubleSpinBox) else value // scale
            )
        )
        spin.valueChanged.connect(lambda value, control=slider, scale=factor: control.setValue(round(value * scale)))
        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(slider, 1, 0)
        layout.addWidget(spin, 1, 1)
        layout.setColumnStretch(0, 1)
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
        """Compose live summary and editors on one page with direct section routes."""
        from .workspace_ui import build_workspace
        build_workspace(self)
        QTimer.singleShot(0, self, self._layout_gpu_cockpit)

    def refresh_workspace_language(self):
        """Restore dynamic presentation after the shared text translation pass."""
        self.fan_visual.refresh_language()
        self.fan_edit_hint.setText(self._fan_curve_locked_text())
        self._update_fan_workflow()
        self._refresh_gpu_dashboard()
        if self.devices.currentText():
            self.tuning_gpu_name.setText(self.devices.currentText())

    def _layout_gpu_cockpit(self) -> None:
        from .workspace_ui import reflow_toolbar
        if not hasattr(self, 'gpu_primary_workspace'): return
        self.gpu_primary_workspace.reflow(); self.gpu_summary_panel.reflow()
        reflow_toolbar(self)
        self._layout_tuning_actions()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        QTimer.singleShot(0, self, self._layout_fan_controls)

    def _layout_tuning_actions(self):
        grid = self.tuning_actions_grid
        while grid.count(): grid.takeAt(0)
        columns = 2 if self.tuning_page.width() >= 570 else 1
        for index, control in enumerate((self.test_button, self.save_button, self.preview_cancel, self.more_tuning_actions)):
            control.setMinimumHeight(38)
            grid.addWidget(control, index // columns, index % columns)
        grid.setColumnStretch(0, 1); grid.setColumnStretch(1, 0 if columns == 1 else 1)

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
        check = QPushButton("PCIe und PC-System in der Hardware-Prüfung prüfen")
        check.clicked.connect(lambda: self.host.tabs.setCurrentIndex(self.host.hardware_checker_page_index))
        layout.addWidget(check)
        self.sections.addTab(page, "Hardware")
