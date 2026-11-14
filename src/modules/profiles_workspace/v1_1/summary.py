# SPDX-License-Identifier: GPL-3.0-or-later
"""Saved values with original curve/swatch art; never live hardware samples."""
import math
import re
from pathlib import Path
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPalette, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget
from modules.navigation_settings.v1_0.artwork import category_icon
from .surfaces import Surface
from .model import lcd_summary_data


class SavedAccent(QWidget):
    def __init__(self, key, data):
        super().__init__()
        self.key, self.data = key, data
        self.setMinimumHeight(40); self.setMaximumHeight(44)

    def paintEvent(self, _event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        palette = QApplication.palette()
        accent = palette.color(QPalette.ColorRole.Highlight)
        if self.key == 'cooling':
            points = self.data.get('fan_curve') or self.data.get('pump_curve')
            if isinstance(points, (tuple, list)):
                clean = [point for point in points if isinstance(point, (list, tuple)) and len(point) == 2
                         and all(type(value) in (int, float) and math.isfinite(value) for value in point)]
                if len(clean) >= 2:
                    xmin, xmax = min(x for x, y in clean), max(x for x, y in clean)
                    path = QPainterPath()
                    for index, (x, y) in enumerate(clean):
                        point = QPointF(5+(x-xmin)/max(1, xmax-xmin)*(self.width()-10),
                                        self.height()-5-max(0, min(100, y))/100*(self.height()-10))
                        path.moveTo(point) if index == 0 else path.lineTo(point)
                    p.setPen(QPen(accent, 2)); p.drawPath(path)
        elif self.key in {'rgb', 'design'}:
            fields = ('studio_primary', 'studio_secondary') if self.key == 'rgb' else ('accent',)
            colors = [str(self.data.get(field, '')).lstrip('#') for field in fields]
            for index, value in enumerate(colors):
                if re.fullmatch('[0-9a-fA-F]{6}', value):
                    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor('#'+value))
                    p.drawRoundedRect(QRectF(index*46, 5, 36, 25), 7, 7)
        p.end()


class SummaryTile(Surface):
    def __init__(self, key, title, icon, lines, payload, tr):
        super().__init__()
        self.setObjectName('profileSummaryTile'); self.key = key; self.icon_key = icon
        self.setMinimumHeight(148)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(self); layout.setContentsMargins(16, 14, 16, 16); layout.setSpacing(9)
        header = QHBoxLayout(); header.setSpacing(10)
        self.icon_label = QLabel(); self.icon_label.setFixedSize(34, 34)
        self.title_label = QLabel(tr(title)); self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet('font-weight: 650; background: transparent;')
        header.addWidget(self.icon_label); header.addWidget(self.title_label, 1); layout.addLayout(header)
        self.value_label = QLabel('\n'.join(lines)); self.value_label.setWordWrap(True)
        self.value_label.setMinimumWidth(0)
        self.value_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        layout.addWidget(self.value_label)
        data = lcd_summary_data(payload) if key == 'lcd' else payload.get(key, {})
        if not isinstance(data, dict): data = {}
        if key == 'cooling' and (data.get('fan_curve') or data.get('pump_curve')):
            layout.addWidget(SavedAccent(key, data))
        elif key in {'rgb', 'design'}:
            layout.addWidget(SavedAccent(key, data))
        elif key == 'lcd':
            self.add_poster(data, layout)
        self.refresh_palette()

    def add_poster(self, data, layout):
        value = data.get('media') or data.get('file')
        if not isinstance(value, str) or not value: return
        from modules.display_effects.v1_11.catalog import ASSET_ROOT, DESIGNS
        try:
            media = Path(value).resolve()
            if not media.is_relative_to(ASSET_ROOT.resolve()): return
            variant = next((v for design in DESIGNS for v in design.variants if v.video_path.resolve() == media), None)
            if variant is None: return
            poster = QPixmap(str(variant.preview_path))
        except (OSError, ValueError, RuntimeError): return
        if poster.isNull(): return
        label = QLabel(); label.setPixmap(poster.scaled(160, 58, Qt.AspectRatioMode.KeepAspectRatio,
                                                        Qt.TransformationMode.SmoothTransformation))
        label.setFixedHeight(58); layout.addWidget(label)

    def refresh_palette(self):
        self.icon_label.setPixmap(category_icon(self.icon_key, QApplication.palette(), 34).pixmap(34, 34))
        self.update()
