# Open Hardware Control – zentrale Projektdokumentation

Stand: **3.4.29.44 STABLE**, 05. September 2026

## Zielbild

Open Hardware Control by Frelidon ist die gemeinsame, modular erweiterbare Linux-Oberfläche für unterstützte Hardware. Die komplette bisherige NZXT-Kraken-Anwendung bleibt als fest eingebautes NZXT-Modul erhalten. Corsair-Hardware wird über OpenLinkHub eingebunden. Zusätzliche RGB-Geräte erscheinen über eine von OHC automatisch verwaltete lokale Hardware-Engine. Spätere Gerätefamilien können als weitere Module hinzukommen, ohne die Navigation mit einer langen Reihe von Hauptreitern zu überladen.

Open Radeon Control Center bleibt ein eigenständiges Projekt. Es wird weder technisch noch organisatorisch in Open Hardware Control verschmolzen.

## Version 3.4.29.44 STABLE

Version 3.4.29.44 hält ein gespeichertes RGB-Startprofil während einer vorläufigen OpenRGB-Teilerkennung vorgemerkt, wartet begrenzt auf den vollständigen Gerätebestand und startet danach das Design. Die Modulregisterprüfung folgt nun dem tatsächlichen Build-Kanal, sodass der zuvor intern geprüfte 3.4.29-Stand stabil veröffentlicht werden kann. Der plattformunabhängige Vorschau-Warteschlangentest berücksichtigt auch das mitgelieferte OHC-Video auf frischen GitHub-Runnern ohne Cache.

Version 3.4.29.42 repariert die Wallpaper-Wiedergabesteuerung über das in Plasma registrierte CaptSilver-D-Bus-Objekt und ergänzt Seitenverhältnis, Zuschneiden und Vollbildstreckung pro Zielbildschirm. Das Programmfenster verwendet standardmäßig den Hauptbildschirm, kann einen benannten Monitor dauerhaft wählen und fällt bei dessen Fehlen zurück. Einheitlich schmale Scrollleisten gelten in der gesamten Anwendung. Assistent, geprüfter Fedora-Installer, feste Galeriekarten, schreibgeschützte Workshop-Bibliothek und Originalzustand als Standard bleiben erhalten.

Version 3.4.29.38 modernisiert das RGB-Studio, lagert die hardwarefreie Designgalerie in Modul 1.1 aus und verhindert einen dauerhaft blockierten ENE-Reinitialisierungszustand nach abgewiesenen Befehlen. TRCC Linux 9.9.12 ist die empfohlene kompatible Backend-Version; der reale Levita-Hardwaretest bleibt auf 9.9.11 dokumentiert.

Hotfix 3.4.29.1 ergänzt die beim ersten Modulschnitt fehlenden expliziten Importe für LCD- und Über-Seitentexte. Ein echter Offscreen-Test baut nun alle elf Hauptseiten vollständig auf, ohne Hardwareerkennung zu starten.

Hotfix 3.4.29.2 verhindert beim Desktop-Shell-Stopp den beobachteten Qt/KDE-Abbruch samt leerem Fenster, unterdrückt alte Kraken-LCD-Startbefehle bei aktiver Levita und ersetzt nach einer aktivierten Temperaturkurve den veralteten manuellen Reglerwert. Die persönliche PC-Ansicht zeigt die Thermalright Levita Vision 360 und führt die Jungle-Leopard-GPU-Halterung getrennt vom ENE-RAM als Airgoo-Kanal B6 mit 24 LEDs.

Hotfix 3.4.29.3 hält nach einer ausdrücklichen Administratorfreigabe eine eng begrenzte, an den OHC-Prozess gebundene Lüfter-Helfersitzung offen. Dadurch läuft die Levita-CPU-Kurve auch nach Ablauf des kurzfristigen Polkit-Caches weiter, ohne alle paar Minuten einen neuen Hintergrunddialog zu erzeugen. Auf reinen Thermalright-Systemen entfallen unnötige liquidctl-/Kraken-Starts, die alte Kraken-Uhr wird ausgeblendet, und ein stabil von sieben auf sechs Geräte geschrumpfter OpenRGB-Bestand wird als Hardwareänderung gespeichert.

Hotfix 3.4.29.4 verhindert den Startabbruch, wenn das Display-Studio bereits beim Seitenaufbau den gespeicherten TRCC-Designordner und dessen erste Vorschau wiederherstellt, bevor die eigentliche Log-Seite existiert. Der reale TRCC-Linux-9.9.11-Test bestätigt außerdem für USB `87ad:70db` den sichtbaren Farbzyklus sowie den vollständigen Handshake mit Modell-ID 64, Sub-Byte 3 und 1600×720.

Hotfix 3.4.29.5 setzt den von TRCC dauerhaft gespeicherten dekorativen Split-Modus vor jedem Medienladen zuerst sicher auf null. Damit erreicht der bestätigte Absturz von TRCC Linux 9.9.11 mit PySide6 6.11 beim Aufruf von `QImage.mirrored()` den Video-Start nicht mehr. Die Stile A–C bleiben als gekennzeichnete lokale Vorschau erhalten; die echte rechte 80-Pixel-Aussparung bleibt unabhängig davon für Hardwarewerte gesperrt.

Version 3.4.29.6 ersetzt die schmale Vorschau-Markierung durch eine tatsächlich an TRCC übertragene transparente Maske mit schwarzem rechten Balken. Die Referenzeinstellung ist 320 Pixel breit und verschiebt das Bild 160 Pixel nach links; Balkenbreite sowie Hintergrund-X/Y bleiben frei einstellbar. Bilder und gewöhnliche Videos werden dafür nur als lokale Arbeitskopien vorbereitet, nie im Importordner verändert. Zwei feste Abstandsvorlagen ergänzen die weiterhin einzeln verstellbaren Hardwarewerte, und doppelte `C`-/Prozent-Einheiten werden nicht mehr an bereits vollständig formatierte Texte angehängt.

Hotfix 3.4.29.8 ergänzt sichere PWM/DC-Umschaltung, globale/einzelne Lüftervorlagen und Kurven-Reset. Die Polkit-Dauerfreigabe wird über einen unprivilegiert lesbaren Statusmarker zuverlässig erkannt. Levita-Medien werden unverzerrt auf 1600×720 skaliert; Balken-Drag, Element-Undo, lokale Kategorien, sichtbare Prozentzeichen und geräteabhängige LCD-Kacheln verbessern den Editor. UI-Tests dürfen keine Hardwareprozesse starten, und ein abgestürzter OpenRGB-Server wird bis zum bewussten manuellen Neuversuch gesperrt.

