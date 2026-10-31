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
