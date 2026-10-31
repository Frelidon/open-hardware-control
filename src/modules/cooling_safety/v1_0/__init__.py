"""Hardware-specific cooling duty floors."""

from .policy import CoolingDutyPolicy, clamp_cooling_duty, cooling_duty_policy

__all__ = ["CoolingDutyPolicy", "clamp_cooling_duty", "cooling_duty_policy"]
