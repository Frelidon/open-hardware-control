# Komponenten- und Versionsübersicht – Version 3.4.29.167

## OHC-Modulstand und aktuelle Ubuntu-Konfiguration

Stand 06.10.26: Die unten ausdrücklich als Ubuntu angegebenen externen Versionen wurden auf dem aktuellen Ubuntu-PC geprüft. Versions-/Importprüfungen bestätigen Installation und Benutzerzugriff, nicht die optische Anzeige oder die physische Steuerung jedes Geräts. Frühere Fedora-Hardwaretests sind separat als historische Referenz aufgeführt.

OHC `.156` ist installiert und korrigiert bedienbare LED-Verlaufsentwürfe,
räumliche Richtung und animierte RGB-Lüftervorschau. Der volle Release-Wächter
besteht mit 1.301 Tests und fünf Untertests. DPKG, alle 365 Python-Quellen,
unveränderte private Profile vor Neustart und enge nichtinteraktive Berechtigungen
sind geprüft. Automatischer RGB-/LCD-Start und Videofortschritt sind protokolliert.
Reale Fedora-Hardware und optische Kontrolle bleiben gesondert offen.
Automatischer RGB-Start und Levita-Videofortschritt sind auf Ubuntu protokolliert,
jedoch keine optische Bestätigung. Die reine Paketstage-Rechtekorrektur für
frische DEB-Installationen und der kanonische Geräteimport für erfolgreiche
LCD-Statusabfragen sind abschließend gebaut, unabhängig geprüft und installiert.
Der Release-Wächter besteht mit 1.132 Tests und fünf Untertests;
DEB-/RPM-Verzeichnisse sind root-owned 0755.
Die verifizierten externen Ubuntu-Komponenten bleiben unverändert. Der neue
Startprofil-/USB-Konfliktschutz ist keine neue Hardwarefreigabe und kein
behaupteter erfolgreicher Live-Test auf Fedora.

