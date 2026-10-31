# Unterstützte Geräte – Open Hardware Control 3.4.29.129

3.4.29.129: Die Geräteunterstützung bleibt unverändert. Die Korrektur betrifft
ausschließlich die sichere Zuordnung und Bereinigung eines von OHC neu
gestarteten TRCC-Prozesses. 3.4.29.128: Die Geräteunterstützung bleibt unverändert. Die überarbeitete
GPU-Oberfläche und der Snapshot-Metadatenexport ändern keine Hardwaregrenzen;
Snapper-Löschen bleibt auf validierte Konfigurationen und positive Nummern
begrenzt. 3.4.29.127: Die Geräteunterstützung bleibt unverändert. Der Snapshot-Manager
ergänzt ausschließlich Linux-System- und Dateisystemfunktionen. 3.4.29.126: Die neue GPU-Oberfläche
verwendet weiterhin ausschließlich von LACT gemeldete Grenzen und dieselbe
lokale Unix-Socket-Schnittstelle. Ziehbare Kurvenpunkte, Entwürfe und der
kombinierte Test-/Übernahmeknopf umgehen weder CoolerControl-Besitzprüfung noch
physischen Reaktionstest oder automatische LACT-Rückstellung.

Entwicklung vom 25.09.26 für 3.4.29.125: Die Geräteunterstützung bleibt unverändert. Die
Gehäuseseite zeigt LED- und PWM-Aktionen nur für dazu fähige Blöcke und zählt
in einer lesenden Analyse Geräte, PWM-Zuordnungen, ARGB-Routen und LED-Pfade.
Display/Pumpenkopf zeigt keine erfundene LED- oder Lüftersteuerung. Exakte
0-MHz-GPU-Taktproben gelten bei AMD als normaler Energiesparzustand. Die
optionale dauerhafte GPU-Lüfterübernahme ist standardmäßig aus und greift nur
nach einem bestätigten LACT-Test; 100% wird unverändert als 100% übertragen.

3.4.29.124: Die physische Geräteunterstützung bleibt unverändert. Deklarierte
Gehäuselüfterzahlen und LEDs je Lüfter werden automatisch in den räumlichen
LED-Pfad übernommen, ohne Reihe/Ring automatisch umzuschalten. Ringpfade
verwenden die deklarierte Lüftersegmentierung für die einzelne LED-Reihenfolge.

3.4.29.122: Jeder
ARGB-Anschluss speichert seine räumliche Laufrichtung unabhängig; dies gilt
auch für Grafikkarte und Grafikkartenhalterung.

3.4.29.121: Der separate
SDK-Arbeiter kapselt Renderfehler jetzt pro Gerät ab. Eine gemeinsame begrenzte
Animationsuhr verhindert große Phasensprünge bei langsamen vollständigen
Geräteframes. Gespeicherte Lüftertopologien behalten ihre Einheiten und können
ihre Animationsrichtung unabhängig umkehren.

3.4.29.120: Die Modellnamen AMD RX 9000/7000 und NVIDIA RTX 50/40 dienen
ausschließlich der Profiloberfläche. Sie sind keine pauschale Schreib- oder
Kompatibilitätszusage; Grenzen stammen weiterhin nur live von LACT. GPU-
Unterprofile sind an die exakte LACT-Geräte-ID gebunden und dürfen erst nach
lokaler Prüfung automatisch schreiben. Eigene transparente GPU-Bilder und die
neutralen OHC-Abbildungen ändern keine Hardwareunterstützung. Gamescope skaliert
nur den Lasttest. In dieser Entwicklung erfolgte kein physischer GPU-Schreibtest.

3.4.29.117: Die im `.116`-Nutzerprotokoll auf MSI und Airgoo abgestürzten
Zonenversuche sind entfernt. Laufende Effekte nutzen vollständige
OpenRGB-Geräteframes; frühere Versuchswerte sind wirkungslos. Nach einem
vollständigen OHC-Neustart wurden wieder alle sechs Geräte erkannt.
Bestätigte physische LED-Zahlen und ARGB-Routen bleiben bestehen.

