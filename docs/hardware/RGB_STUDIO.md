# RGB-Studio – Open Hardware Control

## Start, Wiederaufnahme und OpenRGB-Profilimport · nächste Version

Direkt unter dem Seitenkopf steht ein großer gemeinsamer Status für gewähltes
Startprofil, Profilautomatik, passive Wiederaufnahme und den aktuellen
RGB-Sitzungsbesitz. Nach der ersten ausdrücklichen Bestätigung, dass OHC die
RGB-Steuerung übernehmen darf, werden Profilautomatik und Wiederaufnahme als
Vorgabe eingeschaltet. Das ist keine dauerhafte Hardwarefreigabe: fremdes
OpenRGB, eine zweite OHC-Instanz und jede neue Sitzung durchlaufen weiterhin
die bestehenden Sperren und Bestätigungen.

Der Importmanager kopiert geprüfte `.orp`- beziehungsweise künftige
OpenRGB-v6-JSON-Profile in eine private OHC-Bibliothek. Binäre `.orp`-Dateien
enthalten undurchsichtige Controllerdatensätze; sie dürfen deshalb nur auf den
vollständigen gespeicherten Umfang angewendet werden. Eine scheinbare
Teilfilterung anhand geratenen Binärinhalts ist verboten. Für OHC-Designs
bleiben die vorhandenen Haken an Geräten und Lüftergruppen uneingeschränkt
wirksam.

## Räumliche Designgalerie · 3.4.29.125

Die doppelte große Live-Vorschau ist entfernt; die animierten Designkacheln
sind jetzt die Vorschau und zeigen Kategorie, Auswahl und aktiven Zustand.
Unter „Räumlich“ liegen sechs neue Vorlagen aus drei eigenen Algorithmen:
3D-Fusion bewegt zwei Lichtfronten von den gegenüberliegenden Seiten zur
Mitte, 3D-Kreuzstrom führt zwei Körper gegenläufig, und 3D-Tiefenwelle bewegt
gestaffelte Lichtflächen durch den gespeicherten Gehäuseraum.

Die Projektion nutzt ausschließlich ausdrücklich gespeicherte LED-Pfade und
Komponentenpositionen. Bei Ringen bleibt jeder Lüfter ein eigenes Segment;
LED 1, Lüfterreihenfolge, Drehsinn, Umkehrung und physische Einzelpixelnummer
bleiben maßgeblich. Ohne eindeutigen Pfad bleibt die bisherige lokale Animation
erhalten. Die neuen Designs ändern weder LED-Zahl noch Anschluss oder Besitzer.

## GPU-LED-Sichtassistent 3.4.29.118

Im Dialog „Grafikkarte: Steuerweg und LEDs“ startet „LED-Flüssigkeit abstimmen“
einen Vergleich am echten GPU-ARGB-Anschluss. Dafür müssen GPU und Halterung
bereits ausdrücklich verbunden, synchronisiert, ausgewählt und mit einem
OHC-Lauflicht oder Komet-Effekt aktiv sein. Während des Tests werden andere
ausgewählte OHC-LED-Zonen, geeignete native OpenRGB-Geräte und ausgewählte
NZXT-LED-Kanäle vorübergehend dunkel. Geräte außerhalb des OHC-Besitzes
werden nicht angefasst.

GPU und Halterung erscheinen für den Vergleich vorübergehend in Blau und
Weiß; die gespeicherten Designfarben bleiben erhalten. Jeder neue Wert läuft nach einem bestätigten Frame beider Controller
mindestens zehn Sekunden. „Noch ruckelig“ verringert das Tempo und verbreitert
die GPU-Lichtkanten in kleinen begrenzten Schritten; Helligkeit und Halterung
bleiben erhalten. „Flüssig · übernehmen“ speichert über den bestehenden
GPU-Dialog. Abbrechen setzt den Regler-Entwurf zurück. Beim Schließen wird
das vorherige Design für alle ausgewählten Geräte neu angefordert, solange
OHC die RGB-Engine noch besitzt. Bei Verbindungsverlust endet der Test und
der Grund steht im Log. SDK-Bestätigung beweist keine sichtbare LED-Ausgabe;
die Bewertung bleibt beim Nutzer.

