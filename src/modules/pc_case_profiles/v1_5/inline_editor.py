# SPDX-License-Identifier: GPL-3.0-or-later
"""One owned, dismissible in-page inspector; domain dialogs keep their guards."""
from PySide6.QtCore import QEvent, QPoint, QTimer, Qt
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)


class CaseInspector(QFrame):
    def __init__(self, host, profile_panel, diagram):
        super().__init__()
        self.host, self.profile_panel, self.diagram = host, profile_panel, diagram
        self.active_dialog = None
        self.generation = 0
        self.original_minimum = diagram.minimumWidth()
        self.setObjectName("caseInlineInspector")
        self.setMinimumWidth(430)
        self.setMaximumWidth(860)
        self.setMinimumHeight(480)
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        self.title = QLabel()
        self.title.setWordWrap(True)
        row.addWidget(self.title, 1)
        close = QPushButton("×")
        close.setFixedSize(38, 38)
        close.setToolTip(host.tr_static("Abbrechen"))
        from modules.ui_performance.v1_1.dynamic_text import remember
        remember(host, close, tooltip="Abbrechen")
        close.clicked.connect(self.dismiss)
        row.addWidget(close)
        layout.addLayout(row)
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.body, 1)
        QApplication.instance().installEventFilter(self)
        self.hide()

    def reserve(self, title):
        self.dismiss()
        self.generation += 1
        self.title.setText(title)
        from modules.ui_performance.v1_1.dynamic_text import canonical, remember
        remember(self.host, self.title, text=canonical(self.host, title))
        if hasattr(self.host, "case_page_index"):
            self.host.tabs.setCurrentIndex(self.host.case_page_index)
        if hasattr(self.host, "case_sections"):
            self.host.case_sections.setCurrentIndex(0)
        self.profile_panel.hide()
        self.diagram.setMinimumWidth(360)
        self.show()
        self._adapt_width()
        return self.generation

    def is_current(self, token):
        return self.generation == token and self.isVisible() and not any(
            getattr(self.host, key, False) for key in
            ("explicit_quit_requested", "session_shutdown_requested", "exit_cleanup_in_progress"))

    def present(self, dialog, token=None):
        if token is None: token = self.reserve(dialog.windowTitle())
        if not self.is_current(token):
            dialog.reject()
            dialog.deleteLater()
            return
        self.title.setText(dialog.windowTitle())
        from modules.ui_performance.v1_1.dynamic_text import canonical, capture_form, remember
        remember(self.host, self.title, text=canonical(self.host, dialog.windowTitle()))
        from .editor_sections import adapt_topology
        from modules.rgb_studio.v1_15.led_topology_editor import LedTopologyEditor
        for editor in dialog.findChildren(LedTopologyEditor):
            adapt_topology(self.host, editor)
        capture_form(self.host, dialog)
        self.active_dialog = dialog
        dialog.setParent(self.body, Qt.WindowType.Widget)
        dialog.setWindowModality(Qt.WindowModality.NonModal)
        dialog.setMinimumSize(0, 0)
        if dialog.layout() is not None:
            dialog.layout().setContentsMargins(6, 6, 6, 6)
        self.body_layout.addWidget(dialog)
        dialog.finished.connect(lambda _result: self._finished(dialog, token))
        dialog.show()
        QTimer.singleShot(0, self, self._fit_page)

    def _finished(self, dialog, token):
        if self.active_dialog is dialog:
            self.active_dialog = None
            self.body_layout.removeWidget(dialog)
        dialog.deleteLater()
        if token == self.generation:
            self.generation += 1
            self.hide()
            self.profile_panel.show()
            self.diagram.setMinimumWidth(self.original_minimum)

    def dismiss(self):
        self.generation += 1
        dialog = self.active_dialog
        if dialog is not None:
            self.active_dialog = None
            self.body_layout.removeWidget(dialog)
            dialog.reject()
        self.hide()
        self.profile_panel.show()
        self.diagram.setMinimumWidth(self.original_minimum)

    def _adapt_width(self):
        parent = self.parentWidget()
        if parent is None: return
        available = parent.width()
        page = self.host.tabs.currentWidget()
        if isinstance(page, QScrollArea) and page.widget() is not None:
            # Content minimums include the old inspector width. Measure the
            # viewport instead, or a narrow resize gets locked in that width.
            inset = max(0, parent.mapTo(page.widget(), QPoint(0, 0)).x())
            available = page.viewport().width() - 2 * inset
        wanted = min(860, max(430, min(round(available * .58), available - 374)))
        if self.minimumWidth() != wanted or self.maximumWidth() != wanted:
            self.setFixedWidth(wanted)

    def _fit_page(self):
        page = self.host.tabs.currentWidget()
        if self.active_dialog is not None and self.is_current(self.generation) and isinstance(page, QScrollArea):
            layout = self.active_dialog.layout()
            if layout is not None:
                natural = layout.minimumSize().height() + self.title.height() + 48
                self.setMinimumHeight(max(480, natural))
            from PySide6.QtWidgets import QDialogButtonBox
            footer = self.active_dialog.findChild(QDialogButtonBox)
            page.ensureWidgetVisible(footer if footer is not None else self, 0, 12)

    def eventFilter(self, watched, event):  # noqa: N802
        if self.isHidden(): return False
        page = self.host.tabs.currentWidget()
        viewport = page.viewport() if isinstance(page, QScrollArea) else None
        if watched in (self.parentWidget(), viewport) and event.type() == QEvent.Type.Resize:
            self._adapt_width()
        if watched in (self, viewport) and event.type() == QEvent.Type.Resize:
            QTimer.singleShot(0, self, self._fit_page)
        if (event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape
                and isinstance(watched, QWidget) and watched.window() is self.host.window()):
            self.dismiss()
            return True
        # Keep drafts open until Save, Cancel, Escape or the explicit close
        # button.  Native combo-box popups can briefly route their closing
        # mouse event through the main window; treating that as an outside
        # click used to discard the complete component/LED form.
        if watched is self.host and event.type() in {QEvent.Type.Hide, QEvent.Type.Close}:
            self.dismiss()
        return False

    def shutdown(self):
        self.dismiss()
        QApplication.instance().removeEventFilter(self)


def present_editor(host, dialog, *, token=None):
    inspector = getattr(host, "case_inspector", None)
    if inspector is None: return False
    inspector.present(dialog, token)
    return True
