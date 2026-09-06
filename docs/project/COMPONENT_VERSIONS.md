# Komponenten- und Versionsübersicht – Version 3.4.29.47

## Getestete Referenzkonfiguration

| Komponente | Version / Stand |
|---|---|
| Open Hardware Control by Frelidon | 3.4.29.47 STABLE |
| OHC Wallpaper Engine for KDE | Modul 1.2 · CaptSilver v1.4 kompatibel · Pause/Fortsetzen/Weiter/Ton über Plasmas registriertes `/WallpaperEngine`-D-Bus-Objekt · echter lokaler Zurück-Schritt trotz fehlender Upstream-Zurück-API · DisplayMode 0/1/2 pro Bildschirm · Erststart-Assistent/Fünf-Workshop-Checkliste · offizielle SHA256-verifizierte Fedora-RPM-Installation erst nach zwei Bestätigungen über Polkit/DNF · feste Galerie-Kartenmaße nach Apply-Refresh · lokale Steam-Workshop-/Video-Galerie · Originalwerte als Standard · rücksetzbare optionale Optimierung ohne Plugin-Patches |
| OHC RGB-Effekt-Engine | Modul 1.1 · 10 eigene Effekte · 20 Vorlagen · eingebettete Engine-Schalter · persistente Vorlagenfarben · Gesamthelligkeit · native Kanalergebnisse · begrenzte ENE-DRAM-Startwiederholung |
| OHC Mainboard-Fan-Modul | 3.4.29.47 · Linux hwmon/NCT6687 · kalibrierungspflichtige PWM-Kanäle · sichere PWM/DC-Umschaltung nur über vorhandenes `pwmN_mode` · prozessgebundene Polkit-Helfersitzung · robuste benutzerspezifische Dauerfreigabe mit Entfernen-Funktion · globale/einzelne Leise/Ausbalanciert/Leistung-Vorlagen · Kurven-Reset · Fallback/Firmware-Rückgabe |
| OHC Thermalright-Levita-Modul | Anwendung 3.4.29.47 · Datenoberfläche Modul 1.4 · Display USB `87ad:70db` · TRCC Linux 9.9.12 empfohlen / 9.9.11 hardwarebestätigt · zwei große Ebenengalerien · elf eigene Hintergründe, zwei eigene Datenlayouts und eine eigene 30-Sekunden-Animation · persistente Intensität 25–150 % je Ebene/Design · Orbital-Standard 130 %, Nebula 100 % · sichtbare Format-Einheiten · read-only AMD-GPU-Taktwächter für den 1.000.000-Hz-Grenzfall · ein TRCC-Daemon als einziger USB-Besitzer · Korrekturen nur über Unix-Socket · eigener Ordner mit Ebenenzuweisung/Favoriten · transparente Zwei-Ebenen-Live-Vorschau · kombinierte Design-/Notch-Maske · ein Cache-Theme pro vollständigem Design · begrenzte Wiederholung · read-only `config1.dc` und validiertes Cache-`trcc.json` · Pumpe/Radiator über getrennt bestätigte Mainboard-PWM-Header |
| OpenRGB | optional installiert · von OHC verwalteter fensterloser Kindprozess auf `127.0.0.1:6742`; alle Qt-Clientprozesse offscreen; Fedora-44-Test mit `1.0~rc2`; Direct-Farben über eigenen OHC-SDK-Helfer statt CLI-ApplyOptions |
| OHC OpenRGB-SDK-Helfer | Protokoll 4–5 · validiertes `RESIZEZONE` · Controller-/Zonensynchronisation · Modus-/Farbrücklesung · Loopback-only · begrenzte Geräte-/LED-/Paketwerte |
| OHC Desktop Shell | 1.0 (lokal, ohne Hardwarezugriff) |
| OHC Desktop-Backupformat | Schema 2, SHA-256-Export |
| OpenLinkHub | 0.9.0 (Zielsystem; realer Integrationstest ausstehend) |
| Python | 3.14.6 |
| PySide6 | 6.11.1 |
| Qt | 6.11.1 |
| Qt SVG | 6.11.1 (`qt6-qtsvg`) |
| Qt 6 D-Bus | Fedora: `qdbus-qt6` aus `qt6-qttools`; alternative Namen werden erkannt |
| KDE KConfig | `kwriteconfig6` aus `kf6-kconfig` |
| liquidctl | 1.16.0 |
| Pillow | 12.3.0 |
| Distribution | Nobara / Fedora 44 |
| Kernel | 7.1.4-200.nobara.fc44.x86_64 |
| NZXT Kraken 2023 Firmware | 2.0.0 |
| Kraken USB-ID | `1e71:300e` |
| NZXT 2023 RGB Controller USB-ID | `1e71:2012` |
| Thermalright Levita Vision Display USB-ID | `87ad:70db` |
| TRCC Linux | 9.9.12 empfohlen und CLI-/Daemon-kompatibel; 9.9.11 mit Bulk-Handshake 1600×720 und Farbzyklus auf Referenzdisplay bestätigt |

Die Über-Seite zeigt zusätzlich die tatsächlich installierten Laufzeitversionen dynamisch an. Andere Versionen können funktionieren, gelten aber erst nach einem Hardwaretest als geprüft.

Die fünf Maus-SVGs sind eigene Projektgrafiken unter GPL-3.0-or-later; es werden keine externen Bilddateien oder Hersteller-Renderings mitgeliefert.

Die RGB-Effekt-, Geräte-/Gruppen- und NZXT-Validierungslogik ist eigener Projektquellcode unter GPL-3.0-or-later. OpenRGB und dessen Effects Plugin werden nicht mitgeliefert; die Über-Seite liest nur bei vorhandener Installation die lokale OpenRGB-Versionsausgabe.
