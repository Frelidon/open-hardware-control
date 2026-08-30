# Open Hardware Control — Project Status

**Current development version:** 3.4.29.7 INTERN

**Status date:** 30 August 2026

**Release channel:** INTERNAL — public release scripts remain blocked while `BUILD_CHANNEL=INTERN`.

## Current objective

Continue Open Hardware Control as a modular Linux hardware-control application while preserving the mature NZXT Kraken path and expanding validated integrations without introducing competing hardware writers.

Version 3.4.26 adds a repository-native AI development layer so Cursor, Codex, Claude Code and future coding agents can recover project context from files rather than depending on one long chat.

Version 3.4.29 adds a local-first Thermalright Levita Vision display studio to the LCD page. It imports user-selected local media and TRCC layout folders, provides a safe preview/test mode and delegates real USB communication to the separately installed GPL TRCC Linux backend.

Version 3.4.29.7 suppresses the OHC native window surface before a KDE/Wayland tray-autostart UI is constructed, closing the photographed black-window flash, and makes every OpenRGB Qt client invocation headless as a second window-suppression boundary. It also adds user-facing grant/remove controls for an optional exact-user Polkit rule so the fixed, bounded NCT6687 helper can be authorized once across reboots without storing a password.

The 3.4.29 codebase has also begun an incremental local-AI-oriented split of the historical `kraken_control.py` monolith. The executable remains compatible, while independent constants, temperature helpers, privacy logging, the serial command backend, cooling widgets and localization/help data now live in focused modules documented by `MODULE_MAP.md`.

## What 3.4.29 adds so far

- Hotfix 3.4.29.1 restores application startup by importing both private localized LCD/About source strings that were missed during the first modularization pass. A real offscreen construction test now builds all 11 main pages without initializing hardware.
- Hotfix 3.4.29.2 removes the graphical Qt dependency from the desktop-shell stop path, skips obsolete Kraken LCD profile writes on Levita systems and synchronizes manual controls with an activated temperature curve.
- The personal Thermaltake PC view now migrates its AIO labels to Thermalright Levita Vision 360 and records the Jungle Leopard GPU support as Airgoo Channel B6 with 24 LEDs, independently from both ENE-DRAM modules.
- Hotfix 3.4.29.3 keeps one narrowly validated Polkit fan-helper session alive after explicit authorization, so a running CPU curve no longer times out after the authorization cache expires. It also skips unnecessary liquidctl initialization on Thermalright-only systems, hides obsolete Kraken clock controls and learns a stable 7-to-6 OpenRGB inventory change without weakening the large-drop cold-start safeguard.
- Hotfix 3.4.29.4 fixes startup when the LCD studio restores a saved TRCC media directory before the main Log page exists. The regression now starts the complete UI with a persisted real image. TRCC Linux 9.9.11 has also physically completed the red/green/blue/black cycle on the reference `87ad:70db` display; its full handshake confirms model ID 64, sub-byte 3 and 1600×720.
- Hotfix 3.4.29.5 resets TRCC's persisted decorative split mode to zero before loading media. This avoids the confirmed TRCC 9.9.11/PySide6 6.11 `QImage.mirrored()` crash; styles A–C stay available as clearly marked local previews, while the physical 80-pixel right cutout remains protected.
- Version 3.4.29.6 applies a real adjustable black TRCC mask over the camera/notch area instead of merely drawing a preview guide. Its wider 320-pixel reference default, persistent background X/Y shift and two overlay spacing presets remain user-adjustable; locally prepared image/video copies never overwrite imported originals. Formats that already include `°C` or `%` now suppress TRCC's second unit suffix.
- Hotfix 3.4.29.7 prevents the photographed black OHC surface during minimized KDE/Wayland autostart, keeps every OpenRGB CLI process offscreen and offers explicit persistent-fan-authorization grant/remove controls without storing a password or weakening PWM calibration.

- Full-width Thermalright Levita Vision studio inside the existing LCD page.
- Local-only import for images, videos, `.zt` media and complete TRCC layout directories containing `config1.dc`; imported manufacturer assets are neither copied nor packaged.
- A true 1600×720 editor with a real adjustable 80–800-pixel black right-hand mask (320-pixel reference default), background X/Y movement and matching dynamic protection for movable hardware values.
- Movable, hideable, resizable and recolorable CPU temperature/load, GPU temperature/load, memory and clock overlays.
- Test mode enabled by default: previews and the local color-cycle test perform no USB writes.
- Hardware detection, color test, media/theme loading and the live metric render loop use bounded shell-free commands through the separately installed TRCC Linux backend. Decorative split modes remain preview-only until the confirmed TRCC Qt compatibility defect is fixed.
- Exact Thermalright Levita Vision 360 ARGB Black cooling identity with separate, user-confirmed motherboard mappings for its 4-pin PWM pump and radiator fans.
- Conservative cooling profiles and CPU-temperature curves become writable only after both relevant headers have passed the existing 70-percent/10-second physical test. CoolerControl ownership remains exclusive and OHC restores firmware control on exit.
- ENE-DRAM cold-start reclaim now runs two ordered Direct passes before profile animation, because the latest real log confirmed that one successful protocol pass can still leave the physical LEDs asleep.
- The previous 3.4.28 chassis-card behavior, modularization, CoolerControl ownership, application-wide blue design and confirmed Kraken profiles remain intact.

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
- Thermalright display/cooling: `thermalright_display.py`, `thermalright_display_ui.py`, `thermalright_cooling.py`.
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

## Confirmed next work and 3.4.29 progress

- RGB Studio, LCD, Profiles, Log, Corsair/OpenLinkHub, Settings, About and Help now share the current blue-tinted dashboard surface design.
- Kraken quick-profile buttons now track the last fully successful Leise, Ausbalanciert or Leistung write instead of displaying a static default.
- Mainboard chassis-fan cards keep their internal channel selection separate from visible expansion; all cards start collapsed and at most one explicitly opened card is expanded.
- CoolerControl ownership now distinguishes the `coolercontrold` background daemon from the closed graphical client, reports its autostart state and provides confirmed controls for temporary takeover or permanent service disable/enable.

## Known boundaries / not automatically claimed

- Hardware support beyond explicitly tested devices remains provisional until real-hardware verification.
- Thermalright Levita hardware support remains provisional: local editor/import/test mode, USB detection and read-only PWM/RPM discovery are verified. The physical display write via `trcc` and actual PWM response still require an in-app user confirmation; OHC therefore keeps every write behind explicit calibration.
- Firmware flashing/version switching is not a supported feature in this repository.
- GPU fan control is not part of the mainboard PWM subsystem.
- Open Radeon Control Center remains separate.

## Before the next public release

- Keep `BUILD_CHANNEL=INTERN` until real desktop/hardware testing is complete.
- Run all release checks.
- Verify current documentation/version references.
- Confirm no secrets/personal logs are present.
- Require a clean committed state and explicit project-owner approval before any GitHub push/tag/release.
