# Open Hardware Control 3.4.29.102 INTERN

## GPU control

The new GPU page uses LACT's local Unix socket for GPU measurements and
optional tuning. A change is first applied for a bounded load trial. LACT
automatically reverts unconfirmed settings; OHC explicitly requests the
revert and checks the prior configuration before offering a separate permanent
save. Previously saved values are retained per GPU for a later explicit
restoration, even after an OHC restart. A short trial does not prove long-term
clock, voltage or thermal stability. No GPU setting is written on page open.

CoolerControl's GPU fan assignments are checked before LACT writes. Users can
release the LACT fan channel and assign the GPU in CoolerControl; case fans may
remain under CoolerControl. Firmware remains the release fallback. RGB Studio
continues to own GPU lighting through OpenRGB, separate from LACT performance
and fan tuning.

The GPU page now lists OpenRGB-classified graphics-card lighting controllers.
Supported MSI and ASUS cards can use their own I²C/SMBus controller without
an ARGB motherboard cable. Actual OpenRGB detection, modes and zones determine
what OHC can control; vendor names alone do not qualify a card. The existing
RGB Studio path remains the sole lighting writer.

## Setup and shutdown

The first-run wizard offers opt-in LACT and OpenRGB installation. LACT is
installed from its documented Fedora COPR or Arch repository only after
confirmation and Polkit authorization. Other distributions open LACT's
official package instructions. LACT 0.10.1 is the minimum for GPU writes.

An independent observer records whether the application completed its ordered
exit. After an unexpected end it may stop only OHC-owned helpers whose exact
PID incarnation was journaled; it records the result for the next startup
log. A CoolerControl service stopped temporarily for OHC is returned on
normal exit or attempted after a crash. Power loss, denied Polkit access and
unavailable system services cannot be recovered by a user-space observer.

## Verification status

The complete release gate passed 733 tests, including offscreen UI, GPU
module, localization and process-shutdown regressions, plus security/privacy
and module-registry checks. LACT is not installed on the reference machine,
so real GPU tuning and fan handoff remain unverified. Package checks must pass
before this internal version is considered built. No installed
application or hardware settings were changed during development.
