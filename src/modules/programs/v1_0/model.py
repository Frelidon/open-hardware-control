# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure bounded inventory and profile model for Programs 1.0."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import shlex
from typing import Callable


FORMATS = ("System", "Flatpak", "Snap", "AppImage")
MAX_ENTRIES = 1600
MAX_PROFILES = 300


@dataclass(frozen=True)
class InstalledProgram:
    name: str
    identifier: str
    format: str
    executable: str


@dataclass(frozen=True)
class ProgramProfile:
    name: str
    identifier: str
    format: str
    version: str = ""
    executable: str = ""
    repository: str = ""
    source_version: str = ""


def _value(lines: tuple[str, ...], key: str) -> str:
    prefix = key + "="
    return next((line[len(prefix):].strip() for line in lines if line.startswith(prefix)), "")


def _command(raw: str) -> tuple[str, ...]:
    try:
        return tuple(token for token in shlex.split(raw[:2048]) if not token.startswith("%"))
    except ValueError:
        return ()


def desktop_programs(
    roots: tuple[Path, ...] | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> tuple[InstalledProgram, ...]:
    """Read a bounded set of desktop entries without executing their commands."""
    locations = roots or (
        Path.home() / ".local/share/applications",
        Path("/var/lib/flatpak/exports/share/applications"),
        Path.home() / ".local/share/flatpak/exports/share/applications",
        Path("/usr/local/share/applications"),
        Path("/usr/share/applications"),
    )
    found: dict[tuple[str, str], InstalledProgram] = {}
    remaining = MAX_ENTRIES
    for root in locations:
        if remaining <= 0 or (cancelled is not None and cancelled()):
            break
        try:
            entries = sorted(root.glob("*.desktop"))[:remaining]
        except OSError:
            continue
        remaining -= len(entries)
        for entry in entries:
            if cancelled is not None and cancelled():
                return tuple(sorted(found.values(), key=lambda item: (item.name.casefold(), item.format)))
            try:
                lines = tuple(entry.read_text(encoding="utf-8", errors="replace").splitlines()[:320])
            except OSError:
                continue
            if _value(lines, "NoDisplay").casefold() == "true":
                continue
            name = _value(lines, "Name")[:160]
            tokens = _command(_value(lines, "Exec"))
            if not name or not tokens:
                continue
            program_format, identifier, executable = "System", Path(tokens[0]).name, tokens[0]
            if Path(tokens[0]).name == "flatpak":
                candidates = [token for token in tokens[1:] if token != "run" and not token.startswith("-")]
                if candidates:
                    program_format, identifier = "Flatpak", candidates[-1][:256]
            elif Path(tokens[0]).name == "snap":
                candidates = [token for token in tokens[1:] if token != "run" and not token.startswith("-")]
                if candidates:
                    program_format, identifier = "Snap", candidates[-1][:256]
            elif tokens[0].casefold().endswith(".appimage"):
                program_format, identifier = "AppImage", str(Path(tokens[0]).expanduser())[:1024]
            identifier = identifier.strip()
            if not identifier:
                continue
            key = program_format.casefold(), identifier.casefold()
            found.setdefault(key, InstalledProgram(name, identifier, program_format, executable[:1024]))
    return tuple(sorted(found.values(), key=lambda item: (item.name.casefold(), item.format)))


def default_programs_folder(home: Path | None = None) -> Path:
    """Resolve the XDG documents folder without executing a helper process."""
    owner = home or Path.home()
    documents = owner / "Documents"
    try:
        lines = (owner / ".config/user-dirs.dirs").read_text(encoding="utf-8", errors="replace").splitlines()[:80]
    except OSError:
        lines = []
    prefix = "XDG_DOCUMENTS_DIR="
    raw = next((line[len(prefix):].strip().strip('"') for line in lines if line.startswith(prefix)), "")
    if raw:
        expanded = raw.replace("$HOME", str(owner), 1)
        candidate = Path(expanded).expanduser()
        if candidate.is_absolute():
            documents = candidate
    return documents / "Open Hardware Control" / "Programs"


def normalize_base_folder(raw: object, fallback: Path | None = None) -> Path:
    default = fallback or default_programs_folder()
    text = str(raw or "").strip()
    candidate = Path(text).expanduser() if text else default
    return candidate if candidate.is_absolute() else default


def profile_from_program(program: InstalledProgram) -> ProgramProfile:
    return ProgramProfile(program.name, program.identifier, program.format, executable=program.executable)


def dump_profiles(profiles: tuple[ProgramProfile, ...]) -> str:
    return json.dumps([asdict(item) for item in profiles[:MAX_PROFILES]], ensure_ascii=False, separators=(",", ":"))


def load_profiles(raw: object) -> tuple[ProgramProfile, ...]:
    try:
        values = json.loads(str(raw or "[]"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return ()
    if not isinstance(values, list):
        return ()
    result: list[ProgramProfile] = []
    seen: set[tuple[str, str]] = set()
    for value in values[:MAX_PROFILES]:
        if not isinstance(value, dict):
            continue
        name = str(value.get("name", "")).strip()[:160]
        identifier = str(value.get("identifier", "")).strip()[:1024]
        program_format = str(value.get("format", "System"))
        version = str(value.get("version", "")).strip()[:80]
        executable = str(value.get("executable", "")).strip()[:1024]
        repository = str(value.get("repository", "")).strip()[:220]
        source_version = str(value.get("source_version", "")).strip()[:120]
        if not name or not identifier or program_format not in FORMATS:
            continue
        key = program_format.casefold(), identifier.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(ProgramProfile(name, identifier, program_format, version, executable, repository, source_version))
    return tuple(result)
