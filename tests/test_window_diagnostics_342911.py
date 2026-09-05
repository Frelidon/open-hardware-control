from __future__ import annotations

import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QProcess, QProcessEnvironment, Qt
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QFrame, QLabel, QPushButton, QVBoxLayout

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from window_diagnostics import (  # noqa: E402
    WindowProcessDiagnostics,
    is_expected_qt_auxiliary_widget,
    process_start_summary,
    widget_window_summary,
)


def test_process_summary_identifies_helper_without_recording_secret_values() -> None:
    summary = process_start_summary(
        "/usr/bin/openrgb",
        ["/usr/bin/openrgb", "--token", "do-not-log-me", "--client", "--list-devices"],
        {"QT_QPA_PLATFORM": "offscreen"},
        source="Test",
    )
    assert "Programm=openrgb" in summary
    assert "--client" in summary
    assert "--list-devices" in summary
    assert "do-not-log-me" not in summary
    assert "QT_QPA_PLATFORM=offscreen" in summary


def test_widget_summary_contains_window_identity_and_redacts_home() -> None:
    app = QApplication.instance() or QApplication(["window-diagnostics-test"])
    dialog = QDialog()
    dialog.setObjectName("diagnosticDialog")
    dialog.setWindowTitle(str(Path.home() / "private-title"))
    dialog.resize(420, 180)
    summary = widget_window_summary(dialog, "GEÖFFNET")
    assert "Klasse=QDialog" in summary
    assert "Objekt=diagnosticDialog" in summary
    assert "Objekt-ID=0x" in summary
    assert "420x180" in summary
    assert "QObject-Elternkette=" in summary
    assert str(Path.home()) not in summary
    dialog.deleteLater()
    app.processEvents()


def test_global_filter_records_open_and_close_in_persistent_and_visible_logs() -> None:
    app = QApplication.instance() or QApplication(["window-diagnostics-test"])
    persistent: list[str] = []
    visible: list[str] = []
    diagnostics = WindowProcessDiagnostics(app, persistent_sink=persistent.append)
    diagnostics.set_ui_sink(visible.append)
    dialog = QDialog()
    dialog.setWindowTitle("Leeres Testfenster")
    dialog.show()
    app.processEvents()
    dialog.close()
    app.processEvents()

    assert any("FENSTER GEÖFFNET" in line and "Leeres Testfenster" in line for line in persistent)
    assert any("FENSTER GESCHLOSSEN" in line for line in persistent)
    assert any("FENSTERDIAGNOSE: FENSTER GEÖFFNET" in line for line in visible)
    app.removeEventFilter(diagnostics)
    dialog.deleteLater()
    diagnostics.deleteLater()
    app.processEvents()


def test_exact_blank_startup_qframe_is_diagnosed_and_blocked() -> None:
    app = QApplication.instance() or QApplication(["window-diagnostics-test"])
    persistent: list[str] = []
    diagnostics = WindowProcessDiagnostics(app, persistent_sink=persistent.append)
    frame = QFrame()
    layout = QVBoxLayout(frame)
    layout.addWidget(QLabel("interner Inhalt", frame))
    frame.resize(640, 480)
    frame.show()
    app.processEvents()

    assert frame.testAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
    assert not frame.isVisible()
    blocked = [line for line in persistent if "VERDÄCHTIGES LEERFENSTER BLOCKIERT" in line]
    assert len(blocked) == 1
    assert "QFrame/Window/elternlos/titellos/640x480" in blocked[0]
    assert "QLabel" in blocked[0]
    assert "letzter Prozess (nur zeitlich)=" in blocked[0]

    app.removeEventFilter(diagnostics)
    frame.deleteLater()
    diagnostics.deleteLater()
    app.processEvents()


