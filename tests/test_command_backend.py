import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from command_backend import needs_headless_qt_platform


def test_openrgb_gui_binary_is_forced_onto_headless_qt_platform() -> None:
    assert needs_headless_qt_platform(["/usr/bin/openrgb", "--client", "127.0.0.1:6742"])
    assert needs_headless_qt_platform(["/opt/OpenRGB.AppImage", "--server"])
    assert not needs_headless_qt_platform(["/usr/bin/python3", "openrgb_sdk.py"])
    assert not needs_headless_qt_platform(["/usr/bin/liquidctl", "status"])
