# Open Hardware Control — Agent Device-Support Summary

`SUPPORTED_DEVICES.md` is the authoritative human-facing compatibility document. This file is a concise agent index; update both when support changes.

## Directly tested / primary reference

- NZXT Kraken 2023 (`1e71:300e`) through the validated NZXT/liquidctl path: liquid temperature, pump, radiator fan and LCD on the tested reference configuration.
- NZXT 2023 RGB Controller (`1e71:2012`): three RGB channels through the validated NZXT path.

Do not promote other detected Kraken capability entries to “tested” without real hardware evidence.

## Thermalright Levita Vision 360 ARGB Black

- Exact product identity: `Thermalright Levita Vision 360 ARGB Black`.
- Display: USB `87ad:70db`; OHC's 1600×720 editor and safe local test mode are verified. Real writes are delegated to the separately installed TRCC Linux backend and are not yet promoted to fully hardware-tested status.
- Cooling: pump and radiator fans connect to motherboard 4-pin PWM headers. Driver labels may suggest `Pump Fan` and `CPU Fan`, but both mappings require independent physical 70-percent/10-second confirmation.
- Read-only evidence on the reference system found pump and CPU-fan RPM through NCT6687. PWM response still requires user confirmation in OHC.
- CoolerControl ownership blocks concurrent writes. Owned headers are restored to firmware/BIOS control on exit.
- No coolant sensor is exposed through this path; never synthesize one from CPU/GPU temperatures or RPM.

## Corsair

Corsair devices are discovered through the locally installed OpenLinkHub service/API. OHC intentionally does not maintain a guessed direct Corsair USB support table. Available actions depend on what the installed OpenLinkHub version reports and supports.

## OpenRGB devices

RGB coverage follows the user's separately installed OpenRGB backend. OHC uses its private local engine and bounded SDK helper. Detection does not equal validated hardware compatibility; unfamiliar controllers must be tested conservatively, especially variable ARGB LED counts/zones.

## Mainboard/chassis fans

The current backend targets Linux hwmon PWM control with a focus on NCT6687/NCT6687D. Electrical channel mapping must be calibrated and physically confirmed. Board name alone is diagnostic metadata, not a safe mapping source.

## Explicitly outside current support claims

- GPU fan control through the mainboard fan subsystem.
- Firmware flashing/updating/version switching.
- General voltage/clock tuning.
- Unverified direct Corsair USB writes.
- Open Radeon Control Center integration into this repository.

When adding support, record: device identity, read-only detection evidence, write path, safety/ownership model, real hardware test status, and regression tests.
