# Changelog

## Unreleased

## 3.4.29.158 INTERN · 31.10.26

- Treat OpenRGB SDK v6 packet 157 as the documented asynchronous active-profile
  callback after validating its bounded null-terminated payload. Continue to
  reject malformed and unknown packets and invalidate cached inventory safely.
- Prevent the valid callback from being misreported as an ACK-10 failure during
  ENE-DRAM recovery while MSI Mystic Light and the remaining Direct devices run.
- Keep the corrected 1 MHz TRCC boundary value until three consecutive valid
  five-second AMD GPU clock samples prove that the dynamic source recovered.
  Missing or malformed readings reset the recovery evidence instead of restoring
  the unsafe live source.

## 3.4.29.157 INTERN · 20.10.26

- Replace the mixed historical roadmap with a current split between actionable
  repository work, real-hardware/optical confirmation and long-term candidates.
- Keep Python/PySide6 as the application architecture. Require profiling and a
  Python fallback before considering Rust for an isolated pure CPU hotspot.
- Make animated case-fan light rings slightly brighter and wider through a
  bounded cached colour transform; preserve black/off segments, gradients,
  effect timing, physical mapping and hidden-timer shutdown.
- Keep package installation as phased follow-up work; no package-manager action
  is claimed by this change.
- Add Programs 1.0 with a bounded background inventory of desktop applications,
  search, configurable absolute base folder and validated saved profiles for
  System, Flatpak, Snap and AppImage. Add an explicit background GitHub release
  check/download for all official assets and both source archives, with host and
  size limits, SHA256SUMS, JSON manifest, atomic version folder and no overwrite.
  It never executes a discovered desktop command; package actions require a
  separately validated profile, exact preview and explicit confirmation.
- Add manually saved installation targets with an exact confirmation preview:
  per-user Flatpak from an existing Flathub remote, Snap through Polkit with an
  optional validated channel, and local AppImage user-execute activation inside
  the configured base folder. Use argument arrays, bounded output and no shell;
  leave ambiguous distribution system packages disabled.
- Persist a normalized GitHub owner/repository and source-release version on an
  installation profile separately from its Flatpak branch or Snap channel;
  selecting the profile restores the matching download source.
- Allow an exact downloaded AppImage asset from the inspected release plan to
  be selected for an AppImage profile only after the atomic version folder and
  GitHub-reported byte count are present. Installation header/path checks remain
  separate and mandatory.
- Distinguish a Levita USB claim held by the exact TRCC daemon registered by the
  current OHC session from a foreign owner. Recover the former once through the
  existing bounded restart/design-restore path while leaving all untracked,
  preexisting or PID-mismatched processes untouched.
- Audit `.151`–`.156` against code, tests and later status evidence: repository
  implementation is present; real Fedora coverage and optical case-RGB
  brightness/direction/order confirmation remain explicitly open.
- Ignore queued cooling-ownership probe requests after shutdown or Qt process
  deletion, preventing a late Shiboken exception during full UI teardown.

## 3.4.29.156 INTERN · 06.10.26

- Keep fresh LED-path drafts editable even when no path was saved; handle
  actual Qt child polish and inline reparenting without dismissing the editor.
  Only explicit user gestures activate path saving. Opening, count-only changes
  and cancelling do not invent geometry or authorize hardware.
- Correct visible spatial wave travel, independent local effect reversal and
  per-header projection when the overall case direction is local. Preserve
  physical LED/fan numbering, explicit header overrides and unmapped legacy frames.
- Restore animated case fan light rings using bounded samples from the same
  confirmed effect clock. A single reported header can show schematic colours
  without a saved physical path; ambiguous routes stay unresolved. No RPM simulation.
- Preserve unfinished flow choices on ordinary refresh, reflect changed saved
  profile directions and explain when a declared LED path is still needed.
- Add real Qt mouse/keyboard, save/cancel, visible/hidden timer and temporal-frame
  regressions, separate Fedora/Ubuntu fixtures and 2,154 four-language UI sources.
  Existing device commands, profiles, counts, designs and ownership remain intact.

## 3.4.29.155 INTERN · 06.10.26

- Import the canonical Levita device key for successful playback-health
  callbacks; cover real Qt class methods and globals on both distributions
  so AST fixture injection cannot hide an undefined runtime symbol.
- Separate a legacy NZXT assistant preset from an explicitly selected startup
  PC/RGB/LCD profile only on confirmed Ubuntu/Levita systems without a ready
  NZXT; preserve unknown pending values and other distribution/hardware lanes.
- Retain the pending preset and the selected user's cooling payload without
  inventing PWM intent, mappings, calibration or an automatic migration.
- Classify an occupied Levita USB interface separately from daemon IPC/FPS
  failure and trailing udev hints on Ubuntu; stop only OHC's own retries.
- Preserve the saved design and immutable request, allowing explicit Apply
  through the existing queue after the other owner is released; never
  automatically terminate a foreign display application.
- Add targeted startup and LCD ownership regressions, a translated dynamic
  conflict status and 2,153 shared four-language message sources.
- Make separate Fedora/Ubuntu guards, native commands and regressions mandatory
  project rules; retain Fedora behavior and distinguish fixtures from live
  hardware evidence. Preserve `.154` inventory, routing and authorization fixes.
- Normalize real directories only inside the isolated DEB/RPM stage to 0755,
  preventing group-writable helper ancestors on fresh installations under
  umask 002. Preserve source/host/symlink-target permissions, file contents,
  helper/policy file modes and RPM dependencies; add a real-stage regression.

## 3.4.29.154 INTERN · 06.10.26

- Request OpenRGB 1.0's detailed inventory only for the trusted Ubuntu backend;
  preserve older OpenRGB/Fedora listing commands and complete device metadata.
- Reject names-only inventory without device types before it can replace controller identities,
  selected devices, physical routes or LED configuration.
- Open GPU header setup for explicitly routed external lighting even without a
  native GPU controller; reuse the reported Direct-header editor and guards.
- Classify explicitly routed GPU blocks for their GPU effect group without
  enabling native GPU hardware detectors or changing whole-device frames.
- Distinguish the preserved narrow fan authorization from a TRCC daemon's
  generic administrator prompt; do not grant general passwordless root access.
- Launch the audited Ubuntu TRCC backend through an OHC-owned child adapter:
  its exact RAM metadata query uses an argument-free read-only helper with a
  dedicated active-session action. Other automatic metadata stays unprivileged;
  upstream files, global PATH and independent TRCC processes are unchanged.
- Force the dedicated metadata policy to read-only 0644 in both package
  formats instead of inheriting checkout permissions; retain runtime trust
  refusal for group/world-writable helpers or policies.
- Keep the fallback RPM's explicit system-helper/policy manifest in sync with
  the normal RPM spec, with real header/payload ownership and mode regressions.
- Retain established designs, module switches, PC-profile topology and all
  later Ubuntu responsiveness/crash guards.

## 3.4.29.153 INTERN · 06.10.26

- Prevent the Levita thumbnail scheduler from calling Qt methods on preview
  cards whose C++ objects were already deleted during a rapid category change.
- Prune stale weak references both while prioritizing visible thumbnail jobs
  and when delivering a finished preview, so subsequent scroll signals cannot
  repeat the same runtime exception.
- Ignore delayed Snapshot Manager process-expiry callbacks after Qt has already
  destroyed their QProcess object during application shutdown.
- Replace the plain module-checkbox grid with synchronized two-column cards,
  module icons, green/grey status dots, and direct toggle switches.
- Add a deleted-card queue regression, deterministic gallery isolation, and a
  full offscreen Settings render. Fedora-specific installation commands remain.
- Recover missing `.148` feature/ownership controls, design automation,
  snapshot setup/creation/filtering/resource controls, hardware overview cards,
  GPU artwork, dashboard editing and four bundled original LCD animations.
- Keep feature enablement separate from sidebar visibility and preserve each
  PC profile's explicit pump/radiator wiring, including deliberate empty roles.
- Move Ubuntu LACT reads into a cancellable bounded process; optional clocks
  errors do not block stats, and stale device results cannot update a new GPU.
- Restore explicit inline GPU power confirmation and fail-closed feature gates.
- Audit optional backend versions using official sources and native package
  metadata; add Ubuntu/Arch vkmark dependencies and preserve Fedora commands.
- Add explicitly selected Ubuntu OpenRGB SDK 6 compatibility while retaining
  protocol 4/5 support and Fedora's prior negotiation default.
- Recognize OpenLinkHub user installs, require actual API write acknowledgement,
  and correct Nexus touch-key casing, inclusive bounds and atomic backup safety.
- Preserve Windows preview packaging and existing Linux/Windows platform paths.
- Bind delayed GPU/Hardware Fix callbacks to QObject lifetimes and reject stale
  Hardware Checker process replies; forbid OpenLinkHub redirects and proxies.
- Scope all delayed LCD callbacks to window lifetime, preserving timer delays
  and hardware/recovery semantics, with deleted-page and live-control tests.
- Keep complete GPU fan labels/curves accessible at narrow sizes, restore the
  automation navigation switch, and translate all fan-workflow states.
- Recognize separately installed trusted Ubuntu OpenRGB 1.0/liquidctl 1.16.0
  without replacing distro packages; four catalogs contain 2,152 messages.

## 3.4.29.152 INTERN · 05.10.26

- Detect the CPU at startup and load its verified default pump/radiator curves
  while preserving every later user-selected CPU profile or edited curve.
- Place the CPU automation directly below the cooling ownership/conflict guard.
- Let PC profiles store CPU_FAN, PUMP_FAN, radiator, pump and chassis mappings;
  require confirmation before replacing a conflicting mapping.
- Migrate the owner-confirmed MSI MAG X870 TOMAHAWK WIFI connector layout once,
  by exact reported connector labels and without writing PWM hardware.
- Restore the explicit settings panel for sidebar module visibility and extend
  all four language catalogs to 1,916 shared entries.

## 3.4.29.151 INTERN · 05.10.26

- Split Ubuntu's package-list refresh from dependency installation so a broken
  third-party source no longer hides that the install step never ran. OHC
  reports such sources but does not modify them automatically.
- Reuse an existing `~/nct6687d` Git checkout with `pull --ff-only`, clone into
  that fixed location only when absent, and stop safely if the path is not a
  Git checkout.
- Add the optional persistent NCT6687 fan-helper authorization as wizard step
  five. Its actual system marker controls the state; package installation
  remains an ordinary administrator action.
- Extend all four language catalogs to 1,901 shared entries.

## 3.4.29.150 INTERN · 05.10.26

- Detect Ubuntu, Fedora, and Arch Linux in the guided NCT6687/DKMS/MOK setup
  and copy a distribution-specific dependency command instead of always
  presenting Fedora's `dnf` command.
- Keep the common upstream clone/DKMS path shared, add the MSI-specific
  `nct6683` blacklist and `msi_fan_brute_force=1` option only on detected MSI
  X870 systems, and fail closed on unsupported distributions.
- Show the detected distribution and mainboard in the wizard, localize the new
  UI in DE/EN/ES/FR, and document matching Arch kernel headers.

## 3.4.29.149 INTERN · 05.10.26

- Add the Hardware Checker → Hardware Fix sub-page with a narrow MSI MAG
  274QPF X30MV VRR profile, fixed-action job locking, status/adoption controls,
  actual DRM measurement, and profile-scoped removal.
- Anonymize the bundled EDID by removing its serial descriptor and omit all
  personal metadata, local paths, and game history.
- Add the prominent RGB startup/resume summary, LCD source manager, OpenRGB
  profile library, and local iCUE NEXUS static design import.
- Fix the DEB upgrade on current Ubuntu releases by accepting the split
  `polkitd` and `pkexec` packages as the supported alternative to the legacy
  `policykit-1` dependency. Fedora/RPM behavior is unchanged.

## Unveröffentlichter RGB-/LCD-/NEXUS-Manager · 05.10.26

- Show RGB startup profile, takeover state and automatic resume in a prominent
  top panel. After the first explicit takeover confirmation, profile autostart
  and passive reclaim default to enabled; session ownership and conflict checks
  remain mandatory.
- Extend the local LCD media manager to GIFs and connect it to the Kraken page
  for multiple folders and individual files. Bundled OHC designs always remain
  visible and removing a source never deletes user media.
- Add a private, validated OpenRGB profile library. Legacy binary `.orp`
  profiles can be applied only to their complete saved device scope; OHC does
  not guess controller records to fake per-device filtering.
- Add a backed-up, atomic iCUE NEXUS design bridge for local OpenLinkHub user
  installations. Static 640×48 artwork and bounded manifest-defined touch
  buttons are imported without a new USB driver; activation uses the documented
  loopback `/api/lcd/profile` endpoint.
- Extend all four localization catalogs to 1,888 messages. Fedora packaging and
  runtime paths remain unchanged.

## Unveröffentlichter RAM-/Levita-/Neustart-Hotfix · 05.10.26

- Show every detected Direct RGB DIMM as one logical memory bank while retaining
  one stable ID, LED count and SDK frame per physical module. The shared editor
  applies a validated common count; fixed eight-LED ENE modules stay at eight,
  while resizable hardware keeps the range reported by OpenRGB.
- Run the existing bounded ENE Direct reclaim before the first manual RGB
  design, not only during profile autostart, so accepted SDK frames do not leave
  cold-started memory controllers asleep.
- Default Levita to real TRCC control only when both the detected display and
  backend are present. Missing hardware/backend remains preview-only. The
  reference TRCC 9.10.4 installation passes all 11 doctor checks and sees USB
  `87ad:70db`.
- Add an orderly OHC restart action whose detached waiter validates the old PID
  and waits for the single-instance owner to exit before relaunching.

## Unveröffentlichte PC-Profil-/RGB-Topologiekorrektur · 05.10.26

- Store a complete, bounded settings-only hardware snapshot in user-created PC
  profiles: physical ARGB controller/header routes, fan and LED counts, manual
  headers, LED paths, RAM/device grouping and aliases, selected devices, GPU
  routes and known PWM-to-case assignments.
- Restore that topology with stable identifiers and fail closed when a device
  or header is absent. Loading a PC profile still performs no RGB, fan, GPU or
  display write.
- Keep the embedded Case inspector open across combo-box selection and outside
  clicks; drafts now close only through Save, Cancel, Escape or the explicit
  close button.
- Evaluate the supplied runtime log: both ENE DRAM modules repeatedly accepted
  complete eight-LED SDK frames; the remaining failure was the unconfigured MSI
  header during intermediate tests, not a RAM transport failure.
- Resolve stored personal fan defaults into the user snapshot and prevent a
  legacy one-DIMM route from narrowing a multi-device RAM block to one module.

## Unveröffentlichte Ubuntu-Backend-/Levita-Bibliothekskorrektur · 05.10.26

- Offer the separately maintained TRCC Linux backend on the LCD page only when
  a Thermalright Levita is detected and the backend is missing; expose the same
  verified Ubuntu installation in the setup wizard.
- Add an Ubuntu 26.04 path to the existing LACT installer while retaining the
  established Fedora and Arch branches. The GPU page, setup wizard and RGB
  Studio keep their existing LACT/OpenRGB installation actions.
- Load bundled OHC Levita designs even on a fresh profile with no TRCC/custom
  folder, and include TRCC's stock, downloaded catalog and user-media roots.
- Pin the official TRCC 9.10.4 and LACT 0.10.1 Ubuntu packages and verify their
  published SHA-256 digests before APT installation. No design is applied and
  no GPU/RGB/fan value is changed by installation.
- Extend all four localization catalogs to 1,851 messages and add focused
  installer, media-root and UI regressions.

## Unveröffentlichter OpenRGB-Start-Hotfix · 05.10.26

- On Ubuntu only, prevent OpenRGB CLI clients used for SDK inventory and device
  commands from performing a second local hardware detection by adding
  `--nodetect`. Fedora retains its established command line unchanged.
- On the affected RX 9070 XT system, disable only the matching Sapphire GPU
  detector in OHC's private OpenRGB configuration after repeated amdgpu SMU
  timeouts began six to seven seconds after OpenRGB startup. Six other RGB
  devices remained available during the bounded verification run, with no new
  SMU, GFX or ring timeout in the kernel log. The failed session had included
  the Sapphire controller among all seven selected RGB devices.

## 3.4.29.131 INTERN · 01.10.26

- Recognize TRCC Linux 9.10.4's exact successful hand-off to its daemon-owned
  VideoLoop and keep OHC's memory supervision active without retrying the
  deliberately completed CLI helper.
- Record daemon delegation as a healthy runtime transition instead of a ticker
  failure and keep game/desktop status aligned with daemon-owned cadence.
- Make the independent Levita shutdown helper restore the installed OHC module
  root before importing its health model, fixing the observed standalone
  `ModuleNotFoundError` after the parent process ended.
- Confirm the official 9.10.4 backend on the reference display with continuing
  1600×720 frame writes and stable RSS, thread and file-descriptor samples.

## 3.4.29.130 INTERN · 01.10.26

- Finish the responsive no-scroll GPU cockpit, direct five-point fan-curve
  dragging, exact modern numeric controls and local custom artwork actions.
- Route fan-only trials exclusively through LACT's reversible physical fan
  check; graphics load remains exclusive to tuning or an explicit load test.
- Keep RGB navigation aligned with the visible gallery, prevent the all-designs
  counter from clipping and scale the compact gallery up to six columns.
- Add settings-only case-space flow direction, speed and real LED-order editing,
  plus user-measured fan/component distance or depth in millimetres or inches.
- Defer SSD-cache maintenance while the user is active and run bounded work at
  idle I/O priority with cooperative yields and timing telemetry.
- Extend all four localization catalogs to 1,838 messages and add regression
  coverage plus renewed GPU/case offscreen rendering evidence.

## 3.4.29.129 INTERN · 01.10.26

- Transfer ownership from the old TRCC daemon PID to the exactly identified
  replacement after an OHC-controlled display-daemon restart.
- Teach the independent shutdown watcher the same replacement event so normal
  exit and crash cleanup stop the current OHC-owned child without touching an
  unrelated TRCC instance.
- Add regressions for replacement adoption, stale-old-PID rejection and
  journal replay of the transferred ownership record.

## 3.4.29.128 INTERN · 01.10.26

- Redesign Snapshot Manager thresholds and Btrfs rate limits as compact cards
  with synchronized sliders and exact numeric inputs.
- Add an atomic JSON metadata-list export and explicitly confirmed deletion of
  one Snapper snapshot through the fixed helper. Reject snapshot zero and keep
  full rollback outside the one-click UI.
- Refine the responsive GPU cockpit against the approved reference with a
  visible device heading, compact live metrics, wide clock/power tracks and a
  fan curve placed ahead of advanced ownership details.
- Extend all four localization catalogs to 1,808 messages and add real
  offscreen renderers for both revised pages.

## 3.4.29.127 INTERN · 01.10.26

- Add Snapshot Manager 1.0 as a configurable main page with Linux distribution,
  filesystem, backend, Snapper configuration/timer and Btrfs discard discovery.
- Pause new automatic Snapper work for Feral GameMode, Gamescope, configured
  processes or KDE full-screen applications. Add an optional multi-core CPU
  plus GPU heuristic with three-sample entry/release hysteresis.
- Add separate bounded desktop/game Btrfs discard rates and manual blocking for
  one hour, a chosen deadline or indefinitely. Already-running kernel work is
  throttled rather than forcibly terminated.
- Add a fixed root-owned Polkit helper with no arbitrary command, unit or path
  input, plus automatic deadline resume and recoverable root-owned mode state.
- List Snapper snapshots read-only and explain safe inspection. Keep destructive
  rollback outside the application UI.
- Extend all four localization catalogs to 1,791 shared messages and add model,
  security, navigation, packaging, full-UI and rendering regressions.

## 3.4.29.126 INTERN · 25.09.26

- Rebuild the Graphics Card control surface as a responsive three-column GPU
  cockpit inspired by the approved reference: overview/tuning, fan control and
  load-test/presentation remain visible together on wide displays and reflow
  to two or one column on narrower windows.
- Add a direct-manipulation five-point fan graph, exact spin boxes and Quiet,
  Balanced and Performance drafts while retaining LACT's reported bounds.
- Add an explicit “test + apply” path. It performs the reversible physical fan
  response test first and confirms exactly that candidate in LACT only after a
  pass; test-only rollback and a separate post-test save remain available.
- Make the fan workflow state visible and distinguish rollback success from a
  permanent commit in both the status text and GPU log.
- Add clipboard buttons for OHC events, LACT service messages or the combined
  GPU diagnostic report. Keep the general Log copy action scoped to its active
  category tab.
- Add GPU cockpit offscreen rendering and interaction regressions without live
  hardware I/O.

## 3.4.29.125 INTERN · 25.09.26

- Accept an exact 0 MHz AMD GPU clock as a normal power-gated idle sample,
  while retaining anomaly reporting for negative and over-limit readings.
- Coalesce repeated identical Qt helper-start diagnostics for five minutes and
  summarize automatic mainboard-fan curve writes as one bounded batch line.
- Redesign the Case device table around actual capabilities, hiding impossible
  LED/PWM cells for display/pump blocks and adding a read-only mapping analysis.
- Remove the redundant large RGB Studio live-preview panel and enlarge the
  animated design cards. Add the Spatial category with six presets based on
  3D Fusion, 3D Crossflow and 3D Depth Wave across saved case LED paths.
- Keep ring paths individually addressable per fan and physical LED. Existing
  start point, fan order, clockwise direction and case direction remain intact.
- Add an optional, default-off GPU fan action that permanently stores a passed
  fan-only LACT test. Mixed clock/power drafts still require the separate save;
  a static 100% request remains 1.0 in LACT and failed tests never save.
- Extend all four localization catalogs to 1,736 shared messages and retain the
  strict 78,000-character data-file limit through lossless literal compression.

## 3.4.29.124 INTERN · 22.09.26

- Keep fan count and physical topology independent. New LED paths default to a
  row, and forwarding the case fan count no longer overwrites a saved row or
  explicitly selected ring layout.
- Retain the known fan segmentation for both layouts. Ring rendering continues
  to address each fan separately with its own LED order and clockwise setting.
- Add a dedicated RGB/fan log view next to the complete and hardware-anomaly
  views. Path saves and effect plans include layout, total LEDs, fan count,
  LEDs per fan, endpoints, rotation, fan order and case-space direction.
- Keep all three log views on the existing bounded 60-minute buffers, including
  recovered crash-context RGB/fan events.

## 3.4.29.123 INTERN · 22.09.26

- Forward the physical fan count from each case component to its LED-path
  editor and derive the total from the saved LEDs-per-fan model.
- Forward unsaved fan-count changes from the open component dialog as well.
- Upgrade a compatible legacy line path to a ring bank using the declared fan
  count, so ring direction and fan order are immediately available.

## 3.4.29.122 INTERN · 22.09.26

- Store the case-space animation direction inside each declared LED path.
  Horizontal and vertical fan groups, the GPU and the support bracket no
  longer overwrite one shared direction value.
- Keep the old global direction as a read-only migration fallback. Saving an
  existing path upgrades only that component without changing any other one.
- Validate ring-preview geometry before constructing a native Qt painter and
  close every painter deterministically. Clockwise and fan-order changes no
  longer paint through a transient combo-box state.

## 3.4.29.121 INTERN · 22.09.26

- Remove the delayed Qt callback that could race destruction of the RGB LED
  path editor and cause the recorded native segmentation fault.
- Preserve multi-fan zone shape, default declared fan banks to ring topology,
  add a per-component animation reverse switch and animate configured fans in
  the case preview.
- Pace all Direct devices from one bounded visual clock. Slow 1080-LED batches
  may reduce motion speed but no longer skip large animation phases, including
  when only some components have a spatial path.
- Keep rendering in the separate SDK worker and contain render failures per
  device so healthy devices and the GUI continue.
- Add a dedicated GPU navigation icon and an explicit two-step LACT fan test
  and permanent OHC takeover flow.

## 3.4.29.120 INTERN · 22.09.26

- Add exact-device GPU subprofiles containing the complete LACT configuration,
  fan/Zero-RPM state and 4K/8K stress-test choices. The selected GPU subprofile
  is part of a main OHC profile; imported or modified payloads remain safe
  drafts until locally verified for that GPU.
- Add optional per-profile startup activation through the existing LACT
  pending/confirm/revert transaction, power guard, health check and
  CoolerControl ownership boundary.
- Default the load test to a maximized KDE window with visible taskbar and add
  minimized/full-screen choices. When Gamescope is installed, 4K/8K is rendered
  internally and fitted to the monitor output instead of creating an oversized
  window.
- Add an AMD RX 9000/7000 and NVIDIA RTX 50/40 presentation catalog without
  guessed clocks, power or fan limits. Add horizontal/vertical mounting,
  original neutral GPU family artwork and a visibility-bound animated
  fan/curve preview.
- Redesign the real Qt GPU workspace to match the rendered dark control-deck
  direction, including live GPU/hotspot, fan RPM and power cards, deeper
  profile artwork panels and clearly separated primary safety actions.
- Import transparent PNG/WebP GPU artwork into a private 0600 OHC copy with
  strict size/type/alpha/path checks. Change/removal never touches the source.
- Extend all four localization catalogs to 1,722 unique shared messages and add
  regression coverage for profiles, artwork, PID-bound KWin presentation,
  Gamescope scaling and the complete offscreen UI.

## 3.4.29.119 INTERN · 22.09.26

- Fix the GPU fan preview crash caused by intersecting change-dictionary data
  directly with a set. Fan-mode and curve changes now enter the existing
  bounded LACT preview and response verification path.
- Stop and disconnect the case ARGB route inventory timer before its dialog
  accepts and opens the LED editor. Preserve the live topology preview's Qt
  ownership when moving it into the responsive component layout.
- Keep a private, bounded crash-context ring containing the final five minutes
  of already-redacted application log lines. After an incomplete exit, write
  `last-crash-context.log` and replay it into the next visible/session log.
  Enable all-thread Python tracebacks for fatal native signals and archive the
  prior trace on restart.

## 3.4.29.118 INTERN · 20.09.26

- Add a ten-second, user-rated GPU/support LED smoothness wizard to the
  existing motion editor. It changes bounded GPU approach, fade and tempo
  only after the user requests another candidate, and saves only after
  “Smooth · apply”.
- During calibration, black out other selected Direct zones and compatible
  native/NZXT lights. Restore the selected design when the wizard closes;
  abort on lost hardware ownership or missing confirmed frames.
- Keep the proven whole-device OpenRGB SDK path. A newly confirmed frame on
  both paired controllers starts each ten-second observation period.
- Use temporary blue/white on the paired strips during calibration. Pixel
  and fan-zone tests light only the chosen pixel/zone white and turn other
  selected OHC LEDs off, with guarded restoration after closing the dialog.

## 3.4.29.117 INTERN · 20.09.26

- Remove both zone-packet trial switches and the subsequent SDK zone-write
  path after the owner's `.116` log showed timeouts and an OpenRGB process
  crash when both trials were enabled. Saved trial settings are ignored.
- Preserve the previously working whole-device frame path, existing Direct
  preparation, LED counts, GPU/support motion controls and Case preview.
  Record that a full OHC restart restored the owner's RGB devices; optical
  fluidity remains a separate investigation.

## 3.4.29.116 INTERN · 20.09.26

- Restore complete OpenRGB device frames as the default for both GPU and
  support after the owner's `.115` log showed timeouts and an OpenRGB engine
  exit following the MSI zone-packet trial. Ignore the former saved trial key.
- Offer separate explicit GPU and support comparisons, both initially off.
  Disable an active trial on an SDK failure or managed-engine exit and log
  component, packet path and fallback. The read-only animated Case schematic
  remains unchanged.

## 3.4.29.115 INTERN · 20.09.26

- Compare OpenRGB's documented per-zone SDK packet with the previous whole-device
  frame path on an explicitly routed MSI GPU controller. The GPU dialog can
  return to the previous path; the log identifies the path used. SDK frame
  acknowledgements remain distinct from visible hardware updates.
- Animate configured GPU, support and RAM LEDs in the Case schematic while an
  OHC effect runs. A missing saved path uses a stylized row rather than
  inventing a physical LED direction; hidden views pause rendering.

## 3.4.29.114 INTERN · 20.09.26

- Apply GPU/support motion sliders live through the existing OpenRGB worker
  when a design is running; Cancel restores saved values, Save persists, and
  a Defaults button restores bounded draft values. The dialog now uses the
  actual paced frame time during active output instead of free-running at
  its own smooth 25-Hz preview clock.
- Add a separate GPU white peak and brighter low-level transitions, based on
  the owner's video of the saturated GPU strip. The support's light shape and
  the shared head clock stay unchanged. Do not silently fall back to the old
  sharp generic effect if GPU rendering fails.
- Open GPU control from the Case page and GPU component editor. A known single
  ARGB header goes directly to the LED editor; a distinct button changes its
  routing. Every related editor names its component. Draw saved physical LED
  paths as schematic points on case blocks without inferring missing paths.

## 3.4.29.113 INTERN · 20.09.26

- Widen the GPU strip's default approach/fade to 40%/38%, preserving the
  support strip's 32%/36% and all explicit saved adjustments.
- Use a fixed shared open-strip travel cycle so tuning either LED row changes
  only that row's light shape, not the paired row's motion phase. The preview
  and sole SDK worker calculate the same frame; optical validation remains.

## 3.4.29.112 INTERN · 20.09.26

- Add a live, per-LED GPU/support preview to the existing GPU routing dialog.
  Approach and fade out are separate per strip, while motion speed stays
  shared; cancelling leaves
  the saved effect untouched. Both rows use their configured physical counts.
- Pace GPU/support motion by dispatched OpenRGB frames. A delayed SDK write
  cannot skip several virtual frames when the next one is sent. Show measured
  per-controller transfer rates in the editor; optical output remains unreadable.
- Keep the two strips on one motion clock, preserve the serial SDK writer and
  include the motion settings in RGB profile data.

## 3.4.29.111 INTERN · 20.09.26

- Select the LACT GPU explicitly for both benchmark paths. The former
  `DRI_PRIME=1` routed vkmark to the integrated GPU on the owner's system;
  a bounded repeated 8K run reached 100% on the intended RX 9070 XT.
- Keep vkmark's actual GPU banner and exit details, align the scene duration
  with the selected test length and log GPU clock, power and throttling.
- Give a newly enabled LACT fan more time to spin up inside the automatic
  rollback window; require an observed RPM response before permanent save.
  Disabled fan profiles no longer show a stored target as active.
