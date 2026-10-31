# Open Hardware Control 3.4.29.152 INTERN

## CPU startup defaults

- OHC detects the installed CPU at startup and loads the matching verified
  default pump and radiator curves.
- The automatic defaults are used only while the curves remain automation
  owned. Any manual CPU selection, imported cooling profile, edited curve, or
  applied curve becomes user owned and is preserved on subsequent starts.
- The control and current state appear directly below **Cooling ownership ·
  conflict protection**. Loading defaults never activates hardware control.

## Complete PC fan topology

- CPU_FAN and PUMP_FAN are available beside SYS_FAN connectors in the PC case
  mapper, so radiator, pump, and case fans can be saved together.
- Mapping remains settings-only: assigning or loading a connector performs no
  PWM write, calibration, or control activation.
- Replacing an occupied connector or position requires confirmation, and every
  change is synchronized into the selected local PC profile.
- On the detected MSI MAG X870 TOMAHAWK WIFI only, the previously confirmed
  reference wiring is migrated once by exact board-reported connector labels.
  No pwm index is guessed and existing user assignments win.

## Module settings and scope

- Settings once again expose all optional sidebar modules with a one-click
  restore action.
- The four UI languages contain 1,916 shared messages.
- Fedora-specific package and setup behavior is unchanged.
