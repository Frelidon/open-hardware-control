# RGB-Studio – Open Hardware Control 3.4.16 INTERN

## Tempoübernahme und automatische Inventarnachprüfung 3.4.16

Änderungen an Tempo, Farbe, Helligkeit und Richtung werden kurz zusammengefasst. Läuft noch ein NZXT-/GPU-Auftrag, bleibt nur der neueste Stand vorgemerkt und wird direkt nach dessen Abschluss seriell übertragen. Die Aktivanzeige nennt das tatsächlich bestätigte Tempo; SDK-Worker-Antworten sind dafür an den exakten Frame gebunden.

Der OpenRGB-Gerätebestand wird höchstens einmal pro Minute rein lesend geprüft. Ein plötzlicher großer Abfall, zum Beispiel von sieben auf zwei Geräte während des Backend-Starts, ersetzt die vollständige Liste erst nach zwei verzögerten Bestätigungen. Unveränderte Hintergrundprüfungen bauen den Arbeitsbereich nicht neu auf und verändern weder Fokus noch Scrollposition.

## Modusfarben und sortierbarer Arbeitsbereich 3.4.15

Die OHC-Modi stehen als eigene Liste mit Beschreibung und Farbanforderung bereit. Rainbow erzeugt sein Spektrum selbst, Statisch und Atmen verwenden eine Farbe; die übrigen Muster verwenden zwei Farben. Jedes sichtbare Farbfeld unterstützt direkte Hex-Eingabe, Standardfarben und den Farbdialog.

Die Standardreihenfolge ist Engine → Geräte und Effekte → Thermaltake-360-PC-Ansicht → Gruppen. Jeder Hauptbereich besitzt rechts oben einen Ziehgriff sowie zugängliche Auf-/Ab-Schalter. OHC speichert die Reihenfolge und stellt sie auf Wunsch auf den Standard zurück. Gerätekacheln, Effekte und Gruppen bleiben intern fest geordnet und bestehende Profile unverändert kompatibel.

## Direkte Galerie und sichere Wiederübernahme 3.4.13

18 eigene prozedurale Presets erscheinen als laufende Kacheln. Ein Klick überträgt das gewählte Muster direkt; „Feste Farbe“ verwendet die Hauptfarbe und reagiert unmittelbar auf spätere Farbänderungen. Ein dauerhaftes Statusfeld und getrennte blaue beziehungsweise grüne Kachelrahmen zeigen die Auswahl und den lokal bestätigten Übertragungszustand.

„RGB-Steuerung neu übernehmen“ verwirft ausschließlich OHCs vorbereiteten SDK-Zustand, erkennt die Hardware neu und wendet die Auswahl erneut an. Die optionale automatische Wiederübernahme ist standardmäßig aus, beendet kein fremdes OpenRGB und wartet auf das sichere Ende des fremden Prozesses beziehungsweise SDK-Servers. Eine zuvor unbestätigte RGB-Freigabe wird nicht automatisch erteilt.

## Galerie, Profilstart und Kraken-Reihenfolge 3.4.12

17 eigene prozedurale Presets erscheinen als laufende Kacheln in sechs Kategorien. Die bisherige ComboBox bleibt intern für alte Profile erhalten. Ein Startprofil darf die RGB-Freigabe nur dann übernehmen, wenn `studio_autostart_enabled` ausdrücklich gespeichert wurde; fremdes OpenRGB und eine bereits belegte OHC-RGB-Sitzung blockieren weiterhin jeden Schreibzugriff. Die drei Kraken-Kanäle sind in der PC-Skizze nummeriert und lassen sich in die physische Reihenfolge ziehen.

## Dauerhafte Mehrgeräteframes und Einrichtungsassistent 3.4.11

Der frühere 100-ms-Round-Robin startete für jedes Direct-Gerät und jeden Animationsframe einen neuen Python-Prozess mit eigener SDK-Verbindung. Bei fünf Direct-Geräten erhielt dadurch jedes Gerät nur ungefähr zwei Updates pro Sekunde. Version 3.4.11 hält stattdessen einen isolierten Loopback-SDK-Worker und eine Verbindung offen, bereitet jedes Gerät einmal vor und überträgt alle ausgewählten Direct-Geräte in einem gemeinsamen 40-ms-Frame. Es bleibt immer genau ein Auftrag offen; veraltete Zwischenbilder werden zusammengefasst statt aufgestaut.