3.4.29.116: MSI-GPU und Airgoo-Halterung senden standardmäßig wieder
vollständige OpenRGB-Geräteframes. Die `.115`-Teststellung wird ignoriert.
Getrennte Zonenpakettests sind nur nach ausdrücklicher Auswahl möglich und
fallen bei SDK-Fehlern oder Engine-Ende auf den Standard zurück. Das
Nutzerprotokoll der `.115` zeigt Zeitüberschreitungen und einen
OpenRGB-Engine-Abbruch nach dem MSI-Zonenversuch; der optionale Weg ist auf
diesem Gerät nicht als stabil bestätigt.

3.4.29.115: Für eine ausdrücklich auf MSI-Mystic-Light zugeordnete GPU kann
der OpenRGB-SDK-Arbeiter testweise vollständige Zonenpakete senden. Der
bisherige Gerätepaketweg bleibt im GPU-Dialog wählbar. 24,5–25 bestätigte
SDK-Frames pro Sekunde an GPU und Halterung belegen keine ebenso flüssige
physische Ausgabe; der neue Weg braucht einen Sichtvergleich. Die animierte
Gehäusezeichnung ist rein lesend und zeigt ohne gespeicherten physischen
LED-Verlauf nur eine schematische Anordnung.

Die GPU-Seite kann auf einer von LACT 0.10.1+ gemeldeten AMD-GPU eine
fünfpunktige Lüfterkurve oder einen statischen Wert von 35–100 % vorbereiten.
Die Übernahme verlangt freigegebenen CoolerControl-GPU-Besitz, einen kurzen
LACT-Test und getrenntes Speichern. Ein längerer 4K/8K-Lasttest kann aktuelle
LACT-Werte ohne Tuning-Schreibzugriff prüfen; ein positiver Befund setzt
gemessene hohe GPU-Last voraus. Automatische Rückstellung setzt einen
passenden OHC-Vorwert voraus. Die vom Nutzer direkt in LACT gesetzten 100 %
lieferten im Snapshot 3852 RPM; der neue OHC-Lüfterpfad und 8K-Test sind
auf dieser Karte noch nicht praktisch bestätigt.

## Allgemeiner Hardware-Checker

Version 3.4.29.96 prüft ausschließlich lesend die vom laufenden Linux-System
gemeldeten CPU-/SMT-/Virtualisierungs-, Board-, PCIe-GPU-, NVMe- und RAM-Daten. Aktuelle und
maximale Linkgeneration/Lane-Zahl stammen vom Kernel. Eine grüne Anzeige ist
eine Übereinstimmung dieser Werte, keine neue allgemeine Kompatibilitätszusage.
GPU-Leerlaufdrosselung bleibt bis zu einem ausdrücklichen kurzen vkmark-,
glmark2- oder Vulkan-vkcube-Test
gelb. NVMe wird ohne Schreibbenchmark geprüft. Optionale DMI-Speicherdetails
laufen über eine feste Polkit-Abfrage; Passwörter und Seriennummern gelangen
nicht in OHC. Der lokale Referenzlauf ist keine Gerätefreigabe für andere PCs.

3.4.29.89 / RGB Studio 1.12: weichere offene GPU-Lichtspuren und optionale
gemeinsame GPU-/Halterungsanimation an ausdrücklich zugeordneten ausgewählten
Direct-Zonen. LED-Zahlen und physische Tests bleiben getrennt; keine neue
Treiber-/Firmware-Kompatibilität oder garantierte optische Bildrate.

3.4.29.112 zeigt GPU-/Halterungs-LEDs mit den konfigurierten Anschlusszahlen
und einstellbarem Vorlauf, Auslauf und Tempo. Die gemessene SDK-Übertragungsrate
ist sichtbar, die optische Hardwareausgabe bleibt nicht rücklesbar. Keine
zusätzliche Geräte- oder Protokollkompatibilität folgt daraus.

3.4.29.113 vergrößert die Standard-Lichtkante der GPU und hält den gemeinsamen
Bewegungszyklus bei getrennt eingestellten Kanten fest. Gespeicherte Werte und
physische LED-Zahlen bleiben erhalten; optischer Geräteabgleich steht aus.

3.4.29.114 ergänzt einen getrennten GPU-Weißspitzenregler und direkte
Live-Vorschau für bereits aktive OHC-Effekte. Die Gehäuseansicht zeigt nur
gespeicherte eindeutige LED-Verläufe. Keine neue Gerätefreigabe; die echte
GPU-Lichtwirkung muss optisch und anhand der SDK-Übertragungsrate nachgeprüft
werden.

