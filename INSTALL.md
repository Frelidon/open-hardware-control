# Installation unter Linux

Diese Anleitung gilt für **Open Hardware Control by Frelidon 3.4.29.5 INTERN**. Lade das interne Testpaket zuerst in `~/Downloads`. Diese Version ist noch nicht für ein öffentliches GitHub-Release bestimmt.

## Fedora und Nobara

Empfohlenes RPM-Paket:

```bash
cd ~/Downloads
sudo dnf install ./open-hardware-control-3.4.29.5-0.intern2.noarch.rpm
```

Alternativ das universelle ZIP verwenden. Die benötigten Pakete lauten:

```bash
sudo dnf install liquidctl python3-pyside6 python3-pillow qt6-qtsvg polkit
```

## Debian, Ubuntu und Linux Mint

Empfohlenes DEB-Paket:

```bash
cd ~/Downloads
sudo apt install './open-hardware-control_3.4.29.5~intern2_all.deb'
```

Alternativ das universelle ZIP verwenden. Die benötigten Pakete lauten:

```bash
sudo apt update
sudo apt install liquidctl python3-pyside6.qtwidgets python3-pyside6.qtsvg python3-pil policykit-1
```

## Arch Linux, Manjaro und EndeavourOS

```bash
sudo pacman -S --needed liquidctl pyside6 python-pillow qt6-svg polkit unzip
cd ~/Downloads
unzip open_hardware_control_v3_4_29_5_INTERN.zip
cd open-hardware-control-3.4.29.5-INTERN
chmod +x install.sh
./install.sh
```

## openSUSE Tumbleweed und Leap

```bash
sudo zypper install liquidctl python3-pyside6 python3-Pillow libQt6Svg6 polkit unzip
cd ~/Downloads
unzip open_hardware_control_v3_4_29_5_INTERN.zip
cd open-hardware-control-3.4.29.5-INTERN
chmod +x install.sh
./install.sh
```

Die verfügbaren Python-Paketnamen können sich zwischen Leap- und Tumbleweed-Versionen unterscheiden. Falls `zypper` einen Namen nicht findet, suche mit `zypper search pyside6`, `zypper search Pillow` und `zypper search liquidctl` nach dem Namen deiner installierten Ausgabe. Das Installationsskript zeigt fehlende Komponenten an und fügt keine fremden Paketquellen hinzu.

## Universelles Installationspaket

Für alle oben genannten Distributionen:

```bash
cd ~/Downloads
unzip open_hardware_control_v3_4_29_5_INTERN.zip
cd open-hardware-control-3.4.29.5-INTERN
chmod +x install.sh
./install.sh
```

Die vorhandene Version wird aktualisiert. Danach findest du **Open Hardware Control by Frelidon** im Anwendungsmenü.

## Optionale Pakete für KDE-Desktop-Designs

Open Hardware Control erkennt fehlende Werkzeuge automatisch und bietet ihre Installation nach Bestätigung an.
Unter Fedora 44 werden `kf6-kconfig` und `qt6-qttools` verwendet. Das darin enthaltene Programm heißt dort
`qdbus-qt6` und wird seit Version 3.1.1 direkt erkannt. Ein manueller Kompatibilitätslink ist nicht erforderlich. Version 3.2.0 bietet zusätzlich QtNetwork/QtDBus für die lokale Windows-8/8.1-Oberfläche an.

Die automatische Zuordnung unterstützt außerdem `libkf6config-bin`/`qdbus-qt6` für APT,
`kconfig`/`qt6-tools` für Pacman und `kf6-kconfig`/`qt6-tools-qdbus` für Zypper. Diese Pakete sind optional:
Ohne sie bleiben NZXT- und OpenLinkHub-Steuerung vollständig verfügbar.

## Automatisch verwaltetes OpenRGB-Backend für das RGB-Studio

Das RGB-Studio kann OpenRGB direkt aus den bereits eingerichteten Paketquellen anbieten. Unter Fedora/Nobara werden `openrgb` und `openrgb-udev-rules` installiert; unter APT, Pacman und Zypper wird das jeweilige `openrgb`-Paket verwendet. Es werden keine fremden Repositories hinzugefügt.

Nach der Installation startet Open Hardware Control das Backend automatisch als privaten, fensterlosen Kindprozess. Ein manueller Serverbefehl oder OpenRGB-Fenster ist nicht mehr erforderlich. Die Verbindung bleibt ausschließlich auf `127.0.0.1:6742` begrenzt. Eine fremd gestartete OpenRGB-Instanz wird nicht übernommen und blockiert OHC-Schreibzugriffe, bis sie beendet wurde.

Start im Terminal:

```bash
~/.local/bin/open-hardware-control
```

## NZXT-USB-Zugriff

Wenn die Kraken erkannt wird, Schreibbefehle aber wegen fehlender Rechte scheitern:

```bash
~/.local/share/open-hardware-control/install-udev-rule.sh
```

Danach die USB-Verbindung der Kraken neu herstellen oder den PC neu starten.

## Deinstallation

Beim universellen ZIP im entpackten Paketordner:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

Bei RPM oder DEB:

```bash
sudo dnf remove open-hardware-control
```

oder:

```bash
sudo apt remove open-hardware-control
```

Persönliche Profile und Einstellungen im Benutzerverzeichnis werden bei einer normalen Paketentfernung nicht gelöscht.


## NCT6687-Mainboard-Lüfterrechte ab 3.4.23.1

RPM/DEB installieren den eng begrenzten Polkit-Helfer automatisch nach `/usr/libexec/open-hardware-control-fan-helper` und die zugehörige Policy nach `/usr/share/polkit-1/actions/`. Die OHC-GUI bleibt als normaler Benutzer aktiv. Bei einer ZIP-/Benutzerinstallation kann der Systemteil ausdrücklich mit `./install-fan-helper.sh` installiert werden. OHC sollte nicht komplett mit `sudo` gestartet werden.
