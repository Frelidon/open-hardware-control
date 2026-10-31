# Open Hardware Control 3.4.29.125 INTERN

Internal development build, 25 September 2026.

## Diagnostics and reliability

- Accept exact 0 MHz AMD GPU clock samples as a normal power-gated idle state;
  negative or over-limit readings remain hardware anomalies.
- Coalesce identical Qt helper-process start messages for five minutes and
  summarize automatic mainboard-fan curve writes as bounded batch events.

## Case, RGB and LED topology

- Modernize the Case device table around detected capabilities. Impossible
  LED or PWM fields are hidden for display and pump-only blocks, and a new
  read-only analysis summarizes devices, PWM mappings, ARGB routes and paths.
- Preserve ring segmentation so every fan and physical LED remains individually
  addressable from LED-1 position, rotation, fan order and case direction.
- Replace the redundant large RGB live preview with larger animated design
  cards. Add six Spatial presets driven by 3D Fusion, 3D Crossflow and 3D Depth
  Wave across explicitly saved case LED paths.

## GPU fan control

- Keep a static 100% fan request exact through the LACT scale conversion.
- Add a default-off option to store a passed fan-only test permanently in LACT.
  Failed tests never save, and mixed clock or power drafts still require the
  existing separate confirmation path.

## Verification and scope

- All four localization catalogs contain 1,736 shared messages.
- 821 automated tests pass, including the two local-socket suites; the Case and
  RGB pages were additionally rendered offscreen for visual inspection.
- Development and verification performed no hardware writes. Physical fan,
  GPU, RGB and case-light validation on the target machine remains the final
  user smoke test; this build adds no new device or wire-protocol claim.
