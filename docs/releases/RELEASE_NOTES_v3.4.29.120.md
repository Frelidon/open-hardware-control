# Open Hardware Control 3.4.29.120 INTERN

Internal development build, 22 September 2026.

## GPU profiles and artwork

- Exact-GPU subprofiles store the complete LACT configuration, fan curve,
  Zero-RPM state, stress duration, 4K/8K size and window presentation.
- The selected GPU subprofile is embedded in an OHC main profile. Imported or
  edited GPU payloads remain non-writing drafts until locally verified for the
  same LACT GPU ID.
- Optional startup activation keeps the existing CoolerControl ownership,
  LACT pending/confirm/revert, power and telemetry checks.
- Transparent PNG/WebP artwork can be imported, changed and removed. OHC owns
  only a normalized private copy; the original is never modified or deleted.

## Interface and load test

- Maximized window with visible taskbar is the default stress-test mode;
  minimized and full-screen modes are saved with the GPU profile.
- Optional Gamescope keeps vkmark's internal 4K/8K rendering independent from
  the monitor-sized output. The KWin state helper targets only the exact
  benchmark PID.
- Original unbranded AMD-/NVIDIA-coloured family illustrations, horizontal or
  vertical mounting and an animated fan-curve preview refresh the GPU page.
- The real Qt workspace now follows the dark rendered control-deck design with
  permanent GPU/hotspot, fan RPM and power cards, a deeper artwork stage and
  clearly highlighted safe actions. Evidence renders use the actual OHC theme.
- Current AMD RX 9000/7000 and NVIDIA RTX 50/40 names are presentation-only;
  they never supply clocks, power or fan limits.

## Verification

- Focused GPU/profile/artwork/window/dependency tests and the complete
  four-language release gate pass (801 tests plus security scan).
- Runtime/developer archives, source archive, Local-AI bundle and the internal
  RPM were built with SHA-256 manifests and the rolling external backup. No
  installation, publication or physical GPU write was made.
