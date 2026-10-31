# Open Hardware Control 3.4.29.115 INTERN

## GPU transfer comparison

The owner's `.114` log reports MSI JARGB 1 with 30 declared GPU LEDs and
Airgoo B6 with 12 support LEDs. Both show about 24.5–25 successful SDK
frames per second, while the GPU alone still looks stepped. This rate counts
OHC-to-OpenRGB socket completion, not physical LED changes.

OpenRGB's documented SDK exposes whole-device updates (1050) and zone
updates (1051). The routed MSI GPU controller now defaults to a reversible
zone-packet comparison after its normal Direct-mode preparation. The GPU
dialog's “GPU: Zonenpakete testen” checkbox switches it back to the former
device-packet path. Every nonempty zone of that controller is sent in its
validated declared order; RAM and the Airgoo support retain their existing
paths. Mismatched zone lengths safely fall back to the complete device
packet. The application log records which path was used and states that a
socket response is not optical confirmation. No raw HID/firmware commands,
new OpenRGB instance or competing writer were added.

## Animated case schematic

During a running OHC RGB design, the Case drawing now animates the GPU,
support and RAM from their explicitly routed controllers and configured LED
counts. It uses the last frame clock, including the paced GPU/support clock.
Saved physical paths retain their recorded direction and endpoints; when a
path is absent, a schematic component row is shown without claiming real
wiring direction. Hidden pages stop the preview timer. No preview frame
opens a device or writes hardware.

## Verification

Local socket tests cover device and zone packet shapes, a saved-path switch
and the unchanged Airgoo path. Pure-frame and offscreen UI tests cover the
three component animations and visible timer. The effect on the owner's
physical MSI header requires an A/B optical check after installation.
