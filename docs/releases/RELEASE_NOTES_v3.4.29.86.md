# Open Hardware Control 3.4.29.86 INTERN

- Orderly application exit no longer aborts when the root-owned fan-helper
  rejects user-level signals. Close its existing stdin pipe and wait for EOF
  first; isolate all existing cleanup stages. Preserve close-to-tray. A clean
  LCD marker is cleared only after restoration, not before.
- Reported controller/header wiring remains selectable while the owned engine
  is offline. Actual ownership and device-quarantine restrictions remain.
  The route editor has explicit engine recovery and updates its open inventory;
  stale discovery callbacks/busy flags cannot latch manual restart. Only the
  concrete owned engine can be stopped, never a foreign RGB application.
- A bounded LED preview suspends background inventory and automatic design
  application. Tests cannot overlap or continue after engine loss. Closing or
  saving reapplies the selected design once after successful test completion,
  only with unchanged design/selection, enabled writes and available own engine.
  No automatic crash loop or guessed firmware lighting mode is introduced.
- Fan blocks offer category, editable brand/model, black/white variant and
  LEDs per fan with a dynamic total. The personal TZMRIT Interstellar-V2
  reference (Amazon ASIN B0CN39T7QN) uses the owner-observed eight addressable
  LEDs: two fans = 16. This is not a manufacturer-verified universal count.
  Selected-block totals are validated against actual SDK zone bounds before
  suggestion/save/test; other headers, GPU 30 LEDs, support 24 LEDs and PWM
  remain unchanged. Existing manual header declarations are not bulk migrated.
- RGB Studio 1.8, Application Shutdown 1.0, PC Case Profiles 1.2;
  1,394 complete DE/EN/ES/FR messages. Hardware-free regression coverage only:
  no claim that the underlying native OpenRGB crash or electrical controller
  firmware issue is fixed. No installation, Git tag or public publishing.

## Airgoo investigation

The official [Airgoo guide](https://www.airgootech.com/guide.html) names OpenRGB
1.0rc3. The upstream [AG-DRGB16 report #4970](https://gitlab.com/CalcProgrammer1/OpenRGB/-/issues/4970)
describes severe stuttering with Effects/Visual Map on Windows, not this exact
Linux crash. [Resize report #681](https://gitlab.com/CalcProgrammer1/OpenRGB/-/issues/681)
described crashes during simultaneous resize/LED updates and was closed as fixed
in 2024. These are context, not proof of the present crash cause or defective
hardware; no driver update or destructive configuration reset is performed.
