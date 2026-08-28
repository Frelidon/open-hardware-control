| 3.4.25 INTERN | Neues PySide6-Dashboarddesign, kompakte Navigation ohne Community-Edition-Branding, neue Übersicht, modernisierte Kühlungszentrale, direkte System-Fan-Karten, separater Kurvendialog und vierstufiger Lüfter-Zuordnungsassistent. |
# Funktionsübersicht nach Version

| Version | Erstmals hinzugekommene Hauptfunktionen |
|---|---|
| 3.4.27 INTERN | Getrennte CoolerControl-Daemon-/Autostartanzeige, bestätigte Polkit-Dienstaktionen, einheitliche blau getönte Detailflächen auf allen Hauptseiten sowie vollständig blaue Kraken-Schnellprofile erst nach erfolgreicher Hardwareübertragung. |
| 3.4.23.2 INTERN | Kompaktes Cooling-Dashboard, CoolerControl-Ownership-Sperre, einzelne System-Fan-Karten mit Kurvenvorschau sowie grafischer PWM/RGB-Gehäuse-Assistent mit sicherem 30/80-%-Kontrasttest und persistenter Einbauplatz-Zuordnung. |
| 3.4.23.1 INTERN | Polkit-geschützter NCT6687-Fan-Helper für root-geschützte hwmon-PWM-Schreibzugriffe, 10-s-Kalibrierung mit RPM-Verlauf, MSI-EC-verträgliche Zielbestätigung und treibereigene Firmwarekurven-Rückgabe über pwmN_enable=2. |
| 3.4.23 INTERN | Sichere Mainboard-Lüftersteuerung über Linux-hwmon/NCT6687 mit bestätigungspflichtiger 70-%-Kalibrierung, individuellen Sensorquellen/Kurven je PWM-Kanal, Leise/Ausbalanciert/Leistung-Vorlagen mit sicherer Empfehlung, Sensor-Fallback, optionalem nct6687d-10-s-Watchdog, Firmware-Rückgabe, Secure-Boot-/Treiberdiagnose sowie ENE-DRAM-Reinitialisierung im RGB-Studio. |
| 3.4.22 INTERN | RGB-/ENE-Stabilitäts-Hotfix mit wirklich langlebigem SDK-Worker, Direct+Native-Bestätigungsbarriere, gezieltem RAM-Reclaim im Einzeltest, repariertem LCD-GIF-Skalierungsaufruf und direkt aktivierten AM5-CPU-Kurven. |
| 3.4.21 INTERN | Zentraler Kraken-USB-/RGB-Request-Koordinator, stabiler RGB-Profilstart nach vollständiger Geräteerkennung, Shutdown-LCD-Fallback, reparierte Schnellprofile-Einbettung, ESC-Live-Renderer, dynamische LCD-Zielauflösung sowie skalierbare und animierte LCD-Vorschauen. |
| 3.4.20 INTERN | Einmaliges ENE-DRAM-Priming, popupfreier Tray-Autostart, Sprache zuerst im Setup, integrierte Hilfe, konsolidierter LCD-Arbeitsbereich, acht eingebaute OHC-GIFs, Uhr als Animationsebene und Import des aktuellen verschachtelten NZXT-ESC-v3-Formats. |
| 3.4.19 INTERN | LCD-Kachel-Dashboard, flüssigere externe GIF/Hardware-Rendererstarts, PAUSE/RESUME für LCD-Displayeinstellungen, stabileres ENE-DRAM-Direct und vollständige Discover/AppStream-Metadaten. |
| 3.4.18 INTERN | Unabhängiger NZXT-ESC-Schema-v3-Importer mit Pflicht-Vorschau/Kompatibilitätsbericht, lokale LCD-Profilbibliothek, einfacher Drag-and-drop-Editor, Sensor-Remapping, Originalzustand sowie vollständiges Backup/Restore ohne gebündelten Fremdcode oder Designs. |
| 3.4.16 INTERN | Serialisierte Latest-value-wins-Übernahme für RGB-Geschwindigkeit und andere Effektparameter, exakte SDK-Framebestätigung sowie ressourcenschonende automatische Geräteprüfung mit Schutz vor vorübergehenden 7→2-Inventarabfällen. |
| 3.4.15 INTERN | Modusabhängige Hex-/Standardfarben, benutzersortierbare RGB-/LCD-/Kühlungsbereiche sowie erweiterte und kartenweise ein-/ausblendbare CPU-/GPU-Übersicht. |
| 3.4.14 INTERN | NZXT-Alternating-Fallback ohne `KeyError`, sichere Unterscheidung eigener OpenRGB-Clients, begrenzte interne RGB-Fehlerliste ohne modale Teilfehlerdialoge sowie sichtbare Vorlage „Frelidon PC“. |
| 3.4.13 INTERN | Direkt anwendbare RGB-Kacheln einschließlich „Feste Farbe“, dauerhafte Ausgewählt-/Aktiv-Anzeige sowie sichere manuelle oder optionale automatische RGB-Wiederübernahme nach separatem OpenRGB. |
| 3.4.12 INTERN | Sortierbare Kraken-Kanäle, animierte RGB-Galerie, sicherer Profilstart, stabiler RGB-Scrollpunkt und LCD-Ebenenmodus mit drei neuen Originaldesigns. |
| 3.4.11 INTERN | Dauerhafter Loopback-SDK-Worker, gemeinsame 25-Hz-Mehrgeräteframes mit Latest-frame-wins, gemessene Übertragungsrate, RGB-Einrichtungsassistent, Einzelzonen-Sichttest und automatische Sapphire-External-Control-Vorbereitung. |
| 3.4.10 INTERN | Vollständige OpenRGB-Geräteframes mit einmaligem Zonen-Fallback, 24-LED-Profile für Interstellar V2 Normal/Reverse, Plausibilitätswarnungen, ehrlicher Status zwischen Serverbestätigung und physischer Ausgabe, ckb-next-Konflikterkennung sowie robusterer Auswahl-/Scrollschutz. |
| 3.4.9 INTERN | Sichere OpenRGB-ARGB-Zoneneinrichtung mit `Lüfter/Geräte × LEDs`, Thermaltake-Portvorschlägen, validiertem SDK-`RESIZEZONE`, profilgespeicherten Größen, konfigurationsbedingten Fehlern ohne Quarantäne und priorisierten NZXT-Aufträgen. |
| 3.4.8 INTERN | Bestätigte OpenRGB-Direct-Ausgabe über aktuelle Controllerdaten und vollständige Zonenwrites, Modus-/Farbrücklesung, Sperre separat laufender OpenRGB-Prozesse sowie NZXT-`sync` bei gemeinsamer Dreikanalauswahl. |
| 3.4.7 INTERN | OpenRGB-SDK-Protokoll 4/5 mit kompatibler Aushandlung für ENE-RAM, bereinigte NZXT-2023-Effektzuordnung ohne `marquee-4` sowie harte Einzelinstanz-Sperre vor sämtlichen Hardwarezugriffen. |
| 3.4.6 INTERN | Klarere Liste ausgewählter RGB-Geräte mit Steuerweg und Ergebnisstatus, automatische Sitzungsprotokolle, fehlertolerante Mehrgeräteaktionen, einmalige Direct-Mode-Vorbereitung pro Gerät, getrennte GPU-/Hardwaremodus-Auswahl, Scrollpositionsschutz sowie Ausblendung des doppelt dargestellten NZXT-Controllers. |
| 3.4.5 INTERN | Begrenzter Loopback-SDK-Schreibpfad für Direct-Geräte ohne OpenRGB-CLI-`ApplyOptions`, Scrollpositionsschutz, geordnetes 12-Lüfter-Thermaltake-Profil und Hinzufügen/Bearbeiten/Entfernen/Auto-Anordnen eigener PC-Blöcke. |
| 3.4.4 INTERN | Atomare Reset-/Engine-Neustartfolge, vorgemerkte Schreibfreigabe bis zur frischen Erkennung, Zusammenführung vollständig gespiegelter OpenRGB-Inventare, Zonenprotokollierung und verschiebbare Thermaltake-PC-Ansicht mit aktuellem 120-mm-Lüfterlayout. |
| 3.4.3 INTERN | Sitzungsspezifische Isolation einzelner OpenRGB-`ApplyOptions`-Absturzgeräte, fortgesetzte Test-/Befehlsfolgen, echte Fehlerzählung pro Direct-Gerät und eindeutige OpenRGB-Indexdiagnose. |
| 3.4.2 INTERN | Start-Hotfix für die zu früh gelesene RGB-Vorschauuhr, defensiver Initialisierungsfallback sowie automatische private Start-/Absturzprotokolle im XDG-Zustandsverzeichnis. |
| 3.4.1 INTERN | Serielle OpenRGB-Einzelgerätebefehle gegen den rc2-Mehrgeräteabsturz, persistente Auswahl/Gruppen, native Fallbacks für Geräte ohne Direct Mode, eindeutige Gerätenamen, Einzelgeräte-Testmodus sowie PC-Skizze mit Frelidons A1-/A2-/B6-/B7-/SYS-FAN6-/Kraken-Profil. |
| 3.4.0 INTERN | Automatisch verwaltete fensterlose RGB-Engine, Fremdinstanz- und Mehrfachprozess-Sperre, Gerätekacheln, Drag-&-Drop-Gruppen mit unabhängigen Effekten, ENE-DRAM-Deduplizierung, topology-sichere NZXT-Effekte und bestätigter Komplett-Reset. |
| 3.3.0 INTERN | Eigenes RGB-Studio über lokalen OpenRGB-SDK-Client, statische Einzelgerätefarben, native Modi, zehn OHC-Effekte, sieben Vorlagen, Profilintegration, sitzungsweise Schreib-/Besitzsperren und standardmäßig verborgene experimentelle Desktop-Designs. |
| 3.2.0 INTERN | Windows-8/8.1-Kachelübersicht und Charms-Leiste, freie auswählbare OHC-Symbole/Mauszeiger, selektierbare Backups mit Aufbewahrung und sicherem Export/Import sowie Breeze-Light-Notfallrücksetzung. |
| 3.1.1 INTERN | Distributionsübergreifende Qt-6-D-Bus-Erkennung, Fedora-`qdbus-qt6`-Korrektur sowie bestätigte automatische Installation optionaler KDE-Desktop-Werkzeuge über DNF, APT, Pacman und Zypper. |
| 3.1.0 INTERN | Reversible KDE-Plasma-Desktop-Designs im Windows-11- und macOS-Stil mit Vorschau, Bestätigung, Backup, automatischem Rollback und interner Paketkennzeichnung. |
| 3.0.9 | Öffentliche Multi-Hardware-Version: direkte OpenLinkHub-Maustastenbelegung, begrenzte fensterlokale Tastaturmakros, saubere LCD-Temperaturbilder, Celsius/Fahrenheit sowie RPM-/DEB-/ZIP-Pakete. |
| 3.0.7 INTERN | Originale Kraken-Wassertemperaturanzeige beim echten Beenden sowie eigene interaktive OpenLinkHub-Maus-SVGs mit Modellfamilien, Hotspots und auslesbaren Tastenfunktionen. |
| 3.0.6 INTERN | Vollständige LCD-/GIF-Moduswiederherstellung aus Startprofilen, fünf Sekunden verzögerter LCD-Autostart, zuverlässiger Tray-Zustand und geordnete Sitzungssignale. |
| 3.0.5 INTERN | Softwaregeregelte Pumpen- und Lüfterkurven nach CPU-Temperatur mit Glättung, Hysterese, GIF-USB-Koordination, Profilmigration, Sensorfehler- und Beenden-Fallback. |
| 3.0.4 INTERN | Sitzungsweise freigegebene, validierte OpenLinkHub-Steuerung für Kühlung, RGB/LCD, Maus, Tastatur und Headset über die lokale API. |
| 3.0.3 INTERN | Stabile, theme-unabhängige Aktivfarbe für Manuell/Kurve auf Basis des zuletzt bestätigten Gerätebefehls; kein vorzeitiger Qt-Checkzustand. |
| 3.0.2 INTERN | Eindeutige kanalgetrennte Umschaltung zwischen manueller fester Drehzahl und Pumpen-/Lüfter-Hardwarekurve mit synchroner Aktivmarkierung. |
| 3.0.1 INTERN | Koordinierte PAUSE-/RESUME-USB-Übergabe: Pumpen-, Lüfter-, Kurven- und Profiländerungen während GIF-/Hardwareanimation; derselbe vorbereitete Stream läuft danach automatisch weiter. |
| 3.0.0 INTERN | Gemeinsame Open-Hardware-Control-Oberfläche, hierarchische Navigation, hardwareabhängige Module, vollständiges NZXT-Modul und sichere read-only OpenLinkHub-Geräteintegration mit Benutzerdienst-Aktionen. |
| 2.9.23 INTERN | Live aktualisierte CPU-/GPU-Werte in animierten Hardwaredesigns über isolierten Renderprozess; Wasser bleibt letzter sicherer Kraken-Wert. |
| 2.9.22 INTERN | Fünf nahtlose 20/25-FPS-Hardwareanimationen mit Ringen/Orbits sowie gemeinsamer 70–150-%-Regler für Schrift- und Zahlengröße. |
| 2.9.21 INTERN | Fünf runde Live-Hardwaredesigns für Wasser/CPU/GPU, dGPU-Sensorauswahl, Eisblau plus Farbvorlagen und `#RRGGBB`, vollständige Sprachumschaltung nach Einstellungswiederherstellung. |
| 1.0 | Erste Grundsteuerung der NZXT Kraken über liquidctl. |
| 2.0 | PySide6-Oberfläche, Live-Status, feste Pumpen-/Lüfterwerte, Schnellprofile, Kurven, Sicherheitsumschaltung, RGB, LCD-Bilder, Einstellungen, Autostart, Tray, Installer und Deinstaller. |
| 2.1 | Serielle asynchrone QProcess-Warteschlange; Entfernung des absturzanfälligen QThreadPool/QRunnable-Aufbaus. |
| 2.2 | Eindeutige LCD-Einzelübertragung und optionaler Wiederholungs-Fallback. |
| 2.3 | LCD-Uhr, runde Vorschau, Frelidon-Branding, Über-Bereich, GPL-Lizenz, Diagnosewerkzeug und englische Grunddokumentation. |
| 2.3.1 | Sicherheitsbestätigungen, sichere Kurvenprüfung, 65/65-Standardprofil, stärkere Anonymisierung und SECURITY.md. |
| 2.4 | Transparente Links zu Websites, Quellcode und Lizenzen; offizieller NZXT-Gerätelink. |
| 2.5 | Klare Beschränkung auf Kraken, zugehörige Radiatorlüfter, LCD und separaten NZXT-RGB-Controller. |
| 2.6 | Grafischer Kurveneditor, Live-Temperaturmarker, Hell/Dunkel/System und Hex-Akzentfarben. |
| 2.7 | Tastaturbedienung, AMD-AM5-Profile, CPU-Temperatur und -Assistenz, udev-Reparatur und dynamische Komponentenstände. |
| 2.7.1 | Direct-Access-Hotfix für Pumpen- und Lüfterkurven. |
| 2.8 | Expertenmodus, Anzeige des aktiven Kühlmodus und automatisches erneutes Senden der LCD-Uhr. |
| 2.8.1 | Abhängigkeitsprüfung vor PySide6-Start und kontrollierte DNF-Installation. |
| 2.9 | Ersteinrichtungsassistent, zwölf prozedurale Animationen, adaptive DPI-/Monitorlayouts, kategorisierte Profile, Import/Export, Startprofile und vollständiger Quellcode-Snapshot. |
| 2.9.1 | CPU-Offscreen-Renderer und getrennte Hintergrund-/Inhaltsebenen; vollständigeres Klick-, Änderungs-, Menü-, Tastatur- und Navigationsprotokoll mit Log-Export. |
| 2.9.2 | Scrollbare Einstellungen, größeres Hauptfenster und einmalige Layoutmigration für bestehende Installationen. |
| 2.9.3 | Light-Theme-/Hintergrund-Hotfix für stabile Ebenenreihenfolge und RGB32-Rendering. |
| 2.9.4 | Animationen lassen sich nach dem Ausschalten wieder aktivieren; letztes Thema bleibt erhalten. |
| 2.9.5 | Direct Access für alle Kühlungswrites, stiller Hintergrundbetrieb bei Berechtigungsfehlern und 10.000-Zeichen-Loglimit. |
| 2.9.6 | LCD-Uhr-Regression beim Start behoben und durch Regressionstest abgesichert. |
| 2.9.20 INTERN | Vereinfachte normale FPS-Auswahl, erweiterte Diagnoseoptionen, wahrscheinliche GIF-Loop-Warnung und nahtlos neu erzeugte Moving-Bars-Testdateien. |
| 2.9.19 INTERN | Streng fortlaufende LCD-Phasen, phasenstabiler 26,667-Hz-CAM-Zieltakt und sanfter Abbau einzelner Überläufe in höchstens 0,25-ms-Schritten. |
| 2.9.17 INTERN | ACK-synchronisierte CAM-Taktung direkt nach `37 02`, 0,10-ms-CAM-Abstand und Diagnosekennung `cam-raw-ack-paced` gegen horizontales Tearing und Mikroruckler. |
| 2.9.16 INTERN | Exklusiver Kraken-Zugriff während GIF-Streaming, eindeutige `37 01`/`37 02`-ACK-Zuordnung trotz ungefragter Statusberichte, 12-Sekunden-Watchdog und automatischer Wiederanlauf von Statusabfragen/Kühlbefehlen. |

