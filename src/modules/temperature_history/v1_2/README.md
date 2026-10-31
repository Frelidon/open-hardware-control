# Temperaturverlauf 1.2

`gauge.py` draws the same compact twelve-segment 0–100 °C scale in Overview,
Cooling and Temperature Recording. It reads only the already sampled Celsius
value. The scale is visual context, never a thermal safety threshold.

.91 keeps the public API but lazily resolves GUI exports, so pure sensor imports
load no Qt. The production panel consumes Process Runtime's fresh read-only
sensor catalog; synthetic/legacy hosts without runtime retain the reader helper.
No duplicate production GUI sysfs sweep or new hardware/report-write authority.

Version 1.2 keeps the compact CPU/GPU/coolant graph and dedicated,
interactive cooling-page recorder for every plausible read-only Linux hwmon
temperature. It groups CPU, GPU/hotspot/VRAM, DDR5 SPD, NVMe/SSD, motherboard,
VRM and other sources, exposes current/minimum/maximum values, and stores only
a bounded session history in memory. Local date and time now appear on axes,
hover details and the readings table. A resizable split view and explicit
CSV/JSON report manager export any selected sensors and absolute session range;
no file is created automatically. Its panel mixin keeps the fixed Cooling
sidebar children and the internal control/recording views synchronized in both
directions. The module never writes hardware and writes reports only after the
user chooses a destination.
