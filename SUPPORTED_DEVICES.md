# Unterstützte Geräte – Open Hardware Control 3.4.29.45

## Direkt getestetes NZXT-Modul

| Gerät | USB-ID | Backend | Umfang |
|---|---|---|---|
| NZXT Kraken 2023 | `1e71:300e` | liquidctl | Wasser, Pumpe, Radiatorlüfter, LCD |
| NZXT 2023 RGB Controller | `1e71:2012` | liquidctl | drei RGB-Kanäle |

Der Schwerpunkt bleibt die NZXT Kraken RGB 360 (2023, Standard / Non-Elite) mit Firmware 2.0.0. Andere Kraken-Varianten gelten erst nach realem Hardwaretest als bestätigt.

## Thermalright Levita Vision 360 ARGB Black

| Teilpfad | Erkennung/Anschluss | Backend | Umfang und Status |
|---|---|---|---|
| Display | USB `87ad:70db` (`USBDISPLAY`) | separat installiertes GPL-Backend TRCC Linux 9.9.12 empfohlen; 9.9.11 getestet | Handshake Modell-ID 64/Sub 3 mit 1600×720 und sichtbarer Rot-/Grün-/Blau-/Schwarz-Übertragung unter 9.9.11 bestätigt; 9.9.12 ist CLI-/Daemon-kompatibel und behebt den Fedora-RPM-Konflikt, wurde am Referenzdisplay aber noch nicht erneut getestet |
| Pumpe | 4-Pin PWM, vom Linux-Treiber typischerweise als `Pump Fan` gemeldet | Linux hwmon/NCT6687 | RPM read-only erkannt; Schreiben erst nach separatem 70-%-/10-s-Test |
| Radiatorlüfter | 4-Pin PWM, vom Linux-Treiber typischerweise als `CPU Fan` gemeldet | Linux hwmon/NCT6687 | RPM read-only erkannt; Schreiben erst nach separatem 70-%-/10-s-Test |

OHC zeigt den exakten Namen **Thermalright Levita Vision 360 ARGB Black** an. USB-Display und PWM-Kühlung sind technisch getrennt. Die Linux-Headernamen dienen nur als Vorschlag; der Benutzer muss Pumpe und Radiatorlüfter einzeln physisch bestätigen. Danach stehen feste Werte, Leise/Ausbalanciert/Leistung/Sicherheit und CPU-Temperaturkurven zur Verfügung. Bei aktivem CoolerControl bleiben PWM-Schreibzugriffe gesperrt, und beim geordneten Programmende werden von OHC übernommene Header an BIOS/Firmware zurückgegeben.

Die kurze allgemeine TRCC-Geräteliste meldete zunächst eine generische 480×480-Zuordnung. Der anschließende vollständige Geräte-Handshake ist für die Geometrie maßgeblich und bestätigte `(1600, 720)`, Modell-ID 64 und Sub-Byte 3. Der offizielle TRCC-Farbzyklus wurde auf dem physischen Display sichtbar abgeschlossen. OHC behält deshalb die 1600×720-Arbeitsfläche und die dazugehörige rechte Aussparung bei.

TRCC Linux 9.9.11 verwendet für die dekorativen Split-Modi A–C unter PySide6 6.11 einen nicht kompatiblen Schlüsselwortaufruf von `QImage.mirrored()` und bricht dadurch beim Rendern ab. OHC 3.4.29.5 setzt einen eventuell gespeicherten Split-Modus deshalb zwingend vor dem Laden eines Mediums auf null. A–C bleiben klar als lokale Vorschau markiert; die physische rechte 80-Pixel-Aussparung wird weiterhin unabhängig vom TRCC-Split-Modus ausgespart.

OHC 3.4.29.8 richtet die eigene transparente Vollbildmaske nach der aktuellen Referenzaufnahme standardmäßig auf 80 Pixel und den Hintergrund auf X/Y 0 aus; die Breite bleibt zwischen 80 und 800 Pixeln einstellbar und kann direkt in der Vorschau gezogen werden. Bilder und übliche Videos werden immer seitenrichtig in eine lokale 1600×720-Cache-Arbeitskopie eingepasst oder optional unverzerrt beschnitten; komplette TRCC-Layouts und `.zt`-Dateien bleiben unverändert. Elementpositionen besitzen eine lokale Rückgängig-Historie, und `%`/Temperaturzeichen werden über den passenden TRCC-Einheitenpfad erhalten.

