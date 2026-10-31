# Hardware backends 1.0

Stores explicit or automatic backend choices and resolves them fail-closed.
Version 1.0 only exposes transports already implemented by OHC: TRCC Linux for
the Levita display and OHC's calibrated Linux-hwmon path for mainboard fans.
Native Levita USB and CoolerControl control adapters remain visible roadmap
entries in the UI, but cannot be selected until a tested transport exists.