Die Oberfläche zeigt die tatsächlich abgeschlossene SDK-Rate je Gerät, letzte erfolgreiche Übertragung, Batch-Dauer und zusammengefasste Frames. Das ist weiterhin kein elektrischer Nachweis der sichtbaren LEDs. Ein sechsstufiger Assistent verbindet Besitzkonfliktprüfung, Umbenennen, Einzeltest, Zonen-/LED-Kalibrierung, Thermaltake-Aufbau und Sapphire-External-Control. Der Zonendialog kann jede Zone einzeln in der Testfarbe einschalten und die übrigen Zonen desselben Controllers schwarz setzen.

Bei Nicht-Direct-Geräten bevorzugt eine OHC-Animation automatisch den tatsächlich gemeldeten Modus `External Control`; auf dem Referenzsystem betrifft das die Sapphire RX 9070 XT. Statische Einzelaktionen und der GPU-/Hardwaremodus bleiben ausdrücklich bedienbar und seriell.

## Vollständige Geräteframes und Interstellar-V2-Profil 3.4.10

Nach realer Bestätigung der Zonengrößen zeigte sich, dass eine erfolgreiche SDK-Rücklesung noch keine sichtbare ARGB-Ausgabe garantiert. Version 3.4.10 überträgt deshalb statische Farben und jeden OHC-Animationsschritt immer als vollständigen `UPDATELEDS`-Geräteframe. Beim ersten Wechsel in Direct Mode werden vollständig abgebildete Zonen zusätzlich einmal über `UPDATEZONELEDS` geschrieben. Das deckt beide OpenRGB-Treiberpfade ab, ohne pro Frame doppelte USB-Arbeit zu erzeugen.

Der Zonendialog enthält Profile für TZMRIT/Jungle-Leopard Interstellar V2 Normal und Reverse mit jeweils 24 adressierbaren LEDs pro Lüfter. OHC multipliziert diesen Modellwert mit der in der PC-Ansicht einem Anschluss zugeordneten Lüfterzahl. Nicht zugeordnete Hub-Ports werden auf 0 vorbereitet; bekannte Nicht-Lüfter-Komponenten bleiben manuell. Ungewöhnlich hohe Werte erzeugen eine Bestätigung, weil ein ARGB-Datenanschluss die Anzahl verketteter LEDs nicht elektrisch melden kann.

Ein erfolgreicher SDK-Auftrag wird als bestätigter OpenRGB-Serverzustand dargestellt; die physisch sichtbare ARGB-Ausgabe bleibt ausdrücklich nicht rücklesbar. Konfigurationsfehler entfernen ein Gerät aus dem aktuellen Effekt, lösen aber keine Sicherheitssperre aus. Der Prozessbesitz prüft zusätzlich ckb-next neben OpenLinkHub und separaten OpenRGB-Prozessen.

## ARGB-Zoneneinrichtung 3.4.9

Die realen OpenRGB-SDK-Daten von MSI MYSTIC LIGHT und Airgoo AG-DRGB16 enthalten benannte Kanäle, aber null angelegte Farbplätze. Das ist kein gewöhnlicher Schreibfehler: Bei variablen ARGB-Anschlüssen muss zuerst festgelegt werden, wie viele LEDs hinter jedem Kanal verkettet sind.

Der neue Dialog „LED-Zonen und Lüfter einrichten“ liest für jede Zone aktuelle Größe, Mindestwert, Höchstwert und Änderbarkeit. Gespeichert werden `Lüfter/Geräte × LEDs je Gerät`; bekannte A1-/A2-Lüfterzahlen aus der Thermaltake-Ansicht erscheinen als Vorschlag. Weil der Controller die konkrete Lüfterbestückung elektrisch nicht erkennen kann, bleibt die modellabhängige LED-Zahl eine ausdrückliche Benutzereingabe.

OHC sendet anschließend den offiziell dokumentierten SDK-Befehl `RGBCONTROLLER_RESIZEZONE`, bestätigt die neue Zonengröße durch Rücklesung, aktiviert Direct Mode und schreibt die vollständigen Zonenfarben. Nicht eingerichtete Null-Zonen werden als Konfigurationshinweis aus einer Softwareanimation entfernt, jedoch nicht quarantänisiert. Die Größen gehören zu den lokalen Einstellungen und zu exportierten RGB-/Gesamtprofilen. Version 3.4.10 ergänzt darauf den vollständigen Geräteframe.

