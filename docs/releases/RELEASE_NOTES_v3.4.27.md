# Open Hardware Control 3.4.27 INTERN

3.4.27 is an internal Fedora test build and the first step of the next interface and cooling-control pass.

## CoolerControl service management

- OHC distinguishes the closed CoolerControl graphical client from the active `coolercontrold` system service.
- The Cooling ownership panel reports both the current daemon state and whether CoolerControl starts automatically with the system.
- The existing temporary takeover remains available without changing autostart.
- New explicitly confirmed Polkit actions can disable and stop CoolerControl persistently or enable and start it again.

## Consistent interface design

- RGB Studio, LCD, Profiles, Log, Corsair/OpenLinkHub, Settings, About and Help now use the same blue-tinted cards, editors, tables and input surfaces as the modern Overview and Cooling dashboards.
- Kraken detail sections use the same visual language while retaining distinct warning and safety colours.

## Kraken quick profiles

- Leise, Ausbalanciert and Leistung start neutral and only become fully blue after both pump and radiator-fan writes succeed.
- A manual value, CPU curve or general saved profile clears the quick-profile highlight instead of leaving a stale selection visible.
- A confirmed quick-profile state is reconstructed from the stored pump and fan mode details after restart.

## Chassis-fan curve cards

- Detected chassis-fan cards remain compact and collapsed instead of opening the first channel automatically.
- Every card provides a clear curve/details action; opening another card closes the previous one.
- Closing the embedded editor also collapses its associated card without changing fan-control ownership or saved curves.

## Local AI project handoff

- `docs/ai/START_HIER_LOKALE_KI.md` gives local coding models a short mandatory project and safety entry point.
- `docs/ai/LM_STUDIO_ANLEITUNG_DE.md` documents the recommended LM Studio Bionic setup for Qwen2.5-Coder-14B, context-memory tradeoffs and repository selection.
- `docs/ai/LOCAL_AI_STARTPROMPT.txt` provides a reusable first prompt, while the GitHub guide separates internal branch pushes from blocked public releases and never stores credentials.
- A credential-free Git bundle transfers the current branch and required history to another local-AI workspace without embedding `.git` account configuration in the source ZIP.
- `docs/project/MODULE_MAP.md` routes context-limited models to the smallest relevant file set for UI, Kraken, mainboard-fan, RGB, OpenLinkHub and release tasks.
- The first compatibility-preserving refactor moves constants, temperature helpers, privacy logging, the serial command backend, cooling widgets and localization/help data out of the historical main file without changing hardware ownership behavior.

## Safety

- Disabling CoolerControl never starts OHC mainboard-fan control automatically.
- Before enabling CoolerControl, OHC stops its own mainboard regulation and restores firmware/BIOS ownership.
- The services remain mutually exclusive so OHC does not write competing PWM values.

This package remains on the `INTERN` channel for local Fedora/Nobara testing. It is not a public stable release.