Hotfix 3.4.29.9 übernimmt den aktuellen TRCC-Linux-Katalog exakt: Gallery `a001–a082`, Tech `b001–b025`, HUD `c001–c072`, Light `d001–d055`, Nature `e001–e054` und Aesthetic `y001–y010`. Lokale Medien und Layoutordner werden nur bei einer gültigen originalen ID automatisch einsortiert und numerisch geordnet; alle anderen Dateien bleiben unter „Eigene Dateien“. Dafür werden weder Herstellerdateien heruntergeladen noch mit OHC ausgeliefert.

Hotfix 3.4.29.10 ergänzt echte getrennte Levita-Ebenen: Ein lokales Video läuft unten, während ein vollständiges importiertes TRCC-Hardwaredesign seine Live-Sensorwerte darüber zeichnet. Die eigene Designmaske wird mit dem rechts oben und unten auf 18 Renderpixel gerundeten Levita-Balken kombiniert, statt sie zu ersetzen. Eine neue Kachel zeigt lokale Bild-/Layout- und kurze Videovorschauen direkt in OHC. Die bislang noch synchrone OpenRGB-Versions- und Inventarabfrage wird ebenfalls ausdrücklich offscreen gestartet und kann beim Programmaufbau kein leeres Hilfsfenster mehr öffnen.

Hotfix 3.4.29.12 baut das Levita-Studio auf moderne Karten für Hintergrund und Datenoberfläche um, animiert lokale Videos in der Hauptvorschau und ergänzt drei eigene OHC-Hintergründe. Ein ausdrücklich aktivierbares Startdesign speichert beide Ebenen, wartet die Desktop-Ruhezeit ab und wiederholt einen fehlgeschlagenen Displaystart genau einmal. Unpassende TRCC-Layoutgeometrien werden auch bei breiten Importen ausgeschlossen; Qt-Desktop-ID und `StartupWMClass` sichern die richtige Plasma-Symbolzuordnung.

Hotfix 3.4.29.13 trennt den gemerkten eigenen Designordner von seiner aktiven Einbindung, sortiert vollständige Live-Themes standardmäßig in Ebene 2 und erlaubt bewusste Ebenenwechsel. Videokarten besitzen Standbild- und Hover-Vorschau. Eigene Levita-Helligkeit und -Ausrichtung verwenden reale TRCC-Befehle. USB-Wechsel werden serialisiert und ein bestätigter Timeout einmal begrenzt wiederholt. Die globalen Gehäuselüfterprofile stehen nun oben in der Zusammenfassung, ohne Kalibrierung oder Aktivierung zu verändern.

Hotfix 3.4.29.14 beseitigt die synchrone Videovorschau-Erzeugung im Qt-Hauptthread. Eine sichtbare Warteschlange mit höchstens zwei `ffmpeg`-Workern hält die Oberfläche bei großen Katalogen bedienbar; erfolgreiche Startbilder bleiben quellversionsgebunden für spätere Programmstarts im OHC-Cache erhalten.

Hotfix 3.4.29.15 erhält Bild- und Videohintergründe beim Wechsel der Datenoberfläche und aktualisiert die kombinierte Vorschau bei jedem Klick auf Ebene 2. Fehlt einem TRCC-Layout die trennbare Hintergrunddatei, zeigt OHC ersatzweise seine vollständige `Theme.png`. Die Vorschau ist mittig auf 960×432 begrenzt und entspricht damit ohne seitliche Leerbalken exakt dem Levita-Format 1600×720.

Hotfix 3.4.29.16 fasst gleiche vollständige Dateinamen im Levita-Katalog zu genau einer Karte zusammen. Bei mehreren Sicherungspfaden wird der normale beziehungsweise kürzeste Pfad bevorzugt; gespeicherte Auswahlen werden automatisch auf diese Datei umgestellt. Benutzerdateien bleiben vollständig unangetastet. Das neue Log identifiziert das schwarze Startfenster außerdem als OHC-eigenes, elternloses und namenloses 640×480-`QFrame`. Nur dieses vollständige Muster wird vor der Anzeige gesperrt; vertiefte Objekt-, Layout-, Kinder-, Elternketten- und Zeitdiagnosen bleiben erhalten.

Hotfix 3.4.29.19 repariert die reale Übertragung dieser bearbeiteten Ebene. OHC akzeptiert sein geprüftes natives Cache-`trcc.json` jetzt wie TRCC Linux als vollständiges Theme und verlangt dafür kein künstliches `config1.dc`. Auswahlwechsel vermeiden außerdem unnötige Karten- und Vorschau-Neuaufbauten.

Hotfix 3.4.29.24 integriert die geprüften 22/23-Korrekturen in den vollständigen Repository-Stand: beschädigte Layout-Einträge werden einzeln übersprungen, Symlink-Themes abgewiesen, der Split-Standard ist sicher Aus, Rendererstart wird bestätigt und Vorschauprozesse werden beim Beenden geschlossen. Das aktuelle Levita-Fachmodul ist 1.2. Hotfix 3.4.29.21 übernahm zuvor eine gewählte Ebene-1-Karte sofort in die große Vorschau und rundete nur die äußeren rechten Displayecken; die Innenkante des Notchbalkens blieb gerade.

Hotfix 3.4.29.20 bringt Editor und reales Levita-Display geometrisch zusammen: Alle TRCC-Textkoordinaten sind Blockmittelpunkte, animierte Hintergrundframes ersetzen keine Drag-Objekte mehr und eine erneut gewählte Hintergrundkarte wird unmittelbar neu geladen. Die Kraken-Kühlmittelkarte erscheint nur bei verbundenem Kraken und tatsächlich geliefertem Temperaturwert.

Hotfix 3.4.29.18 macht die Levita-Datenoberfläche 2 vollständig editierbar. Logische Datenblöcke bleiben intern zusammen, können aber jeweils einzeln gezogen und über ein Kontextmenü angepasst werden; die gesamte Ebene besitzt zusätzliche X/Y-Offsets. Die Fachlogik ist in einem versionierten Modulordner getrennt, und das verpflichtende Modulregister hält Pfade, Versionen und kleine Kontextbudgets für künftige Coding-KIs fest.

Hotfix 3.4.29.17 ersetzt das generische Symbol des Plasma-Systemabschnitts durch das kompakte OHC-Emblem. Eine eigene 22×22-Datei ergänzt die installierten Icongrößen; das Tray erhält ausschließlich die projektbezogene 22/32/48/64-Rasterstaffelung.

Hotfix 3.4.29.11 protokolliert zur Ursachenfindung des weiterhin sichtbaren leeren Startfensters jedes eigene Qt-Top-Level-, Dialog-, Popup- und Werkzeugfenster samt nativer Oberflächenerzeugung. Gestartete Helferprozesse tragen Programm, sichere Befehlsmerkmale und `QT_QPA_PLATFORM` in das sichtbare sowie das frühe dauerhafte Startprotokoll ein. Die Levita-Rundung zeigt ausschließlich nach innen zum Display, während die rechte Außenkante bündig bleibt.

