# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-blocking Programs inventory and profile page."""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QProcess, QThread, Signal, Qt
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox,
    QPushButton, QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from .model import (
    InstalledProgram, ProgramProfile, desktop_programs, dump_profiles,
    load_profiles, normalize_base_folder, profile_from_program,
)
from .github_release import (
    GitHubReleaseError, ReleasePlan, download_release, downloaded_appimages,
    inspect_release, normalize_repository,
)
from .install_plan import InstallPlanError, apply_appimage_plan, build_install_plan


class InventoryWorker(QObject):
    completed = Signal(object)
    failed = Signal(str)

    def run(self) -> None:
        try:
            thread = QThread.currentThread()
            self.completed.emit(desktop_programs(cancelled=thread.isInterruptionRequested))
        except Exception as exc:  # UI boundary: report, never crash the main loop.
            self.failed.emit(type(exc).__name__)


class GitHubWorker(QObject):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, action: str, repository: str, version: str,
                 base_folder: Path, plan: ReleasePlan | None = None) -> None:
        super().__init__()
        self.action, self.repository, self.version = action, repository, version
        self.base_folder, self.plan = base_folder, plan

    def run(self) -> None:
        try:
            thread = QThread.currentThread()
            if self.action == "inspect":
                result = inspect_release(self.repository, self.version)
            elif self.plan is not None:
                result = download_release(
                    self.plan, self.base_folder,
                    cancelled=thread.isInterruptionRequested,
                )
            else:
                raise GitHubReleaseError("Release wurde noch nicht geprüft.")
            self.completed.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc)[:500] or type(exc).__name__)


