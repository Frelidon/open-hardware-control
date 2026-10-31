# Open Hardware Control 3.4.29.60 INTERN

This internal version fixes the KDE/Wayland restore regression visible in the
supplied 3.4.29.59 trace. The maximized `3440×1394` work-area rectangle is no
longer accepted as a normal floating geometry. OHC stores normal geometry
separately, clamps all four edges to the selected screen and adapts its minimum
size for small logical HiDPI work areas. A 60–95% windowed-size setting and
`Ctrl+Alt+0` safe-fit action remain available even when title-bar controls are
off-screen.

The RGB PC view now follows the approved two-column concept more closely. The
personal Retro 360 Amazon action is removed; each catalog entry retains its
manufacturer source. Thirty entries use original model-family OHC silhouettes,
not copied product artwork. The view supports AIO/air-cooling visualization,
one-click airflow reversal and splitting a fan block into individually
draggable fans. The detailed Devices and Effects area is collapsed once by the
upgrade migration. Hardware ownership and write paths are unchanged.

No GitHub push, tag or public release was created.