Einzelpixel- und Lüfterzonen-Sichttests zeigen den gewählten Pixel oder die
gewählte Zone weiß und schalten andere ausgewählte OHC-LEDs vorübergehend
schwarz. Beim Schließen des Testdialogs kehrt das gewählte Design zurück,
sofern die RGB-Engine noch im Besitz von OHC ist.

## Zonenversuch entfernt 3.4.29.117

Das `.116`-Nutzerprotokoll zeigt zuerst funktionierende GPU-/Halterungs-
Effekte mit Geräteframes. Nach Einschalten beider Zonenversuche kamen
Zeitüberschreitungen und ein OpenRGB-Engine-Absturz. Ein vollständiger
OHC-Neustart stellte sechs Geräte und den Geräteframe wieder her. Die beiden
Schalter und der laufende Zonen-Schreibweg sind deshalb entfernt; gespeicherte
Versuchswerte werden ignoriert. Die bestätigten 30 GPU- und 12 Halterungs-
LEDs bleiben erhalten. Ob die GPU-Steifigkeit mit der LED-Zahl, dem
OpenRGB-Gerätetakt oder der Lichtkurve zusammenhängt, benötigt einen
getrennten Sichtvergleich. OpenRGB und OHC sollen dabei nicht gleichzeitig
dieselben RGB-Geräte schreiben.

## Sichere GPU-/Halterungs-Übertragungswahl 3.4.29.116

Nach dem `.115`-Test meldete das Nutzerprotokoll Zeitüberschreitungen und
ein unerwartetes Ende der verwalteten OpenRGB-Engine. Deshalb verwenden
Grafikkarte und Halterung wieder standardmäßig die vorherigen vollständigen
Geräteframes. Die `.115`-Teststellung wird ignoriert. Im GPU-Dialog können
MSI-GPU und Airgoo-Halterung ihre Zonenpakete getrennt und ausdrücklich
testen. Bei SDK-Fehlern oder Engine-Ende wird ein aktiver Test abgeschaltet;
ein Engine-Absturz bleibt bis zum manuellen Neustart gesperrt. Das Log nennt
Komponente, Schreibweg und Rückstellung. SDK-Antworten sind keine optische
Bestätigung. Die Gehäuseanimation bleibt rein lesend.

## MSI-GPU-Zonenweg und animiertes Gehäuse 3.4.29.115

Der Eigentümer sieht für Grafikkarte und Halterung jeweils etwa 24,5–25
erfolgreiche SDK-Frames pro Sekunde, aber die GPU bleibt optisch stufig.
Diese Zahl misst nur die Übergabe an OpenRGB, nicht den tatsächlichen
LED-Wechsel. Für die ausdrücklich auf MSI JARGB 1 gelegte GPU verwendet
OHC jetzt testweise die dokumentierten OpenRGB-Zonenpakete (SDK 1051)
statt des bisherigen Gesamtgerätepakets (1050). Die Option „GPU:
Zonenpakete testen“ im GPU-Dialog lässt sich abwählen und speichern.
Andere Zonen des MSI-Geräts werden vollständig mitgeschrieben; RAM und
Halterung behalten ihren bisherigen Weg. Das Log meldet `zones` oder
`device` als Schreibweg. Erst ein Sichtvergleich auf dem echten Anschluss
zeigt, welcher Weg besser aussieht.

Die Gehäusezeichnung animiert bei laufendem OHC-RGB-Effekt Grafikkarte,
Halterung und RAM mit den ausdrücklich konfigurierten LED-Zahlen. Wo noch
kein physischer Verlauf gespeichert ist, ist die Punktreihe nur eine
schematische Vorschau ohne Richtungsbehauptung. Sie schreibt keine LEDs.

## GPU-Lichtverlauf und Gehäusezugang 3.4.29.114

