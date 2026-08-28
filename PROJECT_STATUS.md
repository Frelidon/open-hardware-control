# Open Hardware Control — Project Status

**Current development version:** 3.4.27 INTERN

**Status date:** 28 August 2026

**Release channel:** INTERNAL — public release scripts remain blocked while `BUILD_CHANNEL=INTERN`.

## Current objective

Continue Open Hardware Control as a modular Linux hardware-control application while preserving the mature NZXT Kraken path and expanding validated integrations without introducing competing hardware writers.

Version 3.4.26 adds a repository-native AI development layer so Cursor, Codex, Claude Code and future coding agents can recover project context from files rather than depending on one long chat.

Version 3.4.27 now combines clearer CoolerControl ownership and persistent service controls with the application-wide blue dashboard design and confirmed Kraken quick-profile feedback. The remaining cooling interaction work is tracked in `ROADMAP.md`.

The 3.4.27 codebase has also begun an incremental local-AI-oriented split of the historical `kraken_control.py` monolith. The executable remains compatible, while independent constants, temperature helpers, privacy logging, the serial command backend, cooling widgets and localization/help data now live in focused modules documented by `MODULE_MAP.md`.

## What 3.4.27 adds so far

- Separate reporting for the CoolerControl graphical client, active `coolercontrold` background service and service-autostart state.
- Confirmed Polkit actions to stop CoolerControl temporarily, disable it permanently or enable and start it again.
- Safe ownership transitions: disabling CoolerControl never starts OHC fan control automatically; enabling CoolerControl first returns mainboard channels to firmware/BIOS ownership.
- Blue-tinted cards, editors, tables and inputs across RGB Studio, LCD, Profiles, Log, Corsair/OpenLinkHub, Settings, About, Help and Kraken detail areas.
- Kraken Leise/Ausbalanciert/Leistung buttons become fully blue only after both requested hardware writes succeed and are cleared by individual/manual control.
- Local AI handoff files and a credential-free Git bundle provide LM Studio/Qwen2.5-Coder setup, full branch history, a mandatory repository startup sequence and a permission-gated GitHub branch workflow without storing credentials.
- First compatibility-preserving monolith split: six focused modules reduce the main file by roughly 1,600 lines, avoid circular imports and are included in installation and release packaging.
- Chassis-fan cards now start collapsed, expose `Kurve & Details bearbeiten` on every card, expand only one explicit selection and collapse again when the action or embedded editor is closed.

## What 3.4.26 adds

- Root `AGENTS.md` as the primary durable agent instruction set.
- `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `DEVICE_SUPPORT.md` and `AI_HANDOFF.md` as maintained project memory.
- Cursor project rules under `.cursor/rules/`.
- Cursor slash workflows under `.cursor/commands/`.
- Project-level Cursor hooks with session context injection and destructive-command confirmation.
- Release/publish scripts that enforce release channel, clean-worktree, authentication and test requirements without an external backup dependency.

## Current major modules

- NZXT Kraken control: `nzxt_backend.py`, `kraken_sensors.py`, `kraken_cam_streamer.py`, `kraken_lcd_designs.py`, `nzxt_rgb.py`, `nzxt_esc_profiles.py`.
- Main GUI and orchestration: `kraken_control.py`, `cooling_widgets.py`, `localization_catalog.py`, `ui_layout.py`.
- Shared application infrastructure: `app_constants.py`, `temperature_utils.py`, `privacy_logging.py`, `command_backend.py`.
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

## Confirmed next work and 3.4.27 progress

- RGB Studio, LCD, Profiles, Log, Corsair/OpenLinkHub, Settings, About and Help now share the current blue-tinted dashboard surface design.
- Kraken quick-profile buttons now track the last fully successful Leise, Ausbalanciert or Leistung write instead of displaying a static default.
- Mainboard chassis-fan cards keep their internal channel selection separate from visible expansion; all cards start collapsed and at most one explicitly opened card is expanded.
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