class ProgramsPage(QScrollArea):
    def __init__(self, host: QWidget, translate: Callable[[str], str]) -> None:
        super().__init__(host)
        self.host, self.tr_text = host, translate
        self.programs: tuple[InstalledProgram, ...] = ()
        self.profiles = load_profiles(host.settings.value("programs/profiles", "[]"))
        self._thread: QThread | None = None
        self._worker: InventoryWorker | None = None
        self._github_thread: QThread | None = None
        self._github_worker: GitHubWorker | None = None
        self.release_plan: ReleasePlan | None = None
        self.install_process: QProcess | None = None
        self._install_output = bytearray()
        self.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(20, 18, 20, 24)
        title = QLabel(self.tr_text("Programme")); title.setObjectName("pageTitle"); layout.addWidget(title)
        hint = QLabel(self.tr_text("Installierte Programme erkennen und wiederverwendbare Installationsprofile vorbereiten."))
        hint.setWordWrap(True); hint.setObjectName("muted"); layout.addWidget(hint)

        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel(self.tr_text("Grundordner")))
        self.base_folder = QLineEdit(str(normalize_base_folder(host.settings.value("programs/base_folder", ""))))
        self.base_folder.editingFinished.connect(self.save_base_folder)
        choose = QPushButton(self.tr_text("Ordner auswählen …")); choose.clicked.connect(self.choose_folder)
        folder_row.addWidget(self.base_folder, 1); folder_row.addWidget(choose); layout.addLayout(folder_row)

        controls = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText(self.tr_text("Programme durchsuchen …"))
        self.search.textChanged.connect(self.render_inventory)
        self.refresh_button = QPushButton(self.tr_text("Installierte Programme neu laden"))
        self.refresh_button.clicked.connect(self.refresh_inventory)
        controls.addWidget(self.search, 1); controls.addWidget(self.refresh_button); layout.addLayout(controls)

        self.status = QLabel(self.tr_text("Programmliste wurde noch nicht geladen.")); self.status.setObjectName("muted")
        layout.addWidget(self.status)
        self.inventory = QTableWidget(0, 3)
        self.inventory.setHorizontalHeaderLabels((self.tr_text("Programm"), self.tr_text("Format"), self.tr_text("Kennung / ausführbare Datei")))
        self.inventory.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.inventory.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.inventory.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.inventory.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.inventory)
        save = QPushButton(self.tr_text("Auswahl als Installationsprofil speichern")); save.clicked.connect(self.add_profile)
        layout.addWidget(save, 0, Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(QLabel(self.tr_text("Gespeicherte Installationsprofile"), objectName="sectionTitle"))
        self.profile_table = QTableWidget(0, 4)
        self.profile_table.setHorizontalHeaderLabels((self.tr_text("Programm"), self.tr_text("Format"), self.tr_text("Version / Kennung"), self.tr_text("GitHub-Projekt")))
        self.profile_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.profile_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.profile_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.profile_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.profile_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.profile_table.itemSelectionChanged.connect(self.load_selected_profile_source)
        layout.addWidget(self.profile_table)
        profile_editor = QHBoxLayout()
        self.profile_name = QLineEdit(); self.profile_name.setPlaceholderText(self.tr_text("Profilname"))
        self.profile_format = QComboBox()
        for item in ("System", "Flatpak", "Snap", "AppImage"): self.profile_format.addItem(item, item)
        self.profile_identifier = QLineEdit(); self.profile_identifier.setPlaceholderText(self.tr_text("App-ID, Snap-Name oder AppImage-Pfad"))
        self.profile_version = QLineEdit(); self.profile_version.setPlaceholderText(self.tr_text("Flatpak-Branch oder Snap-Channel (optional)"))
        save_manual = QPushButton(self.tr_text("Profil hinzufügen")); save_manual.clicked.connect(self.add_manual_profile)
        for widget, stretch in ((self.profile_name, 1), (self.profile_format, 0), (self.profile_identifier, 2), (self.profile_version, 1), (save_manual, 0)):
            profile_editor.addWidget(widget, stretch)
        layout.addLayout(profile_editor)
        profile_actions = QHBoxLayout()
        self.install_button = QPushButton(self.tr_text("Ausgewähltes Profil installieren")); self.install_button.clicked.connect(self.install_selected_profile)
        assign_source = QPushButton(self.tr_text("GitHub-Projekt zuordnen")); assign_source.clicked.connect(self.assign_github_source)
        remove = QPushButton(self.tr_text("Ausgewähltes Profil entfernen")); remove.clicked.connect(self.remove_profile)
        profile_actions.addWidget(self.install_button); profile_actions.addWidget(assign_source); profile_actions.addWidget(remove); profile_actions.addStretch()
        layout.addLayout(profile_actions)
        self.install_status = QLabel(self.tr_text("Keine Installation aktiv.")); self.install_status.setWordWrap(True); self.install_status.setObjectName("muted")
        layout.addWidget(self.install_status)
        note = QLabel(self.tr_text("Installationsbefehle bleiben getrennt. GitHub wird nur nach einem ausdrücklichen Prüfen- oder Download-Klick kontaktiert."))
        note.setWordWrap(True); note.setObjectName("muted"); layout.addWidget(note)

        layout.addWidget(QLabel(self.tr_text("GitHub-Release herunterladen"), objectName="sectionTitle"))
        github_row = QHBoxLayout()
        self.github_repository = QLineEdit(str(host.settings.value("programs/github_repository", "") or "")); self.github_repository.setPlaceholderText(self.tr_text("Besitzer/Repository oder GitHub-URL"))
        self.github_version = QLineEdit(str(host.settings.value("programs/github_version", "") or "")); self.github_version.setPlaceholderText(self.tr_text("Version leer lassen für neuestes Release"))
        self.github_check = QPushButton(self.tr_text("Release prüfen")); self.github_check.clicked.connect(self.inspect_github_release)
        github_row.addWidget(self.github_repository, 2); github_row.addWidget(self.github_version, 1); github_row.addWidget(self.github_check)
        layout.addLayout(github_row)
        self.github_status = QLabel(self.tr_text("Noch kein GitHub-Release geprüft.")); self.github_status.setWordWrap(True); self.github_status.setObjectName("muted")
        layout.addWidget(self.github_status)
        self.github_download = QPushButton(self.tr_text("Alle Dateien und Source-Code herunterladen"))
        self.github_download.setEnabled(False); self.github_download.clicked.connect(self.download_github_release)
        layout.addWidget(self.github_download, 0, Qt.AlignmentFlag.AlignLeft)
        appimage_row = QHBoxLayout()
        appimage_row.addWidget(QLabel(self.tr_text("Heruntergeladenes AppImage")))
        self.github_appimage = QComboBox()
        self.github_appimage.addItem(self.tr_text("Kein heruntergeladenes AppImage verfügbar"), "")
        self.assign_appimage_button = QPushButton(self.tr_text("AppImage dem ausgewählten Profil zuweisen"))
        self.assign_appimage_button.setEnabled(False)
        self.assign_appimage_button.clicked.connect(self.assign_downloaded_appimage)
        appimage_row.addWidget(self.github_appimage, 1)
        appimage_row.addWidget(self.assign_appimage_button)
        layout.addLayout(appimage_row)
        layout.addStretch(); self.setWidget(body); self.render_profiles()
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.stop)

    def choose_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, self.tr_text("Grundordner auswählen"), self.base_folder.text())
        if selected:
            self.base_folder.setText(selected); self.save_base_folder()

    def save_base_folder(self) -> None:
        folder = normalize_base_folder(self.base_folder.text())
        self.base_folder.setText(str(folder))
        self.host.settings.setValue("programs/base_folder", str(folder)); self.host.settings.sync()

    def refresh_inventory(self) -> None:
        if self._thread is not None:
            return
        self.refresh_button.setEnabled(False); self.status.setText(self.tr_text("Installierte Programme werden im Hintergrund gelesen …"))
        thread = QThread(self); worker = InventoryWorker(); worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.completed.connect(self._inventory_ready); worker.failed.connect(self._inventory_failed)
        worker.completed.connect(thread.quit); worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater); thread.finished.connect(self._scan_finished)
        self._thread, self._worker = thread, worker
        thread.start()

    def _inventory_ready(self, values: object) -> None:
        self.programs = tuple(values) if isinstance(values, tuple) else ()
        self.status.setText(self.tr_text("{count} installierte Programme erkannt.").format(count=len(self.programs)))
        self.render_inventory()

    def _inventory_failed(self, reason: str) -> None:
        self.status.setText(self.tr_text("Programmliste konnte nicht gelesen werden: {reason}").format(reason=reason))

    def _scan_finished(self) -> None:
        if self._thread is not None:
            self._thread.deleteLater()
        self._thread = None; self._worker = None; self.refresh_button.setEnabled(True)

    def inspect_github_release(self) -> None:
        self.release_plan = None; self.github_download.setEnabled(False)
        self.host.settings.setValue("programs/github_repository", self.github_repository.text().strip())
        self.host.settings.setValue("programs/github_version", self.github_version.text().strip())
        self.host.settings.sync()
        self._start_github("inspect", None)

    def download_github_release(self) -> None:
        if self.release_plan is None:
            return
        count = len(self.release_plan.items)
        answer = QMessageBox.question(
            self, self.tr_text("GitHub-Release herunterladen"),
            self.tr_text("{count} Dateien einschließlich beider Source-Code-Archive nach {folder} herunterladen?").format(
                count=count, folder=self.base_folder.text(),
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self._start_github("download", self.release_plan)

    def _start_github(self, action: str, plan: ReleasePlan | None) -> None:
        if self._github_thread is not None:
            return
        self.save_base_folder()
        thread = QThread(self)
        worker = GitHubWorker(action, self.github_repository.text(), self.github_version.text(),
                              Path(self.base_folder.text()), plan)
        worker.moveToThread(thread); thread.started.connect(worker.run)
        worker.completed.connect(self._github_ready); worker.failed.connect(self._github_failed)
        worker.completed.connect(thread.quit); worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater); thread.finished.connect(self._github_finished)
        self._github_thread, self._github_worker = thread, worker
        self.github_check.setEnabled(False); self.github_download.setEnabled(False)
        self.github_status.setText(self.tr_text("GitHub-Anfrage läuft im Hintergrund …"))
        thread.start()

    def _github_ready(self, result: object) -> None:
        if isinstance(result, ReleasePlan):
            self.release_plan = result
            total = sum(item.size or 0 for item in result.items)
            self.github_status.setText(self.tr_text("Release {tag} · {count} Dateien · gemeldete Assets {size}").format(
                tag=result.tag, count=len(result.items), size=self._format_bytes(total),
            ))
            self.github_download.setEnabled(True)
            self._refresh_downloaded_appimages()
        elif isinstance(result, Path):
            self.github_status.setText(self.tr_text("Release vollständig geprüft gespeichert: {folder}").format(folder=result))
            self._refresh_downloaded_appimages()

    def _github_failed(self, reason: str) -> None:
        self.github_status.setText(self.tr_text("GitHub-Vorgang fehlgeschlagen: {reason}").format(reason=reason))

    def _github_finished(self) -> None:
        if self._github_thread is not None:
            self._github_thread.deleteLater()
        self._github_thread = None; self._github_worker = None; self.github_check.setEnabled(True)
        self.github_download.setEnabled(self.release_plan is not None)

    @staticmethod
    def _format_bytes(value: int) -> str:
        amount = float(max(0, value))
        for unit in ("B", "KiB", "MiB", "GiB"):
            if amount < 1024 or unit == "GiB":
                return f"{amount:.1f} {unit}"
            amount /= 1024
        return f"{amount:.1f} GiB"

    def render_inventory(self, *_args: object) -> None:
        query = self.search.text().strip().casefold()
        visible = tuple(item for item in self.programs if not query or query in item.name.casefold() or query in item.identifier.casefold())
        self.inventory.setRowCount(len(visible))
        for row, program in enumerate(visible):
            for column, value in enumerate((program.name, program.format, program.identifier)):
                cell = QTableWidgetItem(value); cell.setData(Qt.ItemDataRole.UserRole, program); self.inventory.setItem(row, column, cell)

    def add_profile(self) -> None:
        row = self.inventory.currentRow()
        cell = self.inventory.item(row, 0) if row >= 0 else None
        program = cell.data(Qt.ItemDataRole.UserRole) if cell is not None else None
        if not isinstance(program, InstalledProgram):
            QMessageBox.information(self, self.tr_text("Programme"), self.tr_text("Bitte zuerst ein erkanntes Programm auswählen.")); return
        profile = profile_from_program(program)
        key = profile.format.casefold(), profile.identifier.casefold()
        self.profiles = tuple(item for item in self.profiles if (item.format.casefold(), item.identifier.casefold()) != key) + (profile,)
        self._save_profiles(); self.render_profiles()

    def remove_profile(self) -> None:
        row = self.profile_table.currentRow()
        if not 0 <= row < len(self.profiles):
            return
        self.profiles = self.profiles[:row] + self.profiles[row + 1:]
        self._save_profiles(); self.render_profiles()

    def add_manual_profile(self) -> None:
        profile = ProgramProfile(
            self.profile_name.text().strip()[:160], self.profile_identifier.text().strip()[:1024],
            str(self.profile_format.currentData()), self.profile_version.text().strip()[:80],
        )
        if not profile.name or not profile.identifier:
            QMessageBox.information(self, self.tr_text("Programme"), self.tr_text("Profilname und Programmkennung sind erforderlich.")); return
        validated = load_profiles(dump_profiles((profile,)))
        if not validated:
            QMessageBox.warning(self, self.tr_text("Programme"), self.tr_text("Das Installationsprofil ist ungültig.")); return
        key = profile.format.casefold(), profile.identifier.casefold()
        self.profiles = tuple(item for item in self.profiles if (item.format.casefold(), item.identifier.casefold()) != key) + (profile,)
        self._save_profiles(); self.render_profiles()

    def install_selected_profile(self) -> None:
        if self.install_process is not None:
            return
        row = self.profile_table.currentRow()
        if not 0 <= row < len(self.profiles):
            QMessageBox.information(self, self.tr_text("Programme"), self.tr_text("Bitte zuerst ein Installationsprofil auswählen.")); return
        profile = self.profiles[row]
        try:
            plan = build_install_plan(profile.format, profile.identifier, profile.version, Path(self.base_folder.text()))
        except InstallPlanError as exc:
            QMessageBox.warning(self, self.tr_text("Installation nicht möglich"), self.tr_text(str(exc))); return
        answer = QMessageBox.question(
            self, self.tr_text("Installation bestätigen"),
            self.tr_text("Diesen geprüften Plan jetzt ausführen?\n\n{summary}\n\nBefehl: {command}").format(
                summary=plan.summary, command=plan.display_command,
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        if plan.appimage is not None:
            try:
                apply_appimage_plan(plan)
            except (InstallPlanError, OSError) as exc:
                self.install_status.setText(self.tr_text("Installation fehlgeschlagen: {reason}").format(reason=str(exc))); return
            self.install_status.setText(self.tr_text("AppImage wurde für den aktuellen Benutzer ausführbar gemacht.")); return
        process = QProcess(self); process.setProgram(plan.command[0]); process.setArguments(list(plan.command[1:]))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        process.readyRead.connect(self._read_install_output)
        process.finished.connect(self._install_finished); process.errorOccurred.connect(self._install_error)
        self.install_process = process; self.install_button.setEnabled(False)
        self._install_output.clear()
        self.install_status.setText(self.tr_text("Installation läuft …")); process.start()

    def _read_install_output(self) -> None:
        if self.install_process is None:
            return
        chunk = bytes(self.install_process.readAll())
        self._install_output.extend(chunk[-65_536:])
        if len(self._install_output) > 65_536:
            del self._install_output[:-65_536]

    def _install_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        process = self.install_process
        self._read_install_output()
        output = bytes(self._install_output).decode("utf-8", errors="replace")[-1000:]
        self.install_status.setText(
            self.tr_text("Installation abgeschlossen.") if exit_code == 0
            else self.tr_text("Installation fehlgeschlagen: {reason}").format(reason=output.strip() or f"Exit {exit_code}")
        )
        if process is not None: process.deleteLater()
        self.install_process = None; self.install_button.setEnabled(True)

    def _install_error(self, _error: QProcess.ProcessError) -> None:
        if self.install_process is None:
            return
        self.install_status.setText(self.tr_text("Installation konnte nicht gestartet werden: {reason}").format(reason=self.install_process.errorString()))

    def _save_profiles(self) -> None:
        self.host.settings.setValue("programs/profiles", dump_profiles(self.profiles)); self.host.settings.sync()

    def assign_github_source(self) -> None:
        row = self.profile_table.currentRow()
        if not 0 <= row < len(self.profiles):
            QMessageBox.information(self, self.tr_text("Programme"), self.tr_text("Bitte zuerst ein Installationsprofil auswählen.")); return
        try:
            repository = normalize_repository(self.github_repository.text())
        except GitHubReleaseError as exc:
            QMessageBox.warning(self, self.tr_text("Programme"), self.tr_text(str(exc))); return
        current = self.profiles[row]
        release = self.release_plan.tag if self.release_plan and self.release_plan.repository == repository else self.github_version.text().strip()
        self.profiles = self.profiles[:row] + (ProgramProfile(
            current.name, current.identifier, current.format, current.version,
            current.executable, repository, release,
        ),) + self.profiles[row + 1:]
        self.host.settings.setValue("programs/github_version", release)
        self._save_profiles(); self.render_profiles(); self.profile_table.selectRow(row)
        self.install_status.setText(self.tr_text("GitHub-Projekt {repository} wurde dem Profil zugeordnet.").format(repository=repository))

    def _refresh_downloaded_appimages(self) -> None:
        self.github_appimage.clear()
        paths = downloaded_appimages(self.release_plan, Path(self.base_folder.text())) if self.release_plan else ()
        if not paths:
            self.github_appimage.addItem(self.tr_text("Kein heruntergeladenes AppImage verfügbar"), "")
            self.assign_appimage_button.setEnabled(False)
            return
        for path in paths:
            self.github_appimage.addItem(path.name, str(path))
        self.assign_appimage_button.setEnabled(True)

    def assign_downloaded_appimage(self) -> None:
        row = self.profile_table.currentRow()
        if not 0 <= row < len(self.profiles) or self.profiles[row].format != "AppImage":
            QMessageBox.information(
                self, self.tr_text("Programme"),
                self.tr_text("Bitte zuerst ein AppImage-Profil auswählen."),
            )
            return
        selected = str(self.github_appimage.currentData() or "")
        available = downloaded_appimages(self.release_plan, Path(self.base_folder.text())) if self.release_plan else ()
        path = next((item for item in available if str(item) == selected), None)
        if path is None:
            self._refresh_downloaded_appimages()
            QMessageBox.warning(
                self, self.tr_text("Programme"),
                self.tr_text("Kein heruntergeladenes AppImage verfügbar"),
            )
            return
        current = self.profiles[row]
        self.profiles = self.profiles[:row] + (ProgramProfile(
            current.name, str(path), current.format, current.version,
            current.executable, self.release_plan.repository, self.release_plan.tag,
        ),) + self.profiles[row + 1:]
        self._save_profiles(); self.render_profiles(); self.profile_table.selectRow(row)
        self.install_status.setText(self.tr_text("Das ausgewählte AppImage wurde dem Profil zugeordnet."))

    def load_selected_profile_source(self) -> None:
        row = self.profile_table.currentRow()
        if not 0 <= row < len(self.profiles):
            return
        profile = self.profiles[row]
        if profile.repository:
            self.github_repository.setText(profile.repository)
            self.github_version.setText(profile.source_version)

    def render_profiles(self) -> None:
        self.profile_table.setRowCount(len(self.profiles))
        for row, profile in enumerate(self.profiles):
            detail = f"{profile.version} · {profile.identifier}" if profile.version else profile.identifier
            for column, value in enumerate((profile.name, profile.format, detail, profile.repository or "—")):
                self.profile_table.setItem(row, column, QTableWidgetItem(value))

    def stop(self) -> None:
        if self._thread is not None:
            self._thread.requestInterruption(); self._thread.quit(); self._thread.wait(1500)
        if self._github_thread is not None:
            self._github_thread.requestInterruption(); self._github_thread.quit(); self._github_thread.wait(2000)
        if self.install_process is not None and self.install_process.state() != QProcess.ProcessState.NotRunning:
            self.install_process.terminate(); self.install_process.waitForFinished(1500)

    def refresh_language(self) -> None:
        self.render_inventory(); self.render_profiles()


def build_page(host: QWidget) -> ProgramsPage:
    return ProgramsPage(host, getattr(host, "tr_static", lambda text: text))
