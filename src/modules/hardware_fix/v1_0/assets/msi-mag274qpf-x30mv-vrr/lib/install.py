#!/usr/bin/env python3
"""EDID recovery for the MSI MAG 274QPF X30MV. No automatic reboot or package install."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent.parent
NAME = 'msi-mag274qpf-x30mv-vrr.bin'
FIRMWARE = Path('/usr/lib/firmware/edid') / NAME
PARAM = 'drm.edid_firmware=DP:edid/' + NAME
HASH = '7d975778662fb0f3b16aba96dbd0282a072c6b6b7fb992967f79846f82d13fdc'
ORIGINAL_HASH = 'e6c8562c659b080a013ac1429c198dc905a7260df54e06e53a070a195615588f'
MARKER = '# MSI-VRR-RECOVERY'
ROOT_LOCK = None

def is_target_monitor(data):
    """Recognize only this model while deliberately ignoring its serial descriptor."""
    return (len(data) == 384
            and data[:8] == b'\x00\xff\xff\xff\xff\xff\xff\x00'
            and data[8:12] == bytes.fromhex('3669f05c')
            and b'MAG 274 X30MV' in data[:128]
            and not any(sum(data[i:i+128]) % 256 for i in range(0, len(data), 128)))

def acquire_root_lock():
    global ROOT_LOCK
    lock = Path('/run/lock/open-hardware-control-msi-vrr.lock').open('a+')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        raise RuntimeError('Ein anderer MSI-VRR-Systemjob läuft bereits.')
    ROOT_LOCK = lock

def run(argv, capture=False, cwd=None):
    if not capture:
        print('+', shlex.join([str(a) for a in argv]), flush=True)
    return subprocess.run([str(a) for a in argv], check=True, cwd=cwd,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=None, text=capture)

def require(*commands):
    missing = [c for c in commands if not shutil.which(c)]
    if missing:
        raise RuntimeError('Benötigte Programme fehlen: ' + ', '.join(missing) +
                           '. Keine Änderung vorgenommen.')

def validate_edid(data):
    if (len(data) != 384 or data[:8] != b'\x00\xff\xff\xff\xff\xff\xff\x00'
        or hashlib.sha256(data).hexdigest() != HASH
        or any(sum(data[i:i+128]) % 256 for i in range(0, len(data), 128))):
        raise RuntimeError('Die korrigierte EDID entspricht nicht der geprüften Datei.')

def os_identity():
    return dict(line.split('=', 1) for line in Path('/etc/os-release').read_text().splitlines()
                if '=' in line and not line.startswith('#'))

def preflight(distro, override_bootloader='auto'):
    identity = os_identity()
    family = (identity.get('ID', '') + ' ' + identity.get('ID_LIKE', '')).replace('"', '').split()
    required_id = {'ubuntu': 'ubuntu', 'fedora': 'fedora', 'arch': 'arch'}[distro]
    if required_id not in family:
        raise RuntimeError(f'Dieses Startskript ist für {distro}, gefunden wurde {identity.get("PRETTY_NAME")}.')
    if Path('/run/ostree-booted').exists():
        raise RuntimeError('Fedora Atomic/Silverblue/Kinoite benötigt einen anderen Installationsweg.')
    connectors = []
    for status in Path('/sys/class/drm').glob('card*-*/status'):
        if status.read_text().strip() != 'connected':
            continue
        data = (status.parent / 'edid').read_bytes()
        if is_target_monitor(data):
            connectors.append(status.parent.name)
    if not connectors:
        raise RuntimeError('Der Monitor mit dieser originalen oder korrigierten EDID ist nicht angeschlossen. '
                           'MSI über DisplayPort anschließen und erneut starten.')
    if not any('-DP-' in c for c in connectors):
        raise RuntimeError('Den MSI direkt über DisplayPort anschließen.')
    print('Passender Monitor:', ', '.join(connectors))
    print('Geltungsbereich: alle DisplayPorts. Andere DP-Monitore erhalten dieselbe MSI-EDID!')
    # Conflicting EDID parameters must not silently be overwritten.
    sources = [Path('/proc/cmdline'), Path('/etc/default/grub'), Path('/etc/kernel/cmdline')]
    sources += list(Path('/etc/default/grub.d').glob('*.cfg'))
    for source in sources:
        if source.exists():
            for token in re.findall(r'drm\.edid_firmware=[^\s"\']+', source.read_text()):
                if token != PARAM:
                    raise RuntimeError(f'Anderer EDID-Override in {source}: {token}. Erst klären; keine Änderung.')
    if distro == 'ubuntu':
        require('update-initramfs', 'update-grub')
        wrapper = Path(shutil.which('update-initramfs')).resolve().read_text(errors='replace')
        engine = 'dracut' if 'dracut' in wrapper else 'initramfs-tools'
    elif distro == 'fedora':
        require('dracut', 'grubby')
        engine = 'dracut'
    else:
        if shutil.which('mkinitcpio') and list(Path('/etc/mkinitcpio.d').glob('*.preset')):
            engine = 'mkinitcpio'
            for preset in Path('/etc/mkinitcpio.d').glob('*.preset'):
                if re.search(r'^\s*(?:ALL_config\s*=|\w+_options=.*(?:--config|-c\s))', preset.read_text(), re.M):
                    raise RuntimeError(f'{preset} verwendet eine eigene mkinitcpio-Konfiguration. Automatische Installation abgebrochen.')
        elif shutil.which('dracut'):
            engine = 'dracut'
        else:
            raise RuntimeError('Weder mkinitcpio-Presets noch dracut gefunden.')
    require('lsinitrd' if engine == 'dracut' else 'unmkinitramfs' if engine == 'initramfs-tools' else 'lsinitcpio')
    if distro == 'fedora':
        bootloader = 'grubby'
        info = run(['grubby', '--info=ALL'], capture=True).stdout
        for token in re.findall(r'drm\.edid_firmware=[^\s"\']+', info):
            if token != PARAM:
                raise RuntimeError('Fedora-Boot-Eintrag enthält einen anderen EDID-Override. Keine Änderung.')
    elif override_bootloader != 'auto':
        bootloader = override_bootloader
    else:
        systemd_active = False
        if shutil.which('bootctl'):
            status = subprocess.run(['bootctl', 'status'], text=True, capture_output=True)
            current = status.stdout.split('Available Boot Loaders', 1)[0]
            systemd_active = 'systemd-boot' in current
        if systemd_active:
            bootloader = 'systemd-boot'
        elif Path('/etc/default/grub').exists():
            bootloader = 'grub'
        else:
            raise RuntimeError('Bootloader nicht erkannt. GRUB oder systemd-boot-Type-1 wird benötigt; siehe Anleitung.')
    if distro == 'ubuntu' and bootloader != 'grub':
        raise RuntimeError('Ubuntu-Skript unterstützt GRUB. Andere Bootloader benötigen Anpassung.')
    if bootloader == 'grub':
        require('update-grub' if distro == 'ubuntu' else 'grub-mkconfig')
        if not Path('/etc/default/grub').exists():
            raise RuntimeError('/etc/default/grub fehlt.')
    entries = []
    if bootloader == 'systemd-boot':
        require('bootctl')
        bootpath = Path(run(['bootctl', '--print-boot-path'], capture=True).stdout.strip())
        entries = [p for p in (bootpath / 'loader/entries').glob('*.conf')
                   if re.search(r'^\s*linux\s+', p.read_text(), re.M)]
        if not entries:
            raise RuntimeError('Keine klassischen systemd-boot-Linux-Einträge gefunden. UKIs und signierte UKIs werden nicht automatisch verändert.')
        for entry in entries:
            if not re.search(r'^\s*options\s+', entry.read_text(), re.M):
                raise RuntimeError(f'{entry}: keine options-Zeile. Keine Änderung.')
            for token in re.findall(r'drm\.edid_firmware=\S+', entry.read_text()):
                if token != PARAM:
                    raise RuntimeError(f'Anderer EDID-Override in {entry}. Keine Änderung.')
    images, builds = [], []
    if distro in ('ubuntu', 'fedora'):
        for moddir in Path('/lib/modules').glob('*'):
            version = moddir.name
            image = Path('/boot') / (f'initrd.img-{version}' if distro == 'ubuntu' else f'initramfs-{version}.img')
            if moddir.is_dir() and image.is_file():
                images.append(str(image))
                if distro == 'fedora':
                    builds.append(['dracut', '--force', str(image), version])
        if distro == 'ubuntu':
            builds = [['update-initramfs', '-u', '-k', 'all']]
    else:
        if engine == 'mkinitcpio':
            # Read trusted local shell presets using Bash so path variables expand correctly.
            script = 'source "$1"; for p in "${PRESETS[@]}"; do v="${p}_image"; printf "%s\\n" "${!v}"; v="${p}_uki"; [[ -z ${!v} ]] || exit 42; done; exit 0'
            for preset in Path('/etc/mkinitcpio.d').glob('*.preset'):
                result = subprocess.run(['bash', '-c', script, 'bash', str(preset)], text=True, capture_output=True)
                if result.returncode:
                    raise RuntimeError(f'UKI oder nicht unterstütztes Preset: {preset}. Keine automatische Änderung.')
                images.extend(p for p in result.stdout.splitlines() if p)
            builds = [['mkinitcpio', '-P']]
        else:
            for moddir in Path('/usr/lib/modules').glob('*'):
                pkgbase = moddir / 'pkgbase'
                if not pkgbase.exists():
                    continue
                name = pkgbase.read_text().strip()
                if not re.fullmatch(r'[A-Za-z0-9._-]+', name):
                    raise RuntimeError('Ungewöhnlicher Arch-Kernelname.')
                for suffix in ('', '-fallback'):
                    image = Path('/boot') / f'initramfs-{name}{suffix}.img'
                    if image.exists():
                        images.append(str(image))
                        builds.append(['dracut', '--force'] + (['--no-hostonly'] if suffix else []) + [str(image), moddir.name])
    images = sorted(set(images))
    if not images or not builds:
        raise RuntimeError('Keine unterstützten Boot-Abbilder gefunden. Keine Änderung.')
    print('System:', identity.get('PRETTY_NAME'), '| Initramfs:', engine, '| Bootloader:', bootloader)
    for image in images:
        print('Zu prüfendes Boot-Abbild:', image)
    return dict(distro=distro, engine=engine, bootloader=bootloader, entries=[str(e) for e in entries], images=images, builds=builds)

class Transaction:
    def __init__(self, plan):
        base = Path('/var/backups/msi-vrr-recovery')
        base.mkdir(parents=True, exist_ok=True)
        self.path = Path(tempfile.mkdtemp(prefix=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-'), dir=base))
        self.data = {'plan': plan, 'files': [], 'fedora_kernels': []}
        shutil.copy2(__file__, self.path / 'install.py')
        self.save()
    def save(self):
        (self.path / 'manifest.json').write_text(json.dumps(self.data, indent=2))
    def backup(self, path):
        path = Path(path)
        if any(f['path'] == str(path) for f in self.data['files']):
            return
        entry = {'path': str(path), 'exists': path.exists()}
        if path.exists():
            index = str(len(self.data['files']))
            shutil.copy2(path, self.path / index)
            stat = path.stat()
            entry.update(backup=index, uid=stat.st_uid, gid=stat.st_gid, mode=stat.st_mode & 0o777)
        self.data['files'].append(entry)
        self.save()
    def write(self, path, data, mode=0o644):
        path = Path(path)
        self.backup(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data if isinstance(data, bytes) else data.encode())
        path.chmod(mode)
    def remove(self, path):
        path = Path(path)
        self.backup(path)
        path.unlink(missing_ok=True)

def rebuild(plan):
    for argv in plan['builds']:
        run(argv)

def verify_images(plan, expected):
    for image in plan['images']:
        if plan['engine'] == 'dracut':
            extracted = subprocess.run(['lsinitrd', '-f', str(FIRMWARE).lstrip('/'), image], check=True, capture_output=True).stdout
            if extracted != expected:
                raise RuntimeError(f'EDID fehlt oder stimmt nicht im Boot-Abbild: {image}')
        else:
            with tempfile.TemporaryDirectory(prefix='msi-vrr-check-') as tmp:
                if plan['engine'] == 'mkinitcpio':
                    run(['lsinitcpio', '-x', image], cwd=tmp, capture=True)
                else:
                    run(['unmkinitramfs', image, str(Path(tmp) / 'content')], capture=True)
                files = list(Path(tmp).rglob(NAME))
                if not any(p.is_file() and p.read_bytes() == expected for p in files):
                    raise RuntimeError(f'EDID fehlt oder stimmt nicht im Boot-Abbild: {image}')
        print('EDID bytegleich im Boot-Abbild:', image, flush=True)

def configure_initramfs(tx, plan):
    if plan['engine'] == 'dracut':
        tx.write('/etc/dracut.conf.d/99-msi-vrr.conf', MARKER + '\ninstall_items+=" ' + str(FIRMWARE) + ' "\n')
        # Remove only the obsolete hook created during this conversation, not unrelated hooks.
        old = Path('/etc/initramfs-tools/hooks/msi-vrr-edid')
        if old.exists() and NAME in old.read_text():
            tx.remove(old)
    elif plan['engine'] == 'mkinitcpio':
        tx.write('/etc/mkinitcpio.conf.d/99-msi-vrr.conf', MARKER + '\nFILES+=(' + str(FIRMWARE) + ')\n')
    else:
        tx.write('/etc/initramfs-tools/hooks/msi-vrr-edid', '''#!/bin/sh
set -eu
case "${1:-}" in prereqs) exit 0 ;; esac
source_edid=/usr/lib/firmware/edid/msi-mag274qpf-x30mv-vrr.bin
target_edid="${DESTDIR:?}/usr/lib/firmware/edid/msi-mag274qpf-x30mv-vrr.bin"
mkdir -p "${target_edid%/*}"
cp "$source_edid" "$target_edid"
cmp "$source_edid" "$target_edid"
''', 0o755)

def configure_bootloader(tx, plan):
    if plan['bootloader'] == 'grubby':
        before = run(['grubby', '--info=ALL'], capture=True).stdout
        for block in re.split(r'(?=^index=)', before, flags=re.M):
            kernel = re.search(r'^kernel=(.+)$', block, re.M)
            args = re.search(r'^args=(.+)$', block, re.M)
            if kernel and args:
                tokens = shlex.split(args.group(1))
                args_value = tokens[0] if len(tokens) == 1 else args.group(1)
                overrides = [t for t in args_value.split() if t.startswith('drm.edid_firmware=')]
                if any(t != PARAM for t in overrides):
                    raise RuntimeError('Fedora-Boot-Eintrag enthält bereits einen anderen EDID-Override.')
                tx.data['fedora_kernels'].append({'kernel': shlex.split(kernel.group(1))[0], 'had_param': PARAM in args_value.split()})
        if not tx.data['fedora_kernels']:
            raise RuntimeError('grubby-Ausgabe konnte nicht verlässlich ausgewertet werden. Bootparameter nicht verändert.')
        tx.save()
        run(['grubby', '--update-kernel=ALL', '--args=' + PARAM])
        cmdline = Path('/etc/kernel/cmdline')
        if cmdline.exists() and PARAM not in cmdline.read_text().split():
            tx.write(cmdline, cmdline.read_text().strip() + ' ' + PARAM + '\n')
        if PARAM not in run(['grubby', '--info=ALL'], capture=True).stdout:
            raise RuntimeError('grubby-Abschlussprüfung fehlgeschlagen.')
    elif plan['bootloader'] == 'grub':
        addition = (MARKER + '\ncase " ${GRUB_CMDLINE_LINUX_DEFAULT:-} " in\n'
                    f'  *" {PARAM} "*) ;;\n'
                    f'  *) GRUB_CMDLINE_LINUX_DEFAULT="${{GRUB_CMDLINE_LINUX_DEFAULT:-}} {PARAM}" ;;\n'
                    'esac\n')
        if plan['distro'] == 'ubuntu':
            tx.write('/etc/default/grub.d/99-msi-vrr.cfg', addition)
            run(['update-grub'])
        else:
            file = Path('/etc/default/grub')
            text = file.read_text()
            text = re.sub(r'\n?# MSI-VRR-RECOVERY\n.*?# END MSI-VRR-RECOVERY\n?', '\n', text, flags=re.S)
            tx.write(file, text.rstrip() + '\n\n' + addition + '# END MSI-VRR-RECOVERY\n')
            run(['grub-mkconfig', '-o', '/boot/grub/grub.cfg'])
        if PARAM not in Path('/boot/grub/grub.cfg').read_text():
            raise RuntimeError('GRUB-Abschlussprüfung fehlgeschlagen.')
    else:
        for filename in plan['entries']:
            file = Path(filename)
            text = file.read_text()
            def append(match):
                line = match.group(0)
                return line if PARAM in line.split() else line.rstrip() + ' ' + PARAM
            tx.write(file, re.sub(r'^\s*options[^\n]+', append, text, flags=re.M))
        file = Path('/etc/kernel/cmdline')
        text = file.read_text().strip() if file.exists() else re.sub(r'\b(?:BOOT_IMAGE|initrd)=\S+\s*', '', Path('/proc/cmdline').read_text()).strip()
        if PARAM not in text.split():
            text += ' ' + PARAM
        tx.write(file, text + '\n')

def restore(directory):
    directory = Path(directory).resolve()
    data = json.loads((directory / 'manifest.json').read_text())
    for entry in reversed(data['files']):
        file = Path(entry['path'])
        if entry['exists']:
            file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(directory / entry['backup'], file)
            os.chown(file, entry['uid'], entry['gid'])
            file.chmod(entry['mode'])
        else:
            file.unlink(missing_ok=True)
    for entry in data['fedora_kernels']:
        if not entry['had_param']:
            run(['grubby', '--update-kernel=' + entry['kernel'], '--remove-args=' + PARAM])
    rebuild(data['plan'])
    if data['plan']['bootloader'] == 'grub':
        run(['update-grub'] if data['plan']['distro'] == 'ubuntu' else ['grub-mkconfig', '-o', '/boot/grub/grub.cfg'])
    print('Konfiguration vor diesem Installationslauf wiederhergestellt. Beim nächsten Neustart wirksam.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--distro', choices=['ubuntu', 'fedora', 'arch'])
    parser.add_argument('--check', action='store_true', help='nur lesende Vorprüfung')
    parser.add_argument('--bootloader', choices=['auto', 'grub', 'systemd-boot'], default='auto')
    parser.add_argument('--restore', metavar='BACKUP')
    args = parser.parse_args()
    if args.restore:
        if os.geteuid() != 0:
            raise RuntimeError('Rücknahme mit sudo starten.')
        acquire_root_lock()
        restore(args.restore)
        return
    if not args.distro:
        parser.error('--distro fehlt')
    data = (PACKAGE / 'EDID/vrr-korrigiert.bin').read_bytes()
    validate_edid(data)
    plan = preflight(args.distro, args.bootloader)
    if args.check:
        print('VORPRÜFUNG OK. Es wurde nichts verändert.')
        return
    if os.geteuid() != 0:
        raise RuntimeError('Installation mit sudo starten.')
    acquire_root_lock()
    tx = Transaction(plan)
    rollback = 'sudo python3 ' + shlex.quote(str(tx.path / 'install.py')) + ' --restore ' + shlex.quote(str(tx.path))
    print('Sicherung:', tx.path, '\nRücknahme:', rollback, flush=True)
    try:
        tx.write(FIRMWARE, data)
        configure_initramfs(tx, plan)
        rebuild(plan)
        verify_images(plan, data)
        configure_bootloader(tx, plan)
        print('\nFERTIG: EDID im Boot-Abbild und Bootparameter geprüft. Kein Neustart ausgelöst.')
        print('Jetzt neu starten. Danach als normaler Benutzer: bash 02-VRR-im-Desktop-aktivieren.sh')
        print('Die Hardware-Funktion muss anschließend während eines Vollbildspiels geprüft werden.')
        print('Rücknahme:', rollback)
    except Exception:
        print('\nINSTALLATION NICHT ABGESCHLOSSEN. Noch nicht neu starten.\nRücknahme: ' + rollback, file=sys.stderr)
        raise

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print('FEHLER:', error, file=sys.stderr)
        sys.exit(1)
