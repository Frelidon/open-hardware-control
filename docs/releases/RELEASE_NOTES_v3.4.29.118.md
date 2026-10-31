# Open Hardware Control 3.4.29.118 INTERN

## GPU LED smoothness assistant

The GPU lighting dialog offers a guided visual comparison for an already
running OHC Spinner or Comet effect on explicitly paired GPU and support ARGB
ports. The assistant temporarily switches off other selected OHC RGB zones,
compatible native OpenRGB devices and selected NZXT channels so that the two
strips are easier to judge. Each candidate is sent through the existing
whole-device SDK worker. Its ten-second countdown begins only after both
controllers confirm a new frame. “Still jerky” reduces the bounded tempo
and broadens the GPU light edges; “Smooth · apply” saves the chosen values.
Cancel restores the previous values. Closing the assistant requests the
previously selected design for all selected RGB devices again.

The reference video showed that the GPU's OpenRGB native Serial effect can
look smoother than Runway at some hardware speed settings. This assistant
retains OHC's synchronized external ARGB route so the GPU and support keep
the same timing. It does not claim optical confirmation before the owner
tests this version on the physical GPU.

During calibration, the paired strips use temporary blue and white for a
clearer moving-edge comparison. Single-pixel and fan-zone count tests use
white for the target and black for other selected OHC LEDs. Guarded preview
restoration also runs after a failed test if OHC still owns a healthy engine.

## Verification

Automated tests cover the bounded adjustment steps, blackout of unrelated
Direct zones, both-controller frame gate, ten-second gate, cancellation and
restoration. No physical RGB hardware was written during development.