- Restrict OHC's default GPU power editor to LACT's device-reported stock
  limit. A higher limit needs a confirmed unlock and remains below LACT's
  reported maximum. Ten consecutive excessive-power samples stop an
  un-unlocked long test and request the matching OHC snapshot rollback.
- Soften the GPU/support moving-light front and tail with a wider cubic fade:
  upcoming LEDs glow earlier, adjacent brightness steps shrink and both
  strips retain the same motion clock and their separate real LED counts.

## 3.4.29.110 INTERN · 20.09.26

- Offer an 8K Phong-shaded vkmark load run with measured average/peak GPU
  utilization; insufficient load no longer appears as a passed test.
- Make the GPU fan test button execute LACT's bounded preview, with a
  validated static-speed mode alongside the existing five-point curve.
- Add separate input discard, OHC-snapshot restore and confirmed current
  LACT-profile reset actions. Allow firmware fan release after external
  LACT changes, without requiring an OHC snapshot.
- Add a LACT diagnostic tab with OHC action/reading history, bounded
  systemd journal retrieval and an explicit private local export.

## 3.4.29.109 INTERN · 19.09.26

- Enable the longer GPU load test for the currently active LACT values even
  when no OHC tuning profile has been saved. Newly installed vkmark is
  detected without an application restart.
- Clarify that unsaved tuning inputs are excluded. A current-value test
  writes no GPU configuration; matching OHC-saved profiles still support
  rollback after a detected fault.

## 3.4.29.108 INTERN · 19.09.26

- Put the optional vkmark installer beside the GPU tuning preview. When no
  supported graphics load helper is present, clicking the preview offers
  the confirmed Fedora package installation before any LACT write.
- Share installation completion and errors between the Tuning and Lasttest
  tabs. A successful install leaves the GPU profile unchanged and requires
  another explicit test click.

## 3.4.29.107 INTERN · 19.09.26

- Create and edit a five-point AMD GPU fan curve in OHC even when LACT has
  no existing fan profile. CoolerControl ownership checks and LACT's timed
  preview and explicit save remain required.
- Add a cancellable 15–120 second GPU load test for settings OHC has already
  confirmed. Monitor load, temperature and throttle reports; restore OHC's
  previous LACT snapshot after an observed fault. An aborted or low-load run
  is not reported as a successful test.
- Prefer optional vkmark's larger Vulkan scene over the small vkcube helper
  in Hardware Checker; offer a confirmed Fedora package installation from
  configured sources.

## 3.4.29.106 INTERN · 19.09.26

- Read LACT's live RDNA4 clock limits, enabling the GPU offset and memory
  clock controls even when those fields have not been saved in a GPU profile.
  Changes still require a bounded load preview, verified rollback and a
  separate permanent save.
- Check the originally owned TRCC daemon PID directly at shutdown. If it has
  already exited, another TRCC instance is left untouched and the completed
  release no longer appears as a failed shutdown.

## 3.4.29.105 INTERN · 19.09.26

- Ask KWin for the actual Wayland output of OHC's own window and move it to
  the selected primary output when KWin reports a mismatch; no permanent rule.
- Add confirmed, asynchronous AMD Overdrive preparation through LACT's local
  daemon, with clear restart guidance and unchanged GPU tuning gates.
- Fix repeated LCD gallery input-filter exceptions caused by a host field
  shadowing `QWidget.window()`; the live `.104` session logged this error.
- The window X now always keeps OHC running in the tray, or minimized in the
  taskbar without a tray. Only the tray context menu provides manual Quit;
  the File/header actions close the window instead.

## 3.4.29.104 INTERN · 19.09.26

- Keep LACT GPU measurements and hardware details visible before a GPU profile
  exists; prefer the dedicated GPU when first opening the page.
- Explain disabled AMD Overdrive and provide a direct LACT GUI button for the
  user's setup. Lock tuning until Overdrive and a saved baseline are present.
- Clarify that an inactive CoolerControl service does not claim the GPU fan,
  and treat a missing LACT fan profile as already released.

## 3.4.29.103 INTERN · 19.09.26

- Check LACT 0.10.1+ against installed RPM, Pacman or DEB package metadata;
  LACT 0.10.1 does not implement the previously queried `lact --version`.
- Finish a successful package installation whose daemon was not started,
  without needlessly enabling the Fedora COPR again.
- On Wayland, compare the mapped window surface with the requested output
  before trusting a potentially stale Qt global rectangle, then check once
  more shortly after mapping. Preserve a fixed monitor chosen in settings.

## 3.4.29.102 INTERN · 19.09.26

- Add a GPU page with LACT 0.10.1+ measurements, bounded tuning and fan trials,
  automatic rollback, a separate permanent confirmation and a saved per-GPU
  baseline for explicit later restoration.
- Recheck CoolerControl GPU-fan ownership before LACT writes, provide fan
  release/handoff controls, and keep GPU lighting with OpenRGB.
- Show OpenRGB-detected GPU lighting controllers in the GPU page, including
  compatible MSI I²C and ASUS Aura SMBus models without an external ARGB cable.
  Actual model modes and zones remain authoritative.
- Add an opt-in Fedora/Arch LACT installation path and an optional LACT/OpenRGB
  step in first-run setup; other distributions link to official packages.
- Track exact OHC-owned process identities through application lifetime,
  attempt bounded cleanup after unexpected exit and log the previous result
  when OHC starts again. Return a temporarily stopped CoolerControl service.
- Update four complete language catalogs, dependency version references and
  OpenRGB SDK regression coverage for protocol-6 servers negotiated at level 5.

## 3.4.29.101 INTERN · 19.09.26

- Diagnose am laufenden System: Der installierte `.98`-Fensterschluss wechselte
  um 16:56 in den Infobereich. Das spätere echte Beenden schloss OHC sauber,
  ließ aber den 1,3-GB-TRCC-Daemon nach `device disconnect` weiterlaufen.
- Stoppe beim geordneten Ende nach der Levita-Firmware-Rückgabe den
  nachweislich von OHC gestarteten TRCC-Daemon über dessen eigenen IPC-Befehl.
  Ein bereits beim OHC-Start vorhandener oder inzwischen ersetzter Daemon bleibt
  unangetastet.
- Verhindere, dass eine Abschalt-Rückgabe ohne laufenden Daemon durch
  `TRCC_DAEMON=1` unbeabsichtigt einen neuen startet.

## 3.4.29.100 INTERN · 19.09.26

- Let a direct GPU-test click perform its own initial inventory, then run the
  bounded graphics test. Add a Vulkan `vkcube` fallback and explain missing
  helpers. A link is judged under load only while the helper still runs.
- Give the Hardware Checker, case device list and temperature statistics a
  consistent adaptive table design; long mainboard names remain fully readable.
- Use the same compact twelve-segment temperature display in Overview, Cooling
  and Temperature Recording, with live CPU/GPU/coolant readings in the latter.
- Refine the 30-LED GPU strip after inspecting the owner-supplied video: keep
  the blue base visible and narrow the traveling white highlight. LED counts,
  physical routing and hardware ownership stay governed by existing settings.


## 3.4.29.99 INTERN

- Make Display Effects save its selection as the canonical Levita startup
  design instead of only staging it for a later profile update.
- Treat minimize-to-tray as a saved minimization preference while every real
  window/taskbar Close performs ordered cleanup and exits.
- Unload hidden Qt/FFmpeg video sources and clear their retained frame buffers;
  reload only when a preview becomes visible again.
- Debounce idle Python collection and optional glibc heap trimming after page
  switches/minimization, without a periodic CPU task or private-data swapping.
- Add regressions for canonical startup persistence, close/minimize separation,
  decoder release and optional idle heap reclaim.

## 3.4.29.98 INTERN

- Persist the first explicit "keep running in the tray" close choice and reuse
  it without showing the close dialog again.
- Migrate an existing explicit `.97` tray choice from the bounded private
  shutdown journal when the new setting has not been created yet.
- Keep explicit application/tray Quit, Cancel, disabled tray mode and desktop
  session shutdown on their existing separate paths.
- Add regressions proving the second close no longer prompts and that only an
  actual recorded tray choice qualifies for migration.

## 3.4.29.97 INTERN

- Make window-manager close events unambiguous when tray continuation is enabled:
  Quit, keep running in the tray, or Cancel.
- Route the explicit Quit choice through the existing ordered hardware restore,
  owned-process cleanup and direct Qt exit without waiting for another close event.
- Add a bounded, read-only interpreter for the private shutdown journal. It
  distinguishes clean exit, tray continuation, cancellation, incomplete exit
  and a parent process still alive after the observer deadline.
- Show the interpreted state in System Status and include the last unfinished
  shutdown phase when one can be proven from paired phase records.
- Preserve the existing tray preference, session-shutdown path, restoration
  ordering and rule that process exit is not physical hardware confirmation.

## 3.4.29.96 INTERN

- Add one-click Hardware Checker page for CPU model, SMT/Hyper-Threading,
  mainboard, PCIe GPUs, NVMe SSDs and RAM.
- Run ordinary inventory in a bounded read-only helper process; use one fixed
  Polkit/dmidecode request for RAM DMI without receiving or storing passwords.
- Compare current and reported maximum PCIe generation/lanes with pass, warning,
  failure and unavailable states; avoid false GPU failures from idle downshifts.
- Add a bounded explicit glmark2 GPU-link load test; no clocks, fans, voltage,
  firmware or BIOS settings are changed. SSD inspection performs no write test.
- Support manual RAM model and expected MT/s when firmware data is incomplete.
- Hardware Checker 1.0 with CPU virtualization state; 1,530 complete DE/EN/ES/FR messages.

## 3.4.29.95 INTERN

- Remove permanent Light Band outline/idle highlight stripes and abrupt faint glow.
- Regenerate eight loops at real 4800×2160, downsample to native 1600×720, CRF 10.
- Animate selected LCD layout videos without hover, only in exposed viewports.
- Default effects preview to the last confirmed display composition; exploration is transient.
- Clear selection on outside click/Escape/button/page hide; preserve active catalog effects.
- Disable applying/staging an unselected effect; preserve saved defaults and hardware ownership.
- Reserve gallery geometry and avoid rebuilding scenes for unchanged/empty motion frames.
- Refresh current design category, variant, details and credits on live language changes.
- Display Effects 1.11; 1,483 complete DE/EN/ES/FR messages.


## 3.4.29.94 INTERN

- Wider case properties; component/fan and LED-path fields reflow into columns or tabs.
- Remove inner form scrollbars; retain drafts, validation and Save/Cancel visibility.
- Refresh late tab captions on live language changes.
- Broader quintic GPU/support spinner/comet fades, shared paired sampling at real LED counts.
- PC Case Profiles 1.5 / RGB Studio 1.15; 1,483 atomic DE/EN/ES/FR messages.
- Preserve physical counts, paths, PWM calibration, SDK ownership and existing LCD recovery.


## 3.4.29.93 INTERN

- One explicit Levita default wins over automatic profiles; preview browsing cannot overwrite it.
- Explicit save/apply stages profile media, and superseded startup retries expire.
- Daemon recovery replays accepted prepared commands instead of the current preview.
- Stable large videos avoid periodic 1-GiB resets; growth, real pressure and 3-GiB emergency remain protected.
- Cache identity includes effective config/source assets; profile motion/FPS persist completely.
- LCD Runtime 1.1; 1,482 atomic DE/EN/ES/FR messages. No new hardware write protocol.

## 3.4.29.92 INTERN

- Keep static LCD designs alive through the existing daemon IPC ticker, alongside videos.
- Observe confirmed transfers and finite command deadlines; detect SDK ready/frame stalls.
- Recover concrete clients with bounded backoff and preserve native backend quarantine.
- Private module journal retains PID, exit/request/runtime, failure details and retry decisions.
- Read-only game detection outside Qt; sensor restart and LCD transfer age in System Status.
- Process Runtime 1.1 / LCD Runtime 1.0; 1,481 atomic DE/EN/ES/FR messages.

## 3.4.29.91 INTERN

- First staged supervised read-only sensor process with shared fresh snapshots;
  retain fail-safe cooling and existing hardware ownership.
- Move pure RGB math into the existing bounded SDK worker; keep effects, paths,
  paired GPU/support clocks and transport target unchanged.
- Activate inline case properties from single-click side labels without moving.
- Private exit journal, delayed stack trace and bounded independent parent
  observation; stop remaining owned processes after restore, then direct Qt exit.
- In-page actual process/sensor status, per-process CPU/RSS and 1,476 atomic
  language messages. Autonomous cooling/core and further LCD migration deferred
  to subsequent validated stages; no installation or new hardware write path.

## 3.4.29.90 INTERN

- Portion LCD card construction, reuse on resize and prepare after three idle
  seconds without hidden playback or additional hardware workers.
- Isolate precautionary RAM reclaim from other RGB clocks; drain the last
  affected frame and invalidate stale leases without reapplying the whole effect.
- Embed case component, ARGB route/count/path/test, GPU and PWM forms in one
  right-side inspector; cancel and async-generation guards preserve intent.
- Persist requested cooling startup independently of acquired control; use fresh
  fail-closed owner results and retain quiet/individual calibrated profiles.
- Idempotent explicit tray quit queues Qt exit after isolated cleanup. Restrict
  overlays to left navigation, delete finished animations, retain live text.
- UI Performance 1.1, PC Case Profiles 1.3, RGB Studio 1.13, Cooling State 1.0;
  1,467 complete DE/EN/ES/FR messages. Carry all .89 features; no new hardware
  write path or optical/native-desktop validation claim.

## 3.4.29.89 INTERN

- Smooth explicit GPU-strip spinner/comet heads with open-end fade, count-aware
  rate, wider smooth heads/tails and bounded temporal/area sampling.
- Optionally share GPU effect/clock/normalized progress with the explicitly
  wired support block. Preserve 30 GPU / 12 support LEDs independently;
  require selected, conflict-free, unambiguous existing routes. Missing or ring
  partners remain independent; never auto-select or enable hardware writes.
- Add localized GPU-setup synchronization checkbox, commit-only persistence and
  complete-package retention. Log strip renderer/count/shared clock at effect
  startup, not every frame. Other zones and 25-Hz sole-writer transport unchanged.
- RGB Studio 1.12; 1,448 atomic DE/EN/ES/FR messages. Local internal packaging;
  no physical-FPS, firmware-crash-fix or live-hardware compatibility claim.

## 3.4.29.88 INTERN

- Add reversed fan-ring chain order with top/left or bottom/right physical
  LED 1, independent of per-ring clockwise order. Preview, saved physical paths,
  complete ZIP packages and all spatial effect samplers share the declaration.
  Counts, single-pixel tests and existing unmapped playback remain unchanged.
- Harden complete imports: only exported media/theme/font asset extensions,
  no file/directory conflicts or duplicate directories; validate before staging.
- Quiesce owned timers and restart intentions before profile-worker cancellation;
  a cancellation failure is logged without skipping later shutdown phases.
- Carry corrected personal wiring, shared case/PWM mapping, count editing/testing,
  custom fan library and complete profile packages from .87. RGB Studio 1.11;
  1,446 complete DE/EN/ES/FR messages. Internal local RPM only.

## 3.4.29.87 INTERN

- Add a complete private ZIP export/import in Profiles: typed app settings,
  all user profiles plus current full profile, case positions/scales, RGB/PWM
  assignments, custom fan library and associated media/themes/fonts/LCD store.
  Copy/hash work runs in an owned background worker; strict staged import
  validates paths, types and checksums, relocates nested paths and restores
  only on the next startup with rollback. Reconfirm hardware automation/PWM.
  Existing simple profile JSON exchange remains available.
- Declare physical LED order in the header editor's LED-path tab: strip
  start/end, ring count/start/clockwise order and eight case-space directions,
  including diagonals. Preserve actual physical pixel-test numbering and
  existing local playback when no spatial mapping is configured.

- Correct the owner's personal Airgoo topology: A1 front 2×8, B7 bottom
  reverse intake 3×8, B8 rear exhaust 1×8, A8 Thermalright radiator 3×10,
  B6 GPU support 1×12. Preserve geometry, PWM and unrelated channels.
- Apply personal corrections once, pin complete saved zone counts against
  design snapshots and stop inventory refresh forcing B6 back to 24 LEDs.
- Add a bounded reusable custom manufacturer/model/color/LED fan library,
  selectable in block and existing zone editors, with explicit model save.
- RGB Studio 1.10; Profile Bundle 1.0; 1,442 complete DE/EN/ES/FR messages.
  No new driver, physical LED detection or hardware write path. Local internal
  packaging only; no installation or public publishing.

## 3.4.29.86 INTERN

- Stop the owned privileged fan-helper through existing stdin EOF before
  bounded signal fallbacks; permission denial no longer aborts application exit.
- Isolate orderly cleanup phases, stop owned timers/restart intentions and
  suppress backend completion callbacks while quitting. Preserve close-to-tray.
- Clear the clean LCD marker only after successful restoration, not before it.
- Retain reported offline controller choices without bypassing actual device
  ownership/quarantine. Refresh open selectors after explicit owned-engine
  recovery; invalidate stale discovery generations and clear busy/reinit state.
- Pause background inventory and automatic effect application during a header
  preview. Prevent overlapping tests; refuse test writes after engine failure.
- Restore the selected design once on editor close/save after completed tests,
  never across changed intent, disabled writes, foreign ownership or shutdown.
- Add bounded per-block brand/model/black-white/LED declarations. The owner's
  TZMRIT ASIN reference has eight addressable LEDs per fan; two fans suggest 16
  in the existing bounded header editor, never overwrite unrelated headers.
- RGB Studio 1.8; Application Shutdown 1.0; 1,394 complete DE/EN/ES/FR entries.
  These app-side guards do not establish a fix for a native OpenRGB crash.

## 3.4.29.85 INTERN

- Fix unassigned case blocks stopping at “No ARGB header assigned”: offer
  direct controller/reported-zone selection without drag/drop or recursion.
- Expose LED-count editing and individual-pixel testing in that selection;
  reuse the existing bounded SDK editor, ownership guards and serial queue.
- Persist bounded stable block/header bindings separately from effect and
  position snapshots. Revalidate inventory; missing ports never reroute.
- Allow explicit rebinding/unassignment without erasing global LED counts or
  changing PWM, groups or geometry. GPU blocks retain one GPU-route authority.
- RGB Studio 1.7; PC Case Profiles 1.2. Reuse all 1,390 DE/EN/ES/FR entries.

## 3.4.29.84 INTERN

- Add bounded visual-only corner resizing and a numerical preview-size editor;
  preserve it in settings, case/design/full profiles, moves and fan splitting.
- Keep synchronized or independent cooling scales without duplicating or
  changing LED/PWM hardware topology. Escape/hide cancels preview gestures.
- Fit proportional render/hit geometry within cases; improve explicit mounting
  arrangements and add original 2.5-D projected edges/component shadows.
- Prefer reported SYS_FAN connector names, retaining internal driver identities
  in technical details without renumbering mappings or enabling regulation.
- Open the component editor for double-clicked blocks without RGB assignments.
- Add side callouts with configured LEDs and physical fan connectors, reserving
  readable side gutters; unknown values show — and multi-zone lengths stay
  separate. Read-only display hints do not modify electrical routing.
- Default RGB selection to all writable devices; add an explicit persisted
  individual mode with checkable inventory rows. Locked devices stay excluded.
- PC Case Profiles 1.2; RGB Studio 1.6; 1,390 complete language entries.

## 3.4.29.83 INTERN

- Add a central Case page with shared RGB/LED/PWM mapping, direct block/header editing and optional independent cooling positions without a second hardware topology.
- Extend bounded header/pixel testing to every reported Direct ARGB zone; protect explicit manual counts from design profiles and log declared/server sizes, offsets and SDK results without claiming physical readback.
- Render all configured zones independently with count-adaptive sampling and soft spinner/comet, colour and sparkle transitions. Keep intentional flashes and the existing 25-Hz sole-writer transport target.
- Add 30 detailed original case illustrations, PWM badges and a full-width readable transfer panel. No manufacturer photos or inferred electrical topology.
- PC Case Profiles 1.1; RGB Studio 1.5; 1,387 shared DE/EN/ES/FR messages. Owner visually confirms 30 personal Sapphire LEDs on MSI JARGB 1; new effect fluidity remains optically unverified. Owner authorizes the local RPM build and standing automatic release-backup rotation without repeated questions, retaining the two newest complete versions (.82/.83).

## 3.4.29.82 INTERN

- Route external GPU ARGB by stable controller ID and reported zone, not controller alone. Render the routed strip with its own effect coordinates; preserve independent lengths and effects for other controller zones.
- Add a single-header LED-count editor with one GPU = one device and a bounded explicit single-pixel visual test. Keep other saved headers unchanged; do not guess physical GPU LED counts.
- Retain current physical GPU routes and manual header counts across old/new RGB design profiles and startup. Include route/size changes in effect-request deduplication.
- Migrate only the owner's confirmed personal Sapphire RX 9070 XT wiring to MSI JARGB 1 once. Remove the accidental three-device multiplier from the owner's 80/90 test declaration; preserve explicit choices and unrelated layouts.
- RGB Studio 1.4; DE/EN/ES/FR complete at 1,381 entries with mechanically compacted data-only catalogs. Internal packages only; optical hardware validation remains pending.

## 3.4.29.81 INTERN

- Remove automatic External Control selection for Sapphire/native-only GPU designs. Match the actually reported Rainbow Wave, Runway, Serial and Spectrum Cycle modes without inventing Direct LEDs.
- Add GPU setup from the PC component editor and native controls. Explicitly associate the physically connected ARGB controller and delegate manual LED counts to the existing bounded zone editor.
- Save stable-ID GPU routing with settings and RGB profiles. Existing profiles default to native effects; missing or unselected Direct sources cannot implicitly activate External Control. Preserve the personal PC layout and other LED counts.
- Keep DE/EN/ES/FR complete at 1,372 shared entries. Internal packages and rolling backup only; hardware-free checks do not establish optical compatibility.

## 3.4.29.80 INTERN

- Replace the NCT6687 setup sheet with a status-gated step-by-step wizard. Parse affirmative `mokutil --test-key` output even when an unrelated kernel-keyring warning produces exit code 1, run read-only checks asynchronously and enable only the fixed action needed for the current step.
- Simplify case-fan cards to a friendly System Fan name plus one separate `PWM N` channel caption. Add a confirmed all-assignment reset that stops active OHC control, returns channels to firmware/BIOS and retains saved curves.
- Let the fan-mapping wizard return directly to the next unassigned or unconfirmed channel from its summary page so every fan can be processed in sequence.
- Hide unavailable coolant status and coolant curve sources for Thermalright Levita. Give the safe PWM lower-limit warning its own full-width, high-contrast panel.
- Open the assigned RGB device from a double-clicked PC-view component and launch LED-zone editing for Direct devices. For the supplied Sapphire GPU, preserve the honest one-logical-LED hardware-mode boundary reported by OpenRGB instead of inventing addressable LEDs.
- Treat KDE/Wayland's visible StatusNotifier tray icon as reachable even when Qt reports no icon rectangle. The X button hides OHC from the task manager again; explicit Quit remains the only close path that performs hardware shutdown.
- Keep German, English, Spanish and French complete with 1,365 shared message entries. Internal build only; no GitHub push, tag or public release.

## 3.4.29.79 INTERN

- Add application-wide lightweight page transitions with fade, slide and glow choices. They animate only a transparent overlay, never capture or double-render a page, and stop as soon as the target page is hidden.
- Add a central bounded SSD cache with disabled, 0.5, 1, 2 and 4 GiB presets. LCD/Wallpaper catalogs and scaled previews use it; low-priority maintenance removes the oldest regenerable files first without touching originals.
- Defer multi-second ENE-DRAM recovery work while page navigation is active and suppress detailed startup diagnostics for ordinary hidden Qt surfaces.
- Keep the case-fan automatic-control button synchronized with the real persisted controller state, including its full blue active presentation and rollback after an ownership failure.
- Replace the static NCT6687 setup text with a localized staged assistant for the driver, DKMS certificate, fixed `mokutil --import /var/lib/dkms/mok.pub` terminal action, physical MOK Manager enrollment and post-restart module load. Passwords remain exclusively in the terminal/UEFI and Secure Boot is never disabled or bypassed.
- Complete the localized Wallpaper Engine setup flow with an explicit KDE/Qt D-Bus helper-package step from configured repositories, separate from the SHA256-verified CaptSilver plugin flow.
- Fix the supplied close-button regression: with close-to-tray enabled, transiently invalid tray geometry now minimizes visibly and leaves LCD/RGB/cooling running. Explicit exit still performs orderly hardware cleanup and always terminates the process.
- Extend the close target to 48×42 pixels through the top-right corner and keep window-resize handling from stealing that corner click.
- Keep German, English, Spanish and French complete with 1,353 shared message IDs. Internal build only; no GitHub push, tag or public release.

## 3.4.29.78 INTERN

- Correct the RGB gallery's inherited painter-font growth, use fixed pixel sizes, elide long titles and reserve the favourite area so lower cards no longer become oversized or overlap.
- Reorder RGB Studio around top actions, full-width live preview, a separated design gallery, the PC layout and lower device/effect details; render the visual preview with at least 24 LEDs without changing physical device writes.
- Reuse Display Effects cards and cached posters during responsive relayout, defer playback until the page shell has painted, cap local composition at 20 FPS and keep bundled video playback active only while visible.
- Extend visibility-bound presentation work across menus: pause LCD movies and the animated app background outside their visible surface, stop Thermalright preview timers and thumbnail workers outside the actual gallery viewport, load Wallpaper thumbnails only for visible cards and stop the optional desktop-shell clock while hidden. Hardware output, monitoring and cooling loops remain independent.
- Close normally whenever the configured tray icon is not actually reachable, preventing an invisible surviving process; the existing single-instance activation remains available when the tray is valid.
- Keep German, English, Spanish and French complete with 1,292 shared message IDs. Internal build only; no GitHub push, tag or public release.

## 3.4.29.77 INTERN

- Stop high-frequency RGB and Levita preview painting whenever the corresponding page is hidden; defer hidden Levita gallery-card and thumbnail work until the LCD page is opened, and reduce idle GameMode process polling from three to ten seconds.
- Recognize the reproduced TRCC “interface is in use by another process” failure as recoverable. Try the existing IPC release first and, only if it fails, signal an exactly revalidated same-user `trcc daemon`; add an explicit “Display freigeben” action for a deeply stuck daemon.
- Restore the saved motherboard/case-fan master state and global curve template visibly after startup, including the blue active state of both automatic control and the chosen preset.
- Keep the main window surface suppressed until its requested normal or maximized state has been applied, so the first visible frame already matches the saved startup mode.
- Summarize hidden Qt helper surfaces in the startup window snapshot instead of synchronously writing roughly 160 detailed entries into both persistent and visible logs.
- Recheck official external underpinnings: retain current stable TRCC Linux 9.9.12, OpenLinkHub 0.9.1 and liquidctl 1.16.0; document OpenRGB 1.0-rc3.1 SDK-5 compatibility, update the Qt/PySide reference to 6.11.2 and retain security-fixed Pillow 12.3.0 as the image baseline without silently replacing system packages.
- Keep German, English, Spanish and French complete with 1,292 shared message IDs. Internal build only; no GitHub push, tag or public release.

## 3.4.29.76 INTERN

- Diagnose the supplied long-running Levita failure as a TRCC daemon memory leak: the kernel OOM-killed it at roughly 15.5 GB RSS, leaving a newly spawned daemon holding USB while the old video ticker had lost IPC.
- Monitor only the exact current-user `trcc daemon` process once per minute and, at 1 GiB RSS, stop the ticker, release the daemon through its IPC kill command and reapply the selected design through the existing sole-writer queue.
- Use the same bounded, five-minute-cooled recovery immediately when the video ticker reports a lost daemon connection; do not signal foreign processes or open a second USB owner.
- Replace the visible 10,000-character log truncation with 60-minute application/hardware ring buffers and hard 30,000-line/4-MiB safety caps.
- Persist redacted runtime and uncaught-exception failures in a private bounded `errors.log`; include its latest 400 lines in explicit diagnostic collections.
- Keep German, English, Spanish and French complete with 1,291 shared message IDs. Internal build only; no GitHub push, tag or public release.

## 3.4.29.75 INTERN

- Guard the temporary normal mapping used during startup so it cannot be saved as a user window-state change; delayed startup profiles no longer apply stored window geometry or trigger a second placement pass.
- Reflow LCD Layer-1 backgrounds, Layer-2 data surfaces, free effect cards and Display Effects sensor layouts from their actual viewport width, distributing up to twelve cards per row while preserving selection.
- Add a non-destructive LCD media manager for up to 32 folders and 500 individual images/videos, per-item display aliases and exclusions. It never renames, moves or deletes source files and does not bundle external TRCC media.
- Present TRCC catalog IDs with readable category names and clearer OHC cyber/layout names while keeping stable source paths and profile references.
- Show local date plus time on temperature chart axes, hover details and the readings table; add resizable split views and explicit CSV/JSON exports for a selected absolute range and any recorded sensor set.
- Continue recording all available read-only hwmon temperatures regardless of which series are currently visible. No background report file is created and no tuning/hardware ownership is taken.
- Keep German, English, Spanish and French complete with 1,291 shared message IDs. Internal build only; no GitHub push, tag or public release.

## 3.4.29.74 INTERN

- Map the main window in its normal state on the selected screen before applying a requested maximized state in the following Qt event-loop cycle.
- Verify the screen actually chosen by KWin after the first Wayland mapping and correct a Discover/start-token override only when the observed screen differs from the saved target.
- Record the post-mapping screen and final geometry so future multi-monitor diagnostics distinguish the compositor result from OHC's requested target.
- Show a minimized tray window before applying its target screen and run the same delayed confirmation after tray activation.
- Keep all hardware, profile and display paths unchanged. Internal build only; no GitHub push, tag or public release.

## 3.4.29.73 INTERN

- Make the tray restore action cooler-model aware: Thermalright Levita releases the single TRCC owner and returns to the built-in firmware screen, while NZXT Kraken retains its liquid-temperature action.
- Add prominent Thermalright original-display controls to the LCD page and Display Effects without creating another USB owner; test mode remains strictly write-free and an already-detached daemon is treated idempotently.
- Make the tray Quit action final on its first click by bypassing close-to-tray only for an explicit quit and running the existing cleanup path once.
- Re-render all eight original OHC Light Bands from 3200×1440 supersampled sources and encode the native 1600×720 output at higher quality for sharper LCD playback.
- Keep German, English, Spanish and French complete with 1,277 shared message IDs. Internal build only; no GitHub push, tag or public release.

