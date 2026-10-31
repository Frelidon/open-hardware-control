# Process Runtime 1.1

First staged runtime boundary: one read-only sensor process supplies bounded,
timestamped CPU/GPU/system snapshots to the GUI, cooling and imported LCD metrics.
`controller.py` supervises readiness, one in-flight request, three-second timeout,
bounded 1/2/4-second restart and 2.5-second freshness. Missing/stale data stays
unavailable; never synchronously fall back to sysfs in the production GUI.
`sensor_worker.py` imports no Qt, reads no hardware write paths and communicates
only on owned stdin/stdout. User-created subprocesses never gain PWM calibration.
`health.py` displays actual owned process states and sensor age, software SDK
transfer statistics and shutdown journal location. No invented optical/GPU FPS.

This is the first migration stage, not an autonomous fan service. Cooling stays
in the existing calibrated, ownership-protected controller with its firmware
watchdog. TRCC/OpenLinkHub remain separate sole owners. Explicit quit stops the
runtime; close-to-tray preserves it. A full autonomous core and cooling migration
require subsequent hardware validation, not silent changes to PWM authority.

`diagnostics.py` journals private, bounded module events with exact process ID,
exit status/code, failed request, runtime, bounded stderr/traceback and retry.
`sdk_supervisor.py` adds five-second readiness/frame deadlines and 1/2/4-second
backoff to the existing sole-writer SDK worker. Retry budget resets only after
confirmed progress in a 30-second stable generation; native engine quarantine
remains unchanged. `restart_policy.py` contains the Qt-free retry budget.
