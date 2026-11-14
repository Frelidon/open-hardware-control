# SPDX-License-Identifier: GPL-3.0-or-later
"""Original generic fan illustrations; choosing a card only edits a draft."""
import math
from PySide6.QtCore import QEvent, QTimer, QSize, Qt, QRectF
from PySide6.QtGui import QIcon, QPainter, QPalette, QPen, QPixmap
from PySide6.QtWidgets import QComboBox, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

# Distinct counts observed in the private local component reference. No model,
# electrical mapping or manufacturer support is inferred from those numbers.
LED_COUNTS=(4,6,8,9,10,11,12,14,15,16,17,18,20,22,24,26,28,30,32,34,54)


def fan_icon(count,palette,size=88):
    pixmap=QPixmap(size,size);pixmap.fill(Qt.GlobalColor.transparent)
    p=QPainter(pixmap);p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(size/100,size/100)
    p.setPen(QPen(palette.color(QPalette.ColorRole.Mid),2));p.setBrush(palette.color(QPalette.ColorRole.Base))
    p.drawRoundedRect(QRectF(5,5,90,90),9,9)
    p.setPen(QPen(palette.color(QPalette.ColorRole.Text),2))
    for i in range(7):
        p.save();p.translate(50,50);p.rotate(i*360/7)
        p.drawEllipse(QRectF(1,-12,30,15));p.restore()
    p.setBrush(palette.color(QPalette.ColorRole.Button));p.drawEllipse(QRectF(38,38,24,24))
    p.setPen(Qt.PenStyle.NoPen);p.setBrush(palette.color(QPalette.ColorRole.Highlight))
    for i in range(count):
        angle=i*math.tau/count-math.pi/2
        radius=2.6 if count<=24 else 1.8
        p.drawEllipse(QRectF(50+38*math.cos(angle)-radius,50+38*math.sin(angle)-radius,radius*2,radius*2))
    p.end();return QIcon(pixmap)


class FanCatalog(QGroupBox):
    def __init__(self,host):
        super().__init__(host.tr_static("Lüfterkatalog"))
        self.host=host;self.buttons={}
        root=QVBoxLayout(self);bar=QHBoxLayout()
        self.filter=QComboBox();self.filter.setProperty("i18nTranslateItems",False)
        self.filter.addItem(host.tr_static("Alle"),0)
        for count in LED_COUNTS:self.filter.addItem(f"{count} LEDs",count)
        bar.addWidget(QLabel(host.tr_static("LEDs je Lüfter")));bar.addWidget(self.filter);bar.addStretch();root.addLayout(bar)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.viewport().setAutoFillBackground(False)
        content=QWidget();grid=QGridLayout(content);grid.setContentsMargins(4,4,4,4);grid.setSpacing(10)
        self.scroll.setWidget(content);root.addWidget(self.scroll)
        self.reflow_timer=QTimer(self);self.reflow_timer.setSingleShot(True)
        self.reflow_timer.timeout.connect(self.filter_changed)
        self.scroll.viewport().installEventFilter(self)
        for index,count in enumerate(LED_COUNTS):
            button=QPushButton(f"{count} LEDs");button.setIcon(fan_icon(count,self.palette()))
            button.setIconSize(QSize(64,64));button.setMinimumHeight(78)
            button.setToolTip(host.tr_static("Generischer Lüfter · LED-Zahl als Entwurf übernehmen"))
            button.clicked.connect(lambda _checked=False,value=count:self.choose(value))
            grid.addWidget(button,index//4,index%4);self.buttons[count]=button
        self.filter.currentIndexChanged.connect(self.filter_changed)
        self.grid=grid
        self.filter_changed()

    def eventFilter(self, watched, event):
        if event.type()==QEvent.Type.Resize and not self.reflow_timer.isActive():
            self.reflow_timer.start(0)
        return super().eventFilter(watched,event)

    def filter_changed(self):
        selected=self.filter.currentData();visible=0
        columns=max(1,min(6,self.scroll.viewport().width()//180))
        for count,button in self.buttons.items():
            self.grid.removeWidget(button);show=not selected or selected==count
            button.setVisible(show)
            if show:self.grid.addWidget(button,visible//columns,visible%columns);visible+=1
        rows=max(1,math.ceil(visible/columns))
        row_height=max(button.minimumHeight() for button in self.buttons.values())
        self.scroll.setFixedHeight(min(rows,3)*(row_height+10)+8)
        self.updateGeometry()

    def choose(self,count):
        summary=getattr(self.host,"case_component_summary",None)
        if summary is not None:
            summary.set_led_draft(count)

    def changeEvent(self,event):
        super().changeEvent(event)
        if hasattr(self,"buttons"):
            for count,button in self.buttons.items():button.setIcon(fan_icon(count,self.palette()))
