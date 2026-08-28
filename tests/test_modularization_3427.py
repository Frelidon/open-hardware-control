#!/usr/bin/env python3
"""Regression guards for the first local-AI-oriented monolith split."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
main_path = ROOT / "kraken_control.py"
main_code = main_path.read_text(encoding="utf-8")
main_tree = ast.parse(main_code)

modules = {
    "app_constants.py": ("APP_VERSION", "KRAKEN_MATCH"),
    "command_backend.py": ("CommandResult", "Backend"),
    "cooling_widgets.py": ("CurveEditor", "FanCurveMiniPreview"),
    "localization_catalog.py": ("UI_TRANSLATIONS", "SETUP_TRANSLATIONS", "HELP_TOPICS"),
    "privacy_logging.py": ("redact_private_text", "write_application_crash_log"),
    "temperature_utils.py": ("normalize_temperature_unit", "celsius_to_display"),
}

for filename, exports in modules.items():
    path = ROOT / filename
    assert path.is_file(), filename
    source = path.read_text(encoding="utf-8")
    ast.parse(source)
    assert "import kraken_control" not in source
    for export in exports:
        assert export in source, f"{export} missing from {filename}"

top_level_names = {
    node.name
    for node in main_tree.body
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
}
for moved_name in (
    "Backend", "CommandResult", "PendingCommand", "CurveEditor",
    "FanCurveMiniPreview", "redact_private_text", "application_state_directory",
    "normalize_temperature_unit", "celsius_to_display",
    "_help_topic",
):
    assert moved_name not in top_level_names, moved_name

assert len(main_code.splitlines()) < 22_000
assert "from command_backend import Backend, CommandResult, PendingCommand" in main_code
assert "from cooling_widgets import CurveEditor, FanCurveMiniPreview" in main_code
assert "from localization_catalog import HELP_TOPICS, SETUP_TRANSLATIONS, UI_TRANSLATIONS" in main_code
assert "from app_constants import (" in main_code

print("3.4.27 modularization and local-AI context guards passed.")
