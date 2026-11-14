# Installation unter Linux

Diese Anleitung gilt für **Open Hardware Control by Frelidon 3.4.29.177 STABLE**.
Lade die Pakete aus dem [GitHub-Release](https://github.com/Frelidon/open-hardware-control/releases/tag/v3.4.29.177)
und prüfe sie mit der dortigen `SHA256SUMS` (`sha256sum -c SHA256SUMS`).
Vor einem Update OHC über **Beenden** im Tray ordentlich schließen; ein
Fenster-X kann die Anwendung nur ausblenden. Bestehende Profile, LED-Topologien,
Displaydesigns und getrennt installierte Backends werden nicht zurückgesetzt.

## Fedora und Nobara

Empfohlenes RPM-Paket:

```bash
cd ~/Downloads
sudo dnf install ./open-hardware-control-3.4.29.177-1.noarch.rpm
```

Alternativ das universelle ZIP verwenden. Die benötigten Pakete lauten:

```bash
sudo dnf install liquidctl python3-pyside6 python3-pillow qt6-qtsvg polkit
```

## Debian, Ubuntu und Linux Mint

Empfohlenes DEB-Paket:

```bash
cd ~/Downloads
sudo apt install './open-hardware-control_3.4.29.177_all.deb'
```

Alternativ das universelle ZIP verwenden. Die benötigten Pakete lauten:

```bash
sudo apt update
sudo apt install liquidctl python3-pyside6.qtwidgets python3-pyside6.qtsvg python3-pil polkitd pkexec
```

## Arch Linux, Manjaro und EndeavourOS

```bash
sudo pacman -S --needed liquidctl pyside6 python-pillow qt6-svg polkit unzip
cd ~/Downloads
unzip open_hardware_control_v3_4_29_177.zip
cd open-hardware-control-3.4.29.177
chmod +x install.sh
./install.sh
```

## openSUSE Tumbleweed und Leap

```bash
sudo zypper install liquidctl python3-pyside6 python3-Pillow libQt6Svg6 polkit unzip
cd ~/Downloads
unzip open_hardware_control_v3_4_29_177.zip
cd open-hardware-control-3.4.29.177
chmod +x install.sh
./install.sh
```

Die verfügbaren Python-Paketnamen können sich zwischen Leap- und Tumbleweed-Versionen unterscheiden. Falls `zypper` einen Namen nicht findet, suche mit `zypper search pyside6`, `zypper search Pillow` und `zypper search liquidctl` nach dem Namen deiner installierten Ausgabe. Das Installationsskript zeigt fehlende Komponenten an und fügt keine fremden Paketquellen hinzu.

## Universelles Installationspaket

Für alle oben genannten Distributionen:

```bash
cd ~/Downloads
unzip open_hardware_control_v3_4_29_177.zip
cd open-hardware-control-3.4.29.177
chmod +x install.sh
./install.sh
```

Die vorhandene Version wird aktualisiert. Danach findest du **Open Hardware Control by Frelidon** im Anwendungsmenü.

## Optionales Thermalright-Levita-Backend

Für das Levita-Display wird TRCC Linux 9.10.4 empfohlen. Es bleibt separat installiert und ist keine harte Abhängigkeit des OHC-Pakets, damit Systeme ohne Thermalright-Display keine fremde Paketquelle benötigen. Version 9.10.4 räumt abgeschlossene Daemon-IPC-Worker fortlaufend auf und besitzt den Video-/Sensor-Takt selbst; OHC 3.4.29.177 erkennt diese erfolgreiche Übergabe. Aktualisiere TRCC über dessen offizielle Paketquelle beziehungsweise Release-Anleitung, bevor du die Levita-Hardware in OHC testest.

Der vollständige Modell-/Geometrie-Handshake und Farbzyklus wurde mit TRCC Linux 9.9.11 bestätigt; die dauerhafte 1600×720-Designausgabe und stabile Daemon-Ressourcennutzung zusätzlich mit 9.10.4. OHC startet niemals einen zweiten Levita-USB-Besitzer neben dem TRCC-Daemon.

## Geprüfte Versionsstände und Sicherheitsbasis

Der lokale RGB-Nachweis vom 10.11.2026 verwendet OpenRGB 1.1 mit dem OHC-
Plugin 0.2, MSI-Dirty-Zone-Patch und System-Qt 6.11.2. Das ist ein gesonderter
nativer Aufbau, keine Aussage über die aktuellste Distributionsversion.
Unter Ubuntu wird SDK 6 ausdrücklich unterstützt; der bestehende Standard-
SDK-Pfad anderer Distributionen bleibt erhalten. TRCC 9.10.4 bleibt das getrennte
Levita-Backend. LACT 0.10.1 ist die Mindestversion für GPU-Schreibzugriffe.
Die Ubuntu-Liveprüfung ersetzt keinen Fedora-Hardwaretest. Frühere Auditstände
stehen in [COMPONENT_VERSIONS.md](project/COMPONENT_VERSIONS.md).

OHC installiert keine fremden Binärdateien stillschweigend und ersetzt keine Systembibliotheken. Nutze bevorzugt die Sicherheitsaktualisierungen deiner Distribution. OpenLinkHub besitzt zusätzlich den ausdrücklich zu bestätigenden, SHA-256-geprüften OHC-Aktualisierungsweg; TRCC bleibt nach seiner offiziellen Anleitung separat installiert.

## Optionale Pakete für KDE-Desktop-Designs

Open Hardware Control erkennt fehlende Werkzeuge automatisch und bietet ihre Installation nach Bestätigung an.
Unter Fedora 44 werden `kf6-kconfig` und `qt6-qttools` verwendet. Das darin enthaltene Programm heißt dort
`qdbus-qt6` und wird seit Version 3.1.1 direkt erkannt. Ein manueller Kompatibilitätslink ist nicht erforderlich. Version 3.2.0 bietet zusätzlich QtNetwork/QtDBus für die lokale Windows-8/8.1-Oberfläche an.

Die automatische Zuordnung unterstützt außerdem `libkf6config-bin`/`qdbus-qt6` für APT,
`kconfig`/`qt6-tools` für Pacman und `kf6-kconfig`/`qt6-tools-qdbus` für Zypper. Diese Pakete sind optional:
Ohne sie bleiben NZXT- und OpenLinkHub-Steuerung vollständig verfügbar.

## Automatisch verwaltetes OpenRGB-Backend für das RGB-Studio

Für den neuen nativen Pfad zuerst die vollständige
[RGB-Einrichtungs- und Wiederherstellungsanleitung](hardware/NATIVE_RGB_SETUP.md)
lesen. OHC-Pakete enthalten keinen universellen OpenRGB-Binärtreiber. Ohne
passend gebautes Plugin bleibt der parallele SDK-Pfad verfügbar. Vorhandene
private Engine-/Plugin-Installationen werden nicht ersetzt.

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