Hotfix 3.4.29.7 unterdrückt die native OHC-Fensteroberfläche bereits vor dem Aufbau eines minimierten KDE-/Wayland-Tray-Autostarts und verhindert damit das fotografierte schwarze Zwischenfenster. Zusätzlich laufen auch alle kurzlebigen OpenRGB-Qt-Clients offscreen. Für den fest installierten, eng begrenzten NCT6687-Helfer stehen „Dauerhafte Berechtigung erteilen“ und „Dauerhafte Berechtigung entfernen“ bereit; die benutzerspezifische Polkit-Regel speichert kein Passwort und ändert nichts an Kalibrierung, Besitzschutz, Watchdog oder Firmware-Rückgabe.

Die LCD-Seite enthält ein lokales Thermalright-Levita-Studio mit echter 1600×720-Arbeitsfläche, geschützter rechter 80-Pixel-Aussparung und getrennten Hintergrund-/Hardwaredaten-Ebenen. Ein lokales Video kann hinter einem vollständigen TRCC-Layout mit live aktualisierten Sensorwerten laufen; alternativ bleiben CPU, GPU, RAM und Uhr frei positionierbar. Der Testmodus schreibt standardmäßig nicht auf USB; reale Übertragung wird ausschließlich an das separat installierte GPL-Backend TRCC Linux delegiert.

Für die Thermalright Levita Vision 360 ARGB Black sind Display und Kühlung bewusst getrennt. Das USB-Gerät identifiziert das Display, während Pumpe und Radiatorlüfter über einzeln ausgewählte und physisch bestätigte Mainboard-PWM-Header laufen. Leise, Ausbalanciert, Leistung, Sicherheit und CPU-Temperaturkurven werden erst nach dem 70-%-/10-s-Test freigegeben. CoolerControl blockiert parallele Zugriffe, verwendete Header gehen beim Beenden an BIOS/Firmware zurück, und ein nicht vorhandener Kühlmittelsensor wird nicht simuliert.

Der reale ENE-DRAM-Log zeigte außerdem, dass ein erster erfolgreich beendeter OpenRGB-Direct-Befehl die physischen LEDs noch nicht zwingend weckt. Der automatische Profilstart führt deshalb jetzt zwei geordnete Reclaim-Durchläufe für alle erkannten ENE-Riegel aus, wartet kurz und startet erst danach den dauerhaften RGB-Frame-Worker.

Die Kühlungszentrale unterscheidet nun zwischen dem geschlossenen CoolerControl-Fenster, einem weiterhin laufenden `coolercontrold`-Hintergrunddienst und dessen Autostartzustand. Nach ausdrücklicher Bestätigung kann OHC CoolerControl nur für die aktuelle Sitzung beenden, den Systemdienst dauerhaft deaktivieren oder ihn wieder dauerhaft aktivieren und sofort starten. Die Übergabe bleibt exklusiv: Beim Deaktivieren startet OHC keine Regelung automatisch; beim Aktivieren gibt OHC seine Mainboard-Kanäle zuerst an Firmware/BIOS zurück.

## Version 3.4.26 INTERN

Das Repository besitzt nun ein dauerhaftes, versioniertes KI-Projektgedächtnis für Cursor und andere Coding-Agenten. Projektregeln, Session-Hook und Release-Skripte sorgen dafür, dass neue Chats den aktuellen Stand wiederfinden und Veröffentlichungen nur aus einem geprüften, committed Stand mit ausdrücklicher Freigabe erfolgen.

## Version 3.4.16 INTERN

- Übernimmt schnelle RGB-Parameteränderungen seriell nach dem Latest-value-wins-Prinzip.
- Ordnet SDK-Bestätigungen dem tatsächlich übertragenen Frame zu.
- Prüft den Gerätebestand einmal pro Minute rein lesend und schützt die vollständige Liste vor kurzzeitigen 7→2-Startresultaten.

## Version 3.4.15 INTERN

RGB Studio zeigt jeden OHC-Modus einzeln mit Beschreibung und genau den dafür sinnvollen Farbfeldern. Farben sind als Hexcode, Standardfarbe oder über den Farbdialog wählbar. Die Standardreihenfolge beginnt mit der verwalteten Engine, gefolgt von Geräten/Effekten, PC-Aufbau und Gruppen. Die Hauptbereiche von RGB, LCD und Kühlung sind benutzersortierbar, ihre innere Struktur bleibt fest. Die Übersicht bleibt zuerst und ergänzt ein-/ausblendbare CPU-, GPU-, VRAM- und Topologiekarten.

## Version 3.4.13 INTERN

Animationen für OpenRGB-Direct-Geräte verwenden nun einen dauerhaften Mehrgeräte-SDK-Worker mit 25-Hz-Ziel und ohne Prozess-/TCP-Neustart pro Gerät. Der RGB-Einrichtungsassistent verbindet Konfliktprüfung, Umbenennen, Einzeltest, Zonen-Sichttest, Thermaltake-Aufbau und GPU-External-Control.

## Version 3.4.10 INTERN

Die realen Logs erklären den Ausfall von MSI MYSTIC LIGHT und Airgoo AG-DRGB16: OpenRGB meldet die Kanalnamen, hat für diese variablen ARGB-Zonen aber null Farbplätze angelegt. OHC liest deshalb aktuelle Größe sowie Mindest-/Höchstwert über SDK 5 und bietet einen eigenen Einrichtungsdialog für `Lüfter/Geräte × LEDs je Gerät`. Bekannte A1-/A2-Lüfterzahlen aus der Thermaltake-Ansicht werden vorgeschlagen, die modellabhängige LED-Zahl bleibt eine bewusste Benutzereingabe.

Beim Anwenden validiert OHC jede Zone, sendet den offiziell dokumentierten `RESIZEZONE`-Auftrag, liest die neue Größe zurück, aktiviert Direct Mode und überträgt erst dann die Farbe. Eine noch fehlende Zonengröße ist keine defekte Hardware und führt deshalb nicht mehr nach drei Frames zur Sitzungssperre. NZXT-Aufträge laufen bei gemischter Auswahl zuerst, damit die Kraken nicht hinter mehreren seriellen OpenRGB-Rücklesungen wartet.

## Version 3.4.8 INTERN

Direct-Geräte werden nicht länger schon nach erfolgreichem Socketversand als eingestellt gewertet. Der OHC-SDK-Helfer synchronisiert Geräteanzahl, Controller, Modus, Zonen und tatsächlichen Farbpuffer, schreibt vollständig abgebildete Controller zoneweise und liest den kompletten Zielzustand zurück. Damit erhalten ENE DRAM, MSI MYSTIC LIGHT und Airgoo den Treiberpfad, der ihre gemeldeten Zonen unmittelbar aktualisiert.

