# Open Hardware Control — Architecture

## 11.11.26 – Model-level catalog and stable sidebar clicks (.175)

`hardware_checker/v1_0/device_catalog.py` is immutable metadata using existing
GPU profile IDs, reviewed HTTPS destinations and explicit support boundaries.
`supported_devices.py` owns category/vendor/search filtering and responsive
original cards. Links have no runtime network probes; only explicit clicks
open the browser. Missing/invalid product destinations produce no widget.
`localization/v1_0/device_catalog_messages.py` adds atomic four-language labels.

`navigation_settings/v1_0/sidebar.py:NavigationTree` buffers current-item page
requests during normal pointer selection until native mouseReleaseEvent has
finished. This prevents collapsing section rows during mouse press and Qt then
selecting a shifted row on mouse move. Keyboard/programmatic selection emits
immediately; customization retains the existing Qt drag/drop mode. Main-window
navigation routes and hardware owners are unchanged.

## 11.11.26 – Shared RGB loop boundaries (.171)

`rgb_effects.py` remains the common pure renderer for galleries, native plans,
SDK worker frames and physical/GPU zone rendering. Pulse samples wrapped
Gaussian distance; convergence overlaps its final burst with its exact initial
edge state, using zero-slope smoothstep weights. There is no frame-history
buffer, global time reset or hardware transport change. Stable preset indices
remain separate from reclassified category metadata. Full-catalog regressions
exercise each shared rendering path and whole overlap intervals.

## 11.11.26 – Content transitions and native recovery (.170)

`ui_performance/v1_1/page_transition.py` reveals the real current content page
through a fading palette-background veil and optional bounded position offset.
The controller owns one active animation, cancels stale/hidden/deleted targets,
and restores geometry on interruption, resize and shutdown. The menu is not a
transition target. There are no page snapshots or graphics-effect frame buffers.

`rgb_studio/v1_15/native_stream.py` owns preferred native START/frame recovery
and the confirmed STOP barrier before the SDK backup. Three consecutive failures
and spaced retries prevent a temporary socket delay from replacing the fast
writer. A failed STOP retains native ownership and blocks SDK. Rendering errors
fail design confirmation without interpreting invalid input as transport failure.
The main window delegates this state and keeps existing authority/selection gates.

`application_activation/v1_0/autostart.py` is an installer-only helper that
atomically retargets existing recognized desktop autostart entries after the
user launcher has been updated. It keeps enabled/disabled flags and arguments,
ignores missing entries, custom wrappers and symlinks, and never launches OHC.

## 10.11.26 – RGB native transport and preserved LCD boundary (.169)

`rgb_studio/v1_15/native_plugin.py` owns the bounded Unix-socket client and
generation-aware design confirmation. `src/native/openrgb/OHCNativePlugin.cpp`
validates complete controller frames and queues one latest frame per device.
`LatestFrameWorker.h` gives each device an independent persistent worker and
absolute deadline; slow MSI transfers cannot stall Airgoo. `ColorCodec.h`
explicitly packs validated RGB channels, avoiding upstream macro precedence.
The ordinary parallel loopback SDK helper remains the fallback. Direct devices
receive OHC frames, while external Sapphire mode only selects the physical
ARGB input. User topology and sole OpenRGB hardware ownership remain intact.
`tools/openrgb/msi-761-dirty-zones.patch` is separately built into OpenRGB and
does not alter report formats. Packages preserve the platform-neutral app and
ship complete source/rebuild instructions, not an ABI-independent driver binary.
The Levita/TRCC protocol, layout and frame rate remain unchanged and separate.

## 06.10.26 – LED drafts and case-space projection (.156)

`rgb_studio/v1_15/led_topology_editor.py` owns a private optional-draft group
which reapplies field applicability after Qt polish/reparenting. Only genuine
input signals activate a fresh commit; persistence/transport guards remain
separate. `pc_case_profiles/v1_5/spatial_layout.py` compares persisted flow state
before refreshing widgets, preserving ordinary unfinished drafts while updating
loaded profile directions. Missing paths are explicitly explained in all languages.
`render_plan.py` and the legacy GPU fallback build projection rectangles for
explicit nonlocal header directions, independent of the global-local setting.
`led_topology.py` and `gpu_strip_sampling.py` correct wave travel and local effect
reversal without reordering physical path points. Headers without paths remain local.
`case_animation.py` projects the same bounded confirmed colour frames for the
view. `fan_preview.py` is pure presentation of those colours in light-ring
segments; `diagram.py` owns the visibility-bound timer. Neither creates physical
wiring, sensor RPM, PWM changes or a second SDK writer.

## 06.10.26 – Independent Ubuntu startup and explicit LCD ownership (.155)

`cooling_state/v1_0/startup_policy.py` is a pure decision shared by
`apply_startup_profile()` and `startup_profile_has_lcd_payload()` in the host.
Only the four known legacy NZXT assistant presets may stop blocking an
explicitly selected PC profile on Ubuntu when the actual Levita USB device is
present, no NZXT is ready and cooling selection is auto or the exact Levita.
The pending preset is not deleted or executed as motherboard PWM intent.
The selected profile's own cooling payload still reaches the existing
mapping/calibration/ownership guards unchanged. Fedora, real NZXT, unknown
pending values and absent/unselected Levita retain the prior barrier.

`levita_daemon_health/v1_1/model.py` separates TRCC's explicit USB-interface
ownership error from daemon IPC failure and from a trailing udev hint.
The Ubuntu LCD orchestrator stops only its own apply/startup/ticker retries
when that conflict is reported; it does not restart or signal the other owner,
change FPS, erase the saved design or add a USB path. An explicit Apply after
owner release reuses the existing serialized queue and immutable design request.
Fedora's existing recovery classifier and orchestration remain unchanged.

