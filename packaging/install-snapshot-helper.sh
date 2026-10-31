#!/usr/bin/env bash
set -euo pipefail
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SOURCE_DIR/modules/snapshot_manager/v1_0/helper.py" ]]; then
  HELPER_SRC="$SOURCE_DIR/modules/snapshot_manager/v1_0/helper.py"
elif [[ -f "$SOURCE_DIR/../src/modules/snapshot_manager/v1_0/helper.py" ]]; then
  HELPER_SRC="$SOURCE_DIR/../src/modules/snapshot_manager/v1_0/helper.py"
else
  echo "Snapshot-Helper fehlt." >&2
  exit 2
fi
POLICY_SRC="$SOURCE_DIR/io.github.Frelidon.OpenHardwareControl.snapshot.policy"
[[ -f "$POLICY_SRC" ]] || { echo "Snapshot-Polkit-Regel fehlt." >&2; exit 2; }
sudo install -d -m 0755 /usr/libexec /usr/share/polkit-1/actions
sudo install -o root -g root -m 0755 "$HELPER_SRC" /usr/libexec/open-hardware-control-snapshot-helper
sudo install -o root -g root -m 0755 "$HELPER_SRC" /usr/libexec/open-hardware-control-snapshot-admin-helper
sudo install -o root -g root -m 0644 "$POLICY_SRC" /usr/share/polkit-1/actions/io.github.Frelidon.OpenHardwareControl.snapshot.policy
echo "OHC-Snapshot-Helper und Polkit-Regel installiert."
