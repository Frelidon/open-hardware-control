"""Real sensor drag/drop, reversible selection and reused live reading cards."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from PySide6.QtCore import QMimeData, QPointF, QSettings, Qt
from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
import pytest
from localization_catalog import UI_TRANSLATIONS
from modules.temperature_history.v1_2.panel import TemperatureRecordingMixin
from modules.temperature_history.v1_2.selection import MIME, sensor_keys, sensor_mime

APP=QApplication.instance() or QApplication([])


class Recorder(QWidget,TemperatureRecordingMixin):
    def __init__(self,path):
        super().__init__();self.ui_language='de';self.temperature_unit='c'
        self.settings=QSettings(str(path),QSettings.Format.IniFormat)
        self.format_temperature=lambda value:'—' if value is None else str(value)
        self.initialize_temperature_recording()
        layout=QVBoxLayout(self);layout.addWidget(self.make_temperature_recording_page())
    def tr_static(self,text):return UI_TRANSLATIONS[self.ui_language].get(text,text)


@pytest.fixture
def recorder(tmp_path):
    h=Recorder(tmp_path/'settings.ini');h.resize(1400,950);h.show();APP.processEvents()
    h.temperature_detail_user_configured=True;h.temperature_detail_selected={'cpu'}
    h.temperature_sensor_catalog['ram:test']=('DDR5','memory','fixture hwmon')
    h.temperature_history.append({'cpu':40,'gpu':50,'ram:test':35},timestamp=1000)
    h.temperature_history.append({'cpu':45,'gpu':55,'ram:test':38},timestamp=1001)
    h.refresh_temperature_sensor_tree()
    yield h
    h.close();h.deleteLater();APP.processEvents()


def drop(view,mime):
    event=QDropEvent(QPointF(25,25),Qt.DropAction.CopyAction,mime,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier)
    view.dropEvent(event);return event.isAccepted()


def test_drag_available_to_readings_and_back_preserves_identifiers_and_history(recorder):
    h=recorder;before=h.temperature_history.samples
    assert drop(h.temperature_readings,sensor_mime(['gpu','ram:test','not-a-sensor']))
    assert h.temperature_detail_selected=={'cpu','gpu','ram:test'}
    assert set(h.temperature_readings.rows)=={'cpu','gpu','ram:test'}
    assert drop(h.temperature_sensor_tree,sensor_mime(['gpu']))
    assert h.temperature_detail_selected=={'cpu','ram:test'}
    assert h.temperature_history.samples==before
    assert set(__import__('json').loads(h.settings.value('temperature_history/detail_selected')))=={'cpu','ram:test'}


def test_reading_cards_reuse_widgets_and_follow_units_language_and_sample_window(recorder):
    h=recorder;row=h.temperature_readings.rows['cpu'];card=row[1]
    assert [label.text() for label in row[6]]==['45.0 °C','40.0 °C','45.0 °C']
    h.temperature_unit='f';h.ui_language='fr';h.refresh_temperature_detail_view()
    row=h.temperature_readings.rows['cpu']
    assert row[1] is card
    assert [label.text() for label in row[6]]==['113.0 °F','104.0 °F','113.0 °F']
    assert row[5][0].text()==UI_TRANSLATIONS['fr']['Aktuell']
    assert row[2].pixmap() is not None
    assert h.temperature_statistics_table.isHidden()


def test_filter_does_not_remove_chosen_sensors_and_explicit_empty_selection_survives_restart(recorder):
    h=recorder;h.temperature_detail_group_combo.setCurrentIndex(h.temperature_detail_group_combo.findData('memory'))
    assert set(h.temperature_readings.rows)=={'cpu'}
    h.choose_temperature_sensors(['cpu'],False)
    assert h.temperature_detail_selected==set() and not h.temperature_readings.rows
    h.settings.sync();other=Recorder(h.settings.fileName())
    assert other.temperature_detail_selected==set()
    other.close();other.deleteLater();APP.processEvents()


@pytest.mark.parametrize('data',[b'{}',b'null',b'[1,{}]',b'bad-json',b'x'*20_001])
def test_untrusted_drag_payload_cannot_add_unreported_sensor(data):
    mime=QMimeData();mime.setData(MIME,data)
    assert sensor_keys(mime,{'cpu'})==[]


@pytest.mark.parametrize('size',[(1400,950),(1100,800)])
def test_split_panels_keep_add_button_and_readings_inside_their_layout(recorder,size):
    h=recorder;h.resize(*size);APP.processEvents()
    tree=h.temperature_sensor_tree;readings=h.temperature_readings
    assert tree.property('keepViewportHeight') and readings.property('keepViewportHeight')
    assert tree.parentWidget().rect().contains(tree.geometry())
    assert readings.parentWidget().rect().contains(readings.geometry())