Fedora and Ubuntu are separate equal test lanes under the mandatory AI rules.
Distribution-specific guards and targeted regressions preserve both paths;
fixture success is not a live hardware claim for either distribution.

## 06.10.26 – Complete inventory and external GPU block routes (.154)

OpenRGB command selection distinguishes the trusted Ubuntu 1.0 backend from
the older CLI. Names-only inventory is rejected before the Qt controller
updates any device identity or persisted workspace. The GPU editor reuses
the existing block-route editor for externally connected lighting: actual
Direct controller/header choices do not depend on a native GPU device.
GPU strip effects use that explicit block route, retaining the existing
whole-controller shape validation, conflict checks and independent USB owners.
Personal routes and LED counts remain private profile data, not release defaults.

`trcc_backend/v1_0/runtime.py` constructs the Ubuntu-only child entry and
`launcher.py` adapts the audited TRCC metadata/daemon factories in that child,
without modifying installed upstream files or the global PATH. The dedicated
root-owned DMI helper accepts no arguments, runs one fixed memory read with a
minimal environment and filters identifiers. Its separate Polkit action is
inactive outside an active desktop session; no generic Python or dmidecode
authorization is introduced. Other automatic metadata requests stay unprivileged.

## 06.10.26 – Ubuntu read isolation and preserved module contracts (.153)

`gpu_control/v1_0/read_worker.py` owns bounded read-only LACT transactions;
`read_probe.py` owns one cancellable Qt child/deadline and `read_ui.py` validates
and applies results only to the still-selected device. A missing clocks table
is optional. This Ubuntu lane does not change Fedora's prior read contract.
`backend_updates/v1_0` performs official metadata/package checks outside Qt and
resolves only trusted fixed Ubuntu backend paths. OpenRGB explicitly selects
SDK 6 there, maps UUID wire IDs and verifies acknowledgements; default SDK 5
and whole-device effect frames remain available.

The verified `.148` feature baseline is restored additively in `setup_features`,
`control_authority`, `design_automation` and `platform_support`. Visibility and
hardware enablement have separate persisted models. Snapshot presentation,
process lifetime and actions are split into `views.py`, `process_runtime.py`
and `snapshot_actions.py`; its persistent activity helper is bounded. Hardware
overview cards live in `hardware_checker/v1_0/cards.py`, separate from probe
and current Hardware Fix controls. GPU artwork is presentation-only.

OpenLinkHub still owns Corsair USB. Its current mutations require a documented
success acknowledgement. Nexus imports preserve the upstream profile schema,
reject linked target directories and use unique temporary/backup files.
Its direct loopback opener rejects redirects and ignores environment proxies.
Delayed Hardware Fix/GPU callbacks are QObject-bound; Hardware Checker signals
and deadlines carry current-process identity. Fan labels wrap, and compact GPU
views retain a vertical-scroll fallback rather than clipping the curve.

## 01.10.26 Snapshot Manager privilege and activity boundary (.127)

`snapshot_manager/v1_0/model.py` owns the pure bounded policy and hysteresis.
`probe.py` reads distribution, mount, timer and Btrfs state outside the Qt
process; `activity_probe.py` samples `/proc`, DRM busy state and fixed game
signals. `fullscreen_probe.py` runs a short one-shot KDE script and unloads it
again. `page.py` owns presentation and process deadlines, never privileged
writes. `/usr/libexec/open-hardware-control-snapshot-helper` is root-owned and
reachable only through its dedicated Polkit action. Its interface accepts two
known Snapper timers, four bounded discard numbers, a bounded deadline and a
strict Snapper configuration name. Manual deadlines use a fixed transient
systemd resume unit. The helper stores root-owned state under
`/var/lib/open-hardware-control` so the UI can recover the active mode without
inventing it. Rollback remains an explained manual recovery operation rather
than an application button.

## 22.09.26 GPU profiles, artwork and scaled load windows (.120)

`gpu_profiles/v1_0/model.py` owns bounded exact-device persistence and config
digests; `catalog.py` is presentation-only and `artwork.py` owns strict private
PNG normalization. `gpu_control/v1_0/profile_ui.py` translates those records
to the existing LACT controls and never bypasses their commit transaction.
Main profiles embed one selected GPU record; unknown payloads are stored only
as drafts. `stress.py` optionally nests vkmark at its selected 4K/8K size in
Gamescope, whose output follows the monitor-sized window. The separate KWin
bridge targets only the benchmark PID for maximized, minimized or full-screen
state. The animated fan preview stops when hidden and has no hardware role.

## 20.09.26 Device-frame-only effect transport (.117)

`gpu_lighting.py` no longer exposes packet-mode controls or reads the old
trial settings. Render plans contain no zone-update request.
`openrgb_sdk.py` ignores even a stale `zone_updates` field in a worker
request and sends packet 1050 for every prepared animation frame. Its
existing first-frame Direct setup and one-time compatibility fallback are
unchanged. The sole worker and loopback ownership model remain. `kraken_control.py`
still labels GPU/support SDK paths in the log; `case_animation.py` remains
read-only. The user's `.116` crash demonstrates that preference rollback
cannot revive a crashed OpenRGB engine.

## 20.09.26 Safe GPU/support packet defaults (.116)

`gpu_lighting.py` uses new independent GPU/support experiment keys that
default to false; the `.115` key cannot re-enable a packet route. The SDK
worker sends whole-device frames unless one identified controller was
explicitly opted into validated zone packets. The host logs the component
and returned packet path. A failed SDK frame disables that controller's
experiment before another frame; an unexpected managed-engine exit disables
active experiments before the existing manual-restart quarantine. The
read-only Case preview has no transport role.

## 20.09.26 MSI GPU zone packet comparison and animated Case (.115)