Version 3.4.29.87: korrigierte persönliche Airgoo-
Zuordnung – Front A1 2×8 / SYS_FAN4; Boden Reverse-Intake B7 3×8 / SYS_FAN6;
Heck normal Abluft B8 1×8 / SYS_FAN1; Thermalright-Radiator A8 3×10;
GPU-Halterung B6 1×12. Der Eigentümer ersetzt damit seine ältere 24-LED-
Halterungsangabe. Historische Referenzen unten gelten hierfür nicht mehr.
RGB Studio 1.10 übernimmt diese Werte einmalig nur im persönlichen Profil;
eigene Hersteller/Modelle/Farben/LED-Zahlen können wiederverwendbar gespeichert
werden. Keine allgemeine Herstellerzahl, elektrische Erkennung oder Änderung
der PWM-Kalibrierung. Lokale Paketierung ersetzt keine Hardwareprüfung.

Deklarierte Streifen-/Ringverläufe und räumliche Laufrichtungen nutzen echte
LED-Indizes und vorhandene Gehäusepositionen, ohne die Verkabelung zu messen.
Komplettpakete sichern die Zuordnungen samt Modellen und Medien; beim Import
müssen Hardwareautomatik und PWM-Kalibrierung lokal neu bestätigt werden.

3.4.29.86: Persönliche Lüfterdeklarationen nach Marke/Modell/Schwarz-Weiß
und LEDs je Lüfter im Blockeditor. Die ASIN-Referenz B0CN39T7QN verwendet acht
vom Eigentümer beobachtete adressierbare LEDs, keine allgemein bestätigte
Herstellerzahl. Zwei Lüfter schlagen 16 LEDs nur am ausgewählten Anschluss
unter tatsächlichen SDK-Grenzen vor; keine Massenmigration anderer Zonen.
LED-Vorschau pausiert Erkennung/Auto-Apply und verhindert überlappende Tests;
Zuordnung bleibt offline editierbar, tatsächlicher Besitzschutz bleibt aktiv.
Native OpenRGB-Abstürze sind dadurch nicht als behoben bestätigt.

3.4.29.85: Controller und gemeldeten Direct-Anschluss direkt am Gehäuseblock
wählen, anschließend LED-Anzahl bearbeiten oder einzelne LEDs testen. Manuelle
Bindung bleibt vor Designprofilen geschützt; keine neue Gerätekompatibilität,
elektrische Erkennung, PWM-Steuerung oder optische Bestätigung daraus ableiten.

Stand 3.4.29.83: Der Besitzer hat 30 LEDs an seiner Sapphire RX 9070 XT NITRO+ am MSI JARGB 1 durch Index-Sichttests bestätigt (1 links, 30 rechts). Persönlicher Referenzbefund, kein allgemeiner Herstellerwert. Der Anschluss-/Pixeltest gilt jetzt für alle gemeldeten Direct-ARGB-Zonen; manuelle Werte bleiben vor Designprofilen geschützt. Zentrale Gehäuse-Seite teilt RGB/LED/PWM-Zuordnungen mit Kühlung, optional mit eigenen Positionen. Zählabhängige Effektglättung ist softwaregetestet, optische Flüssigkeit noch zu prüfen.

Entwicklung 3.4.29.102: Der GPU-Reiter zeigt zusätzlich alle durch OpenRGB
explizit als Grafikkarte klassifizierten RGB-Controller und öffnet ihren
bestehenden RGB-Studio-Steuerweg. Dazu können unterstützte MSI-I²C- und
ASUS-Aura-/ENE-SMBus-Karten ohne externes ARGB-Kabel gehören. OHC behauptet
keine pauschale MSI-/ASUS-Modellabdeckung; nur eine tatsächlich erkannte
Karte und ihre gemeldeten Modi/Zonen gelten als bedienbar. LACT-Tuning und
OpenRGB-Lichtsteuerung bleiben getrennte Hardwarepfade.

GPU-ARGB-Fix in 3.4.29.82: Controller und konkreter Anschluss werden getrennt gewählt. Der Einzelanschlusseditor speichert eine Grafikkarte als ein Gerät; der begrenzte Pixeltest hilft bei der sichtbaren Zuordnung. GPU-Effekte verwenden die eigene Zonenlänge, und aktuelle Verkabelung/LED-Anzahl bleiben gegenüber alten Designprofilen erhalten. Nur die bestätigte persönliche Sapphire-Ansicht wird einmalig auf MSI JARGB 1 migriert. 80/90 bleiben Benutzer-Testwerte, keine bestätigten physischen LED-Zahlen. Optische Hardwareprüfung offen.

