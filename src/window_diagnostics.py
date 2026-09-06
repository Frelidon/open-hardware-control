#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Temporary Qt window/process diagnostics for unexplained startup windows."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import os
from pathlib import Path
import re
import sys
import time
from typing import Any

from PySide6.QtCore import QChildEvent, QEvent, QObject, QProcess, QTimer, Qt, Signal
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication, QComboBox, QFrame, QWidget

from privacy_logging import append_startup_event, redact_private_text


_ACTIVE_DIAGNOSTICS: "WindowProcessDiagnostics | None" = None
_AUDIT_HOOK_INSTALLED = False


def _enum_name(value: object) -> str:
    name = getattr(value, "name", "")
    if name:
        return str(name)
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return value.__class__.__name__


def _safe_process_tokens(arguments: Sequence[object]) -> str:
    """Keep useful command shapes without recording positional secrets."""
    tokens: list[str] = []
    skip_next = False
    sensitive = re.compile(r"(?i)(?:password|passwd|token|secret|api[-_]?key|credential)")
    safe_words = {
        "client", "detect", "devices", "display", "initialize", "list",
        "load-theme", "load-video", "play", "play-video", "server", "set",
        "status", "stop-video", "version",
    }
    for raw in list(arguments)[1:]:
        value = str(raw).strip()
        if not value:
            continue
        if skip_next:
            skip_next = False
            continue
        if value.startswith("-"):
            option = value.split("=", 1)[0]
            if re.fullmatch(r"-{1,2}[A-Za-z0-9][A-Za-z0-9_-]{0,40}", option):
                tokens.append(option)
                if sensitive.search(option) and "=" not in value:
                    skip_next = True
        elif value.casefold() in safe_words:
            tokens.append(value)
        if len(tokens) >= 6:
            break
    return ",".join(tokens) if tokens else "keine sicheren Tokens"


def process_start_summary(
    program: object,
    arguments: Sequence[object],
    environment: Mapping[str, object] | None = None,
    *,
    source: str,
) -> str:
    """Return a privacy-bounded helper-process diagnostic line."""
    executable = redact_private_text(str(program or "unbekannt"))
    name = Path(executable).name or executable
    env = environment or os.environ
    qt_platform = str(env.get("QT_QPA_PLATFORM", "vererbt/nicht gesetzt") or "leer")
    session = str(os.environ.get("XDG_SESSION_TYPE", "unbekannt") or "unbekannt")
    return (
        f"PROZESS START · Quelle={source} · Programm={name} · "
        f"Tokens={_safe_process_tokens(arguments)} · Anzahl={len(arguments)} · "
        f"QT_QPA_PLATFORM={qt_platform} · Sitzung={session}"
    )


def _object_label(obj: QObject | None) -> str:
    if obj is None:
        return "<kein Elternobjekt>"
    name = re.sub(r"\s+", " ", obj.objectName().strip()) or "<ohne Objektname>"
    return f"{obj.__class__.__name__}({redact_private_text(name)})"


def _object_parent_chain(obj: QObject, limit: int = 6) -> str:
    chain: list[str] = []
    parent = obj.parent()
    while parent is not None and len(chain) < limit:
        chain.append(_object_label(parent))
        parent = parent.parent()
    if parent is not None:
        chain.append("…")
    return " > ".join(chain) if chain else "<keine>"


def _direct_widget_children(widget: QWidget, limit: int = 10) -> str:
    children = [child for child in widget.children() if isinstance(child, QWidget)]
    labels: list[str] = []
    for child in children[:limit]:
        geometry = child.geometry()
        labels.append(
            f"{_object_label(child)}@{geometry.x()},{geometry.y()} "
            f"{geometry.width()}x{geometry.height()}:{'sichtbar' if child.isVisible() else 'verborgen'}"
        )
    if len(children) > limit:
        labels.append(f"…+{len(children) - limit}")
    return ", ".join(labels) if labels else "<keine>"


