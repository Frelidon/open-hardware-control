# Open Hardware Control 3.4.29.8 INTERN

This internal hotfix completes the requested chassis-fan profiles and PWM/DC controls, fixes persistent authorization state on Fedora, and substantially improves the Thermalright Levita workflow.

- Every detected chassis-fan card now offers Leise, Ausbalanciert and Leistung presets, with the same three choices available globally above all chassis fans. The curve editor also has an explicit reset to the balanced standard.
- PWM/DC mode is shown and writable only if the Linux driver exposes that channel's fixed `pwmN_mode`. Changing it requires confirmation, stops active automation, clears the old calibration/activation and requires the physical safety test again.
- Persistent fan authorization now uses the exact-user Polkit rule plus a root-owned readable state marker. This avoids the false failure caused by Fedora's protected `/etc/polkit-1/rules.d` directory while keeping Polkit authoritative and storing no password.
- Levita images and ordinary videos are prepared as immutable-cache 1600×720 copies without aspect-ratio distortion. Users can choose complete contain or cropped cover behavior.
- The photographed default is now centered at X/Y 0 with an 80-pixel right mask and preview style C. The mask's left edge is directly draggable in the canvas and remains synchronized with its numeric width.
- CPU/GPU/RAM/time overlays retain individual dragging and gain a 20-step “restore last state” history. TRCC metric formats use the render path that keeps `%` and temperature glyphs visible on the physical display.
- Existing local A/B/C/D/E/Y TRCC files are presented in descriptive categories. OHC does not fetch, copy into the release, or redistribute manufacturer media.
- Detected display hardware is prioritized on the LCD page. The round Kraken preview is hidden for a rectangular Thermalright-only system, and the NZXT-ESC importer stays compact until opened when no Kraken is present.
- The full PySide6 construction regression now disables hardware I/O explicitly. An unexpected managed OpenRGB crash blocks automatic restarts for the rest of the session, preventing repeated coredumps until the user deliberately retries.
- A known irrelevant NVIDIA/NVML warning is no longer presented as a hard Thermalright error when it is the only livestream shutdown diagnostic.

All previous calibration, CoolerControl ownership, watchdog, bounded-helper and firmware-return protections remain in force. This is an INTERNAL test build and is not published automatically.
