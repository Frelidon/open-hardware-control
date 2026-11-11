# Open Hardware Control — Agent Device-Support Summary

11.11.26 (.176): Existing chassis-only identification can request 0% for up
to 120 seconds only when the existing driver watchdog can be armed with a short
10-second lease. Sample ticks refresh the lease every three seconds; Next,
Cancel, channel change and shutdown restore all target/contrast snapshots.
CPU_FAN and PUMP_FAN remain excluded from stop tests. Ordinary 70/80% speed
calibration remains ten seconds. "Not connected" is an explicit reversible
choice, never a conclusion from zero RPM. No new electrical/protocol support,
LED count, driver installation or live hardware stop test is claimed.

11.11.26 (.175): The read-only UI catalog lists 41 model/backend entries in
eight categories. Thirty existing GPU profile models are explicitly marked as
backend-dependent profiles, not newly hardware-tested devices. The confirmed
SAPPHIRE NITRO+ RX 9070 XT remains separate. SABRE RGB PRO and HS80 MAX are
individual locally detected OpenLinkHub entries; only reported capabilities
apply. Manufacturer/product links do not establish compatibility. See
[reviewed catalog links](SUPPORTED_DEVICE_LINKS.md). Hardware owners unchanged.

10 November 2026 live Ubuntu RGB diagnosis: six OpenRGB devices detected and
Sapphire RX 9070 XT confirmed in External Control. Independent native-plugin
workers raise measured Airgoo full-frame USB writes from 3.83 to 58.52 Hz.
MSI 761-byte feature reports take approximately 93 ms each on this host; the
original four-zone loop limits GPU-header frames to ~2.8 Hz. No optical 60-Hz
GPU claim is justified. LED counts and Thermalright protocols are unchanged;
the MSI dirty-zone optimization is a separate source-controlled backend patch.
After installing that patch, the single changed MSI zone measures about
10.64 USB frames/s. The owner confirms smooth case/GPU motion and correct GPU
colours after correcting native colour packing. The unchanged Levita design
plays again after normal startup/recovery, confirmed by IPC and the owner.
No display protocol, layout, LED count or LCD FPS setting changed.

25 September post-.124: the supplied session logs show short exact 0 MHz GPU
clock samples followed by normal recovery. For AMD GPUs this is a valid
power-gated idle state, so OHC no longer reports 0 MHz as implausible; negative
or values above 5000 MHz remain rejected. This changes read-only diagnostics,
not GPU control. Repeated identical process-start lines and per-channel fan
curve lines are coalesced without suppressing state changes or emergencies.
The optional GPU fan auto-save remains off by default and executes only after
the existing LACT response test and rollback check pass.

22 September `.120`: RX 9000/7000 and RTX 50/40 names and the two neutral GPU
illustrations are UI catalog data, not compatibility or writable-limit claims.
LACT remains the sole GPU writer and all editable bounds come from the current
device. GPU subprofiles are exact-device-bound and only locally verified data
may use startup activation. Custom transparent artwork is copied privately and
does not change hardware support. Gamescope changes presentation/scaling only.
No physical GPU write was performed for this development version.

20 September `.117`: The owner's `.116` test switched both GPU and Airgoo
support to zone packets, followed by SDK timeouts and a managed OpenRGB
crash. Restarting OHC restored six devices and normal device-frame output.
Per-frame zone trials and their controls are removed; old settings are inert.
The confirmed 30/12 physical LED counts remain. Optical stepping needs an
isolated comparison with OpenRGB's own visible effect, not a guessed count.

20 September `.116`: The installed `.115` log shows SDK timeouts and a
managed OpenRGB engine exit after MSI GPU zone packets became active. The
prior whole-device frame is again the default for GPU and Airgoo support;
the `.115` setting is ignored. Separate explicit trials are possible and
automatically disable on SDK failure or engine exit. The driver-level cause
and visible optical result of either trial remain unverified.