## Bestätigte Zonenwrites und Prozessbesitz 3.4.8

Der bisherige Direct-Helfer konnte unter SDK-Protokoll 4/5 nur feststellen, dass das Paket vollständig an den lokalen Server gesendet wurde. Das war kein Nachweis für den im Server aktiven Modus oder den übernommenen Farbpuffer. Version 3.4.8 fordert deshalb vor jedem Auftrag Geräteanzahl und vollständige Controllerdaten an, prüft den aktuell gemeldeten Direct Mode und verwendet die tatsächliche SDK-Farbpuffergröße.

Entspricht die Summe der gemeldeten Zonen dem Farbpuffer, schreibt OHC jede Zone mit `UPDATEZONELEDS`. Danach wird die Controllerbeschreibung erneut gelesen. Nur wenn aktiver Direct-/Custom-Modus und alle Farben dem Ziel entsprechen, erhält das Gerät den Status „OpenRGB-Zustand bestätigt“. Andernfalls wird es in der Mehrgeräteübersicht als konkreter Fehler geführt.

Eine separate OpenRGB-Oberfläche kann Hardware auch bei ausgeschaltetem SDK-Server besitzen. OHC durchsucht deshalb vor Engine-Start, Sitzungsfreigabe und RGB-Auftrag rein lesend `/proc`, schließt den eigenen verwalteten Kindprozess aus und blockiert bei jeder anderen OpenRGB-PID. Der fremde Prozess wird weder beendet noch verändert. OpenRGB muss weiterhin installiert sein, seine Oberfläche darf während OHCs RGB-Steuerung aber nicht zusätzlich laufen.

Bei gemeinsamer Auswahl aller drei NZXT-Kanäle nutzt OHC den im realen Hardwaretest bestätigten `sync`-Pfad. Eine Teil- oder Einzelkanalauswahl bleibt getrennt; topology-sensitive Effekte werden weiterhin pro physischem Kanal aufgebaut.

## SDK-, NZXT- und Prozesskorrekturen 3.4.7

OpenRGB `1.0~rc2` auf Fedora 44 antwortet auf die SDK-Versionsabfrage mit Revision 5. OHC fordert jetzt Revision 5 an, bleibt mit Revision 4 kompatibel und lehnt nur Server ab, die älter als die für den begrenzten Farbpfad benötigte Revision 4 sind. Der Server bleibt fest auf `127.0.0.1:6742`; die erlaubten Pakete und alle Größenlimits ändern sich nicht.

Der im Test für „Glut-Komet“ erzeugte NZXT-Modus `marquee-4` existiert beim verwendeten NZXT-2023-Treiber nicht. OHC entfernt diesen sowie den nicht bestätigten bewegten Alternating-Alias aus der Auswahlliste. Komet verwendet `pulse`, Kreisel `rainbow-flow`; seit 3.4.15 verwendet Abwechselnd den Zweifarben-Fallback `fading`.

Zusätzlich wird `application-instance.lock` im privaten XDG-State-Verzeichnis vor jeder Hardwareinitialisierung exklusiv mit `flock` gesperrt. Der Deskriptor wird nicht an Kindprozesse vererbt. Ein zweiter Programmstart zeigt nur einen Hinweis und endet; ein nicht erklärbarer Sperrfehler führt ebenfalls zu einem geschlossenen, hardwarefreien Startabbruch.

## Auswahl-, Modus- und Fehlerkorrekturen 3.4.6

Die aktive Auswahl wird nicht mehr in einer verkürzten Textzeile versteckt. Eine große Liste nennt jedes ausgewählte Gerät, seinen tatsächlichen Steuerweg und das letzte Ergebnis. Das durch OpenRGB zusätzlich gemeldete NZXT-Abbild entfällt aus den Kacheln, weil OHC denselben physischen Controller bereits über die drei sicheren `liquidctl`-Kanäle besitzt.

