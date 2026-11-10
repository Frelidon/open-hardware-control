# OHC Native OpenRGB plugin

This is the optional OpenRGB 1.1/API-5 plugin used by RGB Studio. It keeps
OpenRGB as the device owner and accepts bounded JSON-lines frames over a
0600 Unix socket. Frames are acknowledged as soon as they are queued; a
dedicated worker per controller applies only its newest complete frame.
This latest-frame-wins boundary prevents a slow USB/I2C commit from blocking
the 60 Hz animation clock. The existing SDK worker remains the automatic
fallback when this plugin is not installed or cannot be reached.

Version 0.2 uses independent absolute 60-Hz deadlines, one queued frame per
controller and persistent threads. A slow MSI controller cannot delay Airgoo.
Start/reset creates a new generation; STOP drops pending frames and drains
executing submissions before returning. Status replies distinguish queue
acceptance from completed OpenRGB API submissions and never claim optical
readback. The same socket accepts read-only `stats` queries while OHC streams.

`ColorCodec.h` explicitly packs validated hex/array channels into OpenRGB's
0x00BBGGRR format. Passing bitwise expressions into its unparenthesized
`ToRGBColor` macro previously repeated red into every channel. The compiled
colour fixture checks independent channel gradients and rejects invalid input.

The live Ubuntu diagnosis measured Airgoo USB frame writes at 58.52 Hz after
isolation, versus 3.83 Hz with the old global barrier. MSI's 727-byte feature
reports took ~93 ms each. The optional OpenRGB source patch at
`tools/openrgb/msi-761-dirty-zones.patch` skips unchanged zone reports and marks
count changes dirty; it does not change report bytes, size, USB ownership or
the user's LED counts. Its separate backend build must be validated on the
actual board. On this Ubuntu board the installed patch raises the single changed
MSI zone to about 10.64 USB frames/s, not 60. The owner confirms smooth case/GPU
movement and correct GPU colours with the colour fix. A real Fedora hardware
run remains pending.

Build against a matching OpenRGB checkout and Qt 6 development packages:

```sh
cmake -S src/native/openrgb -B /tmp/ohc-native-build \
  -DOPENRGB_SOURCE_DIR=/path/to/OpenRGB
cmake --build /tmp/ohc-native-build
```

Copy `OHCNativePlugin.so` into OpenRGB's per-user `plugins/` directory and
restart the managed OpenRGB instance. The plugin deliberately has no network
listener and removes its socket when unloaded.