def test_named_or_differently_sized_qframes_are_not_blocked() -> None:
    app = QApplication.instance() or QApplication(["window-diagnostics-test"])
    persistent: list[str] = []
    diagnostics = WindowProcessDiagnostics(app, persistent_sink=persistent.append)
    named = QFrame()
    named.setWindowTitle("Erlaubtes Werkzeug")
    named.resize(640, 480)
    sized = QFrame()
    sized.resize(641, 480)
    named.show()
    sized.show()
    app.processEvents()

    assert not named.testAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
    assert not sized.testAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
    assert not any("VERDÄCHTIGES LEERFENSTER BLOCKIERT" in line for line in persistent)

    named.close()
    sized.close()
    app.removeEventFilter(diagnostics)
    named.deleteLater()
    sized.deleteLater()
    diagnostics.deleteLater()
    app.processEvents()


def test_routine_tooltips_and_combo_popups_are_not_logged() -> None:
    app = QApplication.instance() or QApplication(["window-diagnostics-test"])
    persistent: list[str] = []
    diagnostics = WindowProcessDiagnostics(app, persistent_sink=persistent.append)
    button = QPushButton("Leise")
    tooltip = QLabel("Leises Profil", button, Qt.WindowType.ToolTip)
    combo = QComboBox()
    combo_popup = QFrame(combo, Qt.WindowType.Popup)
    unrelated_popup = QFrame(button, Qt.WindowType.Popup)

    assert is_expected_qt_auxiliary_widget(tooltip)
    assert is_expected_qt_auxiliary_widget(combo_popup)
    assert not is_expected_qt_auxiliary_widget(unrelated_popup)

    tooltip.show()
    combo_popup.show()
    unrelated_popup.show()
    app.processEvents()

    assert not any("Leises Profil" in line for line in persistent)
    assert not any("Eltern=QComboBox" in line for line in persistent)
    assert any("Typ=Popup" in line and "Eltern=QPushButton" in line for line in persistent)

    tooltip.close()
    combo_popup.close()
    unrelated_popup.close()
    app.removeEventFilter(diagnostics)
    tooltip.deleteLater()
    combo_popup.deleteLater()
    unrelated_popup.deleteLater()
    button.deleteLater()
    combo.deleteLater()
    diagnostics.deleteLater()
    app.processEvents()


def test_global_filter_records_qprocess_program_and_headless_platform() -> None:
    app = QApplication.instance() or QApplication(["window-diagnostics-test"])
    persistent: list[str] = []
    diagnostics = WindowProcessDiagnostics(app, persistent_sink=persistent.append)
    process = QProcess(app)
    diagnostics.register_qprocess(process)
    environment = QProcessEnvironment.systemEnvironment()
    environment.insert("QT_QPA_PLATFORM", "offscreen")
    process.setProcessEnvironment(environment)
    process.start("/usr/bin/true", [])
    assert process.waitForFinished(3000)
    app.processEvents()

    assert any(
        "Quelle=Qt QProcess" in line
        and "Programm=true" in line
        and "QT_QPA_PLATFORM=offscreen" in line
        for line in persistent
    )
    app.removeEventFilter(diagnostics)
    process.deleteLater()
    diagnostics.deleteLater()
    app.processEvents()


def test_ui_sink_is_detached_when_the_log_widget_is_already_deleted() -> None:
    app = QApplication.instance() or QApplication(["window-diagnostics-test"])
    persistent: list[str] = []
    visible: list[str] = []
    diagnostics = WindowProcessDiagnostics(app, persistent_sink=persistent.append)

    def sink(message: str) -> None:
        visible.append(message)
        raise RuntimeError("Internal C++ object (PySide6.QtWidgets.QPlainTextEdit) already deleted.")

    diagnostics.set_ui_sink(sink)
    diagnostics._record("gelöschtes Log-Widget darf keinen Absturz auslösen")
    app.processEvents()
    assert diagnostics._ui_sink is None
    diagnostics.detach_ui_sink()
    diagnostics._record("nach dem Beenden darf das Log-Widget nicht mehr beschrieben werden")
    app.processEvents()
    assert any("gelöschtes Log-Widget" in line for line in persistent)
    assert any("nach dem Beenden" in line for line in persistent)
    assert not any("nach dem Beenden" in line for line in visible)
    app.removeEventFilter(diagnostics)
    diagnostics.deleteLater()
    app.processEvents()