## Funktionen nach Kategorien

### Kühlung

- Live-Wassertemperatur, Pumpen- und Lüfterwerte – 2.0
- feste Werte und Schnellprofile – 2.0
- Temperaturkurven – 2.0
- grafischer Kurveneditor – 2.6
- AMD-AM5-CPU-Assistenz – 2.7
- Direct Access für Kurven – 2.7.1
- Expertenmodus und aktive Modusanzeige – 2.8
- kategorisierte Kühl- und Gesamtprofile – 2.9
- Mainboard-PWM-Erkennung über Linux-hwmon/NCT6687 ohne feste Kanalzuordnung – 3.4.23
- sichere 70-%-/10-s-Kalibrierung mit RPM-Beobachtung und automatischer Wiederherstellung – 3.4.23.1
- individuelle Mainboard-Lüfterkurven mit CPU/GPU/Kühlmittel/Maximum/gewichteter Sensorquelle – 3.4.23
- Sensorfehler-Fallback, 90-°C-Notanforderung und Firmware-Rückgabe – 3.4.23

### LCD

- statische Bilder, Helligkeit und Ausrichtung – 2.0
- eindeutiger Wiederholungs-Fallback – 2.2
- Uhr, Datum und runde Vorschau – 2.3
- automatisches erneutes Senden der Uhr – 2.8
- LCD- und Gesamtprofile – 2.9

