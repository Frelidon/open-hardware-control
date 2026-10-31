# Open Hardware Control 3.4.29.100 INTERN

- Case devices, Hardware Checker and temperature statistics use a consistent,
  responsive table style. Hardware Checker measures cell content so long
  motherboard names remain visible.
- A direct GPU load-test click performs an initial read-only inventory, then
  launches the bounded graphics helper. Vulkan `vkcube` is supported when
  `glmark2` is unavailable. The checker only calls a PCIe observation
  under-load while the helper is running and explains missing helpers.
- Overview, Cooling and Temperature Recording share a compact twelve-segment
  temperature gauge based on the existing Celsius sensor readings. Recording
  shows CPU, GPU and coolant values together.
- Video-guided GPU strip sampling narrows the moving white highlight and keeps
  the blue base visible. The configured 30 physical LEDs, route, 25-Hz target
  and sole hardware writer are unchanged.

The graphics helper launched on the local RX 9070 XT in two short Vulkan smoke
checks. Full in-app PCIe observation and optical RGB comparison still need a
real-hardware session. This build does not install the application or publish a
GitHub release.
