# Open Hardware Control 3.4.29.88 INTERN

- Carry all .87 improvements: complete private ZIP profile packages with app
  settings, positions/scales, RGB/PWM routes, exact counts, custom fan models,
  associated media and guarded startup-only import with rollback.
- Declare chained fan order separately from per-ring clockwise order.
  Physical LED 1 may start on the top/left or bottom/right fan. Preview and all
  spatial RGB samplers share the mapping; saved old paths remain unchanged.
  The full package preserves this declaration. Pixel tests retain true physical
  numbering, counts and the sole-writer transport stay unchanged.
- Import only recognized media/theme/font asset types, matching export.
  Reject duplicate directories and conflicting file/directory paths before
  creating staging. Never accept an executable simply because it is listed.
- Stop owned timers and clear RGB restart intentions before profile-worker
  cancellation, so a cancellation failure cannot skip later cleanup phases.
  X with close-to-tray still hides; explicit Quit performs orderly release.
- RGB Studio 1.11, Profile Bundle 1.0, Application Shutdown 1.0, PC Case
  Profiles 1.2; 1,446 atomic DE/EN/ES/FR messages.
- Retain confirmed personal counts: GPU MSI JARGB 1 = 30; Airgoo A1 front
  2×8/SYS_FAN4, B7 bottom reverse 3×8/SYS_FAN6, B8 rear 1×8/SYS_FAN1,
  A8 Thermalright radiator 3×10, B6 GPU support 12. Manual edits win.

Local internal packaging only. No installation, firmware/backend update, live
hardware test, push, tag or public release. Hardware-free regressions do not
prove physical FPS or a native OpenRGB/controller firmware crash fix.
