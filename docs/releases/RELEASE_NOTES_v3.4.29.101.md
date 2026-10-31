# Open Hardware Control 3.4.29.101 INTERN

- A live investigation of the installed `.98` showed two distinct behaviors:
  window Close continued in the tray as that version was configured to do,
  while the later explicit Quit cleanly exited OHC. The remaining 1.3 GiB
  process was the separately spawned TRCC display daemon.
- Ordered shutdown now releases the Levita display and then stops the exact
  TRCC daemon observed after OHC started it. A daemon present before OHC or
  one replaced by another process is left alone.
- If no TRCC daemon is running, firmware release does not auto-spawn one just
  to issue `device disconnect`.

This internal build includes the visual, checker and GPU-lighting updates of
3.4.29.100. The leftover daemon in the live session was stopped with TRCC's
own `kill` command and verified absent. No installation or public GitHub
release is performed by this build.
