# Open Hardware Control 3.4.29.66 INTERN

Cooling quick profiles now remain visibly identifiable after they are applied.
Quiet, Balanced and Performance set fixed profile values for the selected AIO
pump and radiator fans, while calibrated case fans receive the matching curve
template. The previous generic “Manual” display has been replaced by explicit
fixed-profile, custom-fixed-value and CPU-curve states; duty values and safety
rules are unchanged.

Overview adds an interactive session temperature history for CPU, GPU and a
genuine coolant sensor where one exists. Users can show or hide each series and
choose five, fifteen or sixty minutes or the full session. Hovering shows the
timestamp and readings. Up to one hour/1,800 validated samples are held in RAM
only and disappear when OHC exits. Levita coolant is never inferred.

Hardware Backends 1.0 adds persisted, fail-closed choices in Settings. Version
1.0 exposes only transports that already exist: TRCC Linux for the Levita
display and calibrated OHC Linux-hwmon for motherboard fans. Planned native
Levita and CoolerControl adapters are visible but disabled until implemented
and validated. An explicit unavailable choice never silently falls back.

All new interface text is available in German, English, Spanish and French.
Calibration, CoolerControl ownership protection, watchdog handling, firmware
return and the existing hardware transports remain unchanged. No GitHub push,
tag or public release was created.
