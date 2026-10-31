#!/usr/bin/env python3
# MSI VRR Ubuntu automation, version 1.
import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
from auto_vrr import UUID, Switch, native_games, save
from x11_games import GameWindows

UNIT_NAME = 'msi-vrr-games.service'
PROGRAMS = ('auto_vrr.py', 'x11_games.py', 'vrr_hardware.py')
MARKER = '# MSI VRR Ubuntu automation, version 1.'

def run(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout.strip()

def main():
    parser = argparse.ArgumentParser(description='Ubuntu-Automatik für AppIndicators und VRR installieren; ohne sudo.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--status', action='store_true')
    group.add_argument('--ruecknahme', action='store_true')
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise RuntimeError('Dieses Desktop-Skript ohne sudo ausführen.')
    release = {}
    for line in Path('/etc/os-release').read_text().splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            release[key] = shlex.split(value)[0] if shlex.split(value) else ''
    if release.get('ID') != 'ubuntu' and 'ubuntu' not in release.get('ID_LIKE', '').split():
        raise RuntimeError('Diese AppIndicators-Automatik ist nur für Ubuntu und Ubuntu-basierte GNOME-Systeme. Fedora bleibt unverändert.')
    target = Path.home() / '.local/share/msi-vrr-auto'
    unit = Path.home() / '.config/systemd/user' / UNIT_NAME
    state_dir = Path.home() / '.local/state/msi-vrr'
    state = state_dir / 'auto-extension-state.json'
    config = Path.home() / '.config/msi-vrr-auto.json'
    if args.status:
        result = subprocess.run(['systemctl', '--user', 'is-active', UNIT_NAME], capture_output=True, text=True)
        print('Automatik:', result.stdout.strip() or 'nicht installiert')
        if (target / 'auto_vrr.py').exists():
            print(run(sys.executable, str(target / 'auto_vrr.py'), '--status'))
        return
    if args.ruecknahme:
        settings = json.loads(config.read_text()) if config.exists() else {}
        detector = GameWindows()
        try:
            if detector.games() + native_games(settings.get('extra_process_names', [])):
                raise RuntimeError('Spiele zuerst beenden; während eines Spiels werden AppIndicators nicht wieder eingeschaltet.')
        finally:
            detector.close()
        if unit.exists() and MARKER not in unit.read_text():
            raise RuntimeError('Unbekannte vorhandene Dienstdatei; keine Änderung.')
        if unit.exists():
            run('systemctl', '--user', 'disable', '--now', UNIT_NAME)
        Switch().leave()
        if unit.exists():
            unit.unlink()
        run('systemctl', '--user', 'daemon-reload')
        print('Automatik entfernt; AppIndicators wieder freigegeben, falls von der Automatik abgeschaltet.')
        print('Gesicherte Dateien und Protokolle bleiben unter', state_dir)
        return
    if not shutil.which('xrandr'):
        raise RuntimeError('xrandr fehlt; für die randlose Monitorerkennung wird dieses vorhandene X11-Werkzeug benötigt.')
    from gi.repository import Gio, GLib
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    info = bus.call_sync('org.gnome.Shell.Extensions', '/org/gnome/Shell/Extensions', 'org.gnome.Shell.Extensions',
                         'GetExtensionInfo', GLib.Variant('(s)', (UUID,)), None, Gio.DBusCallFlags.NONE, -1, None).unpack()[0]
    if not info:
        raise RuntimeError('Ubuntu AppIndicators ist in dieser GNOME-Sitzung nicht vorhanden.')
    if target.is_symlink() or unit.is_symlink() or state.is_symlink():
        raise RuntimeError('Unerwartete symbolische Verknüpfung am Installationsziel; keine Änderung.')
    if unit.exists() and MARKER not in unit.read_text():
        raise RuntimeError('Unbekannte vorhandene Dienstdatei; keine Änderung.')
    for name in PROGRAMS:
        existing = target / name
        if existing.is_symlink():
            raise RuntimeError('Unerwartete Verknüpfung: ' + str(existing))
        if existing.exists() and existing.read_text() != (Path(__file__).parent / name).read_text() and MARKER not in existing.read_text():
            raise RuntimeError('Unbekannte vorhandene Programmdatei: ' + str(existing))
    backup = state_dir / ('auto-install-before-' + time.strftime('%Y%m%d-%H%M%S') + '-' + str(time.time_ns()))
    backup.mkdir(parents=True)
    for index, file in enumerate([unit, state, config] + [target / name for name in PROGRAMS]):
        if file.exists():
            shutil.copy2(file, backup / (str(index) + '-' + file.name))
    target.mkdir(parents=True, exist_ok=True)
    for name in PROGRAMS:
        shutil.copy2(Path(__file__).parent / name, target / name)
    if not config.exists():
        save(config, {'version': 1, 'extra_process_names': []})
    if not state.exists():
        # Adopt only an AppIndicators change recorded by our earlier diagnosis.
        legacy = state_dir / 'gnome-vrr-gaming-backup.json'
        old = json.loads(legacy.read_text()) if legacy.exists() else {}
        adopted = bool(old.get('active') and UUID in old.get('added_disabled', []))
        save(state, {'version': 1, 'uuid': UUID, 'owned': adopted})
        if adopted:
            old['active'] = False
            old['superseded_by'] = UNIT_NAME
            save(legacy, old)
    unit.parent.mkdir(parents=True, exist_ok=True)
    unit.write_text(MARKER + '''
[Unit]
Description=MSI VRR: Ubuntu Vollbild und randlos überwachen
After=graphical-session-pre.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 "%h/.local/share/msi-vrr-auto/auto_vrr.py" --daemon
Restart=on-failure
RestartSec=3

[Install]
WantedBy=graphical-session.target
''')
    run('systemctl', '--user', 'daemon-reload')
    run('systemctl', '--user', 'enable', UNIT_NAME)
    run('systemctl', '--user', 'restart', UNIT_NAME)
    print('FERTIG: Ubuntu-Automatik installiert und für künftige GNOME-Sitzungen aktiviert.')
    print('Vollbild und randlose Spiele auf dem MSI werden fortlaufend geprüft.')
    print('Nur bei anhaltend ausgeschaltetem VRR wird AppIndicators kurz neu initialisiert; fehlgeschlagene Versuche werden begrenzt wiederholt.')
    print('Bei Bedarf verschwinden die Symbole für etwa drei, höchstens zehn Sekunden und bleiben danach sichtbar.')
    print('Dock, Desktop-Symbole und Fensterkacheln bleiben aktiv. Fedora wird nicht verändert.')
    print('Sicherung vor Installation:', backup)
    print('Prüfen: bash 05-Ubuntu-VRR-Automatik.sh --status')
    print('Rücknahme nach Beenden des Spiels: bash 05-Ubuntu-VRR-Automatik.sh --ruecknahme')

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('FEHLER:', error, file=sys.stderr)
        sys.exit(1)
