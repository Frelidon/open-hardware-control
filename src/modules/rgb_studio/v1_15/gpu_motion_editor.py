# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only paired LED preview and bounded GPU motion controls."""
import time
from dataclasses import replace

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QSlider, QVBoxLayout, QWidget

from rgb_effects import RGBEffectConfig
from .gpu_motion import DEFAULT, RANGES, configured_count, load, support_count
from .gpu_strip_sampling import render_gpu_strip_frame, strip_clock
from .slot_routes import slot_routes


class LedRows(QWidget):
    def __init__(self, editor, kind):
        super().__init__(editor)
        self.editor = editor
        self.kind = kind
        self.setMinimumHeight(50)

    def paintEvent(self, _event):
        editor = self.editor
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#101a2a"))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        count = editor.gpu_count if self.kind == "gpu" else editor.support_count
        if not count:
            return
        frame = render_gpu_strip_frame(editor.effect(), count, editor.elapsed(),
                                       sync_count=max(editor.gpu_count, editor.support_count),
                                       tuning=editor.values(), role=self.kind)
        usable = max(1., self.width() - 32.)
        gap = usable / count
        width = min(17., max(2., gap * .68))
        for index, color in enumerate(frame):
            x = 16. + gap * (index + .5) - width / 2.
            painter.setBrush(QColor("#" + color))
            painter.drawRoundedRect(QRectF(x, 6, width, 38), min(6., width / 3.), 6.)


