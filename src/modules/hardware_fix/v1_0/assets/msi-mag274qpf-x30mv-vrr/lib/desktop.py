#!/usr/bin/env python3
"""Select and check VRR in the logged-in GNOME session; run WITHOUT sudo."""
import ast
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

def persisted_vrr(source):
    """Read GNOME's saved MSI refresh mode, including GNOME 50's ratemode."""
    if not source.exists():
        return False
    import xml.etree.ElementTree as ET
    tree = ET.parse(source)
    configurations = tree.findall('configuration')
    latest = configurations[0] if configurations else tree.getroot()
    for monitor in latest.findall('.//monitor'):
        if (monitor.findtext('monitorspec/vendor') == 'MSI'
                and monitor.findtext('monitorspec/product') == 'MAG 274 X30MV'):
            if monitor.findtext('mode/ratemode') == 'variable':
                return True
            rate = monitor.find('mode/rate')
            if rate is not None and rate.get('mode') == 'variable':
                return True
    return False

def main():
    if os.geteuid() == 0:
        raise RuntimeError('Dieses Desktop-Skript ohne sudo im angemeldeten Desktop starten.')
    try:
        from gi.repository import Gio, GLib
    except ImportError:
        raise RuntimeError('Python-GObject fehlt. Ubuntu: sudo apt install python3-gi; '
                           'Fedora: sudo dnf install python3-gobject; Arch: sudo pacman -S python-gobject')
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    def call(method, parameters=None):
        return bus.call_sync('org.gnome.Mutter.DisplayConfig', '/org/gnome/Mutter/DisplayConfig',
                             'org.gnome.Mutter.DisplayConfig', method, parameters, None,
                             Gio.DBusCallFlags.NONE, -1, None)
    try:
        state = call('GetCurrentState').unpack()
    except GLib.Error:
        raise RuntimeError('Keine unterstützte GNOME-Sitzung gefunden. Bei KDE: Systemeinstellungen '
                           '→ Anzeige → MSI → Adaptive Sync/Variable Bildwiederholrate aktivieren. '
                           'Das EDID-/Boot-Setup funktioniert unabhängig davon.')
    serial, monitors, logical, global_properties = state
    target_current = [mode for spec, modes, _ in monitors
                      if spec[1:3] == ('MSI', 'MAG 274 X30MV')
                      for mode in modes if mode[6].get('is-current')]
    if (target_current and all(mode[6].get('refresh-rate-mode') == 'variable'
                              or mode[0].endswith('+vrr') for mode in target_current)
            and persisted_vrr(Path.home() / '.config/monitors.xml')):
        print('FERTIG: GNOME verwendet den variablen Modus; die Auswahl ist dauerhaft gespeichert.')
        return
    info = {spec[0]: (spec, modes, properties) for spec, modes, properties in monitors}
    configuration = []
    found = False
    for x, y, scale, transform, primary, specs, _ in logical:
        assignments = []
        for spec in specs:
            connector = spec[0]
            fullspec, modes, properties = info[connector]
            current = next(m for m in modes if m[6].get('is-current'))
            selected = current[0]
            if fullspec[1] == 'MSI' and fullspec[2] == 'MAG 274 X30MV':
                found = True
                candidates = [m for m in modes if m[1:4] == current[1:4]
                              and (m[6].get('refresh-rate-mode') == 'variable' or m[0].endswith('+vrr'))]
                if not candidates:
                    enabled_experiment = False
                    if shutil.which('gsettings'):
                        r = subprocess.run(['gsettings', 'range', 'org.gnome.mutter', 'experimental-features'],
                                           capture_output=True, text=True)
                        if 'variable-refresh-rate' in r.stdout:
                            r = subprocess.run(['gsettings', 'get', 'org.gnome.mutter', 'experimental-features'],
                                               capture_output=True, text=True, check=True)
                            features = ast.literal_eval(r.stdout.replace('@as ', '').strip())
                            if 'variable-refresh-rate' not in features:
                                features.append('variable-refresh-rate')
                                subprocess.run(['gsettings', 'set', 'org.gnome.mutter', 'experimental-features', repr(features)], check=True)
                                enabled_experiment = True
                    message = ('GNOMEs VRR-Funktion wurde zusätzlich aktiviert. Abmelden und wieder anmelden; danach erneut ausführen. '
                               if enabled_experiment else '')
                    raise RuntimeError(message + 'GNOME bietet für den aktuellen MSI-Modus noch kein VRR an. '
                                       'Adaptive Sync im Monitor-Menü kontrollieren; DP-Kabel kurz ab-/anstecken; '
                                       'Anzeigeeinstellungen schließen und erneut öffnen; danach dieses Skript wiederholen.')
                selected = candidates[0][0]
            props = {key: GLib.Variant('u', properties[key]) for key in ('color-mode', 'rgb-range') if key in properties}
            if 'is-underscanning' in properties:
                props['underscanning'] = GLib.Variant('b', properties['is-underscanning'])
            assignments.append((connector, selected, props))
            print(connector, '→', selected, flush=True)
        configuration.append((x, y, scale, transform, primary, assignments))
    if not found:
        raise RuntimeError('Der MSI-Monitor ist in GNOME nicht aktiv.')
    props = {'layout-mode': GLib.Variant('u', global_properties['layout-mode'])} if 'layout-mode' in global_properties else {}
    def apply(method):
        serial = call('GetCurrentState').unpack()[0]
        call('ApplyMonitorsConfig', GLib.Variant('(uua(iiduba(ssa{sv}))a{sv})', (serial, method, configuration, props)))
    apply(0)
    source = Path.home() / '.config/monitors.xml'
    saved = source.read_bytes() if source.exists() else None
    backup_dir = Path.home() / '.local/state/msi-vrr'
    backup_dir.mkdir(parents=True, exist_ok=True)
    if saved is not None:
        backup = backup_dir / ('monitors-before-' + time.strftime('%Y%m%d-%H%M%S') + '.xml')
        backup.write_bytes(saved)
        print('Desktop-Sicherung:', backup)
    print('\nJetzt ggf. im Bildschirmdialog „Änderungen beibehalten“ wählen. '
          'Das Skript wartet 35 Sekunden auf die Bestätigung.', flush=True)
    apply(2)
    time.sleep(35)
    new_state = call('GetCurrentState').unpack()
    current_variable = False
    for spec, modes, _ in new_state[1]:
        if spec[1:3] == ('MSI', 'MAG 274 X30MV'):
            for mode in modes:
                if mode[6].get('is-current'):
                    print('Aktueller GNOME-Modus:', mode[0], mode[6])
                    current_variable = mode[6].get('refresh-rate-mode') == 'variable' or mode[0].endswith('+vrr')
    # Confirm persistence from the MSI entry, never an unrelated monitor's setting.
    persisted = persisted_vrr(source)
    if not current_variable or not persisted:
        raise RuntimeError('VRR wurde nicht dauerhaft bestätigt. Erneut starten und die Bildschirmabfrage bestätigen.')
    print('FERTIG: GNOME verwendet den variablen Modus; die Auswahl ist dauerhaft gespeichert.')
    print('Der Nachweis der Hardware-Aktivität erfolgt mit 03-VRR-Status-pruefen.sh während eines Vollbildspiels.')

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('HINWEIS:', error, file=sys.stderr)
        sys.exit(1)