Eine `/proc`-Prüfung erkennt außerdem eine separat laufende OpenRGB-Oberfläche auch ohne offenen SDK-Port. OHC blockiert dann seine Engine und jeden RGB-Auftrag, nennt die fremde PID und beendet den Prozess nicht. Bei gemeinsamer Auswahl aller drei NZXT-Kanäle wird der auf der Referenzhardware bestätigte `sync`-Pfad genutzt; einzeln ausgewählte Kanäle bleiben getrennt.

## Version 3.4.7 INTERN

Der im realen RAM-Test gemeldete OpenRGB-SDK-Server verwendet Protokollversion 5. Der OHC-Schreiber unterstützt nun die Revisionen 4 und 5 und handelt die gemeinsame Revision nach demselben Mindestprinzip wie der offizielle OpenRGB-Client aus. Paket-, Geräte-, LED-, Farb- und Loopback-Grenzen bleiben unverändert.

Der NZXT-2023-Treiber in liquidctl 1.16.0 akzeptiert `marquee-4` auf Frelidons Controller nicht. OHC bietet diesen Alias nicht mehr an und verwendet für Glut-Komet den gültigen Hardwaremodus `pulse`; Kreisel und Abwechselnd erhalten ebenfalls bestätigte Alternativen. Zusätzlich besitzt die gesamte Anwendung nun eine eigene Kernel-Dateisperre. Sie liegt vor jedem Qt-/Backend-/Hardwareaufbau, sodass ein zweiter Start niemals eine zweite Kraken-, liquidctl- oder OpenRGB-Sitzung eröffnet.

## Version 3.4.6 INTERN

Die RGB-Geräteauswahl besitzt jetzt eine gut lesbare Ergebnisliste mit Steuerweg und Status. Direct-Geräte werden pro verwalteter Engine-Sitzung nur einmal in den benutzerdefinierten Modus versetzt; weitere Farbframes verwenden ausschließlich den SDK-LED-Pfad. Fehler eines einzelnen Geräts halten Mehrgeräteaktionen nicht mehr vollständig an. Die getrennt bezeichnete GPU-/Hardwaremodus-Auswahl beeinflusst OHC-Effekte nicht mehr unbeabsichtigt, der bereits über `liquidctl` dargestellte NZXT-Controller erscheint nicht zusätzlich als OpenRGB-Duplikat und die RGB-Seite stellt ihre Scrollposition nach Aktionen zuverlässig wieder her. Aktuelle und vorherige Sitzungsprotokolle werden automatisch unter `~/.local/state/open-hardware-control/` geführt und vom Diagnosepaket übernommen.

## Version 3.4.5 INTERN

Der Fedora-Coredump für Airgoo AG-DRGB16 bestätigt den OpenRGB-`ApplyOptions`-Abbruch auch bei einem gültigen Einzelgerätebefehl. OHC schreibt Direct-Geräte deshalb mit einem eigenen, begrenzten Loopback-SDK-Helfer, während OpenRGB separat installiert bleibt und weiterhin Erkennung sowie Hardwareprotokolle übernimmt. Statische Farben, Einzeltest und OHC-Animationen umgehen so den abstürzenden CLI-Pfad.

Die RGB-Seite bewahrt beim Kachel-/Gruppenneuaufbau ihre Scrollposition. Frelidons Thermaltake-Ansicht startet geordnet mit zwölf Lüftern: 3 oben, 2 vorne, 3 an Rückwand/Seite, 3 auf der Netzteilabdeckung vorne und 1 hinten. Eigene Blöcke können hinzugefügt, bearbeitet, entfernt und automatisch angeordnet werden; vorhandene eigene Gruppen und Blöcke bleiben bei der Schemaaktualisierung erhalten.

## Version 3.4.4 INTERN

Die vierzehn gemeldeten OpenRGB-Geräte wurden als vollständiges Spiegelinventar `0…6` plus `7…13` erkannt und auf sieben tatsächliche Backendmeldungen reduziert. Die Reset-/Neustart-Reihenfolge invalidiert alte Erkennungsantworten und schaltet Schreibaktionen erst nach erfolgreichem Engine-Neustart wieder frei. Die bisherige PC-Formularansicht wurde durch einen verschiebbaren Thermaltake-360-mm-Aufbau ersetzt.

## Version 3.4.3 INTERN

Vier Coredumps von OpenRGB `1.0~rc2` auf Fedora 44 bestätigen gerätespezifische `ApplyOptions`-Abstürze auch bei gültigen Einzelgerätebefehlen. Die Anwendung erkennt die charakteristische `stl_vector`-Assertion, isoliert nur die zugeordnete Gerätekachel für die aktuelle Sitzung und setzt Befehlsfolgen mit den übrigen Geräten fort. Direct-Mode-Fehler werden pro Gerät gezählt, sodass erfolgreiche Frames anderer Controller einen wiederholt fehlschlagenden Controller nicht länger verdecken.

## Version 3.4.2 INTERN

Der Start-Hotfix korrigiert die Initialisierungsreihenfolge der RGB-Vorschau: Ihr Zeitgeber existiert nun vor dem Aufbau der RGB-Seite. Zusätzlich schützt ein Fallback gegen vergleichbare frühe Aufrufe. Automatische private Start- und Absturzprotokolle im XDG-Zustandsverzeichnis werden vom Diagnosewerkzeug anonymisiert mit erfasst.

## Version 3.4.1 INTERN

Das RGB-Studio startet das separat installierte OpenRGB-Backend selbst als privaten, fensterlosen Kindprozess auf `127.0.0.1:6742`. Ein eigener OpenRGB-Start ist nicht mehr nötig. Version 3.4.1 verarbeitet jedes Gerät in einer eigenen seriellen CLI-Transaktion, nachdem OpenRGB 1.0~rc2 bei mehreren `--device`-Blöcken reproduzierbar in `ApplyOptions` abgestürzt ist. Geräte ohne Direct Mode erhalten passende gemeldete native Fallbacks.

Auswahl und Gruppen bleiben erhalten, auch wenn die Oberfläche vor der asynchronen Erkennung aufgebaut wird. Gleichnamige Geräte sind getrennt benennbar. Die neue PC-Skizze speichert Position, Anzahl, Anschluss, Gruppe und zugeordnete Kacheln; Frelidons Vorlage enthält Kraken, A1/A2, B6/B7 und `SYS-FAN6`. Die separate sichtbare NZXT-RGB-Box entfällt zugunsten der gemeinsamen `led1`-bis-`led3`-Kacheln.

Schreibzugriffe bleiben pro Sitzung gesperrt. Eine fremde OpenRGB-Instanz und eine zweite schreibende OHC-Instanz werden blockiert. ENE-DRAM-Namensvarianten werden paarweise dedupliziert, ohne echte Riegel zusammenzulegen. NZXT „Flügel“ und andere topology-sensitive Modi werden pro physischem Lüfterkanal übertragen. Eine Softwareanimation hat höchstens einen Einzelgeräteprozess gleichzeitig und stoppt nach drei Fehlern. Der Komplett-Reset beendet Animationen, setzt verfügbare Hardwarestandards und gibt die verwaltete Engine frei.

