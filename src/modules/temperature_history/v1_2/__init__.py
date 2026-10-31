"""Interactive multi-sensor temperature history 1.2."""

from importlib import import_module

_EXPORTS = {
    'TemperatureHistoryChart': 'chart', 'HistorySample': 'model', 'TemperatureHistoryBuffer': 'model',
    'TemperatureRecordingMixin': 'panel', 'temperature_report_rows': 'report',
    'write_temperature_report': 'report', 'TemperatureReportDialog': 'report_dialog',
    'TemperatureSensorReading': 'sensors', 'read_linux_temperature_sensors': 'sensors',
    'TemperatureGauge': 'gauge',
}


def __getattr__(name):
    if name not in _EXPORTS: raise AttributeError(name)
    value = getattr(import_module(f'{__name__}.{_EXPORTS[name]}'), name)
    globals()[name] = value
    return value

__all__ = [
    "HistorySample",
    "TemperatureHistoryBuffer",
    "TemperatureHistoryChart",
    "TemperatureGauge",
    "TemperatureRecordingMixin",
    "TemperatureReportDialog",
    "TemperatureSensorReading",
    "read_linux_temperature_sensors",
    "temperature_report_rows",
    "write_temperature_report",
]
