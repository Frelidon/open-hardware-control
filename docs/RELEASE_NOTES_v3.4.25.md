# Open Hardware Control 3.4.25 INTERN

3.4.25 is the navigation, cooling-editor and visual-consistency follow-up to the 3.4.24 dashboard redesign.

## Highlights

- New fixed **Navigation anpassen** control directly in the left rail.
- Functional module entries can be reordered with drag & drop and individually shown/hidden.
- **Übersicht**, **Navigation anpassen** and **Hilfe** are permanent safety anchors and cannot be removed.
- **Standard wiederherstellen** restores both default order and default visibility.
- Navigation preferences persist across restarts.
- Cooling navigation icon adapts to detected AIO/chassis-fan hardware; RGB Studio and OpenLinkHub now have explicit icons.
- Chassis-fan curves now open as an embedded OHC card instead of a separate undersized window.
- The chassis-fan curve uses the same interactive `CurveEditor` concept as Kraken CPU curves: draggable graph points plus synchronized exact-value table.
- CPU temperature is now the default source for all built-in chassis-fan presets. Untouched legacy `Maximum` profiles from 3.4.24 migrate once to CPU temperature; explicit GPU/liquid/weighted choices are preserved.
- RGB Studio, LCD, Profiles, Log, OpenLinkHub, Settings, About, Help and Desktop Designs now share the same compact module hero/card language used by the redesigned dashboard.
- Privacy redaction no longer mistakes clearly identified four-part software versions such as `3.4.23.2` for IPv4 addresses.

## Safety

- No new raw EC/SMBus register writes were added.
- Existing NCT6687/Polkit helper, calibration gating, watchdog and firmware-return behavior are retained.
- CPU_FAN/PUMP_FAN remain excluded from chassis-fan automation.
- Navigation customization changes presentation only; it does not alter hardware ownership or write permissions.
