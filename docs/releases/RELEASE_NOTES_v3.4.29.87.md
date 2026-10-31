# Open Hardware Control 3.4.29.87 INTERN

- Profiles now offer a complete private ZIP package alongside existing JSON
  exchange. Include all app settings and user profiles, a current full profile,
  case positions/scales, RGB/PWM routes, exact LED counts, custom fan models,
  LED geometry, the LCD profile store and associated media/themes/fonts.
  A bounded owned worker performs copying/hashing off the UI thread.
- Import validates format, typed values, archive paths, file counts/sizes and
  SHA256. Files are staged privately, including empty media roots and ordinary
  copies of local file links; paths inside nested JSON themes are relocated.
  Apply only after explicit confirmation and next startup. Keep rollback;
  hardware automation, CPU regulation and PWM calibration require local
  reactivation. Logs, drivers, services and other apps' settings are excluded.
  Packages contain personal file references; do not publish them casually.
- The ARGB header editor gains an LED-path tab: physical LED 1/start and
  last/end, strip or equal-size rings, clockwise order and preview. Eight
  case-space travel directions include vertical and diagonal sweeps. Use
  existing case positions only for unambiguous assignments. Unconfigured or
  invalid paths preserve local rendering; tests use real 1-based LED indices.
- Carry the owner's corrected Airgoo wiring into this version: front A1
  2×8 / SYS_FAN4, bottom reverse B7 3×8 / SYS_FAN6, rear B8 1×8 / SYS_FAN1,
  Thermalright radiator A8 3×10, GPU support B6 1×12. GPU remains confirmed
  MSI JARGB 1 with 30. One-time personal migration preserves layout/PWM and
  unrelated zones; later manual edits win. Reusable custom manufacturer/model/
  black-white/LED library is selectable in block and zone editors.
- RGB Studio 1.10, Profile Bundle 1.0, PC Case Profiles 1.2 and Application
  Shutdown 1.0; 1,442 complete DE/EN/ES/FR messages. Existing serial transport
  and 25-Hz target are unchanged. Hardware-free tests do not prove physical
  FPS or a fix for native controller firmware/OpenRGB crashes.

Local RPM/runtime/developer/source/Git-bundle build requested. No installation,
backend/firmware update, live hardware test, tag, push or public release.
