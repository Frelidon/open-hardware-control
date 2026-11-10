# SPDX-License-Identifier: GPL-3.0-or-later
"""Persisted RGB exit state and bounded final hardware handoff."""

from __future__ import annotations

import os
import re
import subprocess

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from command_backend import Backend, needs_headless_qt_platform
from nzxt_rgb import build_nzxt_effect_arguments, coalesce_selected_channels
from openrgb_integration import OpenRGBError, best_native_mode_for_effect
from privacy_logging import redact_private_text


MODE_KEY = "rgb_studio/shutdown_lighting_mode"
COLOR_KEY = "rgb_studio/shutdown_lighting_color"
STATIC = "static"
RAINBOW = "rainbow"
VALID_MODES = {STATIC, RAINBOW}
HEX_COLOR = re.compile(r"^[0-9a-f]{6}$")


def normalize_mode(value: object) -> str:
    clean = str(value or STATIC).casefold()
    return clean if clean in VALID_MODES else STATIC


def normalize_color(value: object) -> str:
    clean = str(value or "ffffff").strip().lstrip("#").casefold()
    return clean if HEX_COLOR.fullmatch(clean) else "ffffff"


def load(host) -> tuple[str, str]:
    settings = host.settings
    return (
        normalize_mode(settings.value(MODE_KEY, STATIC)),
        normalize_color(settings.value(COLOR_KEY, "ffffff")),
    )


def _reported_mode(device, effect: str) -> str:
    mode = best_native_mode_for_effect(device, effect)
    available = {item.casefold(): item for item in device.modes if item.casefold() != "direct"}
    return available.get(mode.casefold(), "") if mode else ""


