"""First-run guidance and explicit, verified plugin installation UI."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Callable

from PySide6.QtCore import QProcess, QSettings, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .installer import automatic_install_supported, privileged_install_command


INTRO_SETTING = "wallpaper_engine/onboarding_1_1_complete"
STEAM_STORE_URL = QUrl("steam://store/431960")
STEAM_STORE_WEB_URL = QUrl("https://store.steampowered.com/app/431960/Wallpaper_Engine/")
WORKSHOP_URL = QUrl("https://steamcommunity.com/app/431960/workshop/")
UPSTREAM_URL = QUrl("https://github.com/CaptSilver/wallpaper-engine-kde-plugin/releases")


GUIDE_HTML = """
<h3>Wallpaper Engine in Open Hardware Control einrichten</h3>
<ol>
  <li><b>Wallpaper Engine über Steam installieren.</b> Wallpaper Engine selbst ist kostenpflichtige, separate Software und wird von OHC nicht mitgeliefert.</li>
  <li><b>Mindestens fünf Wallpaper im Workshop abonnieren.</b> Steam vollständig herunterladen lassen; so kann die Galerie sofort sinnvoll getestet werden.</li>
  <li><b>Wallpaper Engine for KDE installieren.</b> Fehlt das CaptSilver-Plugin, kann OHC das zu Fedora passende offizielle RPM herunterladen und dessen veröffentlichte SHA256-Prüfsumme kontrollieren.</li>
  <li><b>Plasma einrichten.</b> In „Originale Plasma-Oberfläche“ den Typ „Wallpaper Engine for KDE“ wählen und als Steam-Bibliothek den Ordner mit <code>steamapps</code> angeben, meistens <code>~/.local/share/Steam</code>.</li>
  <li><b>Bibliothek neu laden und testen.</b> Ein Wallpaper auswählen, den Zielbildschirm festlegen und anwenden. Eigene Videos gehören nur in einen getrennten kleinen Videoordner.</li>
  <li><b>Optional optimieren.</b> Erst nach einem erfolgreichen Test kann das reversible Leistungsprofil aktiviert werden. Der Originalzustand bleibt Standard.</li>
