# Open Hardware Control 3.4.29.69 INTERN

Internal Linux test build. No GitHub release or tag is created.

## LCD navigation

- Both LCD child pages now show browser-like `Display & layout` and `Display effects` tabs in addition to the expandable sidebar.
- Clicking either tab opens the matching main page; both tab bars and the sidebar remain synchronized.
- Section Tabs 1.0 provides the same reusable, stable page-ID pattern for future multi-page sections.

## Active Display Effects selection

- Display Effects 1.7 matches the Levita Studio's active bundled video by its exact validated path.
- Effect type, category, main design and colour variant are selected together instead of defaulting visually to Smoke.
- A programmatic sync blocks user-selection callbacks and therefore does not restage a profile or invoke hardware.
- The original OHC Light Ribbons design adds a warm travelling wave over light rods in eight horizontal, vertical and diagonal directions.
- All eight 1600×720 loops are rendered reproducibly from OHC code; the reference recording, cooler shape and product logo are not packaged.

## Safety and compatibility

- The existing Levita Studio remains the sole route to the TRCC hardware writer.
- No cooling, PWM, USB protocol, device-support or ownership boundary changed.
- All visible additions are covered in German, English, Spanish and French.
