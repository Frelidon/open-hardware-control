# Open Hardware Control 3.4.29.116 INTERN

## Restore the working RGB path

The owner's installed `.115` log shows the MSI GPU changing from the normal
device frame to zone packets at 03:20:40. SDK timeouts followed, then the
managed OpenRGB engine exited and OHC stopped the animation. The log does
not prove which OpenRGB driver call crashed, but the new packet path is the
clear regression trigger. `.116` therefore defaults both GPU and support
to the previous whole-device frame path. The `.115` experiment preference is
ignored even if it was saved.

The GPU setup dialog offers separate, unchecked zone-packet trial switches
for the routed MSI GPU and Airgoo support. They are available only when
those controllers are explicitly identified. An SDK failure disables the
affected trial and returns it to the device-frame path. An unexpected
managed-engine exit disables active trials and retains the existing manual
restart quarantine. The log names GPU or support, the packet path and any
automatic fallback. A socket response still cannot verify visible LEDs.

The read-only animated Case schematic from `.115` remains. No hardware
configuration, LED count or route is changed during upgrade.

## Verification

Loopback tests cover default device packets, opt-in zone packets and return
to device packets. UI tests cover the independent defaults, stale `.115`
setting, and automatic preference fallback. Physical optical behavior of
either experimental route must be judged on the actual devices.