</ol>
<p><b>Wichtig:</b> Die Plugin-Installation beginnt nie automatisch. Nach dem Download fragt OHC nochmals nach; erst dann erscheint Polkits normale Passwortabfrage. OHC speichert kein Passwort.</p>
"""


class FirstStartDialog(QDialog):
    def __init__(self, owner: "WallpaperEngineOnboarding") -> None:
        super().__init__(owner)
        self.owner = owner
        self.setWindowTitle("Wallpaper Engine · Erste Einrichtung")
        self.setModal(True)
        self.setMinimumWidth(720)
        layout = QVBoxLayout(self)
        text = QLabel(GUIDE_HTML)
        text.setWordWrap(True)
        text.setOpenExternalLinks(False)
        layout.addWidget(text)
        quick = QHBoxLayout()
        steam = QPushButton("1 · Wallpaper Engine in Steam öffnen")
        steam.clicked.connect(owner.open_steam)
        workshop = QPushButton("2 · Workshop öffnen")
        workshop.clicked.connect(owner.open_workshop)
        install = QPushButton("3 · Plugin installieren")
        install.setEnabled(not owner.plugin_present)
        install.clicked.connect(self._install)
        quick.addWidget(steam)
        quick.addWidget(workshop)
        quick.addWidget(install)
        layout.addLayout(quick)
        close_row = QHBoxLayout()
        later = QPushButton("Später erneut zeigen")
        later.clicked.connect(self.reject)
        understood = QPushButton("Anleitung verstanden")
        understood.setDefault(True)
        understood.clicked.connect(self._complete)
        close_row.addStretch()
        close_row.addWidget(later)
        close_row.addWidget(understood)
        layout.addLayout(close_row)

    def _install(self) -> None:
        self.accept()
        self.owner.start_install()

    def _complete(self) -> None:
        self.owner.mark_intro_complete()
        self.accept()


class WallpaperEngineOnboarding(QGroupBox):
    """Persistent setup card plus an optional first-visit dialog."""

    def __init__(
        self,
        *,
        settings: QSettings,
        logger: Callable[[str], None],
        process_tracker: Callable[..., object] | None,
        install_changed: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__("Erste Einrichtung · Schritt für Schritt", parent)
        self.settings = settings
        self.logger = logger
        self.process_tracker = process_tracker
        self.install_changed = install_changed
        self.plugin_present = False
        self.download_process = QProcess(self)
        self.download_process.finished.connect(self._download_finished)
        self.install_process = QProcess(self)
        self.install_process.finished.connect(self._install_finished)

        layout = QVBoxLayout(self)
        guide = QLabel(GUIDE_HTML)
        guide.setWordWrap(True)
        guide.setOpenExternalLinks(False)
        layout.addWidget(guide)
        actions = QGridLayout()
        steam = QPushButton("Wallpaper Engine in Steam öffnen")
        steam.clicked.connect(self.open_steam)
        workshop = QPushButton("Workshop öffnen · mindestens 5 abonnieren")
        workshop.clicked.connect(self.open_workshop)
        self.install_button = QPushButton("Offizielles KDE-Plugin installieren")
        self.install_button.clicked.connect(self.start_install)
        upstream = QPushButton("Offizielle Plugin-Releases")
        upstream.clicked.connect(lambda: QDesktopServices.openUrl(UPSTREAM_URL))
        actions.addWidget(steam, 0, 0)
        actions.addWidget(workshop, 0, 1)
        actions.addWidget(self.install_button, 1, 0)
        actions.addWidget(upstream, 1, 1)
        layout.addLayout(actions)
        self.checklist = QLabel("Einrichtungsstatus wird geprüft …")
        self.checklist.setWordWrap(True)
        layout.addWidget(self.checklist)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)
        self.install_status = QLabel("Die Installation wird nur nach ausdrücklicher Bestätigung gestartet.")
        self.install_status.setWordWrap(True)
        layout.addWidget(self.install_status)

    def update_runtime_state(self, *, plugin: bool, steam_library: Path, wallpaper_count: int, active_surfaces: int) -> None:
        self.plugin_present = plugin
        supported, support_text = automatic_install_supported()
        self.install_button.setEnabled(not plugin and supported and not self._busy())
        self.install_button.setText("KDE-Plugin ist installiert" if plugin else "Offizielles KDE-Plugin installieren")
        checks = (
            f"{'✓' if plugin else '○'} KDE-Plugin · "
            f"{'✓' if (steam_library / 'steamapps').is_dir() else '○'} Steam-Bibliothek · "
            f"{'✓' if wallpaper_count >= 5 else '○'} Workshop-Wallpaper {wallpaper_count}/5 · "
            f"{'✓' if active_surfaces else '○'} Plasma-Fläche aktiviert"
        )
        self.checklist.setText(f"{checks}\nAutomatischer Installer: {support_text}")

    def intro_complete(self) -> bool:
        return self.settings.value(INTRO_SETTING, False, type=bool)

    def mark_intro_complete(self) -> None:
        self.settings.setValue(INTRO_SETTING, True)
        self.settings.sync()

    def show_first_start_dialog(self, *, force: bool = False) -> None:
        if os.environ.get("OHC_DISABLE_HARDWARE_IO") == "1":
            return
        if not force and self.intro_complete():
            return
        FirstStartDialog(self).exec()

    def open_steam(self) -> None:
        if not QDesktopServices.openUrl(STEAM_STORE_URL):
            QDesktopServices.openUrl(STEAM_STORE_WEB_URL)

    def open_workshop(self) -> None:
        QDesktopServices.openUrl(WORKSHOP_URL)

    def start_install(self) -> None:
        if self.plugin_present:
            self.install_status.setText("Das KDE-Plugin ist bereits installiert.")
            return
        supported, detail = automatic_install_supported()
        if not supported:
            QMessageBox.information(self, "Automatische Installation nicht verfügbar", detail)
            return
        answer = QMessageBox.question(
            self,
            "Offizielles Plugin herunterladen?",
            "OHC lädt das zu diesem Fedora passende RPM ausschließlich vom offiziellen CaptSilver-GitHub-Release. "
            "Vor einer Installation werden Dateiname, Größe und veröffentlichte SHA256-Prüfsumme geprüft. Fortfahren?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        if self._busy():
            return
        helper = Path(__file__).with_name("installer.py")
        self.download_process.setProgram(sys.executable)
        self.download_process.setArguments([str(helper)])
        self._track(self.download_process, "wallpaper-plugin-download")
        self.download_process.start()
        self.progress.show()
        self.install_button.setEnabled(False)
        self.install_status.setText("Offizielles Plugin-RPM wird heruntergeladen und per SHA256 geprüft …")
        self.logger("WALLPAPER ENGINE: bestätigter offizieller Plugin-Download gestartet")

    def _download_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        self.progress.hide()
        stderr = bytes(self.download_process.readAllStandardError()).decode("utf-8", "replace").strip()
        stdout = bytes(self.download_process.readAllStandardOutput()).decode("utf-8", "replace").strip()
        if exit_status != QProcess.ExitStatus.NormalExit or exit_code != 0:
            detail = stderr.splitlines()[-1][:400] if stderr else f"Exit-Code {exit_code}"
            self._fail(f"Download oder Prüfung fehlgeschlagen: {detail}")
            return
        try:
            result = json.loads(stdout.splitlines()[-1])
            package = Path(str(result["path"]))
            command = privileged_install_command(package, str(result["sha256"]))
        except (IndexError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            command = []
        if not command:
            self._fail("Das geprüfte RPM liegt nicht im geschützten OHC-Installer-Cache.")
            return
        answer = QMessageBox.question(
            self,
            "Plugin jetzt mit Administratorrechten installieren?",
            "Die SHA256-Prüfung ist erfolgreich. DNF darf das offizielle RPM jetzt systemweit installieren. "
            "Im nächsten Fenster fragt Polkit nach deinem Administratorpasswort; OHC kann das Passwort weder sehen noch speichern.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.install_status.setText("RPM geprüft und zwischengespeichert; die Installation wurde nicht gestartet.")
            self.install_button.setEnabled(True)
            return
        self.install_process.setProgram(command[0])
        self.install_process.setArguments(command[1:])
        self._track(self.install_process, "wallpaper-plugin-install")
        self.install_process.start()
        self.progress.show()
        self.install_status.setText("Warte auf Polkit-Passwortabfrage und DNF-Installation …")
        self.logger("WALLPAPER ENGINE: bestätigte Plugin-Installation an Polkit/DNF übergeben")

    def _install_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        self.progress.hide()
        stderr = bytes(self.install_process.readAllStandardError()).decode("utf-8", "replace").strip()
        stdout = bytes(self.install_process.readAllStandardOutput()).decode("utf-8", "replace").strip()
        if exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0:
            self.install_status.setText(
                "Plugin erfolgreich installiert. Öffne nun die originale Plasma-Oberfläche und wähle „Wallpaper Engine for KDE“."
            )
            self.logger("WALLPAPER ENGINE: offizielles CaptSilver-Plugin erfolgreich installiert")
            self.install_changed()
            return
        output = stderr or stdout
        detail = output.splitlines()[-1][:400] if output else f"Exit-Code {exit_code}"
        self._fail(f"Installation nicht abgeschlossen: {detail}")

    def _busy(self) -> bool:
        return any(process.state() != QProcess.ProcessState.NotRunning for process in (self.download_process, self.install_process))

    def _fail(self, message: str) -> None:
        self.install_status.setText(message)
        self.install_button.setEnabled(not self.plugin_present)
        self.logger(f"WALLPAPER ENGINE FEHLER: {message}")

    def _track(self, process: QProcess, label: str) -> None:
        if self.process_tracker is None:
            return
        try:
            self.process_tracker(process, label)
        except TypeError:
            self.process_tracker(process)
