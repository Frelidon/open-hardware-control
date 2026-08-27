# Open Hardware Control 3.4.23 INTERN

3.4.23 is the first internal build that adds safety-gated motherboard/case fan control to the shared Open Hardware Control application. It also turns the proven ENE-DRAM cold-start workaround into a visible RGB Studio status and manual recovery action.

## Mainboard fan control

- Detects board identity through Linux DMI for diagnostics and discovers fan-capable controllers through `/sys/class/hwmon`.
- Initial focus: NCT6687/NCT6687D and MSI X870-family systems. Board identity never creates an automatic physical PWM mapping.
- Every channel must pass a guided 70%-for-5-seconds calibration and explicit physical confirmation before automatic control can be enabled.
- Per-channel label, sensor source, CPU/GPU weighting, minimum duty, hysteresis, response delay and five-point fan curve.
- Built-in Quiet, Balanced and Performance presets. OHC can recommend a preset from detected board/channel context, but the recommendation only fills the editor and never authorizes a PWM write.
- Sensor sources: CPU, GPU, Kraken liquid, maximum of available sensors, or weighted CPU/GPU.
- Three consecutive missing sensor samples request a 70% fallback. A 90 °C emergency condition requests 100%.
- Disabling automatic control or exiting cleanly returns enabled channels to firmware/BIOS control where the hwmon driver exposes a writable automatic mode. If nct6687d exposes `fan_control_watchdog`, OHC refreshes a 10-second lease so the driver can restore original curves if the controlling process vanishes.
- Driver/Secure Boot diagnostics and Fedora NCT6687 setup guidance are included. OHC does not bypass Secure Boot/MOK and does not use raw I/O or private SMBus register writes.
- If a PWM sysfs node is not writable by the current user, the first implementation remains read-only for that channel rather than silently escalating privileges.

## ENE-DRAM

- RGB Studio shows a dedicated information/status card only when ENE DRAM is detected.
- The status explains that a complete power loss can require an additional OpenRGB driver initialization and that RGB profile startup may therefore take a few seconds longer.
- “ENE-RAM erneut initialisieren” reruns the known working OpenRGB Direct reclaim for every detected ENE DRAM module and then reapplies the current OHC effect.
- The normal cold-start path remains one reclaim per OpenRGB/hardware session; effect changes do not repeatedly hammer the mode register.

## Safety and compatibility

- Existing Kraken USB coordination, CPU curves, LCD streaming, shutdown fallback, OpenRGB RGB coordination and OpenLinkHub integration remain intact.
- Mainboard PWM discovery is write-free. Automatic fan writes require `writable + calibrated + enabled` for each channel.
- No GPU fan control, firmware update, voltage/clock tuning or unverified raw controller access is added in this release.

This is an internal test build. Real mainboard PWM behavior still needs validation on the target system before any public release.
