# Open Hardware Control 3.4.29.154 INTERN

## Ubuntu RGB inventory

- OpenRGB 1.0 separates the names-only `--list-devices` output from
  `--list-detailed`, which includes modes, headers and LEDs.
- OHC selects the detailed command only for its trusted Ubuntu 1.0 backend;
  older OpenRGB and Fedora retain their existing commands.
- Names-only responses without device types are rejected before changing the stable device inventory
  or persisted selections and routes. A zero-LED names-only result is not a
  valid replacement for a previously complete device description. Legitimate
  empty devices remain supported; omitted empty CLI lists are not guessed.

## External GPU lighting

- GPU setup can use a reported mainboard ARGB header without requiring a
  separate native OpenRGB GPU controller.
- The existing controller/header editor saves an explicit block route, which
  also identifies the GPU effect group and strip renderer.
- PC profiles retain physical routes and LED counts. Missing or conflicting
  controllers remain blocked rather than silently selecting another header.
- Existing native GPU detector exclusions, whole-device frame validation and
  hardware ownership protections remain intact.

## Privilege boundaries and preserved features

- A display daemon's generic administrator request is distinct from the
  persistent, narrow fan-helper authorization. No general passwordless root
  rule is introduced.
- OHC-owned Ubuntu TRCC children redirect only their exact memory-DMI query to
  a fixed argument-free root-owned helper. It has a dedicated active-session
  action, runs a bounded read-only system command and filters device identifiers.
- DEB and RPM explicitly install that policy with 0644 permissions rather than
  inheriting a writable checkout mode; runtime trust checks remain fail-closed.
- The standard-library RPM fallback includes the same fixed system helpers
  and policies as the normal RPM spec; actual payloads are regression-checked.
- Other automatic metadata probes remain unprivileged. Existing upstream TRCC
  files, global PATH and independently running TRCC programs are untouched.
- The official Ubuntu package already supplies USB access; its startup hint
  incorrectly checks only one udev directory. OHC checks the standard directories
  and does not install duplicate rules merely to silence that hint.
- Existing designs, module switches, profile topology, Ubuntu background GPU
  reads and Qt lifetime guards remain present.
- Settings changes and offscreen regressions do not prove optical RGB output;
  the physical result must still be checked on the owner's connected hardware.

## Upstream reference

The CLI distinction is documented in the official
[OpenRGB 1.0 source](https://gitlab.com/CalcProgrammer1/OpenRGB/-/blob/release_1.0/cli.cpp).
