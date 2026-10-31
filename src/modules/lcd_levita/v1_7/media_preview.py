# SPDX-License-Identifier: GPL-3.0-or-later
"""Selected local video preview and a separate last-confirmed composition."""
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
import time
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap
from modules.lcd_media_manager.v1_0.preview_visibility import PreviewVisibility, exposed
from .motion_renderer import render_layer2_motion_frame


def video_source(media):
    if media is None: return None
    media = Path(media)
    if media.is_dir():
        media = next((media / name for name in ('Theme.mp4', 'Theme.webm', 'Theme.mov', 'Theme.mkv', 'Theme.avi')
                      if (media / name).is_file()), None)
    return media.resolve() if media and media.is_file() and media.suffix.lower() in {'.mp4', '.webm', '.mov', '.mkv', '.avi'} else None


@dataclass(frozen=True)
class Composition:
    media: Path
    hardware: object
    values: dict
    motion: bool
    scale_mode: str

    @classmethod
    def capture(cls, studio):
        canvas = studio.canvas
        fields = ('layer1_intensity', 'layer2_intensity', 'hardware_layer', 'layout', 'specs',
                  'background_x', 'background_y', 'notch_visible', 'notch_width',
                  'notch_top_radius', 'notch_bottom_radius', 'split_mode', 'background')
        values = {name: deepcopy(getattr(canvas, '_' + name)) if name in {'layout', 'specs'}
                  else getattr(canvas, '_' + name) for name in fields}
        hardware = studio.current_hardware_design_path()
        return cls(studio.current_media_path(), hardware, values, studio._layer2_motion_enabled(hardware),
                   str(studio.media_scale_mode.currentData()))

    def render(self, target, background=None):
        v = self.values
        target.set_layer_intensities(v['layer1_intensity'], v['layer2_intensity'])
        target.set_hardware_layer(v['hardware_layer']); target.set_editable_layout(v['layout'])
        target.set_specs(v['specs']); target.set_background_offset(v['background_x'], v['background_y'])
        target.set_notch_mask(v['notch_visible'], v['notch_width'], v['notch_top_radius'], v['notch_bottom_radius'])
        target.set_split_mode(v['split_mode'])
        target.set_background(background if background is not None else v['background'])
        target.set_motion_layer(QPixmap.fromImage(render_layer2_motion_frame(self.hardware.name, (time.monotonic() / 6.) % 1.))
                                if self.motion and self.hardware else QPixmap())


class MediaPreview(QObject):
    confirmed_changed = Signal()

    def __init__(self, studio):
        super().__init__(studio)
        self.studio = studio
        self.video = None
        self.pending = self.applied = None
        self.firmware_released = False
        self.last_frame = 0.
        self.observer = PreviewVisibility(studio.canvas, self.refresh, self)

    def capture(self): self.pending = Composition.capture(self.studio)

    def confirm(self):
        if self.pending is not None:
            self.applied, self.pending = self.pending, None
            self.firmware_released = False
            self.confirmed_changed.emit()

    def release(self):
        self.applied = self.pending = None
        self.firmware_released = True
        self.confirmed_changed.emit()

    def refresh(self):
        studio = self.studio
        active = not studio.shutdown_started and exposed(studio.canvas)
        if active and studio._layer2_motion_enabled(studio.current_hardware_design_path()):
            studio.layer2_motion_timer.start()
        else:
            studio.layer2_motion_timer.stop()
        path = video_source(studio.current_media_path())
        if active and path is not None:
            if self.video is None:
                from modules.lcd_media_manager.v1_0.video_preview import BundledVideoPreview
                self.video = BundledVideoPreview(self)
                self.video.frame_ready.connect(self.frame)
            self.video.load(path)
        if self.video is not None: self.video.set_active(active and path is not None)

    def frame(self, image):
        if not exposed(self.studio.canvas) or self.studio.shutdown_started: return
        if self.video.source_path != video_source(self.studio.current_media_path()): return
        now = time.monotonic()
        fps = max(5, min(20, self.studio.preview_fps))
        if now - self.last_frame < 1. / fps: return
        self.last_frame = now
        self.studio.canvas.set_background(self.studio._fit_qpixmap(QPixmap.fromImage(image),
                                           str(self.studio.media_scale_mode.currentData())))

    def shutdown(self):
        self.observer.shutdown()
        if self.video is not None: self.video.shutdown()
