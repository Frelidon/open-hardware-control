#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Safe, transactional KDE Plasma designs for Open Hardware Control.

Only local KDE components and original OHC artwork are used. Applying a design
creates a backup and a recovery marker before any Plasma file is changed.
Backups can be selected, pruned, exported and safely imported.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Mapping

from desktop_assets import (
    CURSOR_THEMES,
    ICON_THEMES,
    DesktopAssetError,
    cursor_theme_name,
    data_root,
    desktop_asset_status,
    icon_theme_name,
    install_desktop_assets,
)


SCHEMA_VERSION = 2
SUPPORTED_BACKUP_SCHEMAS = (1, 2)
SUPPORTED_STYLES = ("windows11", "macos", "windows8", "windows81")
SUPPORTED_MODES = ("dark", "light")
DEFAULT_RETENTION = 10
MIN_RETENTION = 1
MAX_RETENTION = 50
MAX_IMPORT_SIZE = 32 * 1024 * 1024
MAX_IMPORT_FILES = 64
CONFIG_FILES = (
    "kdeglobals",
    "kwinrc",
    "plasmarc",
    "plasmashellrc",
    "plasma-org.kde.plasma.desktop-appletsrc",
    "kglobalshortcutsrc",
    "kcminputrc",
    "dolphinrc",
)
STYLE_TITLES = {
    "windows11": "Windows-11-Stil",
    "macos": "macOS-Stil",
    "windows8": "Windows-8-Stil",
    "windows81": "Windows-8.1-Stil",
}
DEFAULT_ASSETS = {
    "windows11": ("ohc-windows11", "ohc-windows11"),
    "macos": ("ohc-macos", "ohc-macos"),
    "windows8": ("ohc-windows8", "ohc-windows8"),
    "windows81": ("ohc-windows8", "ohc-windows8"),
}
QDBUS6_CANDIDATES = (
    "qdbus6",
    "qdbus-qt6",
    "/usr/lib64/qt6/bin/qdbus",
    "/usr/lib/qt6/bin/qdbus",
)
AUTOSTART_NAME = "open-hardware-control-desktop-shell.desktop"
KWIN_SCRIPT_ID = "ohc-charms"
EXPORT_ROOT = "ohc-design-backup"


class DesktopDesignError(RuntimeError):
    """Raised when a desktop design cannot be applied or restored safely."""


def _read_os_release(path: Path = Path("/etc/os-release")) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result
    for line in lines:
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key] = value.strip().strip('"').strip("'")
    return result


