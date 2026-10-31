# TRCC backend 1.0

This module owns the explicit installer hand-off for the separately maintained
GPL-3.0 TRCC Linux backend used by Thermalright Levita displays.

- Installation is offered only after OHC has read-only detected the supported
  Thermalright USB device and found no `trcc` executable.
- The packaged helper is Ubuntu-only. Fedora and all other distributions keep
  their existing behavior and are directed to the upstream instructions.
- The helper downloads the pinned, tested official release and verifies its
  published SHA-256 digest before asking APT to install it.
- Installation does not apply a display design or perform USB writes.

On Ubuntu, OHC adapts only the root-owned system TRCC process through
`runtime.py` / `launcher.py`. Its exact RAM-speed DMI read uses the dedicated,
argument-free `/usr/libexec/open-hardware-control-dmi-memory-helper`; the helper
runs one trusted system `dmidecode -t memory` with a minimal environment and
removes serial numbers, asset tags and UUIDs. Its Polkit action is limited to
active desktop sessions. Missing helper or other optional metadata requests
fall back to unprivileged reads; IMC elevation is disabled only in this child
process. Spawned OHC daemons inherit the adapter. No upstream file, global PATH,
fan grant, existing foreign daemon or Fedora command is changed. The DEB/RPM
contains the helper/policy; explicit Ubuntu ZIP setup installs that same pair.