OHC 3.4.29.9 übernimmt die originalen TRCC-Kategorien samt gültigen ID-Bereichen: Gallery `a001–a082`, Tech `b001–b025`, HUD `c001–c072`, Light `d001–d055`, Nature `e001–e054` und Aesthetic `y001–y010`. Bereits vorhandene lokale Medien und Layoutordner werden anhand dieser ID einsortiert und numerisch geordnet. Unbekannte, fehlerhafte oder außerhalb des Bereichs liegende Namen bleiben unter „Eigene Dateien“; es werden keine Herstellerdateien geladen oder ausgeliefert.

OHC 3.4.29.10 verwendet für den schwarzen rechten Balken in Editor und realer Maskendatei einen dezenten Radius von 18 Renderpixeln an Ober- und Unterkante. Die neue Hover-Kachel zeigt nur lokale Vorschauen; bei gewöhnlichen Videos erzeugt das vorhandene `ffmpeg` bis zu vier kleine Cacheframes, die OHC selbst abspielt. Es startet weder einen externen Player noch einen Netzwerkabruf.

Zusätzlich trennt OHC 3.4.29.10 den Videohintergrund vom vollständigen Hardwaredaten-Design. Im Zwei-Ebenen-Modus lädt OHC zuerst den lokalen TRCC-Layoutordner, wodurch TRCC Linux dessen `config1.dc` als live aktualisierte Sensoranordnung übernimmt, und ersetzt anschließend nur den Hintergrund mit `play-video`. Die zum Design gehörende `01.png` wird mit dem rechten Levita-Balken alpha-komponiert. Diese Sequenz folgt dem vorhandenen Backendvertrag; ihr Dauertest auf dem physischen Display bleibt wie die übrige vollständige OHC-Designübertragung noch offen.

OHC 3.4.29.11 richtet den Radius ausschließlich an den beiden zum sichtbaren Display zeigenden Balkenecken aus; die rechte physische Außenkante bleibt bündig schwarz. Die zusätzlich aktive Fenster-/Helferprozessdiagnose verändert keine USB-, PWM- oder Backendgrenze und liest unter Wayland keine Fenster fremder Anwendungen aus.

Zusätzlich erkennt OHC die von TRCC Linux installierten vollständigen Levita-Landschaftsdesigns unter `~/.trcc/data/theme1600720l` automatisch. Ein solches Layout kann seinen eigenen Hintergrund und seine vorhandene `config1.dc` mit Live-Positionen, Farben und Sensorwerten direkt übernehmen oder als obere Datenebene über einem anderen lokalen Video dienen. Andere TRCC-Geometrien werden nicht als Levita-Design angeboten; Erkennung und Vorschau lösen keinen USB-Schreibzugriff aus.

OHC 3.4.29.12 stellt Hintergrund und Datenoberfläche als Karten dar und animiert Videos direkt in der großen Hauptvorschau. Carbon Blue, Titanium Blue und Plasma Circuit sind projektbezogene lokale 1600×720-Hintergründe. Breit gewählte TRCC-Elternordner liefern nur dann ein Live-Layout, wenn `1600720l` im Geometriepfad oder eine exakt 1600×720 große PNG-Vorschau die Levita-Fläche bestätigt. Der ausdrücklich aktivierbare Display-Autostart speichert beide Ebenen, bleibt im Testmodus schreibgeschützt und versucht ein beim Desktopstart noch nicht bereites Display höchstens einmal erneut.

OHC 3.4.29.13 trennt Bilder/Videos von vollständigen `config1.dc`-Datenoberflächen und erlaubt eine ausdrückliche manuelle Ebenenabweichung. Eigene Ordner können ohne Dateilöschung ausgeblendet und samt letzter Auswahl wieder aktiviert werden. Helligkeit und Ausrichtung sind echte, auf Levita begrenzte TRCC-Befehle. USB-Designwechsel warten auf die Freigabe des vorherigen Renderers und wiederholen einen bestätigten Handshake-Timeout höchstens einmal.

OHC 3.4.29.14 erzeugt die Startbilder großer Videokataloge über höchstens zwei Hintergrund-Worker. Ein Fortschrittsbalken bleibt sichtbar, bis die Warteschlange abgeschlossen ist; unveränderte Ergebnisse werden bei späteren Programmstarts direkt aus dem dauerhaften Cache geladen.

