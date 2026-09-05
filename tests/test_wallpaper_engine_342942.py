#!/usr/bin/env python3
"""Regression guards for the native Wallpaper Engine for KDE page."""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.wallpaper_engine.v1_2.installer import (
    PluginInstallError,
    installer_cache_directory,
    parse_os_release,
    privileged_install_command,
    select_release_asset,
)
from modules.wallpaper_engine.v1_2.library import (
    is_unsafe_video_folder,
    previous_workshop_entry,
    scan_video_folder,
    scan_workshop_library,
)
from modules.wallpaper_engine.v1_2.plasma import (
    DBUS_INTERFACE,
    DBUS_OBJECT,
    DISPLAY_MODES,
    OPTIMIZED_PROFILE,
    PLASMA_SERVICE,
    PLUGIN_ID,
    STOCK_PROFILE,
    build_display_mode_script,
    build_profile_script,
    build_select_script,
    build_video_folder_script,
    normalize_display_mode,
    playback_command,
    read_plasma_wallpaper_states,
)


with tempfile.TemporaryDirectory(prefix="ohc-wallpaper-engine-") as raw_temp:
    root = Path(raw_temp)
    steam = root / "Steam"
    project = steam / "steamapps/workshop/content/431960/123456"
    project.mkdir(parents=True)
    (project / "movie.mp4").write_bytes(b"video")
    (project / "preview.jpg").write_bytes(b"preview")
    (project / "project.json").write_text(
        json.dumps(
            {
                "title": "Test Video",
                "type": "video",
                "file": "movie.mp4",
                "preview": "preview.jpg",
                "tags": ["Technology"],
            }
        ),
        encoding="utf-8",
    )
    broken = steam / "steamapps/workshop/content/431960/999999"
    broken.mkdir()
    (broken / "project.json").write_text('{"file":"../../outside","type":"video"}', encoding="utf-8")

    entries = scan_workshop_library(steam)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.ident == "123456"
    assert entry.title == "Test Video"
    assert entry.kind == "video"
    assert entry.packed_source.endswith("movie.mp4+video")
    assert entry.preview_path == project / "preview.jpg"
    older_entry = type(entry)(
        ident="123455",
        title="Older",
        kind="video",
        source_path=entry.source_path,
        preview_path=None,
    )
    assert previous_workshop_entry([entry, older_entry], entry.ident) == older_entry
    assert previous_workshop_entry([entry, older_entry], older_entry.ident) == entry
    assert previous_workshop_entry([], entry.ident) is None

    own_videos = root / "Videos/Wallpaper"
    own_videos.mkdir(parents=True)
    (own_videos / "own.webm").write_bytes(b"video")
    (own_videos / "ignore.txt").write_text("not video", encoding="utf-8")
    videos = scan_video_folder(own_videos)
    assert len(videos) == 1
    assert videos[0].ident.startswith("video:")
    assert videos[0].packed_source.endswith("own.webm+video")
    assert is_unsafe_video_folder(steam, steam)
    assert not is_unsafe_video_folder(own_videos, steam)

    config = root / "plasma-org.kde.plasma.desktop-appletsrc"
    config.write_text(
        f"""[Containments][568]
lastScreen=0
wallpaperplugin={PLUGIN_ID}

[Containments][568][Wallpaper][{PLUGIN_ID}][General]
Fps=25
DisplayMode=2
PauseMode=5
ResumeTime=1000
SteamLibraryPath[$e]=file:{steam}
VideoFolderPath[$e]=
WallpaperSource[$e]={entry.packed_source}
WallpaperWorkShopId=123456

[Containments][569]
lastScreen=1
wallpaperplugin={PLUGIN_ID}

[Containments][569][Wallpaper][{PLUGIN_ID}][General]
SteamLibraryPath[$e]=file:{steam}
VideoFolderPath[$e]={own_videos}
WallpaperWorkShopId=654321
""",
        encoding="utf-8",
    )
    states = read_plasma_wallpaper_states(config)
    assert [state.screen for state in states] == [0, 1]
    assert states[0].steam_library == steam
    assert states[0].video_folder is None
    assert states[0].settings == {"Fps": 25, "PauseMode": 5, "ResumeTime": 1000, "DisplayMode": 2}
    assert states[1].video_folder == own_videos

    select_script = build_select_script(
        workshop_id=entry.ident,
        packed_source=entry.packed_source,
        steam_library=steam,
        target_screen=1,
    )
    assert f'd.wallpaperPlugin="{PLUGIN_ID}"' in select_script
    assert "d.screen!==1" in select_script
    assert 'd.writeConfig("WallpaperWorkShopId","123456")' in select_script
    assert entry.packed_source in select_script

    clear_script = build_video_folder_script(None, None)
    assert 'd.writeConfig("VideoFolderPath","")' in clear_script
    assert "wallpaperPlugin!==" in clear_script

    optimized_script = build_profile_script(OPTIMIZED_PROFILE, 0)
    stock_script = build_profile_script(STOCK_PROFILE, None)
    for key in STOCK_PROFILE:
        assert f'd.writeConfig("{key}",' in optimized_script
        assert f'd.writeConfig("{key}",' in stock_script
    assert 'd.writeConfig("Fps",25)' in optimized_script
    assert 'd.writeConfig("Fps",30)' in stock_script
    assert "wek-cache" not in optimized_script
    assert "systemctl" not in optimized_script

    assert [mode for mode, _label in DISPLAY_MODES] == [0, 1, 2]
    assert normalize_display_mode(0) == 0
    assert normalize_display_mode("2") == 2
    assert normalize_display_mode(99) == 1
    display_script = build_display_mode_script(2, 1)
    assert "d.screen!==1" in display_script
    assert 'd.writeConfig("DisplayMode",2)' in display_script

    with patch("modules.wallpaper_engine.v1_2.plasma.qdbus_program", return_value="/usr/bin/qdbus-qt6"):
        command = playback_command("Pause")
    assert command == [
        "/usr/bin/qdbus-qt6",
        PLASMA_SERVICE,
        DBUS_OBJECT,
        f"{DBUS_INTERFACE}.Pause",
    ]
    try:
        playback_command("NotAMethod")
    except ValueError:
        pass
    else:
        raise AssertionError("An unknown D-Bus method must be rejected")

    os_release = parse_os_release('ID=fedora\nVERSION_ID="44"\nNAME="Fedora Linux"\n')
    assert os_release["ID"] == "fedora"
    assert os_release["VERSION_ID"] == "44"
    release = {
        "tag_name": "v1.4",
        "draft": False,
        "prerelease": False,
        "assets": [
            {
                "name": "wallpaper-engine-kde-plugin-qt6-1.4-1.fc44.x86_64.rpm",
                "browser_download_url": "https://github.com/CaptSilver/wallpaper-engine-kde-plugin/releases/download/v1.4/wallpaper-engine-kde-plugin-qt6-1.4-1.fc44.x86_64.rpm",
                "size": 3_089_779,
                "digest": "sha256:" + ("b" * 64),
            }
        ],
    }
    asset = select_release_asset(release, "44", "x86_64")
    assert asset.tag == "v1.4"
    assert asset.name.endswith("fc44.x86_64.rpm")
    assert asset.sha256 == "b" * 64
    try:
        select_release_asset(release, "43", "x86_64")
    except PluginInstallError as error:
        assert "kein passendes offizielles RPM" in str(error)
    else:
        raise AssertionError("A Fedora-mismatched RPM must not be selected")

    with patch.dict(os.environ, {"XDG_CACHE_HOME": str(root / "cache")}):
        cache = installer_cache_directory()
        package = cache / asset.name
        package.write_bytes(b"\xed\xab\xee\xdbverified official rpm fixture")
        digest = hashlib.sha256(package.read_bytes()).hexdigest()
        with patch("modules.wallpaper_engine.v1_2.installer.shutil.which", side_effect=lambda name: f"/usr/bin/{name}"):
            command = privileged_install_command(package, digest)
            assert command[:4] == ["/usr/bin/pkexec", "/usr/bin/dnf", "install", "-y"]
            assert command[-1] == str(package.resolve())
            assert privileged_install_command(package, "0" * 64) == []

print("3.4.29.44 Wallpaper Engine playback, scaling, setup and integration regression guards passed.")
