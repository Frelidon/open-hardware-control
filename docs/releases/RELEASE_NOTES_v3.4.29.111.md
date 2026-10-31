# Open Hardware Control 3.4.29.111 INTERN

## GPU load and LACT fan verification

The `.110` diagnostic showed only 35% average RX 9070 XT load despite an 8K
vkmark run. On this host, `DRI_PRIME=1` selected the Ryzen integrated GPU.
Both OHC benchmark paths now select the LACT device by its reported PCI
vendor/device ID. The long test checks vkmark's actual device banner and
records exit details, clock, power and throttling. Its scene duration extends
beyond the selected 15, 30, 60 or 120 seconds. A repeated, bounded 15-second
8K run reported the RX 9070 XT and 30 of 30 load samples at 100%.

The `.110` fan diagnostic confirmed that LACT accepted a static 100% setting
and PWM immediately rose to 255. RPM had only begun rising when OHC reverted
the two-second preview. A newly enabled fan now has up to 3.8 seconds within
LACT's timed rollback window to show an RPM response; absent response prevents
permanent save. Existing fan profiles still use the confirmed LACT write and
rollback check. Diagnostics display no active speed target while LACT fan
control is disabled.

OHC now defaults the GPU power editor to LACT's reported device default:
330 W on this Sapphire card. A higher limit needs an explicit confirmation
and cannot exceed LACT's reported maximum. An already active higher value
set outside OHC is labelled as active; OHC presents the stock limit as an
untested proposal until the user tests and saves it. During a long test
without that unlock, ten consecutive average-power samples more than 5%
above the reported default stop the workload. OHC restores an earlier
profile only if its own matching snapshot exists. This does not measure
connector temperature or replace the GPU driver's own power protection.

## Safety and verification

The repeated benchmark changed no LACT tuning or fan setting. A read-only
LACT check after the owner's clock concern found a 0 MHz offset, no custom
core maximum and a 330 W cap equal to LACT's reported default. A transient
3300 MHz observation does not, by itself, establish long-term stability.
The new fan timing still awaits a user-initiated hardware test; no GPU fan
write was performed while preparing this version.

The GPU's open-strip spinner/comet now illuminates approaching pixels earlier
and fades departing pixels more gradually. The GPU and explicitly paired
support still share one clock; their configured physical LED counts, 25-Hz
transport target and single writer are unchanged. Automated frame tests pass;
the final look on the owner's LEDs still needs an optical check.
