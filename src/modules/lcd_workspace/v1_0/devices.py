# SPDX-License-Identifier: GPL-3.0-or-later
"""Keep the Kraken compatibility cards reachable without mixing display families."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget
from .navigation import CurrentPageStack, WorkspaceTabs


class LegacyTileGroups(QWidget):
    """The existing tile order/visibility API, grouped by the three UI tasks."""
    orderChanged = Signal(object)
    thermalrightVisibilityChanged = Signal(bool)
    GROUPS = (('content', 'profiles'), ('preview', 'hardware', 'clock'), ('display', 'startup'))

    def __init__(self, factory, sections, order):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        self._default = ['thermalright', *[key for key, _widget, _span in sections]]
        self._order = [key for key in order if key in self._default]
        self._order.extend(key for key in self._default if key not in self._order)
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0)
        self.tabs = WorkspaceTabs(); root.addWidget(self.tabs); self.areas = []
        for index, keys in enumerate(self.GROUPS):
            # Full-width compatibility forms keep every old control reachable.
            area = factory('lcd-tiles', [(key, widget, 3) for key, widget, _span in sections if key in keys], self._order)
            area.orderChanged.connect(self._changed)
            self.tabs.widget(index).layout().addWidget(area); self.areas.append(area)

    def order(self): return list(self._order)

    def _changed(self, changed):
        iterator = iter(changed); keys = set(changed)
        self._order = [next(iterator) if key in keys else key for key in self._order]
        self.orderChanged.emit(self.order())

    def set_key_visible(self, key, visible):
        if key == 'thermalright':
            self.thermalrightVisibilityChanged.emit(bool(visible))
            return
        for area in self.areas: area.set_key_visible(key, visible)

    def prioritize(self, keys):
        requested = [key for key in keys if key in self._order]
        self._order = requested + [key for key in self._order if key not in requested]
        for area in self.areas: area.prioritize(keys)

    def reset_order(self):
        self._order = list(self._default)
        for area in self.areas: area.prioritize(self._default)
        self.orderChanged.emit(self.order())


class LcdDeviceShell(QWidget):
    def __init__(self, studio, legacy, prefer_levita):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(14)
        row = QHBoxLayout(); row.addWidget(QLabel('LCD-Gerät'))
        self.device = QComboBox(); self.device.setMinimumHeight(40)
        self.device.addItem('Thermalright Levita Vision', 'thermalright')
        self.device.addItem('NZXT Kraken', 'kraken'); row.addWidget(self.device, 1)
        root.addLayout(row)
        self.stack = CurrentPageStack(); self.stack.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        self.stack.addWidget(studio); self.stack.addWidget(legacy); root.addWidget(self.stack)
        self._user_selected = False
        self._prefer_levita = bool(prefer_levita)
        self.device.activated.connect(lambda _index: setattr(self, '_user_selected', True))
        legacy.thermalrightVisibilityChanged.connect(self._thermalright_visibility)
        self.device.currentIndexChanged.connect(self._changed)
        self.device.setCurrentIndex(0 if prefer_levita else 1)
        self._changed(self.device.currentIndex())

    def _changed(self, index):
        self.stack.setCurrentIndex(index); self.stack.updateGeometry(); self.updateGeometry()

    def select_device(self, key):
        """Honor an explicit editor-navigation request without applying a design."""
        index = self.device.findData(key)
        if index < 0: return False
        self._user_selected = True
        self.device.setCurrentIndex(index)
        return True

    def _thermalright_visibility(self, available):
        if not self._user_selected:
            self.device.setCurrentIndex(0 if available and self._prefer_levita else 1)
