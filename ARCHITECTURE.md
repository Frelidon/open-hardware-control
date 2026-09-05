# Open Hardware Control — Architecture

## Architectural principle

Open Hardware Control is a single Linux desktop application with modular hardware backends. The GUI may unify devices visually, but ownership, validation and transport remain separated so two subsystems do not write to the same physical device concurrently.

`MODULE_REGISTRY.md` is the authoritative machine-readable task-to-module index. New or migrated feature code lives in exactly one current `modules/<name>/v<major>_<minor>/` directory. Module version and application version are independent: a later application release may still use a stable module 1.0. `AI_DEVELOPMENT_GUIDE.md` defines the mandatory extension steps and file-size budgets for context-limited coding models.

## Layers

### 1. UI / application orchestration

- `kraken_control.py` — executable PySide6 compatibility orchestrator, navigation, page composition and the still-unextracted legacy feature controllers.
- `app_constants.py` — application identity, version and shared defaults.
- `branding.py` — project-owned logo/icon selection, the compact sidebar brand surface and a dedicated 22/32/48/64 raster set for Plasma's system-tray entry.
- `temperature_utils.py` — hardware-independent temperature unit conversion.
- `privacy_logging.py` — privacy redaction plus bounded startup/crash logging.
- `window_diagnostics.py` — early privacy-bounded Qt-window and helper-process tracing plus an exact-signature quarantine for the observed unnamed parentless 640×480 `QFrame`.
- `command_backend.py` — serialized `QProcess`/liquidctl command queue used by the UI orchestrator.
- `cooling_card_state.py` — pure single-expanded-card state transitions for the chassis-fan UI.
- `cooling_widgets.py` — hardware-independent curve editor and compact fan-curve preview.
- `localization_catalog.py` — static translations and built-in help topics without Qt/hardware dependencies.
- `ui_layout.py` — persisted UI layout/navigation model.
- `modules/window_placement/v1_0/placement.py` — Qt-independent normalization and selection policy for a primary or explicitly named startup screen; unavailable names fall back to primary.
- `desktop_shell.py`, `desktop_designs.py`, `desktop_assets.py` — KDE desktop-design tooling kept logically separate from hardware writers.
- `modules/wallpaper_engine/v1_2/` — local Wallpaper Engine for KDE library, Plasma adapter, onboarding, verified Fedora installer and page; the installed CaptSilver plugin remains the renderer and owner of its QML configuration surface.

`MODULE_MAP.md` is the task-oriented reading guide for local coding models after they resolve the current version in `MODULE_REGISTRY.md`. New base modules must not import `kraken_control.py`; the main file re-exports moved names during the incremental migration so existing tests and integrations remain compatible.

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

Safety invariant: unconfirmed channels are not automatically written, and firmware/BIOS ownership is restored when OHC control ends where supported. The optional persistent authorization is one exact-account Polkit rule for the same fixed helper action; it changes only whether Polkit asks again and does not widen the helper protocol or bypass calibration.

### 4a. Thermalright Levita display and cooling

- `thermalright_display.py` — local media/TRCC discovery, non-destructive complete-filename catalog deduplication, strict Levita geometry filtering, protected cutout and rendering model.
- `dashboard_layout.py` — small dashboard-layout mixin that combines saved card preferences with current hardware/value availability; it performs no hardware discovery or writes.
- `thermalright_display_ui.py` — legacy-compatible thin orchestration for the card library, media preparation, process queue and the versioned editor module.
- `modules/lcd_levita/v1_4/layout_model.py` — pure, malformed-record-tolerant layer-2 block model, coordinate bounds, whole-layout offsets and settings serialization.
- `modules/lcd_levita/v1_4/layout_canvas.py` — Qt canvas interaction: one stable draggable graphics item per logical data block; right-click requests the inline property editor in the surrounding surface instead of opening a dialog.
- `modules/lcd_levita/v1_4/panel_geometry.py` — pure 1600×720 geometry for separately adjustable top/bottom media radii at the right notch boundary and the independent outer panel outline.
- `modules/lcd_levita/v1_4/runtime_policy.py` — pure validation and safe fallback for persisted Levita runtime settings.
- `modules/lcd_levita/v1_4/theme_adapter.py` — read-only import of `trcc.json` or delegated legacy `config1.dc` decoding and immutable OHC cache-theme staging; selected video and generated mask are linked into the same staged theme to keep the hardware apply in one connected `load-theme` session.
- `thermalright_cooling.py` — read-only USB identity, driver-label-based PWM role suggestions and conservative profile duties.

