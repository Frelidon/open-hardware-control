#!/usr/bin/env bash
set -euo pipefail
TASK_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
command -v python3 >/dev/null || { echo 'Python 3 fehlt; keine Änderung vorgenommen.' >&2; exit 1; }
if [[ ${1:-} == --check || $EUID -eq 0 ]]; then
 exec python3 "$TASK_DIR/lib/install.py" --distro fedora "$@"
else
 exec sudo python3 "$TASK_DIR/lib/install.py" --distro fedora "$@"
fi