OHC 3.4.29.15 zeigt die gewählte Ebene‑2-Datenoberfläche auch über einem Bildhintergrund und nutzt bei unvollständigen TRCC-Layouts deren vollständige `Theme.png` als Vorschau. Die mittige Vorschau besitzt ohne seitliche Leerbalken exakt das Levita-Verhältnis 1600×720.

OHC 3.4.29.16 zeigt gleiche vollständige Dateinamen unabhängig vom Sicherungspfad nur einmal. Andere Namen oder Dateiendungen bleiben getrennt; keine Originaldatei wird gelöscht, verschoben oder verändert.

OHC 3.4.29.18 macht die Datenoberfläche 2 editierbar. Jeder logische Live-Block lässt sich einzeln ziehen; getrennt importierte CPU-/GPU-Beschriftungen und ihre Auslastungswerte werden dabei als gemeinsamer Block behandelt. Rechtsklick ändert Farbe, Schriftgröße und Text beziehungsweise Bezeichnung, während Gesamt-X/Y die komplette Ebene verschiebt. OHC speichert nur eigene Overrides und ein Cache-`trcc.json`; `config1.dc`, Bilder und Videos werden nicht überschrieben.

OHC 3.4.29.19 behebt den Übertragungsabbruch dieses Cache-Layouts. Der vorgeschaltete OHC-Check akzeptiert jetzt wie TRCC Linux entweder ein vorhandenes `config1.dc` oder ein geprüftes natives `trcc.json` mit 1600×720-Geometrie. Bestehende `editable-themes/theme-*`-Ordner werden direkt wiederverwendet; fehlerhaftes JSON und fremde Geometrien bleiben gesperrt.

OHC 3.4.29.21 übernimmt eine gewählte Ebene-1-Karte sofort in die große Vorschau und rundet nur die äußeren rechten Displayecken; die Innenkante des Notchbalkens bleibt gerade.
OHC 3.4.29.24 isoliert beschädigte Layoutdatensätze, weist symlink-verlinkte Theme-Dateien ab, startet Split-Vorschauen sicher auf Aus und bestätigt den Rendererstart vor der Aktivmeldung. USB-Protokoll und Hardwaregrenzen bleiben unverändert.

OHC 3.4.29.35 liest zusätzlich projekt-eigene und importierte native 1600×720-`trcc.json`-Layouts ein. Ebene 1 und 2 stehen nebeneinander; ein Kartenmenü weist komplette Themes ausdrücklich einer Ebene zu und verwaltet Favoriten, ohne Originaldateien zu verändern. Nebula Drift und Orbital Command sind eigene, mit OpenAIs eingebautem Bildgenerator erzeugte OHC-Grafiken; Orbital Command enthält CPU-/GPU-Auslastung, Temperatur, Takt und GPU-Speicherbelegung. Die acht vom Projektinhaber gezeigten Sci-Fi-Bilder dienten ausschließlich als Stilreferenz und werden nicht zusätzlich kopiert oder verpackt.

OHC 3.4.29.20 verwendet für Textblöcke dieselben Mittelpunkt-Koordinaten wie TRCC Linux. Videoframes aktualisieren nur noch Ebene 1, ohne die verschiebbaren Elemente der Ebene 2 neu zu erzeugen. Dadurch bleiben Uhr und Sensorblöcke beim Ziehen stabil; die Vorschau lädt den gewählten Hintergrund auch bei erneuter Auswahl sofort neu.

Nach einer ausdrücklichen Polkit-Administratorfreigabe verwendet OHC für wiederholte Kurvenwerte eine einzige prozessgebundene Helfersitzung. Deren Protokoll akzeptiert weiterhin ausschließlich begrenzte, validierte NCT6687-Aktionen; beim Programmende wird zuerst die Firmwaresteuerung wiederhergestellt und danach die Sitzung geschlossen. Dadurch entsteht nach Ablauf des kurzfristigen Polkit-Caches kein neuer Hintergrunddialog für jeden Kurvenwert.

Optional kann dieselbe eng begrenzte Helferaktion über „Dauerhafte Berechtigung erteilen“ einmalig für das aktuelle Benutzerkonto freigegeben werden. Die benutzerspezifische Polkit-Regel bleibt nach Neustarts erhalten, speichert kein Passwort und kann über „Dauerhafte Berechtigung entfernen“ wieder gelöscht werden. Kalibrierung, Besitzerprüfung, Watchdog und Firmware-Rückgabe werden dadurch nicht gelockert.

