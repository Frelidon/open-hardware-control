# Open Hardware Control 3.4.29.155 INTERN

## Ubuntu startup profile

- A known legacy NZXT assistant preset no longer permanently blocks the
  explicitly selected PC/RGB/LCD startup profile when Ubuntu detects Levita,
  no NZXT is ready and cooling selection is auto or the exact Levita.
- The pending preset remains stored and is not executed as Thermalright PWM
  intent. Explicit user cooling curves retain their existing mapping,
  calibration, ownership and write guards.
- Real NZXT, unknown pending values, missing Levita and other distributions
  retain the previous behavior. The owner's private startup-profile selection
  is a separately authorized local change, not a universal shipped migration.

## Levita USB ownership

- Ubuntu distinguishes TRCC's explicit occupied-interface error from a
  daemon IPC fault, FPS failure and trailing udev setup suggestion.
- OHC stops its own apply/startup/ticker retries while preserving the saved
  design and immutable request. It does not automatically stop another
  application, reset the foreign daemon or create another USB writer.
- Close the other display owner and explicitly apply the design again;
  the same existing serialized command queue is used.
- The conflict status is translated in all four languages, including dynamic
  updates. Fedora's established recovery path remains unchanged.
- Successful LCD health callbacks use the canonical imported device key;
  a previously hidden NameError no longer interrupts status handling. Real
  Qt class-method regressions cover static and animated healthy replies on
  both distribution branches with actual module globals.

## Package-stage directory permissions

- DEB/RPM staging normalizes only its own real directories to 0755, including
  copied directories and the stage root, independently of the build umask.
- Helper ancestors are safe on fresh installations. Source files, symlink
  targets, stage parents and existing host paths are not chmod targets.
- Helper/policy contents and file permissions, RPM dependencies and runtime
  behavior remain unchanged; a real isolated stage regression uses umask 002.

## Preservation and verification

- `.154` detailed OpenRGB inventory, external GPU routing, profile topology,
  designs, module switches and narrowly scoped authorization remain intact.
- Fedora and Ubuntu are equal supported targets with separate guards,
  correct native commands and targeted regression requirements. Existing
  features, design templates and settings must be retained on both paths.
- Source/fixture checks do not prove physical RGB/LCD output. Real Fedora
  hardware testing is pending in this Ubuntu follow-up; it is not inferred
  from simulated Fedora regression coverage or an Ubuntu run.
- The initial `.155` Ubuntu installation was verified: all 364 installed
  Python sources match, existing helper ancestors remain 0755 and the
  narrowly scoped DMI read works without another authorization prompt.
- The installed startup profile reports five RGB devices, both RAM modules
  with eight LEDs and JARGB 1 with 30 LEDs. The connected LCD daemon reports
  theme playback and 452 advancing frames at 15 FPS; these checks do not
  claim visual inspection of the physical LEDs or display.
- Final release-gate, rebuilt archive/permission and rolling-backup checks
  after the package-stage normalization remain pending.
