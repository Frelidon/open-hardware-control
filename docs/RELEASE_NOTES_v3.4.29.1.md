# Open Hardware Control 3.4.29.1 INTERN

This hotfix restores application startup after 3.4.29 failed while constructing the LCD page.

- Explicitly imports the localized GIF safety source text used by the LCD page.
- Explicitly imports the localized About summary source text used by the About page.
- Adds a real PySide6 offscreen regression that constructs all 11 main pages without starting hardware discovery or issuing hardware commands.
- Retains all Thermalright Levita display/cooling and strengthened two-pass ENE-DRAM startup features from 3.4.29.

This is an INTERNAL test build and is not published automatically.
