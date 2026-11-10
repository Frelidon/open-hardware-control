#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Interactive, original OHC schematic for PC case profiles."""

from __future__ import annotations

import re
from typing import Iterable

from PySide6.QtCore import QPointF, QRectF, Qt, Signal, QTimer
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from rgb_devices import RGBLayoutSlot, infer_layout_position, layout_visual_kind, reorder_layout_device_ids
from modules.rgb_studio.v1_15.led_topology import path_points
from modules.rgb_studio.v1_15.timing import RGB_TARGET_INTERVAL_MS

from .case_renderer import draw_chassis, draw_fan, draw_component, draw_gpu_component, draw_slot_label, case_aspect_ratio, slot_label_placements
from .case_geometry import fitted_slot_rect, fan_radius
from .resize_interaction import ResizeInteraction
from .case_animation import FAN_ROLES, frame as case_led_frame
from .fan_preview import draw_light_ring

RGB_DEVICE_MIME_TYPE = "application/x-open-hardware-control-rgb-device"


class PCLayoutDiagram(ResizeInteraction, QWidget):
    """Original draggable Thermaltake-style PC layout canvas."""

    slot_moved = Signal(str, float, float, str)
    slot_resized = Signal(str, float)
    device_dropped = Signal(str, str)
    slot_selected = Signal(str)
    slot_focused = Signal(str)
    fan_order_changed = Signal(str, object)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.init_resize()
        self.slots: list[RGBLayoutSlot] = []
        self.drag_slot_id = ""
        self.drag_offset = QPointF()
        self.drag_position: QPointF | None = None
        self.drag_fan_slot_id = ""
        self.drag_fan_source_index = -1
        self.drag_fan_target_index = -1
        self.selected_slot_id = ""
        self.channel_assignments = {}
        self.channel_names = {}
        self.topology_labels = {}
        self.led_paths = {}
        self.distance_links = []
        self.distance_unit = "mm"
        self.led_animations = {}
        self.animation_host = None
        self.animation_timer = QTimer(self)
        self.animation_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.animation_timer.setInterval(500)
        self.animation_timer.timeout.connect(self.tick_led_animation)
        self.case_title = "Thermaltake · Retro 360 TG"
        self.case_visual_style = "retro"
        self.case_id = "thermaltake-retro-360-tg"
        self.cooling_visual = "auto"
        self.setMinimumSize(760, 570)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setAccessibleName("Verschiebbare Thermaltake-PC-Ansicht mit RGB- und Lüfterpositionen")

    def set_case_template(self, template: object) -> None:
        self.case_id = str(getattr(template, "case_id", "thermaltake-retro-360-tg"))
        self.case_title = str(getattr(template, "title", "PC-Gehäuse"))
        self.case_visual_style = str(getattr(template, "visual_style", "classic"))
        self.setAccessibleName(f"Verschiebbare PC-Ansicht · {self.case_title}")
        self.update()

    def set_cooling_visual(self, visual: object) -> None:
        clean = str(visual)
        self.cooling_visual = clean if clean in {"auto", "aio", "air"} else "auto"
        self.update()

    def set_slots(self, slots: Iterable[RGBLayoutSlot]) -> None:
        self.slots = list(slots)
        if self.selected_slot_id and not any(
            (slot.slot_id or slot.position) == self.selected_slot_id for slot in self.slots
        ):
            self.selected_slot_id = ""
        self.update()

    def set_channel_assignments(self, assignments):
        self.channel_assignments = {str(slot): str(channel) for channel, slot in assignments.items() if channel and slot}
        self.update()

    def set_channel_names(self, names):
        self.channel_names = dict(names)
        self.update()

    def set_topology_labels(self, labels):
        self.topology_labels = dict(labels)
        self.update()

    def set_led_paths(self, paths):
        self.led_paths = dict(paths)
        self.update()

    def set_distance_links(self, links, unit="mm"):
        self.distance_links = list(links)[:128]
        self.distance_unit = "in" if str(unit) == "in" else "mm"
        self.update()

    def draw_distance_links(self, painter: QPainter) -> None:
        slots = {slot.slot_id or slot.position: slot for slot in self.slots}
        painter.save()
        for link in self.distance_links:
            source = slots.get(str(link.get("source", "")))
            target = slots.get(str(link.get("target", "")))
            if source is None or target is None:
                continue
            start, end = self.slot_center(source), self.slot_center(target)
            depth = str(link.get("kind", "distance")) == "depth"
            pen = QPen(QColor("#b78cff") if depth else QColor("#4ad8ff"), 2)
            if depth:
                pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawLine(start, end)
            direction = end - start
            length = max(1.0, (direction.x() ** 2 + direction.y() ** 2) ** .5)
            normal = QPointF(-direction.y() / length, direction.x() / length)
            midpoint = (start + end) / 2 + normal * 13
            value_mm = float(link.get("distance_mm", 0.0))
            if self.distance_unit == "in":
                label = f"{value_mm / 25.4:.2f} in"
            else:
                label = f"{value_mm:.1f} mm"
            metrics = painter.fontMetrics()
            width = metrics.horizontalAdvance(label) + 14
            badge = QRectF(midpoint.x() - width / 2, midpoint.y() - 11, width, 22)
            painter.setPen(QPen(QColor("#8066b5") if depth else QColor("#267f9e"), 1))
            painter.setBrush(QColor(5, 17, 31, 225))
            painter.drawRoundedRect(badge, 7, 7)
            painter.setPen(QColor("#eadfff") if depth else QColor("#d9f7ff"))
            painter.drawText(badge, Qt.AlignmentFlag.AlignCenter, label)
        painter.restore()

    def set_led_animations(self, specs, host):
        self.led_animations = dict(specs)
        self.animation_host = host
        if self.isVisible():
            self.animation_timer.setInterval(self.animation_interval())
            self.animation_timer.start()
        self.update()

    def animation_interval(self):
        active = bool(self.led_animations and getattr(self.animation_host, "openrgb_effect_active", False))
        return RGB_TARGET_INTERVAL_MS if active else 500

    def tick_led_animation(self):
        if not self.isVisible():
            self.animation_timer.stop()
            return
        interval = self.animation_interval()
        changed = self.animation_timer.interval() != interval
        if changed:
            self.animation_timer.setInterval(interval)
        if interval == RGB_TARGET_INTERVAL_MS or changed:
            self.update()

    def showEvent(self, event):
        super().showEvent(event)
        if self.animation_host is not None:
            self.animation_timer.setInterval(self.animation_interval())
            self.animation_timer.start()

    def hideEvent(self, event):
        self.animation_timer.stop()
        super().hideEvent(event)

    @staticmethod
    def schematic_led_points(slot, count):
        if slot.position == "ram" and slot.count == 2 and count >= 2:
            first = count // 2
            return ([(.30, .12 + .76 * i / max(1, first - 1)) for i in range(first)]
                    + [(.70, .12 + .76 * i / max(1, count - first - 1))
                       for i in range(count - first)])
        height = .18 if slot.position == "gpu" else .50
        return [(.06 + .88 * i / max(1, count - 1), height) for i in range(count)]

    def slot_animation_colors(self, slot):
        key = slot.slot_id or slot.position
        spec = self.led_animations.get(key)
        try:
            return case_led_frame(self.animation_host, spec) if spec is not None else ()
        except (ValueError, KeyError, TypeError):
            return ()  # Preview failure never changes the hardware writer.

    def draw_led_path(self, painter, slot, rect, selected, colors=()):
        key = slot.slot_id or slot.position
        data = self.led_paths.get(key)
        if data is None and not colors:
            return
        path, count = data if data is not None else (None, len(colors))
        if colors and len(colors) != count:
            return
        try:
            points = (path_points(path, count, slot.position not in {"front", "side", "rear"})
                      if path is not None else self.schematic_led_points(slot, count))
        except ValueError:
            return
        if not points:
            return
        area = rect.adjusted(12, 12, -12, -12)
        if area.width() <= 0 or area.height() <= 0:
            return
        visible = list(range(0, len(points), max(1, len(points) // 48)))
        if visible[-1] != len(points) - 1:
            visible.append(len(points) - 1)
        mapped = [QPointF(area.left() + area.width() * points[i][0],
                          area.top() + area.height() * points[i][1]) for i in visible]
        painter.save()
        painter.setPen(QPen(QColor(80, 215, 255, 195 if selected else 85), 1.5))
        if path is not None and path["kind"] == "line":
            for first, second in zip(mapped, mapped[1:]):
                painter.drawLine(first, second)
        painter.setPen(Qt.PenStyle.NoPen)
        for index, point in zip(visible, mapped):
            painter.setBrush(QColor("#" + colors[index]) if colors else QColor(118, 207, 255, 245 if selected else 125))
            painter.drawEllipse(point, 3.2 if colors else 2.4 if selected else 1.8,
                                3.2 if colors else 2.4 if selected else 1.8)
        if not colors:
            for point, color in ((mapped[0], QColor("#37efa7")),
                                 (mapped[-1], QColor("#ffad5b"))):
                painter.setBrush(color)
                painter.drawEllipse(point, 5 if selected else 3.5, 5 if selected else 3.5)
        painter.restore()

    @staticmethod
    def _animation_color(colors, index, count, fallback):
        if not colors:
            return fallback
        sample = min(len(colors) - 1, int((index + .5) * len(colors) / max(1, count)))
        return QColor("#" + colors[sample])

    def draw_strip_visual(self, painter, rect, colors, accent):
        line = rect.adjusted(8, rect.height() * .34, -8, -rect.height() * .34)
        painter.save()
        painter.setPen(QPen(QColor("#40586b"), 1))
        painter.setBrush(QColor("#0b141d"))
        painter.drawRoundedRect(line, line.height() / 2, line.height() / 2)
        segments = min(48, max(1, len(colors)))
        for index in range(segments):
            color = self._animation_color(colors, index, segments, accent)
            left = line.left() + line.width() * index / segments
            right = line.left() + line.width() * (index + 1) / segments
            painter.setPen(QPen(color, max(2.0, line.height() * .55)))
            painter.drawLine(QPointF(left, line.center().y()), QPointF(right, line.center().y()))
        painter.restore()

    def draw_gpu_edge_lighting(self, painter, rect, colors, accent):
        """Overlay the cooler's light guide without replacing its fan view."""

        left = rect.left() + max(10.0, rect.width() * .045)
        right = rect.right() - max(10.0, rect.width() * .045)
        y = rect.top() + max(7.0, rect.height() * .10)
        segments = min(64, max(1, len(colors)))
        painter.save()
        painter.setPen(QPen(QColor(4, 10, 16, 230), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(left, y), QPointF(right, y))
        for index in range(segments):
            color = self._animation_color(colors, index, segments, accent)
            first = left + (right - left) * index / segments
            second = left + (right - left) * (index + 1) / segments
            glow = QColor(color)
            glow.setAlpha(70)
            painter.setPen(QPen(glow, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
            painter.drawLine(QPointF(first, y), QPointF(second, y))
            painter.setPen(QPen(color, 3.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
            painter.drawLine(QPointF(first, y), QPointF(second, y))
        painter.restore()

    def draw_ring_visual(self, painter, rect, count, colors, accent, path=None, segmented=False):
        horizontal = rect.width() >= rect.height()
        centers = self._fan_centers(rect, count, horizontal)
        radius = fan_radius(rect, count, horizontal)
        painter.save()
        painter.setBrush(QColor("#08121b"))
        for index, center in enumerate(centers):
            color = self._animation_color(colors, index, len(centers), accent)
            painter.setPen(QPen(color, max(3.0, radius * .18)))
            painter.drawEllipse(center, radius * .72, radius * .72)
            if segmented:
                draw_light_ring(painter, center, radius * .91, colors, index, count, path)
        painter.restore()

    def set_selected_slot(self, slot_id: str) -> None:
        self.selected_slot_id = str(slot_id)
        self.update()

    def canvas_area(self) -> QRectF:
        width, height = max(180, self.width() - 280), max(180, self.height() - 52)
        aspect = case_aspect_ratio(self.case_id)
        width = min(width, height * aspect)
        height = min(height, width / aspect)
        return QRectF((self.width() - width) / 2, (self.height() - height) / 2, width, height)

    def slot_center(self, slot: RGBLayoutSlot) -> QPointF:
        return self.slot_rect(slot).center()

    def raw_slot_center(self, slot: RGBLayoutSlot) -> QPointF:
        area = self.canvas_area()
        if slot.slot_id == self.drag_slot_id and self.drag_position is not None:
            return QPointF(
                area.left() + area.width() * self.drag_position.x(),
                area.top() + area.height() * self.drag_position.y(),
            )
        return QPointF(area.left() + area.width() * slot.x, area.top() + area.height() * slot.y)

    def slot_rect(self, slot: RGBLayoutSlot) -> QRectF:
        scale = self.resize_scale if (slot.slot_id or slot.position) == self.resize_slot_id else slot.scale
        return fitted_slot_rect(slot, self.canvas_area(), point=self.raw_slot_center(slot), scale=scale)

    def slot_at(self, point: QPointF) -> RGBLayoutSlot | None:
        for slot in reversed(self.slots):
            if self.slot_rect(slot).adjusted(-5, -5, 5, 5).contains(point):
                return slot
        return None

    def label_rectangles(self):
        return slot_label_placements(QRectF(self.rect()), self.canvas_area(),
                                     [self.slot_rect(slot) for slot in self.slots],
                                     height=61, side_first=True)

    def label_at(self, point):
        return next((slot for slot, badge in zip(self.slots, self.label_rectangles())
                     if badge is not None and badge.contains(point)), None)

    def normalized_point(self, point: QPointF) -> QPointF:
        area = self.canvas_area()
        return QPointF(
            max(0.04, min(0.96, (point.x() - area.left()) / max(1.0, area.width()))),
            max(0.04, min(0.96, (point.y() - area.top()) / max(1.0, area.height()))),
        )

    @staticmethod
    def _fan_centers(rect: QRectF, count: int, horizontal: bool) -> list[QPointF]:
        amount = max(1, count)
        if horizontal:
            step = rect.width() / amount
            return [QPointF(rect.left() + step * (index + 0.5), rect.center().y()) for index in range(amount)]
        step = rect.height() / amount
        return [QPointF(rect.center().x(), rect.top() + step * (index + 0.5)) for index in range(amount)]

    @staticmethod
    def _draw_fan(
        painter: QPainter,
        center: QPointF,
        color: QColor,
        channel_label: str = "",
        highlighted: bool = False,
        radius: float = 24,
    ) -> None:
        draw_fan(painter, center, color, channel_label, highlighted, radius)

    @staticmethod
    def _kraken_channel_label(device_id: str) -> str:
        match = re.fullmatch(r"nzxt:led([1-9][0-9]*)", str(device_id))
        return match.group(1) if match else ""

    def fan_device_ids(self, slot: RGBLayoutSlot) -> tuple[str, ...]:
        if slot.group_id != "kraken-radiator" or slot.position != "top":
            return ()
        if len(slot.device_ids) != slot.count:
            return ()
        ordered = tuple(device_id for device_id in slot.device_ids if self._kraken_channel_label(device_id))
        return ordered if len(ordered) == slot.count else ()

    def fan_index_at(self, slot: RGBLayoutSlot, point: QPointF) -> int | None:
        device_ids = self.fan_device_ids(slot)
        if not device_ids:
            return None
        centers = self._fan_centers(self.slot_rect(slot), slot.count, True)
        return next(
            (
                index for index, center in enumerate(centers)
                if (point - center).manhattanLength() <= fan_radius(self.slot_rect(slot), slot.count, True) * 1.2
            ),
            None,
        )

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt API
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        area = self.canvas_area()
        glass = draw_chassis(painter, area, self.case_id)
        painter.setPen(QColor("#14232d"))
        painter.drawText(area.adjusted(16, 8, -80, -8), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, self.case_title)

        cooling_visual = self.cooling_visual
        if cooling_visual == "auto":
            cooling_visual = "aio" if any(slot.position == "pump" for slot in self.slots) else "air"
        if cooling_visual == "air":
            tower = QRectF(glass.center().x() - 46, glass.center().y() - 72, 92, 144)
            painter.setPen(QPen(QColor("#8bb8ff"), 2))
            painter.setBrush(QColor(63, 91, 116, 145))
            painter.drawRoundedRect(tower, 9, 9)
            for offset in range(12, 84, 12):
                painter.drawLine(tower.left() + 8, tower.top() + offset, tower.right() - 8, tower.top() + offset)
            self._draw_fan(painter, tower.center(), QColor("#8bb8ff"))
        elif cooling_visual == "aio":
            pump = next((slot for slot in self.slots if slot.position == "pump"), None)
            radiator = next((slot for position in ("top", "side", "front") for slot in self.slots if slot.position == position), None)
            if pump is not None and radiator is not None:
                start = self.slot_center(pump)
                end = self.slot_center(radiator)
                painter.setPen(QPen(QColor("#68c8e8"), 4))
                for offset in (-7, 7):
                    tube = QPainterPath(QPointF(start.x(), start.y() + offset))
                    tube.cubicTo(
                        QPointF(start.x() + 80, start.y() + offset),
                        QPointF(end.x() - 80, end.y() + offset),
                        QPointF(end.x(), end.y() + offset),
                    )
                    painter.drawPath(tube)

        for slot in self.slots:
            rect = self.slot_rect(slot)
            selected = (slot.slot_id or slot.position) in {self.drag_slot_id, self.selected_slot_id}
            accent = QColor("#42d8ff") if slot.airflow == "intake" else QColor("#ff9a52") if slot.airflow == "exhaust" else QColor("#8bb8ff")
            painter.setPen(QPen(accent.lighter(145) if selected else accent, 3 if selected else 2))
            painter.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 28 if not selected else 52))
            painter.drawRoundedRect(rect, 10, 10)
            visual_kind = layout_visual_kind(slot)
            colors = self.slot_animation_colors(slot)
            path_data = self.led_paths.get(slot.slot_id or slot.position)
            fan_path = path_data[0] if path_data else None
            if visual_kind == "fans":
                horizontal = rect.width() >= rect.height()
                ordered_devices = self.fan_device_ids(slot)
                for index, center in enumerate(self._fan_centers(rect, slot.count, horizontal)):
                    label = self._kraken_channel_label(ordered_devices[index]) if ordered_devices else ""
                    highlighted = bool(
                        (slot.slot_id or slot.position) == self.drag_fan_slot_id
                        and index == self.drag_fan_target_index
                    )
                    fan_color = self._animation_color(colors, index, slot.count, accent)
                    self._draw_fan(painter, center, fan_color, label, highlighted, fan_radius(rect, slot.count, horizontal))
                    if slot.position in FAN_ROLES:
                        draw_light_ring(painter, center, fan_radius(rect, slot.count, horizontal),
                                        colors, index, slot.count, fan_path)
                if ordered_devices:
                    painter.setPen(QColor("#93a9bb"))
                    painter.drawText(
                        rect.adjusted(5, 1, -5, -3),
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                        "← HECK",
                    )
                    painter.drawText(
                        rect.adjusted(5, 1, -5, -3),
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
                        "FRONT →",
                    )
                spec = self.led_animations.get(slot.slot_id or slot.position, {})
                if slot.position == "gpu" and spec.get("gpu_lighting") in {"edge-strip", "mixed", "indirect"}:
                    self.draw_gpu_edge_lighting(painter, rect, colors, accent)
            elif visual_kind == "strip":
                self.draw_strip_visual(painter, rect, colors, accent)
            elif visual_kind == "ring":
                self.draw_ring_visual(painter, rect, slot.count, colors, accent, fan_path,
                                      segmented=slot.position in FAN_ROLES)
            else:
                if slot.position == "gpu":
                    draw_gpu_component(painter, rect, slot.name, slot.gpu_visual, colors, accent)
                else:
                    draw_component(painter, rect, slot.position, accent)
            # Fan/ring/strip/GPU drawings already own their light geometry.
            # Overlaying the generic linear LED path created the unwanted long
            # bar across otherwise separate fans.
            if visual_kind == "component" and slot.position != "gpu":
                self.draw_led_path(painter, slot, rect, selected, colors)
            if slot.airflow != "component":
                painter.setPen(accent)
                airflow = "IN →" if slot.airflow == "intake" else "← OUT"
                painter.drawText(rect.adjusted(4, 3, -4, -3), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight, airflow)

        self.draw_distance_links(painter)

        rectangles = [self.slot_rect(slot) for slot in self.slots]
        badges = self.label_rectangles()
        for slot, rect, badge in zip(self.slots, rectangles, badges):
            channel = self.channel_assignments.get(slot.slot_id or slot.position, "")
            pwm = self.channel_names.get(channel, channel)
            connection = " · ".join(value for value in (pwm, slot.connection) if value)
            metadata = self.topology_labels.get(slot.slot_id or slot.position, ("LEDs: —", f"PWM: {pwm or '—'}", ""))
            draw_slot_label(painter, rect, slot.name, connection,
                            (slot.slot_id or slot.position) == self.selected_slot_id, badge=badge, metadata=metadata[:3])
        self.draw_resize_handle(painter)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt API
        label = self.label_at(event.position()) if event.button() == Qt.MouseButton.LeftButton else None
        if label is not None:
            self.selected_slot_id = label.slot_id or label.position
            self.slot_focused.emit(self.selected_slot_id)
            self.slot_selected.emit(self.selected_slot_id)
            self.update()
            event.accept()
            return
        if self.begin_resize(event):
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return
        slot = self.slot_at(event.position())
        if slot is None:
            return
        fan_index = self.fan_index_at(slot, event.position())
        if fan_index is not None:
            self.drag_fan_slot_id = slot.slot_id or slot.position
            self.drag_fan_source_index = fan_index
            self.drag_fan_target_index = fan_index
            self.selected_slot_id = self.drag_fan_slot_id
            self.slot_focused.emit(self.selected_slot_id)
            self.update()
            event.accept()
            return
        self.drag_slot_id = slot.slot_id or slot.position
        self.selected_slot_id = self.drag_slot_id
        self.slot_focused.emit(self.selected_slot_id)
        center = self.slot_center(slot)
        self.drag_offset = event.position() - center
        self.drag_position = QPointF(slot.x, slot.y)
        self.update()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt API
        if self.update_resize(event):
            return
        if self.drag_fan_slot_id:
            slot = next(
                (item for item in self.slots if (item.slot_id or item.position) == self.drag_fan_slot_id),
                None,
            )
            if slot is not None:
                centers = self._fan_centers(self.slot_rect(slot), slot.count, True)
                self.drag_fan_target_index = min(
                    range(len(centers)),
                    key=lambda index: abs(event.position().x() - centers[index].x()),
                )
                self.setToolTip("Kraken-Kanal auf den gewünschten Platz ziehen · links = Heck · rechts = Front")
                self.update()
            event.accept()
            return
        if self.drag_slot_id:
            self.drag_position = self.normalized_point(event.position() - self.drag_offset)
            self.update()
            event.accept()
            return
        slot = self.slot_at(event.position())
        if slot is not None:
            assignment = f"{len(slot.device_ids)} Gerät(e) zugeordnet" if slot.device_ids else "noch kein RGB-Gerät zugeordnet"
            extra = "\nNummerierten Lüfter ziehen = Kraken-Kanal umordnen" if self.fan_device_ids(slot) else ""
            self.setToolTip(
                f"{slot.name}\n{slot.connection}\n{assignment}\n"
                f"Ziehen = Position ändern · Doppelklick = Geräte auswählen{extra}"
            )
            metadata = self.topology_labels.get(slot.slot_id or slot.position)
            if metadata: self.setToolTip(self.toolTip() + "\n" + "\n".join(value for value in metadata if value))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt API
        if self.finish_resize(event):
            return
        if event.button() == Qt.MouseButton.LeftButton and self.drag_fan_slot_id:
            slot = next(
                (item for item in self.slots if (item.slot_id or item.position) == self.drag_fan_slot_id),
                None,
            )
            slot_id = self.drag_fan_slot_id
            source_index = self.drag_fan_source_index
            target_index = self.drag_fan_target_index
            self.drag_fan_slot_id = ""
            self.drag_fan_source_index = -1
            self.drag_fan_target_index = -1
            if slot is not None:
                ordered = reorder_layout_device_ids(slot.device_ids, source_index, target_index)
                if ordered != slot.device_ids:
                    self.fan_order_changed.emit(slot_id, ordered)
            self.update()
            event.accept()
            return
        if event.button() != Qt.MouseButton.LeftButton or not self.drag_slot_id:
            return
        slot = next((item for item in self.slots if (item.slot_id or item.position) == self.drag_slot_id), None)
        position = self.drag_position
        slot_id = self.drag_slot_id
        self.drag_slot_id = ""
        self.drag_position = None
        if slot is not None and position is not None:
            inferred = infer_layout_position(slot, position.x(), position.y())
            self.slot_moved.emit(slot_id, position.x(), position.y(), inferred)
        self.update()
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt API
        slot = self.slot_at(event.position()) or self.label_at(event.position())
        if slot is not None:
            self.slot_selected.emit(slot.slot_id or slot.position)
            event.accept()

    def dragEnterEvent(self, event) -> None:  # noqa: N802 - Qt API
        if event.mimeData().hasFormat(RGB_DEVICE_MIME_TYPE):
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # noqa: N802 - Qt API
        slot = self.slot_at(event.position())
        if slot is None:
            return
        try:
            device_id = bytes(event.mimeData().data(RGB_DEVICE_MIME_TYPE)).decode("utf-8")
        except (UnicodeDecodeError, ValueError):
            return
        if device_id:
            self.device_dropped.emit(device_id, slot.slot_id or slot.position)
            event.acceptProposedAction()


class CoolingLayoutDiagram(PCLayoutDiagram):
    """Shared original case renderer, channel badges and hit targets."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(620, 440)
        self.setAccessibleName("Gehäuseansicht zur Zuordnung von PWM-Lüfterkanälen")
