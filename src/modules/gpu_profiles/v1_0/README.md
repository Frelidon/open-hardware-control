# GPU profiles 1.0

Stores up to 32 local, exact-GPU-bound profiles containing the LACT
configuration, fan/Zero-RPM state, load-test resolution, duration and window
presentation. A SHA-256 digest detects changed embedded profile data; imported
or edited main profiles cannot silently turn an unverified GPU payload into an
automatic hardware write.

The model catalog is presentation-only. Clock, power, temperature and fan
limits always come from the currently connected card through LACT.

`visual_catalog.py` describes original OHC schematic cooler shapes and light
guides for the case view. These presentation profiles never invent electrical
LED counts, fan limits or hardware routes. The chosen shape is saved with the
case slot and is independent of the verified LACT profile.