## 3.4.29.72 INTERN

- Move Spectrum Ring, Neon Double Arc, Prism Segments and Aurora Radar animation exclusively into editable Layer 2, each with an enabled-by-default on/off control and original glow, particle and motion rendering.
- Compose a chosen Layer-1 background and animated decoration locally into one validated cached 1600×720 stream beneath the live data; the existing TRCC daemon remains the sole USB owner.
- Separate preview FPS from physical LCD FPS, retain 15 FPS as the default, and expose 60 LCD FPS only through an explicit experimental Settings opt-in with automatic 60→30→20→15 fallback.
- Detect games conservatively through Feral GameMode, Gamescope, an explicit process allow-list or manual mode; do not infer games from system load or inspect arbitrary Wayland windows.
- Restore the real normal/maximized main-window state before first display and clear every frame-resize cursor on leave, hide, close, deactivation and state change.
- Remove the obsolete Layer-1 Spectrum Ring catalog entry and automatic Layer-1/Layer-2 coupling; keep selection/profile staging and all hardware ownership boundaries unchanged.
- Keep German, English, Spanish and French complete with 1,268 shared message IDs. Internal build only; no GitHub push, tag or public release.

## 3.4.29.71 INTERN

- Replace the hidden Layer-1 design combo with a graphical preview-card gallery while retaining category/colour filters and visible creator, original-source and licence links.
- Add the original deterministic OHC Spectrum Ring loop and automatically pair it with the matching editable live-data layout; no reference frame, manufacturer logo or copied product geometry is included.
- Polish original OHC Layer-2 themes with consistent local DejaVu typography, compact glass clock frames and a deliberately subtle static ring beneath the moving design.
- List the dynamic primary screen and every fixed connector in Settings, and place maximized windows normally on the requested output before re-maximizing to prevent KWin restoring the old monitor.
- Rename the owner's eight cyber images and retained high-quality corridor video descriptively; move the two lower-quality duplicate encodes to a recoverable folder outside the scanned library.
- Keep profile-update staging, the single TRCC queue and every cooling/hardware ownership boundary unchanged; DE/EN/ES/FR contain 1,250 shared message IDs. Internal build only; no GitHub push, tag or public release.

## 3.4.29.70 INTERN

- Add four original editable rainbow telemetry layouts: Spectrum Ring, Neon Double Arc, Prism Segments and Aurora Radar, with no manufacturer logo or copied product artwork.
- Extend the layer-2 editor to manage up to twelve custom text elements with text, locally installed font, size, colour, visibility and free position.
- Stage custom fonts and text through a private validated native theme while preserving the existing single TRCC queue and hardware ownership boundary.
- Fix the Levita canvas at 880×396 (the exact 1600:720 ratio) so expanding, collapsing, switching or scrolling adjacent controls cannot resize the preview.
- Record the non-destructive multi-folder and individual-file LCD Design Manager as committed work for one of the next two or three versions.
- Keep German, English, Spanish and French complete with 1,226 shared message IDs. Internal build only; no GitHub push, tag or public release.

## 3.4.29.69 INTERN

- Add synchronized browser-like tabs for `Display & layout` and `Display effects` to both LCD child pages while keeping the existing expandable sidebar.
- Introduce reusable Section Tabs 1.0 so future multi-page sections use the same stable page-ID navigation pattern.
- Make Display Effects 1.7 mirror an active bundled Levita medium through its exact validated path, including category, design and colour variant.
- Add the original, reproducibly rendered OHC Light Ribbons design as eight seamless 1600×720 directional variants; no reference-video frames, cooler geometry or product logo are included.
- Block user-change signals during synchronization; opening the page does not stage a profile or call the TRCC/hardware path.
- Keep German, English, Spanish and French complete with 1,220 shared message IDs. Internal build only; no GitHub push, tag or public release.

## 3.4.29.68 INTERN

- Expose Cooling as an expandable sidebar section with fixed `Control & profiles` and `Temperature recording` child entries, matching the established LCD navigation.
- Synchronize sidebar selection and the internal Cooling view in both directions and preserve both children through navigation customization/reset.
- Confirm from the supplied log and installed RPM query that 3.4.29.67 was running; the recorder existed but was insufficiently discoverable. No sensor, cooling or hardware-write path changed.

## 3.4.29.67 INTERN

- Added a dedicated Cooling temperature recorder for all plausible read-only Linux-hwmon sources, with group/series filters, long session windows, hover values and current/minimum/maximum statistics.
- Added conservative model-aware Levita PWM floors (50% pump, 25% radiator) at every control and final-write boundary because Thermalright publishes maximum RPM but no minimum duty.
- Fixed the profile table shrinking after update, preserved selection, exposed stored content in a tree and added freely combinable profile sections.
- Kept sensor sampling strictly read-only so monitoring does not take GPU/CPU tuning ownership from Open Radeon Control Center or other tools.

## 3.4.29.66 INTERN

- Replace the ambiguous manual state after Quiet/Balanced/Performance with an explicit fixed-profile state. Pump and radiator values remain fixed and case fans continue receiving the matching curve template; no cooling policy or duty value changed.
- Add Hardware Backends 1.0 with persisted, fail-closed Automatic/TRCC Linux and Automatic/OHC Linux-hwmon choices. Native Levita and CoolerControl adapters are visible but disabled until a validated implementation exists.
- Add Temperature History 1.0 to Overview: selectable CPU, GPU and genuine coolant series, 5/15/60-minute or full-session windows, and an interactive hover cursor with timestamp and readings.
- Keep at most one hour/1,800 validated readings in memory only. No telemetry is written to disk and no coolant value is synthesized for Levita.
- Extend German, English, Spanish and French atomically to 1,182 stable messages; preserve calibration, CoolerControl ownership, watchdog, firmware return and all existing transport boundaries. Internal build only; no GitHub push, tag or public release.

## 3.4.29.65 INTERN

- Compare the photographed application preview with the physical 1600×720 Levita output and isolate the mismatch to TRCC's wider/taller live-value font rather than block positions.
- Add an automatic per-value TRCC safety calculation using the configured text and font size with 22 percent width and 12 percent height reserves.
- Regenerate all three Nebula Drift presets; depending on the value, their frames are approximately 16–18 percent wider and 10–12 percent taller.
- Preserve the faint translucent artwork, video visibility, live-data definitions, positions, single-owner TRCC queue and all hardware-write paths. Internal build only; no GitHub push, tag or public release.

## 3.4.29.64 INTERN

- Restore the original faint RGBA Nebula Drift artwork so the selected Layer-1 video remains visible beneath the complete data surface.
- Replace the broad opaque clock and metric cards with compact dark pills sized only around each live value.
- Bundle three editable presets with different data densities: Minimal, System and Performance.
- Composite the gallery previews over a bundled landscape thumbnail to make the actual two-layer result visible before applying it.
- Add alpha/transparency, theme discovery and distinct metric-set regressions. Preserve the single-owner TRCC queue, display transfer, cooling curves and every hardware-write path. Internal build only; no GitHub push, tag or public release.

## 3.4.29.63 INTERN

- Replace the ambiguous motherboard/case-fan card state captions with explicit next actions: “Automatik einschalten” while inactive and “Automatik ausschalten” while active.
- Update German, English, Spanish and French together without changing the existing 1,151 stable message IDs.
- Add an offscreen regression that toggles a simulated calibrated channel in both directions and verifies the matching action label after each rebuild.
- Preserve every curve, calibration, channel assignment, ownership boundary, watchdog, firmware-return rule and hardware write path.
- Add dark translucent clock/metric cards to Nebula Drift while preserving its original source background, and separate the project-owned Orbit, Aqua Pulse, Horizon Glass and Split Core layouts into orbital, wave, glass-bar and angular visual styles.
- Make the Layer-2 renderer selectively reproducible per theme and refresh all generated previews with a real scalable Noto/DejaVu font instead of an undersized bitmap fallback.
- Correct the release-backup note lookup to the canonical `docs/releases/` directory. Internal build only; no GitHub push, tag or public release.

## 3.4.29.62 INTERN

- Raise Display Effects to 1.6 and add 15 locally bundled, silent 1600×720 videos in Space & Earth, Landscape & sky, and Water & underwater; retain the five abstract designs and add a four-category filter.
- Review every selected excerpt for visible people, title cards and technical overlays. The rejected Saturn-tech, artificial 3D galaxy fly-through and Grand Canyon people clips are not included.
- Add five editable Layer-2 themes derived from individually named CC0 Kenney components and four original OHC Layer-2 themes, each with live metric blocks and notch-safe geometry.
- Preserve strict packaged-media validation, profile-start staging and the sole existing Levita/TRCC hardware writer; the new catalog performs no runtime network access.
- Extend German, English, Spanish and French together to 1,151 stable messages and document each media source, creator and license. Internal build only; no GitHub push, tag or public release.

## 3.4.29.61 INTERN

- Split application styling into versioned UI Themes 1.0 with independent light/dark definitions, an allowlisted registry and a shared controller suitable for future theme additions.
- Rework light-mode semantic surfaces so cards, navigation, status panels, editor overlays and Layer-2 choices retain readable contrast without dark-only fragments.
- Raise Display Effects to 1.5 and decode the selected validated bundled MP4 in the large local preview. Dark Smoke begins at its visible three-second motion point.
- Pause preview decoding on Pause, page changes, window minimization/hiding and controlled shutdown; keep the existing Layer-2 composition and sole Levita/TRCC hardware hand-off.
- Selecting a library effect now automatically stages its media and Layer 2 for the next LCD/full profile update; generated effects are staged once their video exists, and a dedicated button plus translated hint expose the same workflow. The chosen startup profile restores that Levita design before the existing delayed start, while selection alone remains hardware-write-free.
- Add Qt Multimedia to GUI dependency detection and Debian package metadata. Internal build only; no GitHub push, tag or public release.

## 3.4.29.60 INTERN

- Reject a maximized monitor work-area rectangle as normal window geometry, persist the floating rectangle separately, clamp every edge to the selected monitor and adapt minimum bounds on small logical HiDPI desktops.
- Add a 60–95% windowed-size preference and a `Ctrl+Alt+0` safe-fit action that restores accessible title-bar controls without changing KDE monitor configuration.
- Rebuild the PC/case area as a compact two-column workspace with model-family OHC silhouettes, selectable AIO/air visualization, direct airflow reversal and fan-block splitting into individually draggable objects.
- Remove the personal Retro 360 Amazon action while retaining each manufacturer source; migrate Devices and Effects to collapsed once for existing installations.

## 3.4.29.59 INTERN

- Add an OHC-drawn accessible title bar whose move and edge-resize operations are delegated to Qt/KWin on Wayland and X11; preserve maximize/restore, tray-aware close behavior and minimized-autostart suppression.
- Nest Display & Layout and Display Effects below LCD and collapse the subtree when another main area is selected.
- Make RGB Studio compact by default, show four suggestions, add persistent favorites and categorized full-library views, and append Nebula Pulse, Liquid Metal, Ember Flow and Arctic Halo without changing saved older indices.
- Add PC Case Profiles 1.0 with 30 original schematic templates, an exact Thermaltake Retro 360 TG default, official/Amazon links and bounded local custom profiles. No manufacturer artwork or additional hardware writer is included.
- Extend German, English, Spanish and French together. Internal build only; no GitHub push, tag or public release.

## 3.4.29.58 INTERN

- Fix the supplied-trace reproduction where every Display Effects library Apply click ended before any `THERMALRIGHT` command: packaged assets were incorrectly sent through the generated-cache-only path check.
- Add Display Effects 1.3 with a shared strict handoff validator and separate explicit roots for generated cache videos and packaged offline library videos. Symlinks, outside paths and non-MP4 files remain rejected.
- Route bundled choices through the dedicated Levita Studio entry point, retain the existing Layer-2/apply/USB ownership path, and log both accepted selections and pre-apply failures.
- Update the renamed smoke worker imports so procedural rendering remains available under the sole current module folder. Internal build only; no GitHub push, tag or public release.

## 3.4.29.57 INTERN

- Confirm from the supplied trace that the daemon-side Levita `display play` ticker ended unexpectedly after a long run and left the selected display effect frozen as a still frame.
- Restart only that daemon IPC ticker with bounded 1/2/4-second backoff. A run lasting at least 30 seconds renews the retry budget; three rapid failures stop without an infinite loop, USB reconnect or second hardware owner.
- Retain the last bounded, privacy-filtered TRCC stdout/stderr tail in the status log so a future backend exit has actionable evidence instead of discarded output.
- Raise the Levita data-surface/runtime module to 1.5 and add pure restart-policy plus UI-wiring regressions. Internal build only; no GitHub push, tag or public release.

## 3.4.29.56 INTERN

- Add five attributed free-media Display Effects—Seamless Smoke, Dark Smoke, Particle Fog, Fluid Waves and Digital Wave—with Original, Ice Blue, Plasma Violet and Ember Orange 1600×720 H.264 variants.
- Separate the main design and colour subcategory, show creator/source/license as clickable links in the app, and record every source in the bundled asset README and central third-party notices.
- Keep the new library fully offline and pass selected media through the established Levita Studio, Layer-2 composition, reconnect barrier and sole TRCC owner.
- Repair the blank `FENSTERDIAGNOSE:` lines found in the supplied trace by restoring the accidentally unreachable native-window summary; the QColorDialog entries themselves are expected user-visible colour-picker events.
- Extend German, English, Spanish and French together and add catalog, asset, attribution and diagnostics regressions. Internal build only; no GitHub push, tag or public release.

## 3.4.29.55 INTERN

- Make startup responsive by scheduling hardware initialisation after the first Qt event turn, replacing the shell-based dependency probe with direct runtime-capability checks, and deferring Levita media-card construction until the window can paint.
- Add Responsive Startup 1.0: CoolerControl service/process inspection runs in a bounded, coalesced `QProcess` helper instead of the GUI thread. Unknown or failed state remains fail-closed and active OHC fan control is released if a competing daemon appears.
- Replace the Display Effects Layer-2 combo with graphical LCD-Studio preview cards and move effect type to the top of the Effect settings panel.
- Speed first-time effect encoding with the compatible ffmpeg `veryfast` preset and avoid rebuilding the entire Levita gallery when a cached generated effect is already present. The established reconnect barrier, single TRCC owner and ten-second hardware-change cooldown remain unchanged.
- Extend all four modular language files together and add focused startup/effect-selection regression coverage. Internal build only; no GitHub push, tag or public release.

## 3.4.29.54 INTERN

- Add a modular Display Effects 1.0 page next to LCD with a deterministic procedural smoke renderer, live Layer-2 sensor-layout composition, persisted presets and bounded ffmpeg export through the existing Levita Studio apply path.
- Add OpenLinkHub Update 1.0: bounded official release metadata, published SHA-256 verification for user-space archives, safe extraction, recoverable installation backup/rollback, and fixed pkexec DNF/APT commands for package-managed installations. The bundled web UI updates together with OpenLinkHub.
- Complete the German/English/Spanish/French switch for icon-prefixed navigation, runtime fan cards, page headers and About content; require every new Display Effects/OpenLinkHub control in the same four per-language files.
- Suppress desktop startup feedback for tray-only autostart and route a second launcher invocation to the running instance through a private local activation socket while retaining the hardware process lock.
- Keep Levita/Kraken shutdown safety intact and remove a QProcess shutdown race that could dereference the cleared current process after a synchronous finished signal.
- Internal build only; no GitHub push, tag or public release.

## 3.4.29.53 INTERN

- Gibt die Levita beim echten Programmende, beim Tray-„Beenden“, bei Logout und bei behandeltem System-Shutdown nicht mehr nur an das aktive TRCC-Theme, sondern vollständig aus dem TRCC-Daemon frei. Dadurch endet auch dessen Live-Neurendering; nach dem dokumentierten Firmware-Zeitlimit von etwa zwei bis drei Sekunden erscheint wieder das eingebaute Thermalright-Standardbild statt des letzten OHC-Frames.
- Startet nach jedem bestätigten echten Levita-Schreibzugriff einen kleinen prozessgetrennten Pipe-Wächter. Verschwindet der OHC-Hauptprozess unerwartet, sendet dieser genau einen auf drei Sekunden begrenzten, offscreen ausgeführten `trcc device disconnect 87ad:70db`-Aufruf an den vorhandenen Daemon. Ein sauber bestätigter Rückfall beendet den Wächter ohne doppelten Zugriff.
- Behält Testmodus und USB-Besitzgrenzen bei: reine Vorschau startet keinen Wächter, der Wächter verwendet kein eigenes USB-Protokoll und validiert den absoluten ausführbaren `trcc`-Pfad sowie die feste Levita-ID.
- Bestätigt den bestehenden Kraken-Abschaltpfad erneut: laufender CAM-Raw-Stream stoppt zuerst, danach setzt liquidctl synchron die originale Flüssigkeitstemperaturanzeige; eine unsaubere experimentelle LCD-Sitzung bleibt über den vorhandenen Startmarker abgesichert.
- Ergänzt fokussierte Regressionstests für den shellfreien, zeitbegrenzten Daemon-Disconnect, Pfadvalidierung, Wächter-Lebenszyklus sowie Levita-/Kraken-Integration.
- Interne Version; kein GitHub-Push, Tag oder öffentliches Release.

## 3.4.29.52 INTERN

- Verschiebt den vollständigen Sprachbestand in das versionierte Modul `src/modules/localization/v1_0/`.
- Hält Deutsch, Englisch, Spanisch und Französisch jeweils in genau einer eigenen Datei; jede Datei enthält UI-, Einrichtungsassistent- und Hilfetexte der Sprache.
- Ersetzt den bisherigen großen Mischkatalog und die drei fachlich gruppierten Zusatzkataloge durch einen kleinen Katalog-Assembler. Dieser lehnt doppelte deutsche Quellen sowie fehlende oder zusätzliche stabile Nachrichten-IDs sofort ab.
- Behält `src/localization_catalog.py` als dünne kompatible Importoberfläche bei, sodass Hauptfenster und bestehende Integrationen unverändert auf den Katalog zugreifen.
- Aktualisiert KI-Regeln, Modulregister, Architektur, Installer, Paketbau sowie Offscreen- und Sicherheitstests auf die Ein-Datei-pro-Sprache-Struktur.
- Interne Version; kein GitHub-Push, Tag oder öffentliches Release.

## 3.4.29.51 INTERN

- Repariert den Sprachwechsel für die vollständig aufgebaute Oberfläche: Schaltflächen, Auswahlfelder, Kontrollkästchen, Gruppen, Reiter, Menüs, Tabellenköpfe und Platzhalter besitzen jetzt atomare deutsche, englische, spanische und französische Einträge.
- Übersetzt dynamische Galerieangaben werttreu: persönliche Dateinamen bleiben erhalten, während Bild-/Video-/Live-Layout-Typen, Galerie-Zähler und Farbbeschriftungen in der gewählten Sprache erscheinen.
- Ergänzt hervorgehobene Seiten- und Statustexte für Übersicht, Kühlung, Gehäuselüfter, Levita, RGB, Profile, Einstellungen und Hilfe.
- Teilt den Sprachbestand in kleine Fachdateien auf und nimmt diese in Installer, ZIP, RPM, Release-Prüfung und Sicherheitstests auf.
- Macht die gleichzeitige Pflege von Deutsch, Englisch, Spanisch und Französisch für jede künftige sichtbare UI-Änderung in allen KI-Anleitungen verbindlich. Der vollständige Offscreen-UI-Test lehnt neue unübersetzte Bedienelemente ab.
- Interne Version; kein GitHub-Push, Tag oder öffentliches Release.

## 3.4.29.50 INTERN

- Ergänzt die Levita-Galerie um drei projekt-eigene, nahtlose 10-Sekunden-3D-Loops in 1600×720: **Orbital Ring** (Weltraumtor und Planet), **Neon Apex** (futuristischer Sportwagen) und **Quantum Core** (pulsierender Reaktor). Die stummen H.264-Dateien enthalten keine Hersteller-/Stockmedien; `tools/render_levita_loops.py` hält Geometrie und Bewegung reproduzierbar.
- Synchronisiert die obere Kühlprofilwahl und gespeicherte Kühlprofile mit den Gehäuselüfterprofilen. **Leistung** wird von einer temperaturabhängigen Kurve zum konstanten 100-%-Override für Pumpe, Radiator und Gehäuselüfter; bei laufender OHC-Regelung werden bestätigte, aktivierte und schreibbare Kanäle sofort aktualisiert.
- Ergänzt direkt auf jeder System-Fan-Karte den vorhandenen bestätigungspflichtigen 0-%-/10-s-Stopptest. Vorherige Firmware-/hwmon-Zustände werden nach dem begrenzten Test wiederhergestellt.
- Erklärt bei NCT6687-Treibern ohne `pwmN_mode`, dass der elektrische PWM-/DC-Modus im BIOS festgelegt bleibt. OHC nutzt weiterhin ausschließlich dokumentierte sysfs-Knoten und erzwingt keine unbekannten Register; meldet der Treiber `pwmN_mode`, bleibt die sichere Umschaltung mit Warnung und erneuter Kalibrierung verfügbar.

## 3.4.29.49 INTERN

- RGB-Studio klappt „Geräte und Effekte“ sowie die native Hardwarekanal-Liste als große Bereiche in der Seite auf; kein Extra-Fenster, und die Kanalliste bleibt beim Seitenwechsel sichtbar.
- Übersicht „Status & Hinweise“ übernimmt nach bestätigten PWM-Tests den Levita-Zustand: statt der festen Warnung erscheinen ein grüner Punkt und **OK**, solange Pumpe und Radiator bestätigt sind; fehlende Tests oder Sensorfehler nutzen einen roten Punkt und **Fehlerhaft**, im gleichen Raster wie „Erkannte Hardware“.

## 3.4.29.48 STABLE

- Verbindliche Ablage- und Kurz-README-Regel für alle Coding-KIs in `docs/ai/AGENTS.md` (Tabelle *welche Datei wohin*, keine neuen Dateien im Wurzelverzeichnis, README unter 200 Zeilen mit genau einem „Neu in“-Abschnitt und höchstens vier Verlaufsversionen), gespiegelt in `.cursor/rules/70-repository-layout.mdc`, `.github/copilot-instructions.md`, `docs/ai/CLAUDE.md` und `docs/project/DECISIONS.md`. `tests/test_repository_layout_342947.py` erzwingt die Regel.
- Korrigiert den GitHub-Release-Workflow und die Cursor-Regel-Globs, die nach der Verschiebung noch `VERSION`/`BUILD_CHANNEL` im Wurzelverzeichnis beziehungsweise `*.py` ohne `src/` erwarteten; der Tag `v3.4.29.47` bleibt ohne veröffentlichtes Release.

## 3.4.29.47 STABLE

- Sortiert die letzten losen Dateien des Wurzelverzeichnisses in Ordner: der gesamte Anwendungscode (`*.py`, `assets/`, `modules/`, `test-gifs/`) liegt in `src/`; `install.sh`, `uninstall.sh`, `VERSION` und `BUILD_CHANNEL` in `packaging/`; `INSTALL.md`, `CHANGELOG.md` und `README.en.md` in `docs/`; die vollständigen Agentenanweisungen `AGENTS.md` und `CLAUDE.md` in `docs/ai/`; `SECURITY.md` in `.github/`. Im Wurzelverzeichnis bleiben `README.md`, `LICENSE`, `CITATION.cff` und ein kurzer `AGENTS.md`-Wegweiser.
- Die installierte Programmstruktur (`~/.local/share/open-hardware-control`, `/usr/share/open-hardware-control`) bleibt flach und unverändert. `install.sh` erkennt `src/` sowohl im entpackten ZIP (Skript im Paketwurzelordner) als auch im Quellbaum (`packaging/`). RPM-/DEB-Bau, Release-Prüfung, Modulregisterprüfung, Tests, Cursor-Regeln und GitHub-Workflows verwenden die neuen Pfade.
- `app_constants.helper_script_path` und das SVG-Fallback in `branding.py` finden Hilfsdateien im Quellbaum unter `../packaging/`.

## 3.4.29.46 STABLE

- Beendet den minütlichen Hintergrundstart von `openrgb --client 127.0.0.1:6742 --list-devices`, solange das Hauptfenster im Infobereich verborgen ist und weder ein gespeichertes RGB-Startprofil noch eine Schreibfreigabe oder eine bereits geplante Wiederholung ausstehen. Sichtbares Fenster, Startprofil und Wiederholungen verhalten sich unverändert; Regressionstest `tests/test_rgb_inventory_tray_guard_342946.py`.
- Sortiert das Repository in Themenordner: Dokumentation nach `docs/project`, `docs/ai`, `docs/hardware`, `docs/security` und `docs/releases`; udev-Regel, Polkit-Policy, Metainfo, Desktop-Vorlage, Icon und Hilfsskripte nach `packaging/`; `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` und `SUPPORT.md` nach `.github/`. `install.sh`, RPM und DEB installieren weiterhin die bekannte flache Programmstruktur; `app_constants.helper_script_path` findet `install-dependencies.sh` und `install-udev-rule.sh` sowohl installiert als auch im Quellbaum.
- Ersetzt die veralteten August-Screenshots durch sieben aktuelle Aufnahmen (Übersicht, Kühlung, RGB-Studio, LCD/Levita, Wallpaper Engine, Profile, Einstellungen) als anklickbare Galerie in `README.md` und `README.en.md`. Installation, Sicherheit, Dokumentation und Status stehen jetzt direkt nach dem Levita-Highlight; die Versionshistorie in der README umfasst nur noch die letzten vier Versionen und verweist für ältere Stände auf `CHANGELOG.md` und `docs/releases/`.

## 3.4.29.45 STABLE

- Isoliert den Levita-Videovorschau-Belastungstest vollständig von bereits beim Studioaufbau gestarteten Aufgaben für die gebündelte OHC-Animation. Vor der Messung werden diese Test-Worker kontrolliert beendet und ihre Zähler geleert; danach werden alle 140 synthetischen Einträge und die Zwei-Worker-Grenze deterministisch geprüft.
- Übernimmt den vollständigen 3.4.29.44-Funktionsstand einschließlich Thermalright-Levita-Display-Highlight, eigener KI-Galerie, OpenRGB-Kaltstartkorrektur und vervollständigter GitHub-Qt/EGL-Testumgebung in den finalen öffentlichen Release.

## 3.4.29.44 STABLE

- Korrigiert den Levita-Videovorschau-Belastungstest für frische Systeme ohne Thumbnail-Cache: Die eine gebündelte OHC-Animation wird als legitimer Anfangsauftrag berücksichtigt, bevor 140 synthetische Videos ergänzt werden.
- Installiert in GitHub Actions die vollständigen Testabhängigkeiten `pytest`, Pillow, PySide6 und die für Qt benötigte EGL-Laufzeitbibliothek. Ein manueller Release-Wiederanlauf validiert einen vorhandenen stabilen Tag, ohne ihn zu verschieben.
- Übernimmt sämtliche Programmkorrekturen, Thermalright-Levita-Highlights und ausschließlich projekt-eigenen KI-Medien aus 3.4.29.43 in den bereinigten öffentlichen Release.

## 3.4.29.43 STABLE

- Stellt die neue Unterstützung für das 1600×720-Display der **Thermalright Levita Vision 360 ARGB Black** als Release-Highlight heraus und bündelt elf eigene OHC-Hintergründe, zwei OHC-Datenlayouts sowie genau eine deduplizierte 30-Sekunden-KI-Animation. Hersteller-/TRCC-Katalogmedien und importierte Benutzerdateien bleiben vollständig außerhalb des Repositorys und der Releasepakete.
- Verhindert, dass ein gespeichertes RGB-Startprofil während der absichtlich zurückgehaltenen ersten OpenRGB-Teilerkennung endgültig verworfen wird. Der Profilstart bleibt nun exklusiv vorgemerkt, wartet begrenzt auf den vollständigen Gerätebestand und übernimmt anschließend das gespeicherte Design.
- Korrigiert die Release-Prüfung des Modulregisters: Sie validiert jetzt den tatsächlich in `BUILD_CHANNEL` gesetzten Kanal und unterstützt dadurch sowohl interne als auch stabile Builds.
- Trennt den temporären RPM-Quellbaum vom gleichnamigen stabilen Laufzeit-ZIP-Baum, sodass der erste `STABLE`-Paketbau nicht mehr mit `FileExistsError` abbricht.
- Übernimmt die geprüften Wallpaper-Engine-, Fensterplatzierungs-, RGB-Studio-, Levita-, Diagnose-, Paketierungs- und Oberflächenänderungen der internen 3.4.29-Reihe in den stabilen Veröffentlichungsstand.

## 3.4.29.42 INTERN

- Repariert Zurück, Pause, Fortsetzen, Weiter und Ton umschalten im Wallpaper-Engine-Bereich. Pause, Fortsetzen, Weiter und Ton adressieren das vom installierten CaptSilver-v1.4-Plugin tatsächlich unter `org.kde.plasmashell` registrierte Objekt `/WallpaperEngine`; Zurück nutzt die vorherige lokale Workshop-Karte, weil CaptSilver v1.4 seine veröffentlichte Previous-Methode intern noch als Vorwärtssprung ausführt.
- Ergänzt die drei originalen CaptSilver-Skalierungswerte „Seitenverhältnis beibehalten“, „Skalieren und zuschneiden“ und „Auf Vollbild strecken“. Die Wahl gilt ausdrücklich für das ausgewählte Bildschirmziel und verändert keine Workshop- oder Plugin-Dateien.
- Startet das Hauptfenster standardmäßig auf dem von Qt/KDE gemeldeten Hauptbildschirm. In Einstellungen → Anzeige und DPI kann stattdessen ein benannter Monitor dauerhaft gewählt werden; ein nicht verbundener Zielmonitor fällt sicher auf den Hauptbildschirm zurück. KWin behält unter Wayland die endgültige Platzierungsentscheidung.
- Vereinheitlicht vertikale und horizontale Scrollleisten in der gesamten Anwendung auf ein schmales acht Pixel breites beziehungsweise hohes, zum Akzent passendes Design.
- Führt Wallpaper Engine als Modul 1.2 und die reine Fensterplatzierungsrichtlinie als Modul 1.0. Erststart-Assistent, sicherer optionaler Installer, feste Galeriekarten, Originalprofil und rücksetzbare Optimierung bleiben unverändert erhalten.