## Direkt getestetes NZXT-Modul

| Gerät | USB-ID | Backend | Umfang |
|---|---|---|---|
| NZXT Kraken 2023 | `1e71:300e` | liquidctl | Wasser, Pumpe, Radiatorlüfter, LCD |
| NZXT 2023 RGB Controller | `1e71:2012` | liquidctl | drei RGB-Kanäle |

Der Schwerpunkt bleibt die NZXT Kraken RGB 360 (2023, Standard / Non-Elite) mit Firmware 2.0.0. Andere Kraken-Varianten gelten erst nach realem Hardwaretest als bestätigt.

## Thermalright Levita Vision 360 ARGB Black

| Teilpfad | Erkennung/Anschluss | Backend | Umfang und Status |
|---|---|---|---|
| Display | USB `87ad:70db` (`USBDISPLAY`) | separat installiertes GPL-Backend TRCC Linux 9.10.4 empfohlen | Handshake Modell-ID 64/Sub 3 mit 1600×720 und Farbzyklus unter 9.9.11 bestätigt; dauerhafte vollständige 1600×720-Frameausgabe, daemoninterner Videotakt und stabile Ressourcen unter 9.10.4 bestätigt |
| Pumpe | 4-Pin PWM, vom Linux-Treiber typischerweise als `Pump Fan` gemeldet | Linux hwmon/NCT6687 | RPM read-only erkannt; Schreiben erst nach separatem 70-%-/10-s-Test |
| Radiatorlüfter | 4-Pin PWM, vom Linux-Treiber typischerweise als `CPU Fan` gemeldet | Linux hwmon/NCT6687 | RPM read-only erkannt; Schreiben erst nach separatem 70-%-/10-s-Test |

OHC zeigt den exakten Namen **Thermalright Levita Vision 360 ARGB Black** an. USB-Display und PWM-Kühlung sind technisch getrennt. Die Linux-Headernamen dienen nur als Vorschlag; der Benutzer muss Pumpe und Radiatorlüfter einzeln physisch bestätigen. Danach stehen feste Werte, Leise/Ausbalanciert/Leistung/Sicherheit und CPU-Temperaturkurven zur Verfügung. Bei aktivem CoolerControl bleiben PWM-Schreibzugriffe gesperrt, und beim geordneten Programmende werden von OHC übernommene Header an BIOS/Firmware zurückgegeben.

Seit 3.4.29.76 schützt OHC lange Levita-Videoläufe vor dem am Referenzsystem belegten TRCC-Daemon-Speicheranstieg. Ein rein lesender Ein-Minuten-Wächter betrachtet ausschließlich den exakten eigenen `trcc daemon`-Prozess und führt ab 1 GiB RSS oder bei verlorener IPC-Verbindung einen kontrollierten `trcc kill` mit anschließender Designwiederherstellung aus. Die vorhandene einzelne TRCC-Warteschlange bleibt der einzige USB-Schreibpfad; eine Fünf-Minuten-Sperre verhindert Wiederholungsschleifen.

Seit 3.4.29.131 erkennt OHC die erfolgreiche TRCC-9.10.4-Übergabe an dessen eigenen VideoLoop. Der planmäßig beendete CLI-Helfer wird nicht mehr als Absturz neu gestartet; die Daemon-Speicherüberwachung bleibt als Notbremse aktiv. Der Referenzlauf sendete fortlaufend 1600×720-Frames, während RSS, Threadzahl und Dateideskriptoren stabil blieben. Der unabhängige Abschaltwächter ergänzt seinen installierten Modulpfad selbst und bleibt nach dem Ende des Elternprozesses importfähig.

