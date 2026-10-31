# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit, distribution-aware LACT installation from documented sources."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
from typing import Any, Callable

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox

from app_constants import DISPLAY_NAME, helper_script_path
from command_backend import CommandResult


def install_lact(host: Any, after: Callable[[], None] | None = None) -> None:
    def next_step() -> None:
        if after:
            QTimer.singleShot(0, after)

    script = helper_script_path(Path(__file__).resolve().parents[3] / "kraken_control.py", "install-lact.sh")
    if not script.is_file():
        host.show_error(host.tr_static("Das LACT-Installationsskript fehlt."))
        next_step()
        return
    try:
        check = subprocess.run([str(script), "--check"], capture_output=True,
                               text=True, timeout=8, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        host.show_error(host.tr_static("LACT-Installation konnte nicht geprüft werden: {reason}").format(reason=exc))
        next_step()
        return
    if check.stdout.strip() not in {"fedora", "arch", "ubuntu"}:
        QMessageBox.information(host, DISPLAY_NAME, host.tr_static("LACT für diese Distribution über das offizielle Paket installieren; anschließend lactd aktivieren."))
        QDesktopServices.openUrl(QUrl("https://github.com/ilya-zlobintsev/LACT#installation"))
        next_step()
        return
    sources = {
        "fedora": "Fedora COPR ilyaz/LACT",
        "arch": "Arch-Paketquelle",
        "ubuntu": "offizielles LACT-Paket für Ubuntu 26.04",
    }
    source = sources[check.stdout.strip()]
    answer = QMessageBox.question(
        host, DISPLAY_NAME,
        host.tr_static("LACT 0.10.1 oder neuer aus {source} installieren/aktualisieren und lactd aktivieren? Administratorrechte sind erforderlich.").format(source=source),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    if answer != QMessageBox.StandardButton.Yes:
        next_step()
        return
    pkexec = shutil.which("pkexec")
    if not pkexec:
        host.show_error(host.tr_static("pkexec/Polkit ist für die Installation erforderlich."))
        next_step()
        return

    def done(result: CommandResult) -> None:
        if result.ok:
            host.log_message("GPU-LACT: Paket installiert/aktualisiert · Dienst gestartet")
            QMessageBox.information(host, DISPLAY_NAME, host.tr_static("LACT installiert. GPU-Zugriff wird erneut geprüft."))
            host.gpu_control_page.refresh()
        else:
            host.show_error(host.tr_static("LACT-Installation fehlgeschlagen: {reason}").format(
                reason=result.combined or str(result.returncode)))
        next_step()

    host.backend.run_async([pkexec, str(script), "--install"], callback=done, timeout=900)