20 September `.115`: Both GPU and support report roughly 24.5–25 OHC-to-SDK
frames per second in the owner's `.114` test, but the GPU remains optically
stepped. The explicitly routed MSI GPU controller can test documented
zone-update packets and revert to whole-device packets. This changes the
OpenRGB SDK call, not the hardware driver or ownership. Case animation is
read-only and schematic where no physical path is saved. Physical improvement
remains unverified; SDK success is not LED readback.

20 September `.114`: The owner's phone video confirms a visible GPU/support
optical mismatch despite the `.113` software preview and 50%/50% GPU edge
settings; the owner also tested slower motion. OHC now permits live draft
adjustment on already running effects, caps the GPU white peak separately
and draws declared case LED paths. This adds no protocol or controller support.
Actual GPU and support SDK rates and an optical test are still pending; no
physical improvement is claimed from source inspection alone.

20 September `.113`: GPU and support use one fixed open-strip travel cycle
independent of their separately configured edge widths. The GPU default is
40%/38% lead/tail; saved values remain authoritative. This changes animation
shape only, not LED routing or device support. Optical verification remains.

20 September `.112`: GPU/support LED motion can be tuned and previewed at
each configured physical LED count. The displayed transfer rate measures
successful OpenRGB SDK frames; OHC cannot measure the visible optical rate.
Delayed batches slow the shared motion clock rather than skipping LEDs. No
new controller, protocol or LED count is inferred from this software change.

20 September `.111`: A bounded 15-second 8K vkmark check on the owner's
RX 9070 XT reported vendor/device `1002:7550`; all 30 half-second sysfs
samples showed 100% GPU busy. The previous `.110` invocation used
`DRI_PRIME=1`, which selected the Ryzen iGPU on this system. No GPU profile
was written during verification. A read-only LACT response showed a 0 MHz
offset, no custom core maximum, and a 330 W power cap equal to its reported
default. The `.110` OHC fan preview did set PWM 255, but 0–50 RPM before
rollback did not prove spin-up; the longer bounded verification in `.111`
awaits a user-initiated physical test. No general compatibility claim is
inferred from this one system.
The owner's Sapphire NITRO+ model lists 330 W typical board power and a
12V-2x6 connector; this is distinct from AMD's 304 W reference design.
OHC now locks the normal editor to LACT's device-reported 330 W default and
requires explicit unlock above it. OHC cannot sense connector contact heat.

20 September `.110`: The owner's `.109` LACT snapshot shows a static 100%
fan setting and 3852 RPM after it was applied directly in LACT. OHC's
previous button only prepared the fan tab; it now starts a bounded LACT
trial, and a fixed-speed mode is available. Releasing a fan reads the live
LACT config, so an external edit is not stranded behind stale OHC state.
The first 15-second `.109` vkmark run reached only 12% load. The new 8K
Phong scene requires measured sustained high load; the OHC fan write and
8K run still need the owner's hardware validation.

19 September `.109`: The longer GPU load test now accepts the current LACT
configuration without an OHC tuning snapshot. This baseline run makes no
GPU configuration write and cannot claim an OHC rollback. A previously
saved, matching OHC snapshot still enables the existing fault rollback.
The owner's `.108` log confirms vkmark installation and successful short
GPU offset previews, but not yet a completed longer benchmark.

19 September `.107`: OHC can prepare a five-point LACT GPU fan curve from
reported capabilities without a prior LACT profile. This has been checked
with simulated daemon responses, not with a live fan write. The 15–120 second
GPU stress run requires an OHC-confirmed snapshot and a stronger vkmark or
glmark2 helper; Hardware Checker also prefers vkmark. A matching prior
snapshot can be restored after an observed fault.

19 September UI/diagnostic follow-up: the explicit GPU link test can use
`vkcube` when `glmark2` is missing, but only a running graphics child permits an
under-load link assessment. Neither helper changes clocks, fans or firmware.
The owner's video is evidence of the look of one 30-LED externally routed
Sapphire strip; the narrower highlight and brighter blue base are software
rendering choices, not proof of physical frame output or a generic LED count.