Seit 3.4.29.67 kann der vorhandene Unterbau in den Einstellungen explizit oder automatisch gewählt werden: TRCC Linux für das Display, OHC Linux-hwmon für Mainboard-PWM. Eine ausdrückliche, nicht verfügbare Wahl fällt nicht still auf einen anderen Schreiber zurück. OHC-nativ und CoolerControl sind sichtbare, aber deaktivierte Zukunftsoptionen und erweitern die aktuelle Kompatibilitätsaussage nicht. Der kompakte Temperaturverlauf der Übersicht bleibt erhalten; die eigene Kühlungs-Unterseite erfasst plausible CPU-, GPU-/Hotspot-/VRAM-, RAM-, SSD/NVMe-, Mainboard-, VRM- und PCH-Quellen rein lesend für höchstens 24 Stunden/28.800 Messpunkte im flüchtigen RAM. Bei Levita bleibt Kühlmittel leer, weil das Gerät keinen solchen Messwert meldet.

Thermalright nennt für die Levita-Pumpe 3000 rpm ±10 % und für die TL-M12Q-Radiatorlüfter 2000 rpm ±10 % als Maximaldrehzahlen, aber kein Mindest-PWM-Signal. OHC bezeichnet seine Untergrenzen deshalb nicht als Herstellervorgabe: Bis belastbare modellspezifische Mindestwerte vorliegen, werden vorsichtige 50 % Pumpe und 25 % Radiator an Reglern, Profilen, Kurven und direkt vor dem finalen hwmon-Schreiben erzwungen. Die physische Kanalbestätigung und CoolerControl-Besitzsperre bleiben zusätzlich erforderlich.

Seit 3.4.29.68 klappt der Bereich „Kühlung“ in der Hauptnavigation wie „LCD“ auf. „Steuerung & Profile“ öffnet die vorhandenen Wasserkühlungs- und Gehäuselüfterregler; „Temperaturaufzeichnung“ öffnet den ausführlichen read-only Verlauf. Diese reine Navigationsänderung erweitert keine Geräteunterstützung.

Die kurze allgemeine TRCC-Geräteliste meldete zunächst eine generische 480×480-Zuordnung. Der anschließende vollständige Geräte-Handshake ist für die Geometrie maßgeblich und bestätigte `(1600, 720)`, Modell-ID 64 und Sub-Byte 3. Der offizielle TRCC-Farbzyklus wurde auf dem physischen Display sichtbar abgeschlossen. OHC behält deshalb die 1600×720-Arbeitsfläche und die dazugehörige rechte Aussparung bei.

Seit 3.4.29.53 gibt ein echtes Programmende, Tray-„Beenden“, Logout oder behandelter Shutdown die Levita mit einem begrenzten `trcc device disconnect 87ad:70db` aus dem Daemon frei. Nach ungefähr zwei bis drei Sekunden ohne neue Frames zeigt die Firmware wieder ihr eingebautes Thermalright-Standardbild. Nach einem bestätigten echten Schreibzugriff überwacht ein getrennter Pipe-Wächter den OHC-Elternprozess und wiederholt nur diesen festen Rückfall einmal bei unerwartetem Prozessende; reine Vorschau aktiviert ihn nicht.

Seit 3.4.29.54 kann die eigene Seite „Display-Effekte“ einen prozeduralen Rauch-Loop mit dem ausgewählten Ebene-2-Sensorlayout vorbereiten. Sie erweitert keine Hardwareunterstützung und schreibt nicht selbst: Testmodus, TRCC-Warteschlange, Masken und der einzige USB-Besitzer bleiben im vorhandenen Levita-Studio.

Seit 3.4.29.55 erscheint der Fensterrahmen vor Geräteinitialisierung und Levita-Kartenaufbau. Die CoolerControl-Prüfung läuft außerhalb des GUI-Prozesses und bleibt bis zum bestätigten Ergebnis fail-closed. Grafische Sensorlayout-Karten und schnellerer Effekt-Cache ändern weder USB-Protokoll noch Geräteunterstützung; die zehnsekündige Schutzpause bleibt bestehen.

Seit 3.4.29.56 enthält Display-Effekte fünf frei lizenzierte, bearbeitete Videodesigns in vier Farbvarianten. Diese lokalen Medien erweitern nur die visuelle Auswahl; sie ändern weder USB-Protokoll noch Geräteunterstützung und werden weiterhin durch den einzigen Levita-/TRCC-Schreibpfad angewendet.

Seit 3.4.29.57 startet OHC einen unerwartet beendeten daemonseitigen Video-Taktgeber begrenzt neu. Dieser Wiederanlauf verwendet nur die vorhandene TRCC-IPC-Verbindung und erweitert weder Geräteunterstützung noch USB-Besitz; schnelle Dauerfehler werden nach drei Versuchen gestoppt.

