# Open Hardware Control 3.4.29 INTERN

## Thermalright Levita Vision

- New local display studio on the LCD page with a 1600×720 canvas and the verified protected right-side 80-pixel cutout.
- Local import of images, videos, `.zt` media and TRCC layout directories. Imported manufacturer files stay at their selected local path and are not shipped by OHC.
- Movable CPU temperature/load, GPU temperature/load, RAM and clock overlays.
- Test mode is enabled by default and performs no USB writes. Real display communication requires the separately installed GPL TRCC Linux backend.
- Exact cooling identity for **Thermalright Levita Vision 360 ARGB Black**.
- Pump and radiator fans are mapped separately to motherboard PWM headers, each requiring the safe physical 70-percent/10-second confirmation before writes are allowed.
- Conservative Silent, Balanced, Performance and Safety values plus CPU-temperature software curves after confirmation.
- Active CoolerControl blocks OHC PWM writes. OHC returns channels it owned to firmware/BIOS control on orderly exit.
- The current device path exposes no coolant sensor; OHC reports this honestly and does not derive a fake water temperature.

## ENE-DRAM cold-start reliability

- The saved RGB profile now runs two ordered OpenRGB Direct reclaim passes across all selected ENE-DRAM modules before starting the persistent animation worker.
- This handles the observed case where OpenRGB reports the first transition as successful while the physical LED controller still remains asleep.
- The UI and logs describe the two passes; the manual reinitialize action uses the same strengthened sequence.

## Verification status

- Focused Thermalright display, UI, cooling, mainboard and ENE tests pass.
- The full non-environmental suite and isolated local OpenRGB protocol suite pass.
- Real display writes still require a locally installed `trcc` backend and user hardware confirmation. PWM writes remain calibration-gated for the same reason.
- This remains an INTERNAL build and is not published automatically.
