#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Lightweight category transitions and performance settings."""

from __future__ import annotations

from pathlib import Path
import json
import shutil
import time
from typing import Any
from shiboken6 import isValid

from PySide6.QtCore import QChildEvent, QEasingCurve, QEvent, QObject, QProcess, QTimer, QVariantAnimation
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QFormLayout, QGroupBox, QLabel, QTabWidget, QVBoxLayout, QWidget

from .cache import CACHE_BUDGETS_MB, DEFAULT_CACHE_MB, cache_budget_mb, cache_root
from .page_transition import TransitionOverlay, transition_duration
from modules.platform_support.v1_0 import helper_command


_USER_ACTIVITY_EVENTS = frozenset({
    QEvent.Type.MouseButtonPress, QEvent.Type.KeyPress, QEvent.Type.Wheel,
    QEvent.Type.TouchBegin, QEvent.Type.TabletPress,
})
_OVERLAY_EVENTS = frozenset({QEvent.Type.Resize, QEvent.Type.Hide, QEvent.Type.Close})


class UiPerformanceController(QObject):
    def __init__(self, host: QWidget) -> None:
        super().__init__(host)
        self.host = host
        self.settings = host.settings
        self.animations: dict[QWidget, QVariantAnimation] = {}
        self.overlays: dict[QWidget, TransitionOverlay] = {}
        self.attached_tabs: set[QTabWidget] = set()
        self._tab_scan_pending = False
        self.closing = False
        self.cache_worker = QProcess(self)
        self.cache_worker.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.cache_worker.finished.connect(self._cache_maintenance_finished)
        self.last_user_activity_at = time.monotonic()
        host.installEventFilter(self)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        for tabs in host.findChildren(QTabWidget):
            self._attach(tabs)
        self.maintenance_timer = QTimer(self)
        self.maintenance_timer.setSingleShot(True)
        self.maintenance_timer.timeout.connect(self.enforce_cache_budget)
        self.maintenance_timer.start(60_000)
        self.memory_reclaim_timer = QTimer(self)
        self.memory_reclaim_timer.setSingleShot(True)
        self.memory_reclaim_timer.setInterval(1_500)
        self.memory_reclaim_timer.timeout.connect(self.reclaim_idle_memory)

    def _attach(self, tabs: QTabWidget) -> None:
        if tabs in self.attached_tabs:
            return
        self.attached_tabs.add(tabs)
        tabs.currentChanged.connect(lambda index, widget=tabs: self._changed(widget, index))

    def _changed(self, tabs: QTabWidget, index: int) -> None:
        self.host.last_ui_navigation_at = time.monotonic()
        if tabs is not getattr(self.host, "tabs", None):
            return
        self.schedule_memory_reclaim()
        if not self.settings.value("performance/transitions_enabled", True, type=bool):
            return
        page = tabs.widget(index)
        if page is not None:
            QTimer.singleShot(0, self, lambda target=page: self.play(target))

    def play(self, page: QWidget) -> None:
        if self.closing or getattr(self.host, "explicit_quit_requested", False): return
        if (not isValid(page) or not page.isVisible() or self.host.isMinimized()
                or page is not self.host.tabs.currentWidget()
                or not self.settings.value("performance/transitions_enabled", True, type=bool)):
            return
        self.stop_transitions()
        style = str(self.settings.value("performance/transition_style", "fade") or "fade")
        if style not in {"fade", "slide", "rise", "glow"}:
            style = "fade"
        overlay = self.overlays.get(page)
        if overlay is None:
            overlay = TransitionOverlay(page, style, QColor(getattr(self.host, "accent_hex", "#00aaff")))
            self.overlays[page] = overlay
            page.installEventFilter(self)
            page.destroyed.connect(lambda _obj=None, target=page: self._forget_page(target))
        overlay.style_name = style
        overlay.accent = QColor(getattr(self.host, "accent_hex", "#00aaff"))
        overlay.prepare(style)
        overlay.raise_(); overlay.show()
        animation = QVariantAnimation(self)
        animation.setDuration(transition_duration(self.settings))
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(0.0); animation.setEndValue(1.0)
        animation.valueChanged.connect(overlay.set_progress)
        animation.finished.connect(overlay.finish)
        animation.finished.connect(lambda target=page: self.animations.pop(target, None))
        animation.finished.connect(animation.deleteLater)
        self.animations[page] = animation
        animation.start()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        event_type = event.type()
        if event_type in _USER_ACTIVITY_EVENTS:
            self.last_user_activity_at = time.monotonic()
            if self.cache_worker.state() == QProcess.ProcessState.NotRunning:
                self.maintenance_timer.start(5_000)
        elif event_type == QEvent.Type.ChildAdded and isinstance(event, QChildEvent):
            # A QTabWidget may still have a plain QWidget wrapper while its C++
            # constructor emits ChildAdded. Coalesce only host widget additions;
            # timers, processes and other windows never trigger a full scan.
            child = event.child()
            if isinstance(child, QWidget) and self._belongs_to_host(watched):
                self._queue_tab_scan()
        elif watched is self.host and event_type in {QEvent.Type.Hide, QEvent.Type.WindowStateChange}:
            if not self.host.isVisible() or self.host.isMinimized():
                self.stop_transitions()
        elif event_type in _OVERLAY_EVENTS and isinstance(watched, QWidget) and watched in self.overlays:
            self._stop_transition(watched)
        return False

    def _stop_transition(self, page: QWidget) -> None:
        animation = self.animations.pop(page, None)
        if animation is not None:
            animation.stop()
            animation.deleteLater()
        overlay = self.overlays.get(page)
        if overlay is not None and isValid(overlay):
            overlay.finish()

    def stop_transitions(self) -> None:
        for page in tuple(self.animations):
            self._stop_transition(page)

    def _forget_page(self, page: QWidget) -> None:
        self.overlays.pop(page, None)
        animation = self.animations.pop(page, None)
        if animation is not None and isValid(animation):
            animation.stop()
            animation.deleteLater()

    def schedule_memory_reclaim(self) -> None:
        """Debounce reclamation until hidden preview decoders have stopped."""

        if not self.closing:
            self.memory_reclaim_timer.start()

    def reclaim_idle_memory(self) -> None:
        if self.closing:
            return
        from .memory import release_idle_memory
        release_idle_memory()

    def _attach_new_tabs(self) -> None:
        self._tab_scan_pending = False
        if self.closing or not isValid(self.host): return
        for tabs in self.host.findChildren(QTabWidget):
            self._attach(tabs)

    def _belongs_to_host(self, watched: QObject) -> bool:
        try:
            return watched is self.host or (
                isinstance(watched, QWidget) and self.host.isAncestorOf(watched)
            )
        except RuntimeError:
            return False

    def _queue_tab_scan(self) -> None:
        if self.closing or self._tab_scan_pending:
            return
        self._tab_scan_pending = True
        QTimer.singleShot(0, self, self._attach_new_tabs)

    def enforce_cache_budget(self) -> None:
        if self.closing or getattr(self.host, "explicit_quit_requested", False): return
        if self.cache_worker.state() != QProcess.ProcessState.NotRunning:
            return
        if time.monotonic() - self.last_user_activity_at < 4.0:
            self.maintenance_timer.start(4_000)
            return
        budget = int(self.settings.value("performance/ssd_cache_mb", DEFAULT_CACHE_MB))
        if budget not in CACHE_BUDGETS_MB:
            budget = DEFAULT_CACHE_MB
        helper = Path(__file__).with_name("maintenance.py")
        program, arguments = helper_command(helper, (cache_root(), budget * 1024 * 1024))
        ionice = shutil.which("ionice")
        if ionice:
            self.cache_worker.start(ionice, ["-c", "3", program, *arguments])
        else:
            self.cache_worker.start(program, arguments)

    def schedule_cache_maintenance(self) -> None:
        if not self.closing:
            self.maintenance_timer.start(5_000)

    def _cache_maintenance_finished(self, _code: int, _status: object) -> None:
        output = bytes(self.cache_worker.readAllStandardOutput()).decode("utf-8", "replace").strip()
        if not output:
            return
        try:
            payload = json.loads(output.splitlines()[-1])
        except (TypeError, ValueError, json.JSONDecodeError):
            return
        logger = getattr(self.host, "log_message", None)
        if callable(logger):
            logger(
                "UI-CACHE: Wartung beendet · "
                f"Dauer={float(payload.get('elapsed_ms', 0.0)):.0f} ms · "
                f"Dateien={int(payload.get('files', 0))} · entfernt={int(payload.get('removed', 0))} · "
                f"verbleibend={int(payload.get('total', 0))} Byte · I/O-Priorität=niedrig"
            )

    def shutdown(self) -> None:
        self.closing = True
        self.maintenance_timer.stop()
        self.memory_reclaim_timer.stop()
        self.stop_transitions()
        if self.cache_worker.state() != QProcess.ProcessState.NotRunning:
            self.cache_worker.terminate()
            if not self.cache_worker.waitForFinished(300):
                self.cache_worker.kill()
                self.cache_worker.waitForFinished(300)
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)


