"""Real Qt coverage for gradual, cancellable section reveal and collapse return."""
from __future__ import annotations

import os
from pathlib import Path
import sys
from types import SimpleNamespace

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import pytest
from PySide6.QtCore import QAbstractAnimation, QCoreApplication, QEvent, QPoint, QPointF, QSettings, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QLayout, QLineEdit, QScrollArea, QVBoxLayout, QWidget
from modules.ui_sections.v1_0.cards import SectionCard


@pytest.fixture
def section_page(tmp_path):
    app = QApplication.instance() or QApplication([])
    host = QWidget()
    host.settings = QSettings(str(tmp_path / 'isolated-sections.ini'), QSettings.Format.IniFormat)
    host.settings.setValue('performance/transitions_enabled', True)
    outer = QVBoxLayout(host); outer.setContentsMargins(0, 0, 0, 0)
    scroll = QScrollArea(); scroll.setWidgetResizable(True); outer.addWidget(scroll)
    content = QWidget(); layout = QVBoxLayout(content)
    layout.setContentsMargins(12, 12, 12, 12); layout.setSpacing(12)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
    before = QWidget(); before.setFixedHeight(420); layout.addWidget(before)
    body = QWidget(); body_layout = QVBoxLayout(body)
    body_layout.setContentsMargins(0, 0, 0, 0)
    entry = QLineEdit(); entry.setMinimumHeight(36); body_layout.addWidget(entry)
    labels = []
    for _index in range(3):
        label = QLabel('Saved settings remain readable when this section opens and the viewport moves.')
        label.setWordWrap(True); label.setMinimumHeight(44); body_layout.addWidget(label); labels.append(label)
    section = SectionCard('Section', 'Saved content is revealed in the existing viewport.', None, body)
    layout.addWidget(section)
    after = QWidget(); after.setFixedHeight(900); layout.addWidget(after)
    scroll.setWidget(content); host.resize(760, 520); host.show()
    app.processEvents(); QTest.qWait(30)
    scroll.verticalScrollBar().setValue(190); app.processEvents()
    fixture = SimpleNamespace(app=app, host=host, scroll=scroll, section=section,
                              entry=entry, labels=labels, origin=scroll.verticalScrollBar().value())
    yield fixture
    host.close(); host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete); app.processEvents()


def settle(milliseconds=500):
    QTest.qWait(milliseconds)
    QApplication.processEvents()


def open_section(page):
    page.section.button.setChecked(True)
    settle(35)
    return page.scroll._ohc_section_reveal


def assert_revealed(page):
    viewport = page.scroll.viewport()
    top = page.section.mapTo(viewport, QPoint()).y()
    if page.section.height() + 32 > viewport.height():
        assert 0 <= top <= 20
    else:
        assert top >= 0
        assert top + page.section.height() <= viewport.height() - 10


def test_expand_is_gradual_then_close_returns_before_hiding_body(section_page):
    page = section_page; bar = page.scroll.verticalScrollBar()
    controller = open_section(page)
    assert controller.animation.state() == QAbstractAnimation.State.Running
    target = controller.animation.endValue()
    assert target > page.origin
    settle(105)
    assert page.origin < bar.value() < target
    assert page.section.body.isVisible()
    settle(380)
    assert_revealed(page)
    assert bar.value() == target
    for label in page.labels:
        bounds = label.rect().translated(label.mapTo(page.section.body, QPoint()))
        assert page.section.body.rect().contains(bounds)
        assert label.height() >= max(label.minimumHeight(), label.heightForWidth(label.width()))
    page.section.button.setChecked(False)
    settle(90)
    assert page.section.body.isVisible(), 'collapse must return before hiding its body'
    assert page.origin < bar.value() < target
    settle(390)
    assert page.section.body.isHidden()
    assert abs(bar.value() - page.origin) <= 1


