# Open Hardware Control 3.4.29.97 INTERN

- When tray continuation is enabled, an ambiguous window-manager close now
  asks explicitly whether to quit, keep running in the tray, or cancel.
- Choosing Quit immediately enters the existing orderly hardware hand-back,
  owned-process cleanup and direct Qt application exit. The saved tray setting
  remains unchanged.
- Add a bounded, read-only interpreter for the private shutdown journal. It
  separates a clean exit from tray continuation, cancellation, an incomplete
  attempt, and a process still alive during independent observation.
- System Status shows the interpreted latest attempt and, when phase records
  prove it, the last unfinished shutdown phase.
- The supplied local journal was classified as tray continuation: window-close
  events had close-to-tray enabled and no exit request. Later explicit Quit
  events completed Qt loop return, Python atexit and parent disappearance.

The change adds no forced kill, elevated command, password handling or hardware
write path. Existing fan/LCD restoration order, session shutdown and tray
preference are preserved. Process termination remains diagnostic evidence, not
proof that physical hardware accepted a restore command. All 713 release tests,
the security/privacy scan and the module/repository checks pass.
