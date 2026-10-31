# Open Hardware Control 3.4.29.104 INTERN

## LACT GPU first setup

The owner's `.103` session installed and started LACT 0.10.1 successfully,
but the GPU page could not display controls. On the live system, LACT reports
the integrated GPU and RX 9070 XT, no saved GPU config for either, and disabled
AMD Overdrive. LACT's null config is a valid first-run state; OHC had treated
it as a fatal error before reading GPU measurements.

The page now shows read-only stats and hardware information with an empty
profile, selects the dedicated GPU by default, and reports the Overdrive state.
It offers a button to open the LACT GUI for explicit Overdrive activation and
baseline setup. Clock and power tuning remain locked until Overdrive is active
and LACT has saved baseline values. This version does not set kernel flags,
regenerate initramfs, reboot or alter live GPU values by itself.

The inactive CoolerControl service is described as having no GPU fan conflict.
Trying to release a GPU fan when LACT has no fan profile reports that the fan
is already free.

## Verification

All 742 release tests and security/privacy/module checks passed. The internal
RPM, runtime/developer ZIPs, source archive and Git bundle were built. Both
`.103`/`.104` external backup manifests, dist SHA-256 and ZIP integrity passed.
DEB was unavailable on this Fedora host. Live GPU tuning and fan writes were
not performed.
