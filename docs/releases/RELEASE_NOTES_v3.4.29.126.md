# Open Hardware Control 3.4.29.126 INTERN

Internal development build, 25 September 2026.

## GPU cockpit

- Rebuild the Graphics Card page around the approved three-column reference:
  Overview & Tuning, Fans, and Load Test & Presentation share one wide cockpit.
  The layout reflows to two or one column on narrower windows.
- Use OHC's neutral GPU artwork or the user's managed custom image. No vendor
  product image is bundled or inferred as a hardware capability.
- Keep profile, hardware, GPU details and LACT diagnostics as secondary tabs.

## Fan curve and permanent LACT takeover

- Edit all five curve points through exact temperature/speed fields or drag
  them directly in the graph. Quiet, Balanced and Performance create bounded,
  monotone drafts within LACT-reported temperature limits.
- Add a prominent combined action that first performs the reversible physical
  response test and only then confirms the identical fan-only candidate in
  LACT. The existing rollback-only trial and separate post-test save remain.
- Show the workflow stage explicitly and log whether a successful test was
  merely rolled back or actually committed. Static 100% remains LACT `1.0`.

## Logs and verification

- Copy OHC GPU events, LACT service messages or their combined report directly
  to the clipboard. The general Log copy action continues to use its active tab.
- The supplied `.125` log confirms the current mainboard-fan batch line works;
  the repeated channel lines shown above it belong to recovered `.124` context.
- Focused GPU/UI/log tests and a full offscreen cockpit render run without live
  hardware writes. Physical fan-curve and permanent-commit validation remains
  the final user smoke test on the target RX 9070 XT system.
