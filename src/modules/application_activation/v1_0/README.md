# Application activation 1.0

This module keeps Open Hardware Control single-instance without turning a
second desktop launch into an error dialog.

- The existing process lock remains the authority that prevents a second
  hardware owner.
- The lock owner exposes one user-only local socket accepting only `show`.
- A second process sends that bounded request and exits before constructing the
  hardware UI.
- Tray autostart removes inherited desktop activation tokens so KDE does not
  retain a task-manager startup placeholder for the intentionally hidden
  window. Normal interactive starts retain desktop startup feedback.

The socket is stored below OHC's private per-user state directory. Failure to
activate never bypasses the process lock or starts a second hardware writer.

`autostart.py` repairs the user installer's existing autostart target when a
new user installation would otherwise leave the old system application active.
Only recognized OHC launchers are retargeted; comments, custom arguments and
disabled flags remain. Missing entries are not created, custom wrappers and
symlinks remain untouched. The helper runs only from the explicit installer,
never during ordinary application startup.
