# Open Hardware Control 3.4.24 INTERN

3.4.24 is the first full UI-design release built around the new compact OHC dashboard concept.

## Highlights

- Persistent compact navigation rail with Open Hardware Control branding only; no Community Edition subtitle.
- Dedicated page titles and subtitles for Overview, Cooling, RGB Studio, LCD, Profiles, Log and other modules.
- Redesigned Overview with compact metric cards, quick actions, detected hardware and status/hints.
- Redesigned Cooling Center with separate CPU/Kraken and chassis-fan summary cards.
- Direct chassis-fan actions: Test, Curve, Assign and per-channel automation state.
- Dedicated fan curve dialog so detailed editing no longer requires scrolling to a distant editor.
- CoolerControl ownership/conflict status directly below the cooling summaries.
- Four-step chassis-fan wizard: Detect → Test → Assign → Save.
- Fresh installs default to the modern dark theme; an existing explicit user theme remains respected.
- Existing NCT6687/Polkit helper, watchdog, calibration and firmware-return safety behavior is retained.
- Internal release validation now includes a real PySide6 offscreen GUI smoke test.

## Safety

No new raw EC/SMBus register writes were added. Mainboard PWM writes continue through the existing constrained helper/sysfs path, and CPU_FAN/PUMP_FAN remain excluded from chassis-fan automation.
