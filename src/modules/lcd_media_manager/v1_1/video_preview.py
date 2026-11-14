#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Visibility-bound, read-only preview playback for bundled display media."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtGui import QImage
from PySide6.QtMultimedia import QMediaPlayer, QVideoFrame, QVideoSink


class BundledVideoPreview(QObject):
    """Decode one allowlisted local video and emit frames only while active."""

    frame_ready = Signal(QImage)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.player = QMediaPlayer(self)
        self.sink = QVideoSink(self)
        self.player.setVideoOutput(self.sink)
        self.player.setLoops(QMediaPlayer.Loops.Once)
        self.player.mediaStatusChanged.connect(self._media_status_changed)
        self.sink.videoFrameChanged.connect(self._frame_changed)
        self.source_path: Path | None = None
        self.latest_image = QImage()
        self._active = False
        self._source_loaded = False
        self._preview_start_ms = 0
        self._seek_pending = False

    def _load_player_source(self) -> None:
        """Open the decoder only while the preview is actually exposed."""

        if self.source_path is None or self._source_loaded:
            return
        self._seek_pending = True
        self.player.setSource(QUrl.fromLocalFile(str(self.source_path)))
        self._source_loaded = True

    def _release_player_source(self) -> None:
        """Release FFmpeg threads and frame buffers for hidden pages."""

        self.player.stop()
        self.player.setSource(QUrl())
        self._source_loaded = False
        self._seek_pending = self.source_path is not None
        self.latest_image = QImage()

    def load(self, path: Path, *, preview_start_ms: int = 0) -> bool:
        clean = path.resolve()
        start_ms = max(0, int(preview_start_ms))
        if self.source_path == clean and self._preview_start_ms == start_ms:
            return False
        self.source_path = clean
        self._preview_start_ms = start_ms
        self._seek_pending = True
        self.latest_image = QImage()
        self._release_player_source()
        if self._active:
            self._load_player_source()
            self.player.play()
        return True

    def set_active(self, active: bool) -> None:
        self._active = bool(active)
        if self._active and self.source_path is not None:
            self._load_player_source()
            self.player.play()
        else:
            self._release_player_source()

    def restart(self) -> None:
        self._load_player_source()
        self.player.setPosition(self._preview_start_ms)
        if self._active:
            self.player.play()

    def shutdown(self) -> None:
        self._active = False
        self._release_player_source()
        self.source_path = None
        self._seek_pending = False

    def _prime_start_position(self) -> None:
        duration_ms = self.player.duration()
        if not self._seek_pending or duration_ms <= 0 or not self.player.isSeekable():
            return
        self.player.setPosition(min(self._preview_start_ms, max(0, duration_ms - 250)))
        self._seek_pending = False

    def _media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status in {QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia}:
            self._prime_start_position()
            return
        if status != QMediaPlayer.MediaStatus.EndOfMedia:
            return
        self.player.setPosition(self._preview_start_ms)
        if self._active:
            self.player.play()

    def _frame_changed(self, frame: QVideoFrame) -> None:
        if not self._active or not frame.isValid():
            return
        image = frame.toImage().copy()
        if image.isNull():
            return
        self.latest_image = image
        self.frame_ready.emit(image)