## 3.4.29.41 INTERN

- Zeigt beim ersten bewussten Öffnen von Wallpaper Engine eine vollständige Schritt-für-Schritt-Einrichtung und hält sie über „Einrichtungsassistent öffnen“ dauerhaft erreichbar. Steam- und Workshop-Aktionen empfehlen mindestens fünf fertig geladene Abonnements und eine anschließende Bibliotheksprüfung.
- Bietet auf Fedora eine ausdrücklich bestätigte automatische CaptSilver-Plugin-Installation. Das passende stabile RPM wird anhand Fedora-Hauptversion und Architektur ausschließlich vom offiziellen GitHub-Release gewählt, als normaler Benutzer begrenzt heruntergeladen und gegen die dort veröffentlichte SHA256-Prüfsumme geprüft. Erst eine zweite Bestätigung startet den festen `pkexec dnf install`-Befehl; Passwort und Administratorentscheidung bleiben vollständig bei Polkit.
- Lässt andere Distributionen bei der offiziellen Anleitung, statt Paketnamen oder privilegierte Befehle zu erraten. Wallpaper Engine selbst bleibt ein separat über Steam zu installierendes Produkt.
- Fixiert Icon- und Kartenmaße der Wallpaper-/Videogalerie auch nach dem automatischen Refresh eines angewendeten Wallpapers. Eine verzögerte Layout-Neuberechnung ersetzt den bisher nötigen Fenstergrößenwechsel.
- Ordnet die Standardnavigation als Übersicht, Kühlung, RGB-Studio, LCD, Wallpaper Engine, optional Corsair/OpenLinkHub, Profile, Einstellungen, Über und Log. Nur exakt frühere Standardfolgen werden migriert; eigene Reihenfolgen bleiben erhalten. Das weiterhin experimentelle Desktop-Design-Modul bleibt außerhalb dieser sichtbaren Standardfolge am Ende.
- Verschiebt eine eigene themengleiche Hauptfenster-Titelleiste bewusst in eine Folgeversion. 3.4.29.41 behält Kwins native Dekoration, bis Wayland-/X11-Verschieben, Resize, Maximieren, Tastaturzugriff und minimierter Tray-Start separat abgedeckt sind.

## 3.4.29.40 INTERN

- Add a dedicated Wallpaper Engine page with read-only Steam Workshop discovery, local preview cards, type/search filters, per-screen targeting and a separate personal-video category.
- Apply selected workshop wallpapers or personal videos through Plasma's documented scripting configuration surface and expose CaptSilver's local D-Bus playback controls.
- Open Plasma's original wallpaper KCM for advanced plugin options instead of embedding or copying the upstream QML surface.
- Keep CaptSilver v1.4 stock settings as the default and add a reversible optional performance profile without installing the removed plugin patches, cache builders or watchers.
- Reject a Steam library as the personal-video folder, preventing the recursive scan that caused the reported multi-second UI stalls.

## 3.4.29.39 INTERN

- Suppress routine Qt tooltip surfaces and direct `QComboBox` popup frames from temporary window diagnostics, eliminating misleading window-open/close noise from normal controls.
- Keep diagnostics active for unrelated popups and retain the exact quarantine for the known parentless, untitled 640×480 startup `QFrame`.

## 3.4.29.38 INTERN

- Modernize RGB Studio with embedded engine controls, explicit on/off buttons, effect-aware persistent colour editing by right-click, a 0–100% overall RGB brightness slider and an in-page native hardware-channel result list.
- Ensure rejected RGB command sequences complete their failure callback so ENE-DRAM reinitialization cannot remain stuck and disable its retry button for the rest of the session.
- Move the hardware-free design gallery into versioned RGB Studio module 1.1, keeping the main orchestrator below its enforced size limit.
- Recommend the compatible TRCC Linux 9.9.12 backend, whose upstream Fedora RPM no longer conflicts with the distribution `python3-sounddevice` package; retain 9.9.11 as the physically tested Levita baseline.

## 3.4.29.37 INTERN

- Preserve explicit percent, temperature, clock and memory units in both bundled Levita live layouts and migrate saved OHC overrides without requiring a reset.
- Add persistent 25–150% intensity controls directly above both LCD layer galleries; Orbital Command defaults to 130%, while Nebula Drift stays at 100%.
- Guard TRCC 9.9.11's misinterpreted low-Hz AMD idle-clock range through 1,000,000 Hz via the existing daemon socket and restore the dynamic format when the sensor recovers.
- Add a dedicated hardware-anomaly Log view plus low-frequency plausibility checks that report only new issues and recovery.

## 3.4.29.36 INTERN

- Create a complete local backup after every successful version build in the sibling `Open Hardware Control Backup` directory, including runtime and developer archives, source snapshot, Local-AI Git bundle, generated RPM/DEB files, release notes and fresh SHA256 checksums.
- Keep the newest two semantic version directories atomically while preserving every unrelated file or folder and refusing recursive backups inside the repository.
- Teach GitHub Copilot, Cursor and local coding agents the same mandatory backup policy, without restoring the removed cloud-backup workflow or making backups a GitHub push gate.

## 3.4.29.35 INTERN

- Repair the stale TRCC-daemon connection left after a Levita unplug or power loss: every explicit design apply now performs a tolerated daemon detach followed by a mandatory fresh 1600×720 handshake before changing display state.
- Use the same serialized reconnect barrier for the physical colour test and independent brightness/orientation actions, preventing OHC from reporting success against a cached handshake whose USB transport is already closed.
- Validate the recovery on the attached 87ad:70db device: disconnect, reconnect, model-64 handshake, four-colour transfer and saved 148-frame theme restore all completed successfully without further transport errors.

## 3.4.29.34 INTERN

- Restore application of OHC's private editable Levita cache themes: validated staged artwork links are accepted at runtime, while the external folder-import boundary continues to reject symlinked theme inputs.
- On every controlled application shutdown, stop the Levita video/stream client and issue one bounded 1.5-second offscreen `display stop-video` request through the existing TRCC daemon so the active original theme returns.
- Add regressions for real staged-theme command construction, strict imported-theme isolation and the bounded shell-free shutdown request.

## 3.4.29.33 INTERN

- Persist the selected RGB Studio design and its per-design one- or two-colour overrides, keeping the selected card visibly outlined after a restart; add Aurora Vortex and Galaxy Comet presets.
- Add a bounded ENE-DRAM cold-start recovery: one immediate native Direct reclaim followed by three precautionary retries after 45 seconds, 2 minutes and 4 minutes, each followed by the current OHC design.
- Reorganize the Levita LCD library as two large side-by-side layer panels with custom-folder import, direct layer assignment, persistent favourites and a favourites-only filter.
- Migrate the Levita notch once to its physical 80-pixel minimum so existing installations also start with the maximum usable image area; later user changes remain persistent.
- Bundle two original project-owned 1600×720 space data surfaces: Nebula Drift and Orbital Command; the latter shows CPU/GPU load, temperature and clocks plus GPU memory usage.
- Reduce the default/global UI scale and common control padding, and rebuild About software links plus supported-device information for About and Help.

## 3.4.29.32 INTERN

- Restore readable left navigation in the light theme: the sidebar uses a light rail, dark item text and a dark selected-item color instead of white text on a pale highlight.
- Move the LCD “Design anpassen” panel to a right-hand column beside the live preview so the controls keep full width instead of sitting in a squeezed strip under the canvas.
- Lay out layer-1 and layer-2 design cards in a full-width grid of 4–8 columns so Gallery, Tech, HUD/Art, Light, Nature, Aesthetic, OHC backgrounds and custom files need less vertical scrolling.

## 3.4.29.31 INTERN

- Make the LCD “Design anpassen” panel readable: number fields and combo boxes keep a usable height and width, the black-bar checkbox gets its own full-width row, and the settings group no longer shrinks below its natural size.
- Stop window diagnostics from writing into the already destroyed log widget during shutdown, so a normal SIGTERM/Qt quit no longer prints Shiboken `QPlainTextEdit already deleted` errors.

## 3.4.29.30 INTERN

- Round the right edge of the selected Levita image/video at its boundary with the black camera/notch bar instead of placing the curve at the physical outer panel edge.
- Add embedded top-right and bottom-right radius controls with a 48 px default, 0–240 px bounds, linked adjustment by default and optional independent adjustment.
- Share one pure geometry implementation between the live preview and generated TRCC mask so the editor and physical display use the same curve.
- Keep the separately rounded physical panel outline independent and do not render the red guide drawn on the reference photograph.
- Raise the Levita data-surface module from 1.3 to 1.4 and retain only `modules/lcd_levita/v1_4/` as its current implementation.

## 3.4.29.29 INTERN

- Explicitly apply and enable the generated full-canvas `01.png` after loading an editable Levita cache theme, restoring both the original layer-2 artwork and the right physical-notch cover when persisted TRCC state had `mask_visible=False`.
- Restore animated display backgrounds with a long-running `display play` ticker that is strictly a `TRCC_DAEMON=1` Unix-socket client; the existing daemon remains the sole USB owner and no second libusb/hidapi App is created.
- Start the ticker only for video-backed media, stop it before a design change and terminate it during Stop/Shutdown so static designs do not pay the animation cost.
- Fit the bounded 16-frame selected-video preview sequence once after loading instead of rescaling every frame to 1600×720 on each 250 ms UI tick.
- Keep the Levita data-surface module at 1.3 because the layout/staging contract is unchanged; this is an orchestration correction backed by TRCC runtime logs.

## 3.4.29.28 INTERN

- Route every OHC TRCC command through TRCC's documented `TRCC_DAEMON=1` mode so one long-lived backend process owns the Levita USB transport and later commands reuse its connected App through the Unix socket.
- Remove OHC's second `trcc display play` process after a successful `load-theme`; the daemon already owns the metrics/render loop and advances the staged video and live values itself.
- Force TRCC client processes offscreen while preserving the daemon's hardware ownership, preventing extra Qt surfaces without creating another in-process USB owner.
- Add real Qt regression coverage for the daemon environment and for successful apply completion without a separate renderer process.
- Keep the Levita data-surface module at 1.3 because this is a transport/orchestration correction outside its stable layout and staging contract.

## 3.4.29.27 INTERN

- Preserve the alpha channel of editable layer-2 artwork while fitting it to the 1600×720 canvas, so it no longer becomes an opaque black surface that hides the selected layer-1 image or video.
- Expand the selected-video preview to a bounded 16-frame, 4-FPS sequence at 800-pixel extraction width and animate it in the large Levita canvas at 250 ms per frame.
- Give selected-video preview frames a new cache generation so previously generated four-frame hover caches cannot mask the corrected behavior.
- Detect a crashed TRCC `QProcess` explicitly, stop automatic USB attempts and report the external backend/libusb crash separately from an ordinary command failure.
- Keep the Levita data-surface module at 1.3; this correction belongs to the legacy media/UI orchestration boundary and does not change the module contract.

## 3.4.29.26 INTERN

- Stage the selected Levita background video, generated panel mask and editable layer-2 blocks as one cache theme so TRCC applies the composition through one connected `load-theme` session instead of separate `load-theme`, `play-video` and `apply-mask` handshakes.
- Coalesce rapid complete-design requests behind a ten-second post-start USB protection interval; the latest selected combination is applied when the interval ends.
- Limit a handshake-timeout path to one retry in total and stop the former nested startup retry from repeatedly addressing an already unresponsive display.
- Report the required complete display power cycle when the USB device remains enumerated but endpoint `0x81` no longer answers the handshake.
- Bump the Levita data-surface/staging module from 1.2 to 1.3 and keep only `modules/lcd_levita/v1_3/` as the current implementation.

## 3.4.29.25 INTERN

- Clarify that `BUILD_CHANNEL=INTERN` blocks public release publication but does not block a normal, explicitly owner-requested push to a tested non-release development branch or an explicitly requested pull request.
- Separate authorization for a normal branch push from pull requests, tags, public releases, force-pushes and remote deletion so coding agents cannot treat one permission as approval for another action.
- Remove contradictory publication-guide wording and make the default no-push instruction explicitly overridable only by a concrete project-owner request.

## 3.4.29.24 INTERN

- Review and integrate all five code fixes from the incomplete 3.4.29.22/23 comparison archives into the complete repository instead of replacing the trusted source tree.
- Continue parsing bounded Levita layer-2 JSON after an individual malformed element and reject symlinked `config1.dc`, `Theme.png` and `00.png` theme inputs.
- Default missing/corrupt split-mode settings to safe Off through the pure module policy, report a livestream active only after `QProcess.started`, retain the bounded autostart retry on `FailedToStart`, and stop hover-preview timers plus ffmpeg on shutdown.
- Bump the Levita data-surface module from 1.1 to 1.2 and keep only `modules/lcd_levita/v1_2/` as the current implementation.
- Validate package profiles during every build: the runtime ZIP intentionally excludes development folders, while the developer ZIP must contain the complete repository test inventory, release scripts, workflows and tools.
- Build the Local-AI Git bundle from a temporary snapshot commit of that exact validated developer tree, so uncommitted release work cannot produce a correctly named but stale bundle. The working repository remains untouched.

## 3.4.29.23 INTERN

- Introduce safe split-mode fallback, renderer-start confirmation and hover-preview process cleanup in the intermediate deep-bugfix archive. Full-repository integration and verification follow in 3.4.29.24.

## 3.4.29.22 INTERN

- Introduce malformed-layout-record recovery and symlink-safe TRCC theme discovery in the intermediate bugfix archive. Full-repository integration and verification follow in 3.4.29.24.

## 3.4.29.21 INTERN

- Paint a selected Ebene-1 background card into the large Levita preview in the same click, using the image itself or a cached first video frame instead of a black intermediate canvas.
- Round only the physical outer-right display corners. Keep the camera/notch bar's inner edge a straight vertical split in preview, generated mask and prepared cache images.
- Extract the panel outline into `modules/lcd_levita/v1_1/panel_geometry.py` so local coding models can load the geometry without the Qt canvas.
- Keep layer-2 module 1.1; this hotfix does not change the editable-block contract.
- Leave the Debian packager wired, but skip DEB output on hosts without `dpkg-deb`.

## 3.4.29.20 INTERN

- Hide the Kraken coolant card on the main dashboard unless a connected Kraken supplies a real liquid-temperature value. Preserve the user's saved card selection while the hardware-dependent card is unavailable.
- Extract dashboard grid and card-availability orchestration from the historical main window into focused `dashboard_layout.py`, keeping `kraken_control.py` below its enforced legacy size ceiling.
- Render imported TRCC layer-2 text coordinates as visual block centres, matching the physical 1600×720 display instead of treating them as top-left positions.
- Keep draggable clock and sensor items alive while animated video frames replace only the preview background; remove rubber-band selection that could consume the first drag gesture.
- Replace layer-2 colour, font-size and text popup dialogs with an integrated editor beside the blue preview canvas. Apply, cancel and per-block reset close the panel in place.
- Reload both selected preview layers immediately when the current background is selected again, and retain the last valid video frame during asynchronous preparation instead of clearing to black.
- Add pure availability-policy tests, centre-coordinate rendering checks, same-card background reload coverage and a regression proving a video-frame update does not replace a live drag item.
- Run the release test gate through pytest so every collected `test_*` function executes; restore real PySide6 modules after the isolated runtime-stub import to prevent cross-test contamination.

## 3.4.29.19 INTERN

- Fix edited Levita layer-2 apply and autostart failures reporting `Kein vollständiges TRCC-Hardwaredesign` for OHC's own `editable-themes/theme-*` cache paths.
- Accept either a legacy `config1.dc` theme or a bounded, valid 1600×720 native `trcc.json` theme, matching TRCC Linux's documented `load-theme` contract. Wrong-geometry and malformed JSON themes remain rejected.
- Preserve every imported source file: existing generated cache themes work immediately and no compatibility `config1.dc` is fabricated or written.
- Stop rebuilding the large background-card catalog for a pure layer-2 selection and remove duplicate preview/status refreshes from the hidden combo model.
- Add regression coverage for the exact failing cache-path shape, valid native JSON loading, invalid geometry rejection and the complete hardware-free UI construction.

## 3.4.29.18 INTERN

- Make every logical Thermalright Levita data-layer-2 block independently draggable while keeping a combined label, live value and unit together as one item.
- Add whole-layer X/Y offsets and a block context menu for color, font size, text/label editing and individual reset. Persist overrides separately per selected design.
- Keep imported TRCC sources immutable. Read native JSON or delegate legacy `config1.dc` decoding to the installed TRCC backend, then stage an OHC-owned content-addressed cache theme with generated `trcc.json` and linked local artwork/media.
- Introduce `modules/lcd_levita/v1_0/` with separate pure layout model, Qt canvas interaction and TRCC adapter responsibilities; keep the existing display UI as the gradual compatibility orchestrator.
- Add the mandatory `docs/project/MODULE_REGISTRY.md`, a registry validator, version-folder rules and strict file-size budgets for local coding models with 16 GB VRAM. Add step-by-step UI, sensor and LCD extension guidance and wire it into every AI startup path.
- Package the versioned module tree in portable, developer, RPM and DEB outputs and add model, persistence, staging, static UI, registry and full offscreen UI regressions.

## 3.4.29.17 INTERN

- Replace the generic `preferences-system-cooling` icon used by the KDE Plasma system-tray entry with OHC's own compact emblem. The tray no longer depends on whether that unrelated desktop-theme icon exists.
- Add a dedicated transparent 22×22 tray raster and construct the `QSystemTrayIcon` from project-owned 22, 32, 48 and 64 pixel assets. Package and portable installers place the new size in `hicolor/22x22/apps` as well.
- Follow the robust ckb-next pattern of providing a named application icon set plus a tray-native small raster, while retaining Qt's portable `QSystemTrayIcon` implementation.
- Extend branding and full-UI regressions to verify the native 22×22 asset, the actual tray icon sizes and the absence of the old generic cooling-icon request.

## 3.4.29.16 INTERN

- Block the repeatedly observed OHC-owned blank startup surface only when it matches the exact signature `QFrame` / top-level `Window` / no parent / no title or object name / non-modal / 640×480. Named frames, dialogs, popups and any differently sized frame remain unaffected.
- Extend window diagnostics with stable in-process object identity, flags, size hint, layout and direct-child counts, QObject ancestry, focus/active/native state, application/window age and the most recent helper process as explicitly timing-only context. Suspicious-frame reports include bounded direct-child geometry before quarantine.
- Deduplicate the Levita media catalog by complete case-insensitive basename, including the suffix. Multiple `d002.mp4` copies now produce one card, while differently named files and `d002.png` remain independent.
- Prefer the installed/normal and shortest media path over copies below `alt`, `old`, `backup`, `sicherung`, `kopie`, `copy`, `archive` or `archiv` directories.
- Migrate a saved selection from a hidden duplicate path to the retained canonical path automatically.
- Report the number of hidden duplicates in both the library label and log. This is a non-destructive catalog operation: OHC never deletes, moves or modifies the user's original media files.
- Add pure and full-UI regressions covering case-insensitive duplicate names, backup-path preference, differently named media, separate extensions and catalog-level duplicate counts, plus positive and negative regressions for the narrowly scoped empty-frame blocker.

## 3.4.29.15 INTERN

- Keep image as well as video backgrounds selected when a complete data layout is chosen in Levita layer 2. The combined main preview now refreshes immediately from every layer-2 card, including a second click on the already selected card.
- Guarantee a visible layer-2 preview for incomplete imported layouts. OHC prefers the extracted transparent hardware-data layer, but falls back to the complete `Theme.png` when `00.png` is missing or no separable layer can be built.
- Replace the full-width graphics viewport with a centered Levita stage that follows the physical 1600×720 aspect ratio. The display preview is capped at 960×432 while the unused page width remains the normal blue OHC background.
- Extend the real offscreen UI regression to verify that selecting a layer-2 layout preserves an image background, produces a non-empty upper layer and retains the exact preview aspect ratio.

## 3.4.29.14 INTERN

- Replace synchronous per-card video probing with a non-blocking thumbnail queue. At most two `ffmpeg` workers run concurrently, so opening or changing a large Levita category no longer freezes the Qt event loop.
- Show visible thumbnail progress while the queue is active and keep the selected main preview responsive. The selected video is queued before the rest of the card catalog.
- Store successful thumbnails in the persistent OHC configuration cache using source path, size and modification time. Unchanged videos therefore load immediately on later application starts; changed files receive a new cache identity.
- Remember unreadable video results for six hours to prevent the same damaged asset from causing a process storm on every category change or restart. Worker timeouts remain bounded to eight seconds.
- Add a regression that constructs 140 uncached video cards and verifies that gallery construction returns immediately, uses no more than two workers and reuses a persisted cache result.

## 3.4.29.13 INTERN

- Keep one remembered custom Levita design directory independently from the TRCC standard catalog. The directory can be hidden with a checkbox and restored with its last selected media without reopening a file dialog; OHC never deletes the directory or its files.
- Separate the Levita card library by function: images/videos remain in background layer 1, while complete `config1.dc` themes with clocks and sensor values belong to data layer 2. Explicit move-to-other-layer buttons preserve intentional exceptions.
- Add a real thumbnail for every supported local video and animate cached preview frames directly inside a hovered card. Keep the main 1600×720 preview animated as before.
- Move “Design anpassen” and direct apply actions into the studio header. Add Levita-specific brightness (0–100), orientation (0/90/180/270) and hover-preview controls backed by TRCC's real `set-brightness` and `set-orientation` commands.
- Serialize Levita USB operations. The persistent `display play` process exits gracefully by SIGINT, a release delay precedes the next theme handshake, concurrent switches are rejected rather than killing each other, and an `Errno 110` handshake timeout gets at most one delayed retry.
- Place the Gehäuselüfter quick profiles Leise, Ausbalanciert and Leistung at the top of the case-fan summary card like the CPU profiles. Automatic channel control remains a separate action and presets still never activate or calibrate a channel.
- On Thermalright-only systems, prioritize the complete Levita studio and move Kraken-only display settings to the end of the LCD workspace.

## 3.4.29.12 INTERN

- Rebuild the Thermalright Levita Display Studio around modern thumbnail cards for background and data layers. TRCC categories are direct buttons, long popup lists are removed, and optional crop/notch and OHC-overlay editors open only when requested.
- Move local video animation into the main 1600×720 preview and constrain the canvas to the display aspect instead of reserving a separate hover-preview column.
- Add three project-owned Levita backgrounds—Carbon Blue, Titanium Blue and Plasma Circuit—as an offline OHC design category.
- Persist the selected background and upper data layer. An explicit checkbox and “save current selection” button can restore and apply that exact Levita design after desktop startup; the writer waits for desktop readiness and retries only once if the device is still busy.
- Keep Levita autostart separate from Kraken LCD profile restoration and preserve the default no-write test mode. Selecting or discovering media alone still never authorizes USB access.
- Reject square and portrait `config1.dc` layouts even when a broad parent TRCC folder is imported; only verified or dimension-matching 1600×720 Levita layouts become live-data cards.
- Bind the running Qt application to the `open-hardware-control.desktop` identity and application icon, and add `StartupWMClass`, so KDE Plasma can show the project icon for the minimized/running window.

## 3.4.29.11 INTERN

- Add the new user-provided Open Hardware Control logo to the application rail. A separately generated text-free transparent emblem is used for the window, tray, taskbar, desktop entry and size-specific Linux icon cache entries.
- Discover TRCC Linux's installed `~/.trcc/data/theme1600720l` layouts automatically. Complete designs can be loaded directly with their own background and saved `config1.dc` live values, or selected as the upper data layer above a different local video.
- Fix the portable ZIP installer so the Thermalright display/cooling modules and startup window diagnostics are copied into the installed runtime.
- Add temporary end-to-end window diagnostics for every OHC top-level/dialog/popup/tool window and native Qt surface creation. Events are written to both the visible application log and the persistent startup log with bounded, privacy-filtered identity and geometry data.
- Trace Python subprocess and Qt QProcess launches with executable name, safe command tokens, argument count, session type and `QT_QPA_PLATFORM`; redact sensitive values and collapse rapid identical repeats.
- Correct the Levita mask so only its inward-facing upper/lower corners are rounded while the physical outer/right edge remains flush and black. Bump cache identities so an older four-corner mask cannot be reused.

## 3.4.29.10 INTERN

- Add a true two-layer Levita mode: a selected local video remains the background while a complete imported TRCC `config1.dc` hardware-data layout renders live above it.
- Preserve complete theme art by alpha-compositing the theme's own `01.png` with the rounded Levita right-hand mask. The in-app canvas extracts the sample hardware layer from `Theme.png`/`00.png` for a combined preview.
- Keep the existing freely movable OHC metrics as an explicit alternative upper layer, and restrict the background chooser to valid videos while a complete hardware design is selected.
- Round only the inward-facing upper/lower corners of the adjustable Levita right-hand mask with an 18-pixel radius; keep its physical outer edge flush in both preview and hardware mask.
- Add a compact preview card to the left of the local Levita media list. Hovering an entry shows images/layout thumbnails and a short four-frame in-app video preview generated only from the local file cache.
- Close the remaining empty-window startup path by forcing the synchronous OpenRGB version query and the direct inventory helper onto Qt's offscreen platform as well as the existing asynchronous clients and managed server.

## 3.4.29.9 INTERN

- Replace the provisional local Levita theme groups with the exact current TRCC Linux cloud catalog: Gallery (`a001–a082`), Tech (`b001–b025`), HUD (`c001–c072`), Light (`d001–d055`), Nature (`e001–e054`) and Aesthetic (`y001–y010`).
- Classify existing local videos, images and layout directories only from a validated in-range original TRCC theme ID, including common filename suffixes, and sort recognized entries by catalog category and numeric theme index.
- Keep unrelated, malformed and out-of-range names under “Eigene Dateien”. Classification is deterministic and entirely local; OHC neither downloads nor redistributes manufacturer media.

## 3.4.29.8 INTERN

- Add safe per-channel PWM/DC selection only when Linux hwmon exposes the fixed `pwmN_mode` node. A confirmed change stops automation, invalidates calibration and requires the physical channel test again.
- Add Leise, Ausbalanciert and Leistung curve presets to every chassis-fan card and the global chassis-fan header, plus an explicit balanced-standard reset in the curve editor. Applying a preset preserves calibration and activation state.
- Fix persistent Polkit grant detection on protected Fedora rule directories with a root-owned readable status marker and explicit helper JSON confirmation. Rule and marker are installed/removed together; no password or extra write authority is stored.
- Change the photographed Levita default to a centered background, 80-pixel right mask and preview style C. Images and ordinary videos are always prepared aspect-correct at 1600×720 with user-selectable contain/cover behavior.
- Make the Levita mask directly draggable in the preview, add a 20-step element-position history with one-click restore, group existing local TRCC themes by stable A/B/C/D/E/Y filename prefixes and keep imported assets local.
- Preserve `%` and temperature suffixes on the physical TRCC display by using the backend's show-unit render path for formats that already contain their required glyph.
- Prioritize detected LCD hardware, hide the round Kraken preview on rectangular Thermalright-only systems and collapse the NZXT-ESC importer when no Kraken is present.
- Prevent full-UI tests from starting OpenRGB or other hardware I/O. If an OHC-managed OpenRGB process nevertheless exits unexpectedly, quarantine automatic restarts for the session until the user explicitly requests a retry.
- Downgrade the known irrelevant TRCC NVIDIA/NVML shutdown warning when it is the only livestream diagnostic, while retaining all other backend failures as errors.

## 3.4.29.7 INTERN

- Suppress creation of the OHC native window surface from the beginning of a minimized KDE/Wayland tray autostart. This removes the photographed black, unpainted OHC window instead of hiding it only after the complete UI constructor; the surface is enabled when the user explicitly opens OHC from the tray.
- Force every OpenRGB Qt invocation, including short-lived `--client` inventory and ENE-DRAM commands, onto the offscreen platform. Previously only the persistent private server was headless, allowing some OpenRGB builds to create an empty startup window for CLI clients.
- Add explicit controls to grant or remove a persistent per-user Polkit authorization for the fixed-path NCT6687 fan helper. Granting requires one final administrator confirmation, stores no password and survives reboots; removal deletes the exact generated rule.
- Keep all existing fan safeguards unchanged: the helper remains limited to validated channels 1–8, firmware restore and the bounded watchdog, while physical 70-percent/10-second channel confirmation remains mandatory.

## 3.4.29.6 INTERN

- Replace the preview-only 80-pixel cutout marker with a real transparent TRCC mask whose opaque black right-hand bar is adjustable from 80 to 800 pixels and defaults to a wider 320 pixels on the reference Levita.
- Add persistent background X/Y movement. Images and ordinary videos are transformed into local cached working copies while imported originals remain untouched; complete TRCC layouts and `.zt` files retain their original background with an explicit compatibility notice.
- Stop appending TRCC units to formats that already contain `°C` or `%`, removing the duplicated `C`/unit text observed on hardware.
- Add two-row and vertical overlay layout presets while retaining individual X/Y, size, visibility and color controls. Overlay placement now respects the selected black-bar width.

## 3.4.29.5 INTERN

- Neutralise TRCC Linux's persisted decorative split mode before loading display media. This prevents its Qt renderer from crashing on PySide6 6.11 when TRCC 9.9.11 calls `QImage.mirrored()` with unsupported keyword arguments.
- Keep the real 80-pixel Levita cutout protected while decorative split styles A–C remain explicitly preview-only until the external backend is compatible.
- Default new split-mode settings to off and add a regression that requires the safe reset to be the first hardware command, before every media load.

## 3.4.29.4 INTERN

- Fixed startup with a previously saved Thermalright/TRCC media directory. Its first preview no longer calls the main log widget while the LCD page is still being constructed.
- Extended the real PySide6 startup regression to persist and restore an actual local display image before the Log page exists.
- Recorded the real TRCC Linux 9.9.11 hardware result for USB `87ad:70db`: the safe color cycle was visible and the authoritative handshake reported model ID 64, sub-byte 3 and 1600×720.

## 3.4.29.3 INTERN

- Replaced one `pkexec` launch per automatic fan-curve write with one authenticated, pipe-bound and strictly validated helper session. This prevents the Polkit authorization cache from expiring underneath a running Thermalright/Mainboard CPU curve after several minutes.
- Skip the unnecessary `liquidctl initialize all` call on confirmed Thermalright-only systems when no supported NZXT USB device is present. Mixed systems with a Kraken or NZXT RGB controller retain the existing initialization path.
- Hide the round Kraken clock controls while Thermalright Levita is selected and redirect any late/stale clock action to the movable Levita Display Studio clock instead of reporting a missing Kraken.
- Accept a stable removal of one or two OpenRGB devices after 2.5 seconds and persist the new expected count, while retaining the stricter cold-start safeguard for large temporary inventory drops.
- Pause an automatic Thermalright CPU curve for five minutes after a privileged-helper failure instead of repeatedly opening authentication/error dialogs from the background control timer.

