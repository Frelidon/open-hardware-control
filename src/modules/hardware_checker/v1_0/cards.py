# SPDX-License-Identifier: GPL-3.0-or-later
"""Original OHC hardware cards, composed alongside current Ubuntu fix tools."""
from __future__ import annotations
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from .model import Assessment, assess_memory, assess_nvme_link, assess_pcie_link
CARD_STATE = {"pass": ("✓", "healthGood"), "warning": ("!", "warningText"),
              "fail": ("✕", "warningText"), "unknown": ("?", "muted"), "info": ("i", "infoText")}


class HardwareIllustration(QWidget):
    """Small original vector glyph; never manufacturer artwork."""

    def __init__(self, kind: str, parent=None) -> None:
        super().__init__(parent)
        self.kind = kind
        self.setFixedSize(104, 76)
        self.setAccessibleName(kind)

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = QRectF(5, 6, 94, 64)
        accent = QColor("#45d8ff")
        painter.setPen(QPen(QColor("#58758a"), 2))
        painter.setBrush(QColor("#102431"))
        if self.kind == "cpu":
            chip = area.adjusted(20, 5, -20, -5)
            painter.drawRoundedRect(chip, 8, 8)
            painter.setPen(QPen(accent, 2))
            painter.drawRoundedRect(chip.adjusted(10, 10, -10, -10), 4, 4)
            painter.setPen(QPen(QColor("#7195a8"), 1))
            for offset in range(10, 55, 9):
                painter.drawLine(area.left() + offset, chip.top() - 5, area.left() + offset, chip.top())
                painter.drawLine(area.left() + offset, chip.bottom(), area.left() + offset, chip.bottom() + 5)
        elif self.kind == "mainboard":
            painter.drawRoundedRect(area, 7, 7)
            painter.setPen(QPen(accent, 2))
            painter.drawRoundedRect(area.adjusted(12, 10, -52, -30), 3, 3)
            for index in range(4):
                painter.drawLine(area.left() + 48, area.top() + 12 + index * 10, area.right() - 9, area.top() + 12 + index * 10)
        elif self.kind == "socket":
            painter.drawRoundedRect(area.adjusted(16, 2, -16, -2), 8, 8)
            painter.setPen(QPen(accent, 2))
            painter.drawRoundedRect(area.adjusted(28, 14, -28, -14), 4, 4)
        elif self.kind == "gpu":
            body = area.adjusted(0, 12, 0, -8)
            painter.drawRoundedRect(body, 7, 7)
            for x in (.24, .50, .76):
                center = QPointF(body.left() + body.width() * x, body.center().y())
                painter.setPen(QPen(accent, 2))
                painter.drawEllipse(center, 13, 13)
                painter.drawEllipse(center, 4, 4)
            painter.drawLine(body.left() + 7, body.top() + 3, body.right() - 7, body.top() + 3)
        elif self.kind == "nvme":
            stick = area.adjusted(2, 20, -2, -14)
            painter.drawRoundedRect(stick, 5, 5)
            painter.setPen(QPen(accent, 2))
            for index in range(3):
                painter.drawRoundedRect(QRectF(stick.left() + 13 + index * 21, stick.top() + 7, 14, 15), 2, 2)
            painter.drawEllipse(QPointF(stick.right() - 8, stick.center().y()), 2, 2)
        else:  # RAM
            for y in (15, 42):
                module = QRectF(area.left(), area.top() + y - 8, area.width(), 20)
                painter.drawRoundedRect(module, 4, 4)
                painter.setPen(QPen(accent, 2))
                painter.drawLine(module.left() + 6, module.top() + 3, module.right() - 6, module.top() + 3)
                painter.setPen(QPen(QColor("#58758a"), 1))
                for index in range(5):
                    painter.drawRect(QRectF(module.left() + 8 + index * 16, module.top() + 7, 11, 8))