The sole loopback SDK worker still prepares the entire controller once.
`gpu_lighting.py` marks only an explicitly routed MSI GPU controller for
the selected zone path; `openrgb_sdk.py` then sends documented 1051 packets
for every nonempty validated zone instead of one 1050 whole-device packet
on subsequent frames. A saved checkbox switches that MSI controller back
to the old path. RAM and Airgoo remain device-frame writers. This is a
transport comparison, not proof that the MSI microcontroller displayed
every socket frame. `kraken_control.py` logs the path returned by the worker.

`pc_case_profiles/v1_5/case_animation.py` resolves only explicit slots and
declared LED counts to pure frames. `diagram.py` paints them from the last
dispatched frame time and pauses its timer when hidden. A missing physical
path gets a stylized component row; saved paths keep their declared points.
No case widget writes to an RGB controller.

## 20.09.26 Live GPU motion and case path preview (.114)

`gpu_motion_editor.py` puts slider values in a transient host draft. The
existing frame timer reads that draft in `render_plan.py`; its sole SDK worker
still owns all OpenRGB writes. Closing the editor clears the draft and the
next timer frame uses stored settings. `gpu_motion.py` adds a bounded GPU white
peak while `gpu_strip_sampling.py` lifts low GPU edge levels and caps the
highlight. The support's curve and phase are unchanged. `argb_controls.py`
opens a known single header directly, while a separate case route action
retains controller reassignment. `topology_labels.py` exposes only saved,
unambiguous LED paths to `diagram.py`, which draws start/end and route dots.

## 20.09.26 GPU/support LED motion editor (.112–.113)

`rgb_studio/v1_15/gpu_motion.py` validates the saved approach/fade/tempo and
caps visual-clock progression after delayed SDK dispatches. `gpu_motion_editor.py`
renders the configured GPU/support LED counts without writing hardware. The
existing GPU dialog commits settings only on save. `render_plan.py` carries the
bounded tuning and one shared visual timestamp to the sole OpenRGB SDK worker;
`gpu_routing.py` applies it only to GPU/support open strips. The frame rate
shown in the editor comes from successful worker acknowledgements, not from
optical readback. In `.113`, `gpu_strip_sampling.strip_clock()` fixes a shared
open-strip travel cycle independent of the two edge envelopes. The 25-Hz timer, ownership
checks and serial writer remain.

## 20.09.26 GPU benchmark device and fan verification

`stress.py` derives the Vulkan device selector from LACT's PCI vendor/device
ID. Both the short tuning preview and longer read-only load test remove an
inherited ordinal `DRI_PRIME` and select that GPU explicitly. The long test
records vkmark's own device banner, plus LACT load, clocks, power,
temperature and throttling. Its scene lasts beyond the selected test window.
For a newly claimed GPU fan, `page.py` waits up to 3.8 seconds within LACT's
automatic rollback deadline and requires an observed RPM rise before
enabling permanent save. A missing RPM response is inconclusive and reverts.

`power_policy.py` treats LACT's finite `cap_default` as the ordinary OHC
upper bound and its `cap_max` as the confirmed unlock ceiling. `power_ui.py`
requires a separate confirmation before editing above default. It keeps
an externally active high LACT value visible while presenting the default
as an uncommitted proposal. During an un-unlocked long test, ten consecutive
LACT average-power samples above 105% of default stop the workload and
restore a matching OHC snapshot where one exists. LACT still owns every
power write; OHC does not infer physical connector temperature.

## 20.09.26 GPU fan and diagnostic actions

`gpu_control/v1_0/fan_profile.py` validates curve and static LACT fan
settings. `fan_ui.py` exposes the selected mode and sends the fan test
button to `page.py`'s bounded preview. `client.py` checks the current LACT
configuration against the requested trial, permitting only LACT's omission
of zero hysteresis defaults. `reset_ui.py` owns read-only input discard and
the explicitly confirmed per-GPU LACT-default reset. `diagnostics_ui.py`
holds a bounded OHC action history, reads the last 200 lactd journal lines
asynchronously and exports on request with private file permissions.
`stress.py` validates the 4K/8K vkmark command; `stress_ui.py` observes
selected-GPU load, temperature and throttling, and only calls high load a
meaningful pass when the samples warrant it. It never writes tuning values
for a current-value run.

## 19.09.26 Current-value GPU load test

`stress_ui.py` samples LACT's current GPU configuration at launch. With no
OHC-owned snapshot, the benchmark is read-only and monitors that same
configuration; a fault stops the graphics process and reports that OHC has
no prior value to restore. With a matching saved OHC snapshot, the previous
rollback path remains available. The Tuning inputs are never implicitly
applied by the long test.

## 19.09.26 GPU benchmark installation in both views

`gpu_control/v1_0/page.py` detects the missing short-test benchmark before
calling LACT's `set_gpu_config`. It delegates installation to the existing
`stress_ui.py` helper path, which serializes requests and reports the result
in both GPU tabs. `packaging/install-dependencies.sh` selects Fedora's
`vkmark` package from configured repositories and asks before installation.
Finishing that process never applies or tests GPU tuning values automatically.

## 19.09.26 GPU fan curve and load verification

`gpu_control/v1_0/fan_profile.py` validates five ordered temperature/speed
points against LACT's read-only fan limits. `fan_ui.py` edits the curve and
passes only validated fields to `client.py`; LACT is the sole GPU fan writer.
`stress.py` selects a larger Vulkan benchmark and screens LACT telemetry.
`stress_ui.py` owns the cancellable process and timer for an OHC-saved GPU
profile. A fault requests the prior snapshot only if LACT still matches the
saved OHC configuration. `hardware_checker/v1_0` prefers vkmark and retains
glmark2/vkcube fallbacks for its read-only PCIe link assessment.

## 19.09.26 LACT capability and Levita exit checks

