# Open Hardware Control 3.4.29.123 INTERN

Internal development build, 22 September 2026.

## Fan-bank handoff

- The LED-path editor now receives the physical fan count already declared in
  the case component.
- A saved LEDs-per-fan model supplies the total LED count automatically, for
  example 4 fans × 8 LEDs = 32 LEDs.
- Changes made in an open component dialog are forwarded before that dialog
  is saved.
- Compatible legacy line paths open as the corresponding ring bank, making
  clockwise direction and physical fan order available without duplicate
  entry.

## Verification

- Component editor, ARGB routing, topology persistence and profile tests pass.
  The complete release gate is run before packaging.
