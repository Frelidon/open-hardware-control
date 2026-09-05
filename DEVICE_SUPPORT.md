# Open Hardware Control — Agent Device-Support Summary

`SUPPORTED_DEVICES.md` is the authoritative human-facing compatibility document. This file is a concise agent index; update both when support changes.

## Directly tested / primary reference

- NZXT Kraken 2023 (`1e71:300e`) through the validated NZXT/liquidctl path: liquid temperature, pump, radiator fan and LCD on the tested reference configuration.
- NZXT 2023 RGB Controller (`1e71:2012`): three RGB channels through the validated NZXT path.

Do not promote other detected Kraken capability entries to “tested” without real hardware evidence.

## Thermalright Levita Vision 360 ARGB Black

- Exact product identity: `Thermalright Levita Vision 360 ARGB Black`.
- Display: USB `87ad:70db`; OHC's 1600×720 editor and safe local test mode are verified. TRCC Linux 9.9.11 completed a visually confirmed hardware color cycle, and its authoritative handshake reported model ID 64/sub-byte 3 at 1600×720. OHC design/video/overlay longevity still requires an in-app real-hardware test.
- Cooling: pump and radiator fans connect to motherboard 4-pin PWM headers. Driver labels may suggest `Pump Fan` and `CPU Fan`, but both mappings require independent physical 70-percent/10-second confirmation.
- Read-only evidence on the reference system found pump and CPU-fan RPM through NCT6687. PWM response still requires user confirmation in OHC.
- CoolerControl ownership blocks concurrent writes. Owned headers are restored to firmware/BIOS control on exit.
- After explicit Polkit authorization, repeated curve writes reuse one narrowly validated helper child bound to the OHC process. This avoids background reauthorization after several minutes without weakening the required calibration or fixed-path helper validation.
- An optional user-installed exact-account Polkit rule can retain that authorization across reboots. OHC exposes separate grant/remove controls, stores no password and continues to require physical PWM-channel confirmation.
- Since 3.4.29.8 the helper mirrors grant state into a root-owned readable marker because Fedora's Polkit rule directory is intentionally not traversable by the desktop user. The marker is status only; Polkit remains authoritative.
- Since 3.4.29.9 existing local Levita media follows TRCC Linux's exact Gallery/Tech/HUD/Light/Nature/Aesthetic catalog when its filename or layout-directory name begins with a validated in-range original theme ID. Unknown names remain custom; OHC performs no catalog download.
- Since 3.4.29.10 OHC can load a complete local TRCC theme as the live hardware-data layer and then replace only its background with a local video. The backend's verified `load-theme` → `play-video` contract preserves the adopted `config1.dc` layout; this code path still needs the recorded long-running physical display confirmation.
- Since 3.4.29.10 the generated right-hand mask uses the same subtle 18-pixel rounded ends as the editor preview. A theme's own `01.png` is alpha-composited with that bar so its artwork is not discarded. Local list-hover thumbnails and short video frame loops are UI-only.
- Since 3.4.29.11 only the mask corners facing into the display are rounded; the physical outer/right edge stays flush. The temporary window/process diagnostics do not change device access or ownership and never enumerate unrelated Wayland windows.
- Since 3.4.29.11 OHC automatically offers complete layouts installed by TRCC Linux in its verified `theme1600720l` directory. Their existing `config1.dc` is adopted directly for live positions, colors and sensor values, or used as the upper layer above a different video. Other TRCC geometries are not treated as Levita layouts.
- Since 3.4.29.12 the card library also filters broad parent-directory imports: a live `config1.dc` theme requires a verified landscape path or an exact 1600×720 PNG preview. The three bundled OHC backgrounds are project-owned local images, not TRCC manufacturer media.
- Since 3.4.29.12 a user may explicitly enable one saved two-layer Levita startup design. Test mode still prevents the write; otherwise OHC waits for desktop readiness and retries a not-yet-ready display only once through the existing serial TRCC queue.
- Since 3.4.29.13 custom-folder storage and catalog inclusion are separate and disabling inclusion never touches disk files. Complete `config1.dc` themes default to data layer 2; an explicit persisted move can place one in layer 1. Levita brightness/orientation use bounded TRCC commands, and design swaps gracefully stop the renderer, wait for USB release and retry one confirmed timeout at most once.
- Since 3.4.29.14 video-card stills are decoded by at most two background workers and persisted in a source-versioned cache. Opening large catalogs therefore does not block the Qt interface, while modified files automatically receive new thumbnails.
- Since 3.4.29.15 selecting a layer-2 layout preserves image and video backgrounds and always refreshes the combined main preview. Incomplete themes fall back to `Theme.png`; the centered viewport follows the exact 1600×720 display aspect ratio.
- Since 3.4.29.16 repeated complete filenames are represented by one deterministic catalog card. Normal/short paths win over nested backup copies, and the operation never deletes or modifies user media.
- Since 3.4.29.18 each logical layer-2 live-data block is independently draggable and context-editable, with whole-layer offsets. OHC stores only its own override and generated cache `trcc.json`; imported `config1.dc` and artwork remain unchanged.
- Since 3.4.29.19 the OHC preflight accepts validated 1600×720 native `trcc.json` cache themes as well as legacy `config1.dc`, matching TRCC Linux's actual theme-loader contract. Invalid JSON and wrong geometry remain blocked before device access.
- Since 3.4.29.20 the editor uses TRCC's centre-based text coordinates and updates video backgrounds without recreating draggable layer-2 items. The dashboard coolant card is available only when a connected Kraken supplies a real liquid-temperature value.
- Since 3.4.29.21 an Ebene-1 card click paints the selected image or cached first video frame immediately. The camera bar keeps a straight inner edge; only the two outer-right 1600×720 display corners are rounded.
- Since 3.4.29.24 malformed imported layout records are isolated, symlinked theme inputs are rejected, split preview mode safely defaults to Off and renderer activity is confirmed by the process start event. This does not change the USB protocol or hardware support claim.
- Since 3.4.29.33 native 1600×720 `trcc.json` folders can be imported, assigned explicitly to either layer and favourited without changing originals. Two project-owned space layouts are bundled; their raster artwork was generated with OpenAI's built-in image generator from the owner's blue/purple sci-fi style references, while the reference images themselves are not copied into the package.
- Since 3.4.29.34 OHC accepts its own validated editable-theme cache links again while imported folders remain symlink-restricted. A controlled program exit issues one bounded daemon-only `display stop-video` request and returns the Levita to its active TRCC theme.
- Since 3.4.29.35 every explicit design apply, colour test and brightness/orientation action first replaces a possibly stale daemon device and requires a fresh handshake. This covers the confirmed state where TRCC retained a handshake as connected after unplugging while the underlying BulkLcd transport was already closed.
- DC/PWM selection is available only for a channel whose Linux driver exposes `pwmN_mode`. Changing it invalidates calibration and activation and requires the physical test again.
- No coolant sensor is exposed through this path; never synthesize one from CPU/GPU temperatures or RPM.

