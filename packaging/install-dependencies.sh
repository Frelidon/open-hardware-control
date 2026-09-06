#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail

MODE="${1:---check-and-install}"
PKEXEC_BIN="$(command -v pkexec || true)"

declare -a missing_keys=()
declare -a missing_labels=()
declare -a missing_packages=()

if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
fi

DISTRO_ID="${ID:-unknown}"
PACKAGE_FAMILY="unknown"
PACKAGE_MANAGER=""

if command -v dnf >/dev/null 2>&1; then
    PACKAGE_FAMILY="dnf"
    PACKAGE_MANAGER="$(command -v dnf)"
elif command -v apt-get >/dev/null 2>&1; then
    PACKAGE_FAMILY="apt"
    PACKAGE_MANAGER="$(command -v apt-get)"
elif command -v pacman >/dev/null 2>&1; then
    PACKAGE_FAMILY="pacman"
    PACKAGE_MANAGER="$(command -v pacman)"
elif command -v zypper >/dev/null 2>&1; then
    PACKAGE_FAMILY="zypper"
    PACKAGE_MANAGER="$(command -v zypper)"
fi

package_for() {
    local key="$1"
    case "$PACKAGE_FAMILY:$key" in
        dnf:liquidctl) echo "liquidctl" ;;
        dnf:pyside6) echo "python3-pyside6" ;;
        dnf:pyside6network) echo "python3-pyside6" ;;
        dnf:pyside6dbus) echo "python3-pyside6" ;;
        dnf:qtsvg) echo "qt6-qtsvg" ;;
        dnf:pillow) echo "python3-pillow" ;;
        dnf:kconfig6) echo "kf6-kconfig" ;;
        dnf:qdbus6) echo "qt6-qttools" ;;
        dnf:openrgb) echo "openrgb" ;;
        dnf:openrgb_udev) echo "openrgb-udev-rules" ;;
        dnf:polkit) echo "polkit" ;;
        apt:liquidctl) echo "liquidctl" ;;
        apt:pyside6) echo "python3-pyside6.qtwidgets" ;;
        apt:pyside6network) echo "python3-pyside6.qtnetwork" ;;
        apt:pyside6dbus) echo "python3-pyside6.qtdbus" ;;
        apt:qtsvg) echo "python3-pyside6.qtsvg" ;;
        apt:pillow) echo "python3-pil" ;;
        apt:kconfig6) echo "libkf6config-bin" ;;
        apt:qdbus6) echo "qdbus-qt6" ;;
        apt:polkit) echo "policykit-1" ;;
        apt:openrgb) echo "openrgb" ;;
        pacman:liquidctl) echo "liquidctl" ;;
        pacman:pyside6) echo "pyside6" ;;
        pacman:pyside6network) echo "pyside6" ;;
        pacman:pyside6dbus) echo "pyside6" ;;
        pacman:qtsvg) echo "qt6-svg" ;;
        pacman:pillow) echo "python-pillow" ;;
        pacman:kconfig6) echo "kconfig" ;;
        pacman:qdbus6) echo "qt6-tools" ;;
        pacman:polkit) echo "polkit" ;;
        pacman:openrgb) echo "openrgb" ;;
        zypper:liquidctl) echo "liquidctl" ;;
        zypper:pyside6) echo "python3-pyside6" ;;
        zypper:pyside6network) echo "python3-pyside6" ;;
        zypper:pyside6dbus) echo "python3-pyside6" ;;
        zypper:qtsvg) echo "libQt6Svg6" ;;
        zypper:pillow) echo "python3-Pillow" ;;
        zypper:kconfig6) echo "kf6-kconfig" ;;
        zypper:qdbus6) echo "qt6-tools-qdbus" ;;
        zypper:polkit) echo "polkit" ;;
        zypper:openrgb) echo "openrgb" ;;
        *) return 1 ;;
    esac
}

add_missing() {
    local key="$1"
    local label="$2"
    local package
    package="$(package_for "$key" 2>/dev/null || true)"
    missing_keys+=("$key")
    missing_labels+=("$label")
    [[ -n "$package" ]] && missing_packages+=("$package")
}

qdbus6_available() {
    command -v qdbus6 >/dev/null 2>&1 ||
        command -v qdbus-qt6 >/dev/null 2>&1 ||
        [[ -x /usr/lib64/qt6/bin/qdbus ]] ||
        [[ -x /usr/lib/qt6/bin/qdbus ]]
}

CHECK_GUI_ONLY=false
CHECK_DESKTOP_ONLY=false
CHECK_OPENRGB_ONLY=false
case "$MODE" in
    --check-gui-and-install) CHECK_GUI_ONLY=true ;;
    --check-desktop|--install-desktop|--check-desktop-and-install) CHECK_DESKTOP_ONLY=true ;;
    --check-openrgb|--install-openrgb|--check-openrgb-and-install) CHECK_OPENRGB_ONLY=true ;;
