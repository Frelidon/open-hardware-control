# Open Hardware Control 3.4.29.85 INTERN

- Fix the case-block ARGB action that previously stopped at “No ARGB header
  assigned”. Controller and reported header are now directly selectable;
  dragging a device tile first is no longer required.
- The selection offers LED-count editing and individual-LED testing through
  the existing bounded header editor. Choose an index from 1 through the
  declared count; the explicit test temporarily blacks other controller zones,
  so reapply the design afterwards. Manual counts are not physical readback.
- Explicit stable bindings survive restarts and old effect/position snapshots.
  Rebinding/unassignment changes no PWM, physical fan size, group or geometry;
  missing controllers/headers never silently select a different port.
- GPU blocks retain existing GPU-route authority. Tests still require enabled
  OHC hardware control, private-engine availability and ownership validation;
  no new transport or protocol is introduced.
- RGB Studio 1.7; PC Case Profiles 1.2; 1,390 complete DE/EN/ES/FR entries.
  Local internal RPM packaging only. No installation, Git tag or publishing;
  routine authorized backup rotation retains two complete releases.