OpenRGB und das Effects Plugin wurden als GPL-2.0-or-later geprüft. Eine Kombination unter GPLv3 wäre lizenzseitig grundsätzlich möglich. 3.4.1 übernimmt dennoch keinen fremden C++-/Plugin-Code und keine Assets, sondern verwendet den separaten Dienst und eigene Algorithmen. Der Build bleibt intern, bis reale Mehrgeräte- und Distributionsprüfungen erfolgt sind.

Der Desktop-Design-Bereich ist seit 3.3.0 ausdrücklich experimentell, standardmäßig ausgeschaltet und vollständig aus Navigation und Ansichtsmenü verborgen. Er erscheint erst nach Aktivierung in den Einstellungen; bis dahin erfolgt auch kein Paketangebot.

## Version 3.2.0 INTERN

Windows-8/8.1-Kachelübersicht und Charms-Leiste, freie auswählbare OHC-Symbole/Mauszeiger sowie selektierbare
Desktop-Backups mit geprüftem Export/Import und Breeze-Light-Notfallfallback. Der Build bleibt intern.

## Version 3.1.1 INTERN

Fedora 44 liefert das für Plasma-Skripte verwendete Qt-6-D-Bus-Werkzeug als `qdbus-qt6` statt `qdbus6` aus.
Die Anwendung erkennt jetzt beide Namen und bekannte Qt6-Systempfade direkt. Fehlende KDE-Werkzeuge werden
einmal automatisch angeboten und können auch später über den Desktop-Design-Bereich installiert werden. Die
Paketzuordnung unterstützt DNF, APT, Pacman und Zypper; optionale Desktop-Abhängigkeiten blockieren die
Hardwaresteuerung nicht.

Die hierarchische Navigation enthält neu **System → Desktop-Designs**. Das Modul wird nur in einer erkannten KDE-Plasma-6-Sitzung freigeschaltet und bietet eine Windows-11-artige Anordnung mit unterer Leiste sowie eine macOS-artige Anordnung mit oberer Systemleiste und unterem Dock. Beide Anordnungen besitzen einen hellen und einen dunklen Modus.

Die Vorschau ist vollständig schreibfrei. Erst ein eigener Bestätigungsdialog startet die Änderung. Unmittelbar davor werden `kdeglobals`, `kwinrc`, Plasma-Leistenlayout und weitere ausdrücklich berührte KDE-Dateien in einem datierten Benutzer-Backup gesichert. Scheitert ein Schritt, wird dieses Backup automatisch wiederhergestellt. Das letzte Backup lässt sich zusätzlich manuell aus der Oberfläche zurückspielen.

Für die Optik werden ausschließlich bereits vorhandene KDE-Breeze-Komponenten, Noto Sans und zwei im Projekt erstellte GPL-SVG-Hintergründe verwendet. Es gibt keine externen Design-Downloads, keine zusätzlichen Paketquellen, keine Administratoraktion und keine Microsoft-/Apple-Logos, -Schriften oder -Hintergrundbilder. Andere Desktopumgebungen werden nicht verändert.

Der Build ist ausdrücklich intern: ZIP, DEB und RPM tragen eine INTERN-/intern2-Kennzeichnung. `BUILD_CHANNEL=INTERN` sperrt die öffentlichen Veröffentlichungshelfer, damit dieser Teststand nicht versehentlich als GitHub-Release erscheint. Die Hardwarefunktionen aus 3.0.9 bleiben unverändert enthalten.

## Version 3.0.9

Das OpenLinkHub-Mausmodul verbindet die in 3.0.7 eingeführten eigenen GPL-SVG-Schemata nun mit der dokumentierten Tastenbelegung. Ein Klick auf eine von OpenLinkHub gemeldete physische Taste öffnet einen Dialog für Originalfunktion, Keine, Medien, DPI, Tastatur, Sniper-DPI, Maus oder ein vorhandenes Makro. Die Zuordnung wird erst nach ausdrücklicher Schreibfreigabe und ausschließlich über den fest erlaubten Endpunkt `/api/mouse/updateKeyAssignment` übertragen. Fehlt ein sicher gemeldeter Tastenindex, bleibt das Schema absichtlich nur lesbar.

Ein begrenzter Tastaturmakro-Recorder erstellt OpenLinkHub-Makros aus Einzeltasten und Pausen. Er erfasst nur Eingaben im sichtbaren, fokussierten Dialog, höchstens 64 Tasten und höchstens fünf Sekunden Pause je Schritt. Es gibt keinen globalen Tastatur-Hook und keine verdeckte Aufnahme außerhalb der Anwendung.

Die generierten LCD-Hardwaredesigns zeigen keine kleinen `LIVE`-, `LETZTER WERT`- oder `KRAKEN CONTROL`-Zusätze mehr. Akzentfarbe, Beschriftungsfarbe und Zahlenfarbe sind getrennt einstellbar; Beschriftung und Temperaturzahl besitzen jeweils eine eigene Größe. Eine globale Celsius-/Fahrenheit-Auswahl gilt für Oberfläche, Kurveneditor, Sicherheitsgrenzen, Profile sowie neue statische und animierte LCD-Hardwarebilder. Kühlkurven und Sicherheitslogik speichern intern weiterhin Celsius, damit ein Einheitenwechsel keine Regelwerte verändert.

Beim Wechsel der Temperatureinheit wird ein laufender generierter Hardwareanimationsmodus kontrolliert mit dem neuen Zahlenformat aufgebaut. Benutzerprofile speichern Einheit und neue Darstellungswerte; ältere Profile übernehmen sichere Standardwerte. Die Wiederherstellung der originalen Kraken-Flüssigkeitstemperaturanzeige beim echten Beenden, der verzögerte LCD-Autostart und die CPU-Kurvenregelung bleiben erhalten.

## Version 3.0.7 INTERN

Beim echten Beenden wird zuerst ein laufender CAM-Raw-GIF-Streamer vollständig geschlossen. Anschließend überträgt der Hauptprozess synchron den liquidctl-Befehl für die originale Kraken-Flüssigkeitstemperaturanzeige. Erst danach folgt der autonome Flüssigkeitstemperatur-Kühlfallback für aktive CPU-Kurvenkanäle. Dieser Ablauf gilt auch für geordnete Sitzungssignale beim Abmelden, Neustarten oder Herunterfahren. Das normale Schließen in den System-Tray läuft nicht durch diesen Pfad; dort bleiben LCD-Ausgabe und CPU-Kurvenregelung aktiv.

Das OpenLinkHub-Mausmodul erhielt erstmals eine grafische Zuordnung zwischen physischer Taste und Funktion. Fünf vollständig im Projekt gezeichnete GPL-SVGs decken kompakte, ergonomische, symmetrische, Mehrknopf- und MMO-Formen ab. Die Auswahl erfolgt aus dem Produktnamen, ohne zu behaupten, ein exaktes Hersteller-Rendering zu sein. Anklickbare Qt-Hotspots liegen über dem SVG und sind mit einer dreispaltigen Tabelle für Nummer, Position und Funktion gekoppelt.