## 3.4.29.2 INTERN

- Prevented `desktop_shell.py --quit` from loading the graphical Qt platform integration during logout or cleanup; the stop path now uses `QCoreApplication`, avoiding the observed SIGABRT and empty KDE helper window.
- Suppressed stale Kraken LCD profile writes when Thermalright Levita cooling is active, so startup no longer opens an error dialog for a removed Kraken.
- Made a successfully activated CPU-temperature curve replace stale manual slider values, preventing a previous 100-percent manual value from being reapplied accidentally.
- Migrated the personal PC layout from Kraken to the selected Thermalright Levita Vision 360 while retaining stable saved layout IDs.
- Added a dedicated Jungle Leopard GPU-support block and corrected its confirmed Airgoo Channel B6 configuration from 30 to 24 LEDs, separate from both ENE-DRAM modules.

## 3.4.29.1 INTERN

- Fixed the immediate 3.4.29 startup crash caused by missing explicit imports for the localized LCD GIF safety and About-page source strings after modularization.
- Added a real PySide6 offscreen startup regression that constructs all 11 main pages while suppressing hardware initialization.

## 3.4.29 INTERN

- Added a local-first Thermalright Levita Vision display studio with a 1600×720 canvas, protected 80-pixel right cutout, local TRCC/image/video import, movable CPU/GPU/RAM/clock overlays and a USB-safe test mode enabled by default.
- Added exact `Thermalright Levita Vision 360 ARGB Black` cooling selection. The display remains on USB while pump and radiator control use separately mapped motherboard `PUMP_FAN`/`CPU_FAN` PWM headers.
- Kept Levita PWM writes behind the existing physical 70-percent/10-second confirmation, CoolerControl ownership block and firmware/BIOS restoration on exit. OHC reports that this device path exposes no coolant-temperature sensor instead of fabricating one.
- Added conservative Levita Silent, Balanced, Performance and Safety duties plus CPU-temperature software curves after both channels are confirmed.
- Changed ENE-DRAM cold-start recovery from one acknowledged Direct transition to two ordered full-device passes before the saved RGB design starts. This reflects the observed controller behavior where the first successful command may not yet wake the physical LEDs.
- Added focused Thermalright cooling/display and ENE cold-start regression coverage and included all new modules in runtime/RPM packages.

## 3.4.28 INTERN

- Made chassis-fan cards start collapsed, expand only one explicit selection and close together with their embedded curve editor.
- Split chassis-fan expansion state into a small hardware-independent module and expanded the task-oriented local-AI module map.
- Fixed dynamically rebuilt chassis-fan curve buttons so they immediately use the selected interface language.
- Made the release builder skip an unavailable Debian tool cleanly on Fedora while still producing ZIP, source, Git-bundle and RPM assets.
- Normalized tar metadata timestamps to prevent invalid inherited directory dates from producing RPM warnings.

## 3.4.27 INTERN

- Distinguished the closed CoolerControl graphical client from the active `coolercontrold` background service and its system-autostart state.
- Added confirmed Polkit controls to stop CoolerControl temporarily, disable its system service permanently, or enable and start it again.
- Kept mainboard-fan ownership safe: disabling CoolerControl does not activate OHC automatically, while enabling it returns channels to firmware/BIOS control before starting the competing service.
- Unified RGB Studio, LCD, Profiles, Log, Corsair/OpenLinkHub, Settings, About, Help and Kraken detail areas with the blue-tinted dashboard card design.
- Made Kraken quick-profile buttons reflect the last successfully transmitted Leise, Ausbalanciert or Leistung profile instead of showing a static default selection.
- Added a complete LM Studio/Qwen2.5-Coder handoff with a mandatory start file, reusable initial prompt, credential-free Git bundle, repository access instructions and guarded GitHub workflow.
- Began a compatibility-preserving split of the historical main file into focused constants, temperature, privacy/logging, command-backend, cooling-widget and localization modules, with a task-oriented module map for context-limited local coding models.
- Changed chassis-fan cards to start collapsed, open only one explicitly selected card and close the associated embedded curve editor from the same card action.

## 3.4.26 INTERN

- Added repository-native long-term AI project memory through `AGENTS.md`, project status, architecture, durable decisions, device-support summary and cross-agent handoff docs.
- Added version-controlled Cursor project rules and slash workflows so fresh chats deterministically recover project constraints instead of depending on old chat context.
- Added Cursor project hooks for session context injection and explicit confirmation of destructive shell/Git commands.
- Kept GitHub publication guarded by release-channel, clean-worktree, authentication, test and explicit-approval requirements without a Google Drive or external backup dependency.

## 3.4.25 INTERN

- Added persistent sidebar customization with drag & drop, per-module visibility toggles and a one-click default reset.
- Made Overview, Navigation customization and Help permanent, non-removable safety anchors.
- Replaced the separate chassis-fan curve dialog with an embedded interactive curve card using draggable points and a synchronized value table.
- Changed built-in chassis-fan sensor defaults to CPU temperature and migrate untouched legacy `Maximum` defaults once.
- Added dynamic cooling navigation icon plus explicit RGB Studio and OpenLinkHub icons.
- Unified the modern 3.4.24 visual language across RGB Studio, LCD, Profiles, Log, OpenLinkHub, Settings, About, Help and Desktop Designs.
- Fixed privacy-redactor false positives for clearly identified four-part software versions.

# 3.4.24 INTERN

- Modernized the main PySide6 shell with persistent sidebar branding, per-page headings and compact dark dashboard styling.
- Removed the misleading “Community Edition” concept from the new design language.
- Rebuilt Overview around compact metric cards, quick actions, detected hardware and status hints.
- Rebuilt Cooling around separate CPU/Kraken and chassis-fan summaries, an inline CoolerControl ownership banner and compact system-fan cards.
- Added direct Test / Curve / Assign actions to chassis-fan cards and a dedicated curve-editing dialog.
- Reworked the chassis-fan wizard into Detect → Test → Assign → Save while preserving safe 30/80-percent contrast testing and state restoration.
- Kept NCT6687, Polkit helper, watchdog and firmware-return safety unchanged.
- Added an internal real PySide6 offscreen GUI smoke-test workflow for all major pages.

# 3.4.23.2 INTERN

- Kühlungsseite als kompaktes CPU/Kraken- und Gehäuselüfter-Dashboard neu strukturiert; Details werden nur bei Bedarf aufgeklappt.
- CPU_FAN und PUMP_FAN aus der Mainboard-Gehäuselüfterregelung ausgeschlossen, damit Kraken-Pumpe/Radiatorsteuerung nicht doppelt auftauchen oder konkurrieren.
- System-Fans als einzelne Karten mit RPM/PWM, Sensor, Profil und Kurvenvorschau; keine sichtbare verschachtelte Lüftertabelle mehr.
- CoolerControl-Ownership-Erkennung mit read-only-Sperre bei aktivem `coolercontrold`, expliziter OHC-Übernahme und sauberer Rückgabe.
- Neuer Gehäuselüfter-Assistent mit 30/80-%-Kontrasttest, 10-s-RPM-Beobachtung, vollständiger Zustandswiederherstellung, optional weißer RGB-Testbeleuchtung und gemeinsamer Gehäusezuordnung.
- PWM↔RGB-/Gehäuse-Slot-Zuordnungen werden dauerhaft gespeichert.

# 3.4.23.1 INTERN

- Privilegierter, eng begrenzter NCT6687-Fan-Helper über Polkit: die GUI bleibt unprivilegiert; der Helper akzeptiert ausschließlich validierte pwm1–pwm8-/pwm_enable-/Watchdog-Aktionen am erkannten nct6687-hwmon.
- Mainboard-Kalibrierung von 5 auf 10 Sekunden verlängert und um RPM-Beobachtung ergänzt, damit träge MSI-EC-/msi_fan_brute_force-Reaktionen zuverlässig sichtbar werden.
- NCT6687-Sofort-Readback wird nicht mehr als Zielbestätigung missverstanden: OHC bewertet Treibererfolg, RPM-Verlauf und physische Benutzerbestätigung.
- Rückgabe eines zuvor automatisch geregelten NCT6687-Kanals erfolgt über pwmN_enable=2, damit der aktuelle Treiber seine gesicherte vollständige Firmware-/MSI-Kurve selbst wiederherstellt.
- Treiber-Watchdog wird während der Regelung höchstens alle fünf Sekunden erneuert, um unnötige privilegierte Prozessstarts zu vermeiden.

# 3.4.23 INTERN

- Neue Mainboard-Lüftersteuerung über Linux-hwmon/NCT6687 mit sicherer, bestätigungspflichtiger PWM-Kalibrierung statt fester oder erratener Kanalzuordnung.
- Pro bestätigtem PWM-Kanal: eigener Name, CPU/GPU/Kühlmittel/Maximum/gewichtete Sensorquelle, Mindestleistung, Hysterese, Reaktionsverzögerung und individuelle Kurve.
- Kurvenvorlagen Leise/Ausbalanciert/Leistung mit automatischer Empfehlung als reine Vorlage; keine automatische Kanalzuordnung oder Aktivierung.
- Sensorfehler-Fallback 70 %, 100-%-Notanforderung ab 90 °C und Firmware-/BIOS-Rückgabe beim Deaktivieren bzw. Programmende.
- Treiber-/Secure-Boot-/DKMS-Diagnose sowie Fedora-Einrichtungshinweise für nct6687; keine Umgehung von Secure Boot/MOK.
- ENE-DRAM-Hinweis im RGB-Studio plus manueller Reinitialisierungsbutton für den OpenRGB-Direct-Reclaim.

# 3.4.22 INTERN


## 3.4.22.1 INTERN — ENE-DRAM cold-boot hotfix

- ENE-DRAM modules are now reclaimed once through OpenRGB's own Direct-mode driver path after a cold boot and before the saved RGB profile starts.
- The fallback is session-bounded: it runs once per managed OpenRGB engine lifetime and does not reset Direct mode on every animation frame.
- New `RGB-ENE-WAKE` log entries expose detection, reclaim and fallback status for stubborn RAM controllers.
- 3.4.23 remains reserved for the larger fan-control and hardware-control expansion.

- ENE-/OpenRGB-Stabilitäts-Hotfix: der langlebige SDK-Worker bleibt bei nativen NZXT-/GPU-Schreibvorgängen bestehen und verliert seinen vorbereiteten Direct-Zustand nicht mehr unnötig.
- RGB-Einzeltest kann das Zielgerät einmal neu primen; animierte Designs werden erst nach bestätigtem Direct-Frame und nativen Hardwarebefehlen als aktiv markiert.
- LCD-GIF-Startfehler durch die neue Skalierungsoption behoben (`prepare_gif` akzeptiert wieder den Skalierungsparameter).
- AM5-Profil lädt und aktiviert beide empfohlenen CPU-Kurven direkt, sofern der CPU-Sensor verfügbar ist.
- Mainboard-Lüftersteuerung/Cooling-Center bleibt bewusst für 3.4.23 verschoben.

# 3.4.21 INTERN

- Zentraler Kraken-USB-Koordinator mit Request-IDs, Prioritäten, Besitzerstatus, Latest-request-wins und detailliertem Log für LCD-, Cooling- und Shutdown-Zugriffe.
- RGB-Request-Koordinator fasst doppelte Aufträge zusammen, verwirft veraltete Effekte und stabilisiert den langlebigen OpenRGB-SDK-Worker.
- RGB-Profilstart wartet auf einen stabilen OpenRGB-Gerätebestand und stellt das gespeicherte Design erst danach vollständig wieder her.
- Schnellprofile bleiben Teil der Übersicht statt als elternloses Qt-Fenster beim Autostart auf dem Desktop zu erscheinen.
- Shutdown-Sicherheitsroutine stoppt einen laufenden LCD-Stream und stellt das Kraken-LCD nach Möglichkeit auf Flüssigkeitstemperatur zurück.
- Mitgelieferte LCD-Designs werden per Klick direkt aktiviert, können laufende Designs ersetzen und besitzen eine gespeicherte Skalierung sowie optionale animierte Vorschauen.
- Importierte NZXT-ESC-Profile erhalten einen Live-Renderpfad im CAM-Streamer; eingebettete Vorschauen dienen als Fallbackbasis für bewusst blockierte externe Medien.
- Geräteabhängige LCD-Zielauflösung wird in Renderer/Preview berücksichtigt; nicht verifizierte Raw-USB-Pfade bleiben gesperrt.
- LCD-Arbeitskacheln, kompakte Sticky-Vorschau und Mittelklick-Scrolling verbessern die Bedienung langer LCD-Seiten.
- Profilimport übernimmt den aktuellen Dateinamen als vorgeschlagenen Profilnamen.
- Release-/Privacy-Prüfungen werden weiter verschärft und persönliche Testbezeichnungen neutralisiert.

# 3.4.20 INTERN

- ENE-/OpenRGB-RAM erhält pro frischer RGB-Worker-Sitzung wieder ein einmaliges Direct/Custom-Priming, statt einen vorherigen OpenRGB-GUI-Kontakt vorauszusetzen. Wiederholte Mode-Resets während laufender Effekte bleiben vermieden.
- `--autostart` unterdrückt Ersteinrichtung, Profilwahl und andere modale Startdialoge vollständig; offene Einrichtung wird bis zum manuellen Öffnen zurückgestellt.
- Sprache ist die erste Seite einer frischen Einrichtung und schaltet Deutsch/Englisch/Spanisch/Französisch sofort für die folgenden Seiten um.
- Neuer fester Hilfe-Bereich unten links und F1 mit Suche, integrierten Anleitungen und direkten Sprüngen zu LCD, Kühlung, RGB, Profilen, OpenLinkHub, Designs, Autostart und Diagnose.
- LCD-Bedienung in gemeinsame Bereiche für Anzeige/Uhr, statische oder animierte Inhalte sowie Hardwaredaten/Ebenen zusammengeführt; technische FPS-/Transportwerte liegen unter den erweiterten Animationsoptionen.
- Acht eigene OHC-LCD-GIF-Themen werden reproduzierbar aus Projektquellcode erzeugt und als Galerie mitgeliefert.
- Uhr kann zusätzlich über animierte Bild/GIF- und Hardwaredaten-Ebenen gelegt werden.
- Aktuelle NZXT-ESC-v3-Exporte mit verschachteltem `preset`-Objekt werden importiert. Eingebettete `previewImage`-Daten, CSS-rgb/rgba-Farben und aktuelle Elementtypen werden gelesen; externe URL-/Video-Medien bleiben ohne automatischen Netzwerkzugriff blockiert.

# 3.4.19 INTERN

- LCD-Arbeitsbereich auf eine kompakte Kachelansicht mit drei Spalten umgestellt: Vorschau, Display und eigenes Bild liegen zusammen; Live-Hardware, Uhr, Animation, Ebenenmodus und GIF sind räumlich getrennt; die große Import-Profilverwaltung nutzt die volle Breite.
- Runde LCD-Vorschau von 300 auf 260 Pixel verkleinert, damit sie nicht mehr den oberen Arbeitsbereich dominiert.
- Helligkeit/Ausrichtung nutzen bei laufendem CAM-Raw-GIF die vorhandene koordinierte PAUSE/RESUME-USB-Übergabe statt den kompletten Stream zu stoppen und neu aufzubauen.
- Hardwareanimation und der kombinierte Bild/GIF+Hardware-Ebenenmodus rendern beim Start nicht mehr synchron im Qt-Hauptprozess. Die GUI schreibt nur noch die Spezifikation; der vorhandene Stream-Helfer erzeugt den Framecache außerhalb der Oberfläche.
- OpenRGB-Direct-Vorbereitung sendet `SET_CUSTOM_MODE` nicht erneut, wenn ein Controller Direct bereits bestätigt hat. Das verhindert insbesondere bei ENE-DRAM unnötige Modus-Resets zurück auf Firmware-/Regenbogeneffekte.
- Neue AppStream-Metadaten für Discover/Software-Center: Programmsymbol, ausführliche Beschreibung, GitHub-/Issue-/Quellcode-Verweise, Kategorien, Suchbegriffe und Screenshot-Galerie.
- Paket-Metadaten und Projektlinks auf `Frelidon/open-hardware-control` vereinheitlicht.

# 3.4.18 INTERN

- Neues zentrales `nzxt_backend.py` mit USB-ID-/Modellerkennung und Capability-Modell für Kraken 2023 (`300e`), Kraken 2023 Elite (`300c`), Kraken Elite 2024 RGB (`3012`) und Kraken Plus (`3014`).
- Kraken Elite 2024 RGB und Kraken Plus werden dynamisch als liquidctl-Geräte ausgewählt; Cooling/LCD nutzen weiterhin den seriellen liquidctl-Befehlsweg.
- 2023 Elite (`300c`) bleibt wegen des von liquidctl als defekt markierten Gerätepfads zunächst reine Erkennung ohne Schreibfreigabe.
- RGB-Fähigkeiten der 2024 Elite sind im Backend als experimentell modelliert; OHC aktiviert keine ungeprüften Raw-/HUE2-Schreibbefehle.
- udev-Regeln um `300c`, `3012` und `3014` ergänzt.

# Open Hardware Control 3.4.17 INTERN – unabhängiger NZXT-ESC-Import und LCD-Profilbibliothek

- Eigenständiger, lokal implementierter Importer für das exportierte NZXT-ESC-Presetformat; kein NZXT-ESC-Quellcode, keine Presets, Fonts oder Medien werden eingebettet.
- Pflicht-Vorschau und detaillierter Kompatibilitätsbericht vor jedem Import; externe Medien-URLs bleiben blockiert, unbekannte Ebenen werden deaktiviert erhalten statt still verworfen.
- Lokale OHC-LCD-Profilbibliothek mit Bearbeiten, Umbenennen, Duplizieren, Löschen, Export, Originalzustand, OHC-Standardkopie und vollständigem Backup/Restore.
- Einfacher Drag-and-drop-Ebeneneditor einschließlich Sensor-Remapping und optionaler automatischer Anpassung eindeutiger CPU-/GPU-Beschriftungen.
- Live-Renderer für Messwerte, Text, Trenner, Uhr und Datum auf 240×240 mit OHC-eigenen/Systemschriften und Linux-Sensorquellen.
- Live-Aktivierung nutzt denselben exklusiven LCD-Sicherheitsrahmen wie die bestehenden Hardwaredesigns, Uhr und GIF-Funktionen.

# Open Hardware Control 3.4.16 INTERN – zuverlässiges RGB-Tempo und robuste Geräteerkennung

- Fasst schnelle Regleränderungen zusammen und wendet nach einer laufenden Hardwareübertragung ausschließlich den neuesten RGB-Stand an.
- Ordnet SDK-Worker-Bestätigungen exakt ihrem Frame zu, damit verspätete Frames keinen neueren Profilstand überschreiben.
- Startet jede übernommene Softwareanimation mit definierter Phase und zeigt das bestätigte Tempo im Hardwarestatus.
- Verteilt 10–200 % gleichmäßiger auf die fünf vom NZXT-2023-Controller unterstützten Geschwindigkeitsstufen.
- Prüft den OpenRGB-Gerätebestand höchstens einmal pro Minute rein lesend und bestätigt einen großen 7→2-Abfall zweimal verzögert.
- Behält bei einem vermutlich unvollständigen Scan die letzte vollständige Liste; nur echte Änderungen bauen den RGB-Arbeitsbereich neu auf.
- Ergänzt Tests für Inventarabfälle, NZXT-Geschwindigkeitsabbildung, serielles Latest-value-wins und die automatische Hintergrundprüfung.

---

# Open Hardware Control 3.4.15 INTERN – Modusfarben, sortierbare Bereiche und Hardwareübersicht

- Ersetzt die einzelne OHC-Effekt-Auswahlliste durch eine beschreibende Modusliste mit null, einem oder zwei passenden Farbfeldern.
- Ergänzt pro Modusfarbe Hex-Eingabe, Standardfarben und Farbdialog; vorhandene Profile behalten `primary` und `secondary` unverändert.
- Ordnet RGB standardmäßig als Engine → Geräte und Effekte → Thermaltake-PC-Aufbau → Gruppen.
- Macht die Hauptbereiche in RGB, LCD und Kühlung per Drag-and-drop sowie ↑/↓ sortierbar und speichert jede Reihenfolge in `QSettings`.
- Ergänzt die Übersicht um CPU-Modell, Kerne/Threads, GPU-Modell, VRAM, Treiber und PCI-Pfad.
- Ermöglicht das einzelne Aus- und Einblenden aller Hardwarekarten sowie das Wiederherstellen des Standardzustands.

---

# Open Hardware Control 3.4.13 INTERN – direkte RGB-Kacheln und sichere Wiederübernahme

- Ein Klick auf eine RGB-Designkachel wendet das Muster nach der vorhandenen Sitzungsfreigabe direkt auf die ausgewählten Geräte an.
- Ergänzt „Feste Farbe“ als eigene Kachel; eine geänderte Hauptfarbe wird bei aktiver Freigabe unmittelbar erneut übertragen.
- Trennt sichtbar zwischen dem ausgewählten Muster und einem durch die lokale Übertragung bestätigten aktiven Muster. Ein großes Statusfeld und starke, dauerhafte Kachelrahmen machen beide Zustände erkennbar.
- Ergänzt „RGB-Steuerung neu übernehmen“: OHC verwirft nur seinen eigenen vorbereiteten SDK-Zustand, erkennt die Geräte neu und wendet anschließend die aktuelle Auswahl erneut an.
- Ergänzt eine standardmäßig ausgeschaltete automatische Wiederübernahme. Sie beobachtet ausschließlich, ob ein separates OpenRGB beendet wurde; der fremde Prozess wird niemals beendet.
- Ein noch laufender fremder Prozess oder ein nicht OHC zugeordneter SDK-Server blockiert alle Schreibzugriffe weiterhin sicher. Ein kurz nachlaufender Server wird begrenzt erneut geprüft.
- Speichert die freiwillige Wiederübernahmeoption in RGB- und Gesamtprofilen, übernimmt dabei aber keine zuvor unbestätigte Hardwarefreigabe.
- Hebt den inoffiziellen, unabhängigen Projektstatus in Anwendung und Dokumentation deutlicher hervor.

---

# Open Hardware Control 3.4.12 INTERN – RGB-Galerie, physische Kraken-Reihenfolge und LCD-Ebenen

- Die Thermaltake-PC-Ansicht zeigt Kraken-Kanal 1/2/3 und speichert deren per Drag-and-drop festgelegte physische Reihenfolge; Frelidons Vorgabe ist links/rear `2`, Mitte `3`, rechts/front `1`.
- „Animation anhalten“ bewahrt die RGB-Seitenposition bereits vor allen Widget- und Prozessänderungen und stellt sie auch nach der seriellen NZXT-Sequenz wieder her.
- 17 vollständig eigene, prozedurale RGB-Presets werden als laufende Vorschaukacheln in sechs Kategorien dargestellt.
- Ein RGB-/Gesamtprofil kann ausdrücklich den sicheren RGB-Start speichern. Standard bleibt aus; ein separates OpenRGB oder eine zweite OHC-Instanz blockiert weiterhin.
- Der neue LCD-Ebenenmodus kombiniert ein ausgewähltes Bild/GIF mit fester oder animierter Hardwareanzeige. Deckkraft, Skalierung und X/Y-Position sind einstellbar; CPU/GPU bleiben im phasenstabilen Stream live.
- Neue eigene LCD-Layouts: Neonraster, Radar und Wellenkern. Es werden keine NZXT-, be-quiet!- oder SignalRGB-Assets eingebettet.

# Open Hardware Control 3.4.11 INTERN – flüssige Mehrgeräteframes und RGB-Einrichtungsassistent

- Ersetzt den pro Animationsframe neu gestarteten Python-/TCP-Einzelgerätepfad durch einen dauerhaften, isolierten und ausschließlich an Loopback gebundenen OpenRGB-SDK-Worker.
- Bereitet alle gewählten Direct-Geräte einmal vor und sendet danach pro 40-ms-Takt einen gemeinsamen vollständigen Mehrgeräteframe; dadurch wird der frühere Round-Robin-Durchsatz von ungefähr 2 Hz je Gerät bei fünf Geräten beseitigt.
- Hält höchstens einen Frame offen und fasst überholte Zwischenbilder nach dem Latest-frame-wins-Prinzip zusammen, sodass ein langsamer Controller keine unbeschränkte Prozess- oder Framewarteschlange erzeugt.
- Zeigt je Gerät die tatsächlich abgeschlossene SDK-Rate, den Zeitpunkt des letzten Erfolgs, Batch-Dauer und zusammengefasste Frames; die physische Lichtausgabe bleibt ausdrücklich nicht rücklesbar.
- Ergänzt einen sechsstufigen Einrichtungsassistenten für OpenRGB-/ckb-next-/OpenLinkHub-Besitz, Gerätebenennung, isolierten Test, LED-Zonen, Thermaltake-PC-Aufbau und Sapphire-External-Control.
- Ergänzt im Zonendialog einen Sichttest pro Zone. Dabei leuchtet nur die gewählte Zone des Controllers in der Testfarbe, während dessen übrige Zonen schwarz bleiben.
- Bevorzugt für Nicht-Direct-OHC-Animationen automatisch den tatsächlich gemeldeten Modus `External Control`; bei Frelidons System betrifft dies die Sapphire RX 9070 XT.
- Behält Sitzungsfreigabe, Einzelinstanz-Sperre, fremde-OpenRGB-Blockade, per-Gerät-Fehlerisolation, sicheren Reset und die getrennte NZXT-/liquidctl-Steuerung bei.
- Ergänzt einen Protokolltest, der zwei Frames über dieselbe Verbindung sendet und bestätigt, dass Direct-Vorbereitung und Zonen-Fallback nur beim ersten Frame stattfinden.
- Bleibt intern; die reale Airgoo-/MSI-/RAM-/GPU-Hardwareprüfung ist vor einer öffentlichen Veröffentlichung weiterhin erforderlich.

---

# Open Hardware Control 3.4.10 INTERN – vollständige Geräteframes und Interstellar-V2-Profil

- Sendet Direct-Farben immer als vollständigen OpenRGB-`UPDATELEDS`-Geräteframe. Beim ersten Direct-Wechsel wird eine vollständige Zonenabbildung zusätzlich einmal über `UPDATEZONELEDS` gesendet; nachfolgende Animationsframes vermeiden diesen doppelten Pfad.
- Trennt die SDK-Serverbestätigung ausdrücklich von der physisch nicht rücklesbaren ARGB-Ausgabe, damit ein bestätigter Farbpuffer nicht mehr als sichtbarer Hardwareerfolg missverstanden wird.
- Ergänzt TZMRIT/Jungle-Leopard Interstellar V2 Normal und Reverse als Lüftermodelle mit jeweils 24 adressierbaren LEDs.
- Übernimmt die Lüfterzahl aus der PC-Ansicht, setzt unzugeordnete Hub-Zonen im Modellvorschlag auf 0 und lässt bekannte Komponentenanschlüsse wie B6 zur manuellen Einstellung bestehen.
- Warnt vor unplausiblen Lüfter-/LED-Werten und ungewöhnlich großen Zonen, ohne eine technisch nicht mögliche elektrische Autoerkennung zu behaupten.
- Behandelt sichere Zonen-/Konfigurationsfehler ohne Gerätesperre; bestätigte OpenRGB-Backend-Abstürze bleiben pro Gerät isoliert.
- Ergänzt die Konfliktdiagnose um ckb-next und nennt Überschneidungen mit OpenLinkHub beziehungsweise getrennt laufendem OpenRGB.
- Vergrößert die sichtbare Auswahlliste und stellt RGB-Seiten- sowie Navigationsscrollposition nach mehreren Qt-Layoutphasen robuster wieder her.
- Ergänzt Protokolltests für vollständigen Geräteframe, einmaligen Zonen-Fallback, reine Folgeframes, SDK 4/5, Interstellar-Profile und Konflikt-/Konfigurationsklassifizierung.
- Bleibt intern; es erfolgt keine öffentliche GitHub-Veröffentlichung.

---

# Open Hardware Control 3.4.9 INTERN – ARGB-Zonengrößen und schnellere NZXT-Reaktion

- Erkennt den real bestätigten Zustand von MSI MYSTIC LIGHT und Airgoo AG-DRGB16 mit vorhandenen Kanalnamen, aber null angelegten OpenRGB-Farbplätzen, als fehlende Zonenkonfiguration statt als allgemeinen Schreibfehler.
- Ergänzt einen eigenen Dialog für Lüfter/Geräte und LEDs je Lüfter/Gerät pro OpenRGB-Zone. OHC berechnet daraus die Gesamtzahl, prüft die vom SDK gemeldeten Mindest-/Höchstwerte und speichert die Zuordnung in Einstellungen sowie RGB-/Gesamtprofilen.
- Liest dafür die vollständigen SDK-Zonendaten einschließlich aktueller Größe, Grenzen und Änderbarkeit und verwendet ausschließlich den offiziell dokumentierten `RESIZEZONE`-Befehl vor Direct Mode und Farbwrite.
- Übernimmt bekannte Lüfterzahlen aus Frelidons Thermaltake-Ansicht als sichtbaren Vorschlag für A1/A2; die modellabhängige LED-Zahl wird aus Sicherheitsgründen nicht erfunden.
- Behandelt „0 angelegte LEDs“ in Softwareanimationen als Einrichtungshinweis, entfernt das Gerät aus der laufenden Animation und setzt ausdrücklich keine Sitzungssperre.
- Unterscheidet im Status zwischen wirklich von OpenRGB gelisteten LEDs, gespeicherten OHC-Zonengrößen und einem nur serverseitig bestätigten Farbzustand.
- Priorisiert den getrennten NZXT-/liquidctl-Auftrag vor seriellen OpenRGB-Rücklesungen, damit die Kraken bei einer gemeinsamen Aktion nicht hinter mehreren SDK-Transaktionen wartet.
- Ergänzt Protokolltests für leere vergrößerbare Zonen, `RESIZEZONE`, anschließende Zonenwrites und Rücklesebestätigung sowie Tests für persistente `Lüfter × LEDs`-Berechnung.
- Bleibt intern; es erfolgt keine öffentliche GitHub-Veröffentlichung.

