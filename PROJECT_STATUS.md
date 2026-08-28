# Open Hardware Control — Project Status

**Current development version:** 3.4.26 INTERN

**Status date:** 28 August 2026

**Release channel:** INTERNAL — public release scripts remain blocked while `BUILD_CHANNEL=INTERN`.

## Current objective

Continue Open Hardware Control as a modular Linux hardware-control application while preserving the mature NZXT Kraken path and expanding validated integrations without introducing competing hardware writers.

Version 3.4.26 adds a repository-native AI development layer so Cursor, Codex, Claude Code and future coding agents can recover project context from files rather than depending on one long chat.

The next internal work starts with a consistent application-wide design pass, followed by a focused cooling interaction pass. The detailed sequence is maintained in `ROADMAP.md`.

## What 3.4.26 adds

- Root `AGENTS.md` as the primary durable agent instruction set.
- `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `DEVICE_SUPPORT.md` and `AI_HANDOFF.md` as maintained project memory.
- Cursor project rules under `.cursor/rules/`.
- Cursor slash workflows under `.cursor/commands/`.
- Project-level Cursor hooks with session context injection and destructive-command confirmation.
- Release/publish scripts that enforce release channel, clean-worktree, authentication and test requirements without an external backup dependency.

## Current major modules

- NZXT Kraken control: `nzxt_backend.py`, `kraken_sensors.py`, `kraken_cam_streamer.py`, `kraken_lcd_designs.py`, `nzxt_rgb.py`, `nzxt_esc_profiles.py`.
- Main GUI and orchestration: `kraken_control.py`, `ui_layout.py`.
- Hardware request coordination: `hardware_request_coordinator.py`, `cooling_ownership.py`.
- Mainboard fan control: `mainboard_fan_control.py`, `ohc_fan_helper.py` plus Polkit policy.
- Corsair/OpenLinkHub: `openlinkhub_integration.py`, `openlinkhub_mouse_visuals.py`.
- RGB/OpenRGB: `openrgb_integration.py`, `openrgb_sdk.py`, `rgb_devices.py`, `rgb_effects.py`.
- Desktop customization: `desktop_shell.py`, `desktop_designs.py`, `desktop_assets.py`.
- Release/security tooling: `scripts/` and `.github/workflows/`.

## Important current product behavior

- Persistent sidebar customization supports drag/drop and per-module visibility.
- Overview, Navigation customization and Help are permanent and cannot be hidden or removed.
- Cooling UI uses compact system-fan cards and embedded curve editing.
- Mainboard chassis fans default to CPU temperature for untouched legacy defaults and retain calibration/safety ownership logic.
- RGB Studio manages a private loopback OpenRGB engine and isolates conflicting/external writers.
- Corsair remains mediated through local OpenLinkHub rather than direct, guessed Corsair USB writes.
- LCD/GIF and Kraken hardware requests remain coordinated so simultaneous subsystems do not fight for the same device.

## Confirmed next work and first 3.4.27 progress

- RGB Studio, LCD, Profiles, Log, Corsair/OpenLinkHub, Settings, About and Help still use mixed page structures and need the current dashboard design applied consistently.
- Kraken quick-profile buttons do not yet update their active visual state after a successful Leise, Ausbalanciert or Leistung write.
- Mainboard chassis-fan cards currently select and expand the first detected channel automatically; the target behavior is collapsed by default with at most one explicitly selected card expanded.
- CoolerControl ownership now distinguishes the `coolercontrold` background daemon from the closed graphical client, reports its autostart state and provides confirmed controls for temporary takeover or permanent service disable/enable.

## Known boundaries / not automatically claimed

- Hardware support beyond explicitly tested devices remains provisional until real-hardware verification.
- Firmware flashing/version switching is not a supported feature in this repository.
- GPU fan control is not part of the mainboard PWM subsystem.
- Open Radeon Control Center remains separate.

## Before the next public release

- Keep `BUILD_CHANNEL=INTERN` until real desktop/hardware testing is complete.
- Run all release checks.
- Verify current documentation/version references.
- Confirm no secrets/personal logs are present.
- Require a clean committed state and explicit project-owner approval before any GitHub push/tag/release.
