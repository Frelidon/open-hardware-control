# Window chrome 1.2

Provides Open Hardware Control's own title bar and delegates window movement
and edge resizing to Qt's compositor APIs. This keeps the implementation usable
on KDE Wayland and X11 without manually moving global window coordinates.

The close action calls the main window's normal `close()` path, so the existing
tray/minimize and controlled hardware shutdown policies remain authoritative.
Its 48-by-42-pixel hit target reaches the top-right corner. Window-control
buttons bypass the resize-edge handler, so the corner remains a reliable close
target even on a frameless Wayland window.

The controller records which child widget received a resize cursor and clears
that override on edge leave, hide, close, destruction, deactivation and window
state changes. It never moves or captures the pointer and does not change the
desktop cursor theme.
