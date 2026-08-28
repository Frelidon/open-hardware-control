#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Frelidon contributors
"""Unit conversion helpers shared by UI widgets and control logic."""

from __future__ import annotations


def normalize_temperature_unit(value: object) -> str:
    return "f" if str(value).strip().casefold() in {"f", "fahrenheit", "°f"} else "c"


def celsius_to_display(value: float, unit: str) -> float:
    return value * 9.0 / 5.0 + 32.0 if normalize_temperature_unit(unit) == "f" else value


def display_to_celsius(value: float, unit: str) -> float:
    return (value - 32.0) * 5.0 / 9.0 if normalize_temperature_unit(unit) == "f" else value


def temperature_symbol(unit: str) -> str:
    return "°F" if normalize_temperature_unit(unit) == "f" else "°C"
