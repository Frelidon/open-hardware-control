"""Real pointer gestures and filtered model cards, with no hardware I/O."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from unittest.mock import patch
import pytest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QTreeWidgetItem, QWidget
from modules.navigation_settings.v1_0.sidebar import NavigationTree
from modules.hardware_checker.v1_0.device_catalog import DEVICES, safe_link
from modules.hardware_checker.v1_0.supported_devices import SupportedDevicesPage
from localization_catalog import UI_TRANSLATIONS

APP = QApplication.instance() or QApplication([])


@pytest.mark.parametrize("branch", ["LCD", "Cooling", "Hardware Check"])
def test_reflow_waits_until_pointer_selection_has_finished(branch):
    tree = NavigationTree(); tree.setHeaderHidden(True); tree.resize(320, 700)
    parent = QTreeWidgetItem([branch]); tree.addTopLevelItem(parent)
    parent.addChildren([QTreeWidgetItem([str(i)]) for i in range(2)])
    for caption in ("RGB", "Profiles", "Settings", "About", "Log"):
        tree.addTopLevelItem(QTreeWidgetItem([caption]))
    tree.setCurrentItem(parent.child(1)); parent.setExpanded(True)
    tree.show(); APP.processEvents(); opened = []
    def request(item, previous):
        opened.append(item.text(0))
        parent.setExpanded(item is parent or item.parent() is parent)
    tree.pageRequested.connect(request)
    target = tree.topLevelItem(3); pos = tree.visualItemRect(target).center()
    QTest.mousePress(tree.viewport(), Qt.MouseButton.LeftButton, pos=pos)
    assert opened == [] and parent.isExpanded()
    QTest.mouseMove(tree.viewport(), pos + QPoint(0, 1))
    QTest.mouseRelease(tree.viewport(), Qt.MouseButton.LeftButton, pos=pos + QPoint(0, 1))
    assert opened == ["Settings"] and tree.currentItem() is target and not parent.isExpanded()
    QTest.keyClick(tree, Qt.Key.Key_Down)
    assert opened == ["Settings", "About"]
    tree.setCurrentItem(parent.child(0))
    assert parent.isExpanded() and opened[-1] == "0"
    tree.close(); tree.deleteLater(); APP.processEvents()


@pytest.mark.parametrize("language", ["de", "en", "es", "fr"])
def test_catalog_category_vendor_search_language_and_missing_product_buttons(language):
    host = QWidget(); page = SupportedDevicesPage(host, translate=lambda s: UI_TRANSLATIONS[language].get(s, s))
    page.resize(1000, 700); page.show(); APP.processEvents()
    assert len(page.cards) == len(DEVICES) == 41
    assert page.category.currentData() == "gpu"
    assert [page.vendor.itemData(i) for i in range(1, page.vendor.count())] == ["AMD", "NVIDIA"]
    page.vendor.setCurrentIndex(page.vendor.findData("NVIDIA"))
    visible = [c for c in page.cards if not c.widget.isHidden()]
    assert len(visible) == 16 and all(c.device.vendor == "NVIDIA" for c in visible)
    page.search.setText("5090")
    assert [c.device.name for c in page.cards if not c.widget.isHidden()] == ["GeForce RTX 5090"]
    page.refresh_language()
    assert page.vendor.currentData() == "NVIDIA" and page.search.text() == "5090"
    page.category.setCurrentIndex(page.category.findData("rgb")); page.search.clear()
    airgoo = next(c for c in page.cards if c.device.key == "airgoo-argb")
    assert [caption for button, caption in airgoo.links] == ["Herstellerseite"]
    assert not airgoo.widget.isHidden()
    APP.processEvents()
    assert airgoo.widget.height() <= airgoo.widget.sizeHint().height() + 2
    for card in page.cards:
        assert bool(card.device.product_url) == any(caption == "Produktseite" for _, caption in card.links)
        for button, caption in card.links:
            assert button.text() == UI_TRANSLATIONS[language][caption]
            assert safe_link(button.toolTip())
            with patch("modules.hardware_checker.v1_0.supported_devices.QDesktopServices.openUrl") as open_url:
                button.click()
                assert open_url.call_args.args[0].toString() == button.toolTip()
    page.search.setText("no such device"); assert page.empty.isVisible()
    assert not any(not c.widget.isHidden() for c in page.cards)
    page.close(); page.deleteLater(); host.deleteLater(); APP.processEvents()


@pytest.mark.parametrize("url", ["", "javascript:alert(1)", "/relative", "https://user:password@example.org/", "file:///tmp/test"])
def test_catalog_does_not_create_invalid_link_targets(url):
    assert not safe_link(url)
