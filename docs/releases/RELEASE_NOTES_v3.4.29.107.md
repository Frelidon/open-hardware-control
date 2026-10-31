# Open Hardware Control 3.4.29.107 INTERN

## GPU fan control

OHC can now prepare a five-point GPU fan curve using LACT-reported fan and
temperature limits. The user edits the points in OHC; LACT remains the sole
writer. CoolerControl must release the GPU fan first. The short preview is
automatically reverted by LACT and permanent saving remains a separate click.
The user no longer needs to create an initial fan profile in LACT. The curve
editor uses the edge-temperature sensor and requires a rising curve reaching
at least 90% by 90 °C.

## Load testing

The GPU page adds a cancellable 15, 30, 60 or 120 second load test for OHC
settings that have already been confirmed in LACT. It monitors the selected
GPU's load, temperature and throttle reports. On a detected fault, OHC
restores its previous LACT snapshot only if the saved GPU configuration still
matches; otherwise it reports that rollback could not be verified. A test
with less than 50% observed GPU load is inconclusive. The short preview of a
new clock or power setting also requires observed load before it can unlock
permanent saving. LACT's default five-second confirmation timeout prevents
holding an unsaved clock setting for a longer benchmark.

The optional vkmark Vulkan scene is preferred to the small cube in the GPU
page and Hardware Checker. The GPU page can offer the Fedora vkmark package
from configured repositories after user confirmation. glmark2 remains an
alternative and Hardware Checker retains vkcube as a fallback.

## Verification

The implementation was tested using simulated LACT responses, UI and
localization checks. No live GPU setting, benchmark, package installation or
service restart was performed during development. Real hardware behavior
must be checked after a deliberate installation by the owner.
