#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Install only from the distribution package or LACT's documented Fedora COPR.
set -euo pipefail

mode="${1:---check}"
if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
fi

case "${ID:-}" in
    fedora|nobara) family=fedora ;;
    arch|endeavouros|cachyos|manjaro) family=arch ;;
    ubuntu) family=ubuntu ;;
    *) family=manual ;;
esac

version_ok() {
    command -v lact >/dev/null 2>&1 || return 1
    local version
    # LACT 0.10.1 does not implement `lact --version`. Ask the package manager.
    case "$family" in
        fedora) version="$(rpm -q --qf '%{VERSION}\n' lact 2>/dev/null || true)" ;;
        arch) version="$(pacman -Q lact 2>/dev/null | awk '{print $2}' || true)" ;;
        ubuntu) version="$(dpkg-query -W -f='${Version}\n' lact 2>/dev/null || true)" ;;
        *) version="" ;;
    esac
    [[ "$version" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)([-+._].*)?$ ]] || return 1
    [[ "$(printf '%s\n' 0.10.1 "${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.${BASH_REMATCH[3]}" | sort -V | head -n 1)" == 0.10.1 ]]
}

if [[ "$mode" == --check ]]; then
    if version_ok && systemctl is-active --quiet lactd.service; then
        echo "$family"
        exit 0
    fi
    echo "$family"
    exit 10
fi

[[ "$mode" == --install ]] || exit 64
[[ $EUID -eq 0 ]] || { echo 'Administratorrechte erforderlich' >&2; exit 77; }
# A prior attempt may have installed the package successfully but failed before
# activating the daemon. Finish that attempt without touching the COPR again.
if version_ok && ! systemctl is-active --quiet lactd.service; then
    systemctl enable --now lactd.service
    systemctl is-active --quiet lactd.service
    exit $?
fi
case "$family" in
    fedora)
        command -v dnf >/dev/null 2>&1 || exit 69
        dnf -y install dnf-plugins-core
        dnf -y copr enable ilyaz/LACT
        dnf -y install lact
        ;;
    arch)
        pacman -S --needed --noconfirm lact
        ;;
    ubuntu)
        [[ "${VERSION_ID:-}" == 26.04 ]] || {
            echo 'Das geprüfte LACT-Paket ist für Ubuntu 26.04 bestimmt.' >&2
            exit 69
        }
        command -v wget >/dev/null 2>&1 || exit 69
        command -v sha256sum >/dev/null 2>&1 || exit 69
        tmpdir="$(mktemp -d /tmp/ohc-lact-install.XXXXXX)"
        trap 'rm -rf -- "$tmpdir"' EXIT
        package="$tmpdir/lact-0.10.1-0.amd64.ubuntu-2604.deb"
        wget -q \
            'https://github.com/ilya-zlobintsev/LACT/releases/download/v0.10.1/lact-0.10.1-0.amd64.ubuntu-2604.deb' \
            -O "$package"
        printf '%s  %s\n' \
            'b8006a0d7e414de08f193760a82d346c7308675747ae928501941ac714b59fd3' \
            "$package" | sha256sum -c -
        apt-get install -y "$package"
        ;;
    *)
        echo 'Für diese Distribution bitte das offizielle LACT-Paket verwenden.' >&2
        exit 69
        ;;
esac
version_ok || { echo 'LACT 0.10.1 oder neuer wurde nicht installiert.' >&2; exit 65; }
systemctl enable --now lactd.service
systemctl is-active --quiet lactd.service