Seit 3.4.29.59 werden gebündelte Bibliotheksvideos über eine eigene feste Paketwurzel statt über die private Cachegrenze validiert. Das behebt die zuvor stille Ablehnung beim Anwenden; Symlinks, Dateien außerhalb der jeweiligen Wurzel und andere Formate als MP4 bleiben gesperrt. Hardwarepfad und Geräteunterstützung ändern sich nicht.

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

Der derzeitige Gerätepfad meldet keinen Kühlmittelsensor. OHC zeigt deshalb keinen künstlich aus CPU-/GPU-Temperatur abgeleiteten Wasserwert an und blendet seit 3.4.29.80 auch die zugehörige Statuszeile und Kurvenquelle aus. CPU-/GPU-Temperaturen können unabhängig davon für Anzeige und Softwarekurven verwendet werden; die sicheren internen Untergrenzen bleiben in einer eigenen lesbaren Warnfläche sichtbar.

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
- Gleichnamige GPU-/Controller-Einträge bleiben getrennt, werden nummeriert und können benannt sowie einer PC-Position zugeordnet werden. Seit 3.4.29.80 öffnet ein Doppelklick auf die Komponente das zugeordnete Gerät und bei Direct-Geräten die vorhandene Zonen-/LED-Einrichtung. Der gelieferte Log weist für die Sapphire RX 9070 XT nur eine logische LED und Hardwaremodus aus; OHC erfindet deshalb keine adressierbaren GPU-Segmente.
- Frelidons mitgelieferte verschiebbare PC-Ansicht bildet zwölf Lüfter ab: je nach gewählter Kühlhardware NZXT Kraken 360 oder Thermalright Levita Vision 360 oben, zwei Frontlüfter, drei Reverse-Intakes an Rückwand/Seite, drei Reverse-Intakes auf der Netzteilabdeckung vorne und einen Hecklüfter.
- Die Jungle-Leopard-GPU-Halterung ist in dieser bestätigten Referenzverkabelung eine eigene 24-LED-Komponente an Airgoo Channel B6. Sie wird nicht als ENE-DRAM-Gerät behandelt. Andere Anschlussnotizen wie A1/A2/B7 und die SYS-FAN-Kanäle bleiben editierbare Dokumentation und sind keine allgemeine automatische elektrische Port-Erkennung.

Die indirekte OpenRGB-Kompatibilität ist keine reale Bestätigung jedes einzelnen Gerätemodells. Neue Controller sollten zuerst mit einer statischen Farbe und geringer Helligkeit getestet werden.

## Mainboard-/Gehäuselüfter über Linux hwmon

Version 3.4.23 kann PWM-Kanäle steuern, die Linux über `/sys/class/hwmon` bereitstellt. Der erste Schwerpunkt ist NCT6687/NCT6687D, insbesondere MSI-X870-Systeme. Eine Boardbezeichnung wird nur zur Diagnose verwendet; OHC leitet daraus **keine** feste PWM-Zuordnung ab.