class ResultCard(QFrame):
    def __init__(self, kind: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("settingsCard")
        self.setMinimumHeight(178)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(5)
        top = QHBoxLayout()
        self.icon = QLabel("?")
        self.icon.setObjectName("moduleHeroIcon")
        self.icon.setFixedSize(36, 36)
        self.title = QLabel("—")
        self.title.setObjectName("cardTitle")
        top.addWidget(self.icon)
        top.addWidget(self.title, 1)
        top.addWidget(HardwareIllustration(kind, self))
        layout.addLayout(top)
        self.value = QLabel("—")
        self.value.setObjectName("metricValue")
        self.value.setWordWrap(True)
        value_font = QFont(self.value.font())
        value_font.setPointSize(max(14, value_font.pointSize() + 3))
        value_font.setBold(True)
        self.value.setFont(value_font)
        self.detail = QLabel("")
        self.detail.setObjectName("muted")
        self.detail.setWordWrap(True)
        detail_font = QFont(self.detail.font())
        detail_font.setPointSize(max(11, detail_font.pointSize() + 1))
        self.detail.setFont(detail_font)
        layout.addWidget(self.value)
        layout.addWidget(self.detail)

    def show_result(self, title: str, result: Assessment) -> None:
        icon, style = CARD_STATE.get(result.state, CARD_STATE["unknown"])
        self.title.setText(title)
        self.icon.setText(icon)
        self.icon.setObjectName(style)
        self.icon.style().unpolish(self.icon)
        self.icon.style().polish(self.icon)
        self.value.setText(result.value)
        self.detail.setText(result.detail)

class HardwareOverviewMixin:
    CARD_KEYS = ("cpu", "mainboard", "socket", "gpu", "nvme", "ram")


    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        width = max(1, event.size().width())
        self._reflow_cards(3 if width >= 1040 else 2 if width >= 680 else 1)
        super().resizeEvent(event)

    def _reflow_cards(self, columns: int) -> None:
        if columns == self._card_columns:
            return
        self._card_columns = columns
        while self.card_grid.count():
            self.card_grid.takeAt(0)
        for index, key in enumerate(self.CARD_KEYS):
            self.card_grid.addWidget(self.cards[key], index // columns, index % columns)

    def _populate_cards(self) -> None:
        cpu = self.report.get("cpu", {}) if isinstance(self.report, dict) else {}
        if isinstance(cpu, dict) and cpu:
            topology = f"{cpu.get('cores') or '—'} Kerne · {cpu.get('logical') or '—'} Threads"
            smt = str(cpu.get("smt_state", "unknown"))
            state = "pass" if smt == "enabled" else "fail" if smt == "disabled" else "info"
            detail = f"{topology} · SMT: {self.tr('aktiv') if smt == 'enabled' else self.tr('nicht aktiv') if smt == 'disabled' else self.tr('nicht gemeldet')}"
            self.cards["cpu"].show_result(self.tr("Prozessor"), Assessment(state, str(cpu.get("model", "Unbekannt")), detail))
        else:
            self.cards["cpu"].show_result(self.tr("Prozessor"), Assessment("unknown", "—", self.tr("Noch nicht geprüft")))

        board = self.report.get("board", {}) if isinstance(self.report, dict) else {}
        if isinstance(board, dict):
            board_value = str(board.get("display", "Unbekannt"))
            raw_vendor = str(board.get("vendor_raw", ""))
            detail = self.tr("Nur Identifikation; keine BIOS-Änderung.")
            if raw_vendor and raw_vendor != board.get("vendor"):
                detail += f" · DMI: {raw_vendor}"
        else:
            board_value = str(board or "Unbekannt")
            detail = self.tr("Nur Identifikation; keine BIOS-Änderung.")
        self.cards["mainboard"].show_result(self.tr("Mainboard"), Assessment("info", board_value, detail))
        socket_detail = self.tr("Firmwarefeld") + (f": {self.socket_source}" if self.socket_source else "")
        self.cards["socket"].show_result(self.tr("Sockel"), Assessment(
            "info" if self.socket_name != "Nicht gemeldet" else "unknown",
            self.tr(self.socket_name), socket_detail if self.socket_source else self.tr("Nicht gemeldet"),
        ))

        gpus = self.report.get("gpus", ()) if isinstance(self.report, dict) else ()
        gpu_lines, gpu_details, gpu_states = [], [], []
        if isinstance(gpus, list):
            for gpu in gpus:
                if isinstance(gpu, dict):
                    target = bool(gpu.get("boot_vga")) or len(gpus) == 1
                    assessed = assess_pcie_link(gpu, under_load=bool(
                        getattr(self, "last_scan_under_load", False) and target))
                    gpu_states.append(assessed.state)
                    gpu_lines.append(f"{gpu.get('name', 'GPU')} · {assessed.value}")
                    gpu_details.append(self._translate_detail(assessed.detail))
        gpu_state = "fail" if "fail" in gpu_states else "warning" if "warning" in gpu_states else "pass" if gpu_states else "unknown"
        self.cards["gpu"].show_result(self.tr("Grafikkarte / PCIe"), Assessment(
            gpu_state, "\n".join(gpu_lines) or "—", " · ".join(gpu_details) or self.tr("Noch nicht geprüft"),
        ))

        nvmes = self.report.get("nvmes", ()) if isinstance(self.report, dict) else ()
        nvme_lines, nvme_details, nvme_states = [], [], []
        if isinstance(nvmes, list):
            for drive in nvmes:
                if isinstance(drive, dict):
                    assessed = assess_nvme_link(drive)
                    nvme_states.append(assessed.state)
                    nvme_lines.append(f"{drive.get('name', 'NVMe')} · {assessed.value}")
                    nvme_details.append(self._translate_detail(assessed.detail))
        nvme_state = "fail" if "fail" in nvme_states else "warning" if "warning" in nvme_states else "pass" if nvme_states else "unknown"
        self.cards["nvme"].show_result(self.tr("NVMe-SSD"), Assessment(
            nvme_state, "\n".join(nvme_lines) or "—", " · ".join(nvme_details) or self.tr("Noch nicht geprüft"),
        ))

        memory = assess_memory(self.memory_modules, expected_mts=self.ram_target.value())
        detected = sorted({
            " ".join(str(item.get(field, "")).strip() for field in ("manufacturer", "part")).strip()
            for item in self.memory_modules
        })
        detected_text = ", ".join(value for value in detected if value and value.casefold() not in {"unknown", "not specified"})
        if detected_text and not self.ram_model.text().strip():
            self.ram_model.setText(detected_text[:160])
        total = str(self.report.get("memory_total", "Unbekannt")) if isinstance(self.report, dict) else "Unbekannt"
        ram_name = self.ram_model.text().strip() or detected_text or self.tr("Hersteller/Modell noch nicht angegeben.")
        self.cards["ram"].show_result(self.tr("Arbeitsspeicher"), Assessment(
            memory.state, f"{total} · {memory.value}", f"{ram_name} · {self._translate_detail(memory.detail)}",
        ))
