#!/usr/bin/env python3
# MSI VRR Ubuntu automation, version 1.
"""Monitor VRR in fullscreen/borderless games and retain AppIndicator icons."""
import argparse
import ast
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from x11_games import GameWindows
from vrr_hardware import MSIVRR

UUID = 'ubuntu-appindicators@ubuntu.com'
STATE_DIR = Path.home() / '.local/state/msi-vrr'
CONFIG = Path.home() / '.config/msi-vrr-auto.json'

def acquire_daemon_lock(path=None):
    """Share this profile lock with Open Hardware Control; one watcher per user."""
    path = path or STATE_DIR / 'auto-daemon.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeError('Unerwartete Verknüpfung am VRR-Instanzlock.')
    stream = path.open('a+')
    try:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        stream.close()
        return None
    path.chmod(0o600)
    stream.seek(0)
    stream.truncate()
    stream.write(str(os.getpid()) + '\n')
    stream.flush()
    return stream

def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout.strip()

def disabled():
    value = ast.literal_eval(run('gsettings', 'get', 'org.gnome.shell', 'disabled-extensions').replace('@as ', ''))
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise RuntimeError('Unerwartete GNOME-Erweiterungseinstellung.')
    return value

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temp.chmod(0o600)
    temp.replace(path)

def native_games(extra_names=()):
    """Recognize actual native Steam binaries and explicitly configured games."""
    result = []
    names = {name.casefold() for name in extra_names}
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            if proc.stat().st_uid != os.getuid():
                continue
            comm = (proc / 'comm').read_text().strip()
            if comm.casefold() in names:
                result.append({'pid': int(proc.name), 'process': comm})
                continue
            executable = os.readlink(proc / 'exe')
            # Exclude Proton and runtime helpers; they can outlive the game.
            if '/steamapps/common/' not in executable:
                continue
            folder = executable.split('/steamapps/common/', 1)[1].split('/', 1)[0]
            if folder.casefold().startswith(('proton', 'steamlinuxruntime')):
                continue
            env = (proc / 'environ').read_bytes().split(b'\0')
            appid = next((item.partition(b'=')[2] for item in env if item.startswith(b'SteamAppId=')), b'0')
            if appid.isdigit() and int(appid) > 0:
                result.append({'pid': int(proc.name), 'appid': appid.decode()})
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
    return result

def ready_games(active, focus, pending, seen, now):
    """Wait for a stable focused fullscreen or monitor-filling borderless game."""
    ready = []
    keys = set()
    for game in active:
        key = str(game.get('appid', game.get('process', ''))) + ':' + str(game.get('pid') or game.get('window'))
        keys.add(key)
        if key in seen:
            continue
        window = game.get('window')
        suitable = game.get('covers_msi') or (game.get('fullscreen') and game.get('on_msi', True))
        if window and (window != focus or not suitable):
            pending.pop(key, None)
            continue
        marker = (window, tuple(game.get('geometry') or []), bool(game.get('fullscreen'))) if window else game.get('pid')
        previous = pending.get(key)
        if previous is None or previous[0] != marker:
            pending[key] = (marker, now)
        elif now - previous[1] >= 5:
            ready.append(game)
    for key in list(pending):
        if key not in keys:
            pending.pop(key)
    return ready

class HealthGuard:
    """Retry failed resets, without treating Alt+Tab or brief transitions as faults."""
    def __init__(self):
        self.identity = None
        self.zero_since = None
        self.attempts = 0
        self.next_allowed = 0
        self.warned = False

    def needs_reset(self, ready, value, now):
        identity = tuple(sorted((str(g.get('appid', g.get('process', ''))), str(g.get('pid')), str(g.get('window')), str(g.get('geometry')), str(g.get('fullscreen'))) for g in ready))
        if identity != self.identity:
            self.identity = identity
            self.zero_since = None
            self.attempts = 0
            self.warned = False
        if not ready or value != 0:
            self.zero_since = None
            if value == 1:
                self.attempts = 0
                self.warned = False
            return False
        if self.zero_since is None:
            self.zero_since = now
        if self.attempts >= 3:
            if not self.warned:
                print('VRR bleibt nach drei Versuchen aus. Keine weiteren Tray-Neustarts bis Fokus/Modus wechselt; Spieltest und Protokoll prüfen.', flush=True)
                self.warned = True
            return False
        return now - self.zero_since >= 5 and now >= self.next_allowed

    def attempted(self, now, result):
        self.attempts += 1
        self.zero_since = None
        self.next_allowed = now + (10 if result == 1 else 30)

