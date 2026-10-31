# Open Hardware Control 3.4.29.110 INTERN

## GPU load, fan controls and LACT diagnostics

The owner's `.109` log confirms that the longer GPU test starts and can be
cancelled. The first 15-second run reached only 12% peak GPU load, so it did
not establish stability. The long-test page now offers 4K and 8K vkmark
rendering with per-pixel Phong shading. It defaults to 8K, records each LACT
load/temperature sample and reports a meaningful pass only after at least
three samples, 90% average load and 95% peak load. Temperature and throttle
limits still stop the test. A 4K choice remains available if 8K cannot start.
The short, five-second LACT rollback preview retains its smaller viewport.

The `.109` fan button merely selected the fan tab; it did not write or test
the chosen value. It now runs the same bounded LACT preview as Tuning. The
fan tab offers a validated static 35–100% setting alongside its five-point
curve. LACT remains the sole GPU fan writer, and CoolerControl ownership is
checked before a trial. Trial, permanent save and rollback remain separate.
LACT's confirmed response is distinguished from physical fan response; a
short preview alone cannot prove the final RPM. The supplied LACT snapshot
recorded an externally selected static 100% profile and a 3852 RPM reading,
but OHC's new fan write path has not yet been exercised on hardware.

The Tuning page can discard unsaved inputs, restore an OHC-saved baseline, or
reset the selected active LACT GPU profile to defaults after a separate
confirmation. The fan release action remains available when the profile was
changed directly in LACT. Resets re-read the current LACT state and refuse
to clear a profile that changed after the page was refreshed.

A new LACT log tab captures OHC's GPU actions and selected GPU readings,
loads the last 200 `lactd.service` journal lines without elevated rights,
and exports a private local text file only after the user chooses a path.
LACT's own journal does not record every fan transition; the captured
readings include RPM, PWM, fan mode, configured spin-down delay and ZeroRPM.
The owner should review a diagnostic export before sharing it.

## Verification

The regression suite uses simulated LACT and benchmark processes for static
fan validation, external fan release, stale-profile reset protection,
diagnostic export permissions and insufficient/sufficient GPU-load results.
No live GPU write or 8K benchmark was launched while preparing this version.
