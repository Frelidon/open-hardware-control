# Roadmap

## Current .182 UI step · 12.11.26 — locally installed and verified

The owner requests the next LCD cleanup, one GPU workspace retaining artwork
and showing tuning beside a larger fan curve, plus animated-background settings
first and other existing groups prioritized. Preserve all options, drafts,
profiles, themes, native animations and owner/write safeguards. Source/UI checks,
six packages, both .181/.182 backups and both local .182 installations are verified.
Source implementation is complete: LCD workspaces reuse the original controls,
GPU tuning/curve share one page, and all 17 Settings groups remain reachable.
Targeted checks and full-window source Qt views pass. The final release gate
passes 1,736 tests/five subtests plus compilation, security, privacy and budgets.
Installed Wayland views of GPU, all three LCD tasks and Settings pass in both
themes with isolated settings and no hardware IO. Normal CPU/RGB/Levita startup
is confirmed separately; profiles and both plugins remain unchanged. Packages
and backups remain immutable snapshots preceding this installation evidence.
No GitHub publication requested. Earlier .181 "next" items below are the request
completed by this step. New game integrations and Windows remain separate work.

## Current .181 UI step · 12.11.26 — locally installed and verified

The next bounded owner-requested step is in source: common large section cards
and cancellable profile scrolling, case/component presentation, 15 matching
RGB/LCD pairs with real per-pair sizes, embedded LCD media management, clear
preview progress, help and honest inventory/LACT read status. Preserve settings,
profiles, backgrounds, existing renderers and all hardware-owner/write guards.
User and system .181 are installed and byte-verified against all 464 Python sources.

30 current hub/size/metadata tests, 184 RGB loop checks and 12 section/case
tests pass. Four full UI/localization tests confirm 2,584 shared IDs. Complete
Qt main-window renders of the hub, case and help pass in both themes; explicit
combo ownership fixes the native layout crash and bounded content hints fix
narrow-width clipping. Newer LCD intent and page hiding cancel stale encoder
work; cached MP4 structure receives bounded H.264/geometry/duration checks.
Source validation passes: 1,732 tests/five subtests, compilation, security,
privacy, module budgets and remaining release checks after old local bytecode
cleanup. Six packages, both .180/.181 backups and local .181 installation are verified.
Native installed Wayland views pass in both themes with isolated settings and
disabled hardware IO. Existing profiles/plugins survived; the normal saved RGB
and Levita startup is confirmed by the session log. No GitHub upload/release is requested.
Details and original concepts: [UI redesign plan](UI_REDESIGN_PLAN.md).

### Next bounded steps after this checkpoint

- Review the larger GPU layout and fan-curve concept, then implement/test it with
  the existing short-test, rollback and ownership rules. A read-status badge
  does not complete the full GPU redesign.
- Review remaining legacy LCD menus and simplify them without deleting design,
  import, sensor-layer or playback features. The integrated manager is one step.
- Continue the remaining cross-page/HiDPI audit. Three source window sizes,
  four languages, both themes and installed native views are checked for this
  batch; physical RGB/LCD output and real Fedora hardware remain separate.

### Earlier requests still open

- Modular support for additional manufacturers based on actual diagnostics and
  tested hardware; do not infer control from a brand or LED count.
- Improved RGB color selection and more original fan effects; OpenRGB Originals
  remains and the former redundant RGB OHC Originals group stays redistributed.
- Automation Center program suggestions/file selection, time/calendar workflows
  and night-light options beyond the existing automation rules.
- Actual game telemetry and screen ambience. Existing game integration prepares
  editable process/profile rules only.
- Real Windows hardware-control support beyond the existing preview/build
  infrastructure; separate platform/capability/safety work remains necessary.


## Completed .176 public release · 11.11.26

.176 STABLE is published as Latest, tag/source commit `34c64d3`. Main is updated
without a force-push. All six public package digests match the verified local
build; downloaded SHA256SUMS matches the exact GitHub filenames. Both retained
INTERN/STABLE backups pass eight/nine hashes. The local STABLE gate passes
1,587 tests and five subtests. GitHub's Ubuntu dependency setup has a DNS
failure, so the validated local packages were uploaded through the release UI;
no remote CI success is claimed. The running local INTERN app is unchanged.

## Completed local .176 checkpoint · 11.11.26

Fan mapping now supports explicit disconnected ports, compact remapping access,
120-second chassis identification with a short refreshed driver crash lease and
automatic scoped white RGB lighting. Temperature recording has sensor icons,
ID-only drag selection and reusable current/min/max cards. Four-language real
UI and safety fixtures pass; the full gate passes 1,587 tests and five subtests.
All six artifacts and both .175/.176 rolling backups are verified. User and
system installations are complete (3.4.29.176~intern2), with exact parity for
414 Python sources. Saved profiles/plugin and the active native/GPU/LCD state
are preserved. Real fan stop/crash and Fedora hardware checks are not claimed.
The previous .175 GitHub upload remains unchanged during this follow-up.

## Completed .175 follow-up · 11.11.26