---

# Open Hardware Control 3.4.8 INTERN – bestätigte Zonenwrites und exklusiver OpenRGB-Prozess

- Liest vor jedem Direct-Write die aktuelle OpenRGB-Geräteanzahl und vollständige Controllerbeschreibung; veraltete Geräteindizes können dadurch nicht auf einen anderen Controller zeigen.
- Verwendet für vollständig abgebildete Controller die SDK-Zonenpakete statt eines unbestätigten globalen Farbaufrufs. Das adressiert insbesondere die gemeldeten ENE-DRAM-, MSI-MYSTIC-LIGHT- und Airgoo-Zonen.
- Handelt SDK-Protokoll 4/5 aus, prüft den tatsächlich aktiven Direct-/Custom-Modus und übernimmt die vom SDK gemeldete Farbpuffergröße als verbindlich.
- Liest nach jedem Farbauftrag den Controllerzustand zurück. „OpenRGB-Zustand bestätigt“ erscheint nur, wenn Modus und kompletter Farbpuffer dem Ziel entsprechen; andernfalls wird das konkrete Gerät als Fehler ausgegeben.
- Erkennt eine separat laufende OpenRGB-Oberfläche auch dann über `/proc`, wenn ihr SDK-Server ausgeschaltet ist. OHC startet in diesem Fall keine eigene Engine und keinen RGB-Auftrag, sondern nennt die konkurrierende PID.
- Fasst eine gemeinsame Auswahl aller drei NZXT-RGB-Kanäle zum auf der Referenzhardware bereits bestätigten `sync`-Pfad zusammen. Einzelkanalwahl und topology-sensitive Effekte bleiben erhalten.
- Ergänzt synthetische Protokoll-4/5-Servertests, Zonen-/Rücklesetests, Prozesskollisionstests und NZXT-Kanaltests.
- Bleibt intern; es erfolgt keine öffentliche GitHub-Veröffentlichung.

---

# Open Hardware Control 3.4.7 INTERN – SDK-5-Kompatibilität, NZXT-Fallback und harte Einzelinstanz

- Behebt den real bestätigten RAM-Fehler „OpenRGB-SDK-Protokollversion 5; erwartet wird 4“: Der begrenzte Loopback-Schreiber fordert jetzt Revision 5 an, akzeptiert Server ab Revision 4 und verwendet wie der offizielle OpenRGB-Client die niedrigere beider unterstützten Revisionen.
- Ergänzt Regressionstests für OpenRGB-SDK 5, den kompatiblen Altpfad 4 und die sichere Ablehnung zu alter Serverversionen.
- Entfernt die auf dem NZXT 2023 RGB Controller von liquidctl 1.16.0 nicht unterstützten Aliasse `marquee-4` und `moving-alternating-4`.
- Ordnet OHC-„Glut-Komet“ dem gültigen NZXT-Modus `pulse`, den Kreisel `rainbow-flow` und Abwechselnd `alternating-4` zu; dadurch endet die Aktion nicht mehr in `KeyError('marquee-4')`.
- Fügt eine separate Kernel-Dateisperre für die gesamte Anwendung hinzu. Sie wird vor Qt-Fenster, OpenRGB-Engine, liquidctl-Backend und Kraken-Zugriff erworben und über einen nicht vererbbaren Dateideskriptor bis zum Programmende gehalten.
- Ein zweiter Start zeigt ausschließlich einen Hinweis mit der Besitzer-PID und endet ohne Hardwarezugriff. Kann die Sperre aus einem anderen Grund nicht angelegt werden, startet OHC sicherheitshalber ebenfalls nicht.
- Das Diagnoseprotokoll bestätigte zusätzlich, dass OpenRGB im Fehlerzeitpunkt bereits als von OHC verwalteter Kindprozess lief; ein manuell offenes OpenRGB war nicht die Ursache.
- Bleibt intern; es erfolgt keine öffentliche GitHub-Veröffentlichung.

---

# Open Hardware Control 3.4.6 INTERN – sichtbare Auswahl, Gerätefehler-Isolation und stabiler Bedienzustand

- Ersetzt die kaum lesbare Einzeilen-Zusammenfassung der ausgewählten Kacheln durch eine große Liste mit Gerätename, zuständigem Steuerweg und letztem Schreibergebnis.
- Kennzeichnet den früheren „nativen Gerätemodus“ als GPU-/Hardwaremodus und nennt die tatsächlich betroffenen Nicht-Direct-Geräte; bei Frelidons System ist dies vor allem die Sapphire RX 9070 XT.
- Trennt den expliziten GPU-Modus von automatischen OHC-Effekt-Fallbacks, sodass ein in der Liste stehender Off-/Dark-Modus nicht mehr unbeabsichtigt beim Start eines OHC-Effekts verwendet wird.
- Initialisiert den Direct-/Custom-Modus pro Gerät und verwalteter Engine nur einmal; wiederholte statische Farben und Testdurchläufe senden nicht jedes Mal erneut `SETCUSTOMMODE`.
- Führt serielle Mehrgeräteaktionen auch nach gewöhnlichen Einzelgerätefehlern weiter, speichert den Status am betroffenen Gerät und zeigt am Ende eine gemeinsame verständliche Fehlerübersicht.
- Entfernt das bereits durch das NZXT-/`liquidctl`-Modul vertretene OpenRGB-NZXT-Duplikat aus den normalen Kacheln und Testgeräten, ohne die drei real steuerbaren NZXT-Kanäle zu verlieren.
- Bewahrt RGB-Seiten- und Navigationsscrollposition nach Kachelumbau, Befehlsende und Dialogrückkehr über mehrere Qt-Ereignisrunden; doppelte unnötige Kachel-Neuaufbauten wurden entfernt.
- Schreibt das bereinigte Anwendungsprotokoll automatisch als aktuelle und vorherige Sitzung in das XDG-State-Verzeichnis. Der Diagnosebericht übernimmt beide Logs sowie OpenRGB-Coredump- und Journal-Auszüge.
- Der Diagnosebericht nennt zusätzlich OpenRGB-Paket, laufenden Prozess, Elternprozess und den lokalen SDK-Port; damit ist eine fremd gestartete Instanz von der durch OHC verwalteten Engine unterscheidbar.
- Bleibt intern; es erfolgt keine öffentliche GitHub-Veröffentlichung.

---

# Open Hardware Control 3.4.5 INTERN – lokaler SDK-Schreibpfad und vollständiger Layout-Editor

- Wertet den Fedora-Coredump des gültigen Befehls `openrgb --client 127.0.0.1:6742 --device 6 --color 4c00e6` aus: Der Abbruch liegt in OpenRGB `1.0~rc2` innerhalb von `ApplyOptions`/`std::vector::operator[]`, nicht in der OHC-Auswahl.
- Fügt einen eigenen, kleinen GPLv3-OpenRGB-SDK-Schreibhelfer hinzu, der ausschließlich Loopback akzeptiert und keine Controllerprotokolle oder OpenRGB-Treiber kopiert.
- Verhandelt exakt SDK-Protokollversion 4 und begrenzt Paketgröße, Gerät, LED-Anzahl und RGB-Werte vor jeder Übertragung.
- Schreibt Direct-Geräte bei statischen Farben, Softwareanimationen und im Einzelgerätetest ohne OpenRGB-Kommandozeilenparser; damit erreichen MSI MYSTIC LIGHT und Airgoo AG-DRGB16 nicht mehr den bestätigten `ApplyOptions`-Absturzpfad.
- Verwendet OpenRGB-CLI-Modi nur noch für Geräte ohne Direct Mode; Direct-Geräte erhalten ihre OHC-Effekte ausschließlich über den lokalen SDK-Pfad.
- Bewahrt beim dynamischen Neubau von Gerätekacheln und Gruppen die horizontale und vertikale Scrollposition der RGB-Seite.
- Migriert Frelidons Thermaltake-Profil auf getrennte Blöcke für 3× Kraken oben, 2× Front, 3× Rückwand/Seite Reverse, 3× Netzteilabdeckung vorne Reverse und 1× Heck – insgesamt 12 Lüfter.
- Ergänzt Markieren, Hinzufügen, Bearbeiten, Entfernen und automatische Grundanordnung von Lüfter-/Komponentenblöcken.
- Kennzeichnet die physische Einschränkung gespiegelter Hubs: Meldet das Backend nur eine logische LED, können die angeschlossenen Lüfter nur gemeinsam gefärbt werden.

---

# Open Hardware Control 3.4.4 INTERN – Reset-Race, Spiegelinventar und Thermaltake-PC-Ansicht

- Behebt den im realen Testprotokoll bestätigten Wettlauf zwischen „RGB-Geräte neu erkennen“ und dem noch laufenden Komplett-Reset.
- Verwirft Erkennungsergebnisse, die vor einem Reset oder Engine-Neustart begonnen wurden, und leert danach alle nicht mehr erreichbaren OpenRGB-Kacheln.
- Merkt einen während des Resets angeforderten Neustart vor und führt ihn erst nach tatsächlicher Beendigung des verwalteten OpenRGB-Prozesses aus.
- Aktiviert eine bestätigte RGB-Schreibsitzung erst, nachdem die Engine erreichbar und eine neue Geräteliste erfolgreich eingelesen wurde.
- Erkennt das vollständig gespiegelte OpenRGB-Inventar `0…6` plus `7…13` und entfernt nur bei exakter Gesamtübereinstimmung die zweite Hälfte.
- Führt zusätzlich Geräte mit gleicher belastbarer Seriennummer oder gleichem vollständigem Hardwarepfad zusammen, ohne zwei echte gleichnamige RAM-Riegel zu verschmelzen.
- Protokolliert Quellnamen und gemeldete OpenRGB-Zonen für die spätere Zuordnung von Airgoo-Hub-Ports und angeschlossenen Komponenten.
- Ersetzt den alten PC-Positionsformularblock durch eine große verschiebbare Thermaltake-Ansicht mit Drag & Drop und automatischer Gehäusezonenerkennung.
- Liefert Frelidons aktuellen 120-mm-Aufbau: Kraken 360 oben, zwei Frontlüfter, drei Reverse-Lüfter an Rückwand/Seite, drei Reverse-Lüfter am Boden und einen Heck-Abluftlüfter.
- Bewahrt Gerätenamen, Gruppen und Anschlusshinweise; alte Frelidons-Layoutdaten werden einmalig auf das neue Layoutschema migriert.

---

# Open Hardware Control 3.4.3 INTERN – gerätespezifische OpenRGB-Absturzisolierung

- Wertet vier neue Fedora-Coredumps aus: OpenRGB `1.0~rc2` bricht in `ApplyOptions` auch bei gültigen statischen Einzelgerätebefehlen und gültigen Direct-Mode-Einzelgerätebefehlen ab.
- Erkennt die charakteristische `stl_vector`-/`__n < this->size()`-Assertion und sperrt ausschließlich das verursachende Gerät für die aktuelle OHC-Sitzung.
- Führt serielle RGB-Befehlsfolgen nach einem isolierten Gerät weiter; der Einzelgeräte-Test erreicht dadurch weiterhin sein absichtlich zuletzt geschriebenes Ziel.
- Zeigt die Sitzungssperre an der betroffenen Gerätekachel und in einer zusammengefassten Warnung statt den vollständigen C++-Assertionstext als anklickbaren Fehler darzustellen.
- Zählt gewöhnliche Direct-Mode-Fehler getrennt pro Gerät. Erfolgreiche Frames anderer Geräte setzen diesen Zähler nicht mehr zurück.
- Entfernt ein Gerät nach dem ersten bestätigten OpenRGB-Prozessabsturz beziehungsweise nach drei eigenen gewöhnlichen Schreibfehlern aus der laufenden Softwareanimation; andere Geräte und NZXT-Hardwareeffekte laufen weiter.
- Protokolliert OpenRGB-Geräteindex, Alias, LED-Anzahl und Direct-Fähigkeit, damit künftige Hardwareprotokolle eindeutig zugeordnet werden können.
- Die Quarantäne ist nicht persistent und wird bei jedem neuen OHC-Prozess zurückgesetzt.

---

# Open Hardware Control 3.4.2 INTERN – Start-Hotfix und automatische Absturzprotokolle

- Behebt den durch das reale Fedora-Startprotokoll bestätigten sofortigen Absturz: `update_rgb_studio_preview()` wurde während `build_ui()` aufgerufen, bevor `rgb_preview_started` existierte.
- Initialisiert die RGB-Vorschauuhr nun vor dem Aufbau sämtlicher UI-Bereiche und verwendet zusätzlich einen defensiven Fallback.
- Neuer Regressionstest prüft ausdrücklich, dass die Vorschauuhr vor `build_ui()` gesetzt wird.
- Schreibt private, anonymisierte Lebenszyklusereignisse nach `~/.local/state/open-hardware-control/startup.log`.
- Schreibt die letzte unbehandelte Python-Ausnahme automatisch nach `~/.local/state/open-hardware-control/last-crash.log`.
- Der read-only Diagnosebericht übernimmt die letzten Startzeilen und den letzten Absturz automatisch.

---

# Open Hardware Control 3.4.1 INTERN – RGB-Stabilität und PC-Skizze

- Behebt den durch die Testprotokolle bestätigten OpenRGB-1.0~rc2-Absturz in `ApplyOptions`: kein Aufruf enthält mehr mehrere `--device`-Blöcke.
- Statische Farben, native Modi, Resetaufträge und Direct-Frames werden als validierte Einzelgerätebefehle seriell abgearbeitet.
- Direct-Mode-Animationen rotieren mit global höchstens zehn Geräteframes pro Sekunde durch die aktiven Geräte.
- Geräte ohne Direct Mode blockieren eine gemischte Auswahl nicht mehr, sondern erhalten einen passenden tatsächlich gemeldeten Hardwaremodus; „Blitze“ bevorzugt `Random Flicker`.
- Behebt das vorzeitige Löschen gespeicherter Auswahl- und Gruppenzuordnungen vor Abschluss der asynchronen Geräteerkennung.
- „Alle auswählen“ ist oberhalb und als großer Knopf unterhalb des Kachelbereichs verfügbar.
- Neue Gruppen übernehmen die aktuell ausgewählten Kacheln direkt.
- Gleichnamige GPU-/Controllergeräte werden als getrennte nummerierte Kacheln angezeigt und können dauerhaft benannt werden.
- Neuer Geräte-Testmodus: genau eine Komponente erhält eine frei wählbare Testfarbe, während alle anderen von OHC steuerbaren Geräte seriell ausgeschaltet werden; Wechsel zum nächsten Gerät und direktes Umbenennen sind integriert.
- Neue generische PC-Skizze mit Position, Name, Anzahl, Anschlussnotiz, Gruppe und Gerätekachelzuordnung.
- Mitgelieferte Vorlage „Frelidons PC“ enthält Kraken-Radiator, A1/A2, B6/B7, `SYS-FAN6`, GPU, GPU-Halterung und zwei RAM-Riegel.
- Die separate sichtbare NZXT-RGB-Steuerbox wurde entfernt; die drei NZXT-Kanäle liegen vollständig im gemeinsamen Arbeitsbereich.
- Profile speichern nun auch eigene Gerätenamen und die PC-Skizze; das frühere unbeabsichtigte direkte NZXT-Anwenden beim Profilimport entfällt.
- Der große Komplett-Zurücksetzen-Knopf bleibt unverändert verfügbar.

---

# Open Hardware Control 3.4.0 INTERN – verwaltete RGB-Engine, Gruppen und Komplett-Reset

- OHC startet und beendet die installierte RGB-Hardware-Engine selbst als privaten, fensterlosen Kindprozess; ein manueller OpenRGB-Serverstart entfällt.
- Fremd gestartete OpenRGB-Instanzen werden sichtbar erkannt und für OHC-Schreibzugriffe gesperrt.
- Prozesssperre verhindert zwei gleichzeitig schreibende Open-Hardware-Control-Instanzen.
- Neue quadratische Gerätekacheln mit Mehrfachauswahl und Drag & Drop in frei benennbare Gruppen.
- Gruppen besitzen unabhängige Effektkonfigurationen und werden in Einstellungen sowie RGB-/Gesamtprofilen gespeichert.
- NZXT-Kanäle und zusätzliche RGB-Geräte können gemeinsam oder getrennt ausgewählt werden.
- ENE-DRAM-Aliase wie `ENE DRAM DRAM` werden paarweise entfernt; zwei echte Speicherriegel und deren vollständige LED-Listen bleiben erhalten.
- NZXT-Modi werden über eine feste Positivliste validiert; topology-sensitive Effekte wie „Flügel“ werden bei `sync` getrennt auf `led1` bis `led3` angewendet.
- Großer bestätigungspflichtiger Komplett-Zurücksetzen-Knopf stoppt Animationen, setzt verfügbare Hardwarestandards, entzieht die Sitzungserlaubnis und gibt die Engine frei.
- Sammelbefehle steuern bis zu 64 ausgewählte Geräte mit weiterhin höchstens einem Prozess und zehn Frames pro Sekunde.
- OpenRGB-/Effects-Plugin-Code bleibt getrennt; neue Module `rgb_devices.py` und `nzxt_rgb.py` sind eigener GPLv3-Code.

---

# Open Hardware Control 3.3.0 INTERN – RGB-Studio und experimentelle Desktop-Designs opt-in

- Neues eigenes RGB-Studio für zusätzliche, von einem lokalen OpenRGB-SDK-Server gemeldete Geräte.
- Statische Farbe pro Gerät, gemeldete native Modi, LED-/Zoneninformationen und Direct-Mode-Prüfung.
- Zehn originale prozedurale OHC-Effekte und sieben Designvorlagen mit Live-Vorschau.
- Profilintegration für Gerät, Effekt, Farben, Helligkeit, Geschwindigkeit und Richtung; Hardwarestart bleibt manuell.
- OpenRGB-Schreibzugriffe sind sitzungsweise gesperrt und ausschließlich auf `127.0.0.1:6742` im expliziten Clientmodus begrenzt.
- Besitzsperren verhindern konkurrierende OpenRGB-Schreibzugriffe auf aktive NZXT- und OpenLinkHub-/Corsair-Geräte.
- Softwareanimationen verwenden höchstens einen Frameprozess, 10 Hz Obergrenze und automatischen Stopp nach drei Fehlern.
- Optionales OpenRGB-Paketangebot für DNF, APT, Pacman und Zypper; Fedora ergänzt `openrgb-udev-rules`.
- Kein OpenRGB-/Effects-Plugin-Quellcode und keine fremden Effektassets eingebettet.
- Desktop-Designs sind ausdrücklich experimentell, standardmäßig ausgeschaltet und aus Menü/Navigation verborgen.
- Neue RGB-Studio-, Lizenz-, Sicherheits-, Parser- und Effekt-Regressionstests.

---

# Open Hardware Control 3.2.0 INTERN – Windows 8/8.1, freie Desktop-Assets und Design-Backups

- Windows-8- und Windows-8.1-artige KDE-Plasma-Anordnungen mit eigener bildschirmfüllender Kachelübersicht.
- Schwarze Charms-Leiste über obere/untere rechte Bildschirmecke und `Super+C`; Mehrbildschirm-Geometrien werden getrennt berücksichtigt.
- Die Kachelübersicht liest nur lokale `.desktop`-Einträge und startet Programme ohne Shell; Online-Kacheln und freie Benutzerbefehle sind ausgeschlossen.
- Umschaltbare KDE-Standardsymbole sowie originale OHC-GPL-Symbol- und Mauszeigerpakete für Windowed 11, Orchard/macOS-artig und Metro 8.
- Keine proprietären Microsoft-/Apple-Dateien, keine fremden Designarchive und keine automatischen Downloads.
- Auswählbare Desktop-Backups, einstellbare Aufbewahrungsanzahl, Löschen sowie SHA-256-geschützter ZIP-Export und streng geprüfter Import.
- Transaktionsmarker erkennt unterbrochenes Anwenden; automatische Rückkehr zum Backup und bei beschädigtem Backup zu KDE Breeze Light.
- Abhängigkeitshilfe umfasst QtNetwork/QtDBus für DNF, APT, Pacman und Zypper.
- TiledScreen wurde auf festgehaltenem Quellstand geprüft, aber wegen beliebiger Kachelbefehle, Online-Add-ons und unsicherer Archiv-/Pfadbehandlung nicht eingebettet.
- Windows XT, Vista und Windows 7 bleiben als Wünsche für spätere Versionen dokumentiert.
- Hardwaresteuerung, CAM-Raw-LCD-Streaming, CPU-Kurven und koordinierte Kraken-USB-Pausen bleiben unverändert.

---

# Open Hardware Control 3.1.1 INTERN – Fedora-qdbus-Korrektur und Paketangebot

- Fedora 44 wird mit dem dort bereitgestellten Programmnamen `qdbus-qt6` ohne lokalen Hilfslink erkannt.
- Zusätzlich werden `qdbus6` und die bekannten distributionsabhängigen Qt6-Systempfade sicher unterstützt.
- Fehlende KDE-Desktop-Werkzeuge werden einmal automatisch angeboten und können dauerhaft über den Desktop-Design-Bereich installiert werden.
- Feste Paketzuordnungen decken DNF, APT, Pacman und Zypper ab; es werden keine fremden Paketquellen hinzugefügt.
- Desktop-Werkzeuge bleiben optionale Abhängigkeiten und blockieren weder NZXT- noch OpenLinkHub-Funktionen.
- Nach der Paketinstallation werden Kompatibilität und Schaltflächen automatisch erneut geprüft.
- Alle LCD-, GIF-, Kühlungs-, Profil-, OpenLinkHub- und Sicherheitsregressionstests aus 3.1.0 bleiben erhalten.

---

# Open Hardware Control 3.1.0 INTERN – reversible KDE-Desktop-Designs

- Neuer Bereich **System → Desktop-Designs** für KDE Plasma 6.
- Windows-11-artige Anordnung mit unterer 48-Pixel-Leiste, mittigem Starter-/Programmbereich und Systembereich rechts.
- macOS-artige Anordnung mit oberer Systemleiste, zentriertem Auto-Hide-Dock und Fensterschaltflächen links.
- Beide Anordnungen verwenden ausschließlich vorhandene KDE-Breeze-Komponenten, Noto Sans und eigene GPL-SVG-Hintergründe.
- Vorschau und ausdrücklicher Bestätigungsdialog sind vom tatsächlichen Anwenden getrennt.
- Vor jeder Änderung wird ein datiertes Backup aller berührten KDE-/Plasma-Konfigurationsdateien angelegt.
- Fehler während des Anwendens lösen eine automatische Wiederherstellung des unmittelbar zuvor erzeugten Backups aus.
- Das letzte Desktop-Backup kann aus der Oberfläche wiederhergestellt werden.
- Das Modul benötigt keine Administratorrechte, lädt keine Designs herunter und führt keine beliebigen Shellbefehle aus.
- Interne ZIP-, DEB- und RPM-Namen tragen eine eindeutige INTERN-/intern1-Kennzeichnung.
- `BUILD_CHANNEL=INTERN` blockiert die mitgelieferten öffentlichen GitHub-Veröffentlichungsskripte.
- Sämtliche Funktionen aus 3.0.9 für OpenLinkHub-Maustasten/Makros, LCD-Stile, Fahrenheit, CPU-Kurven, Tray und geordnetes LCD-Zurücksetzen bleiben erhalten.

---

# Open Hardware Control 3.0.9 – Maustasten/Makros, saubere LCD-Werte und Fahrenheit

- Erste öffentliche Open-Hardware-Control-Version auf Basis der vollständig geprüften internen 3.0.x-Reihe.
- Release-Artefakte für Fedora/Nobara (`.rpm`), Debian/Ubuntu/Mint (`.deb`), ein universelles Installations-ZIP sowie das vollständige `Entwicklerpaket 3.0.9`.
- Distributionsabhängige Installation für DNF, APT, Pacman und Zypper mit klaren Befehlen aus `~/Downloads`.
- Suchfreundliche Projektbeschreibung für NZXT Kraken, Kraken LCD, Linux, liquidctl, fan control, Corsair und OpenLinkHub.
- Gemeldete OpenLinkHub-Maustasten öffnen direkt aus SVG oder Tabelle einen Belegungsdialog.
- Dokumentierte API-Unterstützung für Medien-, DPI-, Tastatur-, Sniper-, Maus- und vorhandene Makrofunktionen sowie Originalfunktion, Gedrückthalten und Ausführen beim Loslassen.
- Neue Makroaufnahme für einzelne Tastendrücke und Pausen, begrenzt auf das sichtbare aktive Dialogfenster und 64 Schritte.
- Eingabekataloge und Makronamen werden über die dokumentierten lokalen Endpunkte gelesen, bereinigt und begrenzt.
- LCD-Hardwaredesigns entfernen kleine LIVE-/LETZTER-WERT-/KRAKEN-CONTROL-Zusätze.
- Beschriftung und Temperaturzahl besitzen getrennte Hex-Farben und getrennte Größen von 60 bis 200 Prozent.
- Celsius/Fahrenheit ist eine globale, profilfähige Anzeigeeinstellung für Dashboard, Status, Kurven, Sicherheitsgrenzen und LCD-Hardwareanimationen.
- Kurven- und Sicherheitslogik bleiben intern in Celsius, damit ein Einheitenwechsel die Hardwarewirkung nicht verändert.
- Eine laufende generierte Hardwareanimation wird beim Einheitenwechsel kontrolliert beendet, neu gerendert und wieder gestartet.

---

# Open Hardware Control 3.0.6 – LCD-Profilstart und zuverlässiger Tray-Autostart

- Profile speichern nun ausdrücklich den aktiven LCD-Modus: Einzelbild, Bild-Wiederholung, Uhr, statisches Hardwaredesign, Hardwareanimation oder normales GIF.
- Ein beim Aktualisieren des Profils laufendes GIF wird beim nächsten Start wieder als Animation geladen und nicht nur als erstes Standbild.
- Vorhandene 3.0.5-LCD-Profile ohne Modusfeld migrieren `.gif`-Dateien automatisch zum GIF-Streamer und statische Dateien zum Einzelbildmodus.
- Beim Desktop-Autostart wird die LCD-Wiederherstellung bis fünf Sekunden nach Programmstart verzögert; der normale manuelle Start behält die bisherige kurze Verzögerung.
- Gesamtprofile dürfen ihren gespeicherten maximierten/normalen Fensterzustand während des Tray-Autostarts nicht anwenden. Dadurch bleibt das Hauptfenster zuverlässig verborgen beziehungsweise minimiert.
- Nach dem Laden des Startprofils wird der gewünschte Autostart-Fensterzustand nochmals abgesichert.
- Nur Startprofile mit einem tatsächlichen LCD-Anteil besitzen beim Start das Display; reine Kühl- oder Designprofile blockieren die globale LCD-Wiederherstellung nicht mehr.
- SIGTERM und SIGINT werden in einen geordneten Qt-Abschluss überführt. Der Crashmarker wird vor möglicherweise längerem USB-Aufräumen gelöscht, damit ein normaler Desktop-Neustart nicht als LCD-Absturz behandelt wird.
- CPU-Kurvenregelung, GIF-USB-Koordination, OpenLinkHub-Steuerung und alle Sicherheitsfallbacks bleiben erhalten.

---

# Open Hardware Control 3.0.5 – CPU-Temperaturkurven

- Sichtbare Pumpen- und Radiatorlüfterkurve von Kraken-Wassertemperatur auf CPU-Temperatur umgestellt.
- Eigenständiger 1-Sekunden-Regeltimer liest AMD-CPU-Sensoren direkt über Linux-hwmon und bleibt während des LCD-GIF-Streams aktiv.
- Lineare Kurveninterpolation, EMA-Glättung, 2-%-Quantisierung und asymmetrische Hysterese verhindern hörbares Pendeln und unnötige USB-Übergaben.
- Steigende Kühlanforderungen reagieren schneller als fallende; der 100-%-Endpunkt wird ohne Absenkverzögerung übernommen.
- Pumpe und Lüfter werden bei gleichzeitiger Änderung in einem gemeinsamen koordinierten GIF-USB-Fenster gesetzt.
- Alle AMD-AM5-Profile besitzen CPU-Temperaturpunkte mit 100 % bei 90 °C beziehungsweise 85 °C für Ryzen 7000 X3D.
- Alte gespeicherte 20–50-°C-Wasserkurven und Profilkurven werden beim Upgrade nicht als CPU-Werte missverstanden, sondern sicher migriert.
- Bei fünf aufeinanderfolgenden CPU-Sensorfehlern setzt die Regelung aktive Kurvenkanäle auf 75 %.
- Die Wassertemperatur bleibt als unabhängige 42/50-°C-Sicherheitsüberwachung erhalten.
- Beim echten Programmende werden aktive CPU-Kanäle auf konservative autonome Wasser-Hardwarekurven zurückgestellt; Tray-Betrieb lässt die CPU-Regelung weiterlaufen.
- OpenLinkHub-Steuerung, Manuell-/Kurven-Schaltflächen, LCD-Streamer, ACK-Prüfung und Framecache bleiben erhalten.

---

# Open Hardware Control 3.0.4 – direkte OpenLinkHub-Gerätesteuerung

- Fest freigegebene, dokumentierte OpenLinkHub-Schreibaktionen für Kühlung, RGB/LCD, Maus, Tastatur und Headset ergänzt.
- Temperatur- und RGB-Profile werden aus der lokalen API gelesen und in den passenden Geräteauswahlen angeboten.
- Direkte Schreibzugriffe müssen für jede Programmsitzung ausdrücklich bestätigt werden und bleiben bei zwei aktiven Diensten gesperrt.
- Wertebereiche, Geräte-, Kanal- und Profilangaben werden vor jedem Befehl validiert; beliebige API-Pfade oder JSON-Nutzlasten sind ausgeschlossen.
- Vollständige Seriennummern verlassen das Hilfsmodul nicht. Die Oberfläche erhält nur gekürzte Suffixe und nicht rückrechenbare Steuerkennungen.
- Erfolg wird aus Prozess- und API-Antwort bestätigt; danach werden Gerätewerte automatisch neu eingelesen.
- Komplexe Makrofolgen, vollständiger RGB-Editor und neue LCD-Mediendateien verbleiben zunächst im OpenLinkHub-Web-Dashboard.
- NZXT-Kraken-Steuerung und GIF-USB-Handoff bleiben unverändert.

---

