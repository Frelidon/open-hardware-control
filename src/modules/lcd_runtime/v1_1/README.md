# LCD Runtime 1.1

`progress.py` parses complete positive `sent … bytes (theme=…)` acknowledgements
from the legacy TRCC CLI ticker and the exact successful TRCC 9.10.4 hand-off
sentence. In daemon-owned mode OHC keeps health/memory supervision active but
does not restart the deliberately completed CLI helper; TRCC's own VideoLoop
paces video and sensor rendering.
`controller.py` watches 45-second startup/command deadlines and 15 seconds of
missing successful sends after startup. The same existing IPC ticker keeps both
static and animated displays active. Visibility never stops hardware output.
Timeout kills only the exact owned CLI client; recovery delegates the existing
bounded ticker policy (renewed by confirmed progress only) or existing daemon recovery with its five-minute cooldown.
Native hardware crashes retain quarantine; no second USB owner or raw protocol.
Acknowledgements are software send results, not optical display confirmation.
An unsupported CLI output format fails visibly rather than inventing progress.

`game_activity.py` coordinates the async probe. `game_probe.py` moves process-name scanning and a bounded GameMode query out of
the GUI. One in-flight probe, capped output, a three-second parent deadline and
captured enable intent prevent stale results from changing current FPS policy.
Tests: `tests/test_module_supervision_342992.py` plus existing LCD/full-UI suites.

`design_state.py` preserves the single explicit saved default over automatic
profiles and snapshots accepted commands for recovery. Preview selections never
write defaults/profile staging. Generation guards cancel superseded startup retries, including later preview
browsing. GPU clock correction metadata is copied with the accepted hardware
request rather than read from a later preview.
`memory_guard.py` allows stable video RSS, preserves 3-GiB emergency protection,
low MemAvailable (<256 MiB when RSS >=1 GiB), and sustained growth (three >=64-MiB
increases, >=256 MiB overall). No reset during apply. Reconnection can still be
visible on actual failures. Regression: `tests/test_lcd_design_authority_342993.py`.
