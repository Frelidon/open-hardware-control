#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Conservative model-aware PWM floors for supported liquid coolers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CoolingDutyPolicy:
    hardware_key: str
    pump_minimum: int
    fan_minimum: int
    pump_rated_max_rpm: int | None = None
    fan_rated_max_rpm: int | None = None
    manufacturer_minimum_published: bool = False
    note: str = ""

    def minimum(self, channel: str) -> int:
        if channel == "pump":
            return self.pump_minimum
        if channel == "fan":
            return self.fan_minimum
        raise ValueError(f"unknown cooling channel: {channel}")


POLICIES = {
    "thermalright-levita-vision-360-argb-black": CoolingDutyPolicy(
        hardware_key="thermalright-levita-vision-360-argb-black",
        pump_minimum=50,
        fan_minimum=25,
        pump_rated_max_rpm=3000,
        fan_rated_max_rpm=2000,
        manufacturer_minimum_published=False,
        note=(
            "Thermalright publishes 3000 rpm ±10% maximum pump speed and 2000 rpm ±10% "
            "maximum TL-M12Q fan speed, but no minimum PWM duty. OHC therefore uses a "
            "conservative 50% pump and 25% radiator floor until a model-specific minimum is published."
        ),
    ),
    "nzxt": CoolingDutyPolicy(
        hardware_key="nzxt",
        pump_minimum=20,
        fan_minimum=0,
        manufacturer_minimum_published=False,
        note="Validated application command range retained for supported NZXT Kraken devices.",
    ),
}


def cooling_duty_policy(hardware_key: str) -> CoolingDutyPolicy:
    return POLICIES.get(str(hardware_key), POLICIES["nzxt"])


def clamp_cooling_duty(hardware_key: str, channel: str, duty: int | float) -> int:
    policy = cooling_duty_policy(hardware_key)
    return max(policy.minimum(channel), min(100, int(round(float(duty)))))
