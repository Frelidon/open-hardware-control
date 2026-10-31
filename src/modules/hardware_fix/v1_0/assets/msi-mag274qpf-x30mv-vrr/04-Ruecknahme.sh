#!/usr/bin/env bash
set -euo pipefail
TASK_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if [[ $# -ne 1 ]]; then
  echo 'Aufruf: bash 04-Ruecknahme.sh /var/backups/msi-vrr-recovery/DEIN-SICHERUNGSORDNER' >&2
  echo 'Den Sicherungsordner zeigt das Installationsskript an.' >&2
  exit 1
fi
case "$1" in
  /var/backups/msi-vrr-recovery/*) ;;
  *) echo 'Bitte einen Sicherungsordner unter /var/backups/msi-vrr-recovery angeben.' >&2; exit 1 ;;
esac
if [[ $EUID -eq 0 ]]; then
  exec python3 "$TASK_DIR/lib/install.py" --restore "$1"
else
  exec sudo python3 "$TASK_DIR/lib/install.py" --restore "$1"
fi