| Komponente | Version / Stand |
|---|---|
| Open Hardware Control by Frelidon | 3.4.29.167 STABLE · öffentlicher OHC-eigener Designkatalog, sichtbare unabhängige Feature-Reifegrade/-Versionen, hardwareunabhängiger Levita-UI-Test, zeitunabhängige Vorschauprüfung und zuverlässiges Ausblenden eigener LCD-Medien ohne TRCC-Systemkatalog; SDK-6-Profilmeldung und TRCC-GPU-Taktgrenzschutz aus `.158` erhalten; Fedora-Liveprüfung und optische Kontrolle bleiben offen |
| OHC Feature Lifecycle | Modul 1.0 · reine zentrale Darstellungsmetadaten; aktiviert/deaktiviert keine Funktion und verändert weder Einstellungen noch Hardwarebesitz |
| OHC Snapshot-Manager | Modul 1.0 · read-only Distribution-/Dateisystem-/Backend-/Snapper-/Btrfs-Erkennung · GameMode/Gamescope/Programmliste/KDE-Vollbild plus optionale Mehrkern-CPU-und-GPU-Hysterese · moderne gekoppelte Regler-/Zahlenkarten · manuelle Zeit-/Dauersperre · feste Snapper-Timer und begrenzte Btrfs-Discard-Werte ausschließlich über eigenen root-owned Polkit-Helfer · atomarer JSON-Metadatenexport · einzeln bestätigtes Löschen ab Snapshot 1 · kein Ein-Klick-Rollback und keine beliebigen Befehle/Pfade |
| OHC GPU-Steuerung | Modul 1.0 · LACT 0.10.1+ als optionale lokale API · responsives Drei-Spalten-Cockpit mit vertikalem Scroll-Rückfall für kleine Fenster · vollständige umbrochene Lüftertexte · fünf direkt ziehbare und zahlengekoppelte Lüfterpunkte · lokaler GPU-Bildimport/-reset · reiner Lüftertest garantiert ohne Grafiklast · Leistungslimit standardmäßig höchstens LACT-Werkswert, darüber explizite Freischaltung · Kurztest mit automatischer LACT-Rückstellung · nur bestätigte Werte dauerhaft · CoolerControl-GPU-Lüfter muss freigegeben sein · OpenRGB-RGB getrennt |
| OHC Prozesslaufzeit / LCD Runtime | Module 1.1 / 1.1 · bestätigte Sendefortschritte, Befehls-/Framefristen, isolierte Spielerkennung und privates Moduljournal |
| OHC Levita-Daemongesundheit | Modul 1.1 · reine Klassifizierung ausdrücklicher USB-Besitzerkonflikte und primärer Backendfehler · Ubuntu stoppt nur eigene Wiederholungen und hält gespeichertes Design unverändert · kein automatisches Beenden fremder Programme; Fedora-Rückstellung unverändert |
| OHC Laufzeitprotokoll / Absturzwiederherstellung | Module 1.0 / 1.0 · sichtbarer 60-Minuten-Ringpuffer · 30.000-Zeilen-/4-MiB-Hartgrenze · vollständige aktuelle/vorherige Sitzung · privates rotiertes 2-MiB-Fehlerlog · privater 2-MiB-Absturzring mit exakt fünf Minuten Wiederherstellung nach unvollständigem Ende · Fatal-Signal-Python-Stacks aller Threads · Diagnoseauszug nur nach ausdrücklicher Sammlung |
| OHC-Lokalisierung | Modul 1.0 · je ein vollständiges Laufzeitmodul für Deutsch, Englisch, Spanisch und Französisch · 2.154 gemeinsame Nachrichtenquellen je Sprache einschließlich LED-Pfad-Hinweis, USB-Besitzerstatus, wiederhergestellter Designs, Snapshot-Manager, GPU, Hardware-Checker, Gehäuse-Raumdaten, räumlicher RGB-Designs, LED-Assistent, TRCC-Installation, CPU-Automatik und Hilfe · vollständiger Offscreen-Sprachwächter |
| OHC Hardware-Checker | Modul 1.0 · begrenzte read-only CPU-/SMT-/Virtualisierungs-/Board-/PCIe-GPU-/NVMe-/RAM-Erkennung · Polkit-eigene DMI-Abfrage ohne Passwortzugriff · optionaler ausdrücklicher vkmark-, glmark2- oder Vulkan-vkcube-Lasttest · keine BIOS-, Takt-, Spannungs-, Lüfter-, Firmware- oder SSD-Schreibänderung |
| OHC Anwendungsabschluss | Modul 1.1 · X/Fensterschließen lässt OHC im Tray weiterlaufen oder minimiert ohne Tray in die Taskleiste · nur sichtbares manuelles Beenden im Tray-Kontextmenü führt die geordnete Hardware-Rückgabe und Qt-Beendigung aus · kontrollierte TRCC-Neustarts übertragen die exakt geprüfte Kindprozesszuordnung auf die neue PID · unabhängiger Lebenszeitwächter für exakte OHC-Kinder und protokollierte Fehler · keine fremden Prozesssignale |
| OHC UI-Themes | Modul 1.0 · getrennte helle/dunkle/Studio-Paletten und semantische Stilwerte · reine getrennte Qt-Stilfragmente · registrierter Erweiterungspunkt für zukünftige Designs · Systemmodus übernimmt native Qt-Palette |
| OHC-Fensterleiste / Platzierung | Leiste 1.2 · Platzierung 1.5 · eigene Titelleiste · 48×42-Pixel-Schließfläche bis in die Ecke · Qt-Systembewegung/-größenänderung für Wayland/X11 ohne Abfangen der Fensterknöpfe · sichere separate Normalgeometrie und Startzustandswahl · Haupt-/feste Anschlusswahl · fertiger Zustand im ersten sichtbaren Frame · KWin-Bestätigung des tatsächlichen Wayland-Ausgangs mit PID-/Titelbindung und begrenztem Hilfsprozess |
| OHC UI-Leistung / SSD-Cache | Modul 1.1 · leichte linke Navigationseffekte ohne Seitenaufnahme · verborgene Videovorschauen entladen Decoder/Frames · Cachepflege erst nach Eingaberuhe, mit Nice 15, Idle-I/O-Priorität und kooperativen Portionen · 0/0,5/1/2/4-GiB-Budget nur für regenerierbare Kataloge/Vorschaubilder · keine Original- oder Hardwaredateien |
| OHC-PC-Gehäuseprofile | Modul 1.5 · responsive Spalten/Reiter ohne innere Scrollleiste und mit ausdrücklichem Entwurfsabschluss · fähigkeitsabhängige Topologie und 30 originale Schema-Startvorlagen · vollständiger validierter, nicht schreibender Profil-Snapshot für ARGB-Routen, Lüfter-/LED-Zahlen, Geräte/RAM, LED-Wege sowie CPU_FAN-/PUMP_FAN-/Gehäuse-PWM-Plätze · konfliktbehaftete Zuordnungen nur nach Bestätigung · räumliche Richtung/Tempo und echter LED-Reihenfolgeeditor · keine erfundenen Maße, keine Herstellerbilder und keine Hardwarezuordnung durch Raumdaten |
| OHC Navigationseinstellungen | Modul 1.0 · vollständige zweispaltige Kartenliste der optionalen Seitenmodule mit Symbol, Statuspunkt, Schalter und Wiederherstellung aller Bereiche · Sidebar und Einstellungen bleiben synchron · Übersicht, Navigationsanker und Hilfe bleiben erreichbar · Ausblenden startet oder stoppt keine Hardware |
| OHC-Anwendungsaktivierung | Modul 1.0 · privater lokaler Socket mit fester `show`-Nachricht · bestehende Prozesssperre bleibt Hardware-Autorität · Desktop-Starttokens nur bei `--autostart` unterdrückt |
| OHC Reaktionsfähiger Start | Modul 1.0 · Geräteinitialisierung nach erstem Qt-Zyklus · zusammengefasste CoolerControl-Prüfung außerhalb des GUI-Prozesses · unbekannter Besitzerstatus fail-closed |
| OHC Display-Effekte | Modul 1.11 · sichtbare Layout-Videos und bestätigte Vorschaukopie · neu gerenderte Lichtbänder · prozeduraler Rauch · responsive grafische Ebene-1- und Sensorlayout-Kacheln · fünf abstrakte Fremddesigns × vier Farbvarianten · 15 menschenfreie Natur-/Weltraumclips · acht aus 3200×1440 übersampelte OHC Light Bands · direkte Thermalright-Firmware-Rückgabe · kein eigener paralleler TRCC-/USB-Schreibpfad |
| OHC Responsive Galerien / LCD-Medienmanager | Module 1.0 / 1.0 · tatsächliche Viewportbreite bis zwölf Spalten · mehrere lokale Ordner und Einzelbilder/-videos · eigene Anzeigenamen und nicht-destruktive Ausblendungen · lesbare TRCC-Kategorienamen · keine Veränderung oder Auslieferung externer Quelldateien |
| OHC Bereichs-Unterreiter | Modul 1.0 · wiederverwendbare browserähnliche Unterreiter · stabile Seiten-IDs · mehrere Leisten und Seitenleiste bleiben synchron · keine Hardwareabhängigkeit |
| OHC OpenLinkHub-Update | Modul 1.0 · offizieller fester GitHub-Release-Endpunkt · vorhandene DNF-/APT-Quellen oder streng erkannter Benutzerdienst · veröffentlichte SHA-256 · Backup/Rollback · ausdrückliche Bestätigung |
| OHC Wallpaper Engine for KDE | Modul 1.3 · CaptSilver v1.4 kompatibel · Pause/Fortsetzen/Weiter/Ton über Plasmas registriertes `/WallpaperEngine`-D-Bus-Objekt · DisplayMode 0/1/2 pro Bildschirm · lokalisierter Assistent mit bestätigter KDE-Hilfspaketprüfung · offizielle SHA256-verifizierte Fedora-RPM-Installation erst nach zwei Bestätigungen über Polkit/DNF · zentral zwischengespeicherter Workshop-Katalog und Vorschaubilder · Steam-Originale unverändert |
| OHC Profile Bundle | Modul 1.0 · vollständiger privater ZIP-Export/Import mit typisierten Einstellungen, Profilen, Gehäuse/RGB/PWM/Lüftermodellen/LED-Verläufen und Medien · Datei-Hintergrundprozess · Pfad-/SHA-Prüfung und Rückfallkopie · Bestätigung beim nächsten Start und erneute Hardwarefreigabe |
| OHC RGB-Effekt-Engine | Modul 1.15 · 13 eigene Algorithmen und 34 Vorlagen einschließlich sechs räumlicher Designs und vier wiederhergestellter OHC Originals · kompakte responsive Galerie mit bis zu sechs Karten · synchronisierte Navigation/Kategorieauswahl · einstellbarer räumlicher Ablauf mit Tempo, acht Laufrichtungen und echter LED-/Lüfterreihenfolge · laufende Effekte ausschließlich mit vollständigem Geräteframe · Sichttests mit Rückstellung · native GPU-Animationen als Standard · expliziter profilfähiger ARGB-Steuerweg und begrenzter manueller LED-Zonen-Editor |
| OHC Hardware-Unterbauten | Modul 1.0 · persistente Automatik-/Direktauswahl · TRCC Linux für Levita · OHC Linux-hwmon für Mainboard-PWM · ausdrückliche Auswahl fällt bei Nichtverfügbarkeit nicht still zurück · kommende Adapter deaktiviert |
| OHC NCT6687-Treiber-/MOK-Assistent | Modul 1.1 · getrennte feste Abhängigkeitsbefehle für Ubuntu, Fedora und Arch Linux anhand `/etc/os-release` · Ubuntu-Aktualisierung/Installation getrennt · vorhandener fester Git-Checkout nur per `pull --ff-only` · gemeinsame Upstream-/DKMS-Schritte · MSI-X870-Optionen nur bei passender DMI-Erkennung · optionale per-user Polkit-Dauerfreigabe als fünfter Schritt · asynchroner read-only Secure-Boot-/MOK-/Modulstatus · kein Passwortzugriff, automatischer Neustart oder Secure-Boot-Umgehung |
| OHC Temperaturverlauf | Modul 1.2 · kompakter CPU/GPU/Kühlmittel-Verlauf plus eigene Kühlungs-Unterseite · gruppierte read-only Linux-hwmon-Sensoren · höchstens 24 Stunden/28.800 Messpunkte im RAM · lokales Datum/Uhrzeit · skalierbare Splitter · ausdrücklicher CSV-/JSON-Export frei gewählter Zeiträume/Sensoren · keine automatische Persistenz und kein Steuerungsbesitz |
| OHC Kühlungssicherheit | Modul 1.0 · modellbezogene Untergrenzen an Regler-, Profil-, Kurven- und finaler Schreibgrenze · Levita vorsichtig 50 % Pumpe/25 % Radiator, da Thermalright nur Maximaldrehzahlen veröffentlicht · vorhandene NZXT-Bereiche bleiben erhalten |
| OHC Kühlungszustand | Modul 1.0 · reine Startprofilrichtlinie trennt bekannte alte NZXT-Assistentenwünsche nur auf bestätigtem Ubuntu/Levita ohne bereites NZXT vom expliziten PC-Startprofil · Pendingwert und nutzereigene Kühlung bleiben erhalten · keine PWM-Schreibfreigabe; Fedora-/NZXT-Guard unverändert |
| OHC Mainboard-Fan-Modul | 3.4.29.80 · Linux hwmon/NCT6687 · freundliche eindeutige Headernamen ohne doppelte PWM-Angabe · kalibrierungspflichtige PWM-Kanäle · schrittweiser Zuordnungsassistent mit direktem nächsten Lüfter · vollständiges Zurücksetzen aller Gehäuselüfter-Zuordnungen bei erhaltenen Kurven · persistente und sichtbar blau markierte Automatik/Schnellprofile · Backend-Auswahl und asynchroner fail-closed Besitzerstatus · 100-%-Leistungs-Override · rückstellender 0-%-/10-s-Stopptest je Gehäuselüfter · sichere PWM/DC-Umschaltung nur über vorhandenes `pwmN_mode`, sonst BIOS-Erklärung · prozessgebundene Polkit-Helfersitzung · automatische Kurvenänderungen als gebündelte Zustands-/60-s-Heartbeat-Zeile · Fallback/Firmware-Rückgabe |
| OHC Thermalright-Levita-Modul | Anwendung 3.4.29.80 · nicht vorhandene Kühlmittelquelle wird weder angezeigt noch angeboten · lesbarer separater Sicherheitshinweis · Datenoberfläche Modul 1.7 · Daemongesundheit Modul 1.1 · automatische und manuelle streng validierte Wiederherstellung · sichtbarkeitsgebundene Galerien/Vorschauen · LCD-Medienmanager Modul 1.0 · Leistung/Spielerkennung Modul 1.1 mit Zehn-Sekunden-Abfrage · 15 LCD-FPS Standard, 60 nur experimentell · Abschaltwächter Modul 1.0 mit Stopp eines OHC-eigenen Daemons beim Ende · Display-Effekte Modul 1.11 · Display USB `87ad:70db` · ein TRCC-Daemon als einziger USB-Besitzer |
| Qt Multimedia | PySide6 QtMultimedia · lokaler H.264-Lesepfad ausschließlich für sichtbare Display-Effektvorschau |
| OpenRGB | Ubuntu: 1.0 · SHA256-geprüftes offizielles portables Release im root-owned privaten Backend-Verzeichnis `/usr/local/lib/open-hardware-control-backends/openrgb-1.0` · Versionsaufruf als normaler Benutzer geprüft · OHC nutzt SDK-Protokoll 6 auf Ubuntu, Fedora-Kompatibilität bleibt bei Protokoll 5 · von OHC verwalteter fensterloser Kindprozess auf `127.0.0.1:6742`; Direct-Farben über eigenen OHC-SDK-Helfer · Ubuntu-Paket 0.9 bleibt unverändert als Rückfalloption |
| OHC OpenRGB-SDK-Helfer | Protokoll 4–6 · Ubuntu 6, Fedora 5 · vollständige Gerätepakete für laufende Effekte; einmaliger Direct-Kompatibilitäts-Fallback bleibt · validiertes `RESIZEZONE` · Controller-/Zonensynchronisation · Modus-/Farbrücklesung · Loopback-only · begrenzte Geräte-/LED-/Paketwerte · Socket-Antwort ist keine optische Bestätigung |
| OHC Desktop Shell | 1.0 (lokal, ohne Hardwarezugriff) |
| OHC Desktop-Backupformat | Schema 2, SHA-256-Export |
| OpenLinkHub | Ubuntu: 0.9.2 installiert · Web-UI im selben Paket |
| ckb-next | Ubuntu: 0.6.2 installiert · Paket `0.6.2+dfsg-0.3` · Corsair-Steuerungsbesitz bleibt gegenüber OpenRGB getrennt |
| Python | Ubuntu: 3.14.4 |
| PySide6 | Ubuntu: 6.10.2 |
| Qt | Ubuntu: 6.10.2 |
| Qt 6 D-Bus / KDE KConfig | Ubuntu: `qdbus`, `qdbus6`, `qdbus-qt6` und `kwriteconfig6` nicht im PATH gefunden; diese Hilfsprogramme sind nicht installiert, kein erfolgreicher Setup-/Upgrade-Status behauptet |
| liquidctl | Ubuntu: 1.16.0 · SHA256-geprüftes offizielles Wheel in privater venv unter `/usr/local/lib/open-hardware-control-backends/liquidctl-1.16.0` · Versionsaufruf, Import und finaler Interpreterpfad als normaler Benutzer geprüft · Ubuntu-Paket 1.15.0 unverändert als Rückfalloption |
| Pillow | Ubuntu-System-Python: 12.1.1 installiert · kein Upgrade auf die frühere Fedora-Referenzversion behauptet |
| Distribution | Ubuntu 26.04.1 LTS |
| Kernel | Ubuntu: 7.0.0-38-generic |
| Kraken USB-ID | `1e71:300e` |
| NZXT 2023 RGB Controller USB-ID | `1e71:2012` |
| Thermalright Levita Vision Display USB-ID | `87ad:70db` |
| TRCC Linux | Ubuntu: 9.10.4 installiert · bestehender Thermalright-Unterbau, weiterhin ein TRCC-Daemon als einziger USB-Besitzer |
| LACT | Ubuntu: 0.10.1 installiert · Paket `0.10.1-0` · OHC-Schreibzugriffe nur ab 0.10.1; Versionsprüfung bestätigt keine Takt-/Übertaktungsfähigkeit jeder GPU |
| CoolerControl | Ubuntu: nicht installiert; kein Upgrade oder installierter Steuerungsdienst behauptet |
| vkmark / glmark2 / Gamescope / Snapper / MangoHud / Wallpaper Engine for KDE | Ubuntu: nicht installiert; jeweils weder passendes Paket noch Programm im PATH beim lokalen Audit bestätigt |

