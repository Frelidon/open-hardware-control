"""Top-aligned four-language help and explicit recognition-only metadata badges."""
import os
from pathlib import Path
import sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from PySide6.QtCore import QCoreApplication, QEvent, Qt, QUrl
from PySide6.QtGui import QPalette, QColor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLabel, QTabWidget, QVBoxLayout, QWidget
from modules.help_center.v1_0.controller import open_help, populate, show_topic
from modules.help_center.v1_0.page import build_page
from modules.dashboard_status.v1_0.model import recognition, topology_counts
from modules.dashboard_status.v1_0.cards import initialize, refresh
from modules.localization.v1_0 import HELP_TOPICS, UI_TRANSLATIONS
from modules.localization.v1_0.help_dashboard_messages import HELP_DASHBOARD_MESSAGES
from modules.ui_performance.v1_1.adaptive_views import install_content_heights

APP = QApplication.instance() or QApplication([])


class HelpHost(QWidget):
    def __init__(self):
        super().__init__(); self.ui_language = "de"
        self.tabs = QTabWidget(); QVBoxLayout(self).addWidget(self.tabs)
        for _ in range(12): self.tabs.addTab(QWidget(), "")
        self.help_page = build_page(self)
        self.help_page_index = self.tabs.addTab(self.help_page, "Hilfe")
        self.tabs.setCurrentIndex(self.help_page_index)

    def tr_static(self, source):
        own = {HELP_DASHBOARD_MESSAGES['de'][key]: value
               for key, value in HELP_DASHBOARD_MESSAGES[self.ui_language].items()}
        return own.get(source, UI_TRANSLATIONS[self.ui_language].get(source, source))

    def make_module_hero(self, _icon, title, *_args): return QLabel(title)
    def help_topics_for_language(self): return HELP_TOPICS[self.ui_language]
    def on_help_topic_selected(self, current, _previous):
        if current: show_topic(self, current.data(0, Qt.ItemDataRole.UserRole))
    def on_help_link_clicked(self, url):
        if url.scheme() == "ohc" and url.host() == "page": self.tabs.setCurrentIndex(int(url.path().strip('/')))


def dispose(host):
    host.hide(); host.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)


def test_help_topics_start_at_top_and_preserve_content_search_and_deep_links():
    host = HelpHost()
    try:
        host.resize(1440, 1000); host.show(); install_content_heights(host)
        QTest.qWait(50)
        tree = host.help_topic_tree
        assert tree.objectName() == "helpTopicTree" and tree.property("keepViewportHeight")
        assert not hasattr(tree, "_ohc_content_height")
        assert tree.height() > 340
        assert tree.visualItemRect(tree.topLevelItem(0)).top() <= 4
        open_help(host, "profiles")
        for language in ("de", "en", "es", "fr"):
            host.ui_language = language; populate(host); QTest.qWait(10)
            assert tree.currentItem().data(0, Qt.ItemDataRole.UserRole) == "profiles"
            assert tree.topLevelItemCount() == len(HELP_TOPICS[language])
            text = host.help_browser.toPlainText()
            topic = HELP_TOPICS[language]['profiles']
            assert topic['title'] in text and topic['intro'] in text
            assert all(step in text for step in topic['steps'])
            assert 'ohc://page/5' in host.help_browser.toHtml()
            host.help_search.setText("no matching help subject 999")
            assert tree.topLevelItemCount() == 0
            assert host.tr_static("Keine passende Anleitung gefunden.") in host.help_browser.toPlainText()
            open_help(host, "profiles")
            assert not host.help_search.text()
            assert tree.currentItem().data(0, Qt.ItemDataRole.UserRole) == "profiles"
            assert host.tabs.currentIndex() == host.help_page_index
        host.help_browser.anchorClicked.emit(QUrl("ohc://page/5"))
        assert host.tabs.currentIndex() == 5
        # Painting the actual cards exercises the delegate and original icons.
        assert not host.help_page.grab().isNull()
    finally: dispose(host)


def test_help_palette_change_refreshes_article_and_icons_without_losing_topic():
    host = HelpHost()
    try:
        open_help(host, "profiles")
        palette = QPalette(host.help_browser.palette())
        palette.setColor(QPalette.ColorRole.Text, QColor('#ddeeff'))
        host.help_browser.setPalette(palette); APP.processEvents(); QTest.qWait(10)
        assert "#ddeeff" in host.help_browser.toHtml()
        assert host.help_topic_tree.currentItem().data(0, Qt.ItemDataRole.UserRole) == "profiles"
    finally: dispose(host)


