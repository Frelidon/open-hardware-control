# Open Hardware Control 3.4.29.45

Diese stabile Version veröffentlicht die vollständig geprüfte 3.4.29-Entwicklungsreihe mit Thermalright-Levita-Studio, modernisiertem RGB-Studio, Wallpaper Engine for KDE, sicherer Mainboard-Lüftersteuerung und zahlreichen KDE-/Wayland-Korrekturen.

## Highlight: Thermalright Levita Vision Display

**Open Hardware Control unterstützt jetzt das 1600×720-Display der Thermalright Levita Vision 360 ARGB Black.** Das neue lokale Display-Studio kombiniert eigene Bilder oder Videos mit einer zweiten Ebene für live aktualisierte CPU-, GPU-, RAM- und Zeitdaten. Vorschau und sicherer Testmodus funktionieren ohne USB-Schreibzugriff; die bewusste Hardwareübertragung läuft über das separat installierte GPL-Backend TRCC Linux.

Die integrierte OHC-Galerie enthält elf eigene 1600×720-Hintergründe, zwei vollständige OHC-Datenlayouts und eine 30-sekündige KI-Animation. Sämtliche Motive wurden vom Projektinhaber mit OpenAI-Werkzeugen selbst erstellt. **Keine Thermalright-/TRCC-Herstellerdesigns, Katalogvideos oder importierten Benutzerdateien werden mit OHC veröffentlicht.**

## Letzte Fehlerkorrekturen

- Ein gespeichertes RGB-Startprofil bleibt jetzt vorgemerkt, wenn OpenRGB beim Kaltstart zunächst nur einen Teil des bekannten Gerätebestands meldet. Nach der begrenzten automatischen Nachprüfung wird das Design auf den vollständigen Bestand angewendet.
- Die Modulregisterprüfung folgt dem tatsächlichen `BUILD_CHANNEL` und akzeptiert neben internen Builds nun auch einen korrekt vorbereiteten stabilen Release.
- Der stabile RPM-Build verwendet einen getrennten temporären Quellbaum und kollidiert nicht mehr mit dem gleichnamigen Laufzeit-ZIP-Verzeichnis.
- Der Levita-Videovorschau-Belastungstest beendet und leert zunächst bereits gestartete Aufgaben für gebündelte Medien. Seine 140 synthetischen Videokarten und die Zwei-Worker-Grenze werden dadurch auf schnellen wie langsamen GitHub-Runnern deterministisch geprüft.
- GitHub Actions installiert die vollständige PySide6-/Pillow-/pytest-Testumgebung einschließlich der für Qt notwendigen EGL-Laufzeit.
- Das exakt identifizierte titellose 640×480-Qt-Leerfenster bleibt vor der Anzeige quarantänisiert; normale Dialoge, Auswahlfenster und ComboBox-Popups bleiben unbeeinträchtigt.

## Wichtige Neuerungen seit der letzten öffentlichen Version

- Lokales Thermalright-Levita-Display-Studio mit zwei Ebenen, 1600×720-Vorschau, editierbaren Live-Datenblöcken, Video-Hintergründen, sicherem TRCC-Daemonpfad und unveränderten Importdateien.
- Eigene Offline-Designgalerie mit elf Bildern, zwei Live-Datenlayouts und genau einer deduplizierten 30-Sekunden-Animation – ohne Hersteller- oder TRCC-Katalogmedien.
- RGB-Studio mit eigener verwalteter OpenRGB-Engine, Geräte-/Zonenansicht, persistenten Designs und Farben, nativen Hardwarekanälen sowie begrenzter ENE-DRAM-Kaltstartwiederherstellung.
- Wallpaper Engine for KDE mit schreibgeschützter lokaler Workshop-Galerie, Multi-Monitor-Ziel, Wiedergabe- und Skalierungssteuerung, Originalprofil und vollständig rücksetzbarer optionaler Optimierung.
- Persistente Wahl des Startbildschirms mit sicherem Hauptbildschirm-Rückfall; unter Wayland behält KWin die endgültige Positionierungsentscheidung.
- Kalibrierungspflichtige Mainboard-/Gehäuselüftersteuerung über Linux hwmon/NCT6687 mit Besitzschutz, Watchdog und sicherer Firmware-Rückgabe.
- Neue Hardwarediagnose, konsistente schmale Scrollleisten, überarbeitete Navigation, Projektbranding und erweiterte Geräte-/Sicherheitsdokumentation.

## Sicherheit und Besitzgrenzen

- OpenRGB, OpenLinkHub, NZXT, Mainboard-PWM und TRCC bleiben getrennte, koordinierte Besitzerpfade.
- Steam-Workshop-Dateien, CaptSilver-Installation und importierte TRCC-Medien werden nicht verändert.
- Hardware-Schreibzugriffe bleiben bestätigungs-, konflikt- und testmodusgeschützt; Zugangsdaten werden nicht gespeichert.

## Pakete

Die Veröffentlichung enthält das universelle ZIP, RPM, DEB, Quellarchiv, vollständige Entwicklerpaket und Local-AI-Git-Bundle. Alle Dateien werden gemeinsam über `SHA256SUMS` geprüft.