## Reifegrade der Hauptbereiche

| Bereich | Feature-Version | Reifegrad |
|---|---:|---|
| Übersicht | 0.9.0 | Beta |
| Grafikkarte | 0.8.0 | Beta |
| Gehäuse | 0.9.0 | Beta |
| Hardware-Checker | 0.6.0 | Alpha |
| Snapshot-Manager | 0.5.0 | Alpha |
| Automationszentrale | 0.4.0 | Alpha |
| Programme | 0.5.0 | Alpha |
| Kühlung | 0.9.0 | Beta |
| RGB-Studio | 0.9.0-rc1 | Release Candidate |
| LCD | 0.9.0-rc1 | Release Candidate |
| Display-Effekte | 0.8.0 | Beta |
| Profile | 0.9.0 | Beta |
| Corsair · OpenLinkHub | 0.4.0 | Alpha |
| Wallpaper Engine | 0.8.0 | Beta |
| Desktop-Designs | 0.5.0 | Alpha |
| Einstellungen / Über | 1.0.0 | Stabil |
| Log | 0.9.0 | Beta |

## Historische Fedora-Referenz, nicht aktueller Ubuntu-Installationsstand

Die frühere Nobara-/Fedora-44-Referenz verwendete Kernel `7.1.4-200.nobara.fc44.x86_64`, Python 3.14.6, Qt/PySide6/Qt SVG 6.11.2, Pillow 12.3.0, OpenRGB `1.0~rc2` mit OHC-SDK 5, liquidctl 1.16.0, OpenLinkHub 0.9.0 sowie später ein angebotenes 0.9.1-Update, LACT `0.10.1-1` aus COPR und CoolerControl 5.0.1. Fedora-Hilfspaketnamen bleiben `qdbus-qt6` aus `qt6-qttools` und `kwriteconfig6` aus `kf6-kconfig`. Diese Angaben sind keine Ubuntu-Paketbefehle und kein behaupteter aktueller Ubuntu-Upgradezustand.

NZXT Kraken 2023 Firmware 2.0.0 gehört ebenfalls zu dieser historischen Hardware-Referenz. TRCC 9.9.11 bleibt die frühere physisch bestätigte Handshake-/Farbzyklus-Basis; der fortlaufende 1600×720-VideoLoop mit TRCC 9.10.4 und stabilem RSS-/Thread-/Dateideskriptorstand wurde am 01.10.26 auf der damaligen Referenz bestätigt. Diese Hardwarebeobachtungen ersetzen keinen aktuellen Ubuntu-Gerätetest.

Die Über-Seite zeigt zusätzlich die tatsächlich installierten Laufzeitversionen dynamisch an. Andere Versionen können funktionieren, gelten aber erst nach einem Hardwaretest als geprüft.

Die fünf Maus-SVGs sind eigene Projektgrafiken unter GPL-3.0-or-later; es werden keine externen Bilddateien oder Hersteller-Renderings mitgeliefert.

Die RGB-Effekt-, Geräte-/Gruppen- und NZXT-Validierungslogik ist eigener Projektquellcode unter GPL-3.0-or-later. OpenRGB und dessen Effects Plugin werden nicht mitgeliefert; die Über-Seite startet für Versionsangaben keinen synchronen OpenRGB-Prozess.
