# Open Hardware Control 3.4.29.122 INTERN

Internal development build, 22 September 2026.

## Independent LED paths

- Store the case-space travel direction per controller zone instead of in one
  global setting. Each horizontal or vertical fan group keeps its own value.
- Apply the same separation to GPU and GPU-support routes, even when both are
  zones on the same physical controller.
- Preserve the former global setting only as a migration fallback. The next
  save upgrades the selected path without touching another component.

## Preview stability

- Validate ring geometry before a native Qt painter is created.
- End the painter deterministically after every valid frame. Switching
  clockwise direction or fan order cannot paint a transitional combo-box
  value into a dialog that is being closed.

## Verification

- Dedicated persistence, GPU-strip, ARGB routing and repeated live-preview
  selector tests pass. The complete release gate is run before packaging.