3.4.29.96 adds a generic read-only Hardware Checker for Linux-reported CPU/SMT/virtualization,
PCIe GPU, NVMe and DMI memory state. Current/max link values and a bounded
optional GPU load observation are diagnostic evidence, not new device support.
No storage write benchmark, tuning, fan action, firmware or BIOS change occurs.
The local reference probe observed Ryzen 7 9800X3D SMT active, a primary Radeon
PCIe 5.0 ×16 link and one NVMe ×2 link against its reported ×4 maximum; do not
generalize these results to another board, slot or component.

3.4.29.89 / RGB Studio 1.12 adds softer open-strip GPU motion and optional
shared GPU/support effect time across explicitly assigned Direct zones with
valid declared counts and both devices selected. No new hardware compatibility,
firmware update, physical readback or guaranteed optical frame rate is claimed.

Version 3.4.29.87, RGB Studio 1.10: the owner supersedes the older support
reference with 12 addressable LEDs at Airgoo B6. Confirmed personal wiring is
front A1 2×8 / SYS_FAN4, bottom reverse intake B7 3×8 / SYS_FAN6, rear normal
exhaust B8 1×8 / SYS_FAN1, Thermalright radiator A8 3×10, and support B6 1×12.
SYS_FAN labels are physical notes, never inferred internal pwmN identities.
One-time personal settings migration and reusable custom fan metadata add no
driver compatibility or electrical auto-detection. Older 24-LED references
below describe history and are superseded only for this owner's configuration.

3.4.29.87 adds declared LED strip/ring paths and eight physical travel
projections; no auto-detected wiring or optical FPS claim. Complete profile
packages preserve mappings/models/positions/media but require local hardware
write authority and PWM recalibration. No new driver or firmware support.

3.4.29.85 adds direct case-block controller/reported-header selection with
stable settings-only binding and existing bounded count/pixel testing. No
new device compatibility or optical validation is claimed; PWM stays separate.

Version 3.4.29.83 reference update: the owner visually verified 30 addressable LEDs on their personal Sapphire RX 9070 XT NITRO+ at MSI JARGB 1 (1 left, 30 right, 29 one step back). Do not generalize this to other GPU models or use it as electrical auto-detection. Generic Direct-header tests, protected manual counts, semantic ARGB diagnostics and count-aware zone effects are implemented; new animation fluidity remains optically unverified. The central Case workspace shares physical RGB/LED/PWM assignments and permits separate positions only; PWM assignment never calibrates or enables control.

`SUPPORTED_DEVICES.md` is the authoritative human-facing compatibility document. This file is a concise agent index; update both when support changes.

## Directly tested / primary reference

- NZXT Kraken 2023 (`1e71:300e`) through the validated NZXT/liquidctl path: liquid temperature, pump, radiator fan and LCD on the tested reference configuration.
- NZXT 2023 RGB Controller (`1e71:2012`): three RGB channels through the validated NZXT path.

Do not promote other detected Kraken capability entries to “tested” without real hardware evidence.

## Thermalright Levita Vision 360 ARGB Black

