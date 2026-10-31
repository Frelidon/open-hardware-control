# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit Ubuntu installer hand-off for the TRCC Linux backend."""
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


def install_trcc(host: Any, after: Callable[[], None] | None = None) -> None:
    def next_step() -> None:
        if after:
            QTimer.singleShot(0, after)

    script = helper_script_path(
        Path(__file__).resolve().parents[3] / "kraken_control.py", "install-trcc.sh"
    )
    if not script.is_file():
        host.show_error(host.tr_static("Das TRCC-Installationsskript fehlt."))
        next_step()
        return
    try:
        check = subprocess.run(
            [str(script), "--check"], capture_output=True, text=True,
            timeout=8, check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        host.show_error(host.tr_static(
            "TRCC-Linux-Installation konnte nicht geprüft werden: {reason}"
        ).format(reason=exc))
        next_step()
        return
    if check.returncode == 0:
        QMessageBox.information(
            host, DISPLAY_NAME, host.tr_static("TRCC Linux ist bereits installiert.")
        )
        studio = getattr(host, "thermalright_display_studio", None)
        if studio is not None:
            studio.reload_backend_availability()
        next_step()
        return
    if check.stdout.strip() != "ubuntu":
        QMessageBox.information(
            host, DISPLAY_NAME,
            host.tr_static(
                "TRCC Linux für diese Distribution anhand der offiziellen Anleitung installieren."
            ),
        )
        QDesktopServices.openUrl(QUrl(
            "https://github.com/Lexonight1/thermalright-trcc-linux/blob/main/doc/GUIDE_INSTALL.md"
        ))
        next_step()
        return
    answer = QMessageBox.question(
        host, DISPLAY_NAME,
        host.tr_static(
            "TRCC Linux 9.10.4 aus dem offiziellen Projektpaket installieren? "
            "Administratorrechte sind erforderlich."
        ),
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
            host.log_message("LCD-TRCC: offizielles Ubuntu-Paket 9.10.4 installiert")
            QMessageBox.information(
                host, DISPLAY_NAME,
                host.tr_static("TRCC Linux wurde installiert. Die LCD-Bibliothek wird neu geladen."),
            )
            studio = getattr(host, "thermalright_display_studio", None)
            if studio is not None:
                studio.reload_backend_availability()
        else:
            host.show_error(host.tr_static(
                "TRCC-Linux-Installation fehlgeschlagen: {reason}"
            ).format(reason=result.combined or str(result.returncode)))
        next_step()

    host.backend.run_async([pkexec, str(script), "--install"], callback=done, timeout=900)
