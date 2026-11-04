#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Transient effect exploration with last-confirmed LCD composition fallback."""
from pathlib import Path
import time
from PySide6.QtCore import QEvent, QProcess, Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QAbstractButton, QAbstractSlider, QComboBox, QPushButton, QWidget
from .base_page import DisplayEffectsPage as BasePage
from .video_preview import BundledVideoPreview
from modules.lcd_media_manager.v1_0.preview_visibility import PreviewVisibility, exposed
from modules.lcd_levita.v1_7.media_preview import video_source


class DisplayEffectsPage(BasePage):
    def __init__(self, *args, **kwargs):
        self._window_preview_active = True
        self._preview_ready_after_show = False
        self._preview_activation_serial = 0
        self._last_video_frame_at = 0.
        self._preview_override = False
        super().__init__(*args, **kwargs)
        self.video_preview = BundledVideoPreview(self)
        self.video_preview.frame_ready.connect(self._video_frame_ready)
        self.preview_visibility = PreviewVisibility(self.preview_canvas, self._refresh_preview_driver, self)
        self.stock_library.user_selected.connect(self._select_library_preview)
        self.stock_library.selection_cleared.connect(self.clear_preview_selection)
        self.clear_button = QPushButton(self.tr('Auswahl aufheben'))
        self.clear_button.clicked.connect(self.clear_preview_selection)
        # The action row is the sibling layout directly below the canvas.
        self.preview_actions.insertWidget(2, self.clear_button)
        media = getattr(self.studio, 'media_preview', None)
        if media is not None: media.confirmed_changed.connect(self.sync_active_selection)
        QApplication.instance().installEventFilter(self)
        self.sync_active_selection()

    def _composition(self):
        return getattr(getattr(self.studio, 'media_preview', None), 'applied', None)

    def _active_media(self):
        composition = self._composition()
        if composition is not None: return composition.media
        if getattr(getattr(self.studio, 'media_preview', None), 'firmware_released', False): return None
        provider = getattr(self.studio, 'current_media_path', None)
        return provider() if callable(provider) else None

    def _library_selected(self):
        return self._preview_override and self.effect_combo.currentData() == 'library'

    def _current_video_path(self):
        return self.stock_library.current_video() if self._library_selected() else (
            video_source(self._active_media()) if not self._preview_override else None)

    def _preview_is_active(self):
        return bool(self._playing and self._window_preview_active and self._preview_ready_after_show
                    and exposed(self.preview_canvas))

    def set_window_active(self, active):
        self._window_preview_active = bool(active)
        self._refresh_preview_driver()

    def _refresh_preview_driver(self):
        video = getattr(self, 'video_preview', None)
        if video is None: return
        active = self._preview_is_active()
        selected = self._preview_override or self.stock_library._selection_active
        self.apply_button.setEnabled(selected and self.export_process.state() == QProcess.ProcessState.NotRunning)
        self.remember_button.setEnabled(selected)
        if self._current_video_path() is not None:
            self.preview_timer.stop()
            video.set_active(active)
        else:
            video.set_active(False)
            if active: self.preview_timer.start()
            else: self.preview_timer.stop()

    def _fallback_frame(self, background=None):
        composition = self._composition()
        if composition is not None:
            composition.render(self.preview_canvas, background)
        elif getattr(getattr(self.studio, 'media_preview', None), 'firmware_released', False):
            self.preview_canvas.set_background(QPixmap())
            self.preview_canvas.set_hardware_layer(QPixmap())
            self.preview_canvas.set_editable_layout(None); self.preview_canvas.set_specs(())
            self.preview_canvas.set_motion_layer(QPixmap())
        elif hasattr(self.studio, 'canvas'):
            self.studio.sync_effect_preview(self.preview_canvas,
                background if background is not None else self.studio.canvas._background)

    def render_preview(self):
        video = getattr(self, 'video_preview', None)
        if self._preview_override and not self._library_selected():
            super().render_preview()
            return
        path = self._current_video_path()
        if video is None or path is None:
            self._fallback_frame()
            self._refresh_preview_driver()
            return
        start = 0
        changed = video.load(path, preview_start_ms=start)
        if changed or video.latest_image.isNull():
            if self._library_selected():
                self.studio.sync_effect_preview(self.preview_canvas, self.stock_library.current_preview().scaled(
                    1600, 720, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else: self._fallback_frame()
        else: self._video_frame_ready(video.latest_image)
        self._refresh_preview_driver()

    def _video_frame_ready(self, image: QImage):
        if not self._preview_is_active() or image.isNull(): return
        if self.video_preview.source_path != self._current_video_path(): return
        now = time.monotonic()
        fps = max(5, min(20, int(getattr(self.studio, 'preview_fps', 20))))
        if now - self._last_video_frame_at < 1. / fps: return
        self._last_video_frame_at = now
        background = QPixmap.fromImage(image).scaled(1600, 720, Qt.AspectRatioMode.IgnoreAspectRatio,
                                                     Qt.TransformationMode.SmoothTransformation)
        composition = self._composition()
        if not self._preview_override and composition is not None:
            background = self.studio._fit_qpixmap(QPixmap.fromImage(image), composition.scale_mode)
        if self._library_selected(): self.studio.sync_effect_preview(self.preview_canvas, background)
        else: self._fallback_frame(background)

    def _select_library_preview(self):
        self._preview_override = True
        self.effect_combo.setCurrentIndex(max(0, self.effect_combo.findData('library')))
        self._library_selection_changed()
        self.render_preview()

    def _library_selection_changed(self):
        if not self.stock_library._selection_active: self._preview_override = False
        if self._preview_override and not self._syncing_effect_selection:
            self.settings.setValue('display_effects/library_media', str(self.stock_library.current_video()))
        if self.isVisible(): self.render_preview()

    def _control_changed(self, key):
        self._preview_override = True
        super()._control_changed(key)

    def _preset_changed(self, index):
        if not self._syncing_effect_selection: self._preview_override = True
        super()._preset_changed(index)

    def _effect_type_changed(self, index):
        if not self._syncing_effect_selection:
            self._preview_override = self.effect_combo.currentData() != 'library' or self.stock_library._selection_active
        super()._effect_type_changed(index)
        self._refresh_preview_driver()

    def sync_active_selection(self):
        if self._preview_override: return
        self._syncing_effect_selection = True
        try:
            active = self._active_media()
            matched = isinstance(active, Path) and self.stock_library.select_video(active)
            kind = 'library' if matched else str(self.settings.value('display_effects/type', 'smoke'))
            self.effect_combo.blockSignals(True)
            self.effect_combo.setCurrentIndex(max(0, self.effect_combo.findData(kind)))
            self.effect_combo.blockSignals(False)
            if not matched: self.stock_library.clear_selection()
            self._effect_type_changed(self.effect_combo.currentIndex())
        finally: self._syncing_effect_selection = False
        if self.isVisible(): self.render_preview()

    def clear_preview_selection(self):
        self._preview_override = False
        self.stock_library.clear_selection()
        self.sync_active_selection()

    def eventFilter(self, watched, event):  # noqa: N802
        if self._preview_override and isinstance(watched, QWidget) and self.isAncestorOf(watched):
            if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
                self.clear_preview_selection(); return True
            if event.type() == QEvent.Type.MouseButtonPress:
                parent = watched
                while parent is not None and parent is not self:
                    if isinstance(parent, (QAbstractButton, QAbstractSlider, QComboBox)): break
                    parent = parent.parentWidget()
                else: self.clear_preview_selection()
        return False

    def toggle_playback(self):
        super().toggle_playback(); self._refresh_preview_driver()

    def restart_preview(self):
        video = getattr(self, 'video_preview', None)
        if video is not None and self._current_video_path() is not None:
            video.restart(); self.render_preview()
        else: super().restart_preview()

    def showEvent(self, event):
        super().showEvent(event)
        self.sync_active_selection()
        self._preview_ready_after_show = False
        self._preview_activation_serial += 1
        serial = self._preview_activation_serial
        self._refresh_preview_driver()
        QTimer.singleShot(40, self, lambda: self._activate_preview_after_show(serial))

    def _activate_preview_after_show(self, serial):
        if serial != self._preview_activation_serial or not self.isVisible(): return
        self._preview_ready_after_show = True
        self.render_preview(); self._refresh_preview_driver()

    def hideEvent(self, event):
        self._preview_activation_serial += 1
        self._preview_ready_after_show = False
        self._preview_override = False
        self.stock_library.clear_selection()
        video = getattr(self, 'video_preview', None)
        if video is not None: video.set_active(False)
        super().hideEvent(event)

    def refresh_language(self):
        super().refresh_language()
        self.stock_library.refresh_language()
        if hasattr(self, 'clear_button'): self.clear_button.setText(self.tr('Auswahl aufheben'))

    def shutdown(self):
        QApplication.instance().removeEventFilter(self)
        self.preview_visibility.shutdown()
        self.video_preview.shutdown()
        super().shutdown()
