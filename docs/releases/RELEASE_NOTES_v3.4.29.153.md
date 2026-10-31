# Open Hardware Control 3.4.29.153 INTERN

## LCD category crash fixed

- The supplied crash report was traced to the Thermalright Levita preview
  queue after rapid category changes such as **Aesthetic**, **Own files**, and
  **Nature**.
- Qt had already destroyed an old preview card while its Python weak reference
  still existed. The visibility scheduler then called `isVisibleTo()` on the
  invalid wrapper and raised the same `RuntimeError` again on later scroll
  signals.
- Both thumbnail scheduling and finished-preview delivery now validate and
  prune deleted Qt wrappers before calling widget methods.
- Delayed Snapshot Manager timeout callbacks also ignore QProcess wrappers
  already destroyed during shutdown.
- All delayed LCD callbacks are window-bound; deleted pages cancel library,
  progress and recovery callbacks without changing delays or hardware behavior.

## Restored module design

- The functional but plain module checkbox grid from `.152` is replaced by the
  established OHC card language: two columns, module icons, green/grey status
  dots, and direct toggle switches.
- Sidebar customization and Settings share the same persisted visibility
  state. Existing ordering and hidden modules are retained.
- Hiding a module remains a navigation-only operation and does not stop or
  alter active hardware control.
- All 16 optional navigation pages include synchronized switches, including
  the restored automation centre.

## Preserved features and Ubuntu responsiveness

- Compared the verified `.148` archive and recovered feature switches,
  ownership choices, design automation, snapshot creation/filter/resource
  controls, hardware overview cards, GPU artwork and dashboard customization.
  Later Ubuntu fixes remain present.
- Restored Circuit Chase, Neon Particle Garden, Prism Drift and Twin Wyrm Orbit
  with original licensed assets. The display-effects catalogue now has 25 designs.
- Sidebar visibility no longer overwrites function enablement. Each PC profile
  retains its own explicit radiator/pump routing, including deliberately empty
  roles; no mapping leaks in from another profile.
- Ubuntu LACT inventory, metrics and clocks use bounded cancellable background
  processes. Stale results cannot update a different GPU. An unavailable clocks
  table is optional and does not block stats.
- GPU power increases require explicit inline confirmation. Disabled features
  and non-OHC owners block writes.
- Complete fan labels wrap at narrow sizes; a scroll fallback keeps the entire
  curve reachable. All fan-workflow states are translated in DE/EN/ES/FR.
- Delayed GPU/Hardware Fix callbacks follow QObject lifetime; old Hardware
  Checker replies and deadlines cannot affect replacement processes.

## Current external interfaces

- Official release/tag checks and native package queries run off the GUI thread.
  Missing and untracked programs are distinct.
- Ubuntu/Arch dependencies include vkmark. Package-family selection uses
  `os-release`, never the incidental presence of a foreign package tool.
- SDK 6 is an explicit Ubuntu OpenRGB lane; SDK 4/5 and Fedora's default remain.
- OpenLinkHub 0.9.2 user installs are recognized; rejected HTTP-200 writes no
  longer appear successful. Nexus touch-key casing, inclusive bounds and
  unique atomic temporary/backup files match the current interface.
- Local OpenLinkHub requests reject redirects and ignore environment proxies.
- Ubuntu can select explicitly installed root-owned OpenRGB 1.0/liquidctl 1.16.0
  from a fixed versioned tree; distro files and the Qt runtime remain intact.
- Software upgrades are separately approved operations; checking a version
  never updates it or restarts a hardware service.

## Verification and scope

- Added an exact regression with a deleted C++ preview-card object.
- The complete real Qt UI builds and the Settings page renders offscreen with
  hardware I/O disabled.
- All four language catalogs contain 2,152 shared messages.
- Fedora-specific package/setup commands are retained. Shared established UI
  features were restored; no hardware success is claimed by offscreen tests.
- The supplied later log does not establish a new native crash cause. The
  deleted-preview exception is fixed; physical RGB/fan/display behavior still
  requires owner verification.