class ShutdownLightingMixin:
    """Offer one exit-light choice and apply it before RGB ownership release."""

    def load_rgb_shutdown_lighting(self) -> None:
        self.rgb_shutdown_lighting_mode, self.rgb_shutdown_lighting_color = load(self)

    def build_rgb_shutdown_lighting_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("rgbShutdownLightingPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        title = QLabel("BELEUCHTUNG NACH PROGRAMMENDE")
        title.setObjectName("rgbStartupAutomationTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        row = QHBoxLayout()
        row.addWidget(QLabel("Wenn Open Hardware Control beendet ist:"))
        self.rgb_shutdown_lighting_combo = QComboBox()
        self.rgb_shutdown_lighting_combo.addItem("Einzelfarbe", STATIC)
        self.rgb_shutdown_lighting_combo.addItem("Rainbow · Hardwaremodus", RAINBOW)
        self.rgb_shutdown_lighting_combo.setCurrentIndex(max(
            0, self.rgb_shutdown_lighting_combo.findData(self.rgb_shutdown_lighting_mode)
        ))
        self.rgb_shutdown_lighting_combo.currentIndexChanged.connect(
            self.set_rgb_shutdown_lighting_mode
        )
        row.addWidget(self.rgb_shutdown_lighting_combo)
        self.rgb_shutdown_lighting_color_button = QPushButton()
        self.rgb_shutdown_lighting_color_button.clicked.connect(self.pick_rgb_shutdown_lighting_color)
        row.addWidget(self.rgb_shutdown_lighting_color_button)
        row.addStretch()
        layout.addLayout(row)

        note = QLabel(
            "Standard ist Weiß. Die Einstellung wird nur beim echten Beenden angewendet, nicht beim Minimieren in den Infobereich. Rainbow verwendet ausschließlich einen vom Gerät gemeldeten Hardwaremodus; fehlt er, bleibt die gewählte Einzelfarbe als Rückfall erhalten."
        )
        note.setWordWrap(True)
        note.setObjectName("muted")
        layout.addWidget(note)
        self.sync_rgb_shutdown_lighting_controls()
        return panel

    def sync_rgb_shutdown_lighting_controls(self) -> None:
        button = getattr(self, "rgb_shutdown_lighting_color_button", None)
        if button is None:
            return
        button.setText(self.tr_static("Wunschfarbe wählen"))
        button.setToolTip(f"#{self.rgb_shutdown_lighting_color}")
        button.setEnabled(self.rgb_shutdown_lighting_mode == STATIC)

    def set_rgb_shutdown_lighting_mode(self, _index: int = -1) -> None:
        combo = getattr(self, "rgb_shutdown_lighting_combo", None)
        if combo is None:
            return
        self.rgb_shutdown_lighting_mode = normalize_mode(combo.currentData())
        self.settings.setValue(MODE_KEY, self.rgb_shutdown_lighting_mode)
        self.settings.sync()
        self.sync_rgb_shutdown_lighting_controls()

    def pick_rgb_shutdown_lighting_color(self) -> None:
        selected = QColorDialog.getColor(
            QColor("#" + self.rgb_shutdown_lighting_color),
            self,
            self.tr_static("Wunschfarbe nach Programmende"),
        )
        if not selected.isValid():
            return
        self.rgb_shutdown_lighting_color = normalize_color(selected.name())
        self.settings.setValue(COLOR_KEY, self.rgb_shutdown_lighting_color)
        self.settings.sync()
        self.sync_rgb_shutdown_lighting_controls()

    def _run_rgb_shutdown_command(self, command: list[str], *, timeout: int = 5) -> tuple[bool, str]:
        environment = os.environ.copy()
        if needs_headless_qt_platform(command):
            environment["QT_QPA_PLATFORM"] = "offscreen"
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=max(1, min(8, int(timeout))),
                check=False,
                env=environment,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return False, redact_private_text(str(exc))
        detail = redact_private_text((result.stderr or result.stdout or "").strip())
        return result.returncode == 0, detail

    def _openrgb_shutdown_commands(self, device) -> tuple[list[str], list[str] | None]:
        color = self.rgb_shutdown_lighting_color
        if self.rgb_shutdown_lighting_mode == RAINBOW:
            native = _reported_mode(device, RAINBOW)
            if native:
                return self.openrgb_client.native_mode_command(
                    device.index, native, [color], 100
                ), self._openrgb_static_shutdown_command(device)
        command = self._openrgb_static_shutdown_command(device)
        return command, None

    def _openrgb_static_shutdown_command(self, device) -> list[str]:
        color = self.rgb_shutdown_lighting_color
        if device.supports_direct:
            count, sizes = self.openrgb_device_write_shape(device)
            return self.openrgb_client.sdk_color_command(
                device.index,
                [color] * count,
                count,
                direct=True,
                zone_sizes=sizes,
            )
        native = _reported_mode(device, STATIC)
        if not native or native.casefold() not in {"static", "fixed"}:
            raise ValueError("kein gemeldeter statischer Hardwaremodus")
        return self.openrgb_client.native_mode_command(device.index, native, [color], 100)

    def apply_rgb_shutdown_lighting_sync(self, reason: str = "") -> None:
        """Apply the requested persistent state while OHC still owns its RGB engine."""

        if reason == "Programmneustart":
            self.log_message("RGB-PROGRAMMENDE: bei Programmneustart übersprungen")
            return
        if not getattr(self, "openrgb_write_enabled", False):
            self.log_message("RGB-PROGRAMMENDE: keine aktive exklusive OHC-RGB-Freigabe · keine Abschlussfarbe geschrieben")
            return

        completed = 0
        failed = 0
        openrgb_available = (
            getattr(self, "openrgb_server_reachable", False)
            and not getattr(self, "openrgb_external_server_detected", False)
        )
        for device in self.selected_openrgb_devices() if openrgb_available else ():
            if self.openrgb_device_conflict(device):
                continue
            try:
                command, fallback = self._openrgb_shutdown_commands(device)
            except (OpenRGBError, ValueError) as exc:
                failed += 1
                self.log_message(
                    f"RGB-PROGRAMMENDE: {self.rgb_device_display_name(device)} übersprungen · {redact_private_text(str(exc))}"
                )
                continue
            ok, detail = self._run_rgb_shutdown_command(command)
            if not ok and fallback is not None:
                ok, fallback_detail = self._run_rgb_shutdown_command(fallback)
                detail = fallback_detail or detail
            if ok:
                completed += 1
            else:
                failed += 1
                self.log_message(
                    f"RGB-PROGRAMMENDE: {self.rgb_device_display_name(device)} fehlgeschlagen"
                    + (f" · {detail[:240]}" if detail else "")
                )

        nzxt_mode = "rainbow-flow" if self.rgb_shutdown_lighting_mode == RAINBOW else "fixed"
        nzxt_colors = [] if nzxt_mode == "rainbow-flow" else [self.rgb_shutdown_lighting_color]
        try:
            nzxt_commands = [
                command
                for channel in coalesce_selected_channels(self.selected_nzxt_rgb_channels())
                for command in build_nzxt_effect_arguments(
                    Backend.rgb_args(), channel, nzxt_mode, nzxt_colors, "normal", "forward"
                )
            ]
        except ValueError as exc:
            nzxt_commands = []
            failed += 1
            self.log_message(f"RGB-PROGRAMMENDE: NZXT-Abschlusslicht ungültig · {exc}")
        for command in nzxt_commands:
            ok, detail = self._run_rgb_shutdown_command(command, timeout=8)
            completed += int(ok)
            failed += int(not ok)
            if not ok:
                self.log_message("RGB-PROGRAMMENDE: NZXT-Abschlusslicht fehlgeschlagen" + (f" · {detail[:240]}" if detail else ""))

        mode = self.tr_static("Rainbow · Hardwaremodus") if self.rgb_shutdown_lighting_mode == RAINBOW else f"#{self.rgb_shutdown_lighting_color}"
        self.log_message(
            f"RGB-PROGRAMMENDE: Abschlussbeleuchtung {mode} · erfolgreich={completed} · fehlgeschlagen={failed} · physische Ausgabe nicht rücklesbar"
        )
