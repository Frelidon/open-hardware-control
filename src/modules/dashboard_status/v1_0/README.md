# Dashboard Status 1.0

`model.py` validates existing read-only CPU/DRM metadata and parses the reported
core/thread counts. It performs no discovery, I/O, inference or hardware writes.
`cards.py` explicitly initializes static information-card badges, tooltips and
translated topology. Recognition remains independent from current telemetry,
connection health, calibration and permission to control hardware.

The host calls `initialize` immediately after creating the four inventory cards,
then `refresh` on language changes. No user settings or sensor timers change.

`device_rows.py` replaces unconditional lower-panel OK badges with current,
already confirmed cooler/mainboard/OpenRGB inventories and the validated DRM
metadata. The host passes its existing thermalright/kraken detection result;
the rows perform no extra device discovery. Levita is never labelled NZXT.
