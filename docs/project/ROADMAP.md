# Roadmap

## Current .175 follow-up · 11.11.26

Reviewed model-level links and category/vendor filters are implemented. The
reproducible shifted-row pointer selection is fixed. Full gate: 1,556 tests and
five subtests pass. Packages and both rolling backups are verified; the user
installation is running with preserved settings and healthy native workers.
The system copy awaits OS authentication. The internal source upload to
`codex/3.4.29-intern` is verified (`5fd7989`); no public tag/release or default
branch change is part of this upload.

Open Hardware Control is developed incrementally. Features are tested before they
are treated as stable. This file contains only active work; completed planning
records remain in release notes, the changelog and `NEXT_VERSION_NOTES.md`.

## Current work — 3.4.29 INTERN

### Owner-requested UI redesign — implementation checkpoint 11.11.26

The .174 implementation passes 1,544 tests and five subtests. The primary user
installation is running and the system package update has completed. Both
installed trees match all 403 Python sources. Profile/plugin preservation, native workers, GPU mode and saved LCD
restore are verified read-only. No DPI override is enabled without explicit Save.


Two review concepts and the implementation scope are recorded in
[UI redesign plan](UI_REDESIGN_PLAN.md): case/fan catalog, content-sized lists
across menus, OpenLinkHub update and device UI, and localized Hardware Check
navigation with Hardware Fix as a child. Pictures are presented before code
changes; later local installation/restart is authorized, publication remains
separate. This is planned work, not an implemented or installed version.

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
