# Open Hardware Control 3.4.29.65 INTERN

The Nebula Drift value frames are calibrated against the supplied photographs
of the application preview and the physical 1600×720 Levita display. Block
positions already matched; the physical TRCC renderer draws its live-value font
approximately 22 percent wider and 12 percent taller than the local
Noto/DejaVu preview metrics.

The renderer now sizes each value frame automatically from its configured text
and font size and then applies those measured TRCC reserves. Depending on the
value, the generated frames are approximately 16–18 percent wider and 10–12
percent taller than in 3.4.29.64. This restores useful interior spacing on the
physical display without returning to large opaque panels.

Nebula Drift Minimal, System and Performance were all regenerated. Their
positions, live-data definitions and faint transparent artwork are unchanged,
so the selected Layer-1 video remains visible.

Display transfer, profile staging, the single-owner TRCC command queue, cooling
curves, calibration, firmware return and every hardware-write path are
unchanged. No GitHub push, tag or public release was created.
