#!/usr/bin/env python3
"""Focused regressions for the next RGB/LCD/NEXUS managers."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.lcd_media_manager.v1_1 import (  # noqa: E402
    DesignLibraryState,
    library_media_items,
)
from modules.openlinkhub_nexus.v1_0 import install_nexus_design, list_nexus_profiles  # noqa: E402
from modules.rgb_studio.v1_15.openrgb_profiles import (  # noqa: E402
    import_openrgb_profile,
    inspect_openrgb_profile,
    list_openrgb_profiles,
)
from modules.rgb_studio.v1_15.startup_status import (  # noqa: E402
    startup_profile_caption,
    startup_status_summary,
)
from openlinkhub_integration import validate_write_payload  # noqa: E402


def test_rgb_startup_summary_resolves_profile_and_all_states() -> None:
    profiles = [{"id": "night", "name": "Nachtbeleuchtung"}]
    assert startup_profile_caption("night", profiles) == "Nachtbeleuchtung"
    summary = startup_status_summary(
        "Nachtbeleuchtung",
        control_enabled=False,
        control_pending=True,
        autostart_enabled=True,
        reclaim_enabled=True,
        consent_confirmed=True,
    )
    assert "Startprofil: Nachtbeleuchtung" in summary
    assert "Automatik: EIN" in summary
    assert "Wiederaufnahme: EIN" in summary
    assert "RGB-Steuerung: STARTET" in summary


def test_lcd_manager_collects_gif_video_and_individual_files_without_deleting(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    gif = folder / "loop.gif"
    video = folder / "clip.mp4"
    single = tmp_path / "single.webp"
    gif.write_bytes(b"gif")
    video.write_bytes(b"video")
    single.write_bytes(b"image")
    state = DesignLibraryState((folder,), (single,), {}, (video,))
    assert library_media_items(state) == (gif.resolve(), single.resolve())
    assert video.read_bytes() == b"video"


def _fake_openlinkhub_root(tmp_path: Path) -> Path:
    root = tmp_path / "OpenLinkHub"
    (root / "database/nexus").mkdir(parents=True)
    (root / "OpenLinkHub").write_bytes(b"binary")
    (root / "database/nexus/nexus.json").write_text(
        json.dumps({"profiles": {"default": {"name": "Default"}}}), encoding="utf-8",
    )
    return root


def test_nexus_image_install_is_bounded_backed_up_and_listed(tmp_path: Path) -> None:
    root = _fake_openlinkhub_root(tmp_path)
    source = tmp_path / "Aurora.png"
    Image.new("RGB", (1200, 160), (20, 80, 180)).save(source)
    result = install_nexus_design(source, root, home=tmp_path)
    assert result.profile_id == "ohc-aurora"
    assert result.backup.is_file()
    target = root / "database/nexus/ohc-aurora.jpg"
    with Image.open(target) as image:
        assert image.size == (640, 48)
    assert ("ohc-aurora", "Aurora") in list_nexus_profiles(root, home=tmp_path)


def test_nexus_manifest_rejects_overlapping_touch_regions(tmp_path: Path) -> None:
    root = _fake_openlinkhub_root(tmp_path)
    Image.new("RGB", (640, 48), (0, 0, 0)).save(tmp_path / "bg.png")
    manifest = {
        "schema": 1, "profile_id": "ohc-buttons", "name": "Buttons", "background": "bg.png",
        "buttons": {
            "0": {"actionCode": 1, "width": 100, "height": 40, "offsetX": 0, "offsetY": 4,
                  "touchPositionMin": 0, "TouchPositionMax": 120},
            "1": {"actionCode": 2, "width": 100, "height": 40, "offsetX": 110, "offsetY": 4,
                  "touchPositionMin": 100, "TouchPositionMax": 200},
        },
    }
    source = tmp_path / "buttons.ohcnexus.json"
    source.write_text(json.dumps(manifest), encoding="utf-8")
    try:
        install_nexus_design(source, root, home=tmp_path)
    except ValueError as exc:
        assert "überschneiden" in str(exc)
    else:
        raise AssertionError("overlapping Nexus touch ranges were accepted")


def test_openrgb_profile_library_accepts_real_headers_and_rejects_fake_files(tmp_path: Path) -> None:
    source = tmp_path / "gaming.orp"
    source.write_bytes(b"OPENRGB_PROFILE\0" + (3).to_bytes(4, "little"))
    assert inspect_openrgb_profile(source).format == "legacy-orp"
    imported = import_openrgb_profile(source, tmp_path / "library")
    assert imported.path.parent == (tmp_path / "library").resolve()
    assert list_openrgb_profiles(tmp_path / "library") == (imported,)
    fake = tmp_path / "fake.orp"
    fake.write_bytes(b"not a profile")
    try:
        inspect_openrgb_profile(fake)
    except ValueError:
        pass
    else:
        raise AssertionError("fake OpenRGB profile was accepted")


def test_openlinkhub_nexus_profile_write_is_allowlisted_and_validated() -> None:
    token = "a" * 64
    assert validate_write_payload(
        "lcd-profile", {"control_id": token, "profile": "ohc-aurora"},
    ) == {"_controlId": token, "profile": "ohc-aurora"}
    try:
        validate_write_payload(
            "lcd-profile", {"control_id": token, "profile": "../../unsafe"},
        )
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe Nexus profile name was accepted")


def test_ui_wires_prominent_start_panel_and_both_import_managers() -> None:
    code = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
    controller = (
        ROOT / "src/modules/openlinkhub_update/v1_0/controller.py"
    ).read_text(encoding="utf-8")
    assert 'setObjectName("rgbStartupAutomationPanel")' in code
    assert "layout.insertWidget(1, self.rgb_startup_automation_panel)" in code
    assert "enable_rgb_automation_after_consent" in code
    assert 'QPushButton("LCD-Designmanager öffnen")' in code
    assert 'QPushButton("OpenRGB-Profil importieren")' in code
    assert 'QGroupBox("iCUE NEXUS · OHC-Designmanager")' in controller