- Exact product identity: `Thermalright Levita Vision 360 ARGB Black`.
- Display: USB `87ad:70db`; OHC's 1600×720 editor and safe local test mode are verified. TRCC Linux 9.9.11 completed the model/sub-byte handshake and colour cycle. TRCC Linux 9.10.4 additionally ran the full OHC theme through its daemon-owned VideoLoop with continuing 1600×720 writes and stable RSS/thread/file-descriptor samples on the reference display.
- Cooling: pump and radiator fans connect to motherboard 4-pin PWM headers. Driver labels may suggest `Pump Fan` and `CPU Fan`, but both mappings require independent physical 70-percent/10-second confirmation.
- Read-only evidence on the reference system found pump and CPU-fan RPM through NCT6687. PWM response still requires user confirmation in OHC.
- CoolerControl ownership blocks concurrent writes. Owned headers are restored to firmware/BIOS control on exit.
- Since 3.4.29.66 Settings exposes the implemented TRCC Linux and OHC Linux-hwmon backends through a persisted fail-closed selector. Native Levita and CoolerControl control adapters are roadmap entries only and remain disabled; the selector does not broaden hardware support.
- Since 3.4.29.67 Cooling includes a read-only Linux-hwmon recorder for plausible CPU, GPU/hotspot/VRAM, RAM, SSD/NVMe, motherboard, VRM, PCH and other temperature sources. It stores at most 24 hours/28,800 samples in volatile memory, takes no control ownership and never invents a Levita coolant value.
- Since 3.4.29.131 OHC accepts TRCC 9.10.4's exact successful daemon-playback hand-off instead of retrying the deliberately completed CLI helper. Memory supervision remains active as an emergency bound. The detached shutdown helper also restores its installed module root before importing OHC code.
- Since 3.4.29.68 the main Cooling entry expands into fixed Control/Profile and Temperature Recording children; this only exposes the existing views and changes no ownership or hardware support.
- Since 3.4.29.69 LCD mirrors its sidebar children through synchronized in-page tabs, and Display Effects mirrors the active validated library medium. This is UI state only and adds no hardware support or writer.
- Thermalright publishes only 3000 rpm ±10% pump and 2000 rpm ±10% TL-M12Q maximum speeds, not minimum PWM duty. OHC therefore labels 50% pump and 25% radiator as conservative internal floors and clamps every UI/profile/curve/final-write boundary; this is not a claimed manufacturer minimum.
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
- Since 3.4.29.34 OHC accepts its own validated editable-theme cache links again while imported folders remain symlink-restricted.
- Since 3.4.29.53 a controlled program exit stops OHC display clients and issues one bounded daemon-only `device disconnect`, allowing the built-in Thermalright firmware screen to return after TRCC's documented two-to-three-second no-frame timeout. A pipe-bound helper armed only after a confirmed real write repeats that fixed release after unexpected OHC parent loss; preview-only use never arms it.
- Since 3.4.29.54 Display Effects prepares a bounded procedural smoke video and delegates it to the existing Levita studio while preserving layer 2. It adds no second TRCC/USB owner. OpenLinkHub and its bundled Web UI may be updated only after confirmation through existing package repositories or a published-SHA-256 user-space archive with backup and rollback.
- Since 3.4.29.55 device initialisation and Levita card construction no longer delay first paint. CoolerControl inspection is a coalesced subprocess and unknown state remains fail-closed. Graphical Layer-2 effect cards and faster cache handling do not expand hardware support or bypass the ten-second Levita cooldown.
- Since 3.4.29.35 every explicit design apply, colour test and brightness/orientation action first replaces a possibly stale daemon device and requires a fresh handshake. This covers the confirmed state where TRCC retained a handshake as connected after unplugging while the underlying BulkLcd transport was already closed.
- DC/PWM selection is available only for a channel whose Linux driver exposes `pwmN_mode`. Changing it invalidates calibration and activation and requires the physical test again.
- No coolant sensor is exposed through this path; never synthesize one from CPU/GPU temperatures or RPM.
- Since 3.4.29.80 unavailable coolant status and curve-source choices are hidden. The full-width safety panel still documents OHC's conservative internal pump/radiator floors.

## Corsair

Corsair devices are discovered through the locally installed OpenLinkHub service/API. OHC intentionally does not maintain a guessed direct Corsair USB support table. Available actions depend on what the installed OpenLinkHub version reports and supports.

## OpenRGB devices

- 3.4.29.86 isolates LED preview from background discovery/effect auto-apply,
  blocks overlapping/offline tests and offers explicit owned-engine recovery.
  Offline wiring choices retain real device ownership/quarantine restrictions.
  Personal fan model declarations use owner-observed eight addressable LEDs
  for ASIN B0CN39T7QN; this is not manufacturer-wide verified LED detection.
  No native driver crash fix or real hardware compatibility is claimed.