## Version 3.0.6 INTERN

Der Profilstart stellt nun auch den tatsächlich aktiven LCD-Modus vollständig wieder her. Gesamt- und LCD-Profile speichern neben Datei, Ausrichtung und Helligkeit einen eindeutigen Modus für Einzelbild, wiederholtes Bild, Uhr, statisches Hardwaredesign, generierte Hardwareanimation oder normales GIF. Profile aus 3.0.5 besitzen dieses Feld noch nicht; eine dort gespeicherte `.gif`-Datei wird deshalb sicher als GIF-Modus migriert, ein statisches Bild als einmalige Bildübertragung.

Beim Desktop-Autostart markiert `--autostart` weiterhin den Hintergrundstart. Das Hauptfenster bleibt nach abgeschlossenem Erstsetup im Tray beziehungsweise ohne verfügbaren Tray minimiert. Ein im Gesamtprofil gespeicherter maximierter Fensterzustand wird nur beim manuellen Anwenden, niemals beim automatischen Hintergrundstart berücksichtigt. Nach dem Laden des Startprofils wird der versteckte Zustand zusätzlich nochmals angewendet.

Die LCD-Wiederherstellung wartet beim Desktop-Autostart bis fünf Sekunden nach dem Anwendungsstart. Erst danach beginnt der gespeicherte Bild-, Uhr-, Hardware- oder GIF-Modus. So können Plasma, System-Tray, udev-Zugriff und andere Desktopdienste zuerst anlaufen. Ein manueller Programmstart verwendet weiterhin nur die normale kurze Geräteverzögerung.

Geordnete Sitzungssignale (`SIGTERM`, `SIGINT`) werden in den Qt-Abschlussweg überführt. Der experimentelle LCD-Crashmarker wird vor längerem Stream- und USB-Aufräumen gelöscht. Ein echter Absturz behält unverändert die Sicherheitswiederherstellung; ein normaler Neustart des Desktops blockiert das gespeicherte LCD-Profil nicht mehr fälschlich.

## Version 3.0.5 INTERN

Die beiden sichtbaren NZXT-Kurven verwenden jetzt ausschließlich die CPU-Temperatur als Eingangsgröße. Die Kraken-Firmware kann selbst nur ihre Flüssigkeitstemperatur auswerten; deshalb berechnet Open Hardware Control die CPU-Kurven als laufende Software-Regelung und überträgt das jeweilige Ergebnis als festen Pumpen- beziehungsweise Lüfterwert.

Ein eigener 1-Sekunden-Timer liest `k10temp` über Linux-hwmon, unabhängig von Kraken-Statusabfragen und USB-Eigentum. Die Regelung interpoliert linear zwischen den fünf Punkten, glättet kurze Ryzen-Temperatursprünge per EMA, quantisiert auf 2-Prozent-Stufen und verwendet getrennte Mindeständerungen und Sperrzeiten: steigende Kühlanforderungen reagieren schneller, fallende Werte werden bewusst verzögert. Erreichen Rohwert oder Kurve den letzten Punkt, werden sofort 100 Prozent angefordert.

Während des exklusiven CAM-Raw-LCD-Streams bleibt das CPU-Sensing aktiv. Eine tatsächlich notwendige Änderung verwendet die in 3.0.1 eingeführte PAUSE-/RESUME-Übergabe; Pumpe und Lüfter werden innerhalb desselben USB-Fensters nacheinander gesetzt. Der Streamer und sein Framecache bleiben dabei erhalten.

Alle AM5-Profile wurden auf CPU-Punkte umgestellt. Profile für 95-°C-Tjmax erreichen bei 90 °C 100 Prozent, Ryzen-7000-X3D-Profile bei 85 °C. Alte gespeicherte Wasserpunkte mit Endwert um 45 bis 50 °C werden beim Upgrade niemals als CPU-Kurve übernommen. Sie werden durch die passende neue CPU-Kurve ersetzt.

Die Wassertemperatur bleibt unabhängig als Sicherheitsgröße mit Warnung bei 42 °C, kritischem Grenzwert bei 50 °C und optionaler 100-Prozent-Umschaltung erhalten. Nach fünf aufeinanderfolgenden CPU-Sensorfehlern setzt die Software aktive Kurvenkanäle vorsorglich auf 75 Prozent. Beim echten Beenden – nicht beim Minimieren in den Tray – schreibt die Anwendung konservative autonome Flüssigkeitstemperaturkurven in die Kraken, weil eine CPU-Softwarekurve ohne laufenden Prozess nicht weiterregeln kann.

## Version 3.0.4 INTERN

Das Corsair-/OpenLinkHub-Modul erhält erstmals direkte Gerätesteuerung innerhalb der gemeinsamen Oberfläche. Die App liest vorhandene Temperatur- und RGB-Profile sowie Geräte- und Kanalfähigkeiten aus der lokalen API. Für passende Geräte stehen Kühlprofile/manuelle Leistung, RGB-Profil, Helligkeit, Kanalbezeichnung, LCD-Ausrichtung, Maus-DPI und -Optionen, Tastaturprofile und gerätespezifische Werte sowie Headset-ANC/Sidetone bereit.

Die Schreibseite bleibt beim Start immer gesperrt und muss ausdrücklich für die aktuelle Programmsitzung bestätigt werden. Bei zwei gleichzeitig aktiven OpenLinkHub-Diensten oder nicht erreichbarer Loopback-API ist keine Freigabe möglich. Das Hilfsmodul besitzt eine feste Zuordnung aus Aktionsnamen zu dokumentierten API-Pfaden und baut jede Nutzlast nach strenger Typ-, Bereichs- und Textprüfung neu auf. Weder die GUI noch ein Kommandozeilenargument können einen beliebigen API-Pfad bestimmen.

Vollständige Corsair-Seriennummern werden weiterhin nicht an Oberfläche oder Log übergeben. Die Statusabfrage erzeugt eine SHA-256-Steuerkennung; unmittelbar vor einem Befehl ordnet das Hilfsmodul diese gegen die aktuelle lokale Geräteliste eindeutig zu. Damit kann die App das Gerät lokal steuern, ohne seine vollständige Kennung in kopierbaren Diagnosedaten zu führen.

Komplexe Makrofolgen, freie Tastenbelegungen, der vollständige RGB-Editor sowie das Anlegen und Hochladen neuer LCD-Medien verblieben in dieser Version zunächst im OpenLinkHub-Web-Dashboard. Die NZXT-Kraken- und GIF-Funktionen blieben unverändert.

## Version 3.0.3 INTERN

