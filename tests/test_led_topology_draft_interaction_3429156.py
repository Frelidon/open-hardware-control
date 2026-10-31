"""Real user input keeps fresh LED drafts editable, private and validated."""
import copy

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QScrollArea, QSpinBox, QTabWidget, QVBoxLayout, QWidget

from test_slot_argb_routes_342985 import APP, Host, HUB
from modules.pc_case_profiles.v1_5.editor_sections import EditorSections
from modules.pc_case_profiles.v1_5.inline_editor import CaseInspector
from modules.rgb_studio.v1_15.led_topology_editor import LedTopologyEditor
from modules.rgb_studio.v1_15.led_topology_store import paths


def settle():
    for _ in range(4):
        APP.processEvents()


def pick(combo, value, *, keyboard=False):
    assert combo.isEnabled() and combo.isVisible(), combo.objectName()
    wanted = combo.findData(value)
    assert wanted >= 0
    if keyboard:
        combo.setFocus()
        QTest.keyClick(combo, Qt.Key.Key_Home)
        for _ in range(wanted):
            QTest.keyClick(combo, Qt.Key.Key_Down)
    else:
        QTest.mouseClick(combo, Qt.MouseButton.LeftButton,
                         pos=QPoint(combo.width() - 12, combo.height() // 2))
        settle()
        view = combo.view()
        assert view.isVisible(), combo.objectName()
        item = combo.model().index(wanted, 0)
        view.scrollTo(item)
        settle()
        # A native popup ignores the opening gesture's immediate release.
        # Move to the intended row and deliver a distinct user click.
        QTest.mouseMove(view.viewport(), view.visualRect(item).center())
        QTest.mouseClick(view.viewport(), Qt.MouseButton.LeftButton,
                         pos=view.visualRect(item).center(), delay=30)
    settle()
    assert combo.currentData() == value, combo.objectName()


def build(language, inline, distro="ubuntu"):
    host = Host(language=language)
    host.ubuntu_runtime = distro == "ubuntu"
    host.resize(1800, 1150)
    host.tabs = QTabWidget(host)
    host_layout = QVBoxLayout(host); host_layout.addWidget(host.tabs)
    page = QWidget(); row = QHBoxLayout(page)
    case_scroll = QScrollArea(); case_scroll.setWidgetResizable(True)
    case_scroll.setWidget(page)
    host.tabs.addTab(case_scroll, "Synthetic case")
    profile, diagram = QWidget(), QWidget()
    row.addWidget(profile); row.addWidget(diagram)
    dialog = QDialog(host)
    dialog.setWindowTitle(host.tr_static("LED-Verlauf"))
    form = QVBoxLayout(dialog)
    count, index = QSpinBox(), QSpinBox()
    count.setRange(1, 512); count.setValue(24)
    index.setRange(1, 24); index.setValue(1)
    form.addWidget(count); form.addWidget(index)
    editor = LedTopologyEditor(host, HUB, "Channel A1", count, index, 3)
    form.addWidget(editor)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    form.addWidget(buttons)
    def save():
        if editor.commit(): dialog.accept()
    buttons.accepted.connect(save)
    buttons.rejected.connect(dialog.reject)
    inspector = None
    host.show()
    if inline:
        inspector = CaseInspector(host, profile, diagram)
        row.addWidget(inspector)
        inspector.present(dialog)
    else:
        dialog.resize(700, 700)
        dialog.show()
    settle()
    return host, dialog, editor, inspector


def cleanup(host, dialog, inspector):
    if inspector is not None:
        inspector.shutdown()
    else:
        dialog.reject()
    host.hide()
    host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    settle()


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
@pytest.mark.parametrize("inline", [False, True])
@pytest.mark.parametrize("distro", ["ubuntu", "fedora"])
def test_mouse_popups_and_keyboard_select_fresh_draft_without_closing_or_writing(language, inline, distro):
    host, dialog, editor, inspector = build(language, inline, distro)
    saved = copy.deepcopy(host.settings.data)
    try:
        assert not editor.group.isChecked() and paths(host) == {}
        assert editor.kind.isEnabled() and editor.start.isEnabled()
        pick(editor.kind, "ring")
        assert editor.group.isChecked()
        assert not editor.end.isEnabled() and editor.clockwise.isEnabled()
        pick(editor.start, "top-left")
        pick(editor.clockwise, False)
        pick(editor.unit_order, True, keyboard=True)
        pick(editor.movement, "top-bottom", keyboard=True)
        QTest.mouseClick(editor.reverse_effect, Qt.MouseButton.LeftButton)
        settle()
        assert editor.reverse_effect.isChecked()
        assert dialog.isVisible() and host.settings.data == saved and host.calls == []
        if inspector is not None:
            assert inspector.active_dialog is dialog
            sections = editor.findChild(EditorSections)
            host.resize(1000, 900); settle()
            assert not sections.wide
            sections.tabs.setCurrentIndex(0); settle()
            assert editor.start.currentData() == "top-left"
            assert editor.clockwise.currentData() is False
        pick(editor.kind, "line", keyboard=True)
        assert editor.end.isEnabled() and not editor.clockwise.isEnabled()
        pick(editor.end, "bottom-right")
        assert dialog.isVisible() and host.settings.data == saved and host.calls == []
        buttons = dialog.findChild(QDialogButtonBox)
        QTest.mouseClick(buttons.button(QDialogButtonBox.StandardButton.Save), Qt.MouseButton.LeftButton)
        settle()
        value = paths(host)["openrgb:hub"]["Channel A1"]
        assert value["kind"] == "line" and value["start"] == "top-left" and value["end"] == "bottom-right"
        assert value["direction"] == "top-bottom" and value["reverse_effect"] is True
        assert host.calls == []
    finally:
        cleanup(host, dialog, inspector)


def test_uncheck_remains_explicit_remove_and_cancelled_draft_never_persists():
    host, dialog, editor, inspector = build("de", True)
    try:
        pick(editor.start, "top-left", keyboard=True)
        assert editor.group.isChecked() and paths(host) == {}
        editor.group.setChecked(False); settle()
        assert editor.start.isEnabled() and editor.kind.isEnabled()
        assert editor.commit() and paths(host) == {}
        saved = copy.deepcopy(host.settings.data)
        pick(editor.kind, "ring")
        pick(editor.clockwise, False)
        QTest.mouseClick(dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.StandardButton.Cancel),
                         Qt.MouseButton.LeftButton)
        settle()
        assert host.settings.data == saved and paths(host) == {} and host.calls == []
    finally:
        cleanup(host, dialog, inspector)


@pytest.mark.parametrize("inline", [False, True])
def test_open_count_only_and_programmatic_restore_do_not_enable_new_path(inline):
    host, dialog, editor, inspector = build("de", inline)
    try:
        editor.count.setValue(30)
        editor.index.setValue(8)
        editor.start.setCurrentIndex(editor.start.findData("top-left"))
        editor.movement.setCurrentIndex(editor.movement.findData("top-bottom"))
        settle()
        assert not editor.group.isChecked() and paths(host) == {} and host.calls == []
        assert editor.commit() and paths(host) == {} and host.calls == []
        host.setEnabled(False)
        editor.update_preview(); settle()
        assert not editor.kind.isEnabled() and not editor.start.isEnabled()
        host.setEnabled(True); settle()
        assert editor.kind.isEnabled() and editor.start.isEnabled()
    finally:
        cleanup(host, dialog, inspector)


def test_invalid_ring_and_identical_line_endpoints_keep_existing_saved_path():
    host, dialog, editor, inspector = build("de", False)
    try:
        pick(editor.start, "top", keyboard=True)
        assert editor.commit()
        saved = copy.deepcopy(host.settings.data)
        pick(editor.kind, "ring")
        editor.count.setValue(25)
        assert not editor.commit() and host.settings.data == saved
        editor.count.setValue(24)
        pick(editor.kind, "line", keyboard=True)
        pick(editor.end, "top", keyboard=True)
        assert not editor.commit() and host.settings.data == saved and host.calls == []
    finally:
        cleanup(host, dialog, inspector)
