# Native RGB-Einrichtung und Wiederherstellung · 3.4.29.169

## Was sich geändert hat

OHC berechnet seine Designs auf einer festen monotonen 60-Hz-Zeitbasis.
Tempo verändert die Bewegung, nicht den Grundtakt. Das optionale native Plugin
übernimmt vollständige Frames direkt innerhalb von OpenRGB. Je Controller
arbeitet genau ein dauerhafter Arbeiter; höchstens der neueste Frame wartet.
Ein langsamer Mainboardtransfer hält damit weder Lüftercontroller noch RAM auf.
Ohne Plugin bleibt der parallele, geordnete Loopback-SDK-Arbeiter verfügbar.

**Wichtig:** Die plattformneutralen ZIP-/DEB-/RPM-Pakete enthalten keinen
universellen OpenRGB-Binärtreiber. OpenRGB bleibt eine getrennte Komponente.
Plugin und OpenRGB müssen gegen dieselbe Qt-Hauptversion und kompatible
Bibliotheken gebaut werden. Ein Qt-6-Plugin kann nicht in Qt-5-OpenRGB geladen
werden. Eine aktuelle OHC-Installation allein ersetzt keinen MSI-Treiber.

Unter Ubuntu wurden OpenRGB 1.1, Plugin-API 5 und System-Qt 6.11.2 gemeinsam
gebaut und am Gerät geprüft. Airgoo erreicht im USB-Messfenster 58,52 komplette
Frames/s statt 3,83. Der MSI-761-Patch reduziert vier langsame Reports auf die
tatsächlich geänderte Zone; diese erreicht hier etwa 10,64 Frames/s.
Das sind **keine garantierten physischen 60 FPS auf jedem Gerät**. Der
Eigentümer bestätigt flüssige Gehäuse-/GPU-Bewegung und korrekte GPU-Farben.
Fedora behält seinen bestehenden SDK-/Systembackendpfad; ein realer Fedora-
Hardwaretest des nativen Qt-6-Pfads steht noch aus.

## Bestehende Installation aktualisieren

1. Persönliche OHC-Profile, Einstellungen und private Enginekonfiguration
   sichern. Keine alten LED-Zahlen auf Verdacht löschen oder neu schätzen.
2. OHC über **Beenden** im Tray ordentlich schließen; das Fenster-X kann nur
   ausblenden. Andere RGB-Programme für dieselben Geräte ebenfalls schließen.
3. Das passende Paket nach [INSTALL.md](../INSTALL.md) installieren. Bestehende
   Benutzerprofile und separat installierte Backends bleiben erhalten.
4. OHC normal, niemals vollständig mit `sudo`, starten. Im RGB Studio die
   Schreibfreigabe und die gewünschten Geräte prüfen.
5. LED-Anzahl und Lüftersegmentierung in **Gehäuse** bestätigen. Nicht belegte
   Anschlüsse bleiben bei null; keine fremden Beispielwerte übernehmen.

## Nativen Ubuntu-Unterbau nachbauen

Diese Schritte sind für ein Entwicklerpaket, Quellarchiv oder Git-Checkout
gedacht. Sie installieren nichts automatisch und erfordern passende offizielle
Distributionspakete. Die Qt-5-Abhängigkeiten der allgemeinen OpenRGB-Anleitung
nicht mit diesem ausdrücklich gegen Qt 6 gebauten Plugin mischen.

```bash
sudo apt install git build-essential pkg-config cmake ninja-build patch \
  qt6-base-dev qt6-base-dev-tools qt6-tools-dev-tools \
  nlohmann-json3-dev libusb-1.0-0-dev libhidapi-dev libmbedtls-dev
```

Bei unauflösbaren APT-Abhängigkeiten abbrechen und die Distributionsquellen
reparieren lassen. Keine pauschalen Bibliotheks-Downgrades erzwingen.
Im OHC-Projektordner einen neuen, leeren Arbeitsordner außerhalb des Repositorys
verwenden und OpenRGB auf dem tatsächlich getesteten Commit bauen:

```bash
OHC_SOURCE="$PWD"
RGB_WORK="$(mktemp -d)"
git clone https://gitlab.com/CalcProgrammer1/OpenRGB.git "$RGB_WORK/OpenRGB"
git -C "$RGB_WORK/OpenRGB" checkout 8e16de27858cf2be6af54a33ce003df74cb9fd3e
git -C "$RGB_WORK/OpenRGB" apply --check "$OHC_SOURCE/tools/openrgb/msi-761-dirty-zones.patch"
git -C "$RGB_WORK/OpenRGB" apply "$OHC_SOURCE/tools/openrgb/msi-761-dirty-zones.patch"
cd "$RGB_WORK/OpenRGB"
qmake6 OpenRGB.pro CONFIG+=release CONFIG+=noudev
make -j2
cd "$OHC_SOURCE"
cmake -S src/native/openrgb -B "$RGB_WORK/plugin" -G Ninja \
  -DOPENRGB_SOURCE_DIR="$RGB_WORK/OpenRGB"
cmake --build "$RGB_WORK/plugin" -j2
```