GPU Control parses LACT's local `device_clocks_info` in a pure model before
showing clock inputs. The parser accepts only the reported AMD RDNA table
and numeric limits; proposals remain bounded by that range and by a small
per-test change. The LACT configuration itself remains the rollback snapshot.
Levita shutdown uses an exact PID read from `/proc` if the largest TRCC
daemon is no longer the originally recorded one, avoiding a false cleanup
failure when that process has exited while retaining the ownership boundary.

## 19.09.26 UI and diagnostic refinement

Hardware Checker 1.0 now discovers a bounded `vkcube` fallback through its
read-only probe and selects fixed arguments in `page.py`. A direct GPU-test click
first runs the ordinary read-only scan, then continues into the load test; it
does not require a separate full check or a privileged DMI dialog. Qt only marks the PCIe
rescan as under load while the graphics child is running. Case and checker
tables size identification columns from content; the shared theme gives case,
checker and temperature statistics the same table treatment. Temperature
History 1.2 adds `gauge.py`, a pure display widget reused by Overview, Cooling
and the recording page. RGB Studio 1.15 changes only pure GPU strip sampling;
the writer, route and saved LED topology are unchanged.


## .96 Read-only hardware assessment

Hardware Checker 1.0 separates pure PCIe/DMI/RAM assessment (`model.py`),
bounded Linux inventory (`probe.py`) and Qt process/UI ownership (`page.py`).
The GUI never runs the inventory synchronously. Ordinary state comes from
`lscpu`, `/proc` and read-only sysfs. CPU virtualization is reported only from
the kernel-exposed AMD SVM or Intel VMX flag. Optional Type-17 memory data uses
fixed system paths for `pkexec dmidecode --type 17`, with credentials retained by
Polkit. A user-started glmark2 child is time-bounded and sampled while active;
it cannot change clocks, voltage, fans, firmware or BIOS. NVMe assessment never
writes storage. Current/max link data is kernel evidence, not a promise that a
component or slot should support a different specification.

## .95 Selected media and exposed preview state

`lcd_levita/v1_7/media_preview.py` captures pending canvas state/media and promotes
it only after successful apply. Browsing and recovery leave the last confirmed
copy intact. `display_effects/v1_11/page.py` owns transient exploration/default
fallback and matching active catalog choices. Shared local Qt decoding and
ancestor clipping live in `lcd_media_manager/v1_0/video_preview.py` and
`preview_visibility.py`; display-effects exports retain their API without a
circular LCD-first import. Null/repeated canvas layers are stable, and bounded
card preparation reserves row height before insertion. No USB writer is added.


.94: `pc_case_profiles/v1_5/editor_sections.py` reparents existing form widgets
between columns/tabs; `inline_editor.py` sizes the inspector from the actual
case viewport, keeps domain dialogs/validation and footer without inner scroll,
and brings the form into view. `ui_performance/v1_1/dynamic_text.py` captures
late tab captions. `rgb_studio/v1_15/gpu_strip_sampling.py` uses wider quintic
spinner/comet envelopes and one paired virtual sampling footprint, evaluated
at each header's actual count. Existing global elapsed clock, directions,
physical topology and sole SDK writer remain authoritative.


## .93 LCD intent and memory policy

LCD Runtime 1.1 `design_state.py` owns explicit default precedence and immutable
accepted command snapshots. Startup generation rejects stale delayed retries;
preview, profile staging and hardware intent remain independent. Recovery uses
the existing serialized sole-writer TRCC queue with the same prepared assets.
`memory_guard.py` classifies stable RSS, sustained growth, emergency RSS and
measured MemAvailable. No memory restart during a pending apply transaction.
Default keys and explicit profile loads remain compatible; no new USB protocol.

## 14.09.26 – Bounded module recovery (.92)

Process Runtime 1.1 supervises the existing sensor and SDK clients with explicit
failure causes, bounded stderr/tracebacks and private module-events.jsonl.
SDK startup and frame acknowledgements have five-second deadlines and 1/2/4-s
backoff. Only confirmed progress after 30 seconds resets its crash budget.
LCD Runtime 1.0 watches positive complete TRCC CLI send acknowledgements, not
PID liveness; static media also uses the existing IPC keepalive ticker. Startup
and finite commands have 45-s deadlines; established transfers have a 15-s
silence deadline. Only concrete owned clients are killed. Existing daemon
recovery/cooldown and native crash quarantine remain authoritative. The
read-only game probe performs /proc scanning and bounded GameMode outside Qt.
Software sends never imply physical LCD readback. GUI/core/cooling are not yet
fully independent services; firmware watchdog and calibrated PWM remain.


.91 adds `process_runtime/v1_1/`: one read-only stdio sensor worker, one in-flight
request, fresh snapshots and bounded host supervisor. Consumers never do a
production GUI fallback read when this runtime is present. Temperature-history
exports are lazy for Qt-free sensors. `rgb_studio/v1_15/render_plan.py` sends pure
calculation data to the existing SDK worker; the host still authorizes every
frame. `application_shutdown/v1_1/` separates durable journal, bounded observer
and owned Qt-process cleanup from hardware restoration. An explicitly confirmed
tray-continuation choice is persisted and may be migrated once from a matching
private journal record; it does not alter explicit Quit or session shutdown.
Autonomous core/cooling service remains a subsequent validated stage, not an
introduced hidden daemon.

## Architectural principle

Open Hardware Control is a single Linux desktop application with modular hardware backends. The GUI may unify devices visually, but ownership, validation and transport remain separated so two subsystems do not write to the same physical device concurrently.

`MODULE_REGISTRY.md` is the authoritative machine-readable task-to-module index. New or migrated feature code lives in exactly one current `src/modules/<name>/v<major>_<minor>/` directory. Module version and application version are independent: a later application release may still use a stable module 1.0. `docs/ai/AI_DEVELOPMENT_GUIDE.md` defines the mandatory extension steps and file-size budgets for context-limited coding models.

