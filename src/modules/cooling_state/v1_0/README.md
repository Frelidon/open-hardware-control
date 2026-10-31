# Cooling state 1.0

Preserve explicitly saved master intent while asynchronous ownership discovery
is pending. Actual active state alone controls the blue dashboard and checkbox;
intent never grants PWM authority. A known free owner and existing calibration,
enabled channels, available adapter and user authorization remain mandatory.
Dashboard actions consume a fresh owner result, invalidate duplicate/stale click
callbacks and synchronize widgets on failure. Imported portable packages keep
their existing disabled-automation contract.

`cpu_defaults.py` keeps detected CPU defaults separate from user ownership.
Older settings are classified as automatic only when both saved curves still
match the selected processor profile. Any explicit profile or curve edit marks
the pair as user-owned, so later startup detection cannot overwrite it.

`startup_policy.py` separates the four legacy NZXT assistant presets from an
independent, explicitly selected PC startup profile. Only Ubuntu with the
actually detected Levita, no ready NZXT and an auto/Levita cooling selection
may bypass that pending-preset barrier. The preset remains stored and is not
applied as Thermalright PWM intent. Other platforms, real NZXT devices and
unknown pending values retain the old guard; explicit profile cooling still
uses the existing mapping, calibration and ownership checks.
