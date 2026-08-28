#!/usr/bin/env bash
set -euo pipefail

OHC_INSTALL_HOME="${OHC_INSTALL_HOME:-${HOME:?Benutzerverzeichnis nicht gesetzt}}"
APP_DIR="$OHC_INSTALL_HOME/.local/share/open-hardware-control"
BIN_DIR="$OHC_INSTALL_HOME/.local/bin"
DESKTOP_DIR="$OHC_INSTALL_HOME/.local/share/applications"
ICON_DIR="$OHC_INSTALL_HOME/.local/share/icons/hicolor/scalable/apps"
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$APP_DIR" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR"
install -m 0755 "$SOURCE_DIR/kraken_control.py" "$APP_DIR/kraken_control.py"
install -m 0644 "$SOURCE_DIR/app_constants.py" "$APP_DIR/app_constants.py"
install -m 0644 "$SOURCE_DIR/command_backend.py" "$APP_DIR/command_backend.py"
install -m 0644 "$SOURCE_DIR/cooling_widgets.py" "$APP_DIR/cooling_widgets.py"
install -m 0644 "$SOURCE_DIR/localization_catalog.py" "$APP_DIR/localization_catalog.py"
install -m 0644 "$SOURCE_DIR/privacy_logging.py" "$APP_DIR/privacy_logging.py"
install -m 0644 "$SOURCE_DIR/temperature_utils.py" "$APP_DIR/temperature_utils.py"
install -m 0755 "$SOURCE_DIR/openlinkhub_integration.py" "$APP_DIR/openlinkhub_integration.py"
install -m 0644 "$SOURCE_DIR/openlinkhub_mouse_visuals.py" "$APP_DIR/openlinkhub_mouse_visuals.py"
install -m 0644 "$SOURCE_DIR/openrgb_integration.py" "$APP_DIR/openrgb_integration.py"
install -m 0755 "$SOURCE_DIR/openrgb_sdk.py" "$APP_DIR/openrgb_sdk.py"
install -m 0644 "$SOURCE_DIR/rgb_devices.py" "$APP_DIR/rgb_devices.py"
install -m 0644 "$SOURCE_DIR/rgb_effects.py" "$APP_DIR/rgb_effects.py"
install -m 0644 "$SOURCE_DIR/ui_layout.py" "$APP_DIR/ui_layout.py"
install -m 0644 "$SOURCE_DIR/nzxt_rgb.py" "$APP_DIR/nzxt_rgb.py"
install -m 0644 "$SOURCE_DIR/desktop_designs.py" "$APP_DIR/desktop_designs.py"
install -m 0644 "$SOURCE_DIR/desktop_assets.py" "$APP_DIR/desktop_assets.py"
install -m 0755 "$SOURCE_DIR/desktop_shell.py" "$APP_DIR/desktop_shell.py"
install -m 0644 "$SOURCE_DIR/kraken_lcd_designs.py" "$APP_DIR/kraken_lcd_designs.py"
install -m 0644 "$SOURCE_DIR/kraken_sensors.py" "$APP_DIR/kraken_sensors.py"
install -m 0644 "$SOURCE_DIR/nzxt_backend.py" "$APP_DIR/nzxt_backend.py"
install -m 0644 "$SOURCE_DIR/nzxt_esc_profiles.py" "$APP_DIR/nzxt_esc_profiles.py"
install -m 0644 "$SOURCE_DIR/hardware_request_coordinator.py" "$APP_DIR/hardware_request_coordinator.py"
install -m 0644 "$SOURCE_DIR/mainboard_fan_control.py" "$APP_DIR/mainboard_fan_control.py"
install -m 0644 "$SOURCE_DIR/cooling_ownership.py" "$APP_DIR/cooling_ownership.py"
install -m 0755 "$SOURCE_DIR/ohc_fan_helper.py" "$APP_DIR/ohc_fan_helper.py"
install -m 0644 "$SOURCE_DIR/io.github.Frelidon.OpenHardwareControl.fan.policy" "$APP_DIR/io.github.Frelidon.OpenHardwareControl.fan.policy"
install -m 0755 "$SOURCE_DIR/install-fan-helper.sh" "$APP_DIR/install-fan-helper.sh"
install -m 0755 "$SOURCE_DIR/kraken_cam_streamer.py" "$APP_DIR/kraken_cam_streamer.py"
install -m 0644 "$SOURCE_DIR/kraken-control.svg" "$APP_DIR/kraken-control.svg"
install -m 0644 "$SOURCE_DIR/kraken-control.svg" "$ICON_DIR/open-hardware-control.svg"
install -m 0755 "$SOURCE_DIR/collect-diagnostics.sh" "$APP_DIR/collect-diagnostics.sh"
install -m 0755 "$SOURCE_DIR/install-udev-rule.sh" "$APP_DIR/install-udev-rule.sh"
install -m 0755 "$SOURCE_DIR/install-dependencies.sh" "$APP_DIR/install-dependencies.sh"
install -m 0644 "$SOURCE_DIR/71-nzxt-kraken-2023.rules" "$APP_DIR/71-nzxt-kraken-2023.rules"
install -m 0644 "$SOURCE_DIR/LICENSE" "$APP_DIR/LICENSE"
install -m 0644 "$SOURCE_DIR/VERSION" "$APP_DIR/VERSION"
install -m 0644 "$SOURCE_DIR/BUILD_CHANNEL" "$APP_DIR/BUILD_CHANNEL"
install -m 0644 "$SOURCE_DIR/SUPPORTED_DEVICES.md" "$APP_DIR/SUPPORTED_DEVICES.md"
install -m 0644 "$SOURCE_DIR/SECURITY.md" "$APP_DIR/SECURITY.md"
install -m 0644 "$SOURCE_DIR/SECURITY_SCAN_REPORT.json" "$APP_DIR/SECURITY_SCAN_REPORT.json"
install -m 0644 "$SOURCE_DIR/README.md" "$APP_DIR/README.md"
install -m 0644 "$SOURCE_DIR/INSTALL.md" "$APP_DIR/INSTALL.md"
install -m 0644 "$SOURCE_DIR/CHANGELOG.md" "$APP_DIR/CHANGELOG.md"
install -m 0644 "$SOURCE_DIR/README.en.md" "$APP_DIR/README.en.md"
install -m 0644 "$SOURCE_DIR/SOFTWARE_AND_LINKS.md" "$APP_DIR/SOFTWARE_AND_LINKS.md"
install -m 0644 "$SOURCE_DIR/SOFTWARE_AND_LINKS.en.md" "$APP_DIR/SOFTWARE_AND_LINKS.en.md"
install -m 0644 "$SOURCE_DIR/SUPPORTED_DEVICES.en.md" "$APP_DIR/SUPPORTED_DEVICES.en.md"
install -m 0644 "$SOURCE_DIR/PROJECT_SCOPE.md" "$APP_DIR/PROJECT_SCOPE.md"
install -m 0644 "$SOURCE_DIR/PROJECT_SCOPE.en.md" "$APP_DIR/PROJECT_SCOPE.en.md"
install -m 0644 "$SOURCE_DIR/CPU_PROFILES.md" "$APP_DIR/CPU_PROFILES.md"
install -m 0644 "$SOURCE_DIR/CPU_PROFILES.en.md" "$APP_DIR/CPU_PROFILES.en.md"
install -m 0644 "$SOURCE_DIR/COMPONENT_VERSIONS.md" "$APP_DIR/COMPONENT_VERSIONS.md"
install -m 0644 "$SOURCE_DIR/ANIMATED_BACKGROUNDS.md" "$APP_DIR/ANIMATED_BACKGROUNDS.md"
install -m 0644 "$SOURCE_DIR/PROFILES.md" "$APP_DIR/PROFILES.md"
install -m 0644 "$SOURCE_DIR/FEATURES_BY_VERSION.md" "$APP_DIR/FEATURES_BY_VERSION.md"
install -m 0644 "$SOURCE_DIR/SOURCE_CODE.md" "$APP_DIR/SOURCE_CODE.md"
install -m 0644 "$SOURCE_DIR/Kraken_Control_Projekt.md" "$APP_DIR/Kraken_Control_Projekt.md"
install -m 0644 "$SOURCE_DIR/Open_Hardware_Control_Projekt.md" "$APP_DIR/Open_Hardware_Control_Projekt.md"
install -m 0644 "$SOURCE_DIR/OPENLINKHUB_INTEGRATION.md" "$APP_DIR/OPENLINKHUB_INTEGRATION.md"
install -m 0644 "$SOURCE_DIR/RGB_STUDIO.md" "$APP_DIR/RGB_STUDIO.md"
install -m 0644 "$SOURCE_DIR/RGB_SECURITY_AUDIT.md" "$APP_DIR/RGB_SECURITY_AUDIT.md"
install -m 0644 "$SOURCE_DIR/DESKTOP_DESIGNS.md" "$APP_DIR/DESKTOP_DESIGNS.md"
install -m 0644 "$SOURCE_DIR/DESKTOP_SECURITY_AUDIT.md" "$APP_DIR/DESKTOP_SECURITY_AUDIT.md"
install -m 0644 "$SOURCE_DIR/THIRD_PARTY_NOTICES.md" "$APP_DIR/THIRD_PARTY_NOTICES.md"
install -m 0644 "$SOURCE_DIR/DEVELOPER_PACKAGE.md" "$APP_DIR/DEVELOPER_PACKAGE.md"
install -m 0644 "$SOURCE_DIR/USB_CAPTURE_FINDINGS.md" "$APP_DIR/USB_CAPTURE_FINDINGS.md"
if [[ -d "$SOURCE_DIR/test-gifs" ]]; then
  rm -rf "$APP_DIR/test-gifs"
  mkdir -p "$APP_DIR/test-gifs"
  cp -a "$SOURCE_DIR/test-gifs/." "$APP_DIR/test-gifs/"