## Complete configuration packages and physical LED geometry

Profile Bundle 1.0 separates typed settings/path rewriting (`values.py`),
strict atomic ZIP I/O (`archive.py`), Qt UI/owned worker (`controller.py`,
`worker.py`), safe startup restore/rollback (`restore.py`) and legacy JSON
exchange (`legacy_profiles.py`). No hardware backend or external app setting
is imported. Imported automation, curve activation and PWM calibration are
fail-closed; the full current profile retains configurations for manual use.

RGB Studio 1.13 owns GPU-only open-strip smoothing in pure `gpu_strip_sampling.py`.
`gpu_support_sync.py` resolves one explicitly wired, selected, conflict-free
GPU/support pair with valid actual counts. Both use the GPU effect and shared
normalized phase; other zones retain their rendering. No count/selection/PWM
mutation, additional writer or rate change. The existing SDK request includes
the persisted synchronization preference in its cache signature.

It separates physical topology normalization/render sampling
(`led_topology.py`), bounded independent settings and case-space projection
(`led_topology_store.py`) from its Qt preview (`led_topology_editor.py`).
Only explicit paths and unambiguous case blocks affect spatial directions.
Fan chain order is independent from rotation within each ring. The optional
bounded reversal flag shares model/preview/sampling/log/package persistence.
Import asset extensions match export and path conflicts are checked pre-staging.
Actual test indices, zone sizes, GPU overrides and sole-writer transport remain.

## Layers

### 1. UI / application orchestration

UI Performance 1.1 owns left-navigation-only overlays, late canonical text
tracking and bounded LCD card preparation. Four GUI-thread cards/turn and a
soft 8-ms budget avoid a monolithic first visit; hidden portions wait for three
seconds without app input. Hidden animation/thumbnail workers stay paused.
Case Profiles 1.3 embeds existing guarded property dialogs as widgets in one
right-side inspector, with explicit Save and generation-scoped async inspection.
Cooling State 1.0 separates persisted requested startup from acquired control;
fresh owner results gate both master buttons, while existing calibrated-channel
and backend checks remain mandatory. Explicit tray quit is idempotent, preserves
startup intent and schedules Qt exit after best-effort isolated cleanup.
RGB Studio 1.13 leases only selected ENE RAM out of SDK frames during the three
precautionary retries. It drains the last RAM-containing frame, retains other
assignments/timers/elapsed phase and invalidates RAM Direct readiness on release.
Reset/shutdown invalidate the lease; no parallel transport or rate increase.

Application Shutdown 1.0 isolates the existing orderly restoration phases.
Owned Qt timers and backend callbacks are quiesced before exit. The root-owned
fan helper is asked to exit by closing its existing stdin pipe and waiting for
EOF, before bounded user-level signal fallbacks; signal denial cannot abort
the remaining cleanup. No new privileged operation or hardware writer is
introduced. Clear the clean LCD marker only after successful restoration.
Close-to-tray remains a hide action, not a hardware shutdown.

PC Case Profiles 1.3 separates proportional fitted geometry, resize gestures,
2.5-D depth materials and reported connector captions into focused helpers.
Visual scale is shared or independently persisted for cooling without changing
hardware topology. RGB Studio 1.13 owns direct per-block controller/header
selection and bounded settings-only physical bindings in `slot_route_editor.py`
and `slot_routes.py`, separate from design/PWM state, plus all-writable/individual
selection in `selection.py`; the list shows the full inventory and never
selects a locked device automatically. These UI actions create no transport.

`header_preview.py` owns a nested preview-depth lease: discovery and automatic
design application pause until the editor closes, preventing old saved sizes
from being reapplied during tests. Successful close/save resumes one unchanged
selected design only with enabled writes and available owned engine.
`engine_recovery.py` handles explicit owned-process restart and discovery
generation invalidation; crash quarantine still blocks automatic restart loops.
`fan_profiles.py` and `fan_profile_editor.py` keep bounded personal physical
model/color/LED declarations independent of PWM/effect snapshots; model totals
are suggestions validated against existing SDK bounds, never bulk migrations.

RGB Studio 1.13 includes a bounded reusable custom fan catalog in `fan_library.py`,
shared by block and zone editors. `personal_wiring.py` applies the owner's
revised five-port Airgoo reference once only, pins complete existing counts
independently from designs and preserves unrelated zones and PWM state. It
does not invent missing server lengths or continuously override manual edits.

- `src/kraken_control.py` — executable PySide6 compatibility orchestrator, navigation, page composition and the still-unextracted legacy feature controllers.
- `src/app_constants.py` — application identity, version and shared defaults.
- `src/branding.py` — project-owned logo/icon selection, the compact sidebar brand surface and a dedicated 22/32/48/64 raster set for Plasma's system-tray entry.
- `src/temperature_utils.py` — hardware-independent temperature unit conversion.
- `src/privacy_logging.py` — privacy redaction plus bounded startup/crash logging.
- `src/window_diagnostics.py` — early privacy-bounded Qt-window and helper-process tracing plus an exact-signature quarantine for the observed unnamed parentless 640×480 `QFrame`.
- `src/command_backend.py` — serialized `QProcess`/liquidctl command queue used by the UI orchestrator.
- `src/cooling_card_state.py` — pure single-expanded-card state transitions for the chassis-fan UI.
- `src/cooling_widgets.py` — hardware-independent curve editor and compact fan-curve preview.
- `src/modules/localization/v1_0/` — one independent data file for each supported language plus a Qt-/hardware-free catalog assembler and dynamic-caption policy.
- `src/localization_catalog.py` — thin compatibility facade for the versioned localization module.
- `src/modules/application_activation/v1_0/` — fixed-message local activation server/client and autostart-only startup-token policy; it does not replace the process lock.
- `src/modules/window_chrome/v1_2/` — accessible OHC main-window chrome using compositor-delegated Qt move/resize operations, explicit cursor cleanup and a corner-reaching close target; dialogs keep native decoration.
- `src/modules/ui_performance/v1_1/` — global lightweight transition overlays and the bounded regenerable catalog/preview cache. It never captures whole pages or owns hardware output.
- `src/modules/ui_themes/v1_0/` — independent light/dark palette and semantic-token modules, an allowlisted future-theme registry and the shared Qt stylesheet controller.
- `src/modules/hardware_backends/v1_0/` — pure fail-closed normalization and resolution of persisted backend choices; it contains no hardware transport.
- `src/modules/hardware_checker/v1_0/` — read-only CPU/SMT, board, PCIe GPU,
  NVMe and RAM inventory with pure actual/maximum assessment, optional fixed
  Polkit DMI details and a user-started bounded GPU link test.
