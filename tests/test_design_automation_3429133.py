#!/usr/bin/env python3
"""Regression coverage for retained .133 themes, rules and original effects."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from modules.design_automation.v1_0.model import (  # noqa: E402
    AutomationRule, process_matches, winning_process_rule,
)
from modules.display_effects.v1_11.catalog import DESIGNS, validated_asset  # noqa: E402
from rgb_effects import BUILTIN_DESIGNS, BUILTIN_DESIGN_CATEGORIES  # noqa: E402


def _rule(**values):
    payload = {
        "rule_id": "rule-1", "name": "Game", "enabled": True,
        "trigger": "game", "trigger_value": "/games/demo.x86_64",
        "profile_id": "user-game", "priority": 50, "restore_previous": True,
    }
    payload.update(values)
    rule = AutomationRule.from_mapping(payload)
    assert rule is not None
    return rule


def test_rule_model_bounds_and_matches_only_exact_process_basename():
    rule = _rule(priority=500)
    assert rule.trigger_value == "demo.x86_64"
    assert rule.priority == 100
    assert process_matches(rule, ("steam", "demo.x86_64"))
    assert not process_matches(rule, ("not-demo.x86_64",))
    assert AutomationRule.from_mapping({"trigger": "interval", "trigger_value": "99999"}).trigger_value == "1440"


def test_higher_priority_matching_rule_wins():
    low = _rule(rule_id="low", priority=10)
    high = _rule(rule_id="high", priority=90)
    assert winning_process_rule((low, high), ("demo.x86_64",)) == high


def test_four_original_display_loops_and_matching_rgb_profiles_are_bundled():
    ids = {design.ident for design in DESIGNS}
    expected = {"ohc-prism-drift", "ohc-twin-wyrm", "ohc-neon-garden", "ohc-circuit-chase"}
    assert expected <= ids
    for design in DESIGNS:
        if design.ident in expected:
            assert design.license_name == "GPL-3.0-or-later"
            assert validated_asset(design.variants[0]).is_file()
            assert validated_asset(design.variants[0], preview=True).is_file()
    assert [title for title, _config in BUILTIN_DESIGNS[30:34]] == [
        "Prism Drift", "Twin Wyrm Orbit", "Neon Particle Garden", "Circuit Chase",
    ]
    assert BUILTIN_DESIGN_CATEGORIES[30:34] == ("Räumlich", "Räumlich", "Energie", "Bewegung")


def test_automation_probe_and_mangohud_path_are_not_shell_executed():
    page = (SRC / "modules/design_automation/v1_0/page.py").read_text(encoding="utf-8")
    assert "subprocess" not in page
    assert "MANGOHUD_CONFIGFILE=" in page
    assert "host.apply_profile_by_id" in page
    assert "QProcess" in page
