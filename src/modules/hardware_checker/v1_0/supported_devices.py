# SPDX-License-Identifier: GPL-3.0-or-later
"""Model cards filtered by device category and vendor; no hardware probing."""
from dataclasses import dataclass
from PySide6.QtCore import QSignalBlocker, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)
from modules.navigation_settings.v1_0.artwork import category_icon
from .device_catalog import CATEGORIES, DEVICES, Device, safe_link


@dataclass
class DeviceCard:
    widget: QGroupBox
    icon: QLabel
    badge: QLabel
    description: QLabel
    links: list
    device: Device


class SupportedDevicesPage(QWidget):
    def __init__(self, host, translate=None):
        super().__init__()
        self.host, self.cards = host, []
        self.translate = translate or host.tr_static
        self._vendor_choices = {}
        root = QVBoxLayout(self)
        self.title = QLabel(objectName="heroTitle"); root.addWidget(self.title)
        self.note = QLabel(); self.note.setWordWrap(True); root.addWidget(self.note)
        filters = QGridLayout(); root.addLayout(filters)
        self.category_label = QLabel(); self.category = QComboBox()
        self.vendor_label = QLabel(); self.vendor = QComboBox()
        self.category_label.setBuddy(self.category); self.vendor_label.setBuddy(self.vendor)
        self.search = QLineEdit()
        filters.addWidget(self.category_label, 0, 0); filters.addWidget(self.vendor_label, 0, 1)
        filters.addWidget(self.category, 1, 0); filters.addWidget(self.vendor, 1, 1)
        filters.addWidget(self.search, 2, 0, 1, 2)
        self.grid = QGridLayout(); self.grid.setSpacing(12); self.grid.setAlignment(Qt.AlignmentFlag.AlignTop); root.addLayout(self.grid)
        self.empty = QLabel(); root.addWidget(self.empty); root.addStretch()
        for device in DEVICES:
            card = QGroupBox(device.name, self)
            card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
            layout = QVBoxLayout(card)
            row = QHBoxLayout(); icon = QLabel(); icon.setFixedSize(60, 60)
            badge = QLabel(); badge.setWordWrap(True)
            row.addWidget(icon); row.addWidget(badge, 1); layout.addLayout(row)
            text = QLabel(); text.setWordWrap(True); layout.addWidget(text, 1)
            links = []
            for caption, url in (("Herstellerseite", device.manufacturer_url), ("Produktseite", device.product_url)):
                target = safe_link(url)
                if not target:
                    continue
                button = QPushButton(); button.setToolTip(target)
                button.clicked.connect(lambda _checked=False, link=target: QDesktopServices.openUrl(QUrl(link)))
                layout.addWidget(button); links.append((button, caption))
            self.cards.append(DeviceCard(card, icon, badge, text, links, device))
        self.category.currentIndexChanged.connect(self._category_changed)
        self.vendor.currentIndexChanged.connect(self._vendor_changed)
        self.search.textChanged.connect(self.reflow)
        self.refresh_language()

    def _category_changed(self):
        self._refresh_vendors(); self.reflow()

    def _vendor_changed(self):
        self._vendor_choices[self.category.currentData()] = self.vendor.currentData()
        self.reflow()

    def _refresh_vendors(self):
        category = self.category.currentData()
        selected = self._vendor_choices.get(category, "")
        vendors = dict.fromkeys(d.vendor for d in DEVICES if not category or d.category == category)
        with QSignalBlocker(self.vendor):
            self.vendor.clear(); self.vendor.addItem(self.translate("Alle Hersteller"), "")
            for vendor in vendors:
                self.vendor.addItem(vendor, vendor)
            self.vendor.setCurrentIndex(max(0, self.vendor.findData(selected)))

    def refresh_language(self):
        tr = self.translate
        self.title.setText(tr("Von OHC unterstützte Geräte"))
        self.note.setText(tr("Lokal bestätigte Geräte und Unterstützung über Backends sind getrennt gekennzeichnet. Die Funktionen richten sich nach Modell, Treiber und Einrichtung."))
        self.category_label.setText(tr("Geräteart")); self.vendor_label.setText(tr("Hersteller"))
        selected = self.category.currentData() if self.category.count() else "gpu"
        with QSignalBlocker(self.category):
            self.category.clear()
            for key, caption in CATEGORIES:
                self.category.addItem(tr(caption), key)
            self.category.addItem(tr("Alle Kategorien"), "")
            self.category.setCurrentIndex(max(0, self.category.findData(selected)))
        self._refresh_vendors()
        self.search.setPlaceholderText(tr("Geräte suchen …"))
        self.empty.setText(tr("Keine passenden Geräte."))
        for card in self.cards:
            device = card.device
            card.widget.setTitle(tr(device.name)); card.badge.setText(tr(device.state))
            card.description.setText(tr(device.description))
            card.icon.setPixmap(category_icon(device.kind, self.palette(), 60).pixmap(60, 60))
            for button, caption in card.links:
                button.setText(tr(caption))
        self.reflow()

    def reflow(self, *_args):
        needle = self.search.text().strip().casefold()
        category, vendor = self.category.currentData(), self.vendor.currentData()
        columns = 3 if self.width() >= 1150 else 2 if self.width() >= 720 else 1
        index = 0
        for card in self.cards:
            self.grid.removeWidget(card.widget)
            device = card.device
            matches = (not category or device.category == category) and (not vendor or device.vendor == vendor)
            haystack = ' '.join((device.name, device.vendor, card.badge.text(), card.description.text())).casefold()
            visible = matches and (not needle or needle in haystack)
            card.widget.setVisible(visible)
            if visible:
                self.grid.addWidget(card.widget, index // columns, index % columns); index += 1
        self.empty.setVisible(index == 0)
        for column in range(3):
            self.grid.setColumnStretch(column, 1 if column < columns else 0)

    def resizeEvent(self, event):
        super().resizeEvent(event); self.reflow()
