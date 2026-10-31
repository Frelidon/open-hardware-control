# Open Hardware Control 3.4.29.124 INTERN

Internal development build, 22 September 2026.

## Fan layout and diagnostics

- The physical fan count no longer forces the LED layout to rings. New paths
  default to a row; an explicitly saved row or ring is retained.
- Ring mode keeps the declared fan segmentation and addresses each ring using
  the known LEDs-per-fan count, LED-1 position, rotation and fan order.
- The Log page now separates the complete event stream, RGB/fan activity and
  hardware anomalies. RGB path saves and effect starts list the concrete
  controller, zone, layout, totals and spatial direction.
- All views retain the existing bounded 60-minute policy and replay matching
  RGB/fan entries from recovered crash context.

## Verification

- LED topology, localization, logging and crash-context regression tests pass.
- The complete release gate is run before packaging.
