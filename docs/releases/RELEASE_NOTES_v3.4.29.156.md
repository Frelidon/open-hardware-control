# Open Hardware Control 3.4.29.156 INTERN

## Case editor

- Fresh LED-path fields remain editable before any physical path was saved,
  including after Qt popup/polish and inline inspector reparenting.
- Actual user selection activates the draft's save flag. Merely opening,
  changing a count or test index, programmatic selection and Cancel do not
  create a path. Explicit unchecking still removes the path on Save.
- Line/ring-specific fields and declared-count validation remain enforced;
  Save/Cancel/Escape remain the explicit editor completion actions.
- Ordinary case refresh retains unfinished direction/speed choices. Changed
  saved profile direction is reflected in the editor. If there is no declared
  path, the four-language status explains the remaining setup step.

## Spatial RGB and animated fan view

- Spatial waves follow their selected visible direction rather than an
  accidentally inverted phase. Rainbow retains its required phase correction.
- A header's own nonlocal direction receives its case-space rectangle even
  when the overall direction is local. Explicit header-local choices and
  unmapped legacy frames remain intact.
- Effect reversal works independently of physical LED/fan numbering, including
  local mode. No controller, port, LED count or geometry is inferred.
- Fan light rings display bounded colour segments from the same confirmed
  effect clock; visible animation starts immediately and hidden timers stop.
- A single reported, configured header can show schematic fan colours without
  an exact physical ring path. Ambiguous routes remain unresolved. This is
  RGB animation, not a measured rotor/RPM simulation or physical LED readback.

## Preservation and verification

- Both Fedora and Ubuntu use the same pure/Qt corrections with separate
  fixture coverage. Their existing backend, package, authorization and
  ownership paths remain unchanged. No native GPU detector is enabled.
- Existing designs, modules, profiles, confirmed counts and physical routes
  remain available. There is no shipped private PC-profile migration.
- New regression suites cover real Qt mouse/keyboard input in all four
  languages, standalone/inline drafts, Save/Cancel, temporal wave frames,
  rendering-plan parity, fan preview images and visible/hidden timers.
- The full release gate passed 1,301 tests and five subtests, including the
  real four-language Qt build, privacy/security and module-budget checks.
- Actual DEB/RPM source contents, root-owned directory/helper permissions,
  RPM digests and unchanged Fedora dependencies passed independent review.
  Both retained `.155`/`.156` backup checksum sets and release checksums pass;
  the recognized older `.154` backup was normally rotated under the owner policy.
- After the owner's normal Ubuntu package confirmation, APT updated only OHC
  with zero network download. DPKG integrity and all 365 installed Python
  sources match. Saved profiles/settings stayed byte-identical before relaunch;
  the verified private backups and orderly old-owner cleanup remain intact.
- Normal startup automatically loads the five-device RGB design and both
  eight-LED DRAM reclaims. The OHC-owned LCD daemon holds the USB interface;
  repeated health replies show advancing video at 15 fps without a new exception.
- Narrow fan/metadata authorization and identifier-filtered RAM reading pass
  without another prompt. No general passwordless administrator rule or login
  autostart change is added. This is post-build installation evidence; package
  snapshots retain their pre-installation report.
  Real Fedora hardware and optical RGB confirmation remain pending separately.