- `src/modules/hardware_fix/v1_0/` — model-specific, reversible fixes below
  Hardware Checker; fixed resources and actions only, starting with an
  anonymized MSI MAG 274QPF X30MV VRR EDID profile.
- `src/modules/temperature_history/v1_2/` — bounded in-memory session history, dated interactive Qt chart, resizable split views, read-only grouped Linux-hwmon discovery and explicit selected-range CSV/JSON reports; it never claims tuning ownership or writes automatically.
- `src/modules/cooling_safety/v1_0/` — model-aware conservative PWM floors applied before every supported cooling write.
- `src/modules/pc_case_profiles/v1_5/` — central Case workspace after Overview, 30 detailed original case illustrations, shared RGB/LED/reported chassis-PWM assignments and optional independent cooling positions only; no control activation or calibration from mapping.
- `src/modules/rgb_studio/v1_15/` — RGB gallery, direct block/header selection with independently persisted stable bindings and explicit native/controller-zone GPU routing; generic bounded Direct-header pixel editor, protected manual counts, semantic ARGB diagnostics and full-width transfer status. Lazy exports keep count-aware pure sampling helpers Qt-free. Every configured zone renders independently without changing the existing sole-writer queue or 25-Hz target; SDK throughput is not physical readback.
- `src/modules/display_effects/v1_11/` — bounded effect state, procedural smoke renderer, attributed/filterable offline media catalog, responsive Layer-1/Layer-2 cards, explicit firmware restore, visibility-bound local MP4 preview and profile-start staging through the existing Levita studio.
- `src/modules/responsive_gallery/v1_0/` — reusable actual-viewport column calculation and coalesced Qt resize relay for card grids.
- `src/modules/lcd_media_manager/v1_0/` — non-destructive multi-folder/individual-media references, exclusions, editable display aliases and safe fallback names; original files remain untouched.
- `src/modules/section_tabs/v1_0/` — reusable synchronized in-page tabs for sidebar sections with child pages; navigation state only.
- `src/modules/responsive_startup/v1_0/` — bounded/coalesced CoolerControl status process plus fail-closed host integration; no PWM writer.
- `src/ui_layout.py` — persisted UI layout/navigation model.
- `src/modules/window_placement/v1_5/` — Qt-independent screen/geometry/start-state policy plus a bounded KWin Wayland script/D-Bus check of the actual compositor output for OHC's PID; unavailable names fall back to primary, and Qt geometry alone cannot confirm a Wayland placement.
- `src/desktop_shell.py`, `src/desktop_designs.py`, `src/desktop_assets.py` — KDE desktop-design tooling kept logically separate from hardware writers.
- `src/modules/wallpaper_engine/v1_3/` — cached read-only Wallpaper Engine library, Plasma adapter, localized onboarding with confirmed helper packages, verified Fedora plugin installer and visibility-bound page; CaptSilver remains the renderer and owner of its QML surface.

`MODULE_MAP.md` is the task-oriented reading guide for local coding models after they resolve the current version in `MODULE_REGISTRY.md`. New base modules must not import `src/kraken_control.py`; the main file re-exports moved names during the incremental migration so existing tests and integrations remain compatible.

### 2. Coordination and ownership

- `src/hardware_request_coordinator.py` — serializes/prioritizes hardware requests where multiple UI features share a device path.
- `src/cooling_ownership.py` — prevents competing cooling controllers from writing simultaneously.
- Process/session locks in the application prevent duplicate OHC instances from owning the same hardware.
- A duplicate launch may ask the lock-owning instance to show its window over a private local socket, but cannot issue hardware commands.

### 3. NZXT backend

- `src/nzxt_backend.py` — device/capability identification.
- `src/kraken_sensors.py` — telemetry/sensor handling.
- `src/kraken_cam_streamer.py` — LCD/CAM-compatible frame streaming path.
- `src/kraken_lcd_designs.py` — built-in LCD design/rendering logic.
- `src/nzxt_rgb.py` — NZXT RGB control and validated effects.
- `src/nzxt_esc_profiles.py` — NZXT CAM/ESC profile import handling.
- `packaging/71-nzxt-kraken-2023.rules` — udev access rule.

### 4. Mainboard chassis-fan backend

- `src/mainboard_fan_control.py` — Linux hwmon/NCT6687 discovery, calibration, curves, sensor selection, friendly kernel labels and runtime safety; the host UI owns the confirmed assignment reset and sequential mapping wizard.
- `src/modules/mainboard_driver_setup/v1_1/` — asynchronous read-only distribution, board, Secure Boot/MOK and module inspection; separate fixed Ubuntu/Fedora/Arch dependency commands; MSI-X870-only options gated by DMI identity; robust affirmative MOK-result parsing and a status-gated wizard around confirmed fixed terminal actions for DKMS key generation, MOK import and post-restart module loading.
- `src/ohc_fan_helper.py` — narrow privileged helper.
- `packaging/io.github.Frelidon.OpenHardwareControl.fan.policy` — Polkit authorization policy.
- `packaging/install-fan-helper.sh` — helper installation.

