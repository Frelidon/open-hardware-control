"""Embedded LCD source editing is bounded, explicit and hardware-free."""
from pathlib import Path
import os
import sys
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QProgressBar, QLabel, QWidget
from modules.lcd_media_manager.v1_1 import DesignLibraryPanel, DesignLibraryDialog, DesignLibraryState
from modules.localization.v1_0.lcd_manager_messages import LCD_MANAGER_MESSAGES


def app():
    return QApplication.instance() or QApplication([])


def test_inline_panel_never_scans_snapshot_or_opens_a_manager_window(tmp_path):
    qt = app(); parent = QWidget()
    folder = tmp_path / 'library'; folder.mkdir()
    first = folder / 'one.png'; first.write_bytes(b'original')
    second = folder / 'two.mp4'; second.write_bytes(b'movie')
    outside = tmp_path / 'outside.png'; outside.write_bytes(b'outside')
    state = DesignLibraryState((folder,), (), {}, ())
    with patch.object(DesignLibraryPanel, '_folder_media', side_effect=AssertionError('no rescan on embedded open')):
        panel = DesignLibraryPanel(state, parent=parent, known_media=(first, second, outside))
        panel.show(); qt.processEvents()
        assert panel.parentWidget() is parent
        assert not panel.isWindow()
        root = panel.tree.topLevelItem(0)
        assert root.childCount() == 2
        root.setExpanded(True); root.child(0).setSelected(True)
        panel.rename_selected(); panel.alias_input.setText('A readable alias'); panel.apply_alias()
        assert panel.state().aliases[str(first)] == 'A readable alias'
        assert first.read_bytes() == b'original'
        assert not any(isinstance(window, QDialog) and window.isVisible() for window in qt.topLevelWidgets())
    parent.deleteLater(); qt.processEvents()


def test_save_and_cancel_are_explicit_and_removal_never_changes_files(tmp_path):
    qt = app(); folder = tmp_path / 'library'; folder.mkdir()
    media = folder / 'video.mp4'; media.write_bytes(b'original media')
    state = DesignLibraryState((folder,), (), {}, ())
    panel = DesignLibraryPanel(state, known_media=(media,)); saved = []; canceled = []
    panel.saved.connect(saved.append); panel.canceled.connect(lambda: canceled.append(True))
    assert not panel.save_button.isEnabled()
    root = panel.tree.topLevelItem(0); root.setExpanded(True); root.child(0).setSelected(True)
    assert saved == []
    panel.remove_selected()
    assert panel.state().excluded == (media,)
    assert panel.save_button.isEnabled()
    panel.cancel_button.click()
    assert canceled == [True] and saved == []
    assert state.excluded == () and media.read_bytes() == b'original media'
    panel.set_state(state, known_media=(media,))
    assert not panel.save_button.isEnabled() and panel.state() == state
    panel.tree.topLevelItem(0).setSelected(True); panel.remove_selected(); panel.save_button.click()
    assert len(saved) == 1 and saved[0].folders == ()
    assert folder.is_dir() and media.read_bytes() == b'original media'
    panel.deleteLater(); qt.processEvents()


def test_language_refresh_preserves_alias_draft_and_stable_tree_identity(tmp_path):
    qt = app(); media = tmp_path / 'still.png'; media.write_bytes(b'original')
    language = ['de']
    def translate(source):
        key = next((key for key, value in LCD_MANAGER_MESSAGES['de'].items() if value == source), None)
        return LCD_MANAGER_MESSAGES[language[0]].get(key, source)
    panel = DesignLibraryPanel(DesignLibraryState((), (media,), {}, ()), translate, known_media=(media,))
    item = panel.tree.topLevelItem(0); item.setSelected(True)
    panel.rename_selected(); panel.alias_input.setText('Unsaved alias')
    for code in ('de', 'en', 'es', 'fr'):
        language[0] = code; panel.refresh_language()
        assert panel.alias_input.text() == 'Unsaved alias'
        assert item.data(0, Qt.ItemDataRole.UserRole) == ('Datei', str(media))
        assert panel.add_folder_button.text() == LCD_MANAGER_MESSAGES[code][3401]
        assert panel.state().aliases == {}
    panel.deleteLater(); qt.processEvents()


def test_source_limits_and_known_media_iterator_are_bounded(tmp_path):
    qt = app(); media = tmp_path / 'additional.png'; media.write_bytes(b'original')
    files = tuple(tmp_path / f'{index}.png' for index in range(500))
    state = DesignLibraryState((), files, {}, ())
    seen = []
    def snapshot():
        for index in range(10000):
            seen.append(index); yield tmp_path / f'media-{index}.png'
    panel = DesignLibraryPanel(state, known_media=snapshot())
    assert len(seen) == 2500
    with patch('modules.lcd_media_manager.v1_1.panel.QFileDialog.getOpenFileNames', return_value=([str(media)], '')):
        panel.add_files()
    assert len(panel.state().files) == 500
    assert not panel.add_files_button.isEnabled()
    panel.deleteLater(); qt.processEvents()


def test_gallery_percentage_is_named_as_preview_cache_work():
    from thermalright_display_ui import ThermalrightDisplayStudio
    qt = app()
    class Host:
        thumbnail_total = 100
        thumbnail_finished = 2
        thumbnail_queue = [object()] * 3
        thumbnail_active = {}
        thumbnail_progress_panel = QWidget()
        thumbnail_progress = QProgressBar()
        thumbnail_progress_label = QLabel()
        def window(self):
            return self
        def tr_static(self, source):
            return source
    host = Host()
    ThermalrightDisplayStudio._update_thumbnail_progress(host)
    assert host.thumbnail_progress.value() == 2
    assert host.thumbnail_progress.maximum() == 100
    assert host.thumbnail_progress_label.text() == 'Galerievorschauen vorbereiten · 3 ausstehend'
    host.thumbnail_progress_panel.deleteLater(); qt.processEvents()


def test_legacy_dialog_uses_shared_editor_and_keeps_source_contract(tmp_path):
    qt = app(); folder = tmp_path / 'library'; folder.mkdir()
    media = folder / 'still.png'; media.write_bytes(b'original')
    state = DesignLibraryState((folder,), (), {}, ())
    dialog = DesignLibraryDialog(state)
    assert isinstance(dialog.panel, DesignLibraryPanel)
    assert dialog.state() == state
    assert DesignLibraryDialog._folder_media(folder) == [media]
    dialog.deleteLater(); qt.processEvents()
