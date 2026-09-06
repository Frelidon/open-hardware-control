# Open Hardware Control 3.4.28 INTERN

3.4.28 is an internal Fedora/Nobara test build focused on clearer chassis-fan interaction, local-AI maintainability and reliable local packaging.

## Chassis-fan cards

- Detected chassis-fan cards start collapsed instead of opening the first internally selected PWM channel.
- Every card has a clear curve/details action, and only one explicitly selected card can be expanded.
- Closing the embedded editor collapses the associated card without changing saved curves or hardware ownership.
- Dynamically rebuilt curve buttons immediately use the currently selected interface language.

## Local AI structure

- The historical main file remains the compatible executable orchestrator.
- Constants, temperature helpers, privacy logging, command execution, cooling widgets, translations/help and chassis-card state live in focused modules.
- `../project/MODULE_MAP.md` directs context-limited models such as Qwen2.5-Coder-14B to the smallest relevant file set.

## Packaging reliability

- Fedora builds no longer abort merely because the optional Debian `dpkg-deb` tool is unavailable.
- ZIP, source archive, local-AI Git bundle and RPM continue to build and receive SHA-256 checksums.
- Tar entry timestamps are normalized to avoid inherited invalid directory dates in RPM builds.

This package remains on the `INTERN` channel for local testing and is not a public stable release.
