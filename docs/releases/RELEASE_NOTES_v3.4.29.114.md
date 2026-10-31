# Open Hardware Control 3.4.29.114 INTERN

## GPU and support light

The owner's phone video shows a saturated white GPU bar with abrupt-looking
edges while the GPU support fades more gently. The GPU now has a separate
white-peak control (35–100%, default 65%) and brighter low-level transition
steps. Previously saved lead, fade and speed values remain intact. The GPU
and support still share their moving-head clock and keep their distinct
physical LED counts.

While an OHC RGB design is active, moving a slider sends a temporary value
through the existing serial OpenRGB worker. Cancel closes the draft and
restores saved values on the next frame. Save makes the values persistent.
The Defaults button resets only the open draft until Save is pressed. No
second device writer or ownership bypass was added. A GPU renderer error
is reported instead of silently falling back to the old sharp generic effect.
During active output, the on-screen LEDs use the paced frame time delivered
to the worker instead of running a separate smooth preview clock.

## Case editing

The Case page and GPU component editor open the same GPU control dialog.
A component with one unambiguous ARGB header opens its LED count editor
directly; a separate control still changes the header assignment. The
component name is visible in the relevant editors. Saved, unambiguous
physical LED paths appear as schematic start, end and route dots on case
blocks. Undeclared directions are left blank.

## Verification

Automated rendering, persistence, four-language UI, draft rollback and
case-routing tests passed. The preview and SDK worker share the same GPU
colour calculation, but actual optical smoothness cannot be proven without
the owner's follow-up hardware test and measured GPU/support transfer rates.
