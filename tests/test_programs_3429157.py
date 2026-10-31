"""Programs 1.0 stays bounded, pure and integrated without installing anything."""
from __future__ import annotations

import os
import json
from pathlib import Path
import sys
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.localization.v1_0.catalog import UI_TRANSLATIONS
from modules.programs.v1_0.model import (
    InstalledProgram, ProgramProfile, default_programs_folder, desktop_programs,
    dump_profiles, load_profiles, normalize_base_folder, profile_from_program,
)
from modules.programs.v1_0.github_release import (
    GitHubReleaseError, download_release, downloaded_appimages, inspect_release,
    parse_release,
)
from modules.programs.v1_0.install_plan import (
    InstallPlanError, apply_appimage_plan, build_install_plan,
)


def test_desktop_inventory_detects_formats_without_executing(tmp_path: Path) -> None:
    root = tmp_path / "applications"; root.mkdir()
    (root / "flatpak.desktop").write_text("[Desktop Entry]\nName=Flat Demo\nExec=flatpak run org.demo.App %U\n", encoding="utf-8")
    (root / "snap.desktop").write_text("[Desktop Entry]\nName=Snap Demo\nExec=snap run demo.snap\n", encoding="utf-8")
    (root / "image.desktop").write_text("[Desktop Entry]\nName=Image Demo\nExec=/opt/Demo.AppImage\n", encoding="utf-8")
    (root / "hidden.desktop").write_text("[Desktop Entry]\nName=Hidden\nNoDisplay=true\nExec=hidden\n", encoding="utf-8")
    programs = desktop_programs((root,))
    assert {(item.name, item.format, item.identifier) for item in programs} == {
        ("Flat Demo", "Flatpak", "org.demo.App"),
        ("Snap Demo", "Snap", "demo.snap"),
        ("Image Demo", "AppImage", "/opt/Demo.AppImage"),
    }


def test_profiles_round_trip_is_bounded_and_rejects_invalid_values() -> None:
    source = InstalledProgram("Demo", "org.demo.App", "Flatpak", "flatpak")
    basic = profile_from_program(source)
    profile = ProgramProfile(
        basic.name, basic.identifier, basic.format, "stable", basic.executable,
        "example/demo", "v1.2.3",
    )
    assert load_profiles(dump_profiles((profile,))) == (profile,)
    assert load_profiles('[{"name":"Bad","identifier":"x","format":"Unknown"}]') == ()
    duplicated = dump_profiles((profile, profile))
    assert load_profiles(duplicated) == (profile,)
    assert load_profiles("not json") == ()


def test_base_folder_uses_xdg_documents_and_rejects_relative_paths(tmp_path: Path) -> None:
    config = tmp_path / ".config"; config.mkdir()
    (config / "user-dirs.dirs").write_text('XDG_DOCUMENTS_DIR="$HOME/Dokumente"\n', encoding="utf-8")
    expected = tmp_path / "Dokumente/Open Hardware Control/Programs"
    assert default_programs_folder(tmp_path) == expected
    assert normalize_base_folder("relative", expected) == expected
    assert normalize_base_folder(tmp_path / "custom", expected) == tmp_path / "custom"


def test_navigation_and_all_four_languages_include_programs() -> None:
    main = (ROOT / "src/kraken_control.py").read_text(encoding="utf-8")
    panel = (ROOT / "src/modules/navigation_settings/v1_0/panel.py").read_text(encoding="utf-8")
    assert '"programs": ("▦   Programme", -1)' in main
    assert "build_programs_page" in main
    assert '("programs", "▦", "Programme")' in panel
    sources = (
        "Programme", "Grundordner", "Installierte Programme neu laden",
        "Gespeicherte Installationsprofile", "GitHub-Release herunterladen",
        "Alle Dateien und Source-Code herunterladen", "GitHub-Projekt zuordnen",
    )
    for language in ("de", "en", "es", "fr"):
        assert all(source in UI_TRANSLATIONS[language] for source in sources)


class _Response:
    def __init__(self, payload: bytes, url: str) -> None:
        self.payload, self.url, self.offset = payload, url, 0

    def __enter__(self): return self
    def __exit__(self, *_args): return False
    def geturl(self) -> str: return self.url
    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self.payload) - self.offset
        chunk = self.payload[self.offset:self.offset + size]; self.offset += len(chunk); return chunk


def test_github_release_downloads_assets_sources_and_hash_manifest(tmp_path: Path) -> None:
    asset, source_zip, source_tar = b"binary", b"zip-source", b"tar-source"
    payload = {
        "tag_name": "v1.2.3", "name": "Stable", "published_at": "2026-10-20T10:00:00Z",
        "draft": False,
        "assets": [{
            "name": "demo.AppImage", "size": len(asset),
            "browser_download_url": "https://github.com/example/demo/releases/download/v1.2.3/demo.AppImage",
        }],
        "zipball_url": "https://api.github.com/repos/example/demo/zipball/v1.2.3",
        "tarball_url": "https://api.github.com/repos/example/demo/tarball/v1.2.3",
    }
    metadata = json.dumps(payload).encode()
    def opener(request, timeout=0):
        url = request.full_url
        if url.endswith("/releases/latest"): return _Response(metadata, url)
        if url.endswith("demo.AppImage"): return _Response(asset, "https://release-assets.githubusercontent.com/demo")
        if "/zipball/" in url: return _Response(source_zip, "https://codeload.github.com/example/demo/zip/v1.2.3")
        if "/tarball/" in url: return _Response(source_tar, "https://codeload.github.com/example/demo/tar.gz/v1.2.3")
        raise AssertionError(url)
    plan = inspect_release("https://github.com/example/demo.git", opener=opener)
    assert plan.tag == "v1.2.3" and len(plan.items) == 3
    target = download_release(plan, tmp_path / "downloads", opener=opener)
    assert {path.name for path in target.iterdir()} == {
        "demo.AppImage", "source-code.zip", "source-code.tar.gz", "SHA256SUMS", "release-manifest.json",
    }
    manifest = json.loads((target / "release-manifest.json").read_text(encoding="utf-8"))
    assert manifest["repository"] == "example/demo" and len(manifest["files"]) == 3
    assert all(len(row["sha256"]) == 64 for row in manifest["files"])
    assert downloaded_appimages(plan, tmp_path / "downloads") == (target / "demo.AppImage",)


