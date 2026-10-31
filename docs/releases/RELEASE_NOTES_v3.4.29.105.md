# Open Hardware Control 3.4.29.105 INTERN

## Primary-screen placement

The owner's `.104` log claimed the main window was on the selected DP-1
primary display, but the window visibly opened on the left HDMI-A-1 display.
On KDE Wayland, OHC now asks KWin for its own mapped window's output and
requests a move to the selected output if needed. The temporary KWin script
matches OHC's process ID and main-window title, is unloaded after the check,
and does not create a permanent window rule. A read-only live test with a
nonexistent PID confirmed the KWin callback; actual placement still needs
visual checking with the installed build.

## AMD Overdrive setup

The GPU page can ask LACT to prepare AMD Overdrive after the user confirms
the boot-system change. LACT owns the configuration and any necessary
initramfs update. OHC keeps the interface responsive, reports errors and
asks for a separate manual restart. Opening or refreshing the page does not
make the change. GPU tuning stays locked until LACT reports Overdrive active
and has a saved baseline profile. The owner already enabled this through
LACT; OHC did not call the new setup command on the live machine.

## Session log diagnosis

The running `.104` app exited after its own log recorded a "Fenster schließen"
click at 19:37:18 and an ordered shutdown. The log does not identify the
click's source. A separate repeated gallery input-filter exception came from
an LCD host field shadowing `QWidget.window()`; the filter now calls the Qt
method through its class, with a regression test.

The owner clarified the desired behavior: the X now always keeps OHC
running in the tray, with taskbar minimization as fallback. The File/header
menus close the window as well; manual Quit is available through the tray
icon's right-click menu. A desktop session shutdown still runs cleanup.

## Verification

All 749 release tests and security/privacy/module checks passed. RPM,
runtime/developer ZIPs, source archive and full-history Local-AI Git bundle
were built. ZIP integrity, relevant new files in ZIP/RPM, the dist SHA-256
manifest and both retained `.104`/`.105` backup manifests passed. DEB was
unavailable on this Fedora host. No live LACT setup, GPU tuning, reboot,
package installation or real OHC window move was performed.
