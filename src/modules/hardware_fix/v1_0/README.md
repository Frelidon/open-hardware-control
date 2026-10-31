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
