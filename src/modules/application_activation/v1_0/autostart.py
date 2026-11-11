# SPDX-License-Identifier: GPL-3.0-or-later
"""Retarget existing OHC autostart entries during a user installation."""

from pathlib import Path
import os
import re
import shlex
import stat
import sys
import tempfile


def _quote(value: str) -> str:
    escaped = value.replace("%", "%%")
    for character in ("\\", '"', "`", "$"):
        escaped = escaped.replace(character, "\\" + character)
    return f'"{escaped}"'


def retarget_entry(text: str, home: Path, launcher: Path, icon: Path) -> str:
    """Preserve comments, disabled flags and custom arguments; never enable it."""
    recognized = {"open-hardware-control", "kraken-control",
                  "/usr/bin/open-hardware-control", "/usr/bin/kraken-control",
                  str(home / ".local/bin/open-hardware-control"),
                  str(home / ".local/bin/kraken-control")}
    lines = text.splitlines(keepends=True)
    section, replacements = "", {}
    for index, line in enumerate(lines):
        value = line.strip()
        if value.startswith("["):
            section = value
        if section != "[Desktop Entry]" or "=" not in line:
            continue
        key, value = line.rstrip("\r\n").split("=", 1)
        if key == "Exec":
            try:
                args = shlex.split(value)
            except ValueError:
                return text
            if not args or args[0] not in recognized:
                return text  # retain an explicitly customized wrapper
            match = re.match(r'^(?:"[^"\\]*(?:\\.[^"\\]*)*"|\S+)(.*)$', value)
            if match is None:
                return text
            suffix = match.group(1)
            if "--autostart" not in args[1:]:
                suffix += " --autostart"
            replacements[index] = f"Exec={_quote(str(launcher))}{suffix}\n"
        elif key == "Icon":
            replacements[index] = f"Icon={icon}\n"
        elif key == "TryExec":
            replacements[index] = f"TryExec={launcher}\n"
    if not any(value.startswith("Exec=") for value in replacements.values()):
        return text
    for index, value in replacements.items():
        lines[index] = value
    return "".join(lines)


def update_existing(home: Path, launcher: Path, icon: Path) -> None:
    for name in ("open-hardware-control.desktop", "kraken-control.desktop"):
        path = home / ".config/autostart" / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 65_536:
            continue
        original = path.read_text(encoding="utf-8")
        updated = retarget_entry(original, home, launcher, icon)
        if updated == original:
            continue
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".ohc-autostart-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(updated)
        try:
            temporary.chmod(stat.S_IMODE(path.stat().st_mode))
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: autostart.py HOME LAUNCHER ICON")
    update_existing(*(Path(value) for value in sys.argv[1:]))