# Open Hardware Control 3.0.3 – stabile Farbmarkierung der Kühlungsbetriebsart

- Qt-Checkzustand der vier Modusschaltflächen entfernt, damit die Oberfläche nicht schon beim Klick vor dem Geräteergebnis umspringt.
- Eigene dynamische Eigenschaft `coolingState` bildet ausschließlich den zuletzt bestätigten Kraken-Modus ab.
- Aktiver Modus besitzt feste grüne Normal-, Hover- und Gedrückt-Farben; Theme und Akzentfarbe können die Markierung nicht mehr ausblenden.
- Ein fehlgeschlagener oder noch laufender Schreibbefehl lässt die bisherige Aktivmarkierung unverändert.
- Keine Änderung an liquidctl-Befehlen, Kurvenregeln, Profilen oder der koordinierten GIF-USB-Übergabe.
- Optionales `OHC_INSTALL_HOME` ermöglicht einen isolierten Installertest; die normale Installation nach `~/.local` bleibt unverändert.
- Reale 3.0.2-Hardwarebestätigung dokumentiert: Lüfterkurve mit fünf Punkten bei laufendem GIF übertragen, Animation nach 258 ms fortgesetzt; Schnellprofile nach 317–351 ms fortgesetzt, ohne LCD-Frame-Sprünge.

---

# Open Hardware Control 3.0.2 – eindeutige Kühlungsbetriebsarten

- Neue kanalgetrennte Schaltflächen für **Manuell aktivieren** und **Pumpen-/Lüfterkurve aktivieren**.
- Ein Modusschalter wird erst nach einem erfolgreich abgeschlossenen Kraken-Schreibbefehl als aktiv markiert.
- Der manuelle Modus überträgt den jeweiligen Schieberegler als feste Drehzahl; der Kurvenmodus validiert und überträgt die angezeigte Hardwarekurve.
- Bestehende Anwenden-Knöpfe, Schnellprofile, Sicherheitsprofil, gespeicherte Profile und CPU-Assistenz aktualisieren dieselbe Modusanzeige.
- Umschaltungen bei laufender GIF-/Hardwareanimation verwenden unverändert die bestätigte PAUSE-/RESUME-USB-Übergabe aus 3.0.1.
- Reale Kraken-3.0.1-Bestätigung dokumentiert: Lüfter 100 % mit 240-ms-Pause und Pumpe 100 % mit 251-ms-Pause; Stream danach ohne LCD-Frame-Sprünge fortgesetzt.

---

# Open Hardware Control 3.0.1 – Kühlung-während-GIF-Version

- Manuelle Pumpen-, Lüfter- und Kurvenänderungen sind jetzt bei laufender GIF- oder generierter Hardwareanimation möglich.
- Schnellprofile, Sicherheitsprofil und gespeicherte Kühlprofile verwenden denselben koordinierten Übergabepfad.
- Neuer PAUSE-/RESUME-Kanal zwischen GUI und dem langlebigen CAM-Raw-Streamer.
- Der Streamer beendet zuerst den aktuellen Frame, schließt HID/Bulk, behält den vorbereiteten RGB565-Cache im Speicher und bestätigt erst dann die USB-Freigabe.
- Nach vollständig abgeschlossenem liquidctl-Direct-Access-Befehl verbindet sich derselbe Streamer neu, primt die vorgemerkte Cachephase zweimal und setzt die Animation fort.
- Niemals zwei gleichzeitige Kraken-Schreiber; normale Statusabfragen bleiben während des Streams pausiert.
- Zeitlimits für Freigabe und Wiederaufnahme sowie bestehender Watchdog, ACK-Abgleich und LCD-Sicherheitsfallback bleiben aktiv.
- Neuer isolierter Regressionstest für Freigabe, Neuverbindung, Cacheerhalt und Befehlsreihenfolge.

---

# Open Hardware Control 3.0.0 – interne Multi-Hardware-Version

- Kraken Control 2.9.23 vollständig als eingebautes NZXT-Modul übernommen.
- Hierarchische linke Navigation mit hardwareabhängiger Sichtbarkeit ergänzt.
- Option „Nicht erkannte Geräte/Module anzeigen“ ergänzt.
- Erste sichere Corsair-/OpenLinkHub-Integration: Installation, Benutzer-/Systemdienst, lokale API, Geräteliste und Telemetrie.
- OpenLinkHub-Dienstaktionen auf `systemctl --user` und eine feste Aktionsliste begrenzt.
- Warnung bei Systemkontext oder zwei aktiven Diensten; systemweite Migration bleibt ausdrücklich manuell.
- Bestehende Kraken-Control-Einstellungen werden beim ersten Start in den neuen Anwendungsschlüssel übernommen.
- Neue zentrale Projektdokumentation und separates OpenLinkHub-Integrationsdokument.
- Open Radeon Control Center bleibt ein eigenständiges Projekt.

---

# Kraken Control 2.9.23 – interne Live-Hardwareanimations-Version

> **INTERNER TESTSTAND – nicht als öffentlicher GitHub-Release vorgesehen.**

- Animierte CPU- und GPU-Anzeigen aktualisieren ihre sichtbaren Temperaturwerte alle zwei Sekunden rein lesend über Linux-`hwmon`.
- Die Wassertemperatur bleibt während des exklusiven Streams der letzte sichere Kraken-Wert; parallele Kraken-Statusabfragen bleiben aus Sicherheits- und Stabilitätsgründen deaktiviert.
- Ein isolierter Spawn-Renderprozess erzeugt bei sichtbaren Temperaturänderungen einen vollständigen neuen 20/25-FPS-Phasensatz. Erst nach erfolgreicher Fertigstellung wird der Cache atomar übernommen.
- Der USB-Prozess zeichnet keine Frames selbst und behält die bestätigte phasenstabile CAM-nahe Reihenfolge ohne Überlappung oder Catch-up-Bursts.
- Lokalisierte `LIVE`-/`LETZTER WERT`-Markierungen in allen vier Render-Sprachen.
- Neue UI-Statusereignisse für erfolgreiche und fehlgeschlagene Livewert-Aktualisierungen; bei einem Renderfehler bleibt der letzte vollständige Cache aktiv.
- CPU-/GPU-Sensorlogik in das gemeinsame read-only Modul `kraken_sensors.py` ausgelagert.
- Neue Tests für Sensorpriorität, dynamische Phasensätze, atomare Cacheübergabe und einen real separat gestarteten Spawn-Renderprozess.
- Keine Firmwareaktualisierung.

---

# Kraken Control 2.9.22 – interne animierte Hardwaredesign-Version

> **INTERNER TESTSTAND – nicht als öffentlicher GitHub-Release vorgesehen.**

- Fünf nahtlose Hardwaredaten-GIFs mit echten, prozedural gezeichneten Ring-, Halo-, Orbit-, Dual- und Trio-Bewegungen.
- Neuer eigener UI-Abschnitt für animierte Hardwaredaten mit Motivwahl, 20/25 FPS, animierter Vorschau, Start und Stop.
- Schrift- und Zahlen-Größe für statische und animierte Designs von 70 bis 150 Prozent einstellbar; Standard auf 125 Prozent angehoben.
- Animationsgenerator verwendet dieselben vier Sprachen, Farbvorlagen und freien `#RRGGBB`-Werte wie die statischen Designs.
- Generierte Animation wird ohne Änderung der ausgewählten eigenen GIF-Datei an den vorhandenen CAM-Raw-Streamer übergeben.
- Animationen verwenden bewusst den letzten Sensorstand als Start-Momentaufnahme, da der exklusive GIF-Stream Kraken-Statusabfragen pausiert.
- Eigene dauerhafte Experimentalwarnung und Einbindung in Crash-Erkennung, Watchdog und LCD-Sicherheitsfallback.
- Einstellungen und Profile speichern Schriftgröße, Animationsmotiv und Animationsrate.
- Keine Firmwareaktualisierung.

---

# Kraken Control 2.9.21 – interne Hardwaredesign-/Sprachversion

> **INTERNER TESTSTAND – nicht als öffentlicher GitHub-Release vorgesehen.**

- Fünf runde Live-Hardwaredesigns für Wasser, CPU, GPU, CPU+GPU und Wasser+CPU+GPU.
- Neues eigenständiges, mit Pillow getestetes 240×240-Renderermodul `kraken_lcd_designs.py`.
- Eisblau als Standard; sieben Vorlagen plus eigener `#RRGGBB`-Wert mit Validierung und Farbdialog.
- AMD-GPU-Temperatur über `amdgpu`/hwmon ergänzt; dedizierte GPU wird über den größten VRAM-Wert bevorzugt.
- GPU-Temperatur als sechste Dashboardkarte ergänzt.
- Live-Modus mit 5–60 Sekunden Intervall, Vorschau, Start/Stop, exklusiver Koordination mit Bild, Uhr, GIF und Fallback.
- Experimentalbestätigung, Crash-Marker, dreistufige Fehlergrenze und Flüssigkeitstemperatur-Sicherheitsfallback auf den neuen Modus erweitert.
- Sprachumschaltung nach der Einstellungswiederherstellung angeordnet und um Menütitel, dynamische Farbtasten sowie datenbasierte RGB-/Profil-Auswahlen ergänzt.
- Sichtbare Grundoberfläche für Deutsch, Englisch, Spanisch und Französisch vervollständigt.
- Keine Firmwareaktualisierung.

---

# Kraken Control 2.9.20 – interne UI-/Loop-Diagnose-Version

> **INTERNER TESTSTAND – nicht als öffentlicher GitHub-Release vorgesehen.**

- Normale GIF-Bildraten auf `CAM-nah · automatisch · empfohlen · max. 25 FPS`, 24 FPS und 25 FPS reduziert.
- 5/8/10/12/15/20 FPS sowie der 25,6-Hz-Rückfallmodus bleiben unter `Erweiterte GIF-Optionen anzeigen` verfügbar.
- 26 und 27 FPS aus der grafischen Auswahl entfernt; alte 30/32-Hz-Experimente bleiben entfernt.
- Neuer nicht blockierender Hinweis, wenn der letzte→erste Bildwechsel im Vergleich zu normalen Nachbarübergängen wahrscheinlich sichtbar ist.
- Moving-Bars-Test-GIFs neu erzeugt. Im 25-FPS-Test sind alle 50 Übergänge einschließlich Loop exakt vier Pixel breit.
- Phasenstabile 2.9.19-Folge durch zusätzliche Regressionstests und Zehn-Minuten-Simulation abgesichert.
- Realen 2.9.19-Hardwaretest dokumentiert: etwa 26,3 Hz, 37,8–37,9 ms Upload, keine LCD-Frame-Wiederholungen/-Sprünge und keine übersprungenen Transportframes.
- Keine Firmwareaktualisierung.

---

# Kraken Control 2.9.19 – interne phasenstabile CAM-Taktversion

> **INTERNER TESTSTAND – nicht als öffentlicher GitHub-Release vorgesehen.**

- Vorbereitete LCD-Phasen werden streng `1, 2, 3 …` übertragen. Ein knappes USB-Zeitfenster kann keine spätere Bildphase mehr auswählen.
- CAM-naher Zieltakt 26,667 Hz; wenn die reale USB-Transaktion länger als 37,5 ms dauert, folgt der nächste vollständige Frame erst nach dem passenden ACK.
- Einzelne Überläufe werden nur aus echtem freien Zeitbudget und höchstens in 0,25-ms-Schritten abgebaut; keine Catch-up-Bursts.
- Moving-Bars-25-FPS-Loop korrigiert: alter regelmäßiger Sprung am 2-Sekunden-Übergang entfernt.
- Keine Firmwareaktualisierung.

---

# Kraken Control 2.9.17 – interne ACK-Sync-/Tearing-Testversion

> **INTERNER HARDWARE-TESTSTAND – nicht automatisch als öffentlicher GitHub-Release vorgesehen.**

- Das neue Hardwarevideo von 2.9.16 wurde frameweise ausgewertet. Die Animation füllt das LCD nun vollständig und läuft deutlich flüssiger; sichtbar bleiben eine horizontale Versatzkante durch gemischte Bildphasen sowie leichtes Haken.
- Der CAM-Mitschnitt wurde gezielt auf die Pause zwischen passendem `37 02`-End-ACK und folgendem `36 01`-Start untersucht: Median 0,113 ms, Minimum 0,070 ms. CAM wartet dort nicht zusätzlich auf eine starre 26,67-Hz-Zeitmarke.
- Der Standardtransport `cam` ist deshalb jetzt **ACK-synchronisiert**. Nach einem vollständig bestätigten Frame startet der nächste nach 0,10 ms. Die Kraken-Antwort bestimmt den realen Takt und unnötig wechselnde Zusatzwartezeiten entfallen.
- Die sichtbare GIF-Zeit bleibt an `time.monotonic()` gekoppelt. Auch der neue Pfad überlappt keine Transfers, holt keine Frames in Bursts nach und akzeptiert weiterhin ausschließlich die passenden Antworten `37 01` und `37 02`.
- Der feste **25,6-Hz-Rückfallmodus** bleibt unverändert erhalten und verwendet weiterhin 0,2 ms Schutzabstand.
- Oberfläche und Log kennzeichnen den neuen Standard als `CAM-synchronisiert · ACK-getaktet` beziehungsweise `cam-raw-ack-paced`. Effektive Rate, P90, Maximum, Wiederholungen, Sprünge und fremde HID-Berichte bleiben sichtbar.
- Exklusiver Kraken-Zugriff, pausierte Status-/Kühlbefehle, autonome Hardwarekurven, automatische Wiederfreigabe und 12-Sekunden-Watchdog bleiben unverändert.
- 2.9.17 führt **keine Firmwareaktualisierung** aus.

---

# Kraken Control 2.9.16 – interne Exclusive-ACK-/Watchdog-Version

> **INTERNER HARDWARE-TESTSTAND – nicht automatisch als öffentlicher GitHub-Release vorgesehen.**

- Die fünf erneut bereitgestellten USBPcap-Aufzeichnungen wurden direkt ausgewertet. Die in 2.9.17 korrigierte datensatzgenaue Zählung weist im langen CAM-GIF-Mitschnitt 341 vollständige 240×240-RGB565-Nutzdatenübertragungen aus; der kontinuierliche Hauptabschnitt erreicht 26,375 Hz. 25,6 Hz bleibt als konservativer Rückfall erhalten.
- Die CAM-Framefolge wurde byte- und zeitgenau bestätigt: `36 01` → `37 01` → 20-Byte-Bulk-Header → 115.200 Byte RGB565 → `36 02` → `37 02`. Eine vollständige CAM-Transaktion dauert im Mittel rund 37,34 ms; der vorhandene 0,2-ms-Schutzabstand bleibt erhalten.
- Neue eindeutige ACK-Zuordnung im `kraken_cam_streamer.py`: Vor jedem Start-/Endbefehl werden alte HID-Berichte verworfen. Der Streamer akzeptiert ausschließlich die passende Antwort `37 01` beziehungsweise `37 02`; ungefragte `75 02`-Statusberichte werden nicht mehr versehentlich als ACK verwendet.
- Hintergrund: liquidctl 1.16.0 gibt in seinem privaten `_write_then_read()` bislang das nächste eingehende HID-Paket zurück, ohne es der gesendeten Anfrage zuzuordnen. Der noch offene liquidctl-Upstream-PR #916 vom 22. Juli 2026 bestätigt genau dieses Problem. Kraken Control verwendet für den internen Streamer deshalb eine lokal begrenzte, strenge Lösung, ohne liquidctl systemweit zu verändern.
- Der GIF-Streamer übernimmt die Kraken jetzt exklusiv. Vor dem Start wird der normale Status-Timer gestoppt und ein bereits laufender oder wartender liquidctl-Befehl höchstens 15 Sekunden sauber abgewartet. Erst danach öffnet der Streamer seine dauerhafte Geräteverbindung.
- Während der Animation werden keine neuen Kraken-Statusabfragen und keine neuen Pumpen-/Radiatorlüfterbefehle gestartet. Die bereits in der Kraken-Firmware gespeicherten Hardwarekurven laufen unabhängig von der App weiter.
- Nach sauberem Stop werden Statusabfragen und Kühlbefehle automatisch wieder freigegeben; nach 0,5 Sekunden wird der Status neu eingelesen.
- Neuer äußerer 12-Sekunden-Watchdog: Bleiben nach Beginn des Hardwarezugriffs Lebenszeichen aus, wird der Helfer beendet und der vorhandene LCD-Sicherheitsfallback stellt die Flüssigkeitstemperaturanzeige wieder her.
- Diagnose erweitert um `ack_matching` und die Anzahl während der ACK-Suche übersprungener fremder HID-Berichte.
- Neue zentrale Projektdokumentation `docs/project/Kraken_Control_Projekt.md` und technische Mitschnittauswertung `docs/hardware/USB_CAPTURE_FINDINGS.md` werden mitinstalliert und liegen im Entwicklerpaket vollständig bei.
- 2.9.16 führt **keine Firmwareaktualisierung** aus. Es bleibt eine experimentelle Beta für Kraken 2023 Standard / Non-Elite mit Firmware 2.0.0 und muss am realen Gerät getestet werden.

---

# Kraken Control 2.9.15 – interne CAM-Raw-LCD-Streamer-/Motion-Version

> **INTERNER TESTSTAND – nicht als öffentlicher GitHub-Release vorgesehen.**

- Der experimentelle GIF-/LCD-Transport wurde gezielt neu aufgebaut. Die in 2.9.14 getesteten **30-Hz- und 32-Hz-Transportmodi wurden entfernt**, weil der Hardware-/Videotest trotz guter USB-Messwerte sichtbares Haken und partielle Bildversätze zeigte.
- Neuer Standardpfad **CAM-nah · 26,67 Hz**. Als sicherer Vergleichs-/Rückfallmodus bleibt **25,6 Hz** erhalten. Es gibt keine Auto-Regelung, kein 25→27→25-Hz-Pendeln und keine Catch-up-Bursts.
- Neuer `kraken_cam_streamer.py`: Der Helfer besitzt die Firmware-2.x-Frame-Transaktion jetzt explizit selbst: `36 01 …` → Geräteantwort → 20-Byte-Bulk-Header → exakt **115.200 Byte RGB565** → `36 02` → Geräteantwort. Die vollständige Kraken-Verbindung bleibt während der Animation offen.
- Der alte `kraken_gif_streamer.py` wurde aus dem internen Paket und Installer entfernt, damit nicht versehentlich der verworfene 30/32-Hz-Pfad gestartet wird.
- Die bisherige reine Crossfade-Zwischenbildmethode wurde ersetzt. Die neue **Motion-Interpolation** schätzt eine konservative globale Bildverschiebung zwischen benachbarten Frames und verschiebt beide Bilder vor dem Überblenden. Bei nicht eindeutig erkennbarer Bewegung fällt sie automatisch auf einen normalen Blend zurück.
- Für Scroll-/Balkenbewegungen entstehen dadurch echte Zwischenpositionen, statt zwei versetzte Balken nur transparent übereinanderzulegen.
- GIF-Inhaltszeit bleibt weiterhin an `time.monotonic()` gekoppelt. Langsame USB-Transfers dürfen einen vollständigen Frame etwas länger halten; Transfers werden niemals überlappt.
- Das Firmware-2.x-Framebuffer-Priming bleibt bei zwei identischen ersten Frames. Danach beginnt erst die eigentliche Wiedergabezeitachse.
- Diagnose erweitert um Kennzeichnung des **CAM-Raw-Pfads**, Anzahl erkannter Bewegungs-Paare, Motion-Interpolationsmodus sowie eindeutige vorbereitete LCD-Frames. P90, EMA, Maximum, Überlauf, Jitter und Frame-Sprungzähler bleiben erhalten.
- Die Oberfläche wurde vereinfacht: LCD-Transport bietet nur noch `CAM-nah · 26,67 Hz · Standard` und `25,6 Hz · Sicher · bewährt`. Die alte 30/32-Hz-Auswahl wurde entfernt.
- Die technischen Test-GIFs 30/32 FPS wurden aus dem Paket entfernt; mitgeliefert bleiben 24/25/26/27-FPS-Tests sowie Diagonal- und Checker-Scroll-Tests.
- Persistente Experimentalbestätigungen, LCD-Crash-Fallback auf Flüssigkeitstemperatur, Uhr-Schutz, minimierter Tray-Autostart, Mehrsprachen-Oberfläche, Direct Access und alle bisherigen Kühl-/Sicherheitsfunktionen bleiben enthalten.

---

# Kraken Control 2.9.14 – interne Smooth-LCD-Transport-/Zwischenbild-Version

> **INTERNER TESTSTAND – nicht als öffentlicher GitHub-Release vorgesehen.**

- Der in 2.9.13 bewährte **25,6-Hz-LCD-Transport** bleibt unverändert als tearing-armer Sicherheits-/Referenzmodus erhalten.
- Zwei neue feste physische LCD-Transportmodi: **30 Hz · Smooth** und **32 Hz · Experimental**. Es gibt weiterhin keine Auto-Regelung und kein 25→27→25-Hz-Pendeln.
- **GIF-Inhaltsrate und LCD-Transportrate sind jetzt vollständig getrennte Einstellungen.** Ein 25-FPS-GIF behält seine ursprüngliche Laufzeit, kann aber mit 25,6, 30 oder 32 LCD-Updates pro Sekunde ausgegeben werden.
- Bei aktivierter **Zwischenbild-Interpolation** wird für zusätzliche LCD-Transportzeitpunkte ein echtes Mischbild zwischen den benachbarten logischen Inhaltsframes vorbereitet. 25-FPS-Inhalt bei 30 Hz erzeugt dadurch 30 zeitlich verteilte LCD-Phasenbilder pro Sekunde statt nur zusätzliche Duplikate.
- Die Vorbereitung verwendet eine phasenbasierte LCD-Bildtabelle pro GIF-Schleife. Der physische Scheduler bleibt auf dem gewählten 25,6/30/32-Hz-Takt, während die sichtbare GIF-Position weiterhin aus `time.monotonic()` abgeleitet wird.
- Die tearing-arme Übertragungsstrategie aus 2.9.13 bleibt erhalten: vollständige synchrone liquidctl-/ACK-Transfers, **0,2-ms-Schutzabstand**, keine überlappenden Bildtransfers und keine Catch-up-Bursts. Ein langsamer Transfer hält lieber ein vollständiges Bild etwas länger.
- Neue Diagnosewerte unterscheiden **LCD-Frame-Wiederholungen/-Sprünge** von rein logischen Inhaltsphasen. Dadurch lässt sich erkennen, ob der physische 30/32-Hz-Ausgabepfad wirklich neue Bilder liefert.
- Oberfläche erweitert um **LCD-Transport** mit den Modi `25,6 Hz · Sicher · bewährt`, `30 Hz · Smooth · mehr Zwischenbilder` und `32 Hz · Experimental · höchste Glättung`.
- 32 FPS ist zusätzlich als Inhalts-Teststufe verfügbar. Die mitgelieferten Test-GIFs wurden um **32-FPS-Farbzyklus** und **32-FPS-Bewegungsbalken** erweitert.
- Persistente Experimentalhinweise, LCD-Crash-Fallback auf Flüssigkeitstemperatur, Uhr-Schutz, Direct Access, Mehrsprachen-Oberfläche und minimierter Tray-Autostart bleiben enthalten.

---

# Kraken Control 2.9.13 – interne 25,6-Hz-Phasenentkopplungs-Version

> **INTERNER TESTSTAND – nicht als öffentlicher GitHub-Release vorgesehen.**

- Langzeittest von 2.9.12 ausgewertet: Bei exakt **25,000 Hz** waren USB-Timing, P90, Überlauf und Transportstatistik praktisch perfekt, das physische LCD wirkte trotzdem überwiegend stehend. Das spricht gegen einen reinen Python-/Schedulerfehler und für eine ungünstige wiederkehrende Display-/Framebuffer-Phase.
- Für **25/26/27-FPS-Inhalte sowie Adaptiv** ist der physische LCD-Transport deshalb jetzt fest auf **25,6 Hz** gesetzt. 24-FPS-Inhalt bleibt bei 24 Hz.
- Keine Auto-Regelung und kein 25→27→25-Hz-Sägezahn: 25,6 Hz bleibt während des gesamten Laufs konstant.
- Die GIF-Inhaltszeit bleibt weiterhin an `time.monotonic()` gekoppelt. Ein 25-FPS-GIF behält dadurch seine reale Laufzeit; der leicht schnellere LCD-Transport wiederholt bei Bedarf kontrolliert vollständige Inhaltsframes, statt die Animation zu beschleunigen.
- Der 25,6-Hz-Versatz ist bewusst gewählt, damit die Startphase der USB-Bildübertragung relativ zur internen LCD-/Framebuffer-Phase fortlaufend wandert, statt bei exakt 25 Hz immer denselben ungünstigen Punkt zu treffen.
- Der synchrone liquidctl-/ACK-Pfad, der **0,2-ms-Schutzabstand**, das Verbot von Catch-up-Bursts, Jitter-/P90-/Überlaufmessung und der Sicherheitsfallback auf Flüssigkeitstemperatur bleiben erhalten.
- Logmodus für 25/26/27 FPS lautet jetzt `stabil-detuned-25.6hz-wallclock`; die Oberfläche kennzeichnet 25 FPS als **„25,6 Hz LCD entkoppelt · empfohlen“**.
- Alle bisherigen 2.9.x-Funktionen bleiben enthalten: persistente Experimentalhinweise, LCD-Crash-Erkennung, Uhr-Fallback, Mehrsprachen-Oberfläche, Direct Access für Kühlbefehle und minimierter Tray-Autostart.

---

# Kraken Control 2.9.12 – interne Stable-Lock-GIF-Version

> **Interner Entwicklungs- und Teststand. Nicht als öffentlicher GitHub-Release vorgesehen.**

- Langzeitlogs aus 2.9.11 ausgewertet: Die bisherige Auto-Stabilisierung pendelte wiederholt von etwa 25 Hz Richtung 27 Hz, traf dann den beobachteten 39–40-ms-Transfercluster und fiel erneut auf etwa 25 Hz zurück. Dieses Sägezahnverhalten konnte als leichtes periodisches Haken sichtbar werden.
- Die selbsttätige Hoch-/Runterregelung wurde für die stabilen GIF-Modi entfernt. **25-FPS-Inhalt läuft jetzt fest mit 25 Hz LCD-Transport**, 24 FPS fest mit 24 Hz.
- 26- und 27-FPS-Inhalte bleiben bewusst Testmodi, verwenden aber ebenfalls einen **stabilen 25-Hz-LCD-Transport**. Da die Inhaltsrate höher als der physische Transport ist, können dort weiterhin zeitbasierte Inhalts-Sprünge auftreten; die GIF-Gesamtgeschwindigkeit bleibt korrekt.
- Adaptiv-Modus bereitet Inhalt jetzt höchstens mit 25 FPS auf und orientiert sich an der durchschnittlichen Quellbildrate, statt standardmäßig 27 FPS Inhalt zu erzeugen.
- Kein Catch-up, kein Burst und kein Feedback-Retuning während des Streams. Vollständige liquidctl-/ACK-Transfers werden seriell abgeschlossen; die nächste Übertragung startet ausgehend vom letzten tatsächlichen Startzeitpunkt.
- Post-ACK-/Framebuffer-Schutzabstand von 0,8 ms auf **0,2 ms** reduziert. Der vollständige synchrone liquidctl-Transfer bleibt abgeschlossen, aber 39–40-ms-Transfers werden bei 25 Hz nicht unnötig zusätzlich verlängert.
- Neue Diagnosewerte **Überlauf gesamt** und **max. Überlauf** zeigen, wie weit einzelne abgeschlossene Transfers das feste Zeitfenster tatsächlich überschritten haben. P90, EMA, Maximum und Jitter-Histogramm bleiben erhalten.
- Das Log kennzeichnet den neuen Modus als `stabil-lock-wallclock`; bei 25 FPS bleibt das LCD-Ziel während des gesamten Laufs konstant bei 25 Hz.
- Wallclock-Inhaltszeit, RGB565-Vorbereitung, doppelte Framebuffer-Initialisierung, Experimentalhinweise, LCD-Crash-Fallback, Uhr-Schutz, Direct Access, Mehrsprachen-Oberfläche und minimierter Tray-Autostart bleiben erhalten.

# Kraken Control 2.9.11 – interne Wallclock-/Auto-Stabil-GIF-Version

> **Interner Entwicklungs- und Teststand. Nicht als öffentlicher GitHub-Release vorgesehen.**

- GIF-Inhaltszeit folgt jetzt direkt `time.monotonic()` und damit der real verstrichenen Wiedergabezeit. Die Abspielgeschwindigkeit hängt nicht mehr davon ab, wie viele USB-Transfers die Kraken physisch pro Sekunde schafft.
- Der in 2.9.10 beobachtete Effekt, dass 25-FPS-Inhalt bei real etwa 25,2-Hz-LCD-Transport langsam auseinanderlaufen konnte, ist damit beseitigt.
- Neue selbsttätige LCD-Transportregelung für 24/25/26/27-FPS-Inhalte und Adaptiv-Modus. Der Transport startet konservativ und lernt aus den letzten USB-Übertragungszeiten; Obergrenze bleibt 27 Hz.
- Die Regelung verwendet das 90. Perzentil der jüngsten Uploadzeiten statt einzelne 38–41-ms-Transfers als dauernden Fehler/Re-Sync zu behandeln. Sinkt die sichere Rate, wird sofort reduziert; Erhöhungen erfolgen bewusst nur langsam.
- Der Framebuffer-Schutzabstand wurde nach dem langen 2.9.10-Hardwaretest von 2,0 ms auf 0,8 ms reduziert. Dadurch werden häufige ~39-ms-Transfers bei 25 FPS nicht künstlich auf >41 ms verlängert.
- Scheduler vollständig auf Start-zu-Start-Taktung umgestellt. Es gibt keine alte globale Deadline, keine Catch-up-Bursts und keine wiederholten Phase-Resets mehr. Wenn ein Transfer das Zeitfenster füllt, beginnt der nächste erst nach Abschluss plus kleinem Schutzabstand.
- 25-FPS-Inhalt startet mit 25-Hz-LCD-Ziel; 26/27-FPS- und Adaptiv-Inhalt starten konservativ bei 25 Hz und können bei genügend USB-Spielraum schrittweise bis 27 Hz ansteigen. 30 FPS bleibt ein expliziter Belastungstest.
- Neue Diagnosewerte im GIF-Log: aktuelles LCD-Ziel, Upload-EMA, P90-Uploadzeit, Maximum, gefüllte Zeitfenster, Inhaltswiederholungen, Inhalts-Sprünge sowie Jitter-Histogramm `<20`, `20–30`, `30–35`, `35–42` und `≥42 ms`.
- `Transportframes übersprungen` bleibt 0. Falls der physische LCD-Takt kurz unter der Inhaltsrate liegt, wird der korrekte GIF-Zeitpunkt aus der Echtzeit gewählt; dadurch kann transparent ein Inhaltsframe übersprungen werden, ohne die komplette Animation zu verlangsamen.
- Framebuffer-Priming bleibt vor dem Start der Wiedergabezeitachse. Der experimentelle Sicherheitsfallback auf Flüssigkeitstemperatur, Uhr-Schutz, Start-LCD-Arbitrierung, Direct Access, Sprachen und minimierter Tray-Autostart bleiben erhalten.

