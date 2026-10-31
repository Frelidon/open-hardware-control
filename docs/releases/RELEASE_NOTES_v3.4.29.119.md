# Open Hardware Control 3.4.29.119 INTERN

## Fan and ARGB crash fixes

The GPU fan preview no longer fails while deciding whether a changed fan mode
or curve requires physical response verification. It now evaluates the keys
of the change mapping and continues through the existing bounded LACT trial
and automatic rollback path.

The case ARGB route dialog owns its 300-ms inventory timer for its complete
lifetime. The timer is stopped and disconnected before the dialog accepts and
opens either the LED editor or the single-pixel test. The responsive topology
layout also preserves the live preview widget while moving it between its form
and preview group.

## Recoverable crash evidence

Already privacy-filtered application log lines are appended to a private,
bounded ring. When the independent shutdown journal identifies an incomplete
previous exit, OHC extracts exactly the final five minutes to
`last-crash-context.log`, then restores those lines into the next visible log
and its session file. A normal previous exit clears the ring without creating
a crash snapshot.

Fatal native signals now write all available Python thread stacks to a
separate private file. On the next start that trace is privacy-filtered and
archived as `last-native-crash.log`, providing evidence even when a PySide/Qt
fault bypasses `sys.excepthook`.

## Verification

Focused tests cover GPU fan change mappings, repeated ARGB editor transitions,
timer shutdown, the exact five-minute boundary, normal-exit discard, file
permissions, size bounds, symlink refusal and native traceback archival. No
physical hardware was written during development.
