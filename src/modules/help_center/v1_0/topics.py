# SPDX-License-Identifier: GPL-3.0-or-later
"""Original topic-card painting using existing category icons and Qt fonts."""
from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPalette, QPen
from PySide6.QtWidgets import QStyle, QStyledItemDelegate

INTRO_ROLE = Qt.ItemDataRole.UserRole + 1
TOPIC_ICONS = {
    "getting_started": "overview", "lcd": "lcd", "cooling": "cooling",
    "rgb": "rgb_studio", "profiles": "profiles", "openlinkhub": "openlinkhub",
    "settings": "settings", "troubleshooting": "log", "supported_devices": "hardware_checker",
    "wallpaper_engine": "wallpaper_engine", "desktop": "desktop_designs",
}


class TopicDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        width = max(180, option.widget.viewport().width() - 62) if option.widget else 230
        font = QFont(option.font); font.setBold(True)
        from PySide6.QtGui import QFontMetrics
        title_height = QFontMetrics(font).boundingRect(
            QRect(0, 0, width, 1000), Qt.TextFlag.TextWordWrap, str(index.data() or "")
        ).height()
        return QSize(280, max(76, title_height + 42))

    def paint(self, painter, option, index):
        painter.save(); painter.setRenderHint(painter.RenderHint.Antialiasing)
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
        bounds = option.rect.adjusted(3, 4, -3, -4)
        palette = option.palette
        fill = QColor(palette.color(QPalette.ColorRole.Base))
        if selected or hovered:
            fill = QColor(palette.color(QPalette.ColorRole.Highlight)); fill.setAlpha(34 if selected else 18)
        border = palette.color(QPalette.ColorRole.Highlight if selected else QPalette.ColorRole.Mid)
        painter.setPen(QPen(border, 1.5 if selected else 1)); painter.setBrush(fill)
        painter.drawRoundedRect(bounds, 12, 12)
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if icon is not None:
            painter.drawPixmap(bounds.x()+12, bounds.y()+15, icon.pixmap(26, 26))
        text_rect = bounds.adjusted(49, 11, -12, -10)
        font = QFont(option.font); font.setBold(True); painter.setFont(font)
        painter.setPen(palette.color(QPalette.ColorRole.Text))
        title_rect = text_rect.adjusted(0, 0, 0, -19)
        painter.drawText(title_rect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignTop,
                         str(index.data() or ""))
        painter.setFont(option.font); painter.setPen(palette.color(QPalette.ColorRole.PlaceholderText))
        intro = option.fontMetrics.elidedText(str(index.data(INTRO_ROLE) or ""),
                                              Qt.TextElideMode.ElideRight, text_rect.width())
        painter.drawText(QRect(text_rect.x(), text_rect.bottom()-15, text_rect.width(), 17),
                         Qt.AlignmentFlag.AlignVCenter, intro)
        painter.restore()