Das Video des Eigentümers zeigt an der externen GPU-Leiste eine stark
gesättigte weiße Fläche mit abrupt wirkenden Rändern, während die Halterung
weicher ausläuft. Der GPU-Dialog hat deshalb zusätzlich „Grafikkarte ·
Helligkeit“ für die weiße Spitze (35–100 %, Standard 65 %). Sehr schwache
GPU-Übergangsstufen werden früher sichtbar; die Halterung behält ihren
Verlauf. Bei laufendem OHC-Effekt verändern die Regler die echten LED-Frames
über denselben seriellen OpenRGB-Arbeiter. Abbrechen verwirft den Entwurf,
Speichern behält ihn. „Standard wiederherstellen“ setzt erst den Entwurf
zurück. Eine langsame oder stufige physische Controller-Ausgabe kann OHC
nicht aus der berechneten Vorschau ausschließen; die gemessenen SDK-Hz im
Dialog und der optische Nachtest bleiben wichtig.

Im Bereich Gehäuse öffnet „Grafikkarte: Steuerweg und LEDs“ denselben
GPU-Dialog. „LED-Anzahl am ARGB-Anschluss ändern“ führt bei genau einem
erkannten zugeordneten Anschluss direkt in dessen LED-Editor;
„ARGB-Anschluss ändern“ öffnet weiterhin die gesonderte Zuordnung.
Gehäuse-/ARGB-Editoren benennen den bearbeiteten Block. Nur tatsächlich
gespeicherte eindeutige LED-Wege erscheinen als Start-, End- und Wegpunkte
auf dem Block der Gehäusezeichnung. Für noch nicht konfigurierte Wege
wird keine Richtung behauptet.

## Gemeinsamer GPU-/Halterungs-Takt 3.4.29.113

Der GPU-Standard für die Lichtkante ist jetzt 40 % Vorlauf und 38 % Auslauf;
die Halterung behält 32 % / 36 %. Bereits gespeicherte Einstellungen bleiben
erhalten. Beide Reihen nutzen denselben festen Streifenzyklus, auch wenn
Vorlauf und Auslauf unterschiedlich sind. So verschiebt ein Regler an der GPU
nicht mehr die Phase der Halterung. Die sichtbare Wirkung muss nach der
Installation an den echten LED-Streifen verglichen werden.

## GPU-/Halterungs-Lichtverlauf 3.4.29.112

Unter „Grafikkarte → Steuerweg und LEDs“ zeigen zwei animierte Reihen die
gespeicherte Anzahl der Grafikkarten- und Halterungs-LEDs. Vorlauf und Auslauf
sind für beide Reihen getrennt einstellbar, das Tempo bleibt gemeinsam. Erst „Steuerweg
speichern“ übernimmt diese Werte; „Abbrechen“ lässt die bisherige Animation.
Die tatsächliche LED-Anzahl wird weiterhin im jeweiligen ARGB-Anschlusseditor
mit dem Einzelpixeltest festgelegt. Die Dialogzeile „Gemessene Bildrate“ zeigt
bestätigte SDK-Übertragungen für beide Controller. Nach einem langsamen Batch
bewegt sich der gemeinsame Lichtkopf pro gesendetem Frame nur begrenzt weiter.
Die Software kann die sichtbare Reaktion der Hardware nicht zurücklesen.

## GPU und Halterung 3.4.29.89

Unter „Grafikkarte → Steuerung und LEDs“ lässt sich „GPU und Halterung
synchronisieren“ abschalten oder einschalten. Die Funktion ist vorbelegt,
wirkt aber nur bei einer ausdrücklich im Gehäuse zugeordneten GPU-Halterung
und einer eindeutig zugeordneten externen GPU-Direct-Zone. Beide Geräte müssen
ausgewählt und konfliktfrei sein, beide Anschlusszahlen gültig eingestellt.
Keine automatische Anschlussvermutung oder Auswahl zusätzlicher Geräte.

