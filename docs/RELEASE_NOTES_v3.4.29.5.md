# Open Hardware Control 3.4.29.5 INTERN

This Thermalright display compatibility hotfix addresses the render failure reported after installing 3.4.29.4.

- The attached log identifies an external TRCC Linux 9.9.11 renderer error: its decorative split overlay calls `QImage.mirrored()` with keyword arguments that PySide6 6.11 does not accept.
- OHC now sends `display split-mode 87ad:70db 0` as the first apply command, before loading an image, video or layout. A bad mode persisted by an earlier run therefore cannot crash the media load first.
- Decorative styles A–C remain usable in the local editor preview but are labelled as preview-only. New settings default to off.
- The physical right-hand 80-pixel Levita cutout remains a protected OHC placement boundary and does not depend on the decorative backend split mode.
- Focused command-order, UI and complete offscreen startup regressions cover the fix.

This is an INTERNAL test build and is not published automatically.
