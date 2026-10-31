# Open Hardware Control 3.4.29.63 INTERN

The action button on every calibrated motherboard/case-fan card now says what
clicking it will do. An inactive channel shows “Automatik einschalten” and an
active channel shows “Automatik ausschalten”; English, Spanish and French use
the corresponding explicit action labels.

This replaces the previous state captions “Automatik aus” and “Automatik
aktiv”. Those captions were technically accurate before a click, but could be
read as the action and caused confirmed PWM channels to be enabled
unintentionally. A full offscreen UI regression now toggles a simulated
calibrated channel in both directions and verifies the matching action text.

No curve point, calibration result, channel assignment, ownership rule,
watchdog, PWM value or hardware-write path changed. The supplied loud-fan event
remains consistent with a real short CPU rise to 73.1 °C and the configured
curve, not a 100-percent fallback or lost sensor.

Nebula Drift now places its large clock and the CPU, GPU and RAM values on four
subtle dark glass cards with restrained cyan/violet outlines. The untouched
source background remains in the theme for reproducible rendering. The four
project-owned generated layouts are also more visually distinct: Orbit uses
instrument rings, Aqua Pulse uses wave arcs, Horizon Glass uses a broad data
bar and Split Core keeps its angular two-sided panels. All generated previews
use a scalable Noto/DejaVu font instead of the previous tiny bitmap fallback.

Release backup handling also retains the release notes from their canonical
`docs/releases/` directory. No GitHub push, tag or public release was created.