class Switch:
    def __init__(self, path=None):
        self.path = path or STATE_DIR / 'auto-extension-state.json'
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {'version': 1, 'uuid': UUID, 'owned': False}
        if self.data.get('uuid') != UUID:
            raise RuntimeError('Unbekannte Erweiterung in der Automatik-Sicherung.')
        # Version one marked failed attempts as completed. Never skip a live
        # VRR check because that old cache contains the current game process.
        self.data.pop('seen_games', None)

    def enter(self, games):
        current = disabled()
        if UUID not in current:
            self.data['owned'] = True
            save(self.path, self.data)  # Write rollback state before the setting.
            run('gsettings', 'set', 'org.gnome.shell', 'disabled-extensions', repr(current + [UUID]))
            print('Spiel erkannt; Ubuntu AppIndicators ausgeschaltet:', games, flush=True)

    def leave(self):
        if not self.data.get('owned'):
            return
        current = disabled()
        if UUID in current:
            run('gsettings', 'set', 'org.gnome.shell', 'disabled-extensions', repr([item for item in current if item != UUID]))
        self.data['owned'] = False
        save(self.path, self.data)
        print('Ubuntu AppIndicators wieder freigegeben.', flush=True)

    def reset(self, games, hardware=None):
        # Recover our previous temporary disablement; respect an extension
        # disabled by the user before automation was installed.
        if self.data.get('owned'):
            self.leave()
            return hardware.value() if hardware else None
        if UUID in disabled():
            print('AppIndicators war bereits vom Benutzer ausgeschaltet; keine Aktivierung.', flush=True)
            return
        self.enter(games)
        started=time.monotonic()
        stable_since=None
        # Let the active fullscreen surface settle and confirm VRR before
        # rebuilding the tray. Keep the interruption bounded to ten seconds.
        try:
            if hardware:
                while time.monotonic()-started<10:
                    value=hardware.value()
                    now=time.monotonic()
                    if value==1:
                        if stable_since is None:stable_since=now
                        if now-started>=3 and now-stable_since>=2:break
                    else:
                        stable_since=None
                    if value is None and now-started>=3:break
                    time.sleep(.25)
            else:
                time.sleep(3)
        finally:
            self.leave()
        result=hardware.value() if hardware else None
        print('AppIndicators wieder aktiv; aktueller VRR-Treiberwert:', result, flush=True)
        return result

def main():
    parser = argparse.ArgumentParser(description='Ubuntu AppIndicators abhängig von laufenden Spielen schalten.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--daemon', action='store_true')
    group.add_argument('--status', action='store_true')
    group.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise RuntimeError('Die GNOME-Automatik ohne sudo ausführen.')
    daemon_lock = acquire_daemon_lock() if args.daemon else None
    if args.daemon and daemon_lock is None:
        print('Eine VRR-Automatik ist bereits aktiv; keine zweite Instanz gestartet.', flush=True)
        return
    config = json.loads(CONFIG.read_text()) if CONFIG.exists() else {'extra_process_names': []}
    switch = Switch()
    detector = GameWindows()
    hardware = MSIVRR()
    def games():
        return detector.games() + native_games(config.get('extra_process_names', []))
    try:
        if args.status:
            print('Erkannte Spiele:', games())
            print('AppIndicators ausgeschaltet:', UUID in disabled())
            print('Vorübergehend von der Automatik abgeschaltet:', bool(switch.data.get('owned')))
            print('Aktueller MSI-VRR-Treiberwert:', hardware.value())
            print('Betriebsart: VRR in Vollbild/randlos überwachen; gezielte Wiederholung bei Blockade.')
            return
        if args.restore:
            if games():
                raise RuntimeError('Spiel zuerst beenden; keine Wiederaktivierung während eines laufenden Spiels.')
            switch.leave()
            return
        stopping = False
        def stop(signum, frame):
            nonlocal stopping
            stopping = True
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        idle_since = None
        pending = {}
        guard = HealthGuard()
        previous_status = None
        save(switch.path, switch.data)
        print('VRR-Automatik gestartet; überwacht fokussiertes Vollbild und randlose MSI-Spiele.', flush=True)
        while not stopping:
            active = games()
            if active:
                idle_since = None
                ready = ready_games(active, detector.focused(), pending, set(), time.monotonic())
                value = hardware.value()
                if ready and switch.data.get('owned'):
                    switch.leave()
                if guard.needs_reset(ready, value, time.monotonic()):
                    result = switch.reset(ready, hardware)
                    guard.attempted(time.monotonic(), result)
                status = 'aktiv' if ready and value == 1 else 'wartet auf VRR' if ready else 'kein fokussiertes Vollbild/randlos auf MSI'
                if status != previous_status:
                    print('VRR-Überwachung:', status, flush=True)
                    previous_status = status
            elif idle_since is None:
                guard.needs_reset([], None, time.monotonic())
                idle_since = time.monotonic()
            elif time.monotonic() - idle_since >= 6:
                switch.leave()
                pending.clear()
            time.sleep(1)
        # During restart/log out retain the ownership record. Never enable the
        # extension on a running game just because the service is stopping.
        if not games():
            switch.leave()
    finally:
        detector.close()
        if daemon_lock is not None:
            daemon_lock.close()

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('FEHLER:', error, file=sys.stderr, flush=True)
        sys.exit(1)
