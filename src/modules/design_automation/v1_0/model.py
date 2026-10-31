#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded rule model for application, game, clock and interval automations."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from typing import Iterable

_CLOCK_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


@dataclass(frozen=True)
class AutomationRule:
    rule_id: str
    name: str
    enabled: bool
    trigger: str
    trigger_value: str
    profile_id: str
    priority: int = 50
    restore_previous: bool = True

    @classmethod
    def from_mapping(cls, value: object) -> "AutomationRule | None":
        if not isinstance(value, dict):
            return None
        rule_id = str(value.get("rule_id", ""))[:64]
        name = str(value.get("name", "Automatisierung")).strip()[:80]
        trigger = str(value.get("trigger", "process"))
        if trigger not in {"process", "game", "time", "interval"}:
            trigger = "process"
        raw = str(value.get("trigger_value", "")).strip()[:260]
        if trigger in {"process", "game"}:
            raw = raw.replace("\\", "/").rsplit("/", 1)[-1].casefold()
        elif trigger == "time" and not _CLOCK_RE.fullmatch(raw):
            raw = "18:00"
        elif trigger == "interval":
            try:
                raw = str(max(1, min(1440, int(raw))))
            except ValueError:
                raw = "30"
        return cls(
            rule_id=rule_id,
            name=name or "Automatisierung",
            enabled=bool(value.get("enabled", True)),
            trigger=trigger,
            trigger_value=raw,
            profile_id=str(value.get("profile_id", ""))[:96],
            priority=max(0, min(100, int(value.get("priority", 50)))),
            restore_previous=bool(value.get("restore_previous", True)),
        )

    def to_mapping(self) -> dict[str, object]:
        return asdict(self)


def process_matches(rule: AutomationRule, running_names: Iterable[str]) -> bool:
    if not rule.enabled or rule.trigger not in {"process", "game"} or not rule.trigger_value:
        return False
    wanted = rule.trigger_value.casefold()
    return any(str(name).casefold() == wanted for name in running_names)


def winning_process_rule(rules: Iterable[AutomationRule], running_names: Iterable[str]) -> AutomationRule | None:
    names = tuple(running_names)
    candidates = [rule for rule in rules if process_matches(rule, names)]
    return max(candidates, key=lambda rule: (rule.priority, rule.rule_id), default=None)
