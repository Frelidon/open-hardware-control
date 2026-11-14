# Hardware Fix 1.0

The profile registry is deliberately narrow. The first profile supports only
the **MSI MAG 274QPF X30MV** over DisplayPort. It installs an anonymized EDID
override that changes the VRR range flag and the required checksum while
retaining the model timings. The monitor serial descriptor is replaced by an
unused descriptor and is not shipped, logged, displayed, or used for matching.

Mutating actions use fixed local resources, a per-profile lock, an interactive
terminal for sudo, and an atomic result file. No arbitrary root scripts or
user-provided paths are accepted. Fedora uses the bundled Fedora path and never
runs the Ubuntu AppIndicators automation.

The bundled automation and terminal diagnostic share the corrected anonymized
EDID hash from `lib/vrr_hardware.py`. Keep it equal to the profile's
`CORRECTED_EDID_SHA256`; regression tests exercise that exact binary through
monitor coverage and DRM CRTC reads. Unknown EDIDs never trigger a tray reset.

The primary `install-local` action coordinates the existing boot installer and,
only on Ubuntu/GNOME after EDID activation, desktop setup and the single local
service. Local ownership is the default; the redundant provider picker is gone.
`workflow.py` has no direct hardware writes. Fixed individual actions remain in
More options. Terminal jobs use a validated hex UUID to correlate even results
that finish before the first poll. Never interpret another job's result.
