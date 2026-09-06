# Open Hardware Control 3.4.22.1 INTERN

Small stability hotfix on top of 3.4.22.

## ENE DRAM cold-boot reclaim

Some ENE-controlled RAM can report `Direct` through OpenRGB after complete power loss while the physical LEDs still ignore SDK frames. 3.4.22.1 performs one explicit Direct-mode transition through OpenRGB's own local CLI/server driver path after the OpenRGB inventory is stable and before the saved RGB profile starts. The normal persistent SDK worker then takes over.

The workaround is intentionally limited to detected ENE DRAM and runs once per managed OpenRGB engine lifetime. No ENE SMBus register implementation is copied into Open Hardware Control.

3.4.23 remains reserved for the planned larger fan-control/hardware-control work.
