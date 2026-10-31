# SPDX-License-Identifier: GPL-3.0-or-later
"""Category/brand/model/color and explicit LEDs per fan in the block editor."""
from PySide6.QtWidgets import QComboBox, QFormLayout, QGroupBox, QLabel, QPushButton, QSpinBox
from .fan_profiles import declared_total, profile_for_slot
from .fan_library import available_brands, available_models, remember_model


class FanProfileEditor(QGroupBox):
    def __init__(self, host, slot, count_input):
        tr = host.tr_static
        super().__init__(tr("Lüfter"), host)
        self.setObjectName("slotFanProfile")
        self.count_input = count_input
        self.host = host
        profile = profile_for_slot(host, slot) if slot else dict(brand="", model="", color="black", leds_per_fan=0)
        form = QFormLayout(self)
        form.addRow(tr("Kategorie"), QLabel(tr("Lüfter")))
        self.brand = QComboBox()
        self.brand.setObjectName("slotFanBrand")
        self.brand.setEditable(True)
        self.brand.lineEdit().setMaxLength(64)
        self.brand.addItem("—", "")
        self.brand.addItems(available_brands(host))
        self.brand.setEditText(profile["brand"])
        self.model = QComboBox()
        self.model.setObjectName("slotFanModel")
        self.model.setEditable(True)
        self.model.lineEdit().setMaxLength(64)
        self.model.setEditText(profile["model"])
        self.color = QComboBox()
        self.color.setObjectName("slotFanColor")
        self.color.addItem(tr("Schwarz"), "black")
        self.color.addItem(tr("Weiß"), "white")
        self.color.setCurrentIndex(max(0, self.color.findData(profile["color"])))
        self.leds = QSpinBox()
        self.leds.setObjectName("slotFanLedsPerFan")
        self.leds.setRange(0, 512)
        self.leds.setSpecialValueText("—")
        self.leds.setValue(profile["leds_per_fan"])
        self.total_label = QLabel()
        self.total_label.setObjectName("slotFanLedTotal")
        form.addRow(tr("Marke"), self.brand)
        form.addRow(tr("Modell"), self.model)
        form.addRow(tr("Farbe"), self.color)
        form.addRow(tr("LEDs je Lüfter"), self.leds)
        form.addRow(tr("Gesamt"), self.total_label)
        self.save_model = QPushButton(tr("Modell speichern"))
        self.save_model.setObjectName("slotFanSaveModel")
        form.addRow(self.save_model)
        def models_changed():
            old = self.model.currentText()
            self.model.blockSignals(True)
            self.model.clear()
            seen = set()
            for value in available_models(host):
                if value["brand"].casefold() == self.brand.currentText().strip().casefold() and value["model"] not in seen:
                    self.model.addItem(value["model"], value["model"])
                    seen.add(value["model"])
            if self.brand.currentText() == "Jungle Leopard": self.model.addItem("Interstellar-V2")
            self.model.setEditText(old)
            self.model.blockSignals(False)
        self.brand.currentTextChanged.connect(lambda _text: models_changed())
        models_changed()
        self.leds.valueChanged.connect(lambda _n: self.update_total())
        self.brand.currentTextChanged.connect(lambda _s: self.update_total())
        self.model.currentTextChanged.connect(lambda _s: self.update_total())
        self.model.activated.connect(self.apply_model)
        self.save_model.clicked.connect(self.store_model)
        count_input.valueChanged.connect(lambda _n: self.update_total())
        self.update_total()

    def values(self):
        return dict(brand=self.brand.currentText().strip()[:64], model=self.model.currentText().strip()[:64],
                    color=self.color.currentData(), leds_per_fan=self.leds.value())

    def total(self):
        return declared_total(self.values(), self.count_input.value())

    def update_total(self):
        total = self.total()
        self.total_label.setText(f"{self.count_input.value()} × {self.leds.value()} = {total} LEDs" if total else "—")
        self.save_model.setEnabled(bool(total and self.values()["brand"] and self.values()["model"]))

    def apply_model(self, _index):
        values = [v for v in available_models(self.host)
                  if v["brand"].casefold() == self.brand.currentText().strip().casefold()
                  and v["model"].casefold() == self.model.currentText().strip().casefold()]
        value = next((v for v in values if v["color"] == self.color.currentData()), None)
        if value is None and len(values) == 1: value = values[0]
        if value is not None:
            self.leds.setValue(value["leds_per_fan"])
            self.color.setCurrentIndex(self.color.findData(value["color"]))

    def store_model(self):
        if remember_model(self.host, self.values()):
            brand = self.brand.currentText()
            self.brand.blockSignals(True)
            self.brand.clear()
            self.brand.addItem("—", "")
            self.brand.addItems(available_brands(self.host))
            self.brand.setEditText(brand)
            self.brand.blockSignals(False)
            model = self.model.currentText()
            if self.model.findText(model) < 0:
                self.model.blockSignals(True)
                self.model.addItem(model, model)
                self.model.setCurrentIndex(self.model.count() - 1)
                self.model.blockSignals(False)
