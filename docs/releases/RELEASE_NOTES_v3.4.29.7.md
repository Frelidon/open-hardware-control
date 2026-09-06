# Open Hardware Control 3.4.29.7 INTERN

This internal hotfix removes the remaining startup window flash and makes the optional motherboard-fan authorization persistent only when the user explicitly requests it.

- A minimized KDE/Wayland tray autostart now suppresses the OHC native window surface before the full PySide6 UI is constructed. The photographed black, unpainted OHC window can therefore no longer be mapped during startup; opening OHC from the tray explicitly enables the surface.
- Every invocation of the Qt-based OpenRGB executable, including short-lived inventory, native-mode and ENE-DRAM reclaim clients, uses the offscreen platform. The private loopback server and foreign-process ownership protections remain unchanged.
- Cooling → System Fans adds separate **Grant persistent authorization** and **Remove persistent authorization** controls for the fixed NCT6687 helper.
- Granting requires one final Polkit administrator confirmation and creates one exact-user rule that survives reboots. No password is stored. Removal deletes that exact generated rule; an already authenticated helper child still ends normally with the current OHC process.
- The privileged helper still accepts no arbitrary command or filesystem path. PWM channels remain bounded to 1–8, watchdog and percentages remain validated, CoolerControl ownership remains exclusive, and every physical fan mapping still requires the existing 70-percent/10-second confirmation.
- Regression coverage constructs the full UI in autostart mode, verifies that the native surface stays suppressed until an explicit open, validates fixed grant/revoke commands and generated Polkit rule contents, and checks the headless OpenRGB command classification.

This is an INTERNAL test build and is not published automatically.
