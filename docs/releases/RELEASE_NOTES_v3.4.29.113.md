# Open Hardware Control 3.4.29.113 INTERN

## GPU and support LED motion

The default GPU strip uses a wider 40% approach and 38% fade so neighbouring
LEDs brighten before the white head and dim more gradually behind it. The
support strip retains its 32%/36% default, and previously saved adjustments
remain unchanged. Both rows now use a fixed shared open-strip travel cycle:
changing the shape of one row does not shift the paired row's head position.

The existing GPU dialog previews the configured physical LED counts and
displays measured successful OpenRGB transfer rates. It saves changes only
when the dialog is confirmed. The target stays at 25 Hz, and the sole SDK
worker and controller ownership checks remain. A slow controller can still
look less fluid than the preview because OHC cannot read the optical LEDs.

## Verification

Automated tests cover the independent shapes, fixed shared phase, real count
mapping, settings and worker frame parity. The editor was rendered offscreen
in all four supported languages. No physical GPU or support LED write or
optical confirmation was made while preparing this build.
