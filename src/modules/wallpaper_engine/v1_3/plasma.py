"""Plasma state parsing and bounded script construction."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil


PLUGIN_ID = "com.github.captsilver.wallpaperEngineKde"
DBUS_SERVICE = "com.github.captsilver.WallpaperEngine"
DBUS_OBJECT = "/WallpaperEngine"
DBUS_INTERFACE = "com.github.captsilver.WallpaperEngine"
PLASMA_SERVICE = "org.kde.plasmashell"
PLASMA_OBJECT = "/PlasmaShell"
PLASMA_EVALUATE = "org.kde.PlasmaShell.evaluateScript"
SECTION_RE = re.compile(
    rf"^\[Containments\]\[(\d+)\]\[Wallpaper\]\[{re.escape(PLUGIN_ID)}\]\[General\]$"
)
CONTAINMENT_RE = re.compile(r"^\[Containments\]\[(\d+)\]$")

STOCK_PROFILE = {
    "AnimatedPreview": True,
    "Fps": 30,
    "PauseMode": 0,
    "ResumeTime": 300,
    "PresentMode": 0,
}
OPTIMIZED_PROFILE = {
    "AnimatedPreview": False,
    "Fps": 25,
    "PauseMode": 5,
    "ResumeTime": 1000,
    "PresentMode": 0,
}
DISPLAY_MODES = (
    (0, "Seitenverhältnis beibehalten"),
    (1, "Skalieren und zuschneiden"),
    (2, "Auf Vollbild strecken"),
)
DEFAULT_DISPLAY_MODE = 1


@dataclass(frozen=True, slots=True)
class PlasmaWallpaperState:
    containment_id: int
    screen: int
    steam_library: Path | None
    video_folder: Path | None
    workshop_id: str
    wallpaper_source: str
    settings: dict[str, object]


def plasma_config_path() -> Path:
    override = os.environ.get("OHC_WALLPAPER_CONFIG", "").strip()
    if override:
        return Path(override).expanduser()
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "plasma-org.kde.plasma.desktop-appletsrc"


def _decode_path(value: str) -> Path | None:
    raw = value.strip()
    if not raw:
        return None
    if raw.startswith("file://"):
        raw = raw[7:]
    elif raw.startswith("file:"):
        raw = raw[5:]
    raw = raw.replace("$HOME", str(Path.home()), 1)
    return Path(os.path.expandvars(os.path.expanduser(raw)))


def _plain_key(key: str) -> str:
    return key.split("[", 1)[0]


def _typed_setting(key: str, value: str) -> object:
    if key == "AnimatedPreview":
        return value.strip().lower() in {"1", "true", "yes", "on"}
    if key in {"Fps", "PauseMode", "ResumeTime", "PresentMode", "DisplayMode"}:
        try:
            return int(value)
        except ValueError:
            return value
    return value


def read_plasma_wallpaper_states(path: Path | None = None) -> list[PlasmaWallpaperState]:
    """Read only the CaptSilver wallpaper groups from Plasma's config."""

    source = path or plasma_config_path()
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return []
    screens: dict[int, int] = {}
    current_containment: int | None = None
    for line in lines:
        containment = CONTAINMENT_RE.match(line.strip())
        if containment:
            current_containment = int(containment.group(1))
        elif line.startswith("["):
            current_containment = None
        elif current_containment is not None and line.startswith("lastScreen="):
            try:
                screens[current_containment] = int(line.split("=", 1)[1])
            except ValueError:
                pass

    states: list[PlasmaWallpaperState] = []
    index = 0
    while index < len(lines):
        match = SECTION_RE.match(lines[index].strip())
        if not match:
            index += 1
            continue
        containment_id = int(match.group(1))
        values: dict[str, str] = {}
        index += 1
        while index < len(lines) and not lines[index].startswith("["):
            if "=" in lines[index]:
                key, value = lines[index].split("=", 1)
                values[_plain_key(key)] = value
            index += 1
        tracked_settings = (*STOCK_PROFILE, "DisplayMode")
        settings = {key: _typed_setting(key, values[key]) for key in tracked_settings if key in values}
        states.append(
            PlasmaWallpaperState(
                containment_id=containment_id,
                screen=screens.get(containment_id, len(states)),
                steam_library=_decode_path(values.get("SteamLibraryPath", "")),
                video_folder=_decode_path(values.get("VideoFolderPath", "")),
                workshop_id=values.get("WallpaperWorkShopId", "").strip(),
                wallpaper_source=values.get("WallpaperSource", "").strip(),
                settings=settings,
            )
        )
    return sorted(states, key=lambda state: (state.screen, state.containment_id))


