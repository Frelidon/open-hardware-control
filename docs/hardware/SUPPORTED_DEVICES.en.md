# Supported devices – Open Hardware Control 3.4.29.129

Version 3.4.29.129 does not change hardware support. It only corrects the
ownership transfer and cleanup of an OHC-restarted TRCC daemon.

## Generic Hardware Checker

Version 3.4.29.96 reads Linux-reported CPU, SMT, CPU virtualization, board,
PCIe GPU, NVMe and RAM state. Current and maximum PCIe generation/lane values
come from the kernel and are diagnostic evidence, not a broader compatibility
claim. Idle GPU downshifts stay warnings until an explicit short glmark2 or
Vulkan vkcube test;
NVMe inspection performs no write benchmark. Optional DMI memory details use a
fixed Polkit action, and OHC receives neither the password nor serial numbers.
The local reference result does not approve other systems or components.

Development after .86 (not packaged): owner-confirmed personal Airgoo wiring
is front A1 2×8 / SYS_FAN4; bottom reverse intake B7 3×8 / SYS_FAN6;
rear normal exhaust B8 1×8 / SYS_FAN1; Thermalright radiator A8 3×10;
GPU support B6 1×12. The twelve-LED support declaration supersedes this
owner's earlier 24-LED reference below. RGB Studio 1.9 migrates only the
personal layout once and adds reusable custom manufacturer/model/color/LED
metadata. This is not general manufacturer verification or auto-detection;
source changes do not modify the installed .86 or PWM calibration.

As of 3.4.29.83 the owner visually verified 30 individually addressable LEDs on their Sapphire RX 9070 XT NITRO+ at MSI JARGB 1 (index 1 left, 30 right). Personal reference observation, not a general manufacturer count. Header/pixel testing now covers every reported Direct ARGB zone and protects manual counts from design profiles. Case shares RGB/LED/PWM assignments with cooling, optionally with separate positions. Count-adaptive smoothing is software-tested; optical fluidity remains to be tested.

GPU ARGB fix in 3.4.29.82: select the controller and individual header separately. The single-header editor saves one GPU as one device; a bounded pixel test assists visual mapping. GPU effects use independent zone coordinates, and current cabling/counts survive old design snapshots. Only the owner's confirmed personal Sapphire layout migrates once to MSI JARGB 1. Values 80/90 remain user test declarations, not confirmed physical LED counts. Optical validation is pending.

## NZXT module

| Device | USB ID | Backend | Scope |
|---|---|---|---|
| NZXT Kraken 2023 | `1e71:300e` | liquidctl | liquid, pump, radiator fans, LCD |
| NZXT 2023 RGB Controller | `1e71:2012` | liquidctl | three RGB channels |

The reference device remains the NZXT Kraken RGB 360 (2023, Standard / Non-Elite) with firmware 2.0.0.

## Thermalright Levita Vision 360 ARGB Black

The display uses USB `87ad:70db` through the separately installed GPL TRCC Linux backend; the reference handshake confirmed model ID 64/sub-byte 3 and 1600×720. Pump and radiator-fan control is technically separate through Linux hwmon and remains locked until each motherboard header passes its own physical confirmation.

Since 3.4.29.76 OHC protects long Levita video runs from the TRCC daemon memory growth confirmed on the reference system. A read-only one-minute guard considers only the exact current-user `trcc daemon` process and, at 1 GiB RSS or after a lost IPC connection, performs a controlled `trcc kill` followed by design restoration. The existing sole TRCC queue remains the only USB writer and a five-minute cooldown prevents recovery loops.

Since 3.4.29.67 Settings can resolve these implemented backends automatically or select them explicitly. An unavailable explicit choice never silently falls back to another writer. Native OHC Levita and CoolerControl control adapters are visible roadmap entries but remain disabled. The compact Overview history remains available; the dedicated Cooling recorder reads plausible CPU, GPU/hotspot/VRAM, RAM, SSD/NVMe, motherboard, VRM and PCH sources for at most 24 hours/28,800 volatile samples. Levita exposes no coolant value, so none is inferred.