### Design und Anzeige

- Hell, Dunkel, System und Hex-Akzent – 2.6
- Ersteinrichtungsassistent – 2.9
- zwölf animierte prozedurale Hintergründe – 2.9
- DPI-/Monitorerkennung, 16:10, 16:9, 21:9 und 32:9 – 2.9
- UI-Skalierung 80–180 Prozent – 2.9
- Design- und Gesamtprofile – 2.9
- sicherer CPU-Offscreen-Hintergrundrenderer – 2.9.1
- scrollbare Einstellungen und vergrößertes Hauptfenster – 2.9.2
- experimentelle Desktop-Designs standardmäßig aus und verborgen – 3.3.0

### RGB-Studio

- statische Farbe pro OpenRGB-Gerät und gemeldete native Hardwaremodi – 3.3.0
- zehn eigene OHC-Softwareeffekte und sieben Designvorlagen – 3.3.0
- Loopback-only SDK-Client, Sitzungsfreigabe und Gerätebesitzsperren – 3.3.0
- Speicherung in exportierbaren Gesamt-/RGB-Profilen – 3.3.0
- verwaltete RGB-Engine ohne manuellen Serverstart – 3.4.0
- Gerätekacheln, Mehrfachauswahl und Drag-&-Drop-Gruppen – 3.4.0
- unabhängige Gruppeneffekte und gemeinsame NZXT-/OpenRGB-Auswahl – 3.4.0
- ENE-DRAM-Aliasfilter und vollständige LED-Listenübernahme – 3.4.0
- topology-sichere NZXT-Effekte und kompletter Geräte-Reset – 3.4.0
- serielle Einzelgeräteausgabe, native Fallbacks und persistente Gruppenzuordnung – 3.4.1
- PC-Skizze, freie Gerätenamen und Frelidons vorbereitetes Hub-/Lüfterprofil – 3.4.1

### Installation und Dokumentation

- Installer, Desktopdatei und Deinstaller – 2.0
- Diagnosewerkzeug – 2.3
- Sicherheitsdokumentation – 2.3.1
- Software-, Quellcode- und Lizenzlinks – 2.4
- Komponentenstände – 2.7
- Abhängigkeitsinstallation – 2.8.1
- zusätzlicher Quellcode-Snapshot und Manifest – 2.9
- detailliertes Benutzeraktionsprotokoll und Log-Export – 2.9.1


### 2.9.4
- Reaktivierbare Hintergrundanimationen mit gespeichertem letzten Thema.
