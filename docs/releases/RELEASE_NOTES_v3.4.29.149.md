# Open Hardware Control 3.4.29.149 INTERN

## Hardware Fix

- Hardware Checker now has a **Hardware Fix** sub-page. The first profile is
  explicitly limited to **MSI MAG 274QPF X30MV – VRR** over DisplayPort.
- The profile verifies the exact monitor model, fixed local resources, current
  boot state, corrected EDID state, and the one canonical Ubuntu user service.
  Mutating jobs are serialized and require an explicit terminal confirmation;
  OHC never receives the sudo password and never restarts automatically.
- The bundled EDID has its monitor serial descriptor removed. Matching uses the
  model identity and valid EDID structure, not a personal serial number. No
  personal names, private paths, or test-game history are shipped.
- Ubuntu can install/adopt the existing `msi-vrr-games.service`, configure GNOME
  VRR, measure real DRM VRR state in a game, disable the automation separately,
  and perform a conservative profile-scoped removal. The existing Fedora path
  remains separate and never receives the Ubuntu AppIndicators automation.

## RGB and display libraries

- RGB Studio prominently shows startup profile, automatic startup, resume, and
  ownership consent; confirmed takeover can enable the safe defaults.
- LCD media sources can include multiple folders and individual files while
  built-in designs remain available.
- OpenRGB profile files can be imported into a private library and loaded as a
  whole profile. Legacy binary `.orp` files are deliberately not advertised as
  safely filterable per controller.
- The local OpenLinkHub integration can import static 640×48 iCUE NEXUS designs
  and validated button manifests without exposing full device serials.

## Version scope

This is source/release version **3.4.29.149 INTERN**. Installing it is a separate
user action; generating the release does not alter the running Fedora setup.

## Ubuntu package update

- The DEB accepts both the older `policykit-1` package and the current split
  `polkitd` plus `pkexec` packages. This fixes upgrades on Ubuntu 26.10 where
  `policykit-1` has no installation candidate. RPM dependencies and Fedora
  runtime behavior are unchanged.
- Quit a running OHC instance through **right-click tray icon → Beenden** before
  installing the update. The window X intentionally keeps OHC running in the
  notification area.