## Corsair

Corsair devices are discovered through the locally installed OpenLinkHub service/API. OHC intentionally does not maintain a guessed direct Corsair USB support table. Available actions depend on what the installed OpenLinkHub version reports and supports.

## OpenRGB devices

RGB coverage follows the user's separately installed OpenRGB backend. OHC uses its private local engine and bounded SDK helper. Detection does not equal validated hardware compatibility; unfamiliar controllers must be tested conservatively, especially variable ARGB LED counts/zones.

The private server and every short-lived OpenRGB CLI client are launched through Qt's offscreen platform. This is a window-suppression property only and does not change device compatibility or ownership.

The same offscreen boundary also applies to synchronous `--version` and direct inventory probes used while building or diagnosing the UI; these helpers cannot map an otherwise empty desktop window.

If the private OpenRGB process crashes during backend discovery, OHC quarantines automatic restart for the rest of the session. A deliberate manual re-detection is required before another backend launch, preventing repeated driver coredumps.

For Frelidon's versioned personal PC layout only, the Jungle Leopard GPU support is confirmed as one 24-LED component on Airgoo Channel B6. OpenRGB exposes it as a hub zone rather than a separate controller, so it must not be grouped with either ENE-DRAM module. This fixed reference mapping is not a general claim about other Airgoo installations.

A stable removal of one or two devices from an expected inventory of at least four may update the saved expected count after 2.5 seconds. Large inventory drops remain protected by the stricter cold-start retry logic and must not be accepted as a permanent hardware change automatically.

## Mainboard/chassis fans

The current backend targets Linux hwmon fan control with a focus on NCT6687/NCT6687D. Electrical channel mapping must be calibrated and physically confirmed. Board name alone is diagnostic metadata, not a safe mapping source. Individual/global presets modify only the stored bounded curves and preserve activation/calibration state; electrical DC/PWM switching is permitted only through a driver-exposed fixed channel node and always resets confirmation state.

## Explicitly outside current support claims

- GPU fan control through the mainboard fan subsystem.
- Firmware flashing/updating/version switching.
- General voltage/clock tuning.
- Unverified direct Corsair USB writes.
- Open Radeon Control Center integration into this repository.

When adding support, record: device identity, read-only detection evidence, write path, safety/ownership model, real hardware test status, and regression tests.
