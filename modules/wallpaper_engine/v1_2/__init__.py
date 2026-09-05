"""Public entry points for the Wallpaper Engine for KDE 1.2 module."""

from .library import WallpaperEntry, previous_workshop_entry, scan_video_folder, scan_workshop_library
from .installer import PluginInstallError, ReleaseAsset, select_release_asset
from .page import WallpaperEnginePage
from .plasma import PlasmaWallpaperState, read_plasma_wallpaper_states

__all__ = [
    "PlasmaWallpaperState",
    "PluginInstallError",
    "ReleaseAsset",
    "WallpaperEnginePage",
    "WallpaperEntry",
    "read_plasma_wallpaper_states",
    "previous_workshop_entry",
    "scan_video_folder",
    "scan_workshop_library",
    "select_release_asset",
]