@pytest.mark.parametrize('interaction', ['wheel', 'scrollbar', 'page_hide'])
@pytest.mark.parametrize('phase', ['opening', 'returning'])
def test_manual_or_hidden_page_cancels_return_without_fighting_user(section_page, interaction, phase):
    page = section_page; bar = page.scroll.verticalScrollBar(); controller = open_section(page)
    settle(75)
    if phase == 'returning':
        settle()
        page.section.button.setChecked(False); settle(75)
        assert page.section.body.isVisible()
    if interaction == 'wheel':
        viewport = page.scroll.viewport()
        event = QWheelEvent(QPointF(20, 20), QPointF(viewport.mapToGlobal(QPoint(20, 20))),
                            QPoint(), QPoint(0, -120), Qt.MouseButton.NoButton,
                            Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False)
        QCoreApplication.sendEvent(viewport, event)
    elif interaction == 'scrollbar':
        QTest.mousePress(bar, Qt.MouseButton.LeftButton, pos=QPoint(max(1, bar.width() // 2), bar.height() // 2))
        QTest.mouseRelease(bar, Qt.MouseButton.LeftButton, pos=QPoint(max(1, bar.width() // 2), bar.height() // 2))
    else:
        page.host.hide(); settle(25); page.host.show()
    assert controller.animation.state() == QAbstractAnimation.State.Stopped
    assert controller.owner is None
    bar.setValue(280); manual = bar.value()
    page.section.button.setChecked(False)
    assert page.section.body.isHidden()
    settle()
    assert bar.value() == manual, (interaction, bar.value(), manual)


def test_rapid_toggle_and_deleted_pending_section_leave_no_animation_callback_error(section_page, monkeypatch):
    page = section_page; failures = []
    monkeypatch.setattr(sys, 'excepthook', lambda *exception: failures.append(exception))
    open_section(page); settle(45)
    page.section.button.setChecked(False); settle(45)
    page.section.button.setChecked(True); settle(45)
    page.section.button.setChecked(False); settle()
    assert page.section.body.isHidden()
    assert page.scroll._ohc_section_reveal.animation.state() == QAbstractAnimation.State.Stopped
    # A queued reveal must tolerate an already deleted card.
    page.section.button.setChecked(True)
    page.section.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    settle()
    assert failures == []


def test_animation_disabled_is_immediate_and_cancels_existing_motion(section_page):
    page = section_page; bar = page.scroll.verticalScrollBar()
    controller = open_section(page); settle(80)
    assert controller.animation.state() == QAbstractAnimation.State.Running
    page.host.settings.setValue('performance/transitions_enabled', False)
    page.section.button.setChecked(False)
    assert page.section.body.isHidden()
    position = bar.value()
    settle()
    assert controller.animation.state() == QAbstractAnimation.State.Stopped
    assert bar.value() == position, 'disabled transitions must not continue an old viewport movement'
    page.section.button.setChecked(True)
    assert page.section.body.isVisible()
    page.section.button.setChecked(False)
    assert page.section.body.isHidden()


def test_profile_edit_focus_keeps_pre_expansion_return_origin(section_page):
    from modules.profiles_workspace.v1_1.page import ProfileWorkspace
    page = section_page
    proxy = SimpleNamespace(editor=page.section, host=SimpleNamespace(profile_name_input=page.entry), scroll=page.scroll)
    ProfileWorkspace.open_editor(proxy, True)
    settle()
    assert_revealed(page)
    controller = page.scroll._ohc_section_reveal
    assert controller.origin == page.origin, (controller.origin, page.origin)
    page.section.button.setChecked(False); settle()
    assert abs(page.scroll.verticalScrollBar().value() - page.origin) <= 1


def test_deleting_card_during_return_does_not_call_invalid_qt_objects(section_page, monkeypatch):
    page = section_page; failures = []
    monkeypatch.setattr(sys, 'excepthook', lambda *exception: failures.append(exception))
    controller = open_section(page); settle()
    page.section.button.setChecked(False); settle(80)
    assert controller.animation.state() == QAbstractAnimation.State.Running
    page.section.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    settle()
    assert controller.animation.state() == QAbstractAnimation.State.Stopped
    assert failures == []
