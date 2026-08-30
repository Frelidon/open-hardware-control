# Open Hardware Control — Agent Device-Support Summary

`SUPPORTED_DEVICES.md` is the authoritative human-facing compatibility document. This file is a concise agent index; update both when support changes.

## Directly tested / primary reference

- NZXT Kraken 2023 (`1e71:300e`) through the validated NZXT/liquidctl path: liquid temperature, pump, radiator fan and LCD on the tested reference configuration.
- NZXT 2023 RGB Controller (`1e71:2012`): three RGB channels through the validated NZXT path.

Do not promote other detected Kraken capability entries to “tested” without real hardware evidence.

## Thermalright Levita Vision 360 ARGB Black

- Exact product identity: `Thermalright Levita Vision 360 ARGB Black`.
- Display: USB `87ad:70db`; OHC's 1600×720 editor and safe local test mode are verified. TRCC Linux 9.9.11 completed a visually confirmed hardware color cycle, and its authoritative handshake reported model ID 64/sub-byte 3 at 1600×720. OHC design/video/overlay longevity still requires an in-app real-hardware test.
- Cooling: pump and radiator fans connect to motherboard 4-pin PWM headers. Driver labels may suggest `Pump Fan` and `CPU Fan`, but both mappings require independent physical 70-percent/10-second confirmation.
- Read-only evidence on the reference system found pump and CPU-fan RPM through NCT6687. PWM response still requires user confirmation in OHC.
- CoolerControl ownership blocks concurrent writes. Owned headers are restored to firmware/BIOS control on exit.
- After explicit Polkit authorization, repeated curve writes reuse one narrowly validated helper child bound to the OHC process. This avoids background reauthorization after several minutes without weakening the required calibration or fixed-path helper validation.
- An optional user-installed exact-account Polkit rule can retain that authorization across reboots. OHC exposes separate grant/remove controls, stores no password and continues to require physical PWM-channel confirmation.
- Since 3.4.29.8 the helper mirrors grant state into a root-owned readable marker because Fedora's Polkit rule directory is intentionally not traversable by the desktop user. The marker is status only; Polkit remains authoritative.
- DC/PWM selection is available only for a channel whose Linux driver exposes `pwmN_mode`. Changing it invalidates calibration and activation and requires the physical test again.
- No coolant sensor is exposed through this path; never synthesize one from CPU/GPU temperatures or RPM.

## Corsair

Corsair devices are discovered through the locally installed OpenLinkHub service/API. OHC intentionally does not maintain a guessed direct Corsair USB support table. Available actions depend on what the installed OpenLinkHub version reports and supports.

## OpenRGB devices

RGB coverage follows the user's separately installed OpenRGB backend. OHC uses its private local engine and bounded SDK helper. Detection does not equal validated hardware compatibility; unfamiliar controllers must be tested conservatively, especially variable ARGB LED counts/zones.

The private server and every short-lived OpenRGB CLI client are launched through Qt's offscreen platform. This is a window-suppression property only and does not change device compatibility or ownership.

If the private OpenRGB process crashes during backend discovery, OHC quarantines automatic restart for the rest of the session. A deliberate manual re-detection is required before another backend launch, preventing repeated driver coredumps.

For Frelidon's versioned personal PC layout only, the Jungle Leopard GPU support is confirmed as one 24-LED component on Airgoo Channel B6. OpenRGB exposes it as a hub zone rather than a separate controller, so it must not be grouped with either ENE-DRAM module. This fixed reference mapping is not a general claim about other Airgoo installations.

A stable removal of one or two devices from an expected inventory of at least four may update the saved expected count after 2.5 seconds. Large inventory drops remain protected by the stricter cold-start retry logic and must not be accepted as a permanent hardware change automatically.

## Mainboard/chassis fans

The current backend targets Linux hwmon fan control with a focus on NCT6687/NCT6687D. Electrical channel mapping must be calibrated and physically confirmed. Board name alone is diagnostic metadata, not a safe mapping source. Individual/global presets modify only the stored bounded curves and preserve activation/calibration state; electrical DC/PWM switching is permitted only through a driver-exposed fixed channel node and always resets confirmation state.

## Explicitly outside current support claims

- GPU fan control through the mainboard fan subsystem.
- Firmware flashing/updating/version switching.
- General voltage/clock tuning.
- Unverified direct Corsair USB writes.
- Open Radeon Control Center integration into this repository.

When adding support, record: device identity, read-only detection evidence, write path, safety/ownership model, real hardware test status, and regression tests.
