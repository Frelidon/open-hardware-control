# Application shutdown 1.1

`journal.py` privately records requests, phases and Qt-loop return regardless of
UI sink lifetime. `watcher.py` reads only the exact exiting parent with starttime
verification for at most 90 seconds; it never signals the app. One delayed stack
dump diagnoses a blocked Python/Qt thread. Logs are private and bounded; hardware-
free mode retains phase journaling but starts neither observer nor fault timer.
`qt_processes.py` reaps remaining window-owned QProcesses only after existing
hardware restoration. The backend retains its own callback-suppressing shutdown.
Explicit exit calls Qt directly after cleanup; this is not forced interpreter exit.
After the software RGB worker stops, the host applies the persisted final
solid colour or reported native Rainbow mode synchronously and best-effort,
then releases the RGB session lock and managed engine. This phase is limited
to a real exit; close-to-tray never enters shutdown and a program restart skips
the final light so startup does not visibly fight the handoff. Command success
does not claim physical LED readback.
An explicit application restart starts a tiny detached standard-library waiter.
It validates the current Linux PID start time, waits until the old process and
its single-instance lock owner have ended, and only then executes the same OHC
entry point without the tray-autostart flag.  This prevents the replacement
from being mistaken for an ordinary second launch while cleanup is still active.

`diagnostics.py` reads at most the bounded private journal and classifies the
latest attempt as clean, continued in the tray, cancelled, incomplete or stuck.
It can name the last unfinished shutdown phase but never treats process exit as
proof that hardware accepted a restore command. The System Status page shows the
classification without exposing journal contents.

The close button and window-manager close events now always keep OHC running:
they hide the window in the tray, or minimize it to the taskbar when no tray is
available. This is independent of the separate ordinary-minimize preference.
The automatic close journal choice is distinct from the historical explicit
tray choice and cannot migrate that preference. The tray context-menu Quit
remains the visible manual exit path; session logout/shutdown also performs
orderly cleanup.

`process_cleanup.py` closes only an OHC-owned pipe-bound helper's stdin and
waits for its existing EOF exit before trying bounded, unprivileged signals.
Root-owned pkexec children can reject signals; the rejection is recorded and
never aborts unrelated cleanup. No kill-by-name, new helper command, Polkit
scope expansion or forced application exit is introduced.

`sequence.py` isolates and logs each existing shutdown phase, preserving
hardware ownership and LCD/fan restore ordering. It stops this window's timers
and cancels engine-restart intentions. The host remains the only orchestrator
of hardware writes and Qt application exit. Timers and restart intentions are
quiesced before cancelling the owned profile worker; a cancellation exception
is recorded by the phase runner without skipping later exit phases. A clean LCD
marker is cleared only
after the restore sequence runs successfully. EOF/pending status and phase
completion are diagnostics, not claims of physical hardware readback.

Closing the window never begins hardware cleanup. Explicit tray Beenden and
catchable session signals use orderly cleanup. SIGKILL cannot execute
in-process cleanup; the firmware guard/watchdog remain best-effort fallbacks,
never an absolute guarantee.