# Kraken Control 2.9.10 – interne GIF-Transport- und Tearing-Schutz-Version

> **Interner Entwicklungs- und Teststand. Nicht als öffentlicher GitHub-Release vorgesehen.**

- GIF-Inhaltsrate und physischer LCD-Transport sind jetzt voneinander getrennt.
- 24-, 25-, 26- und 27-FPS-Inhalte werden CAM-nah mit 27 Hz an die Kraken übertragen; die ursprüngliche GIF-Laufzeit bleibt dabei erhalten.
- 30 FPS bleibt als separater Belastungstest mit 30-Hz-LCD-Transport verfügbar.
- Der 25-FPS-Testpfad verwendet damit nicht mehr zwingend einen problematischen 25-Hz-Displaytakt; 25-FPS-Inhalte werden vollständig und zeitlich korrekt über 27-Hz-Transport abgebildet.
- Der Wiedergabezeitgeber startet erst **nach** den beiden einmaligen Firmware-2.x-Framebuffer-Priming-Transfers. Dadurch entfällt der bisher direkt nach jedem Start auftretende künstliche erste Frame-Verlust.
- Aggressives Catch-up und hartes Überspringen verspäteter Frames wurden entfernt. Ein langsamer USB-Transfer wird vollständig beendet und die nächste Übertragung anschließend sanft neu getaktet.
- Bei Transfers, die in das nächste Zeitfenster hineinreichen, wird ein kurzer 2-ms-Schutzabstand verwendet. Ziel ist weniger Mikroruckeln und weniger tearing-artige Bildversätze bei den beobachteten 38–40-ms-Ausreißern.
- Der Inhaltszeitgeber springt bei einem langsamen Transfer nicht mehrere Bilder vor. Stattdessen wird ein vollständiges Bild minimal länger gehalten; die Animation kann sich bei einem Ausreißer um wenige Millisekunden strecken, bleibt aber visuell kontinuierlicher.
- Neue GIF-Messwerte im Log: Inhalts-FPS, physischer LCD-Transport in Hz, letzter/EMA/maximaler Upload, langsame Transfers, sanfte Re-Syncs und erwartete Inhaltswiederholungen.
- `übersprungen` bleibt im neuen sanften Scheduler bei 0; der Streamer versucht keine Burst-Aufholjagd mehr.
- Neue 26-FPS-Teststufe zwischen 25 und 27 FPS.
- Die technischen Test-GIFs liegen jetzt für 24/25/26/27/30 FPS vor; Farbzyklus und bewegte Balken eignen sich besonders zum Vergleich von Mikroruckeln und tearing-artigen Versätzen.
- Startkonflikt zwischen globaler LCD-Wiederherstellung und einem automatischen Startprofil entschärft: Wenn ein Startprofil aktiv ist, bestimmt dieses den LCD-Zustand, statt parallel noch ein global gespeichertes Bild zu senden.
- Doppelte LCD-Uhr-Minutenupdates werden unterdrückt. Manuelle Änderungen an der Uhr können weiterhin einen erzwungenen Upload im selben Minutenfenster auslösen.
- Dauerhafte Experimentalbestätigungen, LCD-Crash-Fallback auf Flüssigkeitstemperatur, Sprachen Deutsch/Englisch/Spanisch/Französisch, Direct Access, Tray-Autostart und alle bisherigen Sicherheitsfunktionen bleiben erhalten.

# Kraken Control 2.9.9 – interne CAM-27-FPS- und GIF-Timing-Version

> **Interner Entwicklungsstand – nicht für die öffentliche Veröffentlichung vorgesehen.**

- GIF-Streamer auf einen **CAM-nahen Zielbereich bis 27 FPS** erweitert; zusätzliche feste Testmodi **24, 25, 27 und 30 FPS** ergänzen die bisherigen 5, 8, 10, 12, 15 und 20 FPS.
- Adaptiv-Modus zielt nun auf bis zu **27 FPS** statt 15 FPS und bleibt an einer monotonen Zeitachse verankert.
- Feste FPS verändern nicht mehr versehentlich die Abspielgeschwindigkeit des GIFs: Die ursprüngliche GIF-Schleifendauer bleibt erhalten und wird auf den gewählten LCD-Ausgabetakt neu abgetastet.
- Neue standardmäßig aktivierte Option **„Zwischenbilder glätten (Interpolation)“** erzeugt beim Vorbereiten echte Mischbilder zwischen Quellframes. Dadurch können GIFs mit niedriger Quellbildrate bei 24–30 FPS sichtbar flüssiger wirken.
- Frame-Pacing vollständig auf absolute `time.monotonic()`-Zeitpunkte umgestellt. Uploaddauer wird dadurch nicht mehr von Frame zu Frame aufaddiert; bei echtem Rückstand werden veraltete Frames übersprungen statt als Burst nachgesendet.
- Stop/Start-Race behoben: Der alte 3,5-Sekunden-Notfalltimer ist jetzt ein abbrechbarer `QTimer` und kann keinen bereits neu gestarteten GIF-Prozess mehr versehentlich beenden.
- Pillow-12.3-Warnung für `Image.Image.getdata()` beseitigt; auf aktuellen Pillow-Versionen wird `get_flattened_data()` verwendet, mit kompatiblem Fallback für ältere Versionen.
- GIF-Log erweitert: Quellframes, vorbereitete Ausgabeframes, Quelllaufzeit, Zieltakt, Interpolationsstatus, effektive FPS, Uploadzeit und übersprungene Frames werden protokolliert.
- Zehn selbst erzeugte **240×240-Test-GIFs** liegen unter `test-gifs/`: Farbzyklus und bewegte Balken jeweils mit exakt gemittelten 24/25/27/30 FPS sowie ein 27-FPS-Diagonal-Sweep und ein 27-FPS-Checker-Scroll.
- Die GIF-Testdateien verwenden ausschließlich im GIF-Format darstellbare 10-ms-Zeitstufen; ihre Frameverteilung ist so gewählt, dass die jeweilige Schleife im Mittel exakt 24, 25, 27 bzw. 30 Bilder pro Sekunde erreicht.
- Das Generator-Skript `tools/generate_test_gifs.py` liegt vollständig im Quellcode bei; der Installer kopiert die fertigen Test-GIFs zusätzlich nach `~/.local/share/kraken-control/test-gifs/`.
- Minimierter Tray-Autostart, dauerhafte Experimentalbestätigungen, LCD-Crash-Fallback, Direct-Access-Kühlung, Mehrsprachen-Oberfläche und alle Sicherheitsfunktionen aus 2.9.8 bleiben enthalten.

# Kraken Control 2.9.8 – interne Smooth-GIF- und Autostart-Version

> **Interner Entwicklungsstand – nicht für die öffentliche Veröffentlichung vorgesehen.**

- Experimenteller Firmware-2.x-GIF-Streamer vollständig überarbeitet: ein separater, langlebiger `QProcess` hält eine einzige liquidctl-Verbindung offen, statt für jedes GIF-Bild einen neuen CLI-Prozess zu starten.
- GIF-Frames werden vor dem Start auf 240×240 vorbereitet und einmalig in den von liquidctl für Firmware 2.x verwendeten RGB565-Datenstrom konvertiert.
- Erster Frame wird entsprechend dem liquidctl-Firmware-2.x-Verhalten einmalig doppelt übertragen; Folgeframes werden nur einmal gesendet.
- Neue Zeitsteuerung mit `time.monotonic()`: **Adaptiv** misst die reale Uploadzeit und streckt das Timing bei Bedarf gleichmäßig, damit möglichst keine Frames verloren gehen; feste FPS-Modi überspringen bei Rückstand veraltete Frames statt sie als Burst nachzusenden.
- GIF-Bildrate wählbar: adaptives Original-Timing bis maximal 15 FPS sowie feste 5, 8, 10, 12, 15 oder 20 FPS.
- GIF-Status und Log zeigen vorbereitete Frames, effektive Bildrate, letzte Uploadzeit, Taktungsmodus und übersprungene Frames; dadurch lässt sich die tatsächliche Streamleistung auf der Testhardware messen.
- LCD-Modi sind jetzt gegenseitig koordiniert: Uhr, statischer Fallback, Einzelbild, LCD-Ausrichtung und Flüssigkeitstemperatur stoppen einen laufenden GIF-Stream zuerst sauber, statt mit „Kraken verarbeitet gerade einen anderen Befehl“ zu kollidieren.
- Eigener dauerhaft speicherbarer Experimentalhinweis für den GIF-Streamer; „Experimentalhinweise zurücksetzen“ setzt Uhr-, Fallback- und GIF-Bestätigung gemeinsam zurück.
- Crash-Marker und LCD-Sicherheitsfallback gelten nun auch für GIF-Streaming. Ein unerwarteter Stream-Abbruch führt zurück zur Flüssigkeitstemperatur; GIF wird nach unsauberem Ende nicht automatisch fortgesetzt.
- Neue Option **„Beim Systemstart minimiert/im Tray starten“**. Nach abgeschlossenem Erstsetup startet Kraken Control bei Desktop-Autostart standardmäßig im Tray; ein manueller Start öffnet das Fenster weiterhin normal.
- Bestehende Autostart-Dateien werden auf den neuen `--autostart`-Startmarker migriert.
- Deutsch, Englisch, Spanisch und Französisch bleiben als erste interne Sprachstufe enthalten; neue GIF- und Autostart-Bedienelemente sind ebenfalls übersetzt.
- Direct-Access-Kühlungssteuerung, 10.000-Zeichen-Loglimit, LCD-Uhr-Sicherheit, Hintergründe und alle Fixes aus 2.9.7 bleiben erhalten.

# Kraken Control 2.9.7 – interne Sprach- und LCD-Sicherheitsversion

> **Interner Entwicklungsstand – nicht für die öffentliche Veröffentlichung vorgesehen.**

- LCD-Uhr-Hinweis wird nach einmaliger Zustimmung dauerhaft gespeichert und erscheint nach normalen Neustarts nicht erneut.
- Auch die Warnung für den experimentellen LCD-Wiederholungs-Fallback kann dauerhaft bestätigt werden.
- Neuer Punkt **„Experimentalhinweise zurücksetzen“** in den Einstellungen setzt beide Bestätigungen bewusst zurück.
- Neue Crash-Erkennung für experimentelle LCD-Modi: Während Uhr oder Wiederholungs-Fallback aktiv sind, wird ein persistenter Sitzungsmarker gesetzt.
- Bei normalem Programm-/Systemende wird der Marker sauber entfernt; bleibt er nach einem Absturz erhalten, startet die experimentelle LCD-Funktion beim nächsten Start nicht automatisch.
- Nach erkanntem unsauberen Ende wird automatisch die Standardanzeige **Flüssigkeitstemperatur** angefordert. Falls das Gerät gerade nicht verfügbar ist, bleibt die Wiederherstellung vorgemerkt und wird beim nächsten erfolgreichen Geräteaufbau erneut versucht.
- LCD-Rendererfehler lösen sofort den sicheren Flüssigkeitstemperatur-Fallback aus.
- Wiederholte LCD-/Uhr-Uploadfehler werden gezählt; nach drei aufeinanderfolgenden Fehlern wird die experimentelle LCD-Funktion beendet und auf Flüssigkeitstemperatur zurückgeschaltet.
- Verlust der Kraken-Verbindung während eines experimentellen LCD-Modus aktiviert ebenfalls die sichere Wiederherstellung.
- Erste Mehrsprachen-Unterstützung unter **Einstellungen → Sprache**. Verfügbar: **Deutsch, Englisch, Spanisch und Französisch**.
- Die gewählte Sprache wird dauerhaft gespeichert und die statische Hauptoberfläche kann ohne Neustart umgeschaltet werden.
- Diese erste interne Lokalisierungsstufe übersetzt zentrale Tabs, Menüs, Bedienelemente und Einstellungsbereiche. Technische Laufzeit-, Hardware- und Logmeldungen bleiben teilweise Deutsch, damit die Testprotokolle zwischen den Sprachen eindeutig vergleichbar bleiben.
- Direct-Access-Kühlungssteuerung, 10.000-Zeichen-Loglimit, Hintergrund-Hotfixes und alle Sicherheitsfunktionen aus 2.9.6 bleiben enthalten.

# Kraken Control 2.9.6 – LCD-Uhr-Hotfix

- Regression in „Uhr starten“ behoben: Der Startpfad verwendete noch das entfernte Widget `clock_24h`.
- Das Zeitformat wird jetzt korrekt aus `clock_format` gelesen (`24` bzw. `12`).
- „Uhr starten“ protokolliert wieder Startmodus und erfolgreiche/fehlgeschlagene LCD-Uploads.
- Statischer Regressionstest stellt sicher, dass `clock_24h` nicht erneut in den Quellcode gelangt.
- Alle Direct-Access-, Hintergrund-, Scroll-, Profil- und 10.000-Zeichen-Log-Fixes aus 2.9.5 bleiben enthalten.

# Kraken Control 2.9.5 – Direct-Access- und Hintergrund-Hotfix

- Alle Pumpen-/Lüfter-Schreibbefehle verwenden Direct Access, einschließlich fester Werte und CPU-Assistenz.
- Berechtigungsfehler im Hintergrund erzeugen keine wiederholten modalen Reparaturdialoge.
- Sichtbares Log ist auf 10.000 Zeichen begrenzt; alte vollständige Zeilen werden zuerst entfernt.
- CPU-, LCD-Uhr-, Design- und Anzeigeaktionen werden detaillierter protokolliert.

# Kraken Control 2.9.4

- Animierte Hintergründe lassen sich nach „Animation ausschalten“ wieder direkt einschalten.
- Ausschalten löscht das zuletzt gewählte Animationsthema nicht mehr.
- „Animation aktivieren“ stellt bei alten Einstellungen mit Thema „Aus“ automatisch ein gültiges Thema wieder her.
- Aktivieren/Deaktivieren wird sofort angewendet und im Aktionslog protokolliert.

# Kraken Control 2.9.2 – Einstellungs- und Layout-Hotfix

- Der komplette Bereich **Einstellungen** ist jetzt vertikal und bei Bedarf horizontal scrollbar.
- Design-, DPI-, Hintergrund-, Programm-, Abhängigkeits- und Gerätezugriffsoptionen bleiben auch bei 105–180 % App-Skalierung erreichbar.
- Inhaltsbereich der Einstellungen besitzt eine sinnvolle Mindestbreite und transparente Darstellung über animierten Hintergründen.
- Standardfenster auf 1280×880 vergrößert; Mindestgröße auf 820×600 angepasst; kleinere Fenster bleiben dank Scrollbereich bedienbar.
- Einmalige Migration vergrößert auch eine aus 2.9/2.9.1 gespeicherte kleine Fenstergeometrie, begrenzt auf die verfügbare Monitorfläche.
- Scrollbereich ist per Tastatur fokussierbar und besitzt eine Screenreader-Beschriftung.
- CPU-Offscreen-Renderer, vollständiges Aktionsprotokoll und alle Hardwarefixes aus 2.9.1 bleiben enthalten.

# Kraken Control 2.9.1 – Grafik- und Protokoll-Hotfix

- Darstellungsfehler mit vollflächigen vertikalen Farbstreifen bei animierten Hintergründen behoben.
- Animationen werden nicht mehr direkt auf dem zentralen Inhaltswidget gezeichnet.
- Neue getrennte Ebenen: Hintergrund unten, vollständige Bedienoberfläche immer darüber.
- Sicherer CPU-Offscreen-Renderer über `QImage` mit begrenzter interner Auflösung für Wayland, HiDPI, 21:9 und 32:9.
- Bei einem Renderfehler wird die Animation automatisch gestoppt und die Oberfläche bleibt mit normaler Hintergrundfarbe bedienbar.
- Jeder Mausklick auf interaktive Bedienelemente wird im Log protokolliert.
- Zusätzlich werden Tastaturaktionen, Tabwechsel, Menüaktionen und vom Benutzer geänderte Auswahl-, Regler-, Zahlen-, Text- und Tabellenwerte protokolliert.
- Log-Kapazität auf 10.000 Einträge erhöht.
- Log kann kopiert, geleert und als `.log`/`.txt` gespeichert werden.
- Private Pfade und eindeutige Kennungen werden weiterhin vor der Anzeige bereinigt.

# Kraken Control 2.9 – Einrichtung, Profile und adaptive Oberfläche

- Ersteinrichtungsassistent mit Design, Akzentfarbe, Hintergrund, Monitorprüfung und Start-Kühlprofil.
- Heller Modus ist bei neuen Installationen der Standard.
- Zwölf prozedural erzeugte animierte Hintergründe ohne fremde Mediendateien.
- Einstellbare Bildrate, Intensität und Pause bei inaktiver Anwendung.
- Monitor-, DPI-, Gerätepixel- und Seitenverhältniserkennung.
- Responsive Layoutvorgaben für 16:10, 16:9, 21:9 und 32:9.
- App-Skalierung von 80 bis 180 Prozent.
- Neuer Hauptbereich Profile mit Kategorien Gesamt, Kühlung, LCD, RGB und Design.
- Profile erstellen, aktualisieren, duplizieren, umbenennen, löschen, importieren und exportieren.
- Optionales Startprofil oder zuletzt verwendetes Profil.
- Gesamtprofile speichern auch Hintergrund, Anzeige, Fenstergröße und relevante Hardwareeinstellungen.
- Vollständiger Quellcode-Snapshot und Datei-Prüfsummen im Release.
- Dokumentation und Tests auf Version 2.9 aktualisiert.

# Kraken Control 2.8.1 - Abhängigkeits-Assistent

- Startskript prüft liquidctl, PySide6 und Pillow vor dem Programmstart.
- Fehlende Pakete können nach ausdrücklicher Bestätigung über DNF und die normale polkit-Administratorabfrage installiert werden.
- Keine stillen Installationen und keine zusätzlichen oder fremden Paketquellen.
- Neuer Bereich unter Einstellungen zeigt den Zustand aller Laufzeitabhängigkeiten.
- Abhängigkeiten können dort erneut geprüft und repariert werden.
- Falls PySide6 fehlt, übernimmt das Shell-Startskript die Prüfung, bevor die Python-Oberfläche geladen wird.
- Automatische Paketinstallation ist zunächst bewusst auf Nobara/Fedora-Systeme mit DNF begrenzt.

# Kraken Control 2.8

- Expertenmodus für frei einstellbare Kraken-Wassertemperatur-Warn- und Kritisch-Grenzen.
- Deutliche Warnung vor dem Aktivieren; sichere Standardbereiche lassen sich jederzeit wiederherstellen.
- Klare Anzeige, ob Pumpe und Radiatorlüfter zuletzt als feste Drehzahl, Temperaturkurve oder CPU-Assistenz gesetzt wurden.
- Kühlmodus wird gespeichert und beim nächsten Start angezeigt.
- LCD-Uhr kann das aktuelle Minutenbild zusätzlich automatisch in einem frei wählbaren Intervall erneut senden.
- Minutenaktualisierung und Wiederholungs-Fallback der Uhr arbeiten unabhängig voneinander.
- Kurven-Direct-Access-Hotfix aus 2.7.1 bleibt enthalten.

# Kraken Control 2.7.1 - Kurven-Hotfix

- Pumpen- und Lüfterkurven werden gezielt mit `liquidctl --direct-access` übertragen.
- Behebt `insufficient permissions`, wenn feste PWM-Werte über hwmon funktionieren, die hwmon-Kurvenattribute aber nur für root beschreibbar sind.
- Wiederherstellung der Wasserkurven nach CPU-Assistenz und beim Beenden nutzt denselben Direktzugriff.
- Die udev-Reparatur bleibt für den HID-Schreibzugriff erhalten, wird aber nicht mehr fälschlich als alleinige Lösung für gesperrte hwmon-Auto-Point-Dateien dargestellt.

# Kraken Control 2.7 - Tastatur, AM5-Profile und Berechtigungsreparatur

- Vollständige Tastaturwege mit Menüs und globalen Tastenkombinationen.
- Der grafische Kurveneditor gibt Tab/Umschalt+Tab wieder frei; Strg+Links/Rechts wählt Punkte.
- CPU-Temperaturanzeige über den Linux-k10temp-Treiber mit Tctl/Tdie-Priorität.
- Einzelne AMD-AM5-Profile für ausgewählte Ryzen-7000-, 8000G- und 9000-Modelle.
- Sichtbare Trennung zwischen CPU-Tjmax (89/95 °C) und Kraken-Wassertemperatur (42/50 °C).
- Optionale CPU-Temperatur-Assistenz: verstärkte Kraken-Kühlung ab profilspezifischem Wert, 100 % vor Tjmax.
- Empfohlene Kraken-Wasserkurven je CPU-Profil und automatische CPU-Erkennung.
- Schreibzugriffsprüfung für /dev/hidraw vor Lüfter- und Kurvenänderungen.
- Reparaturschaltfläche mit polkit/pkexec sowie aktualisierte udev-Regel und gezieltes USB-/hidraw-Triggern.
- Laufzeitübersicht für Kraken Control, Python, PySide6, Qt, liquidctl, Pillow, Distribution und Kernel.
- Neue Dateien docs/hardware/CPU_PROFILES.md, docs/hardware/CPU_PROFILES.en.md und docs/project/COMPONENT_VERSIONS.md.

# Kraken Control 2.6 - Grafischer Kurveneditor und Design-Einstellungen

- Interaktiver grafischer Editor für Pumpen- und Radiatorlüfterkurven.
- Kurvenpunkte können per Maus oder Tastatur verschoben werden.
- Tabellenwerte und Diagramm bleiben vollständig synchron.
- Die aktuelle Wassertemperatur wird als Marker in beiden Diagrammen angezeigt.
- Sicherheitsregeln bleiben erhalten: steigende Temperaturen, nicht sinkende Leistung und spätestens bei 50 °C 100 %.
- Kurvenwerte werden gespeichert und beim nächsten Start wiederhergestellt.
- Neue Darstellungsmodi: System, Hell und Dunkel.
- Frei wählbare Akzentfarbe als Hex-Code sowie fünf Farbvoreinstellungen.
- Akzentfarbe gilt für Tabs, Schaltflächen, Fokusrahmen, Regler, LCD-Rahmen und Kurvendiagramme.
- Design-Einstellungen werden sofort angewendet und dauerhaft gespeichert.
- README, englische Dokumentation, Desktop-Eintrag, Diagnosebericht, Tests und Projektverlauf wurden auf Version 2.6 aktualisiert.

# Kraken Control 2.5 - Klarer Projektumfang und modulare Ausrichtung

- Kraken Control bleibt bewusst eine spezialisierte Anwendung für die NZXT-Kraken-Wasserkühlung.
- Unterstützt bleiben Wassertemperatur, Kraken-Pumpe, direkt von der Kraken verwaltete Radiatorlüfter, LCD und der separate NZXT 2023 RGB Controller.
- Mainboard-, Gehäuse- und GPU-Lüfter werden ausdrücklich nicht erkannt oder gesteuert.
- AMD-Grafiksteuerung, allgemeines System-Tuning und externe Lüfterverwaltung sind für eigenständige Werkzeuge vorgesehen.
- Der Über-Bereich zeigt den enthaltenen und ausgeschlossenen Funktionsumfang jetzt deutlich an.
- Die Geräteliste erklärt, dass nur die zur Kraken-Kühlung gehörenden Lüfter unterstützt werden.
- Neue Dateien `docs/project/PROJECT_SCOPE.md` und `docs/project/PROJECT_SCOPE.en.md` dokumentieren die Modulgrenzen.
- Versionsanzeige, Installer, Desktop-Eintrag, Diagnosebericht, README, Sicherheitsdokumentation und statische Tests wurden auf 2.5 aktualisiert.

# Kraken Control 2.4 - Transparente Links und Herstellerverweise

- Der Über-Bereich wurde scrollbar und deutlich ausführlicher gestaltet.
- Für liquidctl, Python, PySide6/Qt for Python und Pillow werden Aufgabe, offizielle Website/Dokumentation, GitHub-Quellcode und Lizenzseite angezeigt.
- OpenAI-, ChatGPT- und OpenAI-GitHub-Seiten sind bei der KI-Unterstützung verlinkt; ChatGPT wird ausdrücklich als Entwicklungsunterstützung und nicht als Laufzeitbestandteil bezeichnet.
- Die eigene Projektseite wird nicht erfunden: GitHub/Codeberg bleiben sichtbar als „noch nicht veröffentlicht“, bis eine echte Repository-Adresse feststeht.
- In der Liste der unterstützten Geräte ist die offizielle NZXT-Seite für Kraken (2023) direkt beim unterstützten Kühler verlinkt.
- Zusätzlich sind die NZXT-Kühlerübersicht und die NZXT-Hauptseite erreichbar.
- Neue deutsche und englische Dateien `docs/project/SOFTWARE_AND_LINKS.md` / `docs/project/SOFTWARE_AND_LINKS.en.md` dokumentieren alle verwendeten Komponenten, Herstellerseiten, Quellcode- und Lizenzadressen auch außerhalb der Anwendung.
- Versionsanzeige, Desktop-Eintrag, Installer, README und Sicherheitsdokumentation auf 2.4 aktualisiert.

# Kraken Control 2.3.1 - Sicherheitsupdate

- Programmstatus deutlich als **experimentelle Open-Source-Beta** gekennzeichnet.
- Pumpenwerte unter 30 % und Lüfterwerte unter 20 % erfordern eine ausdrückliche Bestätigung.
- Kühlkurven müssen streng ansteigende Temperaturen, nicht sinkende Leistung und spätestens bei 50 °C einen 100-%-Endpunkt besitzen.
- Neue Schaltfläche für ein sicheres Standardprofil mit 65 % Pumpe, 65 % Lüfter und aktivierter kritischer Schutzumschaltung.
- Warn- und kritische Temperaturgrenzen können sich nicht mehr überschneiden.
- Wiederholter LCD-Fallback und LCD-Uhr werden beim ersten Start nach dem Update vorsorglich deaktiviert.
- Vor dem Aktivieren von LCD-Fallback oder Uhr erscheint eine Warnung zu den unbekannten Langzeitwirkungen häufiger Uploads.
- Diagnosewerkzeug arbeitet jetzt ausschließlich lesend; `liquidctl initialize all` wurde entfernt.
- Diagnosebericht entfernt zusätzlich Home-Pfade, Benutzerkennungen, Hostnamen, Machine-ID und Boot-ID.
- Kopierbare Programmlogs anonymisieren Home-Pfade und typische eindeutige Kennungen.
- Neue Sicherheitsdokumentation `SECURITY.md`.

# Kraken Control 2.3

- Programmname sichtbar zu **Kraken Control by Frelidon** erweitert.
- Neuer **Über**-Bereich mit Projektstatus, unabhängiger Markenkennzeichnung, KI-Unterstützung, GPL-Lizenz und unterstützten Geräten.
- Neue LCD-Uhr mit 24-Stunden- und 12-Stunden-/AM-PM-Format.
- Optionale Datumsanzeige, einstellbare Schriftgröße sowie frei wählbare Text- und Hintergrundfarben.
- Die Uhr erzeugt ein statisches 240×240-Bild und aktualisiert es gezielt zum nächsten Minutenwechsel; Sekunden werden nicht übertragen.
- Uhrmodus wird gespeichert und kann beim nächsten Programmstart automatisch fortgesetzt werden.
- Runde LCD-Vorschau mit kreisförmigem Beschnitt und sichtbarem Displayrahmen.
- Lange LCD-Einstellungen in einen scrollbareren Bereich verschoben.
- Startmenü-Symbol robuster installiert: absolute Symbolreferenz plus Aktualisierung des KDE/Plasma-Caches.
- Neues datenschutzfreundliches Diagnosewerkzeug `kraken-control-diagnostics` für zukünftige Geräteunterstützung.
- Englische Grunddokumentation und separate Liste unterstützter Geräte ergänzt.
- Lizenz auf **GPL-3.0-or-later** festgelegt.

# Kraken Control 2.2

- LCD-Bedienung an das tatsächliche Verhalten der Kraken-Firmware 2.0.0 angepasst.
- Die missverständliche Option **„Bild dauerhaft anzeigen“** wurde durch **„Automatisch erneut senden (Fallback)“** ersetzt.
- Ein statisches Bild kann bewusst einmal übertragen werden; die Oberfläche erklärt, dass es auf Firmware 2.0.0 bereits ohne Wiederholung dauerhaft sichtbar bleiben kann.
- Der LCD-Fallback startet erst, nachdem der erste Bild-Upload erfolgreich abgeschlossen wurde.
- Bei einem fehlgeschlagenen Upload wird der Fallback automatisch wieder deaktiviert.
- Intervallsteuerung ist nur aktiv, solange der Fallback eingeschaltet ist.
- Neuer sichtbarer LCD-Status für Einzelübertragung, Fallback und Flüssigkeitstemperaturmodus.
- **„Zur Flüssigkeitstemperatur zurück“** beendet den Fallback zuverlässig und setzt den gespeicherten Zustand zurück.

# Kraken Control 2.1

- Absturz unter Python 3.14 / PySide6 6.11 behoben.
- QThreadPool und QRunnable entfernt.
- Serielle, asynchrone QProcess-Warteschlange hinzugefügt.
- Sauberes Beenden laufender Prozesse beim Programmende.

# Kraken Control 2.0

- Oberfläche vollständig neu strukturiert.
- Kraken und separater RGB-Controller korrekt getrennt.
- Live-Dashboard, Profile, Pumpen-/Lüfterkurven und Sicherheitsfunktionen ergänzt.
- LCD-Vorschau, Bildübertragung, Autostart, System-Tray, Installer und Deinstaller ergänzt.
