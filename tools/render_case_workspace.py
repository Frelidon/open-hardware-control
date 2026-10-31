#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Hardware-free visual QA of every original case illustration."""

import os
from pathlib import Path
import sys
from dataclasses import replace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtWidgets import QApplication
from modules.pc_case_profiles.v1_5 import CASE_TEMPLATES, PCLayoutDiagram
from modules.pc_case_profiles.v1_5.case_geometry import arrange_case_slots
from rgb_devices import RGBLayoutSlot, RGB_LAYOUT_DEFAULT_POINTS, flori_rgb_layout_profile


def main():
    destination = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ohc-case-render-3429130")
    destination.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    gallery = QImage(2400, 2400, QImage.Format.Format_RGB32)
    gallery.fill(QColor("#070e15"))
    painter = QPainter(gallery)
    for number, template in enumerate(CASE_TEMPLATES):
        diagram = PCLayoutDiagram()
        diagram.resize(960, 720)
        diagram.set_case_template(template)
        _, original = flori_rgb_layout_profile("thermalright")
        slots = [s for s in original if s.airflow == "component"]
        for position, count in template.fan_layout:
            x, y = RGB_LAYOUT_DEFAULT_POINTS[position][0]
            slots.append(RGBLayoutSlot(position, f"{position.upper()} · {count}x", count,
                                       "fans", "", (), f"fans-{position}", x, y,
                                       "exhaust" if position in {"top", "rear"} else "intake", 120))
        diagram.set_slots(arrange_case_slots(slots, template.case_id))
        rendered_ids = [slot.slot_id or slot.position for slot in diagram.slots]
        if len(rendered_ids) >= 2:
            diagram.set_distance_links([{
                "source": rendered_ids[0], "target": rendered_ids[1],
                "kind": "depth", "distance_mm": 118.0,
            }], "mm")
        diagram.set_channel_assignments({"hwmon:test:pwm4": "fans-front"})
        diagram.set_cooling_visual("aio")
        image = QImage(diagram.size(), QImage.Format.Format_RGB32)
        image.fill(QColor("#070e15"))
        diagram.render(image)
        if not image.save(str(destination / f"{template.case_id}.png")):
            raise RuntimeError("render save failed")
        painter.drawImage((number % 5) * 480, (number // 5) * 400,
                          image.scaled(480, 360, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        diagram.close()
    painter.end()
    gallery.save(str(destination / "case-gallery.png"))
    print(destination / "case-gallery.png")
    app.processEvents()


if __name__ == "__main__":
    main()
