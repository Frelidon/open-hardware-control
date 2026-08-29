# Open Hardware Control 3.4.29.4 INTERN

This startup hotfix addresses the crash found immediately after installing 3.4.29.3 with an existing Thermalright design directory saved in the user settings.

- Restoring the saved TRCC media directory may render the first preview synchronously while the LCD page is constructed. The display studio now keeps its callback logging muted during construction, so it no longer accesses the main `log_view` before the Log page exists.
- The real PySide6 full-window regression persists a valid local image before constructing all eleven pages. This reproduces the supplied startup condition and confirms the selected preview is restored successfully.
- TRCC Linux 9.9.11 is now present on the reference Fedora system. The physical red/green/blue/black test completed visibly on USB `87ad:70db`; the full handshake reported 1600×720, model ID 64 and sub-byte 3. Full OHC design/video/overlay endurance remains a separate in-app hardware test.

This is an INTERNAL test build and is not published automatically.