GPU (30 LEDs) und Halterung (12 LEDs) teilen sich dann den GPU-Effekt und
Zeitverlauf; jede Zone behält ihre echte LED-Anzahl und physische Testnummern.
Start-/Endrichtung bleibt konfigurierbar. Ringverläufe bleiben unverändert.
Neon-Kreisel und Lichtspuren werden an offenen Streifen zeitlich/räumlich weich
abgetastet, langsamer bewegt und an den Enden ausgeblendet. Andere Anschlüsse
und native GPU-Modi bleiben unverändert. Der bestehende einzelne SDK-Arbeiter
bleibt bei nominal 25 Hz; reale USB-/Firmware-Verzögerungen sind nicht damit
behoben oder optisch rückgelesen. ARGB-DIAG ergänzt den Strip-Bewegungsplan.
Das Komplettpaket enthält auch die Synchronisationseinstellung.

## Physischer LED-Verlauf 3.4.29.88

Im Anschlusseditor neben „LEDs“ den Reiter „LED-Verlauf“ öffnen und aktivieren.
Bei Streifen „LED 1 beginnt“ und „Letzte LED endet“ auswählen, zum Beispiel
oben/unten oder links/rechts. Bei Lüfterringen Ringzahl, Startpunkt pro Ring
und Drehsinn festlegen; alle Ringe müssen gleich viele LEDs haben. Die Vorschau
berücksichtigt zusätzlich die „Lüfterreihenfolge“: LED 1 kann am oberen/linken
oder am unteren/rechten Lüfter beginnen, unabhängig vom Drehsinn jedes Rings.
Bestehende Verläufe bleiben oben/links zuerst. Das Komplettpaket speichert auch
diese Auswahl; Anschlusszahl und physische Testnummerierung ändern sich nicht.
Die Vorschau
zeigt erste, letzte und aktuell getestete LED. Der Sichttest bleibt immer auf
der echten physischen 1-basierten LED-Nummer, unabhängig von der Effektrichtung.

„Laufrichtung im Gehäuse“ gilt gemeinsam für räumlich konfigurierte Anschlüsse:
vertikal, horizontal oder vier Diagonalen. Vorhandene eindeutig zugeordnete
Gehäuseblöcke liefern Position und Lüfterreihe. Mehrdeutige gemeinsame Header
verwenden lokale Blockkoordinaten, keine erfundene getrennte Verkabelung.
„Wie bisher (pro Anschluss)“ und Anschlüsse ohne Verlauf behalten die bisherigen
Frames. Ungültig gewordene Ringzahlen fallen lokal zurück. Startpunkte bleiben
von Designs unabhängig gespeichert; keine zusätzliche Transportverbindung und
keine garantierte optische FPS. Das [Komplettpaket](PROFILES.md) sichert alles.

## Bestätigte persönliche Verkabelung 3.4.29.87

RGB Studio 1.10 übernimmt im persönlichen Thermalright-Profil einmalig:
Front/SYS_FAN4 A1 2×8 LEDs, Boden/SYS_FAN6 B7 3×8, Heck/SYS_FAN1 B8 1×8,
Radiator A8 3×10 und GPU-Halterung B6 12 LEDs. B6 ersetzt die ältere
24-LED-Referenz; spätere manuelle Änderungen werden nicht mehr regelmäßig
zurückgesetzt. Nur eindeutig gemeldete AG-DRGB16-Anschlüsse werden gebunden;
vollständige gespeicherte Zonen bleiben unabhängig von Designs geschützt.
Positionen, PWM-Zuordnung und nicht genannte Anschlüsse bleiben erhalten.

Im Lüfter-Blockeditor speichert „Modell speichern“ eigene Hersteller, Modelle,
Farbe und LEDs je Lüfter zur Wiederverwendung auch im Zoneneditor. Thermalright
mit zehn LEDs ist die bestätigte persönliche Radiatorreferenz, keine universelle
Hardwareerkennung. Speichern oder Übernahme aktiviert keine Hardwaresteuerung.
Diese Verbesserungen gehen in die lokale .87-Paketierung ein; keine Installation
oder elektrische/optische Prüfung wird dadurch automatisch durchgeführt.

## Gehäuse, Anschlussdiagnose und weiche Effekte 3.4.29.83