Version 3.4.29.82 uses explicit controller-and-zone GPU routing with independent strip coordinates, a bounded single-header editor and an explicit pixel-index visual test. Current saved physical GPU wiring/counts override design snapshots. The owner's personal Sapphire RX 9070 XT/MSI JARGB 1 wiring is confirmed by the owner, not electrically detected; its 80/90 counts remain unverified user test values. Other layouts receive no inferred header. Optical output remains pending; native defaults and existing transport/ownership gates are preserved.

RGB coverage follows the user's separately installed OpenRGB backend. OHC uses its private local engine and bounded SDK helper. Detection does not equal validated hardware compatibility; unfamiliar controllers must be tested conservatively, especially variable ARGB LED counts/zones.

The private server and every short-lived OpenRGB CLI client are launched through Qt's offscreen platform. This is a window-suppression property only and does not change device compatibility or ownership.

The same offscreen boundary also applies to synchronous `--version` and direct inventory probes used while building or diagnosing the UI; these helpers cannot map an otherwise empty desktop window.

If the private OpenRGB process crashes during backend discovery, OHC quarantines automatic restart for the rest of the session. A deliberate manual re-detection is required before another backend launch, preventing repeated driver coredumps.

For Frelidon's versioned personal PC layout only, the Jungle Leopard GPU support is confirmed as one 24-LED component on Airgoo Channel B6. OpenRGB exposes it as a hub zone rather than a separate controller, so it must not be grouped with either ENE-DRAM module. This fixed reference mapping is not a general claim about other Airgoo installations.

Since 3.4.29.80 a component double-click selects its already assigned RGB device and opens the existing zone editor only for Direct devices. The supplied Sapphire RX 9070 XT log reports one logical LED, `GPU Zone` and Hardware Mode rather than Direct Mode, so OHC exposes its reported native modes but does not claim individually addressable GPU segments.

Version 3.4.29.82 restores suitable reported native animations as the automatic GPU design path, removing implicit External Control selection. GPU double-click now opens explicit control-path setup. Manual LED counts use the physically connected external Direct ARGB controller's bounded zone editor; the internal Sapphire zone remains one logical LED. Stable-ID routes persist with RGB profiles, and absent/unselected sources revert to native effects. The UI explains that effects address the external controller including its other zones. This is software regression coverage, not optical hardware validation; no physical GPU strip length or electrical header is inferred.

A stable removal of one or two devices from an expected inventory of at least four may update the saved expected count after 2.5 seconds. Large inventory drops remain protected by the stricter cold-start retry logic and must not be accepted as a permanent hardware change automatically.

## Mainboard/chassis fans

The current backend targets Linux hwmon fan control with a focus on NCT6687/NCT6687D. Electrical channel mapping must be calibrated and physically confirmed. Board name alone is diagnostic metadata, not a safe mapping source. Quiet/Balanced presets update stored bounded curves; Performance is a constant 100-percent curve and is reevaluated immediately while OHC control is active. Presets preserve activation/calibration state. Every chassis-fan card exposes a confirmed, restoring 0-percent/10-second identification test. Version 3.4.29.80 separates the friendly kernel System Fan label from `PWM N`; its full assignment reset stops OHC control, restores firmware ownership and retains curves, while the wizard can continue with the next fan. Electrical DC/PWM switching is permitted only through a driver-exposed fixed `pwmN_mode` node and always resets confirmation state; without that node the mode remains BIOS-owned and OHC writes only the documented `pwmN` duty/DC value.

## Explicitly outside current support claims

- GPU fan control through the mainboard fan subsystem.
- Firmware flashing/updating/version switching.
- General voltage/clock tuning.
- Unverified direct Corsair USB writes.
- Open Radeon Control Center integration into this repository.

When adding support, record: device identity, read-only detection evidence, write path, safety/ownership model, real hardware test status, and regression tests.


3.4.29.172: Described support cards expose the existing model/backend boundaries
without adding drivers. The local OpenLinkHub user backend is updated to .9.4
with .9.2 rollback data. Mouse detail metadata is verified read-only; physical
startup-DPI/profile changes remain an explicit user action.