Seit 3.4.29.8 spiegelt der Root-Helfer diesen Zustand zusätzlich in einem lesbaren Statusmarker, weil normale Fedora-Benutzer das Polkit-Regelverzeichnis nicht durchsuchen dürfen. Der Marker erteilt selbst keinerlei Recht; Polkit bleibt maßgeblich, und Regel/Marker werden gemeinsam angelegt oder entfernt.

Der derzeitige Gerätepfad meldet keinen Kühlmittelsensor. OHC zeigt deshalb keinen künstlich aus CPU-/GPU-Temperatur abgeleiteten Wasserwert an. CPU-/GPU-Temperaturen können unabhängig davon für Anzeige und Softwarekurven verwendet werden.

## Corsair über OpenLinkHub

Open Hardware Control besitzt keine eigene feste Corsair-USB-Geräteliste. Es zeigt die Geräte an, die der lokal installierte OpenLinkHub-Dienst über `/api/devices/` meldet. Damit folgt der Erkennungsumfang der tatsächlich installierten OpenLinkHub-Version.

Seit Version 3.0.4 gibt es direkte Einstellungen nur für Geräte, Kanäle und Profile, die der lokale OpenLinkHub-Dienst meldet. Kühlung, RGB/LCD, Maus, Tastatur und Headset besitzen getrennte, validierte Aktionen. Nicht gemeldete oder komplexe gerätespezifische Funktionen bleiben im Web-Dashboard. Die reale Kompatibilität muss mit OpenLinkHub 0.9.0 und den angeschlossenen Corsair-Geräten geprüft werden.

Version 3.0.9 ordnet erkannte Mäuse anhand des Produktnamens einem generischen SVG-Schema zu. Berücksichtigt werden insbesondere Scimitar-, M55-/M75-, M65-/Dark-Core-/Ironclaw-/Glaive-/Sabre-, Darkstar-/Nightsabre-, Katar- und Harpoon-Familien. Unbekannte Mäuse erhalten das kompakte Standardschema. Das ist eine visuelle Orientierung und keine Aussage über eine exakte Gehäusegeometrie.

Eine Maustaste ist direkt belegbar, wenn OpenLinkHub für sie einen eindeutigen Tastenindex meldet. Unterstützt werden Keine, Medien, DPI, Tastatur, Sniper-DPI, Maus und vorhandene Makros. Die fensterlokale Makroaufnahme erzeugt nur Tastatur-/Pausenschritte; komplexe Folgen bleiben im OpenLinkHub-Web-Dashboard. Welche Zuweisungen ein konkretes Modell tatsächlich annimmt, hängt von der installierten OpenLinkHub-Version und deren Gerätetreiber ab.

## Zusätzliche RGB-Geräte über OpenRGB

Version 3.4.23 besitzt bewusst keine kopierte OpenRGB-USB-Geräteliste. OHC startet das installierte Backend selbst als privaten, fensterlosen Kindprozess und zeigt ausschließlich die von ihm gemeldeten Geräte, Zonen, LEDs und Modi an. Damit entspricht die Hardwareabdeckung der installierten OpenRGB-Version und deren aktivierten Treibern/udev-Regeln.

Auch die kurzlebigen OpenRGB-Clientprozesse für Geräteinventar und native Moduswechsel werden ausdrücklich mit einer Offscreen-Qt-Plattform gestartet. Damit können GUI-basierte OpenRGB-Builds beim OHC-Start kein leeres Hilfsfenster mehr öffnen.

Seit 3.4.29.10 gilt diese Offscreen-Umgebung ausdrücklich auch für die synchrone Versionsabfrage beim Aufbau der Über-Seite und den direkten Inventar-Hilfspfad.

Ein unerwartet abgestürzter privater OpenRGB-Prozess wird seit 3.4.29.8 für den Rest der laufenden OHC-Sitzung nicht automatisch neu gestartet. Erst „RGB-Geräte neu erkennen“ hebt diese Sperre bewusst auf; dadurch entstehen bei einem fehlerhaften OpenRGB-Gerätetreiber keine wiederholten Coredumps.