def widget_window_summary(widget: QWidget, action: str, event: QEvent | None = None) -> str:
    """Describe one OHC-owned top-level QWidget without creating a surface."""
    geometry = widget.geometry()
    title = re.sub(
        r"\s+", " ", redact_private_text(widget.windowTitle().strip() or "<ohne Titel>"),
    )
    object_name = re.sub(r"\s+", " ", widget.objectName().strip()) or "<ohne Objektname>"
    parent = widget.parentWidget()
    parent_name = parent.__class__.__name__ if parent is not None else "kein QWidget-Elternfenster"
    spontaneous = bool(event is not None and event.spontaneous())
    layout = widget.layout()
    layout_name = layout.__class__.__name__ if layout is not None else "kein Layout"
    size_hint = widget.sizeHint()
    try:
        flags = f"0x{int(widget.windowFlags()):x}"
    except (TypeError, ValueError):
        flags = _enum_name(widget.windowFlags())
    direct_children = sum(isinstance(child, QWidget) for child in widget.children())
    return (
        f"FENSTER {action} · Klasse={widget.__class__.__name__} · Titel={title} · "
        f"Objekt={object_name} · Objekt-ID=0x{id(widget):x} · Typ={_enum_name(widget.windowType())} · "
        f"Flags={flags} · "
        f"Geometrie={geometry.x()},{geometry.y()} {geometry.width()}x{geometry.height()} · "
        f"Größenhinweis={size_hint.width()}x{size_hint.height()} · Layout={layout_name} · "
        f"direkte QWidget-Kinder={direct_children} · "
        f"modal={'ja' if widget.isModal() else 'nein'} · sichtbar={'ja' if widget.isVisible() else 'nein'} · "
        f"aktiv={'ja' if widget.isActiveWindow() else 'nein'} · Fokus={'ja' if widget.hasFocus() else 'nein'} · "
        f"WA_DontShowOnScreen={'ja' if widget.testAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen) else 'nein'} · "
        f"WA_NativeWindow={'ja' if widget.testAttribute(Qt.WidgetAttribute.WA_NativeWindow) else 'nein'} · "
        f"spontan={'ja' if spontaneous else 'nein'} · Eltern={parent_name} · "
        f"QObject-Elternkette={_object_parent_chain(widget)}"
    )


def native_window_summary(window: QWindow, action: str) -> str:
    geometry = window.geometry()
    title = re.sub(
        r"\s+", " ", redact_private_text(window.title().strip() or "<ohne Titel>"),
    )


def is_expected_qt_auxiliary_widget(widget: QWidget) -> bool:
    """Return whether Qt created a routine tooltip or combo-box popup."""
    if widget.windowType() == Qt.WindowType.ToolTip:
        return True
    return bool(
        widget.__class__ is QFrame
        and widget.windowType() == Qt.WindowType.Popup
        and isinstance(widget.parentWidget(), QComboBox)
    )


def is_expected_qt_auxiliary_window(window: QWindow) -> bool:
    """Filter native tooltip surfaces that mirror an ignored QWidget."""
    return window.type() == Qt.WindowType.ToolTip
    return (
        f"NATIVES FENSTER {action} · Klasse={window.__class__.__name__} · Titel={title} · "
        f"Typ={_enum_name(window.type())} · Geometrie={geometry.x()},{geometry.y()} "
        f"{geometry.width()}x{geometry.height()} · sichtbar={'ja' if window.isVisible() else 'nein'}"
    )