def test_recognition_requires_positive_reported_values_and_real_drm_address():
    values = dict(cpu_model="AMD Ryzen 7 9800X3D", cpu_topology="8 Kerne · 16 Threads",
                  gpu_model="AMD Radeon RX 9070 XT", gpu_memory="15.9 GiB VRAM", gpu_path="amdgpu · 0000:03:00.0")
    assert all(recognition(**values).values())
    assert topology_counts("8 Kerne · 16 Threads") == (8, 16)
    assert topology_counts("16 Threads") == (None, 16)
    for value in ("0 Threads", "16 Kerne · 8 Threads", "not reported", "—"):
        assert topology_counts(value) == (None, None)
    for key, value, missing in (
        ('cpu_model', 'Prozessor nicht erkannt', 'cpu_model'),
        ('cpu_topology', '0 Threads', 'cpu_topology'),
        ('gpu_model', 'Grafikkarte nicht erkannt', 'gpu_model'),
        ('gpu_memory', 'VRAM nicht gemeldet', 'gpu_memory'),
        ('gpu_memory', '0 GiB VRAM', 'gpu_memory'),
        ('gpu_path', 'Linux DRM', 'gpu_model'),
    ):
        assert not recognition(**(values | {key: value}))[missing]


def test_actual_static_cards_receive_recognition_without_touching_live_cards():
    from kraken_control import ValueCard
    host = HelpHost()
    try:
        for key in ('cpu_model', 'cpu_topology', 'gpu_model', 'gpu_memory'):
            card = ValueCard(key, "unchanged")
            card.setParent(host); setattr(host, key + '_card', card)
        host.current_cpu_temp = None; host.current_gpu_temp = None
        host.control_authority = {'gpu': 'external'}
        initialize(host, cpu_model="AMD Ryzen 7 9800X3D", cpu_topology="8 Kerne · 16 Threads",
                   gpu_model="AMD Radeon RX 9070 XT", gpu_memory="15.9 GiB VRAM", gpu_path="amdgpu · 0000:03:00.0")
        for language in ('de', 'en', 'es', 'fr'):
            host.ui_language = language; refresh(host)
            assert all(getattr(host, key + '_card').status_dot.objectName() == 'metricStatusDot'
                       for key in ('cpu_model', 'cpu_topology', 'gpu_model', 'gpu_memory'))
            assert host.tr_static('Erkannt') in host.cpu_model_card.status_dot.text()
            assert host.cpu_topology_card.value_label.text() == f"8 {host.tr_static('Kerne')} · 16 {host.tr_static('Threads')}"
            assert host.tr_static('Lokale Hardwaredaten sind verfügbar. Die Steuerfreigabe wird im jeweiligen Modul geprüft.') in host.cpu_model_card.toolTip()
            assert host.current_cpu_temp is None and host.current_gpu_temp is None
            assert host.control_authority == {'gpu': 'external'}
    finally: dispose(host)


def test_lower_hardware_rows_require_actual_inventory_and_identify_levita_honestly():
    from modules.dashboard_status.v1_0.device_rows import build, refresh as refresh_rows
    host = HelpHost()
    try:
        panel = QWidget(host); build(host, QVBoxLayout(panel))
        host.devices_ready = False; host.mainboard_channels = {'sys3': object()}
        host.openrgb_detected = True; host.openrgb_devices = []
        host.dashboard_inventory = dict(cpu_model='AMD Ryzen', cpu_topology='8 Kerne · 16 Threads',
            gpu_model='AMD Radeon RX 9070 XT', gpu_memory='15.9 GiB VRAM', gpu_path='amdgpu · 0000:03:00.0')
        refresh_rows(host, thermalright=True, kraken_connected=False)
        widgets = host.dashboard_hardware_widgets
        assert 'Thermalright Levita Vision' in widgets['cooling'][0].text()
        assert 'NZXT' not in widgets['cooling'][0].text()
        assert widgets['cooling'][1].objectName() == 'muted'
        host.dashboard_thermalright_present = True
        refresh_rows(host, thermalright=True, kraken_connected=False)
        assert widgets['cooling'][1].objectName() == 'healthGood'
        assert widgets['mainboard'][1].objectName() == 'healthGood'
        assert widgets['rgb'][1].objectName() == 'muted'
        assert widgets['gpu'][1].objectName() == 'healthGood'
        refresh_rows(host, thermalright=False, kraken_connected=False)
        assert widgets['cooling'][1].objectName() == 'muted'
        host.devices_ready = True; refresh_rows(host)
        assert 'NZXT Kraken' in widgets['cooling'][0].text()
        assert widgets['cooling'][1].objectName() == 'healthGood'
    finally: dispose(host)
