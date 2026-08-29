# Open Hardware Control — Architecture

## Architectural principle

Open Hardware Control is a single Linux desktop application with modular hardware backends. The GUI may unify devices visually, but ownership, validation and transport remain separated so two subsystems do not write to the same physical device concurrently.

## Layers

### 1. UI / application orchestration

- `kraken_control.py` — executable PySide6 compatibility orchestrator, navigation, page composition and the still-unextracted legacy feature controllers.
- `app_constants.py` — application identity, version and shared defaults.
- `temperature_utils.py` — hardware-independent temperature unit conversion.
- `privacy_logging.py` — privacy redaction plus bounded startup/crash logging.
- `command_backend.py` — serialized `QProcess`/liquidctl command queue used by the UI orchestrator.
- `cooling_card_state.py` — pure single-expanded-card state transitions for the chassis-fan UI.
- `cooling_widgets.py` — hardware-independent curve editor and compact fan-curve preview.
- `localization_catalog.py` — static translations and built-in help topics without Qt/hardware dependencies.
- `ui_layout.py` — persisted UI layout/navigation model.
- `desktop_shell.py`, `desktop_designs.py`, `desktop_assets.py` — KDE desktop-design tooling kept logically separate from hardware writers.

`MODULE_MAP.md` is the task-oriented reading guide for local coding models. New base modules must not import `kraken_control.py`; the main file re-exports moved names during the incremental migration so existing tests and integrations remain compatible.

### 2. Coordination and ownership

- `hardware_request_coordinator.py` — serializes/prioritizes hardware requests where multiple UI features share a device path.
- `cooling_ownership.py` — prevents competing cooling controllers from writing simultaneously.
- Process/session locks in the application prevent duplicate OHC instances from owning the same hardware.

### 3. NZXT backend

- `nzxt_backend.py` — device/capability identification.
- `kraken_sensors.py` — telemetry/sensor handling.
- `kraken_cam_streamer.py` — LCD/CAM-compatible frame streaming path.
- `kraken_lcd_designs.py` — built-in LCD design/rendering logic.
- `nzxt_rgb.py` — NZXT RGB control and validated effects.
- `nzxt_esc_profiles.py` — NZXT CAM/ESC profile import handling.
- `71-nzxt-kraken-2023.rules` — udev access rule.

### 4. Mainboard chassis-fan backend

- `mainboard_fan_control.py` — Linux hwmon/NCT6687 discovery, calibration, curves, sensor selection and runtime safety.
- `ohc_fan_helper.py` — narrow privileged helper.
- `io.github.Frelidon.OpenHardwareControl.fan.policy` — Polkit authorization policy.
- `install-fan-helper.sh` — helper installation.

Safety invariant: unconfirmed channels are not automatically written, and firmware/BIOS ownership is restored when OHC control ends where supported.

### 4a. Thermalright Levita display and cooling

- `thermalright_display.py` — local media/TRCC discovery, display geometry, protected cutout and rendering model.
- `thermalright_display_ui.py` — Levita editor, test mode and optional bounded calls to the separately installed TRCC Linux backend.
- `thermalright_cooling.py` — read-only USB identity, driver-label-based PWM role suggestions and conservative profile duties.

The display USB path and motherboard PWM cooling path remain independent. A suggested header is never authorization to write: pump and radiator mappings require separate physical confirmation, CoolerControl ownership blocks writes, and firmware control is restored on exit. No coolant value is inferred from CPU temperature or RPM.

### 5. Corsair via OpenLinkHub

- `openlinkhub_integration.py` — validated local API integration.
- `openlinkhub_mouse_visuals.py` and `assets/mouse-*.svg` — generic project-owned mouse diagrams.

Safety invariant: OpenLinkHub communication remains on validated loopback endpoints; OHC does not invent direct Corsair USB commands.

### 6. OpenRGB / RGB Studio

- `openrgb_integration.py` — managed OpenRGB process/integration layer.
- `openrgb_sdk.py` — bounded loopback SDK protocol implementation.
- `rgb_devices.py` — device/group/topology model.
- `rgb_effects.py` — OHC software effects.

Safety invariant: only the private local engine is writable; external OpenRGB ownership blocks OHC writes. Device-reported capabilities and validated zone sizes are authoritative.

### 7. Release, diagnostics and security

- `collect-diagnostics.sh` — diagnostics collection with privacy handling.
- `scripts/check_release.sh` — compile/tests/security/version gate.
- `scripts/security_scan_release.py` — static release privacy/security scan.
- `scripts/build_release.py` / `.sh` — reproducible package generation.
- `scripts/create_release.sh`, `scripts/publish_github.sh` — GitHub publication entry points.
- `.cursor/hooks.json` — session context and confirmation for destructive shell/Git commands.

## Persistence

User configuration is persisted by the application; project design decisions are persisted in repository documentation. Agents must treat repository files, tests and Git history as higher-confidence project memory than conversational recollection.

## Extension pattern for new hardware

1. Add a dedicated backend/integration module.
2. Detect capabilities without writing first.
3. Establish ownership/conflict boundaries.
4. Validate every write parameter and provide safe fallback/release behavior.
5. Add diagnostic logging that avoids secrets and full serial numbers where unnecessary.
6. Add unit/static regression tests.
7. Document tested vs. merely detected support in `SUPPORTED_DEVICES.md` and `DEVICE_SUPPORT.md`.
8. Integrate UI only after the backend contract is clear.

Do not place model-specific protocol guesses directly into UI code.