def _save_performance_setting(host: Any, key: str, value: object) -> None:
    host.settings.setValue(key, value)
    host.settings.sync()
    controller = getattr(host, "ui_performance", None)
    if controller is not None:
        if key.endswith("ssd_cache_mb"):
            controller.schedule_cache_maintenance()
        elif key.startswith("performance/transition"):
            controller.stop_transitions()


def build_performance_settings(host: Any, layout: QVBoxLayout) -> None:
    box = QGroupBox("Leistung und SSD-Cache")
    form = QFormLayout(box)
    host.page_transitions_checkbox = QCheckBox("Seitenwechsel animieren")
    host.page_transitions_checkbox.setChecked(host.settings.value("performance/transitions_enabled", True, type=bool))
    host.page_transition_style_combo = QComboBox()
    for label, key in (("Sanft einblenden", "fade"), ("Seitlich gleiten", "slide"), ("Von unten gleiten", "rise"), ("Lichtakzent", "glow")):
        host.page_transition_style_combo.addItem(label, key)
    host.page_transition_style_combo.setCurrentIndex(max(0, host.page_transition_style_combo.findData(host.settings.value("performance/transition_style", "fade"))))
    host.page_transition_duration_combo = QComboBox()
    for label, duration in (("Zügig · 220 ms", 220), ("Ruhig · 380 ms", 380), ("Langsam · 550 ms", 550)):
        host.page_transition_duration_combo.addItem(label, duration)
    host.page_transition_duration_combo.setCurrentIndex(
        host.page_transition_duration_combo.findData(transition_duration(host.settings)))
    host.page_transition_duration_combo.currentIndexChanged.connect(lambda: _save_performance_setting(
        host, "performance/transition_duration_ms", host.page_transition_duration_combo.currentData()))
    host.ssd_cache_combo = QComboBox()
    for label, value in (("0 GB", 0), ("0,5 GB", 512), ("1 GB", 1024), ("2 GB", 2048), ("4 GB", 4096)):
        host.ssd_cache_combo.addItem(label, value)
    host.ssd_cache_combo.setCurrentIndex(host.ssd_cache_combo.findData(cache_budget_mb(host.settings)))
    note = QLabel("Der begrenzte Cache beschleunigt LCD- und Wallpaper-Kataloge sowie Vorschaubilder. Alte, jederzeit neu erzeugbare Einträge werden automatisch zuerst entfernt; Originaldateien bleiben unverändert.")
    note.setWordWrap(True); note.setObjectName("muted")
    host.page_transitions_checkbox.toggled.connect(lambda value: _save_performance_setting(host, "performance/transitions_enabled", value))
    host.page_transition_style_combo.currentIndexChanged.connect(lambda: _save_performance_setting(host, "performance/transition_style", host.page_transition_style_combo.currentData()))
    host.ssd_cache_combo.currentIndexChanged.connect(lambda: _save_performance_setting(host, "performance/ssd_cache_mb", host.ssd_cache_combo.currentData()))
    form.addRow(host.page_transitions_checkbox)
    form.addRow("Übergang", host.page_transition_style_combo)
    form.addRow("Übergangsdauer", host.page_transition_duration_combo)
    form.addRow("SSD-Cache", host.ssd_cache_combo)
    form.addRow(note)
    layout.addWidget(box)


def install_ui_performance(host: QWidget) -> UiPerformanceController:
    return UiPerformanceController(host)