Direct-Geräte werden seit 3.4.5 für Farbe und OHC-Effekte über den lokalen SDK-Helfer geschrieben und erreichen den bestätigten CLI-`ApplyOptions`-/`stl_vector`-Absturzpfad nicht mehr. 3.4.7 handelt die auf Fedora gemeldeten SDK-Protokollrevisionen 4 und 5 kompatibel aus. 3.4.9 richtet variable Zonen ein und bestätigt Servermodus sowie Farbpuffer durch Rücklesung. 3.4.10 sendet zusätzlich immer den vollständigen Geräteframe und beim ersten Direct-Wechsel einmal vollständige Zonenframes als Treiber-Fallback. Bei nativen Nicht-Direct-Modi sperrt OHC weiterhin nur das tatsächlich abstürzende Gerät bis zum nächsten Programmstart.

3.4.23 hält für Softwareanimationen eine SDK-Verbindung offen und sendet alle ausgewählten Direct-Geräte in einem gemeinsamen, begrenzten Frame mit 25-Hz-Ziel. Ein ARGB-Controller kann die Zahl verketteter Lüfter/LEDs weiterhin nicht elektrisch erkennen; der Einrichtungsassistent und der Einzelzonen-Sichttest führen deshalb durch die reale Zuordnung.

ARGB-Controller können Zonen melden, ohne die Zahl der elektrisch angeschlossenen LEDs zu kennen. 3.4.9 bietet deshalb „LED-Zonen und Lüfter einrichten“ an: OHC übernimmt vorhandene OpenRGB-Werte, schlägt bei einer passenden PC-Position die bekannte Lüfterzahl vor und lässt pro Zone Lüfterzahl sowie LEDs je Lüfter festlegen. 3.4.10 ergänzt Profile für TZMRIT/Jungle-Leopard Interstellar V2 Normal und Reverse mit 24 LEDs je Lüfter sowie Plausibilitätswarnungen. Die physische LED-Zahl ist nicht elektrisch rücklesbar; die Serverbestätigung wird deshalb nicht als sichtbare Hardwarebestätigung ausgegeben.

- Statische Farbe: pro gemeldetem Gerät.
- Nativer Modus: nur aus der vom Gerät gemeldeten Modusliste.
- OHC-Softwareeffekte: bei gemeldetem `Direct` Mode; andere ausgewählte Geräte erhalten einen passenden tatsächlich gemeldeten nativen Hardwaremodus.
- NZXT: gesperrt, solange das eingebaute NZXT-/liquidctl-Modul das Gerät besitzt.
- Corsair: gesperrt, solange OpenLinkHub erkannt ist.
- Externe SDK-Server: nicht unterstützt; nur `127.0.0.1:6742`.
- Veränderliche ARGB-Zonen: sichere Größenkonfiguration pro Zone mit Lüfterzahl × LEDs je Lüfter; eine gespeicherte PC-Position dient nur als Vorschlag, nicht als elektrische Erkennung.
- ENE-DRAM-Aliaspaare werden dedupliziert; ein vollständig gespiegeltes Gesamtinventar wird auf die erste reale Hälfte reduziert. Mehrere reale Module mit identischem Namen bleiben erhalten.
- ENE-DRAM erhält vor einem gespeicherten automatischen RGB-Start zwei geordnete OpenRGB-Direct-Durchläufe. Ein erfolgreicher Prozessabschluss wird weiterhin nicht als optisch rückgelesene LED-Bestätigung ausgegeben.
- Ein über mindestens 2,5 Sekunden stabiler Rückgang um ein oder zwei Geräte wird als dauerhafte Hardwareänderung übernommen (beispielsweise nach Ausbau des NZXT-Controllers von sieben auf sechs Geräte). Große Einbrüche bleiben weiterhin durch die strengere Kaltstart-Wiederholungslogik geschützt.
- NZXT `led1` bis `led3` erscheinen als eigene Kacheln und können mit anderen Geräten gruppiert werden.
- Gleichnamige GPU-/Controller-Einträge bleiben getrennt, werden nummeriert und können benannt sowie einer PC-Position zugeordnet werden.
- Frelidons mitgelieferte verschiebbare PC-Ansicht bildet zwölf Lüfter ab: je nach gewählter Kühlhardware NZXT Kraken 360 oder Thermalright Levita Vision 360 oben, zwei Frontlüfter, drei Reverse-Intakes an Rückwand/Seite, drei Reverse-Intakes auf der Netzteilabdeckung vorne und einen Hecklüfter.
- Die Jungle-Leopard-GPU-Halterung ist in dieser bestätigten Referenzverkabelung eine eigene 24-LED-Komponente an Airgoo Channel B6. Sie wird nicht als ENE-DRAM-Gerät behandelt. Andere Anschlussnotizen wie A1/A2/B7 und die SYS-FAN-Kanäle bleiben editierbare Dokumentation und sind keine allgemeine automatische elektrische Port-Erkennung.