class WindowProcessDiagnostics(QObject):
    """Global event filter plus Python/QProcess launch tracing."""

    ui_message = Signal(str)

    def __init__(
        self,
        app: QApplication,
        *,
        persistent_sink: Callable[[str], object] = append_startup_event,
    ) -> None:
        super().__init__(app)
        self._app = app
        self._persistent_sink = persistent_sink
        self._ui_sink: Callable[[str], None] | None = None
        self._recent_processes: dict[str, tuple[float, int]] = {}
        self._started_at = time.monotonic()
        self._window_first_seen: dict[int, float] = {}
        self._last_process_context = "noch kein Helferprozess"
        self._last_process_at = 0.0
        self.ui_message.connect(self._write_ui_message)
        app.installEventFilter(self)
        self._record(
            "FENSTERDIAGNOSE AKTIV · Qt-Top-Level-Fenster, native Oberflächen und Helferprozesse werden protokolliert"
        )

    def set_ui_sink(self, sink: Callable[[str], None]) -> None:
        self._ui_sink = sink
        self.scan_existing_processes()
        self.snapshot_top_level_windows("NACH UI-AUFBAU")

    def detach_ui_sink(self) -> None:
        """Stop writing into Qt widgets that may already be destroyed on quit."""

        self._ui_sink = None
        try:
            self.ui_message.disconnect(self._write_ui_message)
        except (TypeError, RuntimeError):
            pass

    def _write_ui_message(self, message: str) -> None:
        sink = self._ui_sink
        if sink is None:
            return
        try:
            sink("FENSTERDIAGNOSE: " + message)
        except RuntimeError:
            self._ui_sink = None

    def _record(self, message: str) -> None:
        safe = redact_private_text(message)
        try:
            self._persistent_sink("FENSTERDIAGNOSE: " + safe)
        except Exception:  # noqa: BLE001 - diagnostics must never break startup
            pass
        try:
            self.ui_message.emit(safe)
        except RuntimeError:
            pass

    def _record_process(self, message: str) -> None:
        now = time.monotonic()
        self._last_process_context = message.split(" · Anzahl=", 1)[0]
        self._last_process_at = now
        signature = message
        previous_at, repeats = self._recent_processes.get(signature, (0.0, 0))
        if now - previous_at < 10.0:
            self._recent_processes[signature] = (previous_at, repeats + 1)
            return
        if repeats:
            self._record(f"{message} · zuvor {repeats} schnelle Wiederholung(en) zusammengefasst")
        else:
            self._record(message)
        self._recent_processes[signature] = (now, 0)

    def record_python_process(
        self,
        program: object,
        arguments: Sequence[object],
        environment: Mapping[str, object] | None,
    ) -> None:
        self._record_process(process_start_summary(
            program, arguments, environment, source="Python subprocess",
        ))

    def register_qprocess(self, process: QProcess) -> None:
        if bool(process.property("ohcWindowDiagnosticsRegistered")):
            return
        process.setProperty("ohcWindowDiagnosticsRegistered", True)

        def state_changed(state: QProcess.ProcessState, item: QProcess = process) -> None:
            if state != QProcess.ProcessState.Starting:
                return
            environment = item.processEnvironment()
            env_map: dict[str, str] | None = None
            if not environment.isEmpty():
                env_map = {key: environment.value(key) for key in environment.keys()}
            arguments = [item.program(), *item.arguments()]
            self._record_process(process_start_summary(
                item.program(), arguments, env_map, source="Qt QProcess",
            ))

        process.stateChanged.connect(state_changed)

    def scan_existing_processes(self) -> None:
        for process in self._app.findChildren(QProcess):
            self.register_qprocess(process)

    def snapshot_top_level_windows(self, action: str) -> None:
        for widget in self._app.topLevelWidgets():
            self._record_window(widget, action)

    def _timing_context(self, widget: QWidget) -> str:
        now = time.monotonic()
        first_seen = self._window_first_seen.setdefault(id(widget), now)
        if self._last_process_at:
            process_age = f"{max(0.0, now - self._last_process_at):.3f}s zuvor"
        else:
            process_age = "nicht vorhanden"
        return (
            f"Laufzeit={max(0.0, now - self._started_at):.3f}s · "
            f"Fensteralter={max(0.0, now - first_seen):.3f}s · "
            f"letzter Prozess (nur zeitlich)={self._last_process_context} · Abstand={process_age}"
        )

    @staticmethod
    def _is_suspicious_empty_startup_frame(widget: QWidget) -> bool:
        """Match only the observed unintended OHC-owned 640x480 top-level frame."""
        return (
            widget.__class__ is QFrame
            and widget.parentWidget() is None
            and widget.windowType() == Qt.WindowType.Window
            and not widget.windowTitle().strip()
            and not widget.objectName().strip()
            and not widget.isModal()
            and widget.width() == 640
            and widget.height() == 480
            and not bool(widget.property("ohcAllowTopLevelFrame"))
        )

    def _quarantine_suspicious_frame(self, widget: QWidget) -> None:
        if bool(widget.property("ohcEmptyStartupFrameBlocked")):
            return
        widget.setProperty("ohcEmptyStartupFrameBlocked", True)
        detail = (
            "VERDÄCHTIGES LEERFENSTER BLOCKIERT · genaues Muster="
            "QFrame/Window/elternlos/titellos/640x480 · "
            f"Kinder={_direct_widget_children(widget)} · {_object_parent_chain(widget)} · "
            f"{self._timing_context(widget)}"
        )
        self._record(detail)
        # WinIdChange arrives before Show for the reported frame. Marking it here prevents
        # the platform surface from being painted; hiding is deferred to avoid event recursion.
        widget.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)

        def hide_if_alive(item: QWidget = widget) -> None:
            try:
                item.hide()
            except RuntimeError:
                pass

        QTimer.singleShot(0, hide_if_alive)

    def _record_window(self, widget: QWidget, action: str, event: QEvent | None = None) -> None:
        self._record(
            f"{widget_window_summary(widget, action, event)} · {self._timing_context(widget)}"
        )
        if action in {"NATIVE-ID GEÄNDERT", "GEÖFFNET"} and self._is_suspicious_empty_startup_frame(widget):
            self._quarantine_suspicious_frame(widget)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        event_type = event.type()
        if isinstance(watched, QWidget) and watched.isWindow():
            if is_expected_qt_auxiliary_widget(watched):
                return False
            actions = {
                QEvent.Type.Show: "GEÖFFNET",
                QEvent.Type.Hide: "AUSGEBLENDET",
                QEvent.Type.Close: "GESCHLOSSEN",
                QEvent.Type.WinIdChange: "NATIVE-ID GEÄNDERT",
            }
            action = actions.get(event_type)
            if action is not None:
                self._record_window(watched, action, event)
        elif (
            isinstance(watched, QWindow)
            and event_type == QEvent.Type.PlatformSurface
            and not is_expected_qt_auxiliary_window(watched)
        ):
            surface_type = getattr(event, "surfaceEventType", lambda: "geändert")()
            self._record(native_window_summary(watched, _enum_name(surface_type)))
        elif event_type == QEvent.Type.ChildAdded and isinstance(event, QChildEvent):
            child = event.child()
            if isinstance(child, QProcess):
                self.register_qprocess(child)
        return False


