# Open Hardware Control 3.4.29.109 INTERN

## GPU load test without saved tuning

The owner's installed `.108` log confirms that vkmark installed successfully
and subsequent short GPU offset previews ran and reverted successfully.
Restarting the application is unnecessary. The longer GPU load-test button
remained unavailable because `.108` required a previously saved OHC tuning
snapshot; the owner had only tested offsets, not saved them permanently.

The longer 15–120 second benchmark can now test the **currently active
LACT GPU configuration** without an OHC snapshot. It does not write GPU
clocks, power or fan settings. The page explains that unsaved Tuning inputs
are excluded from this run. If OHC previously saved the exact active
configuration, its matching prior snapshot can still be restored after an
observed fault. Without that snapshot, the load stops and reports the fault
without claiming a rollback.

## Verification

An offscreen regression starts and cancels the baseline test with simulated
LACT and benchmark processes and asserts no GPU configuration write. Full
release results are documented by the local release check. No live benchmark
or GPU write was run while preparing this package.
