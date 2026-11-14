# SPDX-License-Identifier: GPL-3.0-or-later
"""Original palette-aware device symbols and aspect-preserving sidebar art."""
import math
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QLabel


def draw_symbol(painter, key, rect, foreground, accent):
    painter.save()
    painter.translate(rect.x(), rect.y())
    painter.scale(rect.width() / 100, rect.height() / 100)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(foreground, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.setBrush(Qt.BrushStyle.NoBrush)

    def fan(x, y, radius):
        painter.drawEllipse(QRectF(x-radius, y-radius, radius*2, radius*2))
        painter.drawEllipse(QRectF(x-3, y-3, 6, 6))
        for i in range(5):
            angle = i * math.tau / 5
            painter.drawLine(round(x+math.cos(angle)*5), round(y+math.sin(angle)*5),
                             round(x+math.cos(angle+.45)*(radius-4)), round(y+math.sin(angle+.45)*(radius-4)))
    if key in {"home", "overview"}:
        path=QPainterPath();path.moveTo(12,46);path.lineTo(50,14);path.lineTo(88,46)
        painter.drawPath(path);painter.drawRoundedRect(QRectF(24,43,52,43),3,3)
        painter.setPen(QPen(accent,3));painter.drawRect(QRectF(43,60,15,26))
    elif key == "hardware_fix":
        path=QPainterPath();path.moveTo(68,15);path.cubicTo(35,9,29,35,43,49)
        path.lineTo(17,75);path.lineTo(27,86);path.lineTo(55,58)
        path.cubicTo(78,70,94,43,82,28);path.lineTo(69,42);path.lineTo(56,30);path.closeSubpath()
        painter.drawPath(path)
    elif key in {"hardware_checker", "supported_devices"}:
        painter.drawRoundedRect(QRectF(15,18,70,62),6,6)
        painter.setPen(QPen(accent,5));painter.drawLine(31,49,44,62);painter.drawLine(44,62,70,34)
    elif key in {"settings", "about", "help", "log"}:
        if key == "settings":
            painter.drawEllipse(QRectF(23,23,54,54));painter.drawEllipse(QRectF(40,40,20,20))
            for i in range(8):
                a=i*math.tau/8
                painter.drawLine(round(50+29*math.cos(a)),round(50+29*math.sin(a)),round(50+39*math.cos(a)),round(50+39*math.sin(a)))
        elif key == "log":
            painter.drawRoundedRect(QRectF(22,12,56,76),5,5)
            for y in (31,48,65):painter.drawLine(34,y,66,y)
        else:
            painter.drawEllipse(QRectF(16,16,68,68))
            font=painter.font();font.setPixelSize(49);painter.setFont(font)
            painter.drawText(QRectF(18,16,64,68),Qt.AlignmentFlag.AlignCenter,"?" if key=="help" else "i")
    elif key == "case":
        painter.drawRoundedRect(QRectF(25, 10, 50, 80), 7, 7)
        fan(50, 33, 14); fan(50, 68, 14)
        painter.setPen(QPen(accent, 3)); painter.drawLine(32, 52, 68, 52)
    elif key == "gpu":
        painter.drawRoundedRect(QRectF(8, 29, 82, 42), 6, 6)
        fan(30, 50, 15); fan(67, 50, 15)
        painter.drawLine(19, 72, 73, 72)
        painter.setPen(QPen(accent, 4)); painter.drawLine(25, 79, 65, 79)
    elif key == "openlinkhub":
        painter.drawRoundedRect(QRectF(28, 12, 44, 76), 21, 21)
        painter.drawLine(50, 13, 50, 43)
        painter.drawLine(29, 43, 71, 43)
        painter.setPen(QPen(accent, 4)); painter.drawLine(50, 24, 50, 34)
        painter.drawLine(23, 49, 23, 61)
    elif key in {"cooling", "cooling_controls", "temperature_recording"}:
        fan(50, 50, 33)
        painter.setPen(QPen(accent, 3)); painter.drawRoundedRect(QRectF(10, 10, 80, 80), 10, 10)
    elif key in {"lcd", "lcd_studio", "display_effects", "wallpaper_engine", "desktop_designs"}:
        painter.drawRoundedRect(QRectF(9, 19, 82, 56), 6, 6)
        painter.drawLine(50, 76, 50, 87); painter.drawLine(32, 88, 68, 88)
        painter.setPen(QPen(accent, 3)); painter.drawEllipse(QRectF(36, 32, 28, 28))
    elif key == "rgb_studio":
        for i in range(8):
            a=i*math.tau/8
            painter.setPen(QPen(QColor.fromHsv(i*45, 190, 220), 5))
            painter.drawArc(QRectF(17,17,66,66),i*45*16,32*16)
        painter.setPen(QPen(foreground,3));fan(50,50,21)
    elif key in {"profiles", "programs", "snapshot_manager"}:
        for i in range(3):
            painter.drawRoundedRect(QRectF(15+i*8, 18+i*16, 60, 30), 5, 5)
    elif key == "automations":
        painter.drawEllipse(QRectF(17,17,66,66));painter.drawLine(50,50,50,29);painter.drawLine(50,50,67,58)
    elif key == "games":
        painter.drawRoundedRect(QRectF(12,30,76,45),16,16)
        painter.drawLine(25,51,43,51);painter.drawLine(34,42,34,60)
        painter.setPen(QPen(accent,5));painter.drawPoint(65,46);painter.drawPoint(74,57)
    elif key in {"design_hub", "paired_designs"}:
        fan(31,50,23)
        painter.drawRoundedRect(QRectF(59,27,32,47),4,4)
        painter.setPen(QPen(accent,3));painter.drawLine(64,41,86,41);painter.drawLine(64,53,80,53)
    else:
        for x,y in ((19,19),(55,19),(19,55),(55,55)):
            painter.drawRoundedRect(QRectF(x,y,26,26),5,5)
    painter.restore()


def category_icon(key, palette, size=32):
    from PySide6.QtGui import QPalette
    pixmap=QPixmap(size,size);pixmap.fill(Qt.GlobalColor.transparent)
    painter=QPainter(pixmap)
    draw_symbol(painter,key,QRectF(1,1,size-2,size-2),palette.color(QPalette.ColorRole.Text),palette.color(QPalette.ColorRole.Highlight))
    painter.end()
    return QIcon(pixmap)


class SidebarArtwork(QLabel):
    def __init__(self, source):
        super().__init__()
        self.original=QPixmap(str(source));self.category="overview"
        self.setObjectName("brandLogo")
        self.setFixedSize(176,176)
        self.setStyleSheet("padding: 0; border: none; background: transparent;")

    def set_category(self, category):
        if self.category != category:
            self.category=category;self.update()

    def paintEvent(self, _event):
        from PySide6.QtGui import QPalette
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect=QRectF(self.contentsRect()).adjusted(3,3,-3,-3)
        side=min(rect.width(),rect.height())
        rect=QRectF(rect.center().x()-side/2,rect.center().y()-side/2,side,side)
        path=QPainterPath();path.addRoundedRect(rect,14,14)
        p.setClipPath(path)
        if self.category=="overview" and not self.original.isNull():
            scaled=self.original.scaled(round(side),round(side),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap(round(rect.center().x()-scaled.width()/2),round(rect.center().y()-scaled.height()/2),scaled)
        else:
            draw_symbol(p,self.category,rect.adjusted(18,18,-18,-18),self.palette().color(QPalette.ColorRole.Text),self.palette().color(QPalette.ColorRole.Highlight))
        p.setClipping(False);p.setPen(QPen(self.palette().color(QPalette.ColorRole.Midlight),1));p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect,14,14)


def refresh_navigation_art(host,page=None):
    if not hasattr(host,"navigation_items"):return
    current=host.tabs.currentIndex() if page is None and hasattr(host,"tabs") else page
    key="overview"
    from PySide6.QtGui import QPalette
    signature=(host.palette().color(QPalette.ColorRole.Text).rgba(),host.palette().color(QPalette.ColorRole.Highlight).rgba(),tuple(host.navigation_items))
    repaint=signature!=getattr(host,"_navigation_art_signature",None)
    host._navigation_art_signature=signature
    for name,item in host.navigation_items.items():
        if repaint:item.setIcon(0,category_icon(name,host.palette()))
        if item.parent() is None and item.data(0,Qt.ItemDataRole.UserRole)==current:
            key=name
    if current==getattr(host,"hardware_checker_page_index",-2):
        index=host.hardware_checker_page.section_tabs.currentIndex()
        key=("hardware_checker","hardware_fix","supported_devices")[index]
    for attribute, category in (("design_hub_page_index", "paired_designs"),
                                 ("games_page_index", "games"),
                                 ("design_automation_page_index", "automations")):
        if current == getattr(host, attribute, -3): key = category
    art=getattr(host,"sidebar_artwork",None)
    if art is not None:art.set_category(key);art.update()
