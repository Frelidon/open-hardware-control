# Open Hardware Control 3.4.29.84 INTERN

- Select a case block and drag its lower-right corner to resize it. The block
  editor also offers a 25–200% preview-size control. Escape cancels the gesture;
  only releasing commits settings. Old profiles retain 100% and saved positions.
- Share visual scale between RGB/cooling or keep it independent with the
  existing synchronization option. Hardware LED counts, fan millimeters,
  device identity, calibration and PWM ownership never change on resize.
- Use proportional fan/component render and hit geometry, fitted within the
  case, with original 2.5-D projected case edges and component shadows.
  Explicit arrangement uses case-family mounting centers; Retro front mounts
  are below the drive fascia, reviewed against the official Thermaltake manual:
  https://file.thermaltake.com/file/qig/Retro360TG_Manual.pdf
  These remain adjustable schematic views, not mechanical CAD models.
- Show the reported physical connector as SYS_FAN4 instead of adding PWM 6.
  Component callouts always include configured LED lengths and the fan
  connector in separate lines, with leader lines outside the case. Unknown
  lengths/mappings show —; controller-wide lengths retain per-zone meaning.
  Explicit header hints in notes narrow display only, never change routing.
  The original `nct6687:pwm6` stable identity stays unchanged in technical
  details; no inferred port renumbering or additional hardware write.
- Double-clicking an unassigned RGB block opens its ordinary component editor
  instead of the RGB-device requirement error. RGB and PWM assignment remain
  distinct; a fan connector does not imply a lighting connector.
- Select all writable RGB devices by default; opt into individual selection
  with the visible checkbox and per-device checks in the inventory list.
  Locked devices stay excluded; selection never starts an effect or write.
  Persist the mode; group/subset/clear/reset actions remain explicit subsets.
- PC Case Profiles 1.2; RGB Studio 1.6. DE/EN/ES/FR: 1,390 shared
  messages. Internal local packaging only, no installation/tag/publishing.
  Routine backup rotation retains the two newest complete releases under the
  owner's standing approval. Physical usability remains owner-verifiable.
