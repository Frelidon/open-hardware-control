# Control authority 1.0

Stores one explicit writer selection per hardware domain. `monitor` and every
external owner disable OHC writes for that domain; unavailable providers cannot
be selected. This module does not stop, start or impersonate third-party
software. The host performs bounded release actions before committing a change.