„Grafikkarte / Hardwaremodus“ gilt nur für Geräte ohne Direct Mode und nennt die betroffenen Geräte. Bei Frelidons System ist dies vor allem die Sapphire RX 9070 XT. Diese explizite Auswahl wird nicht mehr als automatische Vorgabe für OHC-Effekte benutzt; dadurch kann ein sichtbarer Off-/Dark-Modus die GPU-Beleuchtung nicht unbeabsichtigt beim Start eines anderen Effekts ausschalten.

Direct-Geräte erhalten `SETCUSTOMMODE` pro verwalteter Engine höchstens einmal. Gewöhnliche Einzelgerätefehler brechen eine serielle Mehrgeräteaktion nicht mehr ab; OHC führt die verbleibenden Befehle aus und zeigt anschließend eine gemeinsame Geräteliste mit Fehlerdetails. Bestätigte `ApplyOptions`-Abstürze bleiben weiterhin auf das verursachende Gerät quarantänisiert.

Der Scrollschutz umfasst nun Seite und Navigation nach Kachelumbau, Befehlsende und Dialogrückkehr. Automatische `session.log`- und `previous-session.log`-Dateien erhalten das bereinigte sichtbare Anwendungsprotokoll für spätere Diagnoseberichte.

## Direct-SDK, Scrollschutz und Layout-Editor 3.4.5

Der neue Fedora-Coredump zeigt den Absturz für den gültigen Einzelgerätebefehl an Airgoo AG-DRGB16 innerhalb von OpenRGBs `ApplyOptions`. Direct-Geräte werden daher bei statischer Farbe, Einzeltest und OHC-Softwareanimation nicht mehr durch den OpenRGB-Kommandozeilenparser geschickt. `src/openrgb_sdk.py` verhandelt stattdessen begrenzt Protokollversion 4 mit dem ausschließlich lokalen, von OHC verwalteten OpenRGB-Server und überträgt die fertigen LED-Farben. OpenRGB bleibt für Erkennung und sämtliche Controllerprotokolle zuständig und muss weiterhin installiert sein; seine Oberfläche muss nicht laufen.

Der Kachel-/Gruppen-Neuaufbau stellt die vorherige Scrollposition nach den Qt-Layoutläufen wieder her. Die PC-Ansicht beginnt geordnet mit zwölf Lüftern und unterstützt nun Hinzufügen, Bearbeiten, Entfernen und automatische Anordnung eigener Blöcke. Ein Hub mit nur einer gemeldeten logischen LED kann elektrisch gespiegelte Lüfter nur gemeinsam steuern; OHC zeigt diese Grenze an und erfindet keine Einzelkanäle.

## Reset-, Inventar- und Layout-Korrekturen 3.4.4

Ein reales Protokoll zeigte eine Neuerkennung, die noch während des vollständigen RGB-Resets lief. Der Reset beendete anschließend die verwaltete Engine, während die alte Oberfläche die zuvor erkannten Geräte weiterhin auswählbar darstellte. Deshalb wurden beim späteren Anwenden nur die drei direkt über `liquidctl` erreichbaren NZXT-Kanäle beschrieben. Version 3.4.4 invalidiert laufende Erkennungsaufträge, leert die OpenRGB-Geräteliste beim Reset und führt einen angeforderten Engine-Neustart erst nach tatsächlicher Prozessbeendigung aus. Eine bestätigte Schreibfreigabe bleibt bis zur neuen erfolgreichen Geräteliste vorgemerkt.

Die gemeldeten Indizes `0…6` und `7…13` waren ein vollständig gespiegeltes Inventar mit gleichem Gerätemuster. OHC entfernt die zweite Hälfte nur dann, wenn mindestens vier Gerätepaare und alle Inventarsignaturen exakt übereinstimmen. Zusätzlich können Einträge mit derselben belastbaren Seriennummer oder demselben vollständigen Hardwarepfad zusammengeführt werden. Zwei echte gleichnamige RAM-Riegel bleiben getrennt.

Der alte Positionsformularblock wurde durch eine große verschiebbare PC-Ansicht ersetzt. Frelidons Vorlage bildet den aktuellen Thermaltake-360-mm-Aufbau ab: Kraken 360 mit drei Lüftern oben, zwei normale Frontlüfter, drei Reverse-Intakes an Rückwand/Seite, drei Reverse-Intakes am Boden und ein Heck-Abluftlüfter; alle Lüfter sind als 120 mm dokumentiert. Blöcke lassen sich direkt ziehen, Gerätekacheln auf ihnen ablegen und per Doppelklick auswählen. Die geometrische Lage wird automatisch als Gehäusezone gespeichert; Anschlussnotizen sind weiterhin eine Benutzerzuordnung, keine elektrische Autoerkennung.

