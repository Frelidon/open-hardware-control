#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Qt surface and bounded process orchestration for Snapshot Manager 1.0."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QDateTime, QIODevice, QProcess, QSaveFile, QTime, QTimer, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QCheckBox, QComboBox, QDateTimeEdit,
    QFileDialog, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMessageBox, QPushButton, QScrollArea, QSlider, QSpinBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from .model import (
    ActivityGate, ActivitySample, SnapshotPolicy, SnapshotRecord, format_bytes,
    normalize_policy, normalize_process_names, parse_snapper_json,
)
from .activity_runtime import ActivityProbeRuntime
from .views import SnapshotViewMixin
from .snapshot_actions import SnapshotActionMixin
from .process_runtime import SnapshotProcessRuntimeMixin


GRANT_ROOT = Path("/var/lib/open-hardware-control/polkit-grants")
MODE_STATE = Path("/var/lib/open-hardware-control/snapshot-manager-state.json")
POLL_MS = 20_000
RESOURCE_POLICY_VERSION = 2


class SnapshotManagerPage(SnapshotViewMixin, SnapshotProcessRuntimeMixin, SnapshotActionMixin, QScrollArea):
    """Snapshot controls."""

    def __init__(self, host: QWidget, translate: Callable[[str], str]) -> None:
        super().__init__(host)
        self.host = host
        self.translate = translate
        self.report: dict[str, object] = {}
        self._processes_stopped = False
        self.gate = ActivityGate()
        self.last_gate_blocked = False
        self.manual_mode = "desktop"
        self.probe_process: QProcess | None = None
        self.helper_process: QProcess | None = None
        self.pending_helper_action = ""
        self.pending_snapshot_after_setup = ""
        self.pending_created_snapshot = ""
        self.pending_manual_snapshot: tuple[str, str] | None = None
        self.snapshot_records: tuple[SnapshotRecord, ...] = ()
        self.visible_snapshot_records: tuple[SnapshotRecord, ...] = ()
        self.policy = self._load_policy()
        self.activity_runtime = ActivityProbeRuntime(
            self, Path(__file__).with_name("activity_probe.py"),
            self._apply_activity_sample, self._log,
        )
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(POLL_MS)
        self.poll_timer.timeout.connect(self.poll_activity)
        self._build()
        self._load_persisted_mode()
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.stop_processes)
        if os.environ.get("OHC_SNAPSHOT_MANAGER_DEMO") == "1":
            self._load_demo()
        else:
            QTimer.singleShot(0, self, self.refresh_system)
            QTimer.singleShot(1_000, self, self.poll_activity)
            self.poll_timer.start()

    def tr(self, text: str) -> str:
        return self.translate(text)


    def _load_policy(self) -> SnapshotPolicy:
        settings = self.host.settings
        raw = {
            key: settings.value(f"snapshot_manager/{key}", default)
            for key, default in {
                "automatic_game_pause": True, "fullscreen_signal": True,
                "load_heuristic": True, "cpu_threshold": 70,
                "gpu_threshold": 65, "busy_core_percent": 65,
                "high_samples": 3, "release_samples": 3,
                "desktop_iops": 50, "desktop_kbps": 16384,
                "game_iops": 5, "game_kbps": 2048,
                "cpu_core_limit": 2, "cpu_percent_per_core": 50,
            }.items()
        }
        try:
            resource_version = int(settings.value("snapshot_manager/resource_policy_version", 0) or 0)
        except (TypeError, ValueError):
            resource_version = 0
        if resource_version < RESOURCE_POLICY_VERSION:
            previous = normalize_policy(raw)
            raw.update({
                "desktop_iops": min(50, previous.desktop_iops),
                "desktop_kbps": min(16384, previous.desktop_kbps),
                "game_iops": min(5, previous.game_iops),
                "game_kbps": min(2048, previous.game_kbps),
                "cpu_core_limit": 2,
                "cpu_percent_per_core": 50,
            })
            for key, value in raw.items():
                settings.setValue(f"snapshot_manager/{key}", value)
            settings.setValue("snapshot_manager/resource_policy_version", RESOURCE_POLICY_VERSION)
            settings.sync()
        return normalize_policy(raw)






    def _toggle_program_manager(self) -> None:
        visible = self.program_manager.isHidden()
        if visible:
            self.program_manager.ensure_loaded()
        self.program_manager.setVisible(visible)
        self.program_manager_button.setText(
            self.tr("Manager schließen") if visible else self.tr("Programme verwalten …")
        )

    def _program_selection_changed(self, names: tuple[str, ...]) -> None:
        self.process_names.setText(", ".join(names))
        self.save_policy()
        self._restart_activity_probe()

    def _automation_option_changed(self, *_args: object) -> None:
        self.save_policy()
        self._restart_activity_probe()



    def _load_persisted_mode(self) -> None:
        try:
            state = json.loads(MODE_STATE.read_text(encoding="ascii"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return
        if not isinstance(state, dict) or state.get("schema") != 1:
            return
        mode = str(state.get("mode", "desktop"))
        if mode == "forever":
            self.manual_mode = "forever"
            self.manual_status.setText(self.tr("Snapshot-Arbeit dauerhaft blockiert, bis du sie fortsetzt."))
        elif mode == "until":
            try:
                deadline = int(state.get("until", 0))
            except (TypeError, ValueError):
                return
            if deadline > QDateTime.currentSecsSinceEpoch():
                self.manual_mode = "until"
                display = QDateTime.fromSecsSinceEpoch(deadline).toString("dd.MM.yyyy HH:mm")
                self.manual_status.setText(self.tr("Snapshot-Arbeit blockiert bis {time}.").format(time=display))
        elif mode == "game":
            self.last_gate_blocked = True

    def save_policy(self, *_args: object) -> None:
        self.policy = normalize_policy({
            **self.policy.__dict__,
            "automatic_game_pause": self.auto_check.isChecked(),
            "fullscreen_signal": self.fullscreen_check.isChecked(),
            "load_heuristic": self.load_check.isChecked(),
            "cpu_threshold": self.cpu_threshold.value(),
            "gpu_threshold": self.gpu_threshold.value(),
            "desktop_iops": 50, "desktop_kbps": self.desktop_rate.value() * 1024,
            "game_iops": 5, "game_kbps": self.game_rate.value() * 1024,
            "cpu_core_limit": self.snapshot_core_limit.value(),
            "cpu_percent_per_core": self.snapshot_cpu_percent.value(),
        })
        for key, value in self.policy.__dict__.items():
            self.host.settings.setValue(f"snapshot_manager/{key}", value)
        self.host.settings.setValue("snapshot_manager/process_names", ",".join(normalize_process_names(self.process_names.text())))
        self.host.settings.setValue("snapshot_manager/resource_policy_version", RESOURCE_POLICY_VERSION)
        if hasattr(self, "program_manager"):
            self.host.settings.setValue("snapshot_manager/process_paths", "\n".join(self.program_manager.paths()))
        self.host.settings.sync()

    def policy_args(self) -> list[str]:
        self.save_policy()
        return [
            str(self.policy.desktop_iops), str(self.policy.desktop_kbps),
            str(self.policy.game_iops), str(self.policy.game_kbps),
            str(self.policy.cpu_core_limit), str(self.policy.cpu_percent_per_core),
        ]



    def _populate_report(self) -> None:
        os_info = self.report.get("os") if isinstance(self.report.get("os"), dict) else {}
        self.os_label.setText(str(os_info.get("name", "Linux")))
        backends = self.report.get("backends") if isinstance(self.report.get("backends"), list) else []
        visible = [item for item in backends if isinstance(item, dict)]
        self.backend_table.setRowCount(len(visible))
        for row, item in enumerate(visible):
            state = "Aktiv" if item.get("active") else "Verfügbar" if item.get("available") else "Nicht installiert"
            for column, value in enumerate((str(item.get("label", "")), self.tr(state))):
                table_item = QTableWidgetItem(value)
                if column == 1:
                    table_item.setForeground(QColor("#4ade80" if item.get("active") else "#94a3b8" if item.get("available") else "#64748b"))
                self.backend_table.setItem(row, column, table_item)
        configs = self.report.get("snapper_configs") if isinstance(self.report.get("snapper_configs"), list) else []
        current = self.config_combo.currentData()
        self.config_combo.clear()
        for config in configs:
            if isinstance(config, dict):
                name = str(config.get("name", ""))
                self.config_combo.addItem(f"Snapper · {name} · {config.get('subvolume', '')}", name)
        if current:
            index = self.config_combo.findData(current)
            if index >= 0:
                self.config_combo.setCurrentIndex(index)
        filesystems = self.report.get("filesystems") if isinstance(self.report.get("filesystems"), list) else []
        root_btrfs = any(
            isinstance(item, dict) and item.get("target") == "/" and item.get("fstype") == "btrfs"
            for item in filesystems
        )
        snapper_available = any(
            isinstance(item, dict) and item.get("id") == "snapper" and item.get("available")
            for item in backends
        )
        needs_setup = root_btrfs and snapper_available and not configs
        self.snapper_setup_button.setVisible(needs_setup)
        if needs_setup:
            self.snapper_setup_status.setText(self.tr(
                "Btrfs und Snapper wurden erkannt, aber es gibt noch keine Konfiguration. "
                "Beim Einrichten öffnet KDE einmalig die Administrator-Passwortabfrage."
            ))
        elif configs:
            self.snapper_setup_status.setText(self.tr("Snapper ist eingerichtet und für manuelle Snapshots bereit."))
        else:
            self.snapper_setup_status.setText(self.tr(
                "Für manuelle Snapshots werden ein Btrfs-Root-Dateisystem und Snapper benötigt."
            ))
        discard = self.report.get("btrfs_discard") if isinstance(self.report.get("btrfs_discard"), list) else []
        pending = sum(int(item.get("discardable_bytes") or 0) for item in discard if isinstance(item, dict))
        iops = next((item.get("iops_limit") for item in discard if isinstance(item, dict)), None)
        self.discard_label.setText(self.tr("Btrfs offen: {amount} · Limit: {iops} IOPS").format(
            amount=format_bytes(pending), iops=iops if iops is not None else "—",
        ))

    def poll_activity(self) -> None:
        if (
            self._processes_stopped
            or self.activity_runtime.process is not None
            or not self.auto_check.isChecked()
            or self.manual_mode != "desktop"
        ):
            return
        names = ",".join(normalize_process_names(self.process_names.text()))
        self.activity_runtime.start(
            names, self.policy.busy_core_percent, POLL_MS // 1_000,
        )

    def _apply_activity_sample(self, raw: object) -> None:
        if not isinstance(raw, dict):
            return
        try:
            sample = ActivitySample(
                cpu_percent=float(raw.get("cpu_percent", 0)), busy_cores=int(raw.get("busy_cores", 0)),
                logical_cores=int(raw.get("logical_cores", 1)),
                gpu_percent=None if raw.get("gpu_percent") is None else float(raw["gpu_percent"]),
                gamemode=bool(raw.get("gamemode")), gamescope=bool(raw.get("gamescope")),
                fullscreen=bool(raw.get("fullscreen")), process_active=bool(raw.get("process_active")),
                process_reason=str(raw.get("process_reason", ""))[:128],
            )
        except (ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError):
            return
        decision = self.gate.update(sample, self.policy)
        gpu_text = "—" if sample.gpu_percent is None else f"{sample.gpu_percent:.0f} %"
        self.activity_status.setText(self.tr("CPU {cpu:.0f} % · {cores}/{total} Kerne hoch · GPU {gpu} · {reason}").format(
            cpu=sample.cpu_percent, cores=sample.busy_cores, total=sample.logical_cores,
            gpu=gpu_text, reason=self.tr(decision.reason),
        ))
        self.hero_state.setText(self.tr("SPIELMODUS · SNAPSHOTS PAUSIERT") if decision.blocked else self.tr("DESKTOP · AUTOMATIK BEREIT"))
        if decision.blocked != self.last_gate_blocked and self.manual_mode == "desktop":
            self.last_gate_blocked = decision.blocked
            if self._persistent_authorized() and os.environ.get("OHC_DISABLE_HARDWARE_IO") != "1":
                self.run_helper("game" if decision.blocked else "desktop", self.policy_args())

    def _restart_activity_probe(self) -> None:
        if self._processes_stopped:
            return
        names = ",".join(normalize_process_names(self.process_names.text()))
        self.activity_runtime.restart(
            names, self.policy.busy_core_percent, POLL_MS // 1_000,
            enabled=self.auto_check.isChecked() and self.manual_mode == "desktop",
        )

    def apply_resource_limits_now(self) -> None:
        if self.run_helper("limits", self.policy_args()):
            self.resource_apply.setEnabled(False)
            self.resource_status.setText(self.tr("Administratorfreigabe wird angefordert …"))

    def block_until(self, date_time: QDateTime) -> None:
        epoch = date_time.toSecsSinceEpoch()
        if epoch <= QDateTime.currentSecsSinceEpoch() + 30:
            self.manual_status.setText(self.tr("Der gewählte Zeitpunkt muss in der Zukunft liegen."))
            return
        if self.run_helper("until", [str(epoch), *self.policy_args()]):
            self.manual_status.setText(self.tr("Administratorfreigabe wird angefordert …"))

    def block_forever(self) -> None:
        if self.run_helper("forever", self.policy_args()):
            self.manual_status.setText(self.tr("Administratorfreigabe wird angefordert …"))

    def resume_now(self) -> None:
        if self.run_helper("desktop", self.policy_args()):
            self.manual_status.setText(self.tr("Administratorfreigabe wird angefordert …"))




    def _selected_snapshot(self) -> SnapshotRecord | None:
        row = self.snapshot_table.currentRow()
        if 0 <= row < len(self.visible_snapshot_records):
            return self.visible_snapshot_records[row]
        return None


    def _render_snapshot_rows(self, *_args) -> None:
        selected = str(self.snapshot_filter.currentData() or "all")
        self.visible_snapshot_records = tuple(
            record for record in self.snapshot_records
            if selected == "all" or record.source == selected
        )
        self.snapshot_table.setRowCount(len(self.visible_snapshot_records))
        for row, record in enumerate(self.visible_snapshot_records):
            source = self.tr("Open Hardware Control") if record.source == "ohc" else self.tr("System / anderes Programm")
            values = (record.number, record.created, record.description, source, record.cleanup, self.tr("Verfügbar"))
            for column, value in enumerate(values):
                self.snapshot_table.setItem(row, column, QTableWidgetItem(value or "—"))
        self.snapshot_table.resizeRowsToContents()
        self.snapshot_export.setEnabled(bool(self.visible_snapshot_records))
        self._snapshot_selection_changed()

    def _snapshot_selection_changed(self) -> None:
        record = self._selected_snapshot()
        deletable = bool(record and record.number.isdigit() and int(record.number) > 0)
        self.snapshot_delete.setEnabled(deletable and self.helper_process is None)
        if record and record.number == "0":
            self.snapshot_action_status.setText(self.tr(
                "Snapshot 0 ist der aktuelle Zustand und kann hier nicht gelöscht werden."
            ))
        elif record:
            self.snapshot_action_status.setText(self.tr("Snapshot {number} ausgewählt.").format(
                number=record.number,
            ))

    def delete_selected_snapshot(self) -> None:
        record = self._selected_snapshot()
        config = str(self.config_combo.currentData() or "")
        if not record or not config or not record.number.isdigit() or int(record.number) <= 0:
            return
        prompt = self.tr(
            "Snapshot {number} aus Snapper-Konfiguration {config} wirklich dauerhaft löschen?\n\n"
            "Diese Aktion kann nicht rückgängig gemacht werden."
        ).format(number=record.number, config=config)
        answer = QMessageBox.question(
            self, self.tr("Snapshot löschen"), prompt,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        if self.run_helper("delete", [config, record.number]):
            self.snapshot_delete.setEnabled(False)
            self.snapshot_action_status.setText(self.tr("Administratorfreigabe wird angefordert …"))

    def export_snapshot_list(self) -> None:
        if not self.snapshot_records:
            self.snapshot_action_status.setText(self.tr("Kein Snapshot zum Exportieren geladen."))
            return
        stamp = QDateTime.currentDateTime().toString("yyyyMMdd-HHmm")
        suggested = str(Path.home() / f"snapshot-liste-{stamp}.json")
        filename, _selected_filter = QFileDialog.getSaveFileName(
            self, self.tr("Liste als JSON exportieren"), suggested, "JSON (*.json)",
        )
        if not filename:
            return
        payload = {
            "schema": 1,
            "exported_at": QDateTime.currentDateTimeUtc().toString(Qt.DateFormat.ISODate),
            "snapper_config": str(self.config_combo.currentData() or ""),
            "snapshots": [
                {
                    "number": record.number,
                    "created": record.created,
                    "description": record.description,
                    "cleanup": record.cleanup,
                    "source": record.source,
                }
                for record in self.snapshot_records
            ],
        }
        output = QSaveFile(filename)
        if not output.open(QIODevice.OpenModeFlag.WriteOnly):
            self.snapshot_action_status.setText(self.tr("Snapshot-Liste konnte nicht exportiert werden."))
            return
        encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        if output.write(encoded) != len(encoded) or not output.commit():
            output.cancelWriting()
            self.snapshot_action_status.setText(self.tr("Snapshot-Liste konnte nicht exportiert werden."))
            return
        self.snapshot_action_status.setText(self.tr("Snapshot-Liste wurde exportiert."))


    def _action_target(self, action: str) -> QLabel:
        if action in {"list", "delete", "create"}:
            return self.snapshot_action_status
        if action == "setup-root":
            return self.snapper_setup_status
        if action == "limits":
            return self.resource_status
        return self.manual_status


    def _helper_finished(
        self, process: QProcess, action: str, exit_code: int,
        _status: QProcess.ExitStatus,
    ) -> None:
        if self.helper_process is not process:
            return
        self.helper_process = None
        self.pending_helper_action = ""
        process.deleteLater()
        output = bytes(process.readAllStandardOutput()).decode("utf-8", "replace")[-524288:]
        try:
            response = json.loads(output)
        except json.JSONDecodeError:
            response = {}
        if exit_code != 0 or not response.get("ok"):
            target = self._action_target(action)
            stderr = bytes(process.readAllStandardError()).decode("utf-8", "replace").strip()
            detail = stderr.splitlines()[-1][:240] if stderr else ""
            helper_error = str(response.get("error") or "")[:240]
            if exit_code == 126:
                category = "Authentifizierungsdialog abgebrochen"
            elif exit_code == 127:
                category = "Polkit-Autorisierung nicht erteilt oder nicht verfügbar"
            elif exit_code < 0:
                category = "Qt konnte den Polkit-Prozess nicht ausführen"
            else:
                category = "privilegierte Aktion fehlgeschlagen"
            reason = helper_error or detail or "keine verwertbare Helferantwort"
            self._log(
                f"Polkit-Aktion fehlgeschlagen · Aktion={action or 'unbekannt'} · "
                f"Exit={exit_code} · Status={_status.name} · Kategorie={category} · Grund={reason}"
            )
            self.snapshot_create.setEnabled(True)
            self.resource_apply.setEnabled(True)
            self.pending_snapshot_after_setup = ""
            self.snapper_setup_button.setEnabled(True)
            self._snapshot_selection_changed()
            if action == "list" and self.pending_created_snapshot:
                target.setText(
                    self.tr(
                        "Snapshot {number} wurde erstellt · Liste konnte nicht aktualisiert werden."
                    ).format(number=self.pending_created_snapshot)
                    + (f" · {detail}" if detail else "")
                )
                self.pending_created_snapshot = ""
            else:
                target.setText(
                    self.tr("Aktion nicht ausgeführt oder abgebrochen.")
                    + f" · {category}"
                    + (f" · {detail}" if detail else "")
                )
            self._dispatch_pending_manual_snapshot()
            return
        self._log(
            f"Polkit-Aktion bestätigt · Aktion={action} · Exit={exit_code} · "
            f"Ergebnis={'Snapshot ' + str(response.get('created_snapshot') or 'erstellt') if action == 'create' else 'erfolgreich'}"
        )
        if action == "list":
            payload = response.get("payload")
            self.snapshot_records = parse_snapper_json(payload)
            self._render_snapshot_rows()
            created_number, self.pending_created_snapshot = self.pending_created_snapshot, ""
            if created_number:
                self.snapshot_action_status.setText(
                    self.tr("Snapshot {number} wurde erstellt · {count} Snapshots geladen.").format(
                        number=created_number, count=len(self.snapshot_records),
                    )
                )
            else:
                self.snapshot_action_status.setText(self.tr("{count} Snapshots geladen.").format(
                    count=len(self.snapshot_records),
                ))
        elif action == "delete":
            number = str(response.get("deleted_snapshot", ""))
            self.snapshot_action_status.setText(self.tr("Snapshot {number} wurde gelöscht.").format(number=number))
            QTimer.singleShot(600, self, self.load_snapshots)
        elif action == "create":
            number = str(response.get("created_snapshot", ""))
            self.snapshot_create.setEnabled(True)
            self.pending_created_snapshot = number or "—"
            self.snapshot_action_status.setText(
                self.tr("Snapshot {number} wurde erstellt · Liste wird aktualisiert …").format(
                    number=self.pending_created_snapshot,
                )
            )
            QTimer.singleShot(600, self, self._refresh_snapshots_after_create)
        elif action == "setup-root":
            self.snapper_setup_button.setEnabled(True)
            self.snapper_setup_status.setText(self.tr(
                "Snapper-Konfiguration „root“ wurde eingerichtet. Die Snapshot-Liste wird neu geladen."
            ))
            description, self.pending_snapshot_after_setup = self.pending_snapshot_after_setup, ""
            if description:
                self.config_combo.clear()
                self.config_combo.addItem("Snapper · root · /", "root")
                self.snapshot_action_status.setText(self.tr("Snapper ist bereit · der Snapshot wird jetzt erstellt."))
                QTimer.singleShot(150, self, lambda text=description: self._create_after_root_setup(text))
        elif action in {"grant", "revoke"}:
            self._refresh_authorization_state()
        elif action == "until":
            self.manual_mode = "until"
            self._restart_activity_probe()
            deadline = QDateTime.fromSecsSinceEpoch(int(response.get("until", 0)))
            self.manual_status.setText(self.tr("Snapshot-Arbeit blockiert bis {time}.").format(time=deadline.toString("dd.MM.yyyy HH:mm")))
        elif action == "forever":
            self.manual_mode = "forever"
            self._restart_activity_probe()
            self.manual_status.setText(self.tr("Snapshot-Arbeit dauerhaft blockiert, bis du sie fortsetzt."))
        elif action == "desktop":
            self.manual_mode = "desktop"
            self.manual_status.setText(self.tr("Snapshot-Arbeit wird im gedrosselten Desktop-Modus fortgesetzt."))
            self._restart_activity_probe()
        elif action == "limits":
            resources = response.get("resources") if isinstance(response.get("resources"), dict) else {}
            cpus = resources.get("allowed_cpus") if isinstance(resources.get("allowed_cpus"), list) else []
            quota = int(resources.get("cpu_quota_percent") or self.policy.cpu_quota_percent)
            self.resource_apply.setEnabled(True)
            self.resource_status.setText(self.tr(
                "Aktiv: {cores} logische CPUs · insgesamt höchstens {quota} % eines CPU-Kerns · niedrige Priorität."
            ).format(cores=len(cpus) or self.policy.cpu_core_limit, quota=quota))
        self._dispatch_pending_manual_snapshot()
        QTimer.singleShot(300, self, self.refresh_system)




    def _persistent_authorized(self) -> bool:
        try:
            uid = os.getuid()
        except AttributeError:
            return False
        return (GRANT_ROOT / f"snapshot-{uid}").is_file()

    def _refresh_authorization_state(self) -> None:
        granted = self._persistent_authorized()
        self.auth_state.setText(self.tr("Automatik autorisiert" if granted else "Automatik benötigt einmalig Administratorfreigabe"))
        self.auth_state.setObjectName("successText" if granted else "warningText")
        self.grant_button.setText(self.tr("Automatikfreigabe entfernen" if granted else "Automatik einmalig autorisieren"))

    def toggle_authorization(self) -> None:
        self.run_helper("revoke" if self._persistent_authorized() else "grant", [])


    def _load_demo(self) -> None:
        self.report = {
            "schema": 1,
            "os": {"name": "Fedora Linux 44 (KDE Plasma)"},
            "backends": [
                {"label": "Snapper", "available": True, "active": True},
                {"label": "Btrfs", "available": True, "active": True},
                {"label": "Timeshift", "available": True, "active": False},
                {"label": "ZFS", "available": False, "active": False},
                {"label": "LVM", "available": False, "active": False},
            ],
            "snapper_configs": [{"name": "1", "subvolume": "/"}],
            "btrfs_discard": [{"discardable_bytes": 6_958_886_912, "iops_limit": 100}],
        }
        self._populate_report()
        self.activity_status.setText("CPU 18 % · 1/16 Kerne hoch · GPU 7 % · Desktop")
        self.snapshot_records = (
            SnapshotRecord("0", "01.10.2026 18:02", "Vor Systemaktualisierung", "number"),
            SnapshotRecord("327", "01.10.2026 12:00", "Manueller Snapshot", "number", source="ohc"),
            SnapshotRecord("326", "30.09.2026 18:00", "timeline", "timeline"),
            SnapshotRecord("325", "30.09.2026 08:14", "Wichtiger Stand", "number"),
        )
        self._render_snapshot_rows()
        self.snapshot_table.selectRow(1)

    def refresh_language(self) -> None:
        self._populate_report() if self.report else None
        self._refresh_authorization_state()



def build_page(host: QWidget) -> SnapshotManagerPage:
    return SnapshotManagerPage(host, getattr(host, "tr_static", lambda text: text))