Since 3.4.29.68 Cooling expands in the main navigation like LCD. `Control & profiles` opens the existing water-cooling and case-fan controls, while `Temperature recording` opens the detailed read-only history. This navigation-only change does not broaden device support.

Since 3.4.29.53 a real application exit, tray Quit, logout or handled shutdown releases Levita from the daemon with a bounded `trcc device disconnect 87ad:70db`. After roughly two to three seconds without new frames, the firmware returns to its built-in Thermalright screen. After a confirmed real write, a separate pipe-bound guard watches the OHC parent and repeats only this fixed fallback once after unexpected process loss; preview-only use never arms it.

Since 3.4.29.54 the project-owned Display Effects page can prepare a procedural smoke loop while retaining the selected layer-2 sensor layout. This does not expand the hardware claim and does not write independently: test mode, masks, queueing and the sole TRCC USB owner remain in the existing Levita studio.

Since 3.4.29.55 the window can paint before device initialisation and Levita card construction. CoolerControl inspection runs outside the GUI process and remains fail-closed until confirmed. Graphical sensor-layout cards and faster effect-cache handling do not change the USB protocol or device-support claim; the ten-second hardware cooldown remains.

Since 3.4.29.56 Display Effects includes five freely licensed, edited video designs in four colour variants. These local media only expand the visual choice; they do not change the USB protocol or device-support claim and are still applied through the sole Levita/TRCC write path.

Since 3.4.29.57 OHC restarts an unexpectedly ended daemon-side video ticker with bounded backoff. Recovery uses only the existing TRCC IPC connection and does not expand device support or USB ownership; three rapid persistent failures stop further attempts.

Since 3.4.29.59 bundled library videos are validated against their own fixed package root instead of the private cache boundary. This fixes their previously silent rejection on apply; symlinks, files outside either designated root and formats other than MP4 remain blocked. The hardware path and device-support claim are unchanged.

## Corsair through OpenLinkHub

Open Hardware Control displays devices reported by the locally installed OpenLinkHub service through `/api/devices/`; it does not maintain a separate fixed Corsair USB list. Validated controls added in version 3.0.4 remain available for reported cooling, RGB/LCD, mouse, keyboard and headset devices. Complex device-specific settings remain in the local dashboard.

Version 3.4.29.54 can check and, only after confirmation, update the existing OpenLinkHub package together with its bundled Web UI. This changes the backend version, not OHC's support claim for untested Corsair devices.

Version 3.0.9 maps reported mice to original generic GPL SVG schematics. A physical button can be edited only when OpenLinkHub reports an unambiguous button index. None, media, DPI, keyboard, sniper-DPI, mouse and existing macro assignments are supported. The recorder creates bounded keyboard/delay macros only while its dialog has focus; complex sequences remain in the OpenLinkHub dashboard.

Real-hardware validation with OpenLinkHub 0.9.0 and the connected Corsair devices is still required. Firmware updates, general motherboard tuning, Open Radeon Control Center and untested direct Corsair USB writes are out of scope. Calibrated motherboard/case fan PWM control through compatible Linux hwmon is included starting with 3.4.23.

## Additional RGB devices through OpenRGB

Version 3.4.23 intentionally carries no copied OpenRGB USB device list. OHC starts the installed backend as a private windowless child process and displays only its reported devices, zones, LEDs and modes. Direct-capable devices use OHC's bounded local SDK writer for colors and software frames, bypassing the crash-prone CLI `ApplyOptions` path; SDK revisions 4 and 5 are negotiated compatibly. Each write sends a complete device frame, while the first Direct initialization also sends a complete per-zone fallback. Animations keep one SDK connection open and submit all selected Direct devices as one bounded 25 Hz target frame. Non-Direct devices receive only a matching reported native mode. ENE DRAM aliases and a fully mirrored inventory are de-duplicated without collapsing real modules. Equal real GPU/controller names stay distinct and can be renamed and mapped to the editable twelve-fan Thermaltake view. NZXT channels are exposed as groupable tiles, while the duplicate OpenRGB NZXT view is hidden. Remote SDK servers are not supported; the endpoint is fixed to `127.0.0.1:6742`.