esac

if [[ "$CHECK_OPENRGB_ONLY" == true ]]; then
    command -v openrgb >/dev/null 2>&1 || command -v OpenRGB >/dev/null 2>&1 || add_missing "openrgb" "OpenRGB mit lokalem SDK-Server"
    if [[ "$PACKAGE_FAMILY" == "dnf" ]] && ! rpm -q openrgb-udev-rules >/dev/null 2>&1; then
        add_missing "openrgb_udev" "OpenRGB-udev-Regeln für Benutzerzugriff"
    fi
elif [[ "$CHECK_DESKTOP_ONLY" == true ]]; then
    command -v kwriteconfig6 >/dev/null 2>&1 || add_missing "kconfig6" "kwriteconfig6 / KDE Frameworks 6 KConfig"
    qdbus6_available || add_missing "qdbus6" "Qt-6-D-Bus-Werkzeug (qdbus)"
    python3 -c 'from PySide6.QtNetwork import QLocalServer' >/dev/null 2>&1 || add_missing "pyside6network" "PySide6 QtNetwork für die lokale Kachelübersicht"
    python3 -c 'from PySide6.QtDBus import QDBusConnection' >/dev/null 2>&1 || add_missing "pyside6dbus" "PySide6 QtDBus für die Charms-Leiste"
elif [[ "$CHECK_GUI_ONLY" == true ]]; then
    python3 -c 'import PySide6' >/dev/null 2>&1 || add_missing "pyside6" "PySide6 / Qt for Python"
    python3 -c 'from PySide6.QtGui import QImageReader; assert any(bytes(x).lower() == b"svg" for x in QImageReader.supportedImageFormats())' >/dev/null 2>&1 || add_missing "qtsvg" "Qt-SVG-Unterstützung"
else
    command -v liquidctl >/dev/null 2>&1 || add_missing "liquidctl" "liquidctl"
    python3 -c 'import PySide6' >/dev/null 2>&1 || add_missing "pyside6" "PySide6 / Qt for Python"
    python3 -c 'from PySide6.QtGui import QImageReader; assert any(bytes(x).lower() == b"svg" for x in QImageReader.supportedImageFormats())' >/dev/null 2>&1 || add_missing "qtsvg" "Qt-SVG-Unterstützung"
    python3 -c 'from PIL import Image' >/dev/null 2>&1 || add_missing "pillow" "Pillow"
fi

if (( ${#missing_keys[@]} == 0 )); then
    echo "Alle benötigten Abhängigkeiten sind installiert."
    exit 0
fi

if [[ -z "$PKEXEC_BIN" ]] && ! command -v sudo >/dev/null 2>&1; then
    missing_packages+=("$(package_for polkit 2>/dev/null || true)")
fi

mapfile -t missing_packages < <(printf '%s\n' "${missing_packages[@]}" | sed '/^$/d' | awk '!seen[$0]++')
label_list="$(printf '%s\n' "${missing_labels[@]}" | sed 's/^/• /')"
package_list="${missing_packages[*]}"

case "$PACKAGE_FAMILY" in
    dnf) manual_command="sudo dnf install ${package_list}" ;;
    apt) manual_command="sudo apt update && sudo apt install ${package_list}" ;;
    pacman) manual_command="sudo pacman -S --needed ${package_list}" ;;
    zypper) manual_command="sudo zypper install ${package_list}" ;;
    *) manual_command="Siehe INSTALL.md für die manuelle Installation." ;;
esac

show_error() {
    local message="$1"
    if command -v kdialog >/dev/null 2>&1; then
        kdialog --title "Open Hardware Control by Frelidon" --error "$message" || true
    elif command -v zenity >/dev/null 2>&1; then
        zenity --error --title="Open Hardware Control by Frelidon" --text="$message" || true
    else
        printf '%b\n' "$message" >&2
    fi
}

ask_confirmation() {
    local purpose="für das NZXT-Modul"
    [[ "$MODE" == "--check-gui-and-install" ]] && purpose="für die grafische Oberfläche"
    [[ "$CHECK_DESKTOP_ONLY" == true ]] && purpose="für die KDE-Plasma-Desktop-Designs"
    [[ "$CHECK_OPENRGB_ONLY" == true ]] && purpose="für das optionale RGB-Studio"
    local message="Open Hardware Control benötigt ${purpose} folgende Pakete:\n\n${label_list}\n\nDistribution: ${DISTRO_ID} (${PACKAGE_FAMILY})\nEs werden nur die bereits eingerichteten Paketquellen verwendet. Es werden keine fremden Paketquellen hinzugefügt.\n\nFortfahren?"
    if command -v kdialog >/dev/null 2>&1; then
        kdialog --title "Abhängigkeiten installieren" --yesno "$message"
        return $?
    fi
    if command -v zenity >/dev/null 2>&1; then
        zenity --question --title="Abhängigkeiten installieren" --text="$message"
        return $?
    fi
    if [[ -t 0 ]]; then
        printf 'Fehlende Abhängigkeiten:\n%s\n\nInstallieren? [j/N] ' "$label_list"
        read -r answer
        [[ "$answer" =~ ^[JjYy]$ ]]
        return $?
    fi
    show_error "Fehlende Abhängigkeiten:\n\n${label_list}\n\nStarte im Terminal:\n${manual_command}"
    return 1
}