Die indirekte OpenRGB-Kompatibilität ist keine reale Bestätigung jedes einzelnen Gerätemodells. Neue Controller sollten zuerst mit einer statischen Farbe und geringer Helligkeit getestet werden.

## Mainboard-/Gehäuselüfter über Linux hwmon

Version 3.4.23 kann PWM-Kanäle steuern, die Linux über `/sys/class/hwmon` bereitstellt. Der erste Schwerpunkt ist NCT6687/NCT6687D, insbesondere MSI-X870-Systeme. Eine Boardbezeichnung wird nur zur Diagnose verwendet; OHC leitet daraus **keine** feste PWM-Zuordnung ab.

- Jeder PWM-Kanal muss vor automatischer Regelung mit dem geführten 70-%-/10-s-Test mit RPM-Beobachtung physisch bestätigt werden.
- Erst bestätigte und ausdrücklich aktivierte Kanäle dürfen von der 1-s-Regelschleife geschrieben werden.
- Sensorquellen: CPU, GPU, Kraken-Kühlmittel, Maximum oder gewichtete CPU/GPU-Temperatur.
- Pro Kanal: eigene Kurve, Mindestleistung, Hysterese und Reaktionsverzögerung.
- Leise/Ausbalanciert/Leistung können pro Kanal oder gemeinsam als Kurvenvorlage gewählt werden; die bestehende Kalibrierung und Aktivierung werden dabei nicht eigenmächtig geändert. Ein eigener Reset lädt den ausbalancierten Standard.
- PWM/DC kann nur umgeschaltet werden, wenn der Kernel für genau diesen Kanal `pwmN_mode` meldet. Der bestätigte Wechsel stoppt die OHC-Automatik, verwirft Kalibrierung/Aktivierung und verlangt anschließend den physischen 70-%-/10-s-Test erneut.
- Bei drei aufeinanderfolgenden fehlenden Sensorwerten fordert OHC 70 % als sicheren Laufzeit-Fallback an; ab 90 °C werden 100 % angefordert.
- Beim Deaktivieren der OHC-Regelung und beim geordneten Programmende wird die Firmware-/BIOS-Steuerung über `pwmN_enable` wiederhergestellt, soweit der Treiber dies schreibbar anbietet. Ein vorhandenes nct6687d-`fan_control_watchdog` wird während aktiver Regelung als zusätzliche 10-s-Absturzsicherung aufgefrischt.
- Wenn die PWM-sysfs-Dateien für den angemeldeten Benutzer nicht schreibbar sind, führt OHC **keinen** Schreibversuch aus. Der Treiber-/Secure-Boot-Dialog zeigt Diagnose und Einrichtungshinweise; Secure Boot/MOK wird nicht umgangen.
- GPU-Lüfter sind ausdrücklich nicht Teil dieser Funktion.

Die reale elektrische Zuordnung und die Schreibbarkeit hängen vom installierten Kernel-/NCT6687-Treiber und der konkreten Board-Firmware ab. Deshalb bleibt die Kalibrierung verpflichtend, auch wenn dasselbe Mainboardmodell bereits bekannt ist.

## Nicht enthalten

- allgemeines Mainboard-/Spannungs-/Takt-Tuning außerhalb der kalibrierten hwmon-PWM-Lüftersteuerung
- GPU-Lüftersteuerung
- Firmwareaktualisierungen
- Open Radeon Control Center; dieses bleibt eigenständig
- ungetestete direkte USB-Schreibzugriffe auf Corsair-Geräte
- eingebettete OpenRGB-Hardwaretreiber; der separat installierte Backendprozess wird von OHC verwaltet

Produktnamen dienen nur der Kompatibilitätsangabe. Open Hardware Control ist kein offizielles Produkt von NZXT, Corsair, OpenLinkHub oder OpenRGB.
