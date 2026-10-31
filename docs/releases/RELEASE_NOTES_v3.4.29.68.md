# Open Hardware Control 3.4.29.68 INTERN

Internal Linux test build. No GitHub release or tag is created.

## Visible Cooling navigation

- Cooling now expands in the main sidebar exactly like LCD.
- `Control & profiles` opens the existing water-cooling and case-fan controls.
- `Temperature recording` opens the detailed interactive multi-sensor recorder introduced in 3.4.29.67.
- Changing the internal Cooling tab keeps the matching sidebar child selected, and selecting either child opens the corresponding view.
- Navigation reset, customization, dynamic translation and hardware visibility preserve both fixed children.

## Safety and compatibility

- Temperature sampling remains read-only and non-owning.
- No cooling curve, PWM value, calibration, CoolerControl ownership check or hardware command changed.
- The supplied log was produced by installed 3.4.29.67 and confirmed that the missing entry was a navigation/UI discoverability problem rather than a sensor or hardware failure.
