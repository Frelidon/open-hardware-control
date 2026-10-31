# Design Automation 1.0

This module owns the local Automation Center for complete OHC profiles.

- `model.py` validates at most 64 bounded rules for process, game, fixed-time
  and interval triggers and resolves exact process-basename priority.
- `probe.py` reads `/proc/*/comm` outside the GUI process. It does not inspect
  window contents, execute desktop entries or use the network.
- `page.py` owns the Qt editor, asynchronous probe controller and the local
  MangoHud configuration/launch-option generator.

Rules contain existing profile IDs, not commands. RGB and Levita activation
reuse their established ownership and startup guards. The previous profile can
be restored after a sustained process trigger ends.