fi
if [[ -d "$SOURCE_DIR/assets" ]]; then
  rm -rf "$APP_DIR/assets"
  mkdir -p "$APP_DIR/assets"
  cp -a "$SOURCE_DIR/assets/." "$APP_DIR/assets/"
fi

cat > "$BIN_DIR/open-hardware-control" <<LAUNCHER
#!/usr/bin/env bash
"$APP_DIR/install-dependencies.sh" --check-gui-and-install || exit \$?
exec python3 "$APP_DIR/kraken_control.py" "\$@"
LAUNCHER
chmod 0755 "$BIN_DIR/open-hardware-control"

cat > "$BIN_DIR/open-hardware-control-diagnostics" <<LAUNCHER
#!/usr/bin/env bash
exec "$APP_DIR/collect-diagnostics.sh" "\$@"
LAUNCHER
chmod 0755 "$BIN_DIR/open-hardware-control-diagnostics"

cat > "$BIN_DIR/open-hardware-control-desktop-shell" <<LAUNCHER
#!/usr/bin/env bash
exec python3 "$APP_DIR/desktop_shell.py" "\$@"
LAUNCHER
chmod 0755 "$BIN_DIR/open-hardware-control-desktop-shell"

# Compatibility launcher for existing scripts and an older autostart entry.
cat > "$BIN_DIR/kraken-control" <<LAUNCHER
#!/usr/bin/env bash
exec "$BIN_DIR/open-hardware-control" "\$@"
LAUNCHER
chmod 0755 "$BIN_DIR/kraken-control"

