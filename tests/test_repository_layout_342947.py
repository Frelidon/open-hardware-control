#!/usr/bin/env python3
"""Guard the permanent repository layout and the short README (owner decision 06.09.26)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ROOT_ALLOWLIST = {
    "README.md",
    "LICENSE",
    "CITATION.cff",
    "AGENTS.md",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
}
ROOT_FOLDERS = {".cursor", ".github", "docs", "packaging", "scripts", "src", "tests", "tools"}
IGNORED = {".git", "dist", "__pycache__", ".pytest_cache", "build", ".venv", "venv"}
README_MAX_LINES = 200
HISTORY_MAX_VERSIONS = 4


def test_root_contains_only_allowlisted_entries() -> None:
    files = {p.name for p in ROOT.iterdir() if p.is_file()}
    folders = {p.name for p in ROOT.iterdir() if p.is_dir()} - IGNORED
    assert files <= ROOT_ALLOWLIST, f"unexpected root files: {sorted(files - ROOT_ALLOWLIST)}"
    assert folders <= ROOT_FOLDERS, f"unexpected root folders: {sorted(folders - ROOT_FOLDERS)}"


def test_root_agents_is_short_pointer() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "docs/ai/AGENTS.md" in text
    assert len(text.splitlines()) <= 12


def test_application_code_lives_in_src() -> None:
    assert (ROOT / "src" / "kraken_control.py").is_file()
    assert (ROOT / "src" / "assets").is_dir()
    assert (ROOT / "src" / "modules").is_dir()
    for name in ("install.sh", "uninstall.sh", "VERSION", "BUILD_CHANNEL"):
        assert (ROOT / "packaging" / name).is_file(), name
    for name in ("INSTALL.md", "CHANGELOG.md", "README.en.md"):
        assert (ROOT / "docs" / name).is_file(), name
    assert (ROOT / ".github" / "SECURITY.md").is_file()


def _check_readme(path: Path, history_heading: str, new_heading: str) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) <= README_MAX_LINES, f"{path.name} has {len(lines)} lines (max {README_MAX_LINES})"
    assert text.count(f"## {new_heading}") == 1, f"{path.name} must contain exactly one '{new_heading}' section"
    history = text.split(f"## {history_heading}", 1)[1]
    versions = re.findall(r"^\*\*(\d+\.\d+\.\d+(?:\.\d+)?)\*\*", history, re.M)
    assert 1 <= len(versions) <= HISTORY_MAX_VERSIONS, f"{path.name} history lists {len(versions)} versions"
    assert "images/screenshots/thumbs/" in text
    assert text.index("## Installation") < text.index("## Sicherheit" if "Sicherheit" in text else "## Security")


def test_german_readme_stays_short() -> None:
    _check_readme(ROOT / "README.md", "Versionsverlauf", "Neu in ")


def test_english_readme_stays_short() -> None:
    _check_readme(ROOT / "docs" / "README.en.md", "Version history", "New in ")