def track_qprocess(process: QProcess) -> QProcess:
    """Register an OHC-owned QProcess before it can enter Starting state."""
    if _ACTIVE_DIAGNOSTICS is not None:
        _ACTIVE_DIAGNOSTICS.register_qprocess(process)
    return process


def _python_audit_hook(event: str, args: tuple[Any, ...]) -> None:
    if event != "subprocess.Popen" or _ACTIVE_DIAGNOSTICS is None:
        return
    try:
        executable, arguments, _cwd, environment = args
        _ACTIVE_DIAGNOSTICS.record_python_process(
            executable,
            list(arguments) if isinstance(arguments, (list, tuple)) else [arguments],
            environment if isinstance(environment, Mapping) else None,
        )
    except Exception:  # noqa: BLE001 - an audit hook may never block a process
        return


def install_window_process_diagnostics(app: QApplication) -> WindowProcessDiagnostics:
    """Install the temporary global diagnostics as early as possible."""
    global _ACTIVE_DIAGNOSTICS, _AUDIT_HOOK_INSTALLED
    diagnostics = WindowProcessDiagnostics(app)
    _ACTIVE_DIAGNOSTICS = diagnostics
    if not _AUDIT_HOOK_INSTALLED:
        sys.addaudithook(_python_audit_hook)
        _AUDIT_HOOK_INSTALLED = True
    return diagnostics
