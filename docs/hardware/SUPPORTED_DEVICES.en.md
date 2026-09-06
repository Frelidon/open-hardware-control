# Supported devices – Open Hardware Control 3.4.29.47

## NZXT module

| Device | USB ID | Backend | Scope |
|---|---|---|---|
| NZXT Kraken 2023 | `1e71:300e` | liquidctl | liquid, pump, radiator fans, LCD |
| NZXT 2023 RGB Controller | `1e71:2012` | liquidctl | three RGB channels |

The reference device remains the NZXT Kraken RGB 360 (2023, Standard / Non-Elite) with firmware 2.0.0.

## Corsair through OpenLinkHub

Open Hardware Control displays devices reported by the locally installed OpenLinkHub service through `/api/devices/`; it does not maintain a separate fixed Corsair USB list. Validated controls added in version 3.0.4 remain available for reported cooling, RGB/LCD, mouse, keyboard and headset devices. Complex device-specific settings remain in the local dashboard.

Version 3.0.9 maps reported mice to original generic GPL SVG schematics. A physical button can be edited only when OpenLinkHub reports an unambiguous button index. None, media, DPI, keyboard, sniper-DPI, mouse and existing macro assignments are supported. The recorder creates bounded keyboard/delay macros only while its dialog has focus; complex sequences remain in the OpenLinkHub dashboard.

Real-hardware validation with OpenLinkHub 0.9.0 and the connected Corsair devices is still required. Firmware updates, general motherboard tuning, Open Radeon Control Center and untested direct Corsair USB writes are out of scope. Calibrated motherboard/case fan PWM control through compatible Linux hwmon is included starting with 3.4.23.

## Additional RGB devices through OpenRGB

Version 3.4.23 intentionally carries no copied OpenRGB USB device list. OHC starts the installed backend as a private windowless child process and displays only its reported devices, zones, LEDs and modes. Direct-capable devices use OHC's bounded local SDK writer for colors and software frames, bypassing the crash-prone CLI `ApplyOptions` path; SDK revisions 4 and 5 are negotiated compatibly. Each write sends a complete device frame, while the first Direct initialization also sends a complete per-zone fallback. Animations keep one SDK connection open and submit all selected Direct devices as one bounded 25 Hz target frame. Non-Direct devices receive only a matching reported native mode. ENE DRAM aliases and a fully mirrored inventory are de-duplicated without collapsing real modules. Equal real GPU/controller names stay distinct and can be renamed and mapped to the editable twelve-fan Thermaltake view. NZXT channels are exposed as groupable tiles, while the duplicate OpenRGB NZXT view is hidden. Remote SDK servers are not supported; the endpoint is fixed to `127.0.0.1:6742`.

An ARGB controller may report zones without being able to electrically detect the number of attached LEDs. The 3.4.9 zone setup keeps existing values, may suggest a known fan count from the PC layout, and lets the user enter fans and LEDs per fan. Version 3.4.10 adds 24-LED profiles for normal and reverse TZMRIT/Jungle Leopard Interstellar V2 fans and flags implausible totals. Server-side readback is deliberately not presented as physical light-output confirmation.

Direct devices no longer enter the confirmed `ApplyOptions`/`stl_vector` CLI path. The per-device quarantine remains as a fallback for native non-Direct CLI modes and does not mean that the physical hardware itself is defective.

## Motherboard/case fans through Linux hwmon

Version 3.4.23 can control PWM channels exposed by Linux through `/sys/class/hwmon`, initially focused on NCT6687/NCT6687D and MSI X870-family systems. Board names are diagnostic hints only; OHC never derives a fixed physical fan mapping from them.

- Every PWM channel must pass a guided 70%-for-5-seconds physical calibration before automatic control is allowed.
- Only calibrated, explicitly enabled and writable channels are touched by the one-second control loop.
- Sensor sources: CPU, GPU, Kraken liquid, maximum, or weighted CPU/GPU temperature.
- Each channel has its own curve, minimum duty, hysteresis and response delay.
- After three consecutive missing sensor readings OHC requests a 70% runtime fallback; at 90 °C it requests 100%.
- Disabling OHC control or exiting cleanly returns channels to firmware/BIOS control through `pwmN_enable` where the driver exposes that state as writable. If nct6687d exposes `fan_control_watchdog`, OHC refreshes it as an additional 10-second crash-safety lease while control is active.
- If the sysfs PWM files are not writable by the current user, OHC does not attempt a write. Driver/Secure Boot diagnostics and setup guidance are shown instead; Secure Boot/MOK is never bypassed.
- GPU fan control is not part of this module.

Actual electrical mapping and write access depend on the installed kernel/NCT6687 driver and board firmware, so physical calibration remains mandatory even for a known board model.
