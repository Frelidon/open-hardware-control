#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validate current-only versioned modules and local-AI context budgets."""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MODULE_ROOT = ROOT / "modules"
REGISTRY_PATH = ROOT / "docs/project/MODULE_REGISTRY.md"
GUIDE_PATH = ROOT / "docs/ai/AI_DEVELOPMENT_GUIDE.md"
REVIEW_LINES = 800
REVIEW_CHARS = 40_000
HARD_LINES = 1_200
HARD_CHARS = 60_000


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    registry = REGISTRY_PATH.read_text(encoding="utf-8")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    channel = (ROOT / "BUILD_CHANNEL").read_text(encoding="utf-8").strip().upper()
    if re.search(r"\b\d{2}:\d{2}(?::\d{2})?\b", registry):
        errors.append("docs/project/MODULE_REGISTRY.md must not contain times")
    if channel not in {"INTERN", "STABLE"}:
        errors.append(f"BUILD_CHANNEL contains an invalid value: {channel}")
    elif f"**Anwendung:** {version} {channel}" not in registry:
        errors.append(
            f"docs/project/MODULE_REGISTRY.md does not match application version {version} {channel}"
        )
    if not GUIDE_PATH.is_file() or "AI_DEVELOPMENT_GUIDE.md" not in registry:
        errors.append("mandatory AI development guide is missing from the registry workflow")

    for feature in sorted(
        path for path in MODULE_ROOT.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    ):
        versions = sorted(
            path for path in feature.iterdir()
            if path.is_dir() and re.fullmatch(r"v\d+_\d+", path.name)
        )
        if len(versions) != 1:
            errors.append(f"{feature.relative_to(ROOT)} must contain exactly one current version folder")
            continue
        current = versions[0]
        relative = current.relative_to(ROOT).as_posix() + "/"
        dotted_version = current.name.removeprefix("v").replace("_", ".")
        if relative not in registry or f"| {dotted_version} |" not in registry:
            errors.append(f"registry does not identify {relative} as module version {dotted_version}")
        if not (current / "README.md").is_file():
            errors.append(f"missing module README: {current.relative_to(ROOT)}")
        for source in sorted(current.glob("*.py")):
            text = source.read_text(encoding="utf-8")
            lines = len(text.splitlines())
            chars = len(text)
            label = source.relative_to(ROOT)
            if lines > HARD_LINES or chars > HARD_CHARS:
                errors.append(f"{label} exceeds hard budget: {lines} lines / {chars} chars")
            elif lines > REVIEW_LINES or chars > REVIEW_CHARS:
                warnings.append(f"{label} reached split-review threshold: {lines} lines / {chars} chars")

    forbidden = re.compile(r"(?i)(?:^|[_-])(old|backup|copy)(?:[_-]|$)")
    for path in MODULE_ROOT.rglob("*"):
        if forbidden.search(path.stem):
            errors.append(f"backup/old copy forbidden in current module tree: {path.relative_to(ROOT)}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("Module registry and local-AI size budgets are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