Safety invariant: unconfirmed channels are not automatically written, and firmware/BIOS ownership is restored when OHC control ends where supported. The optional persistent authorization is one exact-account Polkit rule for the same fixed helper action; it changes only whether Polkit asks again and does not widen the helper protocol or bypass calibration.

The settings-level backend selector exposes only implemented transports: TRCC Linux for the Levita display and calibrated OHC Linux-hwmon for motherboard fans. Automatic selection resolves among those transports. An explicit unavailable choice fails closed and is never silently replaced; planned native-Levita and CoolerControl adapters remain disabled until validated.

### 4a. Thermalright Levita display and cooling

- `src/thermalright_display.py` — local media/TRCC discovery, non-destructive complete-filename catalog deduplication, strict Levita geometry filtering, protected cutout and rendering model.
- `src/dashboard_layout.py` — small dashboard-layout mixin that combines saved card preferences with current hardware/value availability and renders Overview status hints from confirmed PWM/sensor state; it performs no hardware discovery or writes.
- `src/thermalright_display_ui.py` — legacy-compatible thin orchestration for the card library, media preparation, process queue and the versioned editor module.
- `src/modules/lcd_levita/v1_7/layout_model.py` — pure, malformed-record-tolerant layer-2 block model, coordinate bounds, whole-layout offsets and settings serialization.
- `src/modules/lcd_levita/v1_7/layout_canvas.py` — Qt canvas interaction: one stable draggable graphics item per logical data block; right-click requests the inline property editor in the surrounding surface instead of opening a dialog.
- `src/modules/lcd_levita/v1_7/panel_geometry.py` — pure 1600×720 geometry for separately adjustable top/bottom media radii at the right notch boundary and the independent outer panel outline.
- `src/modules/lcd_levita/v1_7/runtime_policy.py` — pure validation and safe fallback for persisted Levita runtime settings.
- `src/modules/lcd_levita/v1_7/stream_recovery.py` — pure bounded backoff policy for a failed daemon IPC video ticker; it never owns USB or performs reconnects.
- `src/modules/lcd_runtime/v1_1/` — lifecycle classification for legacy long-running IPC tickers and TRCC 9.10.4's exact successful transfer to the daemon-owned `VideoLoop`; only genuine failures consume the bounded restart budget.
- `src/modules/lcd_levita_shutdown/v1_0/` — pipe-bound crash guard for the fixed Levita release operation; as a standalone helper it inserts the installed application root before importing versioned OHC modules.
- `src/modules/lcd_levita/v1_7/theme_adapter.py` — read-only import of `trcc.json` or delegated legacy `config1.dc` decoding and immutable OHC cache-theme staging; selected video and generated mask are linked into the same staged theme to keep the hardware apply in one connected `load-theme` session.
- `src/modules/lcd_levita/v1_7/motion_renderer.py` and `motion_compositor.py` — four original Layer-2 glow/particle loops and content-addressed local screen-blend composition with any supported Layer-1 image/video; editable live values remain a separate upper layer.
- `src/modules/display_settings/v1_0/page.py` — Qt-only construction of screen/start-state and experimental Levita-FPS settings; the host remains responsible for persistence, placement and hardware orchestration.
- `src/modules/levita_performance/v1_1/` — pure 15-FPS-safe policy, experimental 60-FPS gate, fallback chain, ten-second polling policy and conservative GameMode/Gamescope/explicit-process signals without load inference or foreign Wayland-window inspection.
- `src/modules/display_effects/v1_11/` — configurable smoke preview and bounded export, responsive graphical Layer-1 cards for five attributed abstract families and fifteen people-free nature/space videos, plus supersampled original eight-direction OHC Light Bands. Exact validated media paths restore the visible category/design/variant without hardware access; Layer-2 decoration stays independently selectable and never changes from a Layer-1 click.
- `src/thermalright_cooling.py` — read-only USB identity, driver-label-based PWM role suggestions and conservative profile duties.

The display USB path and motherboard PWM cooling path remain independent. A suggested header is never authorization to write: pump and radiator mappings require separate physical confirmation, CoolerControl ownership blocks writes, and firmware control is restored on exit. No coolant value is inferred from CPU temperature or RPM. Levita display autostart is a separate explicit setting; discovery alone never writes and test mode remains authoritative. Before an explicit display write, the active play loop releases and OHC replaces any stale daemon device with a tolerated detach plus mandatory fresh handshake; confirmed handshake timeouts receive at most one bounded retry.

Imported Levita source files are immutable. OHC stores user edits as its own settings override and stages a content-addressed cache directory containing generated `trcc.json` plus links to the selected local artwork/media. The external folder scanner rejects symlinked theme inputs, while this private validated cache is accepted by the runtime loader. It never rewrites `config1.dc`. A CPU/GPU label, live usage value and suffix stay one logical block and move together; common TRCC layouts that store the caption and usage as adjacent separate elements are coalesced in OHC's editable model. Since TRCC 9.10.4, the daemon's `VideoLoop` owns the persistent video and sensor cadence; the short-lived `display play` client reports that exact hand-off and exits successfully. OHC keeps daemon-memory supervision active but does not spend ticker-restart budget on this planned exit. Controlled shutdown first stops local display clients and then releases `87ad:70db` from the daemon with one bounded `device disconnect`, so daemon-side metric rendering also ends and the firmware's built-in Thermalright screen can return after its no-frame timeout. After a confirmed real write, a separate pipe-bound helper watches only the OHC parent lifetime and repeats this fixed release once on unexpected parent loss; clean restore cancels it. Because the helper is launched by absolute script path outside the package entry point, it bootstraps the application root into `sys.path` before importing the shared health model.

