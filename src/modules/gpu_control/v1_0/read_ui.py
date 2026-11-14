# SPDX-License-Identifier: GPL-3.0-or-later
"""GPU read result presentation; Ubuntu navigation never waits for LACT."""
from __future__ import annotations

from PySide6.QtCore import QTimer

from modules.mainboard_driver_setup.v1_1.distribution import detect_distribution
from .client import LactClient
from .read_probe import GpuReadProbe
from .read_status import log_failure, set_state


class GpuReadUiMixin:
    def _write_allowed(self) -> bool:
        enabled = getattr(self.host, "feature_enabled", lambda _key: True)("gpu")
        owners = getattr(self.host, "control_authority", {})
        return bool(enabled and str(owners.get("gpu", "auto")) in {"auto", "ohc_lact"})

    def _init_gpu_reads(self) -> None:
        self._ubuntu_async_reads = detect_distribution().family == "ubuntu"
        self.gpu_read_probe = GpuReadProbe(self)
        self.gpu_read_probe.completed.connect(self._gpu_read_completed)
        self.gpu_read_probe.failed.connect(self._gpu_read_failed)
        self.gpu_owner_probe = GpuReadProbe(self)
        self.gpu_owner_probe.timeout.setInterval(8_000)
        self.gpu_owner_probe.completed.connect(self._gpu_owner_completed)
        self.gpu_owner_probe.failed.connect(lambda *_: self._display_gpu_ownership(
            True, "CoolerControl GPU ownership could not be verified"))

    def refresh_ownership_async(self) -> None:
        if self.gpu_owner_probe.process is None:
            self.gpu_owner_probe.request("ownership", getattr(self.client, "path", "/run/lactd.sock"))

    def _gpu_owner_completed(self, _kind: str, data: dict) -> None:
        owner = data.get("ownership")
        if (isinstance(owner, list) and len(owner) == 2
                and isinstance(owner[0], bool) and isinstance(owner[1], str)):
            self._display_gpu_ownership(*owner)
        else:
            self._display_gpu_ownership(True, "CoolerControl GPU ownership could not be verified")

    def _request_gpu_read(self, kind: str, gpu_id: str = "") -> bool:
        # Alternate injected clients retain their existing in-process contract;
        # only the concrete Unix-socket client can be serialized to a process.
        if not self._ubuntu_async_reads or not isinstance(self.client, LactClient):
            return False
        if kind != "metrics" or getattr(self, "gpu_read_state", "unknown") != "connected":
            set_state(self, "loading")
        self.gpu_read_probe.request(kind, self.client.path, gpu_id)
        return True

    def _populate_gpu_devices(self, rows) -> None:
        previous = self.gpu_id
        blocked = self.devices.blockSignals(True)
        self.devices.clear()
        for row in rows:
            self.devices.addItem(str(row.get("name") or row["id"]), row["id"])
        index = self.devices.findData(previous)
        dedicated = next((i for i, row in enumerate(rows) if row.get("device_type") == "Dedicated"), 0)
        self.devices.setCurrentIndex(index if index >= 0 else (dedicated if rows else -1))
        self.devices.blockSignals(blocked)
        self._select_device()

    def _gpu_read_completed(self, kind: str, data: dict) -> None:
        if self.preview_active or getattr(self, "stress_process", None) is not None:
            return
        if kind == "inventory":
            rows = data.get("rows")
            if isinstance(rows, list) and all(isinstance(row, dict) and isinstance(row.get("id"), str) for row in rows):
                self._populate_gpu_devices(rows)
            else:
                self._gpu_read_failed(kind, "Invalid GPU response")
        elif data.get("gpu_id") == self.gpu_id:
            if kind == "device":
                owner = data.get("ownership")
                if (all(isinstance(data.get(key), dict) for key in ("stats", "clocks", "baseline"))
                        and "info" in data
                        and (data.get("overdrive") is None or isinstance(data.get("overdrive"), bool))
                        and isinstance(data.get("warnings", []), list)
                        and all(isinstance(warning, str) for warning in data.get("warnings", []))
                        and isinstance(owner, list) and len(owner) == 2
                        and isinstance(owner[0], bool) and isinstance(owner[1], str)):
                    self._apply_gpu_read(data)
                else:
                    self._gpu_read_failed(kind, "Invalid GPU response")
            elif kind == "metrics" and isinstance(data.get("stats"), dict):
                self.stats = data["stats"]
                self._fill_table(self.metrics, self.stats)
                self._refresh_gpu_dashboard()
                set_state(self, "connected")

    def _gpu_read_failed(self, kind: str, reason: str) -> None:
        set_state(self, "failed", kind=kind, reason=reason)
        log_failure(self, kind, reason)
        if kind == "inventory":
            self.baseline = None
            self.overdrive_enabled = None
            self.status.setText(self.tr("LACT-Dienst nicht erreichbar: {reason}").format(reason=reason))
        else:
            self.status.setText(self.tr("GPU-Daten konnten nicht gelesen werden: {reason}").format(reason=reason))
        self._sync_buttons()

    def _apply_gpu_read(self, data: dict) -> None:
        self.stats = data["stats"]
        self.clocks = data["clocks"]
        self.baseline = data["baseline"]
        self.overdrive_enabled = data["overdrive"]
        self._refresh_gpu_dashboard()
        self._fill_table(self.hardware, data["info"])
        self._fill_table(self.metrics, self.stats)
        for warning in data.get("warnings", ()):
            self._gpu_log(str(warning))
        self._populate_controls()
        self._display_gpu_ownership(*data["ownership"])
        QTimer.singleShot(0, self, self.apply_startup_gpu_profile)
        QTimer.singleShot(0, self, self._consume_pending_main_gpu_profile)
        set_state(self, "connected")
        self._sync_buttons()