Die sichtbare Modusmarkierung in der Kühlungsansicht verwendet keinen `checkable`-Zustand der Qt-Schaltfläche mehr. Dieser Zustand wechselte bereits beim Klick und konnte deshalb während des asynchronen Gerätebefehls kurz den falschen Modus beziehungsweise eine kaum lesbare Theme-Farbe zeigen. Stattdessen erhalten die vier Schaltflächen jetzt eine explizite Eigenschaft `coolingState`. Nur der zuletzt erfolgreich auf die Kraken übertragene Modus wird fest grün dargestellt; Normal-, Hover- und Gedrückt-Zustand besitzen jeweils ausdrücklich definierte Farben.

Die Änderung ist rein visuell und zustandsbezogen. Liquidctl-Befehle, Kurvenvalidierung, Profile und die koordinierte USB-Übergabe bei laufender Animation bleiben unverändert. Während ein neuer Befehl läuft oder fehlschlägt, bleibt der vorher bestätigte Modus sichtbar aktiv.

Der reale Hardwaretest von 3.0.2 bestätigt zusätzlich die in 3.0.2 eingeführte Kurvenumschaltung: Bei laufender 25-FPS-Hardwareanimation wurde die Lüfterkurve `25/25, 30/35, 35/50, 40/75, 45/100` übertragen und dieselbe Animation nach 258 Millisekunden aus dem bestehenden Cache fortgesetzt. Die Schnellprofile Pumpe/Lüfter `45/35`, `100/100` und erneut `45/35` wurden nach 351, 335 beziehungsweise 317 Millisekunden fortgesetzt. Der Stream blieb bei ungefähr 26,3 Hz mit 37,8 bis 38,8 Millisekunden Uploadzeit; es gab keine LCD-Frame-Sprünge, übersprungenen Transportframes, Watchdog- oder Sicherheitsstopps. Die liquidctl-Hinweise zum vorhandenen `nzxt_kraken3`-Kernel-Treiber waren Warnmeldungen, keine fehlgeschlagenen Befehle.

## Version 3.0.2 INTERN

Pumpe und Radiatorlüfter besitzen jetzt jeweils eine eindeutige Umschaltung zwischen **Manuell aktivieren** und der passenden **Hardwarekurve aktivieren**. Der manuelle Schalter überträgt den aktuellen Prozentwert als feste Drehzahl. Der Kurvenschalter prüft die angezeigten Punkte mit den bestehenden Sicherheitsregeln und überträgt die vollständige Wassertemperaturkurve. Erst ein erfolgreich abgeschlossener Kraken-Schreibbefehl markiert den neuen Modus als aktiv.

Die Modusanzeige ist mit allen vorhandenen Schreibwegen verbunden: manuelle Anwenden-Knöpfe, einzelne Kurven, Schnellprofile, Sicherheitsprofil, gespeicherte Profile und CPU-Assistenz aktualisieren denselben Zustand. Bei einer laufenden GIF- oder Hardwareanimation benutzen beide neuen Schalter die PAUSE-/RESUME-USB-Übergabe aus 3.0.1; es entsteht kein paralleler Kraken-Schreiber.

Der reale Hardwaretest von 3.0.1 an der NZXT Kraken 2023 mit Firmware 2.0.0 bestätigt die Übergabe für feste Werte. Bei laufender 25-FPS-Hardwareanimation wurden der Radiatorlüfter auf 100 Prozent und die Pumpe auf 100 Prozent gesetzt. Die Animation setzte sich nach 240 beziehungsweise 251 Millisekunden aus dem bestehenden Cache fort. Der Stream blieb bei ungefähr 26,3 Hz, ohne LCD-Frame-Sprünge, Watchdog- oder Sicherheitsstopp. Die liquidctl-Hinweise zum vorhandenen `nzxt_kraken3`-Kernel-Treiber waren Warnmeldungen, keine fehlgeschlagenen Befehle.

## Version 3.0.1 INTERN

Die wichtigste Änderung ist die koordinierte Kühlungssteuerung bei laufender Kraken-GIF- oder Hardwareanimation. Ein zweiter Prozess schreibt weiterhin niemals parallel auf dieselbe Kraken. Stattdessen führt die App eine kurze Eigentumsübergabe durch:

1. Die GUI sendet `PAUSE` an den langlebigen Streamer.
2. Der Streamer beendet den aktuellen vollständigen Frame, schließt HID- und Bulk-Verbindung und bestätigt `paused`.
3. Die GUI überträgt exklusiv feste Pumpen-/Lüfterwerte, Kurven oder ein Kühlprofil über liquidctl Direct Access.
4. Erst wenn die gesamte serielle Befehlswarteschlange leer ist, sendet die GUI `RESUME`.
5. Der gleiche Streamer verbindet sich erneut, primt die bei der Pause vorgemerkte Cachephase zweimal und setzt seinen bereits vorbereiteten RGB565-Stream fort.

Der GIF-Prozess und sein Framecache werden dabei nicht beendet. Die Anzeige kann für die Dauer des liquidctl-Befehls kurz stehen, muss aber nicht neu decodiert oder vollständig neu gerendert werden. Die Übergabe besitzt getrennte Zeitlimits für USB-Freigabe und Wiederaufnahme. Fehler führen zum bestehenden Sicherheitsstopp und zur Wiederherstellung der Flüssigkeitstemperaturanzeige.

Unterstützt werden manuelle Pumpen-/Lüfterwerte, einzelne Pumpen-/Lüfterkurven, Schnellprofile, das Sicherheitsprofil, gespeicherte Kühlprofile und der vorhandene CPU-Assistenz-Schreibpfad. Normale Kraken-Statusabfragen bleiben während der Animation pausiert; die Wassertemperatur ist deshalb weiterhin der letzte sichere Wert. Eine sichere, autonom in der Kraken gespeicherte Hardwarekurve bleibt Voraussetzung.

## Version 3.0.0 INTERN

Diese Version ist der Übergang von Kraken Control 2.9.23 zu Open Hardware Control:

- linke, hierarchische Navigation statt sichtbarer Haupt-Tabs
- automatische Hardwareerkennung beim Start
- nicht erkannte Gerätemodule standardmäßig ausgeblendet
- Einstellung **„Nicht erkannte Geräte/Module anzeigen“**
- vollständiges NZXT-Kraken-Modul aus 2.9.23 mit Kühlung, RGB, LCD, Profilen, Sprachen und den abgesicherten LCD-Experimenten
- neues Corsair-/OpenLinkHub-Modul
- Erkennung von RPM-Installation sowie Benutzer- und Systemdienst
- ausschließlich lokale API unter `http://127.0.0.1:27003`
- Geräteliste und Telemetrie aus `GET /api/devices/`
- Start, Stopp und Neustart ausschließlich für `OpenLinkHub.service` im Benutzerkontext
- direkter Aufruf des lokalen OpenLinkHub-Web-Dashboards
- klare Warnung bei Systemkontext oder zwei gleichzeitig aktiven Diensten
- automatische Übernahme vorhandener Kraken-Control-Einstellungen beim ersten Start

