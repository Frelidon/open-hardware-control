#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure path validation for handing display-effect media to Levita Studio."""

from __future__ import annotations

from pathlib import Path


def validate_effect_handoff(path: Path, allowed_root: Path) -> Path:
    """Return one regular MP4 below the explicitly selected trusted root."""

    root = allowed_root.expanduser().resolve()
    candidate_path = path.expanduser()
    candidate = candidate_path.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("Display-Effekt liegt außerhalb des erlaubten OHC-Bereichs") from exc
    if (
        not root.is_dir()
        or candidate_path.is_symlink()
        or not candidate.is_file()
        or candidate.suffix.casefold() != ".mp4"
    ):
        raise ValueError("Display-Effekt ist keine sichere lokale MP4-Datei")
    return candidate