def test_downloaded_appimage_selection_requires_exact_plan_file_and_size(tmp_path: Path) -> None:
    payload = {
        "tag_name": "v2", "draft": False,
        "assets": [
            {"name": "demo.AppImage", "size": 12,
             "browser_download_url": "https://github.com/a/b/releases/download/v2/demo.AppImage"},
            {"name": "notes.txt", "size": 4,
             "browser_download_url": "https://github.com/a/b/releases/download/v2/notes.txt"},
        ],
        "zipball_url": "https://api.github.com/repos/a/b/zipball/v2",
        "tarball_url": "https://api.github.com/repos/a/b/tarball/v2",
    }
    plan = parse_release("a/b", payload)
    target = tmp_path / "a/b/v2"; target.mkdir(parents=True)
    image = target / "demo.AppImage"; image.write_bytes(b"x" * 12)
    (target / "notes.txt").write_bytes(b"note")
    assert downloaded_appimages(plan, tmp_path) == (image,)
    image.write_bytes(b"short")
    assert downloaded_appimages(plan, tmp_path) == ()


def test_github_release_rejects_unsafe_names_and_overwrite(tmp_path: Path) -> None:
    payload = {
        "tag_name": "v1", "draft": False,
        "assets": [{"name": "../bad", "size": 1, "browser_download_url": "https://github.com/a/b/releases/download/v1/bad"}],
        "zipball_url": "https://api.github.com/repos/a/b/zipball/v1",
        "tarball_url": "https://api.github.com/repos/a/b/tarball/v1",
    }
    try:
        parse_release("a/b", payload)
    except GitHubReleaseError:
        pass
    else:
        raise AssertionError("unsafe asset name accepted")


def test_flatpak_and_snap_install_plans_are_argument_arrays(tmp_path: Path) -> None:
    def executable(name: str):
        return {"flatpak": "/usr/bin/flatpak", "snap": "/usr/bin/snap", "pkexec": "/usr/bin/pkexec"}.get(name)
    with patch("modules.programs.v1_0.install_plan.shutil.which", side_effect=executable):
        flatpak = build_install_plan("Flatpak", "org.example.App", "stable", tmp_path)
        snap = build_install_plan("Snap", "example", "latest/beta", tmp_path)
    assert flatpak.command == ("/usr/bin/flatpak", "install", "--user", "-y", "flathub", "org.example.App//stable")
    assert snap.command == ("/usr/bin/pkexec", "/usr/bin/snap", "install", "example", "--channel", "latest/beta")
    assert "shell" not in flatpak.display_command.casefold()


def test_appimage_plan_stays_inside_base_and_only_adds_user_execute(tmp_path: Path) -> None:
    image = tmp_path / "Demo.AppImage"
    image.write_bytes(b"\x7fELF\x00\x00\x00\x00AI\x02payload")
    image.chmod(0o600)
    plan = build_install_plan("AppImage", image, "", tmp_path)
    apply_appimage_plan(plan)
    assert image.stat().st_mode & 0o777 == 0o700
    outside = tmp_path.parent / f"{tmp_path.name}-Outside.AppImage"
    outside.write_bytes(b"\x7fELF\x00\x00\x00\x00AI\x02payload")
    try:
        build_install_plan("AppImage", outside, "", tmp_path)
    except InstallPlanError:
        pass
    else:
        raise AssertionError("AppImage outside base accepted")
    outside.unlink()


def test_system_and_invalid_identifiers_fail_closed(tmp_path: Path) -> None:
    for program_format, identifier in (("System", "demo"), ("Flatpak", "bad id;"), ("Snap", "../bad")):
        try:
            with patch("modules.programs.v1_0.install_plan.shutil.which", return_value="/usr/bin/tool"):
                build_install_plan(program_format, identifier, "", tmp_path)
        except InstallPlanError:
            pass
        else:
            raise AssertionError((program_format, identifier))


def test_programs_page_exposes_downloaded_appimage_profile_assignment() -> None:
    page = (ROOT / "src/modules/programs/v1_0/page.py").read_text(encoding="utf-8")
    assert "downloaded_appimages" in page
    assert "def assign_downloaded_appimage" in page
    sources = (
        "Heruntergeladenes AppImage", "Kein heruntergeladenes AppImage verfügbar",
        "AppImage dem ausgewählten Profil zuweisen", "Bitte zuerst ein AppImage-Profil auswählen.",
        "Das ausgewählte AppImage wurde dem Profil zugeordnet.",
    )
    for language in ("de", "en", "es", "fr"):
        assert all(source in UI_TRANSLATIONS[language] for source in sources)
