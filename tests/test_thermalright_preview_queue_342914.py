#!/usr/bin/env python3
"""Regression: a large Levita video gallery must never block Qt construction."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]


def _exercise_real_qt_queue() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    sys.path.insert(0, str(ROOT))

    from PySide6.QtCore import QProcess, QSettings
    from PySide6.QtGui import QColor, QImage
    from PySide6.QtWidgets import QApplication
    from thermalright_display import MediaEntry
    import thermalright_display_ui as display_ui

    qt_app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory(prefix="ohc-preview-queue-") as temporary:
        temporary_root = Path(temporary)
        media_root = temporary_root / "videos"
        media_root.mkdir()
        entries: list[MediaEntry] = []
        for number in range(140):
            video = media_root / f"a{number:03d}.mp4"
            video.touch()
            entries.append(MediaEntry(video, video.name, "video"))

        display_ui.default_trcc_design_directory = lambda: None
        settings = QSettings(str(temporary_root / "settings.ini"), QSettings.Format.IniFormat)
        studio = display_ui.ThermalrightDisplayStudio(settings, temporary_root / "cache")

        started = time.monotonic()
        studio._populate_media_combo(entries)
        elapsed = time.monotonic() - started

        assert elapsed < 1.5, f"gallery construction blocked for {elapsed:.2f}s"
        assert studio.thumbnail_total == 140
        assert len(studio.thumbnail_active) <= 2
        assert len(studio.thumbnail_queue) + len(studio.thumbnail_active) == 140
        assert not studio.thumbnail_progress_panel.isHidden()

        # The cache key includes source path, size, and modification time. A
        # valid result is reused by later cards and later application processes.
        cache_paths = studio._thumbnail_cache_paths(entries[0].path)
        assert cache_paths is not None
        _key, cached_preview, _failure = cache_paths

        studio.pending_apply_sequence = [(('prepared',), False)]
        studio._apply_finished(True, "")
        qt_app.processEvents()
        assert "aktiv" in studio.preview_status.text().casefold()
        assert studio.pending_apply_sequence == []
        assert studio.next_hardware_apply_at > time.monotonic()
        assert studio.command_process.processEnvironment().value("TRCC_DAEMON") == "1"
        assert studio.command_process.processEnvironment().value("QT_QPA_PLATFORM") == "offscreen"
        assert studio.stream_process.processEnvironment().value("TRCC_DAEMON") == "1"
        assert studio.stream_process.processEnvironment().value("QT_QPA_PLATFORM") == "offscreen"
        assert studio._media_is_animated(entries[0].path)

        studio.startup_apply_active = True
        studio.startup_retry_count = 0
        studio.apply_retry_remaining = 0
        studio.pending_apply_sequence = [(('prepared',), False)]
        studio._apply_finished(False, "USB read failed: [Errno 110] Operation timed out")
        assert studio.startup_apply_active is False
        assert studio.startup_retry_count == 0
        assert "stromlos" in studio.preview_status.text().casefold()

        studio.hover_preview_timer.start()
        studio.hover_preview_debounce.start()
        studio.hover_extract_timeout.start()
        studio.hover_extract_process.start(
            sys.executable, ["-c", "import time; time.sleep(10)"],
        )
        assert studio.hover_extract_process.waitForStarted(1_000)
        studio.shutdown()
        assert not studio.hover_preview_timer.isActive()
        assert not studio.hover_preview_debounce.isActive()
        assert not studio.hover_extract_timeout.isActive()
        assert studio.hover_extract_process.state() == QProcess.ProcessState.NotRunning
        preview = QImage(176, 79, QImage.Format.Format_RGB32)
        preview.fill(QColor("#164870"))
        assert preview.save(str(cached_preview))
        assert studio._video_card_thumbnail(entries[0].path) == cached_preview

        studio.deleteLater()
        qt_app.processEvents()


def test_thermalright_video_preview_queue_with_real_qt() -> None:
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    completed = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--child"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


if __name__ == "__main__":
    _exercise_real_qt_queue()
    print("Levita video thumbnails are queued without blocking and persist in the cache.")