## Absturzisolierung 3.4.3

Vier reale Coredumps von Fedora 44 mit OpenRGB `1.0~rc2` zeigen, dass dessen CLI auch bei einem einzelnen gültigen `--device`-Block in `ApplyOptions` abbrechen kann. Betroffen waren ein statischer Ausschaltbefehl und Direct-Mode-Frames verschiedener Gerätenummern. OHC erkennt die charakteristische `stl_vector`-Assertion nun als Backend-Prozessabsturz und sperrt nur dieses Gerät bis zum nächsten Programmstart.

Serielle Befehlsfolgen laufen danach mit den übrigen Geräten weiter. Das ist insbesondere für den Testmodus wichtig, weil das gewählte Ziel absichtlich zuletzt eingeschaltet wird. Softwareanimationen führen getrennte Fehlerzähler je Gerät; der Erfolg eines anderen Controllers löscht dessen Fehlerstand nicht mehr. Ein bestätigter Prozessabsturz führt sofort zur Isolation, gewöhnliche Schreibfehler erst dreimal am selben Gerät.

## Start-Hotfix 3.4.2

Beim Aufbau der 3.4.1-Oberfläche konnte die erste RGB-Vorschau bereits während `build_ui()` angefordert werden, obwohl `rgb_preview_started` erst danach gesetzt wurde. Das reale Fedora-Protokoll bestätigte deshalb einen sofortigen `AttributeError`. Version 3.4.2 setzt die Vorschauuhr vor jedem UI-Aufbau und besitzt zusätzlich einen defensiven Fallback. Ein Regressionstest sichert genau diese Reihenfolge ab.

## Automatisch verwaltete RGB-Engine

Open Hardware Control startet den installierten OpenRGB-Treiber selbst als privaten, fensterlosen Kindprozess. Ein OpenRGB-Fenster oder manuell gestarteter SDK-Server ist nicht mehr notwendig. Der Treiberprozess wird beim vollständigen Beenden von OHC oder über „RGB komplett zurücksetzen“ beendet.

OpenRGB bleibt ein separat installiertes GPL-2.0-or-later-Hardwarebackend. OHC kopiert weder dessen Treiberquellcode noch Effekte des Effects Plugins. Das sichtbare RGB-Studio, die Gruppierung, Vorschau, Profile und zehn Softwareeffekte sind eigener GPL-3.0-or-later-Code.

Die Kommunikation bleibt fest auf `127.0.0.1:6742` beschränkt. OHC startet den Treiber mit privatem Konfigurationsverzeichnis, `--noautoconnect` und ohne sichtbare Oberfläche. Eine bereits fremd gestartete OpenRGB-Instanz wird angezeigt, aber für OHC-Schreibzugriffe gesperrt. Sie muss zuerst beendet werden; danach startet OHC seine eigene Engine.

## Gerätekacheln und Gruppen

Jedes steuerbare Gerät erscheint als quadratische Kachel. Mehrere Kacheln können gleichzeitig ausgewählt und per Drag & Drop in frei benennbare Gruppen verschoben werden. Mitgeliefert werden zunächst die Gruppen „Arbeitsspeicher“, „Lüfter“ und „Grafikkarte“; sie können umbenannt oder gelöscht werden.

Eine Gruppe kann ihr eigenes OHC-Design behalten. Wird danach eine andere Gruppe ausgewählt und ein anderer Effekt gestartet, bleibt die erste Gruppenkonfiguration bestehen. Gruppen, Gerätezuordnungen und Effekte werden in den Programmeinstellungen sowie in RGB-/Gesamtprofilen gespeichert. Importierte Profile starten aus Sicherheitsgründen keine Hardwareanimation automatisch.

Die drei Kanäle des NZXT 2023 RGB Controllers erscheinen neben den von OpenRGB gemeldeten Geräten. Dadurch lassen sich NZXT-Lüfter, Arbeitsspeicher, Grafikkarte und weitere Beleuchtung gemeinsam oder getrennt auswählen.