Die neue Seite „Gehäuse“ steht nach „Übersicht“. Komponenten, RGB-Anschlüsse,
manuelle LED-Anzahl und vorhandene Gehäuselüfter-PWM-Zuordnung werden einmal
eingestellt und in RGB/Kühlung gemeinsam gezeigt. Blockeditoren enthalten
LED-/PWM-Knöpfe; die Anschluss-/Gesamtspalten öffnen per Doppelklick den
Anschlusseditor. Die Gesamtzahl ist eine Deklaration, keine Messung.
Der Synchronisierungsschalter koppelt Positionen; deaktiviert speichert
Kühlung eigene Positionen, niemals eine zweite widersprüchliche Verkabelung.
Zuordnen aktiviert/kalibriert/regelt keinen Kanal. CPU-/Pumpenkanäle bleiben
außerhalb der Gehäuselüfter-Zuordnung.

Jede gemeldete Direct-ARGB-Zone besitzt denselben begrenzten Einzel-LED-Test,
auch JARGB 2/3 und Controllerports. Andere gespeicherte Anschlüsse bleiben
unverändert. Explizit manuelle Werte überleben auch Designprofilwechsel.
Der Besitzer bestätigte am 13.09.26 die persönliche Sapphire RX 9070 XT
NITRO+ mit 30 einzeln adressierbaren LEDs an MSI JARGB 1: Index 1 links,
30 rechts, 29 eine Position zurück. Kein pauschaler GPU-Standardwert.

Alle eingerichteten Zonen verwenden eigene Koordinaten. Pixel-Flächenabtastung
bleibt begrenzt auf vier Samples bis 128 LEDs, zwei bis 512, danach eines.
Neonkreisel/Komet besitzen weiche führende Kanten und Mehrpixel-Spuren; sehr
kurze Streifen bewegen sich langsamer. Wellen/Regenbogen werden flächenweise
gemittelt, Wechselmuster/Funkeln/Pulsfarben weich überblendet. Statisch/Atmen
bleiben kontinuierlich, Blitz behält absichtliche Blitze. Kein Effekt erhöht
den vorhandenen 25-Hz-Transport-Sollwert oder garantiert physische FPS.

Die volle „Übertragung“-Karte zeigt abgeschlossene SDK-Aufträge, Batchdauer
und zusammengefasste Frames. `ARGB-DIAG` protokolliert bei Einrichtung,
Speichern und Test: Serverpuffer versus deklarierte Anzahl, Grenzen,
Zonenoffset, 1-basierten Pixel und SDK-Abschluss. Effektstart nennt Abtastplan
und Sollrate; kein Log pro Frame. SDK-Erfolg ist kein optischer Rücklesebeweis.

