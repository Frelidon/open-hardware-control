# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only paired preview; no hidden-page decoder or hardware writes."""
import math
import time
from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget
from modules.display_effects.v1_11.video_preview import BundledVideoPreview
from modules.lcd_media_manager.v1_1.preview_visibility import PreviewVisibility, exposed
from rgb_effects import BUILTIN_DESIGNS, render_effect
from .controller import resolve_pair
from .catalog import pair_poster


class PairPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.setMaximumHeight(360)
        self.config = next(config for title, config in BUILTIN_DESIGNS if title == 'Matrix Code Rain')
        self.zoom = 100
        self.image = QImage()
        self.epoch = time.monotonic()
        self.active = False
        self.video = BundledVideoPreview(self)
        self.video.frame_ready.connect(self.frame_ready)
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.update)
        self.visibility = PreviewVisibility(self, self.refresh_visibility, self)

    def select(self, pair, variant_id=None, zoom=100):
        index, media = resolve_pair(pair, variant_id)
        self.config = BUILTIN_DESIGNS[index][1]
        self.zoom = zoom
        self.image = QImage(str(pair_poster(pair, variant_id)))
        self.video.load(media)
        self.epoch = time.monotonic()
        self.refresh_visibility()
        self.update()

    def set_zoom(self, zoom):
        self.zoom = zoom
        self.update()

    def frame_ready(self, image):
        self.image = image.scaled(960, 432, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
        self.update()

    def refresh_visibility(self):
        active = exposed(self)
        if active == self.active:
            return
        self.active = active
        self.video.set_active(active)
        if active:
            self.timer.start()
        else:
            self.timer.stop()

    def hideEvent(self, event):
        self.active = False
        self.timer.stop()
        self.video.set_active(False)
        super().hideEvent(event)

    def shutdown(self):
        self.timer.stop()
        self.video.shutdown()
        self.visibility.shutdown()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#030c08"))
        painter.drawRoundedRect(area, 16, 16)
        width, height = area.width(), area.height()
        # On a narrow page fans sit above the LCD instead of obscuring it.
        narrow = width < 620
        fan_area = QRectF(10, 8, width - 20, height * .36) if narrow else QRectF(10, 8, width * .25, height - 16)
        media_area = QRectF(12, height * .39, width - 24, height * .58) if narrow else QRectF(width * .28, 12, width * .70, height - 24)
        if not self.image.isNull():
            # The encoder first fits into a 1600×720 canvas, then zooms this
            # complete canvas. Keep exactly the same aspect and centred crop.
            ratio = min(media_area.width() / 1600, media_area.height() / 720)
            canvas = QRectF(0, 0, 1600 * ratio, 720 * ratio)
            canvas.moveCenter(media_area.center())
            factor = min(canvas.width() / self.image.width(), canvas.height() / self.image.height()) * self.zoom / 100
            target = QRectF(0, 0, self.image.width() * factor, self.image.height() * factor)
            target.moveCenter(canvas.center())
            painter.setBrush(Qt.GlobalColor.black); painter.drawRoundedRect(canvas, 12, 12)
            clip = QPainterPath(); clip.addRoundedRect(canvas, 12, 12)
            painter.save(); painter.setClipPath(clip)
            painter.drawImage(target, self.image); painter.restore()
        radius = min(fan_area.width() / (7 if narrow else 2.6), fan_area.height() / (2.5 if narrow else 7))
        elapsed = max(0.0, time.monotonic() - self.epoch)
        for fan in range(3):
            cx = fan_area.left() + fan_area.width() * (fan + .5) / 3 if narrow else fan_area.center().x()
            cy = fan_area.center().y() if narrow else fan_area.top() + fan_area.height() * (fan + .5) / 3
            painter.setPen(QPen(QColor("#324c40"), 1))
            painter.setBrush(QColor("#0a1710"))
            painter.drawRoundedRect(QRectF(cx-radius*1.2, cy-radius*1.2, radius*2.4, radius*2.4), 8, 8)
            colors = render_effect(self.config, 20, elapsed + fan * .28)
            for led, color in enumerate(colors):
                painter.setPen(QPen(QColor(*color), max(4, radius * .20), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                painter.drawArc(QRectF(cx-radius, cy-radius, radius*2, radius*2), led * 18 * 16, 12 * 16)
            painter.setPen(QPen(QColor("#355345"), 2))
            for blade in range(5):
                angle = blade * math.tau / 5
                painter.drawLine(round(cx), round(cy), round(cx+math.cos(angle)*radius*.65), round(cy+math.sin(angle)*radius*.65))
        painter.end()
