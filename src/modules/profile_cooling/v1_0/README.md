# Profile cooling readiness 1.0

A curve profile whose CPU snapshot is temporarily unavailable waits at most ten
seconds for a fresh sample from the existing read-only ProcessRuntime. No stale
sample fallback, synchronous sysfs read, relaxed 2.5-s freshness or PWM transport.
Only the established `transmit_profile_cooling` path can apply after rechecking
availability and existing ownership/calibration/lease guards.

New profile/cooling requests cancel the previous pending request. Changes to the
loaded cooling controls, shutdown or timeout cancel it too. Timeout is nonmodal
and durable in the shared error log, with sensor age/pending/failure context.
No automatic late application after timeout or user edits.
