#!/usr/bin/env python3
"""Render the real GPU cockpit with deterministic LACT-shaped demo data."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/images/rendering-evidence/gpu-cockpit-3.4.29.130.png"
temporary = tempfile.TemporaryDirectory(prefix="ohc-gpu-render-")
runtime = Path(temporary.name)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["XDG_CONFIG_HOME"] = str(runtime / "config")
os.environ["XDG_STATE_HOME"] = str(runtime / "state")
os.environ["OHC_DISABLE_HARDWARE_IO"] = "1"
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402
import kraken_control as application  # noqa: E402


class DemoLact:
    gpu_id = "1002:7550-1DA2:E489-0000:03:00.0"
    profile = {
        "power_cap": 330.0,
        "performance_level": "auto",
        "max_memory_clock": 1259,
        "gpu_clock_offsets": {"0": 0},
        "fan_control_enabled": True,
        "fan_control_settings": {
            "mode": "curve",
            "curve": {"35": .30, "50": .38, "65": .52, "78": .72, "90": 1.0},
        },
    }

    def devices(self):
        return [{
            "id": self.gpu_id,
            "name": "Sapphire Radeon RX 9070 XT NITRO+",
            "device_type": "Dedicated",
        }]

    def stats(self, _gpu_id):
        return {
            "busy_percent": 98,
            "temps": {"edge": {"current": 52, "crit": 110}, "junction": {"current": 66}},
            "fan": {"speed_current": 1240, "pwm_current": 112, "pwm_max": 255,
                    "temperature_range": [25, 100]},
            "power": {"average": 304, "cap_current": 330, "cap_min": 231,
                      "cap_default": 330, "cap_max": 374},
            "clockspeed": {"gpu_clockspeed": 2900, "target_gpu_clockspeed": 3000},
            "vram": {"total": 17179869184, "used": 4294967296},
        }

    def clocks(self, _gpu_id):
        return {"table": {"type": "amd", "value": {"kind": "rdna", "data": {
            "current_sclk_range": {"min": None, "max": None},
            "sclk_offset": 0,
            "current_mclk_range": {"min": 97, "max": 1259},
            "od_range": {"sclk": None, "sclk_offset": {"min": -500, "max": 1000},
                         "mclk": {"min": 97, "max": 1500}},
        }}}}

    def config(self, _gpu_id):
        return dict(self.profile)

    def overdrive_enabled(self):
        return True

    def request(self, command, _arguments=None):
        if command == "device_info":
            return {"Modell": "Sapphire Radeon RX 9070 XT NITRO+", "VRAM": "16 GiB",
                    "PCIe": "0000:03:00.0", "Treiber": "amdgpu"}
        return {}

    def pending(self, _action):
        return None


def main() -> int:
    app = QApplication.instance() or QApplication([])
    settings = QSettings(application.ORG_NAME, application.APP_NAME)
    settings.setValue("design/theme", "dark")
    settings.setValue("design/accent", "#3478ff")
    settings.setValue("display/ui_scale", 100)
    settings.setValue("setup/completed", True)
    settings.sync()
    application.KrakenControl.check_dependencies = lambda self: ["render-no-hardware"]
    window = application.KrakenControl()
    page = window.gpu_control_page
    page.client = DemoLact()
    page.refresh_ownership = lambda: True
    window.resize(1900, 1120)
    window.connection_label.setText("● System bereit")
    window.connection_label.setObjectName("connectionOk")
    window.footer_status.setText("GPU-Cockpit · sichere Demo-Daten")
    window.navigation.setCurrentItem(window.navigation_items["gpu"])
    window.tabs.setCurrentIndex(window.gpu_control_page_index)
    page.refresh()
    window.show()
    for _ in range(10):
        app.processEvents()
    page.verticalScrollBar().setValue(0)
    for _ in range(3):
        app.processEvents()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image = window.grab()
    if image.isNull() or not image.save(str(OUTPUT), "PNG"):
        raise SystemExit("GPU cockpit rendering could not be saved")
    page.shutdown()
    window.hide()
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
