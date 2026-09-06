#!/usr/bin/env bash
set -euo pipefail
rm -rf "$HOME/.local/share/open-hardware-control"
rm -f "$HOME/.local/bin/open-hardware-control"
rm -f "$HOME/.local/bin/open-hardware-control-diagnostics"
rm -f "$HOME/.local/bin/open-hardware-control-desktop-shell"
rm -f "$HOME/.local/bin/kraken-control"
rm -f "$HOME/.local/share/applications/open-hardware-control.desktop"
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/open-hardware-control.svg"
for size in 22 32 48 64 128 256 512; do
  rm -f "$HOME/.local/share/icons/hicolor/${size}x${size}/apps/open-hardware-control.png"
done
rm -f "$HOME/.config/autostart/open-hardware-control.desktop"
rm -f "$HOME/.config/autostart/open-hardware-control-desktop-shell.desktop"
rm -rf "$HOME/.local/share/kwin/scripts/ohc-charms"
rm -rf "$HOME/.local/share/icons/OHC-Windowed-11"
rm -rf "$HOME/.local/share/icons/OHC-Orchard"
rm -rf "$HOME/.local/share/icons/OHC-Metro-8"
rm -rf "$HOME/.local/share/icons/OHC-Windowed-Cursor"
rm -rf "$HOME/.local/share/icons/OHC-Orchard-Cursor"
rm -rf "$HOME/.local/share/icons/OHC-Metro-Cursor"
command -v kwriteconfig6 >/dev/null 2>&1 && kwriteconfig6 --file kwinrc --group Plugins --key ohc-charmsEnabled false || true
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$HOME/.local/share/applications" || true
command -v kbuildsycoca6 >/dev/null 2>&1 && kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
echo "Open Hardware Control wurde für diesen Benutzer entfernt."
echo "Programmdateien einer älteren Kraken-Control-Installation wurden nicht gelöscht."
echo "Die udev-Regel wurde nicht entfernt."