Reviewed model-level links and category/vendor filters are implemented. The
reproducible shifted-row pointer selection is fixed. Full gate: 1,556 tests and
five subtests pass. Packages and both rolling backups are verified; the user
installation is running with preserved settings and healthy native workers.
The system package update is complete (3.4.29.175~intern2); both installed
trees match all 406 Python sources, and the user app remains active with five
native workers and zero reported errors. The internal source upload to
`codex/3.4.29-intern` is verified (`5fd7989`); no public tag/release or default
branch change is part of this upload.

Open Hardware Control is developed incrementally. Features are tested before they
are treated as stable. This file contains only active work; completed planning
records remain in release notes, the changelog and `NEXT_VERSION_NOTES.md`.

## Current work — 3.4.29 INTERN

### Historical UI implementation checkpoint .174 · 11.11.26

The .174 implementation and both local copies were verified against 403 Python
sources, 1,544 tests and five subtests. Startup-DPI preference, case/fan catalog,
OpenLinkHub .9.4 update and localized hardware navigation are established work.
Later .175–.180 checkpoints are recorded in release notes and project status;
the current source/validation boundary is the .181 section above. Publication
remains a separate explicit owner action.

### Closure audit for 3.4.29.151–3.4.29.157

| Version | Repository implementation | Remaining evidence |
|---|---|---|
| `.151` | Mainboard driver/MOK workflow, separated Ubuntu update/install path and bounded fan grant are present with regressions. | No repository implementation item remains. |
| `.152` | CPU defaults, complete PC PWM topology, profile persistence and module visibility are present with regressions. | No repository implementation item remains. |
| `.153` | Deleted-Qt-object guards, Snapshot Manager shutdown handling and module cards are present with regressions. | No repository implementation item remains. |
| `.154` | Detailed OpenRGB inventory, external GPU routing, narrow RAM metadata helper and package payload checks are present with regressions. | Optical output was not inferred from protocol success. |
| `.155` | Startup-policy separation, occupied-display ownership handling and safe package-directory modes are present with separate Ubuntu/Fedora fixtures. | Repeat on real Fedora hardware. |
| `.156` | Editable LED drafts, spatial direction fixes and animated fan-ring previews are present with regressions. | Confirm brightness, direction and LED order optically. |
| `.157` | Programs inventory/profiles, guarded GitHub download, exact downloaded-AppImage selection and bounded own-daemon Levita recovery are present with regressions. | Release-gate/package evidence is recorded separately; Fedora and optical checks remain owner/hardware work. |

An item is not reopened merely because an older release note says a package or
installation was pending at that historical point; later status evidence records
the completed builds and Ubuntu installation. Real-hardware/optical evidence stays
open until it is actually observed.

### Actionable in the repository

- Measure first: keep UI-event latency, worker duration, cache I/O and display
  frame gaps separate. Add a regression or reproducible measurement before
  changing a hot path and record the result afterwards.
- Keep the Qt main thread free of discovery, decoding, filesystem scans, network
  access and package-manager calls. Work must be bounded, cancellable and must
  not outlive its page or application owner.
- Continue splitting large pages into versioned feature modules with pure,
  directly testable policy/render helpers. Preserve the public Python interfaces
  and Fedora/Ubuntu behavior while moving one responsibility at a time.
- Finish keyboard navigation, focus-state, scaling and profile-migration checks
  for the migrated pages; move new visible text into all four language catalogs.
- Keep the **Programs** module bounded after its installed-application inventory,
  saved profiles, guarded GitHub release/source download, confirmed Flatpak/
  Snap/AppImage actions, persisted source association and exact downloaded-
  AppImage selection. System packages remain disabled without a confirmed
  distribution source.

### Requires owner or real-hardware confirmation

- Confirm case RGB brightness, direction and physical LED order optically.
- Repeat the current hardware and ownership checks on real Fedora hardware;
  Ubuntu results and Fedora fixtures are not a substitute.
- Broaden GPU, fan, display and RGB compatibility only from diagnostic reports
  or tested hardware. Do not advertise inferred compatibility.

## Packaging

Fedora/Nobara RPM and Debian/Ubuntu DEB remain separate, equally supported
paths. Further candidates are:

- Arch/AUR PKGBUILD;
- Flatpak only after its hardware-access and privilege constraints are proven;
- AppImage only with an explicit hardware-helper and update model.

## Performance and implementation language

The application remains Python/PySide6. A complete Rust rewrite would discard
mature UI, hardware, packaging and regression behavior without proving a user
benefit. Rust is an optional implementation detail for an isolated, pure CPU
hotspot only when a profile demonstrates that Python is the bottleneck. Such a
component needs the existing Python API, a safe Python fallback, identical test
fixtures and separate package support. Hardware writes, privilege boundaries and
Qt ownership are not moved merely for language uniformity.

## Longer term

- More Kraken models based on diagnostic reports and real hardware testing.
- Optional CPU performance controls as a separately reviewed future module:
  begin read-only, use documented AMD/Linux interfaces, retain firmware thermal
  limits and never mix clock/voltage writes into the fan helper. PBO, power
  limits, frequency caps and undervolting need separate capability detection,
  rollback, suspend/resume and crash-safety tests before any write path.
- Optional shared launcher/control-center concept for separate Frelidon tools.

This roadmap is not a promise of dates or compatibility.