Version 3.4.1 bewahrt Auswahl und Gruppenzuordnung auch dann, wenn die RGB-Seite vor Abschluss der asynchronen Geräteerkennung aufgebaut wird. Eine neue Gruppe übernimmt die aktuell ausgewählten Kacheln direkt. „Alle schreibbereiten auswählen“ steht oberhalb und als großer Knopf unterhalb des Arbeitsbereichs zur Verfügung. Gleichnamige Geräte werden nummeriert und können über das Stiftsymbol dauerhaft benannt werden.

## Geräte-Testmodus

Der eigene Testbereich dient zur eindeutigen Zuordnung physischer Komponenten. Nach aktivierter Sitzungsschreibfreigabe schaltet OHC zuerst alle anderen von OHC steuerbaren Geräte seriell aus und aktiviert das gewählte Gerät zuletzt mit einer frei wählbaren Testfarbe. „Nächstes Gerät testen“ durchläuft nur exklusiv steuerbare Komponenten. „Test beenden“ schaltet alle von OHC steuerbaren Komponenten aus; die normale Gruppen- und Profilauswahl wird dabei nicht verändert. Das ausgewählte Gerät kann direkt im Testbereich dauerhaft umbenannt werden.

Durch OpenLinkHub belegte Geräte werden nicht verändert und im Status ausdrücklich genannt. Erkennt OHC eine fremd gestartete OpenRGB-Instanz, wird der vollständige Einzeltest blockiert, weil der Zustand aller übrigen OpenRGB-Geräte dann nicht sicher hergestellt werden kann.

## PC-Skizze und mitgeliefertes Profil

Die eigene schematische PC-Ansicht besitzt Positionen für Radiator/Oben, Front, Seite, Boden, Heck, Grafikkarte, Grafikkartenhalterung, Arbeitsspeicher und Pumpenkopf. Für jede Position werden Name, Anzahl, Anschlussnotiz, Gruppe und zugeordnete Gerätekacheln gespeichert. Die Grafik ist vollständig im Projekt gezeichnet und verwendet kein Herstellerbild.

Die Vorlage „Frelidon PC“ enthält:

- Kraken 360 oben mit drei NZXT-Kanälen `led1` bis `led3`;
- zwei Frontlüfter an A1;
- drei Reverse-Intake-Lüfter an Rückwand/Seite;
- drei Reverse-Intake-Lüfter auf der Netzteilabdeckung vorne an RGB-Hub B7 und PWM `SYS-FAN6`;
- einen getrennten Heck-Abluftlüfter;
- Sapphire RX 9070 XT als eigene Gruppe;
- Grafikkartenhalterung an B6 als getrennte Gruppe;
- zwei Arbeitsspeicherriegel.

Die automatische Zuordnung ist eine editierbare Startvorlage. Falls ein Hub zwei physische Komponenten mit demselben OpenRGB-Namen meldet, werden sie als „Gerät 1/2“ und „Gerät 2/2“ getrennt gehalten und können über die PC-Positionen eindeutig benannt werden.

## Stabiler OpenRGB-Ausgabepfad

Die Fedora-Protokolle mit OpenRGB `1.0~rc2` zeigen reproduzierbare Abstürze in `ApplyOptions`/`std::vector::operator[]` sogar bei einzelnen gültigen Geräten. Seit 3.4.5 umgehen Direct-Geräte diesen CLI-Pfad vollständig über den OHC-SDK-Helfer. Nicht-Direct-Geräte erhalten weiterhin nur einzeln und seriell einen tatsächlich gemeldeten nativen Modus.

Direct-Mode-Softwareanimationen verwenden eine globale Round-Robin-Obergrenze von zehn Einzelgeräteframes pro Sekunde. Geräte ohne Direct Mode blockieren die Auswahl nicht mehr: OHC wählt pro Gerät einen tatsächlich gemeldeten passenden Hardwaremodus. Für „Blitze“ wird beispielsweise `Random Flicker` bevorzugt, wenn das Gerät diesen Modus meldet.

## ENE-DRAM-Deduplizierung

