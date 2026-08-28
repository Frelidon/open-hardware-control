# Open Hardware Control 3.4.27 INTERN

3.4.27 is an internal Fedora test build and the first step of the next interface and cooling-control pass.

## CoolerControl service management

- OHC distinguishes the closed CoolerControl graphical client from the active `coolercontrold` system service.
- The Cooling ownership panel reports both the current daemon state and whether CoolerControl starts automatically with the system.
- The existing temporary takeover remains available without changing autostart.
- New explicitly confirmed Polkit actions can disable and stop CoolerControl persistently or enable and start it again.

## Safety

- Disabling CoolerControl never starts OHC mainboard-fan control automatically.
- Before enabling CoolerControl, OHC stops its own mainboard regulation and restores firmware/BIOS ownership.
- The services remain mutually exclusive so OHC does not write competing PWM values.

This package remains on the `INTERN` channel for local Fedora/Nobara testing. It is not a public stable release.