def state_root(env: Mapping[str, str] | None = None) -> Path:
    values = os.environ if env is None else env
    override = values.get("OHC_DESKTOP_DESIGN_STATE_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    base = values.get("XDG_STATE_HOME", "").strip()
    if base:
        return Path(base).expanduser() / "open-hardware-control" / "desktop-designs"
    return Path.home() / ".local" / "state" / "open-hardware-control" / "desktop-designs"


def config_root(env: Mapping[str, str] | None = None) -> Path:
    values = os.environ if env is None else env
    override = values.get("OHC_DESKTOP_DESIGN_CONFIG_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    base = values.get("XDG_CONFIG_HOME", "").strip()
    return Path(base).expanduser() if base else Path.home() / ".config"


def asset_path(style: str) -> Path:
    _validate_style_mode(style, "dark")
    return Path(__file__).resolve().with_name("assets") / "desktop-designs" / f"{style}-wallpaper.svg"


def _validate_style_mode(style: str, mode: str) -> None:
    if style not in SUPPORTED_STYLES:
        raise DesktopDesignError(f"Unbekanntes Desktop-Design: {style}")
    if mode not in SUPPORTED_MODES:
        raise DesktopDesignError(f"Unbekannter Farbmodus: {mode}")


def _atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.is_symlink() or path.is_symlink():
        raise DesktopDesignError(f"Unsicherer symbolischer Link: {path}")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_qdbus6() -> str | None:
    for candidate in QDBUS6_CANDIDATES:
        if candidate.startswith("/"):
            path = Path(candidate)
            if path.is_file() and os.access(path, os.X_OK):
                return str(path)
            continue
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _backup_root(root: Path | None = None) -> Path:
    return (state_root() if root is None else root) / "backups"


def _valid_backup_path(candidate: Path, root: Path | None = None) -> Path | None:
    try:
        resolved = candidate.resolve()
        allowed = _backup_root(root).resolve()
    except (OSError, ValueError):
        return None
    if resolved.parent != allowed or not (resolved / "manifest.json").is_file():
        return None
    return resolved


def latest_backup_path(root: Path | None = None) -> Path | None:
    base = state_root() if root is None else root
    try:
        candidate = Path((base / "latest-backup").read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    return _valid_backup_path(candidate, base)


def backup_path(backup_id: str, root: Path | None = None) -> Path:
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    if not backup_id or backup_id in {".", ".."} or any(char not in allowed for char in backup_id):
        raise DesktopDesignError("Ungültige Backup-Kennung.")
    candidate = _valid_backup_path(_backup_root(root) / backup_id, root)
    if candidate is None:
        raise DesktopDesignError(f"Desktop-Backup wurde nicht gefunden: {backup_id}")
    return candidate


def _read_manifest(backup: Path) -> dict[str, object]:
    try:
        payload = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DesktopDesignError(f"Das Desktop-Backup ist beschädigt: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema") not in SUPPORTED_BACKUP_SCHEMAS:
        raise DesktopDesignError("Das Desktop-Backup hat ein unbekanntes Format.")
    files = payload.get("config_files")
    if not isinstance(files, dict) or any(name not in CONFIG_FILES or not isinstance(value, bool) for name, value in files.items()):
        raise DesktopDesignError("Das Desktop-Backup enthält ungültige Konfigurationsangaben.")
    if payload.get("schema") == 2:
        managed = payload.get("managed")
        if not isinstance(managed, dict) or set(managed) != {"autostart", "kwin_script"} or not all(isinstance(value, bool) for value in managed.values()):
            raise DesktopDesignError("Das Desktop-Backup enthält ungültige Integrationsangaben.")
        previous_style = payload.get("previous_style")
        if previous_style is not None and previous_style not in SUPPORTED_STYLES:
            raise DesktopDesignError("Das Desktop-Backup enthält einen unbekannten vorherigen Stil.")
    return payload


def list_backups(root: Path | None = None) -> list[dict[str, object]]:
    directory = _backup_root(root)
    result: list[dict[str, object]] = []
    if not directory.is_dir():
        return result
    for item in sorted(directory.iterdir(), key=lambda path: path.name, reverse=True):
        if item.is_symlink() or not item.is_dir():
            continue
        valid = _valid_backup_path(item, root)
        if valid is None:
            continue
        try:
            manifest = _read_manifest(valid)
        except DesktopDesignError:
            continue
        result.append({
            "id": item.name,
            "created_utc": manifest.get("created_utc", ""),
            "style": manifest.get("style"),
            "mode": manifest.get("mode"),
            "path": str(valid),
        })
    return result


def backup_retention(root: Path | None = None) -> int:
    base = state_root() if root is None else root
    try:
        value = int(json.loads((base / "settings.json").read_text(encoding="utf-8")).get("backup_retention"))
    except (OSError, ValueError, TypeError, AttributeError):
        value = DEFAULT_RETENTION
    return min(MAX_RETENTION, max(MIN_RETENTION, value))


def set_backup_retention(value: int, root: Path | None = None) -> dict[str, object]:
    if not MIN_RETENTION <= value <= MAX_RETENTION:
        raise DesktopDesignError(f"Die Backup-Anzahl muss zwischen {MIN_RETENTION} und {MAX_RETENTION} liegen.")
    base = state_root() if root is None else root
    _atomic_text(base / "settings.json", json.dumps({"backup_retention": value}, indent=2) + "\n")
    removed = prune_backups(value, base)
    return {"ok": True, "backup_retention": value, "removed": removed}


def prune_backups(retention: int | None = None, root: Path | None = None) -> list[str]:
    keep = backup_retention(root) if retention is None else retention
    records = list_backups(root)
    removed: list[str] = []
    latest = latest_backup_path(root)
    protected = latest.name if latest else None
    for record in [item for item in records[keep:] if item["id"] != protected]:
        path = backup_path(str(record["id"]), root)
        shutil.rmtree(path)
        removed.append(str(record["id"]))
    return removed


def _managed_paths(config: Path | None = None, data: Path | None = None) -> tuple[Path, Path]:
    config_dir = config_root() if config is None else config
    data_dir = data_root() if data is None else data
    return config_dir / "autostart" / AUTOSTART_NAME, data_dir / "kwin" / "scripts" / KWIN_SCRIPT_ID


def create_backup(
    root: Path | None = None,
    config: Path | None = None,
    *,
    style: str | None = None,
    mode: str | None = None,
) -> Path:
    base = state_root() if root is None else root
    config_dir = config_root() if config is None else config
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    backup = base / "backups" / stamp
    saved_config = backup / "config"
    saved_config.mkdir(parents=True, exist_ok=False)
    files: dict[str, bool] = {}
    for name in CONFIG_FILES:
        source = config_dir / name
        exists = source.is_file() and not source.is_symlink()
        files[name] = exists
        if exists:
            shutil.copy2(source, saved_config / name)
    autostart, kwin_script = _managed_paths(config=config_dir)
    managed = {
        "autostart": autostart.is_file() and not autostart.is_symlink(),
        "kwin_script": kwin_script.is_dir() and not kwin_script.is_symlink(),
    }
    previous = read_active_state(base)
    previous_style = previous.get("style") if isinstance(previous, dict) else None
    if previous_style not in SUPPORTED_STYLES:
        previous_style = None
    manifest = {
        "schema": SCHEMA_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "style": style,
        "mode": mode,
        "previous_style": previous_style,
        "config_files": files,
        "managed": managed,
    }
    _atomic_text(backup / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    _atomic_text(base / "latest-backup", str(backup.resolve()) + "\n")
    prune_backups(root=base)
    return backup


def delete_backup(backup_id: str, root: Path | None = None) -> dict[str, object]:
    base = state_root() if root is None else root
    path = backup_path(backup_id, base)
    latest = latest_backup_path(base)
    shutil.rmtree(path)
    records = list_backups(base)
    if latest == path:
        marker = base / "latest-backup"
        if records:
            _atomic_text(marker, str(records[0]["path"]) + "\n")
        elif marker.exists():
            marker.unlink()
    return {"ok": True, "action": "delete-backup", "id": backup_id}


def export_backup(backup_id: str, output: Path, root: Path | None = None) -> dict[str, object]:
    backup = backup_path(backup_id, root)
    _read_manifest(backup)
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    files = [path for path in sorted(backup.rglob("*")) if path.is_file() and not path.is_symlink()]
    if len(files) > MAX_IMPORT_FILES or sum(path.stat().st_size for path in files) > MAX_IMPORT_SIZE:
        raise DesktopDesignError("Das Backup ist für den sicheren Export zu groß.")
    hashes = {path.relative_to(backup).as_posix(): _sha256(path) for path in files}
    with tempfile.NamedTemporaryFile(prefix="ohc-backup-", suffix=".zip", dir=output.parent, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in files:
                archive.write(path, (PurePosixPath(EXPORT_ROOT) / path.relative_to(backup).as_posix()).as_posix())
            archive.writestr(f"{EXPORT_ROOT}/SHA256.json", json.dumps(hashes, sort_keys=True, indent=2) + "\n")
        temporary.replace(output)
    finally:
        if temporary.exists():
            temporary.unlink()
    return {"ok": True, "action": "export-backup", "id": backup_id, "output": str(output), "sha256": _sha256(output)}


def _safe_zip_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    members = archive.infolist()
    if len(members) > MAX_IMPORT_FILES + 4:
        raise DesktopDesignError("Das importierte Backup enthält zu viele Dateien.")
    total = 0
    allowed = {"manifest.json", "SHA256.json", *(f"config/{name}" for name in CONFIG_FILES)}
    seen: set[str] = set()
    for info in members:
        path = PurePosixPath(info.filename)
        if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != EXPORT_ROOT:
            raise DesktopDesignError("Unsicherer Pfad im importierten Backup.")
        if stat.S_ISLNK(info.external_attr >> 16):
            raise DesktopDesignError("Symbolische Links sind in Backups nicht erlaubt.")
        relative = PurePosixPath(*path.parts[1:]).as_posix()
        if relative in seen:
            raise DesktopDesignError(f"Doppelter Pfad im Backup: {relative}")
        seen.add(relative)
        if not info.is_dir() and relative not in allowed:
            raise DesktopDesignError(f"Unerwartete Datei im Backup: {relative}")
        total += info.file_size
        if info.file_size > MAX_IMPORT_SIZE or total > MAX_IMPORT_SIZE:
            raise DesktopDesignError("Das importierte Backup ist zu groß.")
    return members


def import_backup(source: Path, root: Path | None = None) -> dict[str, object]:
    source = source.expanduser()
    if source.is_symlink():
        raise DesktopDesignError("Symbolische Links sind als Backup-Datei nicht erlaubt.")
    source = source.resolve()
    if not source.is_file() or source.stat().st_size > MAX_IMPORT_SIZE:
        raise DesktopDesignError("Die Backup-Datei ist ungültig oder zu groß.")
    base = state_root() if root is None else root
    with tempfile.TemporaryDirectory(prefix="ohc-backup-import-") as temporary_name:
        temporary = Path(temporary_name)
        try:
            with zipfile.ZipFile(source, "r") as archive:
                for info in _safe_zip_members(archive):
                    if not info.is_dir():
                        target = temporary / PurePosixPath(info.filename).relative_to(EXPORT_ROOT)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(archive.read(info))
        except (OSError, zipfile.BadZipFile) as exc:
            raise DesktopDesignError(f"Das Backup-Archiv ist beschädigt: {exc}") from exc
        try:
            expected = json.loads((temporary / "SHA256.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DesktopDesignError(f"Die Backup-Prüfsummen fehlen: {exc}") from exc
        if not isinstance(expected, dict):
            raise DesktopDesignError("Ungültige Backup-Prüfsummen.")
        actual_files = [item for item in temporary.rglob("*") if item.is_file() and item.name != "SHA256.json"]
        actual_names = {item.relative_to(temporary).as_posix() for item in actual_files}
        if actual_names != set(expected):
            raise DesktopDesignError("Dateiliste und Backup-Prüfsummen stimmen nicht überein.")
        if any(not isinstance(expected[name], str) or _sha256(temporary / name) != expected[name] for name in expected):
            raise DesktopDesignError("Eine Datei im Backup hat eine falsche Prüfsumme.")
        _read_manifest(temporary)
        stamp = datetime.now(timezone.utc).strftime("import-%Y%m%d-%H%M%S-%f")
        destination = _backup_root(base) / stamp
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(temporary, destination, ignore=shutil.ignore_patterns("SHA256.json"))
    _atomic_text(base / "latest-backup", str(destination.resolve()) + "\n")
    prune_backups(root=base)
    return {"ok": True, "action": "import-backup", "id": destination.name, "path": str(destination.resolve())}


def _run(args: list[str], *, required: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True, timeout=30, check=False)
    if required and result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"Exit-Code {result.returncode}"
        raise DesktopDesignError(f"{Path(args[0]).name}: {message}")
    return result


def _kwrite(file_name: str, group: str, key: str, value: str) -> None:
    executable = shutil.which("kwriteconfig6")
    if not executable:
        raise DesktopDesignError("kwriteconfig6 wurde nicht gefunden.")
    _run([executable, "--file", file_name, "--group", group, "--key", key, value])


def _plasma_script(script: str) -> None:
    executable = resolve_qdbus6()
    if not executable:
        raise DesktopDesignError("Das Qt-6-D-Bus-Werkzeug wurde nicht gefunden.")
    _run([executable, "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script])


def _panel_script(style: str, wallpaper: Path) -> str:
    wallpaper_uri = wallpaper.resolve().as_uri()
    common = """
var existing = panels();
for (var i = existing.length - 1; i >= 0; --i) { existing[i].remove(); }
"""
    if style == "windows11":
        panels = """
var panel = new Panel;
panel.location = "bottom"; panel.height = 48; panel.lengthMode = "fill"; panel.alignment = "center"; panel.hiding = "none";
var left = panel.addWidget("org.kde.plasma.panelspacer"); left.currentConfigGroup = ["General"]; left.writeConfig("expanding", true);
var launcher = panel.addWidget("org.kde.plasma.kickoff"); launcher.globalShortcut = "Alt+F1";
panel.addWidget("org.kde.plasma.icontasks");
var right = panel.addWidget("org.kde.plasma.panelspacer"); right.currentConfigGroup = ["General"]; right.writeConfig("expanding", true);
panel.addWidget("org.kde.plasma.systemtray"); panel.addWidget("org.kde.plasma.digitalclock"); panel.addWidget("org.kde.plasma.showdesktop"); panel.reloadConfig();
"""
    elif style == "macos":
        panels = """
var top = new Panel; top.location = "top"; top.height = 32; top.lengthMode = "fill"; top.hiding = "none";
var launcher = top.addWidget("org.kde.plasma.kickoff"); launcher.globalShortcut = "Alt+F1";
var topSpace = top.addWidget("org.kde.plasma.panelspacer"); topSpace.currentConfigGroup = ["General"]; topSpace.writeConfig("expanding", true);
top.addWidget("org.kde.plasma.systemtray"); top.addWidget("org.kde.plasma.digitalclock"); top.reloadConfig();
var dock = new Panel; dock.location = "bottom"; dock.height = 64; dock.lengthMode = "fit"; dock.alignment = "center"; dock.hiding = "autohide";
dock.addWidget("org.kde.plasma.kickoff"); dock.addWidget("org.kde.plasma.icontasks"); dock.reloadConfig();
"""
    else:
        height = 40 if style == "windows8" else 44
        panels = f"""
var panel = new Panel; panel.location = "bottom"; panel.height = {height}; panel.lengthMode = "fill"; panel.hiding = "none";
var launcher = panel.addWidget("org.kde.plasma.kickoff"); launcher.globalShortcut = "Alt+F1";
panel.addWidget("org.kde.plasma.icontasks");
var spacer = panel.addWidget("org.kde.plasma.panelspacer"); spacer.currentConfigGroup = ["General"]; spacer.writeConfig("expanding", true);
panel.addWidget("org.kde.plasma.systemtray"); panel.addWidget("org.kde.plasma.digitalclock"); panel.addWidget("org.kde.plasma.showdesktop"); panel.reloadConfig();
"""
    wallpaper_script = f"""
var desktopsList = desktops();
for (var d = 0; d < desktopsList.length; ++d) {{
    desktopsList[d].wallpaperPlugin = "org.kde.image";
    desktopsList[d].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktopsList[d].writeConfig("Image", {json.dumps(wallpaper_uri)});
    desktopsList[d].reloadConfig();
}}
"""
    return common + panels + wallpaper_script


def _shell_command() -> list[str]:
    override = os.environ.get("OHC_DESKTOP_SHELL_EXECUTABLE", "").strip()
    if override:
        resolved = Path(override).expanduser()
        if resolved.is_file() and os.access(resolved, os.X_OK):
            return [str(resolved)]
        raise DesktopDesignError("Der konfigurierte Desktop-Shell-Starter ist nicht ausführbar.")
    installed = shutil.which("open-hardware-control-desktop-shell")
    if installed:
        return [installed]
    helper = Path(__file__).resolve().with_name("desktop_shell.py")
    if helper.is_file():
        return [sys.executable, str(helper)]
    raise DesktopDesignError("desktop_shell.py wurde nicht gefunden.")


def _desktop_exec(command: list[str], style: str) -> str:
    def quote(value: str) -> str:
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return " ".join(quote(item) for item in (*command, "--background", "--style", style))


def _install_shell_integration(style: str) -> None:
    autostart, destination = _managed_paths()
    source = Path(__file__).resolve().with_name("assets") / "desktop-designs" / "kwin" / KWIN_SCRIPT_ID
    if not (source / "metadata.json").is_file() or not (source / "contents" / "code" / "main.js").is_file():
        raise DesktopDesignError("Die geprüfte OHC-Charms-KWin-Komponente fehlt.")
    if destination.is_symlink() or autostart.is_symlink():
        raise DesktopDesignError("Unsicherer symbolischer Link in der Desktop-Integration.")
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    command = _shell_command()
    _atomic_text(
        autostart,
        "[Desktop Entry]\nType=Application\nName=OHC Windows 8 Desktop Shell\n"
        f"Exec={_desktop_exec(command, style)}\nOnlyShowIn=KDE;\nX-KDE-autostart-after=panel\n"
        "X-GNOME-Autostart-enabled=true\nNoDisplay=true\n",
    )
    _kwrite("kwinrc", "Plugins", f"{KWIN_SCRIPT_ID}Enabled", "true")
    subprocess.Popen([*command, "--background", "--style", style], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def _stop_shell_integration(*, remove: bool) -> None:
    try:
        command = _shell_command()
    except DesktopDesignError:
        command = []
    if command:
        _run([*command, "--quit"], required=False)
    try:
        _kwrite("kwinrc", "Plugins", f"{KWIN_SCRIPT_ID}Enabled", "false")
    except DesktopDesignError:
        pass
    if remove:
        autostart, script = _managed_paths()
        if autostart.is_file() and not autostart.is_symlink():
            autostart.unlink()
        if script.is_dir() and not script.is_symlink():
            shutil.rmtree(script)


def _configure_style(style: str, mode: str, icon_option: str, cursor_option: str) -> None:
    dark = mode == "dark"
    look_and_feel = "org.kde.breezedark.desktop" if dark else "org.kde.breeze.desktop"
    color_scheme = "BreezeDark" if dark else "BreezeLight"
    icon_theme = icon_theme_name(icon_option)
    cursor_theme = cursor_theme_name(cursor_option)
    if icon_theme.startswith("OHC-") or cursor_theme.startswith("OHC-"):
        install_desktop_assets()
    look_tool = shutil.which("plasma-apply-lookandfeel")
    if look_tool:
        _run([look_tool, "-a", look_and_feel], required=False)
    _kwrite("kdeglobals", "General", "ColorScheme", color_scheme)
    _kwrite("kdeglobals", "Icons", "Theme", icon_theme)
    _kwrite("kcminputrc", "Mouse", "cursorTheme", cursor_theme)
    _kwrite("kdeglobals", "KDE", "CursorTheme", cursor_theme)
    _kwrite("kdeglobals", "General", "font", "Noto Sans,10,-1,5,50,0,0,0,0,0")
    _kwrite("kdeglobals", "General", "menuFont", "Noto Sans,10,-1,5,50,0,0,0,0,0")
    _kwrite("kdeglobals", "General", "toolBarFont", "Noto Sans,10,-1,5,50,0,0,0,0,0")
    _kwrite("kdeglobals", "General", "fixed", "Noto Sans Mono,10,-1,5,50,0,0,0,0,0")
    _kwrite("kwinrc", "org.kde.kdecoration2", "library", "org.kde.breeze")
    _kwrite("kwinrc", "Plugins", "blurEnabled", "true")
    _kwrite("kwinrc", "Plugins", "contrastEnabled", "true")
    _kwrite("dolphinrc", "General", "ShowStatusBar", "true")
    if style == "macos":
        _kwrite("kdeglobals", "KDE", "SingleClick", "true")
        _kwrite("kwinrc", "org.kde.kdecoration2", "ButtonsOnLeft", "XIA")
        _kwrite("kwinrc", "org.kde.kdecoration2", "ButtonsOnRight", "M")
    else:
        _kwrite("kdeglobals", "KDE", "SingleClick", "false")
        _kwrite("kwinrc", "org.kde.kdecoration2", "ButtonsOnLeft", "M")
        _kwrite("kwinrc", "org.kde.kdecoration2", "ButtonsOnRight", "IAX")
    wallpaper = asset_path(style)
    if not wallpaper.is_file():
        raise DesktopDesignError(f"Hintergrundbild fehlt: {wallpaper.name}")
    _plasma_script(_panel_script(style, wallpaper))
    if style in {"windows8", "windows81"}:
        _install_shell_integration(style)
    else:
        _stop_shell_integration(remove=True)
    reconfigure = resolve_qdbus6()
    if reconfigure:
        _run([reconfigure, "org.kde.KWin", "/KWin", "reconfigure"], required=False)


def _restore_from_backup(backup: Path, config: Path | None = None) -> None:
    config_dir = config_root() if config is None else config
    manifest = _read_manifest(backup)
    config_dir.mkdir(parents=True, exist_ok=True)
    files = manifest["config_files"]
    assert isinstance(files, dict)
    for name in CONFIG_FILES:
        existed = files.get(name)
        saved = backup / "config" / name
        target = config_dir / name
        if target.is_symlink():
            raise DesktopDesignError(f"Wiederherstellungsziel ist ein symbolischer Link: {name}")
        if existed is True and saved.is_file() and not saved.is_symlink():
            shutil.copy2(saved, target)
        elif existed is False and target.is_file():
            target.unlink()
    if manifest.get("schema") == 2:
        managed = manifest["managed"]
        assert isinstance(managed, dict)
        if managed.get("autostart") is True or managed.get("kwin_script") is True:
            previous_style = str(manifest.get("previous_style") or "windows8")
            _install_shell_integration(previous_style)
        else:
            _stop_shell_integration(remove=True)
    else:
        _stop_shell_integration(remove=True)
    active_file = state_root() / "active.json"
    if active_file.exists():
        active_file.unlink()


def _restart_plasma() -> None:
    quit_tool = shutil.which("kquitapp6")
    if quit_tool:
        _run([quit_tool, "plasmashell"], required=False)
    plasma = shutil.which("plasmashell")
    if plasma:
        subprocess.Popen([plasma, "--replace"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def read_active_state(root: Path | None = None) -> dict[str, object] | None:
    base = state_root() if root is None else root
    try:
        payload = json.loads((base / "active.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def emergency_reset() -> dict[str, object]:
    """Return touched appearance settings to conservative Breeze Light."""
    _stop_shell_integration(remove=True)
    look_tool = shutil.which("plasma-apply-lookandfeel")
    if look_tool:
        _run([look_tool, "-a", "org.kde.breeze.desktop"], required=False)
    _kwrite("kdeglobals", "General", "ColorScheme", "BreezeLight")
    _kwrite("kdeglobals", "Icons", "Theme", "breeze")
    _kwrite("kcminputrc", "Mouse", "cursorTheme", "breeze_cursors")
    _kwrite("kwinrc", "org.kde.kdecoration2", "library", "org.kde.breeze")
    _kwrite("kwinrc", "org.kde.kdecoration2", "ButtonsOnLeft", "M")
    _kwrite("kwinrc", "org.kde.kdecoration2", "ButtonsOnRight", "IAX")
    _plasma_script(_panel_script("windows11", asset_path("windows11")))
    root = state_root()
    for name in ("active.json", "transaction.json"):
        target = root / name
        if target.exists():
            target.unlink()
    _restart_plasma()
    return {"ok": True, "action": "emergency-reset", "style": "KDE Breeze Light"}


def recover_pending_transaction() -> dict[str, object]:
    marker = state_root() / "transaction.json"
    if not marker.is_file():
        return {"ok": True, "action": "recovery-check", "recovered": False}
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
        backup = _valid_backup_path(Path(payload["backup"])) if isinstance(payload, dict) else None
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        backup = None
    try:
        if backup is None:
            raise DesktopDesignError("Transaktions-Backup fehlt.")
        _restore_from_backup(backup)
        _restart_plasma()
        result = {"ok": True, "action": "recovery-check", "recovered": True, "fallback": "backup"}
    except Exception:
        result = emergency_reset()
        result.update({"action": "recovery-check", "recovered": True, "fallback": "breeze-light"})
    if marker.exists():
        marker.unlink()
    return result


def desktop_status(env: Mapping[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    os_release = _read_os_release()
    desktop = " ".join(part for part in (values.get("XDG_CURRENT_DESKTOP", ""), values.get("XDG_SESSION_DESKTOP", ""), values.get("KDE_FULL_SESSION", "")) if part)
    is_kde = "kde" in desktop.casefold() or "plasma" in desktop.casefold()
    required = {"kwriteconfig6": shutil.which("kwriteconfig6"), "qdbus (Qt 6)": resolve_qdbus6()}
    missing = [name for name, resolved in required.items() if not resolved]
    backups = list_backups()
    return {
        "ok": True,
        "compatible": bool(is_kde and not missing),
        "desktop": desktop or "Nicht erkannt",
        "is_kde": is_kde,
        "distribution_id": os_release.get("ID", "unknown"),
        "distribution_name": os_release.get("PRETTY_NAME", os_release.get("NAME", "Unbekanntes Linux")),
        "missing_commands": missing,
        "resolved_commands": {name: path for name, path in required.items() if path},
        "latest_backup_available": bool(backups),
        "backups": backups,
        "backup_retention": backup_retention(),
        "recovery_pending": (state_root() / "transaction.json").is_file(),
        "assets": desktop_asset_status(),
        "active": read_active_state(),
        "uses_external_downloads": False,
        "requires_root": False,
    }


def design_plan(style: str, mode: str) -> dict[str, object]:
    _validate_style_mode(style, mode)
    shared = [
        "aktuelle KDE-/Plasma-Konfiguration vollständig sichern",
        "auswählbare KDE- oder frei erzeugte OHC-Symbole und Mauszeiger verwenden",
        "eigenes frei lizenziertes Open-Hardware-Control-Hintergrundbild setzen",
        "Plasma-Leisten nach ausdrücklicher Bestätigung neu anordnen",
        "bei Fehlern automatisch das Backup oder KDE Breeze Light wiederherstellen",
        "keine Pakete, Designs oder Bilder aus dem Internet laden",
    ]
    layouts = {
        "windows11": ["untere 48-Pixel-Leiste", "mittiger Start-/Programmbereich", "moderne Breeze-Fensteranordnung"],
        "macos": ["schlanke obere Systemleiste", "zentriertes automatisch ausblendbares Dock", "Fensterschaltflächen links"],
        "windows8": ["bildschirmfüllende lokale Kachelübersicht", "Charms-Leiste an beiden rechten Ecken und Super+C", "klassische untere Desktop-Leiste"],
        "windows81": ["Windows-8.1-Variante der Kachelübersicht", "Charms-Leiste an beiden rechten Ecken und Super+C", "angepasste untere Desktop-Leiste"],
    }
    return {"ok": True, "style": style, "title": STYLE_TITLES[style], "mode": mode, "changes": shared + layouts[style], "reversible": True}


def apply_design(style: str, mode: str, icon_option: str | None = None, cursor_option: str | None = None) -> dict[str, object]:
    _validate_style_mode(style, mode)
    icon_option = icon_option or DEFAULT_ASSETS[style][0]
    cursor_option = cursor_option or DEFAULT_ASSETS[style][1]
    if icon_option not in ICON_THEMES or cursor_option not in CURSOR_THEMES:
        raise DesktopDesignError("Unbekannte Symbol- oder Mauszeigerauswahl.")
    status = desktop_status()
    if not status["compatible"]:
        details = ", ".join(status["missing_commands"]) or str(status["desktop"])
        raise DesktopDesignError(f"KDE Plasma 6 ist nicht vollständig verfügbar: {details}")
    backup = create_backup(style=style, mode=mode)
    marker = state_root() / "transaction.json"
    _atomic_text(marker, json.dumps({"schema": SCHEMA_VERSION, "backup": str(backup.resolve()), "style": style}, indent=2) + "\n")
    try:
        _configure_style(style, mode, icon_option, cursor_option)
    except Exception:
        try:
            _restore_from_backup(backup)
            _restart_plasma()
        except Exception:
            emergency_reset()
        if marker.exists():
            marker.unlink()
        raise
    active = {
        "schema": SCHEMA_VERSION,
        "style": style,
        "title": STYLE_TITLES[style],
        "mode": mode,
        "icons": icon_option,
        "cursor": cursor_option,
        "applied_utc": datetime.now(timezone.utc).isoformat(),
        "backup": str(backup.resolve()),
    }
    _atomic_text(state_root() / "active.json", json.dumps(active, ensure_ascii=False, indent=2) + "\n")
    if marker.exists():
        marker.unlink()
    return {"ok": True, "action": "apply", "active": active, "restart_session_recommended": True}


def restore_design(backup_id: str) -> dict[str, object]:
    backup = backup_path(backup_id)
    _restore_from_backup(backup)
    _restart_plasma()
    return {"ok": True, "action": "restore", "id": backup_id, "restart_session_recommended": True}


def restore_latest_design() -> dict[str, object]:
    backup = latest_backup_path()
    if backup is None:
        raise DesktopDesignError("Es wurde noch kein gültiges Desktop-Backup gefunden.")
    return restore_design(backup.name)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reversible KDE designs for Open Hardware Control")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--status", action="store_true")
    action.add_argument("--plan", choices=SUPPORTED_STYLES)
    action.add_argument("--apply", choices=SUPPORTED_STYLES)
    action.add_argument("--restore", action="store_true")
    action.add_argument("--restore-backup", metavar="ID")
    action.add_argument("--list-backups", action="store_true")
    action.add_argument("--delete-backup", metavar="ID")
    action.add_argument("--export-backup", metavar="ID")
    action.add_argument("--import-backup", metavar="ZIP")
    action.add_argument("--set-retention", type=int, metavar="ANZAHL")
    action.add_argument("--install-assets", action="store_true")
    action.add_argument("--recover", action="store_true")
    action.add_argument("--emergency-reset", action="store_true")
    parser.add_argument("--mode", choices=SUPPORTED_MODES, default="dark")
    parser.add_argument("--icons", choices=tuple(ICON_THEMES), default=None)
    parser.add_argument("--cursor", choices=tuple(CURSOR_THEMES), default=None)
    parser.add_argument("--output", metavar="DATEI")
    parser.add_argument("--confirm", action="store_true", help="required for changes")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        changes = any((args.apply, args.restore, args.restore_backup, args.delete_backup, args.import_backup, args.set_retention is not None, args.install_assets, args.emergency_reset))
        if changes and not args.confirm:
            raise DesktopDesignError("Änderungen benötigen die ausdrückliche Bestätigung der Oberfläche.")
        if args.status:
            result = desktop_status()
        elif args.plan:
            result = design_plan(args.plan, args.mode)
        elif args.list_backups:
            result = {"ok": True, "backups": list_backups(), "backup_retention": backup_retention()}
        elif args.apply:
            result = apply_design(args.apply, args.mode, args.icons, args.cursor)
        elif args.restore_backup:
            result = restore_design(args.restore_backup)
        elif args.restore:
            result = restore_latest_design()
        elif args.delete_backup:
            result = delete_backup(args.delete_backup)
        elif args.export_backup:
            if not args.output:
                raise DesktopDesignError("Für den Export fehlt --output.")
            result = export_backup(args.export_backup, Path(args.output))
        elif args.import_backup:
            result = import_backup(Path(args.import_backup))
        elif args.set_retention is not None:
            result = set_backup_retention(args.set_retention)
        elif args.install_assets:
            result = install_desktop_assets()
        elif args.recover:
            result = recover_pending_transaction()
        else:
            result = emergency_reset()
    except (DesktopDesignError, DesktopAssetError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
