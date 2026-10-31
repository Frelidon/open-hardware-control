# Open Hardware Control 3.4.29.121 INTERN

Internal development build, 22 September 2026.

## RGB stability and motion

- Fix the native crash identified in `HeaderPreview.restore` by removing the
  delayed Qt callback after LED editor teardown.
- Preserve physical fan-bank dimensions such as 3 × 30 LEDs instead of
  flattening them to one 90-LED device.
- Add a per-component forward/reverse animation control and animate configured
  case fans in the live case view.
- Use one bounded visual clock for configured and local paths. Slow controller
  batches no longer create large visible phase jumps.
- Keep render execution outside the GUI process and contain invalid render
  plans per device inside the SDK worker.

## GPU controls

- Separate the LACT fan response test from permanent Open Hardware Control
  takeover with two numbered actions on the fan page.
- Add a project-owned graphics-card/fan navigation icon. Existing live RPM,
  editable curve, Zero-RPM preservation and rollback safeguards remain active.

## Verification

- Focused RGB, topology, SDK isolation, GPU fan and profile tests pass. The
  complete release gate is run before packaging.