An ARGB controller may report zones without being able to electrically detect the number of attached LEDs. The 3.4.9 zone setup keeps existing values, may suggest a known fan count from the PC layout, and lets the user enter fans and LEDs per fan. Version 3.4.10 adds 24-LED profiles for normal and reverse TZMRIT/Jungle Leopard Interstellar V2 fans and flags implausible totals. Server-side readback is deliberately not presented as physical light-output confirmation.

Direct devices no longer enter the confirmed `ApplyOptions`/`stl_vector` CLI path. The per-device quarantine remains as a fallback for native non-Direct CLI modes and does not mean that the physical hardware itself is defective.

## Motherboard/case fans through Linux hwmon

Version 3.4.23 can control PWM channels exposed by Linux through `/sys/class/hwmon`, initially focused on NCT6687/NCT6687D and MSI X870-family systems. Board names are diagnostic hints only; OHC never derives a fixed physical fan mapping from them.

- Every PWM channel must pass a guided 70%-for-10-seconds physical calibration before automatic control is allowed.
- Only calibrated, explicitly enabled and writable channels are touched by the one-second control loop.
- Sensor sources: CPU, GPU, Kraken liquid, maximum, or weighted CPU/GPU temperature.
- Each channel has its own curve, minimum duty, hysteresis and response delay.
- Quiet and Balanced remain temperature curves. Performance is a constant 100% override and is reevaluated immediately while OHC control is active, without activating unconfirmed channels.
- Every case-fan card offers a confirmed 0%-for-10-seconds identification test and restores the previous hwmon/firmware state afterwards. Some fans cannot physically stop at 0%.
- Electrical PWM/DC switching is available only if the driver exposes `pwmN_mode`; changing it stops automation and requires calibration again. Without that node the BIOS owns the electrical mode while OHC adjusts only the documented `pwmN` duty/DC value.
- After three consecutive missing sensor readings OHC requests a 70% runtime fallback; at 90 °C it requests 100%.
- Disabling OHC control or exiting cleanly returns channels to firmware/BIOS control through `pwmN_enable` where the driver exposes that state as writable. If nct6687d exposes `fan_control_watchdog`, OHC refreshes it as an additional 10-second crash-safety lease while control is active.
- If the sysfs PWM files are not writable by the current user, OHC does not attempt a write. The assistant inspects distribution, mainboard, Secure Boot, the DKMS certificate, MOK enrollment, module signature and load state read-only. Since 3.4.29.150 it copies separate fixed dependency commands for Ubuntu, Fedora and Arch Linux; cloning and DKMS installation then follow the [official nct6687d instructions](https://github.com/Fred78290/nct6687d). Since 3.4.29.151 Ubuntu refresh and installation are separate, an existing fixed checkout is updated only by fast-forward, and the optional restricted persistent fan authorization is wizard step five. Third-party package sources are never changed automatically. The MSI X870 option is added only for a matching detected MSI X870 mainboard. On Arch, `linux-headers` targets the default kernel; other kernels require their matching header package. Confirmed buttons open only fixed key-generation, `mokutil --import /var/lib/dkms/mok.pub`, or `modprobe nct6687` commands in a visible terminal; the password and physical MOK Manager confirmation stay entirely outside OHC. Secure Boot is never bypassed.
- Since 3.4.29.152 the PC profile manager stores CPU_FAN, PUMP_FAN, and SYS_FAN together as settings-only topology. Assigning or loading does not calibrate, enable, or write a channel. On the detected MSI MAG X870 TOMAHAWK WIFI, the owner-confirmed reference wiring is added once by unambiguous driver-reported connector labels; existing user entries take priority.
- GPU fan control is not part of this module.

Actual electrical mapping and write access depend on the installed kernel/NCT6687 driver and board firmware, so physical calibration remains mandatory even for a known board model.
