#!/usr/bin/env bash
set -u

OUT="${1:-$PWD/open-hardware-control-diagnostics-$(date +%Y%m%d-%H%M%S).txt}"
SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

{
  echo "Open Hardware Control by Frelidon diagnostics"
  echo "Version: 3.4.21 INTERN"
  echo "Generated: $(date --iso-8601=seconds 2>/dev/null || date)"
  echo "Mode: diagnostics are read-only (application controls require explicit session approval)"
  echo
  echo "== System =="
  if [ -r /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    echo "Operating system: ${PRETTY_NAME:-unknown}"
  fi
  echo "Kernel: $(uname -s) $(uname -r)"
  echo "Architecture: $(uname -m)"
  echo "Desktop: ${XDG_CURRENT_DESKTOP:-unknown}"
  echo "Session type: ${XDG_SESSION_TYPE:-unknown}"
  echo
  echo "== Software =="
  python3 --version 2>&1
  liquidctl --version 2>&1 || true
  echo
  echo "== OpenRGB installation and process ownership =="
  if command -v openrgb >/dev/null 2>&1; then
    echo "Executable: $(command -v openrgb)"
    if command -v rpm >/dev/null 2>&1; then
      rpm -q openrgb 2>&1 || true
    elif command -v dpkg-query >/dev/null 2>&1; then
      dpkg-query -W -f='Package: ${Package} ${Version}\n' openrgb 2>&1 || true
    fi
  else
    echo "Executable: not installed"
  fi
  OPENRGB_PIDS="$({ pgrep -x openrgb 2>/dev/null || true; pgrep -x OpenRGB 2>/dev/null || true; } | sort -nu)"
  if [ -n "$OPENRGB_PIDS" ]; then
    for OPENRGB_PID in $OPENRGB_PIDS; do
      OPENRGB_PPID="$(ps -o ppid= -p "$OPENRGB_PID" 2>/dev/null | tr -d ' ' || true)"
      echo "-- OpenRGB process --"
      ps -o pid=,ppid=,comm=,args= -p "$OPENRGB_PID" 2>&1 || true
      if [ -n "$OPENRGB_PPID" ]; then
        echo "-- Parent process (determines OHC-managed vs external) --"
        ps -o pid=,ppid=,comm=,args= -p "$OPENRGB_PPID" 2>&1 || true
      fi
    done
  else
    echo "Running process: none"
  fi
  echo "-- Listener on local SDK port 6742 --"
  ss -ltnp 'sport = :6742' 2>&1 || true
  echo
  echo "== liquidctl devices (read-only) =="
  liquidctl list --verbose 2>&1 || true
  echo
  echo "== liquidctl status (read-only) =="
  liquidctl status 2>&1 || true
  echo
  echo "== NZXT USB devices =="
  lsusb 2>&1 | grep -i -E '1e71|NZXT' || true
  echo
  echo "== Relevant hidraw permissions =="
  for dev in /dev/hidraw*; do
    [ -e "$dev" ] || continue
    props="$(udevadm info -q property -n "$dev" 2>/dev/null || true)"
    if grep -qi -E 'ID_VENDOR_ID=1e71|NZXT' <<<"$props"; then
      stat -c '%A %U %G %n' "$dev" 2>/dev/null || true
      printf '%s\n' "$props" | grep -E '^(ID_VENDOR|ID_MODEL|ID_VENDOR_ID|ID_MODEL_ID)=' || true
    fi
  done
  echo
  echo "== udev rule =="
  cat /etc/udev/rules.d/71-nzxt-kraken-2023.rules 2>&1 || true
  echo
  echo "== OpenLinkHub local status (read-only, serial suffix only) =="
  python3 "$SOURCE_DIR/openlinkhub_integration.py" --status 2>&1 || true
  echo
  echo "== Open Hardware Control startup/crash logs =="
  STATE_ROOT="${XDG_STATE_HOME:-$HOME/.local/state}/open-hardware-control"
  if [ -r "$STATE_ROOT/startup.log" ]; then
    echo "-- startup.log (last 120 lines) --"
    tail -n 120 "$STATE_ROOT/startup.log" 2>&1 || true
  else
    echo "startup.log: not present"
  fi
  if [ -r "$STATE_ROOT/last-crash.log" ]; then
    echo "-- last-crash.log --"
    cat "$STATE_ROOT/last-crash.log" 2>&1 || true
  else
    echo "last-crash.log: not present"
  fi
  for SESSION_LOG in session.log previous-session.log; do
    if [ -r "$STATE_ROOT/$SESSION_LOG" ]; then
      echo "-- $SESSION_LOG (last 400 lines) --"
      tail -n 400 "$STATE_ROOT/$SESSION_LOG" 2>&1 || true
    else
      echo "$SESSION_LOG: not present"
    fi
  done
  echo
  echo "== Latest OpenRGB coredump metadata =="
  coredumpctl info --no-pager openrgb 2>&1 | tail -n 180 || true
  echo
  echo "== Current user journal RGB excerpts =="
  journalctl --user -b --no-pager 2>&1 \
    | grep -Ei 'openrgb|open.hardware.control|rgb-studio|rgb-engine' \
    | tail -n 300 || true
} > "$TMP" 2>&1

# Defense in depth: remove common personal and device identifiers even when a
# future liquidctl/udev version adds them to otherwise harmless output.
sed -E \
  -e 's/(Serial number:).*/\1 [REDACTED]/I' \
  -e 's/(ID_SERIAL(_SHORT)?=).*/\1[REDACTED]/I' \
  -e 's/(serial=)[^ ]+/\1[REDACTED]/Ig' \
  -e 's#(/home/)[^/[:space:]]+#\1[USER]#g' \
  -e 's#(/run/user/)[0-9]+#\1[UID]#g' \
  -e 's/(Machine ID|Boot ID|machine-id|boot-id)([=: ]+)[0-9a-f-]+/\1\2[REDACTED]/Ig' \
  -e 's/(Hostname|Static hostname)([=: ]+).*/\1\2[REDACTED]/Ig' \
  -e 's/(USER|USERNAME|LOGNAME)=.*/\1=[REDACTED]/g' \
  "$TMP" > "$OUT.tmp"
python3 - "$OUT.tmp" "$OUT" <<'PY_REDACT'
import re, sys
from pathlib import Path
src, dst = map(Path, sys.argv[1:3])
text = src.read_text(encoding="utf-8", errors="replace")
text = re.sub(r"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b", "[MAC]", text)
ipv4 = re.compile(r"(?<![0-9])(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![0-9])")
def repl(m):
    value=m.group(0)
    before=m.string[max(0,m.start()-32):m.start()].casefold()
    after=m.string[m.end():m.end()+20].casefold()
    if re.search(r"(?:version|v|release|build|open hardware control|ohc)\s*$", before) or re.match(r"\s*(?:intern|stable|alpha|beta|rc)\b", after): return value
    o=tuple(map(int,value.split('.')))
    if o[0] == 127 or o[:3] in {(192,0,2),(198,51,100),(203,0,113)}: return value
    return "[IP]"
text = ipv4.sub(repl, text)
text = re.sub(r"(?i)(?<![0-9a-f:])(?:[0-9a-f]{0,4}:){3,7}[0-9a-f]{0,4}(?![0-9a-f:])", lambda m: m.group(0) if m.group(0)=="::1" else "[IPv6]", text)
text = re.sub(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[EMAIL]", text)
dst.write_text(text, encoding="utf-8")
src.unlink(missing_ok=True)
PY_REDACT
chmod 0600 "$OUT"
echo "Anonymisierter, rein lesender Diagnosebericht erstellt: $OUT"
echo "Bitte den Bericht vor dem Teilen trotzdem kurz kontrollieren."
