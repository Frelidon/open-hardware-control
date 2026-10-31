# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure, explicit installation plans for supported Programs 1.0 formats."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shlex
import shutil


IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,199}$")
CHANNEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*(?:/[A-Za-z0-9][A-Za-z0-9_.-]*){0,2}$")
MAX_APPIMAGE_BYTES = 1024 * 1024 * 1024


class InstallPlanError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class InstallPlan:
    format: str
    summary: str
    command: tuple[str, ...] = ()
    appimage: Path | None = None

    @property
    def display_command(self) -> str:
        if self.appimage is not None:
            return f"chmod u+x {shlex.quote(str(self.appimage))}"
        return shlex.join(self.command)


def _identifier(raw: object) -> str:
    value = str(raw or "").strip()
    if IDENTIFIER_RE.fullmatch(value) is None:
        raise InstallPlanError("Die Programmkennung enthält ungültige Zeichen.")
    return value


def build_install_plan(program_format: object, identifier: object, version: object,
                       base_folder: Path) -> InstallPlan:
    selected = str(program_format or "")
    requested = str(version or "").strip()
    if selected == "Flatpak":
        flatpak = shutil.which("flatpak")
        app_id = _identifier(identifier)
        if flatpak is None:
            raise InstallPlanError("Flatpak ist auf diesem System nicht verfügbar.")
        if requested and IDENTIFIER_RE.fullmatch(requested) is None:
            raise InstallPlanError("Der Flatpak-Branch ist ungültig.")
        reference = f"{app_id}//{requested}" if requested else app_id
        return InstallPlan(selected, f"Flathub · Benutzerinstallation · {reference}",
                           (flatpak, "install", "--user", "-y", "flathub", reference))
    if selected == "Snap":
        snap, pkexec = shutil.which("snap"), shutil.which("pkexec")
        snap_name = _identifier(identifier)
        if snap is None or pkexec is None:
            raise InstallPlanError("Snap und Polkit sind für diese Installation erforderlich.")
        if requested and CHANNEL_RE.fullmatch(requested) is None:
            raise InstallPlanError("Der Snap-Channel ist ungültig.")
        command = [pkexec, snap, "install", snap_name]
        if requested:
            command.extend(("--channel", requested))
        return InstallPlan(selected, f"Snap Store · Systeminstallation · {requested or 'latest/stable'}", tuple(command))
    if selected == "AppImage":
        base = Path(base_folder).expanduser().resolve()
        candidate = Path(str(identifier or "")).expanduser()
        if candidate.is_symlink():
            raise InstallPlanError("Die gewählte Datei ist kein reguläres AppImage.")
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(base)
        except (OSError, ValueError) as exc:
            raise InstallPlanError("Das AppImage muss im gewählten Grundordner liegen.") from exc
        if not resolved.is_file() or not resolved.name.casefold().endswith(".appimage"):
            raise InstallPlanError("Die gewählte Datei ist kein reguläres AppImage.")
        size = resolved.stat().st_size
        if not 1 <= size <= MAX_APPIMAGE_BYTES:
            raise InstallPlanError("Die AppImage-Größe liegt außerhalb der Sicherheitsgrenze.")
        with resolved.open("rb") as stream:
            header = stream.read(12)
        if len(header) < 12 or not header.startswith(b"\x7fELF") or header[8:11] not in {b"AI\x01", b"AI\x02"}:
            raise InstallPlanError("Die Datei besitzt keinen erkannten AppImage-Kopf.")
        return InstallPlan(selected, "Lokales AppImage · nur für den aktuellen Benutzer ausführbar machen", appimage=resolved)
    raise InstallPlanError("Systempakete werden ohne bestätigte distributionsspezifische Paketquelle nicht automatisch installiert.")


def apply_appimage_plan(plan: InstallPlan) -> None:
    if plan.format != "AppImage" or plan.appimage is None:
        raise InstallPlanError("Dies ist kein AppImage-Plan.")
    current = plan.appimage.stat().st_mode
    os.chmod(plan.appimage, current | 0o100, follow_symlinks=False)