- Jeder PWM-Kanal muss vor automatischer Regelung mit dem geführten 70-%-/10-s-Test mit RPM-Beobachtung physisch bestätigt werden.
- Erst bestätigte und ausdrücklich aktivierte Kanäle dürfen von der 1-s-Regelschleife geschrieben werden.
- Sensorquellen: CPU, GPU, Maximum oder gewichtete CPU/GPU-Temperatur; Kraken-Kühlmittel nur dann, wenn tatsächlich der Kraken-Pfad aktiv ist.
- Pro Kanal: eigene Kurve, Mindestleistung, Hysterese und Reaktionsverzögerung.
- Leise/Ausbalanciert können pro Kanal oder gemeinsam als Kurvenvorlage gewählt werden. **Leistung** ist ein konstanter 100-%-Override und wird bei laufender OHC-Regelung sofort neu ausgewertet. Kalibrierung und Aktivierung werden dabei nicht eigenmächtig geändert. Ein eigener Reset lädt den ausbalancierten Standard.
- Jede Gehäuselüfterkarte bietet einen bestätigungspflichtigen 0-%-/10-s-Stopptest zur Zuordnung und stellt danach den vorherigen Zustand wieder her. Manche Lüfter stoppen hardwarebedingt bei 0 % nicht vollständig.
- PWM/DC kann nur umgeschaltet werden, wenn der Kernel für genau diesen Kanal `pwmN_mode` meldet. Der bestätigte Wechsel stoppt die OHC-Automatik, verwirft Kalibrierung/Aktivierung und verlangt anschließend den physischen 70-%-/10-s-Test erneut. Fehlt `pwmN_mode`, legt das BIOS den elektrischen Modus fest; `pwmN` bleibt laut NCT6687-Treiber der Duty-/DC-Leistungswert.
- Bei drei aufeinanderfolgenden fehlenden Sensorwerten fordert OHC 70 % als sicheren Laufzeit-Fallback an; ab 90 °C werden 100 % angefordert.
- Beim Deaktivieren der OHC-Regelung und beim geordneten Programmende wird die Firmware-/BIOS-Steuerung über `pwmN_enable` wiederhergestellt, soweit der Treiber dies schreibbar anbietet. Ein vorhandenes nct6687d-`fan_control_watchdog` wird während aktiver Regelung als zusätzliche 10-s-Absturzsicherung aufgefrischt.
- Wenn die PWM-sysfs-Dateien für den angemeldeten Benutzer nicht schreibbar sind, führt OHC **keinen** Schreibversuch aus. Der Assistent prüft Distribution, Mainboard, Secure Boot, DKMS-Zertifikat, MOK-Registrierung, Modulsignatur und Ladestatus read-only und führt seit 3.4.29.80 Seite für Seite durch die noch offene Aktion. Seit 3.4.29.150 kopiert er getrennte feste Abhängigkeitsbefehle für Ubuntu, Fedora und Arch Linux; Klonen und DKMS-Installation entsprechen danach der [offiziellen nct6687d-Anleitung](https://github.com/Fred78290/nct6687d). Seit 3.4.29.151 sind Ubuntu-Aktualisierung und Installation getrennt, ein vorhandener fester Checkout wird nur per Fast-Forward aktualisiert und die optionale eng begrenzte Lüfter-Dauerfreigabe erscheint als Schritt fünf. Fremde Paketquellen werden nicht automatisch geändert. Die MSI-X870-Option wird nur auf passend erkanntem MSI-X870-Mainboard ergänzt. Unter Arch gilt `linux-headers` für den Standardkernel; andere Kernel brauchen ihr passendes Headerpaket. Eine bestätigende `mokutil`-Textausgabe bleibt auch neben der beobachteten Kernel-Keyring-Warnung gültig. Bestätigte Schaltflächen öffnen nur feste Befehle für Schlüsselerzeugung, `mokutil --import /var/lib/dkms/mok.pub` oder `modprobe nct6687` im sichtbaren Terminal; Passwort und physische MOK-Manager-Bestätigung bleiben vollständig außerhalb von OHC. Secure Boot wird nicht umgangen.
- Seit 3.4.29.152 speichert der PC-Profilmanager CPU_FAN, PUMP_FAN und SYS_FAN gemeinsam als reine Topologieeinstellung. Das Zuordnen oder Laden kalibriert, aktiviert oder beschreibt keinen Kanal. Auf dem erkannten MSI MAG X870 TOMAHAWK WIFI wird die vom Besitzer bereits bestätigte Referenzbelegung einmalig anhand der eindeutigen Treiber-Anschlussnamen ergänzt; vorhandene Nutzereinträge haben Vorrang.
- GPU-Lüfter sind ausdrücklich nicht Teil dieser Funktion.

Die reale elektrische Zuordnung und die Schreibbarkeit hängen vom installierten Kernel-/NCT6687-Treiber und der konkreten Board-Firmware ab. Deshalb bleibt die Kalibrierung verpflichtend, auch wenn dasselbe Mainboardmodell bereits bekannt ist.

## Nicht enthalten

- allgemeines Mainboard-/Spannungs-/Takt-Tuning außerhalb der kalibrierten hwmon-PWM-Lüftersteuerung
- Firmwareaktualisierungen
- Open Radeon Control Center; dieses bleibt eigenständig
- ungetestete direkte USB-Schreibzugriffe auf Corsair-Geräte
- eingebettete OpenRGB-Hardwaretreiber; der separat installierte Backendprozess wird von OHC verwaltet

Produktnamen dienen nur der Kompatibilitätsangabe. Open Hardware Control ist kein offizielles Produkt von NZXT, Corsair, OpenLinkHub oder OpenRGB.
