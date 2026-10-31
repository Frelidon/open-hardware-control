#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit manual snapshot and fixed-root setup actions."""

from __future__ import annotations

from PySide6.QtCore import QTimer


class SnapshotActionMixin:
    def load_snapshots(self, _checked: bool = False, *, after_create: bool = False) -> None:
        config = str(self.config_combo.currentData() or "")
        if config:
            if after_create and self.pending_created_snapshot:
                self.snapshot_action_status.setText(
                    self.tr("Snapshot {number} wurde erstellt · Liste wird aktualisiert …").format(
                        number=self.pending_created_snapshot,
                    )
                )
            else:
                self.snapshot_action_status.setText(self.tr("Snapshot-Liste wird geladen …"))
            if not self.run_helper("list", [config]) and after_create:
                self.snapshot_action_status.setText(
                    self.tr("Snapshot {number} wurde erstellt · Liste später manuell aktualisieren.").format(
                        number=self.pending_created_snapshot or "—",
                    )
                )
                self.pending_created_snapshot = ""

    def create_snapshot_now(self) -> None:
        config = str(self.config_combo.currentData() or "")
        description = self.snapshot_description.text().strip()
        self.pending_created_snapshot = ""
        if not description:
            self.snapshot_action_status.setText(self.tr("Bitte eine kurze Snapshot-Beschreibung eingeben."))
            return
        if not config:
            if self._can_setup_root():
                self.pending_snapshot_after_setup = description
                if self.run_helper("setup-root", []):
                    self.snapshot_create.setEnabled(False)
                    self.snapshot_action_status.setText(self.tr(
                        "Administratorfreigabe wird angefordert · OHC richtet Snapper für das Root-Dateisystem ein und erstellt danach den Snapshot."
                    ))
                else:
                    self.pending_snapshot_after_setup = ""
                return
            self.snapshot_action_status.setText(self.tr("Zuerst eine Snapper-Konfiguration auswählen."))
            return
        if self.helper_process is not None:
            self.pending_manual_snapshot = (config, description)
            self.snapshot_action_status.setText(self.tr(
                "Manueller Snapshot vorgemerkt · wird unabhängig von Automatikpausen direkt nach der laufenden Aktion erstellt."
            ))
            self._log(
                f"Manueller Snapshot vorgemerkt · Automatikmodus={self.manual_mode} · "
                f"Helfer belegt durch {self.pending_helper_action or 'unbekannt'}"
            )
            return
        if self.run_helper("create", [config, description]):
            self.snapshot_create.setEnabled(False)
            self.snapshot_action_status.setText(self.tr(
                "Manueller Snapshot wird erstellt · Automatikpausen werden ignoriert."
            ))

    def setup_snapper_root(self) -> None:
        self.pending_snapshot_after_setup = ""
        if self.run_helper("setup-root", []):
            self.snapper_setup_button.setEnabled(False)
            self.snapper_setup_status.setText(self.tr(
                "KDE-Administratorfreigabe wird angefordert · danach wird nur die Snapper-Konfiguration „root“ angelegt."
            ))

    def _can_setup_root(self) -> bool:
        filesystems = self.report.get("filesystems") if isinstance(self.report.get("filesystems"), list) else []
        backends = self.report.get("backends") if isinstance(self.report.get("backends"), list) else []
        root_btrfs = any(isinstance(item, dict) and item.get("target") == "/" and item.get("fstype") == "btrfs"
                         for item in filesystems)
        snapper = any(isinstance(item, dict) and item.get("id") == "snapper" and item.get("available")
                      for item in backends)
        return bool(root_btrfs and snapper)

    def _dispatch_pending_manual_snapshot(self) -> None:
        """Give an explicit user snapshot priority over every automation pause."""

        pending, self.pending_manual_snapshot = self.pending_manual_snapshot, None
        if pending is None:
            return
        config, description = pending
        self._log(
            f"Manueller Snapshot startet mit Vorrang · Automatikmodus={self.manual_mode} wird ignoriert"
        )
        if self.run_helper("create", [config, description]):
            self.snapshot_create.setEnabled(False)
            self.snapshot_action_status.setText(self.tr(
                "Manueller Snapshot wird erstellt · Automatikpausen werden ignoriert."
            ))

    def _refresh_snapshots_after_create(self, attempt: int = 0) -> None:
        """Refresh the list without hiding a successfully completed write."""

        if not self.pending_created_snapshot:
            return
        if self.helper_process is not None:
            if attempt < 20:
                QTimer.singleShot(
                    500, self, lambda retry=attempt + 1: self._refresh_snapshots_after_create(retry),
                )
                return
            self.snapshot_action_status.setText(
                self.tr("Snapshot {number} wurde erstellt · Liste später manuell aktualisieren.").format(
                    number=self.pending_created_snapshot,
                )
            )
            self.pending_created_snapshot = ""
            return
        self.load_snapshots(after_create=True)

    def _create_after_root_setup(self, description: str) -> None:
        if self.run_helper("create", ["root", description]):
            self.snapshot_action_status.setText(self.tr("Administratorfreigabe bestätigt · Snapshot wird erstellt …"))
