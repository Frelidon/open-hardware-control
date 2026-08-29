# Open Hardware Control 3.4.29.2 INTERN

This hotfix addresses the startup, cooling-state and RGB-layout issues found during real-hardware testing of 3.4.29.1.

- The desktop-shell `--quit` path now uses `QCoreApplication` and never initializes the graphical Qt platform plugin. This prevents the supplied logout coredump and the empty KDE helper window.
- Startup profiles no longer issue Kraken LCD commands when Thermalright Levita cooling is selected, avoiding an obsolete-device error dialog.
- After a CPU-temperature curve is successfully applied, the manual pump/fan controls show the confirmed current curve target instead of retaining an old 100-percent manual value.
- The personal Thermaltake overview migrates its visible radiator and pump blocks from NZXT Kraken to Thermalright Levita Vision 360 while preserving stable saved layout identifiers.
- The Jungle Leopard GPU support is represented as its own 24-LED component. On the confirmed reference wiring, Airgoo Channel B6 is corrected from the old 30-LED value to 24 LEDs and remains separate from both ENE-DRAM devices.

This is an INTERNAL test build and is not published automatically.
