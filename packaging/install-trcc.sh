#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Install the tested official TRCC Linux package on Ubuntu only.
set -euo pipefail

mode="${1:---check}"
if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
fi

family=manual
if [[ "${ID:-}" == ubuntu ]]; then
    family=ubuntu
fi

dmi_helper_present() {
    local source_dir helper_source policy_source
    source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
    helper_source="$source_dir/ohc_trcc_dmi_helper.py"
    [[ -f "$helper_source" ]] || helper_source="$source_dir/../src/ohc_trcc_dmi_helper.py"
    policy_source="$source_dir/io.github.Frelidon.OpenHardwareControl.dmi.policy"
    [[ -x /usr/libexec/open-hardware-control-dmi-memory-helper ]] &&
    trusted_root_path /usr/libexec/open-hardware-control-dmi-memory-helper &&
    trusted_root_path /usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.dmi.policy &&
    cmp -s -- "$helper_source" /usr/libexec/open-hardware-control-dmi-memory-helper &&
    cmp -s -- "$policy_source" /usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.dmi.policy
}

trusted_root_path() {
    local target="$1" uid permissions
    while :; do
        [[ ! -L "$target" && ( -f "$target" || -d "$target" ) ]] || return 1
        uid="$(stat -c '%u' -- "$target")" || return 1
        permissions="$(stat -c '%a' -- "$target")" || return 1
        [[ "$uid" == 0 ]] && (( (8#$permissions & 022) == 0 )) || return 1
        [[ "$target" == / ]] && return 0
        target="${target%/*}"
        [[ -n "$target" ]] || target=/
    done
}

install_dmi_helper() {
    # Only the fixed RAM-information reader receives a silent Polkit action.
    # Never change TRCC's stock dmidecode grant or authorize its root daemon.
    local source_dir helper_source policy_source
    source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
    helper_source="$source_dir/ohc_trcc_dmi_helper.py"
    [[ -f "$helper_source" ]] || helper_source="$source_dir/../src/ohc_trcc_dmi_helper.py"
    policy_source="$source_dir/io.github.Frelidon.OpenHardwareControl.dmi.policy"
    [[ -f "$helper_source" && -f "$policy_source" ]] || return 65
    # Existing distribution-owned parent modes are never broadened.
    trusted_root_path /usr || return 65
    [[ -d /usr/libexec ]] || install -d -m 0755 /usr/libexec
    trusted_root_path /usr/libexec || return 65
    trusted_root_path /usr/share/polkit-1 || return 65
    [[ -d /usr/share/polkit-1/actions ]] || install -d -m 0755 /usr/share/polkit-1/actions
    trusted_root_path /usr/share/polkit-1/actions || return 65
    [[ ! -L /usr/libexec/open-hardware-control-dmi-memory-helper &&
       ! -L /usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.dmi.policy ]] || return 65
    install -o root -g root -m 0755 "$helper_source" /usr/libexec/open-hardware-control-dmi-memory-helper
    install -o root -g root -m 0644 "$policy_source" /usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.dmi.policy
}

version_ok() {
    command -v trcc >/dev/null 2>&1 || return 1
    local version
    version="$(dpkg-query -W -f='${Version}\n' trcc-linux 2>/dev/null || true)"
    [[ "$version" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)([-+._].*)?$ ]] || return 1
    [[ "$(printf '%s\n' 9.7.5 "${BASH_REMATCH[1]}.${BASH_REMATCH[2]}.${BASH_REMATCH[3]}" | sort -V | head -n 1)" == 9.7.5 ]]
}

udev_rule_present() {
    local directory rule
    # Official DEBs install in /lib, while TRCC's general startup hint checks
    # /etc only. Inspect each standard udev directory without running setup.
    for directory in /etc/udev/rules.d /run/udev/rules.d /usr/local/lib/udev/rules.d /usr/lib/udev/rules.d /lib/udev/rules.d; do
        rule="$directory/99-trcc-lcd.rules"
        [[ -f "$rule" ]] || continue
        grep -Eq '^[^#]*SUBSYSTEM=="usb".*ATTR\{idVendor\}=="87ad".*ATTR\{idProduct\}=="70db".*(MODE=|TAG\+="uaccess")' "$rule" && return 0
    done
    return 1
}

if [[ "$mode" == --check ]]; then
    echo "$family"
    version_ok && udev_rule_present && dmi_helper_present && exit 0
    exit 10
fi

[[ "$mode" == --install ]] || exit 64
[[ $EUID -eq 0 ]] || { echo 'Administratorrechte erforderlich' >&2; exit 77; }
[[ "$family" == ubuntu ]] || { echo 'Dieser Helfer installiert TRCC nur auf Ubuntu.' >&2; exit 69; }
install_dmi_helper
# An existing verified package needs only the OHC metadata adapter; no
# redundant download, reinstall or upstream host-wide setup is necessary.
version_ok && udev_rule_present && exit 0
command -v wget >/dev/null 2>&1 || { echo 'wget fehlt.' >&2; exit 69; }
command -v sha256sum >/dev/null 2>&1 || { echo 'sha256sum fehlt.' >&2; exit 69; }

tmpdir="$(mktemp -d /tmp/ohc-trcc-install.XXXXXX)"
trap 'rm -rf -- "$tmpdir"' EXIT
package="$tmpdir/trcc-linux_9.10.4-1_all.deb"
url="https://github.com/Lexonight1/thermalright-trcc-linux/releases/download/v9.10.4/trcc-linux_9.10.4-1_all.deb"
digest="bc25685024e7cfafb6a8be9b13a83ac384c3da21443beffc9fc1a2018b558e8c"
wget -q "$url" -O "$package"
printf '%s  %s\n' "$digest" "$package" | sha256sum -c -
apt-get install -y "$package"
version_ok
udev_rule_present || { echo 'Die offizielle TRCC-USB-Zugriffsregel für 87ad:70db fehlt.' >&2; exit 65; }