Einige OpenRGB-Konfigurationen melden dieselben zwei RAM-Riegel zweimal, etwa als `ENE DRAM` 0/1 und `ENE DRAM DRAM` 6/7. OHC behandelt nur gleich große Namensvarianten derselben DRAM-Familie als Aliaspaare:

- `ENE DRAM` ×2 plus `ENE DRAM DRAM` ×2 wird zu zwei sichtbaren Riegeln;
- zwei Geräte mit exakt demselben Namen bleiben zwei Geräte;
- Seriennummer und Geräteort haben bei stabilen Gerätekennungen Vorrang;
- die längste gemeldete LED-Liste wird übernommen, damit alle LEDs des erhaltenen Riegels angesprochen werden.

## NZXT-Effekte

Alle Befehle werden gegen eine feste Effektdefinition validiert: zulässige Farbanzahl, Geschwindigkeit, Richtung und Kanal. Die Modi entsprechen den von `liquidctl` für den NZXT 2023 RGB Controller dokumentierten Hardwareeffekten.

„Flügel“ ist topology-sensitiv. Bei `sync` sendet OHC den Effekt deshalb getrennt an `led1`, `led2` und `led3`. Der Mittelpunkt der Animation liegt so wieder innerhalb jedes Lüfters und nicht zwischen mehreren als lange Kette behandelten Geräten. Nicht unterstützte Marquee-/Alternating-Aliasse werden nicht mehr angeboten; „Abwechselnd“ nutzt auf diesem Controller `fading`.

## Komplett-Zurücksetzen

Der große rote Knopf führt nach einer eigenen Bestätigung folgende Schritte aus:

1. alle OHC-Softwareanimationen und noch laufenden Frameprozesse stoppen;
2. für OpenRGB-Geräte ausschließlich einen tatsächlich gemeldeten Default-/Hardwaremodus verwenden;
3. den NZXT-Controller auf einen sicheren hardwareseitigen Spektrum-Modus stellen;
4. Auswahl und gespeicherte aktive Gruppeneffekte zurücksetzen;
5. Sitzungsfreigabe und OHC-Prozesssperre lösen;
6. die von OHC gestartete RGB-Engine beenden und Geräte freigeben.

Nicht jedes Mainboard stellt über OpenRGB einen expliziten „Hardware“-/„Default“-Modus bereit. In diesem Fall erfindet OHC keinen und führt keine ungeprüften SMBus-/I²C-Schreibzugriffe aus; es stoppt seine Befehle und gibt das Gerät frei. Der letzte Hardwarezustand kann dann bis zum nächsten Firmware-, Mainboard- oder Kaltstart erhalten bleiben.

## Sicherheitsgrenzen

- Schreibfreigabe gilt nur für die aktuelle Programmsitzung.
- Eine Prozesssperre verhindert zwei gleichzeitig schreibende OHC-Instanzen.
- Von OpenLinkHub belegte Corsair-Geräte und vom NZXT-Modul belegte NZXT-Geräte bleiben im OpenRGB-Pfad gesperrt.
- Softwareanimationen laufen nur auf Geräten mit gemeldetem `Direct` Mode; andere ausgewählte Geräte erhalten einen gemeldeten nativen Fallback.
- Höchstens ein OpenRGB-Einzelgeräteprozess und zehn Geräteframes pro Sekunde; keine Aufholwarteschlange.
- Maximal 64 Geräte pro Auftrag und 4096 LEDs pro Gerät; jedes Gerät wird in einer eigenen Transaktion geschrieben.
- Nach drei aufeinanderfolgenden Fehlern stoppt die Animation automatisch.

## Installation

Fehlt der Treiber, bietet OHC die Installation aus bereits konfigurierten Paketquellen an:

| Distribution | Pakete |
|---|---|
| Fedora / Nobara | `openrgb`, `openrgb-udev-rules` |
| Debian / Ubuntu / Mint | `openrgb` |
| Arch / Manjaro / EndeavourOS | `openrgb` |
| openSUSE | `openrgb` |

Nach der Installation genügt „RGB-Geräte neu erkennen“. Ein eigener Terminalbefehl zum Serverstart ist nicht mehr erforderlich.

Quellen: <https://gitlab.com/CalcProgrammer1/OpenRGB>, <https://openrgb.org/sdk.html>, <https://github.com/liquidctl/liquidctl/blob/main/docs/nzxt-hue2-guide.md>