def preferred_steam_library(states: list[PlasmaWallpaperState]) -> Path:
    override = os.environ.get("OHC_WALLPAPER_STEAM_LIBRARY", "").strip()
    if override:
        return Path(override).expanduser()
    for state in states:
        if state.steam_library is not None:
            return state.steam_library
    candidates = (
        Path.home() / ".local/share/Steam",
        Path.home() / ".steam/steam",
        Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam",
    )
    return next((path for path in candidates if (path / "steamapps").is_dir()), candidates[0])


def plugin_installed() -> bool:
    roots = (
        Path("/usr/share/plasma/wallpapers") / PLUGIN_ID,
        Path.home() / ".local/share/plasma/wallpapers" / PLUGIN_ID,
    )
    return any((root / "metadata.json").is_file() or (root / "metadata.desktop").is_file() for root in roots)


def qdbus_program() -> str | None:
    return shutil.which("qdbus6") or shutil.which("qdbus-qt6") or shutil.which("qdbus")


def _script_prelude(target_screen: int | None, *, activate_plugin: bool) -> str:
    target = -1 if target_screen is None else max(0, int(target_screen))
    activation = f'd.wallpaperPlugin={json.dumps(PLUGIN_ID)};' if activate_plugin else f'if(d.wallpaperPlugin!=={json.dumps(PLUGIN_ID)}) continue;'
    return (
        "var ds=desktops();"
        "for(var i=0;i<ds.length;i++){var d=ds[i];"
        f"if({target}>=0 && d.screen!=={target}) continue;"
        f"{activation}"
        f'd.currentConfigGroup=["Wallpaper",{json.dumps(PLUGIN_ID)},"General"];'
    )


def build_select_script(
    *, workshop_id: str, packed_source: str, steam_library: Path, target_screen: int | None
) -> str:
    if not workshop_id or not packed_source:
        raise ValueError("Wallpaper-Auswahl ist unvollständig")
    return (
        _script_prelude(target_screen, activate_plugin=True)
        + f'd.writeConfig("SteamLibraryPath",{json.dumps(str(steam_library.expanduser()))});'
        + f'd.writeConfig("WallpaperWorkShopId",{json.dumps(workshop_id)});'
        + f'd.writeConfig("WallpaperSource",{json.dumps(packed_source)});'
        + "}"
    )


def build_video_folder_script(folder: Path | None, target_screen: int | None) -> str:
    value = "" if folder is None else str(folder.expanduser())
    return _script_prelude(target_screen, activate_plugin=False) + f'd.writeConfig("VideoFolderPath",{json.dumps(value)});' + "}"


def build_profile_script(profile: dict[str, object], target_screen: int | None) -> str:
    if set(profile) != set(STOCK_PROFILE):
        raise ValueError("Unbekanntes Wallpaper-Profil")
    script = _script_prelude(target_screen, activate_plugin=False)
    for key in STOCK_PROFILE:
        script += f'd.writeConfig({json.dumps(key)},{json.dumps(profile[key])});'
    return script + "}"


def normalize_display_mode(value: object) -> int:
    """Return one of the three DisplayMode values exposed by CaptSilver v1.4."""

    try:
        candidate = int(value)
    except (TypeError, ValueError):
        return DEFAULT_DISPLAY_MODE
    return candidate if candidate in {mode for mode, _label in DISPLAY_MODES} else DEFAULT_DISPLAY_MODE


def build_display_mode_script(mode: object, target_screen: int | None) -> str:
    normalized = normalize_display_mode(mode)
    return (
        _script_prelude(target_screen, activate_plugin=False)
        + f'd.writeConfig("DisplayMode",{normalized});'
        + "}"
    )


def plasma_script_command(script: str) -> list[str]:
    program = qdbus_program()
    if not program:
        return []
    return [program, PLASMA_SERVICE, PLASMA_OBJECT, PLASMA_EVALUATE, script]


def playback_command(method: str) -> list[str]:
    if method not in {"Next", "Pause", "Resume", "ToggleMute", "Reload"}:
        raise ValueError("Unbekannter Wiedergabebefehl")
    program = qdbus_program()
    # CaptSilver registers /WallpaperEngine on Plasma's already-owned bus name.
    # Calling the advertised stand-alone alias fails when that optional alias
    # could not be acquired, while the object remains fully usable here.
    return [] if not program else [program, PLASMA_SERVICE, DBUS_OBJECT, f"{DBUS_INTERFACE}.{method}"]


def original_settings_command() -> tuple[str, list[str]] | None:
    for program, arguments in (
        ("systemsettings", ["kcm_wallpaper"]),
        ("systemsettings6", ["kcm_wallpaper"]),
        ("kcmshell6", ["kcm_wallpaper"]),
    ):
        resolved = shutil.which(program)
        if resolved:
            return resolved, arguments
    return None
