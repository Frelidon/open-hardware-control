# Open Hardware Control 3.4.29.117 INTERN

## Remove the failing RGB packet experiment

The owner's installed `.116` log confirms that GPU and support effects work
on the normal device-frame path. At 03:36:27 and 03:36:29 both zone trials
were enabled; both switched to `zones`, then timed out, and the managed
OpenRGB engine exited unexpectedly at 03:36:49. The automatic preference
fallback could not revive the crashed process. A complete OHC restart at
03:40 restored the normal path and all six recognized devices.

The trial checkboxes and subsequent zone-update packet path are removed.
Saved `.115`/`.116` trial settings are ignored. Running effects now always
send the previous whole-device SDK update after the normal Direct setup.
The existing Direct setup may still use its proven one-time zone fallback;
that also occurred on the owner's successful starts. GPU routing, physical
LED counts, motion controls and read-only Case preview are unchanged.

OpenRGB's SDK distinguishes `UpdateLEDs` (device update) from
`UpdateZoneLEDs` (zone update). Its controller API describes the former as
queued on a device thread and the latter as immediate. The logs establish
correlation between the new multi-zone path and crashes on this system; they
do not identify the exact OpenRGB driver fault or measure optical frame rate.
An isolated comparison with OpenRGB's own effect UI and a video of the real
GPU strip is still needed before changing the motion renderer or LED count.

## Verification

Regression tests ensure that saved trial flags do not enter the render
payload, that even a stale worker field cannot select zone writes, and that
the persistent SDK session sends whole-device packets after preparation.
No live hardware action was performed during development.
