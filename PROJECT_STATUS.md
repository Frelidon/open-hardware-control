# Open Hardware Control — Project Status

**Current development version:** 3.4.26 INTERN  
**Status date:** 27 August 2026  
**Release channel:** INTERNAL — public release scripts remain blocked while `BUILD_CHANNEL=INTERN`.

## Current objective

Continue Open Hardware Control as a modular Linux hardware-control application while preserving the mature NZXT Kraken path and expanding validated integrations without introducing competing hardware writers.

Version 3.4.26 adds a repository-native AI development layer so Cursor, Codex, Claude Code and future coding agents can recover project context from files rather than depending on one long chat.

## What 3.4.26 adds

- Root `AGENTS.md` as the primary durable agent instruction set.
- `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `DEVICE_SUPPORT.md` and `AI_HANDOFF.md` as maintained project memory.
- Cursor project rules under `.cursor/rules/`.
- Cursor slash workflows under `.cursor/commands/`.
- Project-level Cursor hooks with a `beforeShellExecution` GitHub backup gate and destructive-command confirmation guard.
- A reproducible Git backup bundle + HEAD source snapshot with SHA-256 verification.
- A confirmation record bound to the exact Git `HEAD`; a new commit invalidates the previous push authorization automatically.
- Google Drive workflow documentation using Cursor's official Google Drive plugin without storing OAuth credentials in the repository.
- Release/publish scripts wired to refuse GitHub publication if the backup gate is not valid.

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

## Known boundaries / not automatically claimed

- Hardware support beyond explicitly tested devices remains provisional until real-hardware verification.
- Firmware flashing/version switching is not a supported feature in this repository.
- GPU fan control is not part of the mainboard PWM subsystem.
- Open Radeon Control Center remains separate.
- Cursor Google Drive OAuth cannot be embedded in source; the user must connect the official plugin once in Cursor.

## Before the next public release

- Keep `BUILD_CHANNEL=INTERN` until real desktop/hardware testing is complete.
- Run all release checks.
- Verify current documentation/version references.
- Confirm no secrets/personal logs are present.
- Create and verify a Google Drive backup for the exact final commit before any GitHub push/tag/release.