sed -e "s|@EXEC@|$BIN_DIR/open-hardware-control|g" \
    -e "s|@ICON@|$APP_DIR/kraken-control.svg|g" \
    "$SOURCE_DIR/kraken-control.desktop.in" > "$DESKTOP_DIR/open-hardware-control.desktop"
chmod 0644 "$DESKTOP_DIR/open-hardware-control.desktop"
rm -f "$DESKTOP_DIR/kraken-control.desktop"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$DESKTOP_DIR" || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f "$OHC_INSTALL_HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true

# KDE/Plasma liest Desktop-Dateien und Symbole teilweise aus einem Cache.
command -v kbuildsycoca6 >/dev/null 2>&1 && kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
command -v kbuildsycoca5 >/dev/null 2>&1 && kbuildsycoca5 --noincremental >/dev/null 2>&1 || true

echo
INSTALL_VERSION="$(tr -d '\r\n' < "$SOURCE_DIR/VERSION" 2>/dev/null || printf 'unbekannt')"
INSTALL_CHANNEL="$(tr -d '\r\n' < "$SOURCE_DIR/BUILD_CHANNEL" 2>/dev/null || printf 'INTERN')"
echo "Open Hardware Control by Frelidon ${INSTALL_VERSION} ${INSTALL_CHANNEL} wurde installiert."
echo "Start im Terminal: $BIN_DIR/open-hardware-control"
echo "Diagnosebericht: $BIN_DIR/open-hardware-control-diagnostics"
echo "Oder im Anwendungsmenü nach 'Open Hardware Control by Frelidon' suchen."
echo
echo "Fehlende Abhängigkeiten werden in der App geprüft und können dort nach Bestätigung installiert werden."
echo "Die Abhängigkeitsprüfung unterstützt Fedora/Nobara, Debian/Ubuntu/Mint, Arch/Manjaro/EndeavourOS und openSUSE."
echo
echo "Bei Kraken-Schreibfehlern: $APP_DIR/install-udev-rule.sh"
echo "Für geschützte NCT6687-Mainboard-PWM-Steuerung bei ZIP/Benutzerinstallation: $APP_DIR/install-fan-helper.sh"