Layer intensity is presentation state: layer 1 is stored globally and layer 2 per selected design, both bounded to 25–150%. Explicit units in bundled formats always use `show_unit=true`. `src/hardware_diagnostics.py` reads sensors without writes; TRCC's misinterpreted low-Hz range through 1,000,000 Hz may temporarily replace only the affected live format through daemon IPC and restores the dynamic format on recovery. General plausibility polling logs state transitions only.

Before `load-theme`, legacy orchestration accepts either the original `config1.dc` contract or a bounded native `trcc.json` whose root, element list and exact 1600×720 geometry validate. This mirrors TRCC Linux's loader and prevents OHC's own editable cache from being rejected. A layer-2 selection must not rebuild the background-card catalog; hidden combo state is updated under blocked signals and followed by one preview refresh.

### 5. Corsair via OpenLinkHub

- `src/openlinkhub_integration.py` — validated local API integration.
- `src/openlinkhub_mouse_visuals.py` and `src/assets/mouse-*.svg` — generic project-owned mouse diagrams.

Safety invariant: OpenLinkHub communication remains on validated loopback endpoints; OHC does not invent direct Corsair USB commands.

`src/modules/openlinkhub_update/v1_0/` is a separate update boundary. Its read-only policy discovers only existing RPM/DEB packages or an exact user service, compares against the fixed official GitHub latest-release endpoint and validates the advertised amd64 asset size and SHA-256. Package updates use existing repositories. User-space updates stage unprivileged content, preserve configuration/database data, keep the old tree as a sibling backup and roll back when the service cannot start. Because OpenLinkHub ships its Web UI in the same application tree, no independent Web-UI updater is required. All routes require an explicit UI confirmation.

### 6. OpenRGB / RGB Studio

- `src/openrgb_integration.py` — managed OpenRGB process/integration layer.
- `src/openrgb_sdk.py` — bounded loopback SDK protocol implementation.
- `src/rgb_devices.py` — device/group/topology model.
- `src/rgb_effects.py` — OHC software effects.

Safety invariant: only the private local engine is writable; external OpenRGB ownership blocks OHC writes. Device-reported capabilities and validated zone sizes are authoritative. The PC layout may navigate to an assigned device/zone editor but cannot invent Direct Mode or addressable LEDs.
All launches of the Qt-based OpenRGB executable use the offscreen platform, including inventory and native-mode CLI clients, so a backend-only operation cannot create a desktop window.

### 6a. Wallpaper Engine for KDE

- `src/modules/wallpaper_engine/v1_3/library.py` — bounded read-only parsing of local Workshop `project.json` metadata and an explicitly selected personal-video directory; only regenerable metadata is cached.
- `src/modules/wallpaper_engine/v1_3/plasma.py` — read-only Plasma state parsing plus validated commands for Plasma's scripting interface, DisplayMode and CaptSilver's D-Bus object hosted by `org.kde.plasmashell`.
- `src/modules/wallpaper_engine/v1_3/installer.py` — selects only an exact stable official RPM for the local Fedora major/architecture, requires GitHub's SHA256 digest, downloads unprivileged into OHC's private cache and emits a fixed Polkit/DNF command only for that verified path.
- `src/modules/wallpaper_engine/v1_3/onboarding.py` — localized setup checklist, first-visit dialog, confirmed distro helper-package step and asynchronous two-confirmation plugin installer; it never handles administrator credentials.
- `src/modules/wallpaper_engine/v1_3/page.py` — native OHC gallery with fixed card geometry, persistent scaled thumbnail cache, filters, per-screen target, playback controls, three scaling modes and launcher for Plasma's original wallpaper KCM.

OHC never copies, patches or embeds the upstream QML plugin and never writes Steam Workshop files. Applying a wallpaper, scaling mode or one of the two documented setting profiles is an explicit user action routed to Plasma. Playback addresses `/WallpaperEngine` on Plasma's existing session-bus name because that is the object CaptSilver registers even when its optional standalone service alias fails. The personal-video directory rejects the Steam library itself, preventing a recursive scan of Workshop media. The stock CaptSilver v1.4 profile is the default and the optional performance profile changes only documented configuration keys. The shared OHC cache stores only bounded, regenerable metadata and scaled previews; it is not a watcher and never contains Workshop originals.

### 7. Release, diagnostics and security

- `packaging/collect-diagnostics.sh` — diagnostics collection with privacy handling.
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
7. Document tested vs. merely detected support in `docs/hardware/SUPPORTED_DEVICES.md` and `docs/hardware/DEVICE_SUPPORT.md`.
8. Integrate UI only after the backend contract is clear.

Do not place model-specific protocol guesses directly into UI code.


## Content-focused UI contracts (.172)

The original background and diagram animation owners remain unchanged. Case
composition reuses existing state/commit callbacks in three views, with a
settings-only component draft inspector. ContentHeight observes bounded Qt model
events and visible tree expansion; it never probes hardware. Sidebar art uses
original vector drawing and palette-keyed icon caching. Hardware child
navigation synchronizes existing section owners without new top-level pages.
OpenLinkHub device controls are injected with the existing mouse renderer;
metadata comes from bounded .9.4 detail requests outside the Qt thread. Startup
DPI lacks an upstream selection endpoint, so an explicit user-service-only
helper updates exactly the existing Profile field with backup, ownership and
health checks, while named profiles use official HTTP actions. No direct Corsair
USB transport is added. Backend staging integrity and service rollback stay in
separate pure/worker helpers.


The .174 startup-DPI preference is separate from the backend’s mutable active
stage. A private per-profile rule and optional marked user-service pre-start
hook restore it before the sole USB owner starts. Only an explicit Save installs
the hook; reset returns to native behavior. The helper refuses active ownership
and validates files inside the current installation. Missing optional code is
non-blocking. Future module path migrations must retarget marked hooks without
creating unsolicited opt-ins or dropping rules.