class GpuMotionEditor(QGroupBox):
    """Settings remain in draft until the parent GPU routing dialog commits."""

    def __init__(self, host, gpu_id, parent=None):
        tr = host.tr_static
        super().__init__(tr("LED-Lichtverlauf"), parent)
        self.setObjectName("gpuMotionEditor")
        self.host = host
        self.gpu_id = gpu_id
        self.gpu_count = 0
        self.support_count = support_count(host)
        self.sync_enabled = True
        self._support_visible = None
        self.gpu_controller = ""
        self.gpu_zone = ""
        self._start = time.monotonic()
        layout = QVBoxLayout(self)
        self.gpu_label = QLabel()
        self.support_label = QLabel()
        layout.addWidget(self.gpu_label)
        self.rows = (LedRows(self, "gpu"), LedRows(self, "support"))
        layout.addWidget(self.rows[0])
        layout.addWidget(self.support_label)
        layout.addWidget(self.rows[1])
        form = QFormLayout()
        self.form = form
        layout.addLayout(form)
        self.sliders = {}
        for key, caption in (("gpu_lead", "Vorlauf"), ("gpu_tail", "Auslauf"),
                             ("gpu_peak", "Helligkeit"),
                             ("support_lead", "Vorlauf"), ("support_tail", "Auslauf"),
                             ("tempo", "Geschwindigkeit")):
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setObjectName("gpuMotion" + "".join(part.title() for part in key.split("_")))
            slider.setRange(*RANGES[key])
            slider.setValue(load(host)[key])
            value = QLabel(f"{slider.value()} %")
            value.setMinimumWidth(52)
            row = QHBoxLayout()
            row.addWidget(slider, 1)
            row.addWidget(value)
            title = (tr("Grafikkarte") + " · " if key.startswith("gpu_") else
                     tr("Grafikkartenhalterung") + " · " if key.startswith("support_") else "")
            form.addRow(title + (tr("Weiß") + " · " + tr(caption) if key == "gpu_peak" else tr(caption)), row)
            slider.valueChanged.connect(lambda current, label=value: (
                label.setText(f"{current} %"), self.preview_changed()))
            self.sliders[key] = slider
        reset = QPushButton(tr("↺  Standard wiederherstellen"))
        reset.setObjectName("gpuMotionReset")
        reset.clicked.connect(self.reset_defaults)
        layout.addWidget(reset)
        calibrate = QPushButton(tr("LED-Flüssigkeit abstimmen"))
        calibrate.setObjectName("gpuMotionCalibrate")
        calibrate.clicked.connect(self.calibrate)
        layout.addWidget(calibrate)
        self.transport = QLabel()
        layout.addWidget(self.transport)
        note = QLabel(tr("Bei aktivem Effekt live; Abbrechen stellt zurück. Licht nicht rücklesbar."))
        note.setWordWrap(True)
        layout.addWidget(note)
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.refresh)
        self.refresh()

    def values(self):
        return {key: slider.value() for key, slider in self.sliders.items()}

    def reset_defaults(self):
        for key, value in DEFAULT.items():
            self.sliders[key].setValue(value)
        self.reset_preview_phase()

    def calibrate(self):
        from .gpu_motion_wizard import GpuMotionWizard, prepare
        from openrgb_integration import OpenRGBError
        try:
            plan, reason = prepare(self.host, self)
        except (OpenRGBError, ValueError) as exc:
            plan, reason = None, str(exc)
        if plan is None:
            QMessageBox.information(self, self.host.tr_static("LED-Flüssigkeit abstimmen"), reason)
            return
        if GpuMotionWizard(self, plan).exec() == GpuMotionWizard.DialogCode.Accepted:
            callback = getattr(self, "calibration_saved", None)
            if callback is not None:
                callback()

    def preview_changed(self):
        self.host.rgb_gpu_motion_preview = self.values()
        for row in self.rows:
            row.update()

    def clear_live_preview(self):
        if getattr(self.host, "rgb_gpu_motion_preview", None) is not None:
            self.host.rgb_gpu_motion_preview = None
            # The running timer sends the stored settings on its next tick.

    def effect(self):
        group = getattr(self.host, "rgb_group_assignments", {}).get(self.gpu_id, "ungrouped")
        config = getattr(self.host, "rgb_group_effect_configs", {}).get(group)
        if config is not None and getattr(self.host, "rgb_gpu_calibration_targets", None) is not None:
            return replace(config, primary="0000ff", secondary="ffffff")
        return config if config is not None and config.effect_id in {"spinner", "comet"} else RGBEffectConfig(
            "spinner", "0000ff", "ffffff", speed=100)

    def elapsed(self):
        # During a running design, show the same paced frame time that the
        # hardware worker receives; a free-running 25-Hz UI animation can
        # otherwise look smooth while the real controller is falling behind.
        if getattr(self.host, "openrgb_effect_active", False):
            paced = getattr(self.host, "rgb_gpu_visual_elapsed", None)
            if type(paced) in (int, float) and 0 <= paced < 1e9:
                return float(paced)
        return max(0., time.monotonic() - self._start)

    def reset_preview_phase(self):
        count = max(1, self.gpu_count, self.support_count)
        clock = strip_clock(self.effect(), count, self.values())
        self._start = time.monotonic() - (clock["padding"] + .18) / clock["rate"]

    def set_route(self, controller, zone):
        self.gpu_controller, self.gpu_zone = controller or "", zone or ""
        self.gpu_count = configured_count(self.host, self.gpu_controller, self.gpu_zone)
        self.reset_preview_phase()
        self.refresh()

    def set_sync_enabled(self, enabled):
        self.sync_enabled = bool(enabled)
        self.refresh()

    def refresh(self):
        tr = self.host.tr_static
        gpu_text = f"{tr('Grafikkarte')} · {self.gpu_count if self.gpu_count else '—'} {tr('LEDs')}"
        support_text = f"{tr('Grafikkartenhalterung')} · {self.support_count if self.support_count else '—'} {tr('LEDs')}"
        if self.gpu_label.text() != gpu_text:
            self.gpu_label.setText(gpu_text)
        if self.support_label.text() != support_text:
            self.support_label.setText(support_text)
        show_support = bool(self.sync_enabled and self.gpu_count and self.support_count)
        if show_support != self._support_visible:
            self.support_label.setVisible(show_support)
            self.rows[1].setVisible(show_support)
            self.form.setRowVisible(3, show_support)
            self.form.setRowVisible(4, show_support)
            self._support_visible = show_support
        metrics = getattr(self.host, "openrgb_worker_metrics", {})
        support = slot_routes(self.host).get("gpu-support", {}).get("controller", "")
        def rate(controller):
            item = metrics.get(controller, {})
            if item.get("last_success") and time.monotonic() - item["last_success"] > 2.:
                return "—"
            times = item.get("success_times", [])
            return f"{(len(times) - 1) / (times[-1] - times[0]):.1f} Hz" if len(times) >= 2 and times[-1] > times[0] else "—"
        status = f"{tr('Gemessene Bildrate')}: {tr('Grafikkarte')} {rate(self.gpu_controller)}"
        if show_support:
            status += f" · {tr('Grafikkartenhalterung')} {rate(support)}"
        if self.transport.text() != status:
            self.transport.setText(status)
        for row in self.rows:
            row.update()

    def showEvent(self, event):
        super().showEvent(event)
        self.reset_preview_phase()
        self.timer.start()

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)
