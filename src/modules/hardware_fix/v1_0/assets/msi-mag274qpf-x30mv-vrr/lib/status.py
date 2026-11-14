#!/usr/bin/env python3
"""Read-only EDID, DRM and optional GNOME diagnostic; no root required when DRM is readable."""
import ctypes as c
import argparse
import hashlib
import os
from pathlib import Path
import time

from vrr_hardware import PATCH
class Props(c.Structure):
    _fields_ = [('count', c.c_uint32), ('ids', c.POINTER(c.c_uint32)), ('values', c.POINTER(c.c_uint64))]
class Prop(c.Structure):
    _fields_ = [('id', c.c_uint32), ('flags', c.c_uint32), ('name', c.c_char * 32)]

def main():
    parser = argparse.ArgumentParser(description='EDID und echte VRR-Aktivität lesend prüfen.')
    parser.add_argument('--watch', type=int, default=0, metavar='SEKUNDEN', help='VRR wiederholt im Hintergrund messen (1–3600 Sekunden).')
    parser.add_argument('--delay', type=int, default=10, metavar='SEKUNDEN', help='Vor der Messung Zeit zum Wechsel ins Spiel lassen (0–60, Standard 10).')
    args = parser.parse_args()
    if not 0 <= args.watch <= 3600 or not 0 <= args.delay <= 60:
        parser.error('--watch muss 0–3600 und --delay 0–60 sein.')
    print('Kernel:', os.uname().release)
    print('Bootparameter:', Path('/proc/cmdline').read_text().strip())
    parameter = Path('/sys/module/drm/parameters/edid_firmware')
    print('EDID-Override:', parameter.read_text().strip() if parameter.exists() else 'nicht verfügbar')
    lib = c.CDLL('libdrm.so.2')
    lib.drmModeObjectGetProperties.argtypes = [c.c_int, c.c_uint32, c.c_uint32]
    lib.drmModeObjectGetProperties.restype = c.POINTER(Props)
    lib.drmModeGetProperty.argtypes = [c.c_int, c.c_uint32]
    lib.drmModeGetProperty.restype = c.POINTER(Prop)
    lib.drmModeFreeObjectProperties.argtypes = [c.POINTER(Props)]
    lib.drmModeFreeProperty.argtypes = [c.POINTER(Prop)]
    lib.drmSetClientCap.argtypes = [c.c_int, c.c_uint64, c.c_uint64]
    def properties(fd, object_id, type_id):
        result = {}
        p = lib.drmModeObjectGetProperties(fd, object_id, type_id)
        if not p:
            return result
        try:
            for i in range(p.contents.count):
                prop = lib.drmModeGetProperty(fd, p.contents.ids[i])
                if prop:
                    result[prop.contents.name.decode()] = p.contents.values[i]
                    lib.drmModeFreeProperty(prop)
        finally:
            lib.drmModeFreeObjectProperties(p)
        return result
    watch_targets = []
    for status in sorted(Path('/sys/class/drm').glob('card*-*/status')):
        if status.read_text().strip() != 'connected':
            continue
        connector = status.parent
        edid = (connector / 'edid').read_bytes()
        digest = hashlib.sha256(edid).hexdigest()
        print('\nAnschluss:', connector.name, '| EDID:', digest)
        print('Korrigierte MSI-EDID geladen:', 'JA' if digest == PATCH else 'NEIN')
        if digest == PATCH:
            watch_targets.append(connector)
        try:
            fd = os.open('/dev/dri/' + connector.name.split('-', 1)[0], os.O_RDONLY)
        except PermissionError:
            print('DRM-Zugriff nicht erlaubt. Bei Bedarf Status-Skript mit sudo wiederholen.')
            continue
        try:
            lib.drmSetClientCap(fd, 3, 1)  # expose atomic properties; no modesetting
            props = properties(fd, int((connector / 'connector_id').read_text()), 0xc0c0c0c0)
            print('vrr_capable:', props.get('vrr_capable', 'nicht vorhanden'))
            crtc = props.get('CRTC_ID', 0)
            print('VRR_ENABLED:', properties(fd, crtc, 0xcccccccc).get('VRR_ENABLED', 'nicht vorhanden') if crtc else 'kein aktiver CRTC')
        finally:
            os.close(fd)
    if os.geteuid() != 0:
        try:
            from gi.repository import Gio
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            state = bus.call_sync('org.gnome.Mutter.DisplayConfig', '/org/gnome/Mutter/DisplayConfig',
                                  'org.gnome.Mutter.DisplayConfig', 'GetCurrentState', None, None,
                                  Gio.DBusCallFlags.NONE, -1, None).unpack()
            for spec, modes, _ in state[1]:
                current = [m[0] for m in modes if m[6].get('is-current')]
                variable = [m for m in modes if m[6].get('refresh-rate-mode') == 'variable' or m[0].endswith('+vrr')]
                print('\nGNOME:', spec[0], spec[2], '| aktuell:', ', '.join(current), '| VRR-Modi:', len(variable))
        except Exception:
            print('\nGNOME-Abfrage nicht verfügbar; DRM-Angaben gelten unabhängig vom Desktop.')
    print('\nBedeutung: vrr_capable=1 heißt unterstützt. VRR_ENABLED=1 heißt beim Abfragen eingeschaltet.')
    print('VRR_ENABLED=0 auf dem Desktop ist kein alleiniger Gegenbeweis. Im Vollbildspiel auf dem MSI prüfen.')
    if args.watch:
        if not watch_targets:
            raise RuntimeError('Kein aktiver Anschluss mit korrigierter MSI-EDID gefunden.')
        print('\nMessung startet in', args.delay, 'Sekunden. Jetzt mit Alt+Tab ins Vollbildspiel wechseln und dort bleiben.', flush=True)
        time.sleep(args.delay)
        handles = []
        counts = {p.name: {0: 0, 1: 0, 'unbekannt': 0} for p in watch_targets}
        try:
            for connector in watch_targets:
                fd = os.open('/dev/dri/' + connector.name.split('-', 1)[0], os.O_RDONLY)
                handles.append((connector, fd))
                lib.drmSetClientCap(fd, 3, 1)
            for sample in range(args.watch):
                for connector, fd in handles:
                    props = properties(fd, int((connector / 'connector_id').read_text()), 0xc0c0c0c0)
                    crtc = props.get('CRTC_ID', 0)
                    value = properties(fd, crtc, 0xcccccccc).get('VRR_ENABLED') if crtc else None
                    key = value if value in (0, 1) else 'unbekannt'
                    counts[connector.name][key] += 1
                    print(f'{sample + 1:3d}s {connector.name}: VRR_ENABLED={key}', flush=True)
                time.sleep(1)
        finally:
            for _, fd in handles:
                os.close(fd)
        for name, count in counts.items():
            print('\nMessung:', name, '| eingeschaltet:', count[1], '| ausgeschaltet:', count[0], '| unbekannt:', count['unbekannt'])
            if count[1]:
                print('VRR war während der Messung hardwareseitig eingeschaltet.')
            else:
                print('Kein eingeschaltetes VRR gemessen. Nur als Spieltest werten, wenn das Spiel im Vordergrund blieb.')

if __name__ == '__main__':
    main()
