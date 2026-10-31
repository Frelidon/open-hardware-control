# Open Hardware Control 3.4.29.112 INTERN

## GPU and support LED motion

The GPU's existing controller dialog now shows the declared LEDs of its
assigned ARGB zone and of the assigned GPU support as separate animated rows.
Separate GPU and support controls adjust how early approaching LEDs glow and
how far the light fades after the bright head; tempo stays shared. The support
shape can therefore stay as it is while the GPU shape changes. Moving a control changes
only the preview. Saving the controller dialog persists the bounded values;
cancel leaves the previous effect intact. The separate ARGB header editor
remains the place to set and test each physical LED count.

OHC displays recent successful OpenRGB frame rates for each assigned
controller beside the preview. GPU and support use the same paced motion
clock: after a delayed SDK write, the next dispatched frame advances only a
small amount instead of jumping to wall-clock phase. The target remains 25 Hz,
the SDK worker stays the sole writer, and existing selection and ownership
checks remain in force. An effective rate below target can still look less
fluid on real hardware; OHC cannot read back optical output.

## Verification

The preview was rendered offscreen in all four supported languages. Tests
cover saved/cancelled settings, distinct physical counts, shared worker output,
invalid input and pacing after a transfer stall. No GPU RGB write or optical
verification was performed while preparing this build.