Der Patch behält Reportformat, LED-Grenzen und USB-Eigentümer unverändert.
`CONFIG+=noudev` ersetzt keine erforderlichen Benutzerzugriffs-/udev-Regeln.
Vor Installation OHC ordentlich beenden und die bisherigen Dateien separat
sichern. Der geprüfte Ubuntu-Zielpfad lautet:

```bash
sudo install -d -m 0755 /usr/local/lib/open-hardware-control-backends/openrgb-1.1/usr/bin
sudo install -m 0755 "$RGB_WORK/OpenRGB/OpenRGB" \
  /usr/local/lib/open-hardware-control-backends/openrgb-1.1/usr/bin/OpenRGB
install -d -m 0700 "$HOME/.config/FloriLinuxTools/Open Hardware Control/rgb-engine/plugins"
install -m 0755 "$RGB_WORK/plugin/OHCNativePlugin.so" \
  "$HOME/.config/FloriLinuxTools/Open Hardware Control/rgb-engine/plugins/OHCNativePlugin.so"
```

Alle Vorfahren des privilegierten Backendpfads müssen root-owned und dürfen
nicht gruppen-/weltbeschreibbar oder durch Benutzer-Symlinks ersetzbar sein.
Keine bestehenden Systemverzeichnisse pauschal per `chmod` verändern.
Qt-Systembibliotheken und ihr `offscreen`-Plattformplugin müssen vorhanden sein.
OHC wählt diesen festen privaten Backendpfad ausschließlich unter Ubuntu und
bei bestandener Vertrauensprüfung. Fedora wird dadurch nicht umgestellt.

## Bedienung und Kontrolle

- **PLAY** startet die ausgewählten Designs; **STOPP** hält die Bewegung an und
  erhält Auswahl, Farben, Helligkeit und Tempo.
- Änderungen an Haupt-/Nebenfarbe gehören zum gewählten Design. Einzelfarbe
  und Design-Standard-Reset sind getrennte Aktionen.
- **Wenn das Programm aus ist** bestimmt Weiß, Wunschfarbe oder einen vom
  Gerät gemeldeten Rainbow-Modus. Nicht unterstützte Geräte verwenden die
  gewählte Einzelfarbe. Minimieren/Tray löst diesen Abschluss nicht aus.
- Die Sapphire-Option **External Control** schaltet auf den physischen ARGB-
  Eingang um. Sie ist kein eigener Direct-LED-Treiber. Die bestätigte
  Mainboardroute muss ausgewählt und mit der richtigen LED-Zahl konfiguriert sein.
- `RGB-NATIVE` protokolliert API-Übergaben, Fehler und ersetzte Frames.
  Ersetzte Frames sind bei langsamen Geräten erwartbar; alte Frames werden
  nicht später als ruckelnder Rückstau abgespielt. API-Zahlen sind keine
  optische Rücklesung. Erst die aktuelle Generation bestätigt ein Design.

## Fehler und Sicherungen

Bei `Could not find ... offscreen/xcb` zuerst das zur Engine passende
Qt-Plattformplugin prüfen. Niemals wahllos PySide- und System-Qt-Verzeichnisse
mischen. Bei fehlenden Geräten den vollständigen Bestand neu erkennen lassen,
ohne gespeicherte Identitäten, Profile und LED-Topologien zu löschen.

Das Levita-LCD bleibt beim bisherigen TRCC-Daemon. Es bekommt keinen neuen
RGB-Schreibweg und keine geänderte Bildrate. Bei einer OHC-eigenen blockierten
Instanz existiert die begrenzte Wiederherstellung; fremde Besitzer werden nicht
beendet. USB-Diagnose mit `strace` nicht als normalen Dauerstart verwenden:
ein verfolgter Prozess kann privilegierte Helfer nicht normal starten.

Release-Archive enthalten Programmcode, Native-Plugin, MSI-Patch, Tests und
Anleitung. Persönliche Profile und die exakten lokal gebauten Binärdateien
gehören zusätzlich in eine private lokale Sicherung, nicht auf GitHub.
Siehe [Release-Sicherungen](../project/RELEASE_BACKUP_POLICY.md).