if [[ "$MODE" == "--check" || "$MODE" == "--check-desktop" || "$MODE" == "--check-openrgb" ]]; then
    printf '%s\n' "${missing_packages[@]}"
    exit 10
fi

if [[ "$PACKAGE_FAMILY" == "unknown" || -z "$PACKAGE_MANAGER" || ${#missing_packages[@]} -eq 0 ]]; then
    show_error "Die Distribution wurde nicht eindeutig erkannt.\n\nFehlende Komponenten:\n${label_list}\n\nSiehe INSTALL.md für die manuelle Installation."
    exit 2
fi

if [[ "$MODE" == "--check-and-install" || "$MODE" == "--check-gui-and-install" || "$MODE" == "--check-desktop-and-install" || "$MODE" == "--check-openrgb-and-install" ]]; then
    if ! ask_confirmation; then
        echo "Installation abgebrochen."
        exit 20
    fi
elif [[ "$MODE" != "--install" && "$MODE" != "--install-desktop" && "$MODE" != "--install-openrgb" ]]; then
    echo "Unbekannter Modus: $MODE" >&2
    exit 64
fi

declare -a install_command=()
case "$PACKAGE_FAMILY" in
    dnf) install_command=("$PACKAGE_MANAGER" install -y "${missing_packages[@]}") ;;
    apt) install_command=("$PACKAGE_MANAGER" install -y "${missing_packages[@]}") ;;
    pacman) install_command=("$PACKAGE_MANAGER" -S --needed --noconfirm "${missing_packages[@]}") ;;
    zypper) install_command=("$PACKAGE_MANAGER" --non-interactive install "${missing_packages[@]}") ;;
esac

if [[ $EUID -eq 0 ]]; then
    "${install_command[@]}"
elif [[ -n "$PKEXEC_BIN" ]]; then
    "$PKEXEC_BIN" "${install_command[@]}"
elif command -v sudo >/dev/null 2>&1 && [[ -t 0 ]]; then
    sudo "${install_command[@]}"
else
    show_error "Für die Administratorabfrage wurde weder pkexec noch ein interaktives sudo gefunden.\n\nInstalliere manuell:\n${manual_command}"
    exit 3
fi

remaining=()
if [[ "$CHECK_OPENRGB_ONLY" == true ]]; then
    command -v openrgb >/dev/null 2>&1 || command -v OpenRGB >/dev/null 2>&1 || remaining+=("OpenRGB")
    if [[ "$PACKAGE_FAMILY" == "dnf" ]] && ! rpm -q openrgb-udev-rules >/dev/null 2>&1; then
        remaining+=("openrgb-udev-rules")
    fi
elif [[ "$CHECK_DESKTOP_ONLY" == true ]]; then
    command -v kwriteconfig6 >/dev/null 2>&1 || remaining+=("kwriteconfig6")
    qdbus6_available || remaining+=("qdbus (Qt 6)")
    python3 -c 'from PySide6.QtNetwork import QLocalServer' >/dev/null 2>&1 || remaining+=("PySide6 QtNetwork")
    python3 -c 'from PySide6.QtDBus import QDBusConnection' >/dev/null 2>&1 || remaining+=("PySide6 QtDBus")
elif [[ "$CHECK_GUI_ONLY" == true ]]; then
    python3 -c 'import PySide6' >/dev/null 2>&1 || remaining+=("PySide6")
    python3 -c 'from PySide6.QtGui import QImageReader; assert any(bytes(x).lower() == b"svg" for x in QImageReader.supportedImageFormats())' >/dev/null 2>&1 || remaining+=("Qt SVG")
else
    command -v liquidctl >/dev/null 2>&1 || remaining+=("liquidctl")
    python3 -c 'import PySide6' >/dev/null 2>&1 || remaining+=("PySide6")
    python3 -c 'from PySide6.QtGui import QImageReader; assert any(bytes(x).lower() == b"svg" for x in QImageReader.supportedImageFormats())' >/dev/null 2>&1 || remaining+=("Qt SVG")
    python3 -c 'from PIL import Image' >/dev/null 2>&1 || remaining+=("Pillow")
fi

if (( ${#remaining[@]} > 0 )); then
    echo "Nach der Installation weiterhin nicht erkannt: ${remaining[*]}" >&2
    echo "Prüfe die distributionsspezifischen Hinweise in INSTALL.md." >&2
    exit 4
fi

echo "Alle benötigten Abhängigkeiten wurden installiert."
