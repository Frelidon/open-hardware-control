#!/usr/bin/env bash
set -euo pipefail
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HELPER_SRC="$SOURCE_DIR/ohc_fan_helper.py"
POLICY_SRC="$SOURCE_DIR/io.github.Frelidon.OpenHardwareControl.fan.policy"
[[ -f "$HELPER_SRC" && -f "$POLICY_SRC" ]] || { echo "Fan-Helper-Dateien fehlen." >&2; exit 2; }
sudo install -d -m 0755 /usr/libexec /usr/share/polkit-1/actions
sudo install -o root -g root -m 0755 "$HELPER_SRC" /usr/libexec/open-hardware-control-fan-helper
sudo install -o root -g root -m 0644 "$POLICY_SRC" /usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.fan.policy
echo "OHC-NCT6687-Fan-Helper und Polkit-Regel installiert."