## Navigationsmodell

Die Hauptbereiche sind hierarchisch angeordnet:

1. Übersicht
2. Geräte
   - NZXT Kraken 2023
     - Kühlung
     - RGB
     - LCD
   - Corsair · OpenLinkHub
3. Profile
4. Einstellungen
5. Diagnose
   - Log
   - Über

Gerätefamilien erscheinen nur, wenn passende Hardware, ein passender Dienst oder eine lokale API erkannt wurde. Für Entwicklung und Fehlersuche lassen sich alle Module einblenden.

## OpenLinkHub-Sicherheitsgrenze

Open Hardware Control spricht OpenLinkHub nur über eine validierte Loopback-Adresse an. Externe Hosts, HTTPS-Adressen, Zugangsdaten im URL-Text und API-Unterpfade werden vom Integrationsmodul abgelehnt. Seriennummern werden in der Oberfläche nur mit den letzten vier Zeichen dargestellt.

Seit Version 3.0.4 werden ausschließlich dokumentierte, fest freigegebene Corsair-Schreibaktionen verwendet. Version 3.0.9 ergänzt die dokumentierte Maustastenbelegung und eine begrenzte, fensterlokale Makroaufnahme. Nicht sicher aus der allgemeinen Geräteliste ableitbare Funktionen bleiben im lokalen OpenLinkHub-Web-Dashboard.

Dienstaktionen sind auf `systemctl --user` begrenzt. Der systemweite Dienst wird niemals automatisch angehalten, deaktiviert oder überschrieben. Bei einer Migration in den Benutzerkontext muss zuerst sichergestellt werden, dass nur eine OpenLinkHub-Instanz gleichzeitig auf die Hardware zugreift.

## NZXT-Modul

Der Funktionsstand der Kraken-Control-Version 2.9.23 bleibt enthalten:

- Kraken-Wassertemperatur, Pumpe und Radiatorlüfter
- feste Werte und softwaregeregelte CPU-Temperaturkurven über liquidctl Direct Access
- AMD-AM5-Profile mit eigenen Pumpen- und Lüfterkurven
- unabhängige Wassertemperatur-Sicherheitsüberwachung und autonomer Hardware-Fallback beim echten Beenden
- separater NZXT 2023 RGB Controller
- statische Bilder, Uhr, Live-Hardwaredesigns und animierte LCD-Designs
- CAM-naher, exklusiver Firmware-2.x-Rohbildpfad mit ACK-Prüfung, Watchdog und Sicherheitsfallback
- CPU-/GPU-Livewerte im isolierten Renderprozess
- Profile, vier Oberflächensprachen, adaptive Skalierung, Hintergrunddesigns und Diagnoseprotokoll

Die technische Vorgängerdokumentation `Kraken_Control_Projekt.md` und `USB_CAPTURE_FINDINGS.md` bleiben als Modulhistorie vollständig im Entwicklerpaket.

## Installation und Aktualisierung

```bash
chmod +x install.sh
./install.sh
```

Start:

```bash
~/.local/bin/open-hardware-control
```

Der bisherige Befehl `kraken-control` bleibt als Kompatibilitätsstarter erhalten. Das Installationsskript entfernt nur den alten Menüeintrag, nicht die frühere Programmdatei. Dadurch bleibt eine manuelle Rückkehr zur Vorgängerversion möglich.

## Noch zu testen

- 3.0.9 beim echten Beenden, Abmelden und Neustarten mit laufendem GIF prüfen: Nach USB-Freigabe muss die originale Wassertemperaturanzeige erscheinen
- normales Schließen in den Tray prüfen: Animation und CPU-Kurvenregelung müssen weiterlaufen und die Originalanzeige darf noch nicht erzwungen werden
- grafische Ansicht mit den tatsächlich angeschlossenen Corsair-Mausmodellen prüfen; gemeldete Belegungen und Hotspotpositionen vergleichen
- 3.0.6-Verhalten beim echten Plasma-Autostart erneut prüfen: Fenster muss im Tray bleiben und der gespeicherte LCD-/GIF-Modus darf frühestens fünf Sekunden nach Programmstart beginnen
- vorhandenes 3.0.5-Gesamtprofil mit ausgewählter GIF-Datei prüfen; die Animation muss ohne erneutes Profilaktualisieren automatisch migriert und gestartet werden
- normales Abmelden/Neustarten mit laufendem GIF prüfen; der nächste Start darf nicht fälschlich den LCD-Absturzfallback aktivieren

- OpenLinkHub 0.9.0 auf dem Zielsystem im aktuell aktiven Systemkontext erkennen
- Anzeige der tatsächlich angeschlossenen Corsair-Geräte und ihrer Kanalwerte
- Migration zum Benutzerdienst anhand der offiziellen OpenLinkHub-Anleitung
- Benutzeraktionen Start, Stopp und Neustart nach vorhandener User-Service-Installation
- gleichzeitige Nutzung des NZXT- und OpenLinkHub-Moduls ohne USB-Konflikte
- direkte OpenLinkHub-Steuerung an den tatsächlich angeschlossenen Corsair-Geräten prüfen und gemeldete Gerätefelder protokollieren
- überprüfen, welche Maus-, Tastatur- und Headset-Fähigkeiten OpenLinkHub 0.9.0 je Modell in `/api/devices/` ausgibt
- die neue feste grüne Aktivfarbe beim mehrfachen Wechsel zwischen Manuell und Kurve in hellem, dunklem und eigenem Akzent-Theme visuell prüfen
- 3.0.5 an der realen Kraken prüfen: CPU-Kurven für Pumpe und Lüfter einzeln und gemeinsam aktivieren
- Lastwechsel des Ryzen 7 9800X3D prüfen und Logwerte für Glättung, Hysterese und USB-Pausen vergleichen
- CPU-Kurvenregelung während eines 25-FPS-GIFs mindestens zehn Minuten prüfen; die Animation darf nur bei relevanten Prozentänderungen kurz pausieren
- echtes Beenden prüfen: konservative Wasser-Hardwarekurven müssen danach autonom weiterlaufen; Neustart muss die gespeicherten CPU-Modi wieder übernehmen
- prüfen, dass die Aktivmarkierung bei einem absichtlich fehlgeschlagenen Gerätebefehl im vorher bestätigten Zustand bleibt

## Lizenz und Unabhängigkeit

Open Hardware Control steht unter GPL-3.0-or-later. OpenLinkHub und liquidctl sind eigenständige Open-Source-Projekte und keine Bestandteile dieses Quellcodes. Produktnamen dienen ausschließlich der sachlichen Kompatibilitätsangabe. Das Projekt ist nicht offiziell mit NZXT, Corsair, OpenLinkHub oder OpenAI verbunden.
