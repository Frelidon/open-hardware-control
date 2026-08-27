# Open Hardware Control by Frelidon v3.1.0 INTERN

Diese Version ist ein interner Teststand und wird noch nicht als öffentliches GitHub-Release veröffentlicht.

## Neu

- neuer Bereich **System → Desktop-Designs** für KDE Plasma 6
- Windows-11-artige und macOS-artige Plasma-Anordnung, jeweils hell oder dunkel
- schreibfreie Änderungsvorschau und ausdrücklicher Bestätigungsdialog
- datiertes Backup der berührten KDE-/Plasma-Konfiguration vor jeder Änderung
- automatisches Rollback bei Fehlern und manuelle Wiederherstellung des letzten Backups
- ausschließlich vorhandene KDE-Breeze-Komponenten, Noto Sans und zwei eigene GPL-SVG-Hintergründe
- keine externen Theme-Downloads, Paketquellen, Administratorrechte oder proprietären Microsoft-/Apple-Assets
- interne ZIP-, DEB- und RPM-Kennzeichnung sowie gesperrte öffentliche Veröffentlichungshelfer

## Weiter enthalten

- NZXT-Kraken-LCD-, Pumpen-, Radiatorlüfter- und RGB-Steuerung
- CPU-basierte Kühlkurven mit sicherem Hardwarefallback
- GIF-/Hardwareanimation mit koordinierter USB-Übergabe
- originale Flüssigkeitstemperaturanzeige beim echten Beenden
- OpenLinkHub-Geräteansicht und validierte Corsair-Schreibaktionen
- anklickbare Mausgrafik, direkte Tastenzuweisung und begrenzte fensterlokale Makroaufnahme
- getrennte LCD-Farben/-Größen sowie Celsius/Fahrenheit
- Tray-Autostart und verzögerte LCD-Profilwiederherstellung

## Testschwerpunkt

Vor einer öffentlichen Version müssen Windows-11- und macOS-Anordnung auf einem echten Fedora-KDE-Plasma-6-System angewendet und jeweils wiederhergestellt werden. Zusätzlich bleiben die bestehenden NZXT- und OpenLinkHub-Hardwaretests erforderlich.

---

## English summary

Open Hardware Control 3.1.0 INTERNAL adds reversible Windows-11-style and macOS-style layouts for KDE Plasma 6. Previewing is read-only; applying requires a separate confirmation and creates a timestamped backup first. Failures automatically restore that backup. The module uses installed KDE Breeze components, Noto Sans and original GPL SVG wallpapers, with no external theme downloads or proprietary Microsoft/Apple assets. Existing NZXT Kraken, Corsair/OpenLinkHub, mouse assignment, macro, LCD, Fahrenheit and CPU-curve features remain included.
