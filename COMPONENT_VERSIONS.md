# Komponenten- und Versionsübersicht – Version 3.4.29 INTERN

## Getestete Referenzkonfiguration

| Komponente | Version / Stand |
|---|---|
| Open Hardware Control by Frelidon | 3.4.29 INTERN |
| OHC RGB-Effekt-Engine | Schema/Engine 1 · 10 eigene Effekte |
| OHC Mainboard-Fan-Modul | 3.4.25 · Linux hwmon/NCT6687 · kalibrierungspflichtige PWM-Kanäle · CPU/GPU/Kühlmittel/max/gewichtet · Hysterese/Delay · Leise/Ausbalanciert/Leistung · Fallback/Firmware-Rückgabe |
| OHC Thermalright-Levita-Modul | 3.4.29 · Display USB `87ad:70db` · 1600×720 logisch · TRCC-Backend optional · Pumpe/Radiator über getrennt bestätigte Mainboard-PWM-Header |
| OpenRGB | optional installiert · von OHC verwalteter fensterloser Kindprozess auf `127.0.0.1:6742`; Fedora-44-Test mit `1.0~rc2`; Direct-Farben über eigenen OHC-SDK-Helfer statt CLI-ApplyOptions |
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

Die Über-Seite zeigt zusätzlich die tatsächlich installierten Laufzeitversionen dynamisch an. Andere Versionen können funktionieren, gelten aber erst nach einem Hardwaretest als geprüft.

Die fünf Maus-SVGs sind eigene Projektgrafiken unter GPL-3.0-or-later; es werden keine externen Bilddateien oder Hersteller-Renderings mitgeliefert.

Die RGB-Effekt-, Geräte-/Gruppen- und NZXT-Validierungslogik ist eigener Projektquellcode unter GPL-3.0-or-later. OpenRGB und dessen Effects Plugin werden nicht mitgeliefert; die Über-Seite liest nur bei vorhandener Installation die lokale OpenRGB-Versionsausgabe.