PC-Gehäuseprofile 1.1 zeichnet 30 detailliertere originale Vektoransichten.
Retro/North wurden anhand offizieller Produktansichten überprüft; andere
Modellansichten bleiben eigene schematische Illustrationen, keine maßgenaue
Hersteller-CAD-Nachzeichnung. Referenzen: [Thermaltake Retro](https://thermaltakeusa.com/products/retro-360-tg-mid-tower-chassis-ca-11q-00mqwn-00),
[Fractal North](https://www.fractal-design.com/products/cases/north-series/north/north-chalk-white/).
`tools/render_case_workspace.py /tmp/ohc-case-render` rendert alle Vorlagen
hardwarefrei. Herstellerbilder werden nicht mitgeliefert.

## GPU-RGB ohne ARGB-Kabel · Stand 19.09.26

Der OpenRGB-SDK-Pfad in OHC ist herstellerneutral: Jede von OpenRGB als GPU
gemeldete Grafikkarte erscheint nun zusätzlich im GPU-Reiter und kann direkt
zur vorhandenen RGB-Studio-Einrichtung geöffnet werden. OpenRGB unterstützt
beispielsweise MSI-GPU-Controller über I²C und ASUS-Aura-/ENE-GPU-Controller
über SMBus. Das braucht kein 5-V-ARGB-Kabel zum Mainboard. Entscheidend sind
die konkrete PCI-/Subgeräte-ID, Linux-Zugriff und die von OpenRGB tatsächlich
gemeldeten Modi/Zonen. Eine Herstellerreihe allein ist keine Zusage für jede
Karte. OHC führt keine eigenen unbekannten I²C-Befehle aus.

Im GPU-Reiter markiert `Direct` einen vom Controller gemeldeten direkten
Farbweg. Andernfalls bleiben die von OpenRGB gemeldeten nativen Hardwaremodi
verfügbar. Nur eine ausdrücklich an einen Mainboard-ARGB-Anschluss verkabelte
Karte verwendet die manuelle LED-Zahl und den Pixeltest dieses Anschlusses;
ein einzelner logischer OpenRGB-LED-Eintrag beweist keine physische Strip-Länge.
LACT übernimmt GPU-Leistung und optional GPU-Lüfter, OpenRGB die Beleuchtung;
die beiden Zuständigkeiten sind getrennt. OpenRGB 1.0 meldet SDK 6, während
OHC für die Kompatibilität weiter Protokoll 5 aushandelt; der lokale
Protokoll-6-Servertest ist Teil der Releaseprüfung.

Quellen: [OpenRGB GPU-Controller-Dokumentation](https://gitlab.com/OpenRGBDevelopers/OpenRGB-Wiki/-/blob/becf03f35c86c2b2cf260eb86bcb1381c1a521f3/Supported%20Devices/Supported%20Devices.md), [ASUS-Detektor](https://github.com/CalcProgrammer1/OpenRGB/blob/master/Controllers/ENESMBusController/ENESMBusControllerDetect.cpp), [SDK-Spezifikation](https://github.com/CalcProgrammer1/OpenRGB/blob/master/Documentation/OpenRGBSDK.md).

## GPU-ARGB-Anschluss 3.4.29.82

„Grafikkarte: Steuerweg und LEDs“ wählt den realen Direct-Controller und eine
gemeldete Zone, beim bestätigten persönlichen Aufbau MSI → JARGB 1. Der
Anschlusseditor speichert eine Grafikkarte als ein Gerät mit manueller LED-Zahl.
Die physische Länge kann OHC nicht elektrisch erkennen; 80/90 sind Testwerte.
„Eine LED testen“ überträgt nur den gewählten Index ab 1 und schaltet andere
Zonen dieses Controllers vorübergehend schwarz. Danach das Design anwenden.
Der GPU-Effekt verwendet seine eigene Strip-Länge statt der Summe aller
Controllerzonen; andere Zonen behalten unabhängige Längen und Controller-Effekt.
Aktuelle GPU-Verkabelung und LED-Zahl haben Vorrang vor alten Designprofilen.
Nur die persönliche Ansicht erhält die vom Besitzer bestätigte JARGB-1-Migration.
Unbekannte oder mehrdeutige Geräte werden nicht automatisch zugeordnet.

## Kompakte Bibliothek und PC-Gehäuseprofile 3.4.29.62

RGB-Studio 1.2 zeigt beim Öffnen vier Vorschläge und ergänzt Nebula Pulse,
Liquid Metal, Ember Flow und Arctic Halo. Ein Stern speichert Favoriten; bis zu
vier erscheinen in der Favoritenansicht. „Alle Designs“ öffnet die vollständige
kategorisierte Bibliothek. Geräte/Gruppen und die tiefen Effektregler starten
eingeklappt, bleiben aber vollständig in derselben Seite erreichbar.

PC-Gehäuseprofile 1.0 enthält 30 originale OHC-Schemazeichnungen. Ein
Doppelklick auf einen Komponentenblock öffnet das zugeordnete RGB-Gerät; bei
Direct-Geräten folgt unmittelbar die Zonen-/LED-Einrichtung. Meldet ein Gerät
wie die Referenz-Sapphire nur einen Hardwaremodus und eine logische LED, zeigt
OHC diese Backend-Grenze und öffnet die GPU-Steuerweg-Einrichtung, ohne LEDs zu erfinden. Das
Thermaltake Retro 360 TG ist mit den offiziellen Herstellerdaten die exakte
Standardvorlage. Der Programmknopf öffnet ausschließlich die Herstellerquelle
des gewählten Modells; der persönliche Amazon-Kauflink ist nicht Teil der UI.
Die zweispaltige Ansicht unterscheidet eigene Retro-, Lamellen-, Panorama-,
Zweikammer-, Kompakt- und klassische Silhouetten, ohne Herstellerbilder zu
übernehmen. AIO-/Luftkühlung ist umschaltbar. Ein markierter Lüfterblock kann
seinen Luftstrom umkehren oder in einzeln verschiebbare Lüfter geteilt werden.
Eigene PC-Profile speichern diese Ansicht lokal; das Anwenden schreibt keine
Hardwarefarbe. Startpositionen bleiben anpassbare Montagevorschläge und müssen
mit dem realen Aufbau geprüft werden.

## Tempoübernahme und automatische Inventarnachprüfung 3.4.16

Änderungen an Tempo, Farbe, Helligkeit und Richtung werden kurz zusammengefasst. Läuft noch ein NZXT-/GPU-Auftrag, bleibt nur der neueste Stand vorgemerkt und wird direkt nach dessen Abschluss seriell übertragen. Die Aktivanzeige nennt das tatsächlich bestätigte Tempo; SDK-Worker-Antworten sind dafür an den exakten Frame gebunden.

Der OpenRGB-Gerätebestand wird höchstens einmal pro Minute rein lesend geprüft. Ein plötzlicher großer Abfall, zum Beispiel von sieben auf zwei Geräte während des Backend-Starts, ersetzt die vollständige Liste erst nach zwei verzögerten Bestätigungen. Unveränderte Hintergrundprüfungen bauen den Arbeitsbereich nicht neu auf und verändern weder Fokus noch Scrollposition.

## Modusfarben und sortierbarer Arbeitsbereich 3.4.15

Die OHC-Modi stehen als eigene Liste mit Beschreibung und Farbanforderung bereit. Rainbow erzeugt sein Spektrum selbst, Statisch und Atmen verwenden eine Farbe; die übrigen Muster verwenden zwei Farben. Jedes sichtbare Farbfeld unterstützt direkte Hex-Eingabe, Standardfarben und den Farbdialog.

Die Standardreihenfolge ist Engine → Geräte und Effekte → Thermaltake-360-PC-Ansicht → Gruppen. Jeder Hauptbereich besitzt rechts oben einen Ziehgriff sowie zugängliche Auf-/Ab-Schalter. Unter der Designgalerie klappt „Geräte und Effekte“ Auswahl, Modi, Native-Kanäle und Vorschau in der Seite auf; die native Ergebnisliste ist ein zweites eingebettetes Untermenü und kein Extra-Fenster. OHC speichert die Reihenfolge und stellt sie auf Wunsch auf den Standard zurück. Gerätekacheln, Effekte und Gruppen bleiben intern fest geordnet und bestehende Profile unverändert kompatibel.

## Direkte Galerie und sichere Wiederübernahme 3.4.13

18 eigene prozedurale Presets erscheinen als laufende Kacheln. Ein Klick überträgt das gewählte Muster direkt; „Feste Farbe“ verwendet die Hauptfarbe und reagiert unmittelbar auf spätere Farbänderungen. Ein dauerhaftes Statusfeld und getrennte blaue beziehungsweise grüne Kachelrahmen zeigen die Auswahl und den lokal bestätigten Übertragungszustand.

„RGB-Steuerung neu übernehmen“ verwirft ausschließlich OHCs vorbereiteten SDK-Zustand, erkennt die Hardware neu und wendet die Auswahl erneut an. Die optionale automatische Wiederübernahme ist standardmäßig aus, beendet kein fremdes OpenRGB und wartet auf das sichere Ende des fremden Prozesses beziehungsweise SDK-Servers. Eine zuvor unbestätigte RGB-Freigabe wird nicht automatisch erteilt.

## Galerie, Profilstart und Kraken-Reihenfolge 3.4.12

17 eigene prozedurale Presets erscheinen als laufende Kacheln in sechs Kategorien. Die bisherige ComboBox bleibt intern für alte Profile erhalten. Ein Startprofil darf die RGB-Freigabe nur dann übernehmen, wenn `studio_autostart_enabled` ausdrücklich gespeichert wurde; fremdes OpenRGB und eine bereits belegte OHC-RGB-Sitzung blockieren weiterhin jeden Schreibzugriff. Die drei Kraken-Kanäle sind in der PC-Skizze nummeriert und lassen sich in die physische Reihenfolge ziehen.

## Dauerhafte Mehrgeräteframes und Einrichtungsassistent 3.4.11

Der frühere 100-ms-Round-Robin startete für jedes Direct-Gerät und jeden Animationsframe einen neuen Python-Prozess mit eigener SDK-Verbindung. Bei fünf Direct-Geräten erhielt dadurch jedes Gerät nur ungefähr zwei Updates pro Sekunde. Version 3.4.11 hält stattdessen einen isolierten Loopback-SDK-Worker und eine Verbindung offen, bereitet jedes Gerät einmal vor und überträgt alle ausgewählten Direct-Geräte in einem gemeinsamen 40-ms-Frame. Es bleibt immer genau ein Auftrag offen; veraltete Zwischenbilder werden zusammengefasst statt aufgestaut.

Die Oberfläche zeigt die tatsächlich abgeschlossene SDK-Rate je Gerät, letzte erfolgreiche Übertragung, Batch-Dauer und zusammengefasste Frames. Das ist weiterhin kein elektrischer Nachweis der sichtbaren LEDs. Ein sechsstufiger Assistent verbindet Besitzkonfliktprüfung, Umbenennen, Einzeltest, Zonen-/LED-Kalibrierung, Thermaltake-Aufbau und Sapphire-External-Control. Der Zonendialog kann jede Zone einzeln in der Testfarbe einschalten und die übrigen Zonen desselben Controllers schwarz setzen.

Seit 3.4.29.82 nutzt eine OHC-Animation bei Nicht-Direct-Geräten passende gemeldete native Animationen statt automatisch `External Control`. Auf der Sapphire RX 9070 XT werden beispielsweise Rainbow Wave, Runway, Serial und Spectrum Cycle genutzt. Statische Einzelaktionen und der GPU-/Hardwaremodus bleiben ausdrücklich bedienbar und seriell.

„Grafikkarte: Steuerweg und LEDs“ ist auch per GPU-Komponenten-Doppelklick erreichbar. Native Effekte sind der Standard für bestehende persönliche Profile. Nur bei bestätigter 5-V-ARGB-Verkabelung wird ein externer Direct-Controller ausdrücklich zugeordnet; dort öffnet „LED-Anzahl am ARGB-Anschluss ändern“ den vorhandenen Zonen-Editor. Wähle darin den tatsächlich angeschlossenen Kanal und seine reale LED-Zahl innerhalb der Backend-Grenzen. OHC speichert Steuerweg und Zonen in Einstellungen und RGB-Profilen; ein neues/aktualisiertes Profil übernimmt diese Einrichtung. Controller-Designs betreffen auch dessen übrige Zonen. Ohne ausgewählte Quelle verwendet OHC native GPU-Effekte.

Die interne Zone bleibt eine logische LED: [OpenRGBs Sapphire-V3-Implementierung](https://gitlab.com/CalcProgrammer1/OpenRGB/-/raw/master/Controllers/SapphireGPUController/SapphireNitroGlowV3Controller/RGBController_SapphireNitroGlowV3.cpp) begrenzt sie auf eins. Das ist nicht die physische Strip-Länge. [Sapphire](https://www.sapphiretech.com/en/consumer/nitro-radeon-rx-9070-xt-16g-gddr6) beschreibt die externe Synchronisierung über das mitgelieferte 3-Pin-5-V-ARGB-Kabel. Ohne diesen Weg kann eine erfundene GPU-LED-Zahl keine OHC-Einzelpixel-Effekte freischalten.

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

Die offizielle OpenRGB-Version `1.0-rc3.1` vom 23.08.2026 veröffentlicht weiterhin SDK-Protokoll 5. OHCs begrenzter Protokoll-4/5-Parser und der Loopback-Zwang bleiben deshalb kompatibel. Da auf dem Referenzsystem weiterhin das Fedora-Paket `1.0~rc2` läuft, ist dies eine Quell-/Protokollprüfung und keine neue reale Gerätebestätigung.

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
