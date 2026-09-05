# RGB Studio 1.1

`ene_start_recovery.py` owns the bounded delayed ENE-DRAM cold-start policy.
It coordinates only existing public controller operations and performs no raw
SMBus or USB access. The host remains responsible for OpenRGB ownership,
device classification and applying the current design.

`design_gallery.py` owns the hardware-independent Qt gallery for built-in RGB
designs, including left-click selection and right-click color-edit requests.

The host orchestrator keeps a saved profile start pending while OpenRGB's first
cold-start inventory is intentionally treated as incomplete. The existing
bounded inventory retry must either provide writable devices and continue the
profile or release the already-acquired RGB session without an unbounded loop.
