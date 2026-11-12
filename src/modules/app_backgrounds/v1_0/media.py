# SPDX-License-Identifier: GPL-3.0-or-later
"""One visibility-bound decoder. No hardware writes, setting changes or paint I/O."""
import math
from PySide6.QtCore import QObject, QRectF, Qt, QSize
from PySide6.QtGui import QColor, QImage, QImageReader, QRadialGradient
from PySide6.QtWidgets import QApplication
from modules.lcd_media_manager.v1_1.video_preview import BundledVideoPreview
from modules.lcd_media_manager.v1_1.preview_visibility import PreviewVisibility
from .catalog import VIDEO_THEMES, profile_source


class MediaBackground(QObject):
    def __init__(self, widget):
        super().__init__(widget)
        self.widget = widget
        self.closed = False
        self.video = BundledVideoPreview(self)
        from PySide6.QtMultimedia import QMediaPlayer
        self.video.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.video.frame_ready.connect(self.frame_ready)
        self.frame = QImage()
        self.path = None
        self.rgb = None
        self.override = (None, None)
        self.profile_page = False
        self.active = False
        self.failed_path = None
        self.video.player.errorOccurred.connect(self.failed)
        self.visibility = PreviewVisibility(widget, self.sync, self)
        QApplication.instance().applicationStateChanged.connect(self.sync)

    def set_profile(self, payload, *, visible):
        self.profile_page = bool(visible)
        self.override = profile_source(payload) if visible else (None, None)
        self.configure()

    def configure(self):
        selected, rgb = self.override if self.profile_page else (None, None)
        if selected is None and rgb is None:
            selected = VIDEO_THEMES.get(self.widget._theme)
        if selected == self.path and rgb == self.rgb:
            self.sync(); return
        self.path, self.rgb = selected, rgb
        self.failed_path = None
        self.video.shutdown(); self.active = False; self.frame = QImage()
        if selected is not None and selected.is_file():
            if selected.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp'}:
                reader = QImageReader(str(selected))
                if reader.size().width()*reader.size().height() <= 40_000_000:
                    reader.setScaledSize(reader.size().scaled(QSize(960, 540), Qt.AspectRatioMode.KeepAspectRatio))
                    self.frame = reader.read()
            else:
                self.video.load(selected)
        self.widget._frame_dirty = True
        self.sync(); self.widget.update()

    def sync(self, *_args):
        if self.closed: return
        w = self.widget
        if not hasattr(w, '_enabled'): return
        app = QApplication.instance()
        active = (w._enabled and w._window_active and w.isVisible() and not w.window().isMinimized()
                  and (not w._pause_inactive or app.applicationState() == Qt.ApplicationState.ApplicationActive))
        video_active = bool(active and self.video.source_path and self.failed_path != self.path)
        if video_active != self.active:
            self.active = video_active; self.video.set_active(video_active)
        if not active:
            w._timer.stop()
        elif not w._timer.isActive():
            w._timer.start()

    def frame_ready(self, image):
        # Source decoder owns one latest frame; app composition retains at most 960x540.
        self.frame = image.scaled(960, 540, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
        self.widget._frame_dirty = True
        # Presentation stays on the user-selected background frame timer.

    def failed(self, *_args):
        if self.failed_path == self.path: return
        self.failed_path = self.path
        self.video.set_active(False); self.active = False
        self.frame = QImage(); self.widget._frame_dirty = True

    def paint(self, painter, width, height, base):
        if self.path is None and self.rgb is None: return False
        if not self.frame.isNull():
            # Keep aspect ratio and crop at center, never stretch a profile LCD.
            size = self.frame.size().scaled(QSize(width, height), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            target = QRectF((width-size.width())/2, (height-size.height())/2, size.width(), size.height())
            painter.setOpacity(self.widget._intensity / 100 * (.52 if base.lightness()>150 else .86))
            painter.drawImage(target, self.frame); painter.setOpacity(1)
        elif self.rgb is not None:
            from rgb_effects import render_effect
            colors = render_effect(self.rgb, 32, self.widget._phase)
            for index in range(8):
                color = QColor(*colors[index*4]); color.setAlpha(round(self.widget._intensity*.75))
                cx = width*(index+.5)/8
                cy = height*(.5+.22*math.sin(index*1.3+self.widget._phase*.2))
                gradient = QRadialGradient(cx, cy, width*.27)
                gradient.setColorAt(0, color); color.setAlpha(0); gradient.setColorAt(1, color)
                painter.fillRect(QRectF(0,0,width,height), gradient)
        # Decoder error/missing file gracefully leaves the normal palette base.
        return True

    def shutdown(self):
        self.closed = True
        self.video.shutdown(); self.visibility.shutdown()