The display USB path and motherboard PWM cooling path remain independent. A suggested header is never authorization to write: pump and radiator mappings require separate physical confirmation, CoolerControl ownership blocks writes, and firmware control is restored on exit. No coolant value is inferred from CPU temperature or RPM. Levita display autostart is a separate explicit setting; discovery alone never writes and test mode remains authoritative. Before an explicit display write, the active play loop releases and OHC replaces any stale daemon device with a tolerated detach plus mandatory fresh handshake; confirmed handshake timeouts receive at most one bounded retry.

Imported Levita source files are immutable. OHC stores user edits as its own settings override and stages a content-addressed cache directory containing generated `trcc.json` plus links to the selected local artwork/media. The external folder scanner rejects symlinked theme inputs, while this private validated cache is accepted by the runtime loader. It never rewrites `config1.dc`. A CPU/GPU label, live usage value and suffix stay one logical block and move together; common TRCC layouts that store the caption and usage as adjacent separate elements are coalesced in OHC's editable model. Controlled shutdown first stops local display clients and then sends one bounded daemon-only `stop-video` request to restore the active TRCC theme.

Layer intensity is presentation state: layer 1 is stored globally and layer 2 per selected design, both bounded to 25–150%. Explicit units in bundled formats always use `show_unit=true`. `hardware_diagnostics.py` reads sensors without writes; TRCC's misinterpreted low-Hz range through 1,000,000 Hz may temporarily replace only the affected live format through daemon IPC and restores the dynamic format on recovery. General plausibility polling logs state transitions only.

Before `load-theme`, legacy orchestration accepts either the original `config1.dc` contract or a bounded native `trcc.json` whose root, element list and exact 1600×720 geometry validate. This mirrors TRCC Linux's loader and prevents OHC's own editable cache from being rejected. A layer-2 selection must not rebuild the background-card catalog; hidden combo state is updated under blocked signals and followed by one preview refresh.

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
All launches of the Qt-based OpenRGB executable use the offscreen platform, including inventory and native-mode CLI clients, so a backend-only operation cannot create a desktop window.

### 6a. Wallpaper Engine for KDE

- `modules/wallpaper_engine/v1_2/library.py` — bounded read-only parsing of local Workshop `project.json` metadata and an explicitly selected personal-video directory.
- `modules/wallpaper_engine/v1_2/plasma.py` — read-only Plasma state parsing plus validated commands for Plasma's scripting interface, DisplayMode and CaptSilver's D-Bus object hosted by `org.kde.plasmashell`.
- `modules/wallpaper_engine/v1_2/installer.py` — selects only an exact stable official RPM for the local Fedora major/architecture, requires GitHub's SHA256 digest, downloads unprivileged into OHC's private cache and emits a fixed Polkit/DNF command only for that verified path.
- `modules/wallpaper_engine/v1_2/onboarding.py` — persistent setup checklist, first-visit dialog and asynchronous two-confirmation installer orchestration; it never handles administrator credentials.
- `modules/wallpaper_engine/v1_2/page.py` — native OHC gallery with fixed card geometry across apply refreshes, filters, per-screen target, playback controls, three scaling modes and launcher for Plasma's original wallpaper KCM.

OHC never copies, patches or embeds the upstream QML plugin and never writes Steam Workshop files. Applying a wallpaper, scaling mode or one of the two documented setting profiles is an explicit user action routed to Plasma. Playback addresses `/WallpaperEngine` on Plasma's existing session-bus name because that is the object CaptSilver registers even when its optional standalone service alias fails. The personal-video directory rejects the Steam library itself, preventing a recursive scan of Workshop media. The stock CaptSilver v1.4 profile is the default and the optional performance profile changes only documented configuration keys; it installs no helper, cache builder or watcher.

### 7. Release, diagnostics and security

- `collect-diagnostics.sh` — diagnostics collection with privacy handling.
- `scripts/check_release.sh` — compile/tests/security/version gate.
- `scripts/check_module_registry.py` — current-version-folder and 16-GB-context budget gate.
- `scripts/security_scan_release.py` — static release privacy/security scan.
- `scripts/build_release.py` / `.sh` — reproducible package generation.
- `scripts/backup_release.py` — atomic sibling-directory archive of the newest two complete version builds; policy lives in `RELEASE_BACKUP_POLICY.md`.
- `scripts/create_release.sh`, `scripts/publish_github.sh` — GitHub publication entry points.
- `.cursor/hooks.json` — session context and confirmation for destructive shell/Git commands.

## Persistence

User configuration is persisted by the application; project design decisions are persisted in repository documentation. Levita layer-2 edits use the versioned `thermalright/layer2_overrides_v1` settings schema. Agents must treat repository files, tests and Git history as higher-confidence project memory than conversational recollection.

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
