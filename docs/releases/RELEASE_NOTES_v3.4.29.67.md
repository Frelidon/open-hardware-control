# Open Hardware Control 3.4.29.67 INTERN

Internal Linux test build. No GitHub release or tag is created.

## Cooling and temperature recording

- Keeps the compact CPU/GPU/coolant history on Overview.
- Adds `Cooling → Temperature recording` with an interactive multi-sensor chart, group and series selection, 5/15/60-minute, 6-hour and complete-session windows.
- Shows current, minimum and maximum readings with their actual Linux-hwmon source.
- Discovers plausible CPU, GPU edge/hotspot/VRAM, DDR5 SPD, NVMe/SSD, motherboard, VRM, PCH and other temperature inputs read-only.
- Stores at most 24 hours / 28,800 samples in memory and writes no telemetry/history file.

## Liquid-cooling safety

- Adds model-aware, fail-closed cooling duty policy 1.0.
- Thermalright publishes 3000 rpm ±10% maximum pump speed and 2000 rpm ±10% maximum TL-M12Q fan speed for Levita Vision 360 ARGB Black, but no minimum PWM duty.
- OHC therefore labels and enforces conservative internal floors of 50% pump and 25% radiator duty for every fixed value, quick profile, loaded profile, software curve and final hwmon write.
- Existing NZXT validated command ranges remain 20% pump and 0% radiator minimum.

## Profiles

- Fixes profile-table columns collapsing to content width after a refresh/update.
- Preserves the selected row while rebuilding the model.
- Adds an expandable tree showing every stored profile section and setting.
- Custom profiles can now include any combination of cooling, LCD/Levita display, RGB and design/display state.

## Compatibility and verification

- Multi-sensor recording is read-only and does not claim ownership of GPU, CPU, NVMe, RAM or motherboard controls, so it can coexist with Open Radeon Control Center and other monitoring applications.
- Visible additions are translated in German, English, Spanish and French.
- Alternate hardware is simulated by tests; only locally exposed read-only sensors were inspected on the development machine.
