# Open Hardware Control 3.4.29.127 INTERN

Internal development build, 1 October 2026.

## Snapshot Manager

- Adds a dedicated configurable main page for Linux snapshot status, scheduling
  protection, Btrfs cleanup limits and a read-only Snapper snapshot list.
- Detects the operating system, mounted filesystems, Snapper, Timeshift, Btrfs,
  ZFS and LVM tools, and marks backends that are demonstrably active.
- Uses Feral GameMode, Gamescope, configured process names and KDE active
  full-screen state as preferred game signals. An optional guarded CPU/GPU
  fallback requires sustained load on several cores and the GPU.
- Resumes after sustained desktop/idle state. Manual blocking supports one hour,
  a selected date/time or indefinitely.

## Safety boundary

- A dedicated root-owned Polkit helper accepts only two fixed Snapper timers,
  bounded Btrfs discard values, a bounded deadline and a validated Snapper
  configuration name. It cannot run arbitrary commands, units or paths.
- Existing Btrfs kernel cleanup is throttled; the UI does not claim that it can
  be killed safely. Full Snapper rollback remains outside a one-click action.
- Persistent automation authorization is explicit and scoped to the requesting
  desktop user and this one Polkit action; no password is stored.

## Verification

- Pure policy/parser tests, helper-surface security guards, navigation and
  packaging checks, four-language catalog coverage and the complete offscreen
  Qt page construction are included.
- The complete gate passes 828 tests plus security/privacy/module checks.
  Runtime/developer ZIPs, source archive, Local-AI bundle and RPM are built and
  SHA-256 verified. No DEB is produced because `dpkg-deb` is unavailable on
  this host. Rolling `.126` and `.127` backups both verify successfully.
- The actual dark OHC surface is rendered to
  `docs/images/rendering-evidence/snapshot-manager-3.4.29.127.png` with
  deterministic demo data and hardware I/O disabled.
