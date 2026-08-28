# Open Hardware Control by Frelidon 3.4.28 INTERN

<!-- project-badges -->
[![CI](https://github.com/Frelidon/open-hardware-control/actions/workflows/ci.yml/badge.svg)](https://github.com/Frelidon/open-hardware-control/actions/workflows/ci.yml) [![License: GPL-3.0-or-later](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](LICENSE) [![Release](https://img.shields.io/github/v/release/Frelidon/open-hardware-control?display_name=tag)](https://github.com/Frelidon/open-hardware-control/releases)
<!-- /project-badges -->

Open Hardware Control ist eine freie Linux-Oberfläche für **NZXT-Kraken-LCD**, Pumpe, Radiatorlüfter und RGB, für **kalibrierte Mainboard-/Gehäuselüfter über Linux hwmon/NCT6687**, für **Corsair-Geräte über OpenLinkHub** sowie für zusätzliche RGB-Geräte über eine von OHC automatisch verwaltete lokale Hardware-Engine. Das Projekt richtet sich an Fedora, Nobara, Debian, Ubuntu, Linux Mint, Arch Linux, Manjaro, EndeavourOS und openSUSE.

![Open Hardware Control – Übersicht](docs/images/screenshots/01-dashboard-overview.png)

<!-- project-repository -->
Projekt-Repository: <https://github.com/Frelidon/open-hardware-control>
<!-- /project-repository -->

> **Inoffizielles unabhängiges Community-Projekt:** Bisher besteht keine offizielle Unterstützung, Kooperation, Freigabe oder Verbindung zu NZXT, Corsair, be quiet!, OpenLinkHub, OpenRGB oder anderen genannten Herstellern und Projekten. Produkt- und Markennamen dienen nur der Kompatibilitätsbeschreibung. Hersteller und Rechteinhaber erreichen Frelidon über die öffentliche Kontaktadresse im GitHub-Profil oder über den Steam-Benutzernamen **Frelidon**.

Version 3.4.28 INTERN verbindet die verständlichere CoolerControl-Verwaltung mit einem einheitlichen blau getönten Kartendesign und ehrlicher Kraken-Profilanzeige. OHC unterscheidet das geschlossene Programmfenster vom weiterlaufenden `coolercontrold`-Hintergrunddienst und markiert ein Kraken-Schnellprofil erst nach erfolgreicher Hardwareübertragung.

## Neu in 3.4.28 INTERN

- Gehäuselüfterkarten bleiben zunächst kompakt, öffnen nur die ausdrücklich gewählte Kurve und lassen sich über dieselbe Aktion wieder schließen.
- Die weiter aufgeteilte Modulstruktur und `MODULE_MAP.md` reduzieren den Kontextbedarf lokaler Coding-KIs.
- Getrennte Anzeige von laufendem CoolerControl-Hintergrunddienst und aktiviertem Systemstart.
- Bestätigte Polkit-Aktionen für vorübergehende OHC-Übernahme, dauerhaftes Deaktivieren sowie erneutes Aktivieren und Starten von CoolerControl.
- Sichere Übergabe: OHC startet seine Lüfterregelung beim Deaktivieren nicht ungefragt; vor dem Aktivieren von CoolerControl gehen Mainboard-Kanäle an Firmware/BIOS zurück.
- Einheitliches blau getöntes Design für RGB-Studio, LCD, Profile, Log, Corsair/OpenLinkHub, Einstellungen, Über, Hilfe und Kraken-Details.
- Leise, Ausbalanciert und Leistung werden erst nach erfolgreicher Pumpen- und Lüfterübertragung vollständig blau markiert.
- Vollständige lokale-KI-Übergabe für LM Studio/Qwen2.5-Coder mit Startprompt, Projektregeln und abgesichertem GitHub-Ablauf.

## Neu in 3.4.26 INTERN

- Dauerhaftes KI-Projektgedächtnis über `AGENTS.md`, Status-, Architektur-, Entscheidungs- und Geräteunterlagen.
- Cursor-Projektregeln, Slash-Kommandos und Session-Start-Hook für zuverlässige Übergaben zwischen neuen Chats.
- Release-Prüfungen für Version, Kanal, Tests, Datenschutz und reproduzierbare Artefakte ohne externe Backup-Abhängigkeit.
- Destruktive Shell-/Git-Befehle benötigen in Cursor eine ausdrückliche Bestätigung.

## Neu in 3.4.25 INTERN

- neues kompaktes Dark-Dashboard mit permanenter OHC-Seitenleiste und klaren Seitentiteln
- „Community Edition“ wird nicht verwendet; Open Hardware Control bleibt eine einheitliche Open-Source-Anwendung
- Übersicht mit kompakten Hardwarekarten, Schnellaktionen, Hardwareliste und Status-/Hinweisbereich
- Kühlungszentrale mit getrennten Karten für CPU/Kraken und Gehäuselüfter
- System-Fan-Karten mit direkten Aktionen **Testen**, **Kurve** und **Zuordnen**
- eigener Lüfterkurven-Dialog statt weit entfernter Editor-Sektion
- CoolerControl-Ownership-Hinweis direkt unter der Kühlungsübersicht
- Lüfter-Zuordnungsassistent mit vier Schritten: Erkennen, Testen, Zuordnen, Speichern
- standardmäßig dunkles Design bei neuen Installationen; bestehende explizite Design-Einstellung bleibt erhalten
- zusätzlicher echter PySide6-Offscreen-GUI-Smoke-Test im internen Releaseprozess

Version 3.4.23.2 INTERN räumt die Kühlungsseite grundlegend auf: CPU/Kraken und Gehäuselüfter erscheinen als kompakte Dashboard-Karten mit aufklappbaren Details. System-Fan-Kanäle werden als einzelne Karten mit RPM/PWM, Profil, Sensorquelle und Kurvenvorschau angezeigt; CPU_FAN und PUMP_FAN bleiben im separaten Kraken-Bereich. CoolerControl wird als konkurrierender Besitzer erkannt und blockiert parallele PWM-Schreibzugriffe. Ein neuer Gehäuselüfter-Assistent verbindet sicheren PWM-Kontrasttest, optionale weiße RGB-Testbeleuchtung und die gemeinsame RGB-/PWM-Gehäusezuordnung.

Version 3.4.23.1 INTERN ergänzt die Mainboard-Lüftersteuerung um einen eng begrenzten Polkit-Helfer für root-geschützte NCT6687-hwmon-Schreibzugriffe. Die Oberfläche bleibt unprivilegiert. Die sichere Kanal-Kalibrierung läuft jetzt zehn Sekunden, beobachtet den RPM-Verlauf und berücksichtigt den verzögerten MSI-EC-Readback.

Version 3.4.23 INTERN erweitert Open Hardware Control um eine sichere Mainboard-Lüftersteuerung über Linux-hwmon/NCT6687. PWM-Kanäle werden nie blind zugeordnet: Jeder Kanal muss zuerst kurz getestet und physisch bestätigt werden. Danach können pro Kanal eigene Sensorquellen, Kurven, Mindestwerte, Hysterese und Reaktionsverzögerungen genutzt werden. Zusätzlich zeigt das RGB-Studio ENE-DRAM mit zusätzlicher Startinitialisierung sichtbar an und bietet einen manuellen Reinitialisierungs-Button.

## Neu in 3.4.23.2 INTERN

- Kompaktes Kühlungs-Dashboard: CPU/Kraken und Gehäuselüfter als zwei übersichtliche Detailkarten statt einer langen Folge großer Bereiche.
- CPU_FAN/PUMP_FAN werden aus der Mainboard-Gehäuselüftersteuerung ausgefiltert; Pumpe und Radiatorlüfter bleiben vollständig in der bestehenden Kraken-Steuerung.
- Gehäuselüfter erscheinen als einzelne Karten mit RPM, PWM, Sensorquelle, Profil und grafischer Mini-Kurvenvorschau; keine verschachtelte Lüfterlisten-Scrollfläche mehr.
- CoolerControl-Ownership: aktives `coolercontrold` versetzt die Mainboard-PWM-Steuerung in read-only. Explizite Übernahme/Zurückgabe erfolgt über systemd/Polkit und niemals als paralleler Schreibkampf.
- Neuer Gehäuselüfter-Assistent: sicherer 30-%-/80-%-Kontrasttest für zehn Sekunden, anschließende vollständige Wiederherstellung, optionale weiße RGB-Testbeleuchtung und grafische Einbauplatz-Zuordnung über dieselben Slots wie im RGB-Studio.
- PWM↔Einbauplatz-Zuordnungen werden dauerhaft gespeichert und stehen zusammen mit den Profilen Leise/Ausbalanciert/Leistung zur Verfügung.

## Neu in 3.4.23 INTERN

- Neue Mainboard-Lüftersteuerung über Linux-hwmon mit besonderem Fokus auf NCT6687/NCT6687D und MSI-X870-Familien.
- Sichere Kanal-Kalibrierung: ein ausgewählter PWM-Kanal wird zehn Sekunden auf 70 % gesetzt und danach auf seinen vorherigen hwmon-Zustand zurückgestellt; erst nach Benutzerbestätigung darf eine automatische Kurve schreiben.
- Pro bestätigtem Kanal: eigener Name, Sensorquelle CPU/GPU/Kühlmittel/Maximum/gewichtete CPU-GPU-Temperatur, Mindestleistung, Hysterese, Reaktionsverzögerung und individuelle Kurve.
- Drei sichere Kurvenvorlagen „Leise“, „Ausbalanciert“ und „Leistung“ mit automatischer, rein beratender Empfehlung anhand der erkannten Hardware/Kanalbezeichnung; keine Vorlage aktiviert oder kalibriert einen Kanal selbstständig.
- Sensorfehler-Fallback auf 70 % sowie 100-%-Notanforderung ab 90 °C; beim Abschalten der OHC-Regelung oder Programmende wird die Firmware-/BIOS-Steuerung soweit vom Treiber angeboten wiederhergestellt. Falls der aktuelle nct6687d-Treiber `fan_control_watchdog` anbietet, hält OHC zusätzlich einen 10-s-Treiber-Watchdog aktiv, der bei einem abgestürzten/verschwundenen Controllerprozess die ursprünglichen Kurven zurückholen kann.
- Treiber-/Secure-Boot-Diagnose und Fedora-NCT6687-Einrichtungshinweise; OHC umgeht Secure Boot/MOK nicht und schreibt keine ungeprüften Register direkt.
- RGB-Studio zeigt ENE-DRAM mit zusätzlicher Initialisierung an und bietet „ENE-RAM erneut initialisieren“, das den bewährten OpenRGB-Direct-Reclaim erneut ausführt.

Version 3.4.22.1 INTERN ist ein gezielter Stabilitäts-Hotfix für RGB, LCD und CPU-Kurven. Der OpenRGB-SDK-Worker bleibt bei nativen NZXT/GPU-Schreibvorgängen bestehen, ENE-DRAM kann beim Einzeltest einmal gezielt neu geprimt werden und ein animiertes RGB-Design gilt erst nach bestätigtem Direct-SDK-Frame sowie nativen Hardwarebefehlen als übernommen. Zusätzlich akzeptiert der LCD-Streamer wieder die Design-Skalierung ohne Startabbruch und ein geladenes AM5-Profil aktiviert die empfohlenen CPU-Pumpen- und Lüfterkurven unmittelbar.

## Neu in 3.4.23.1 INTERN

- Polkit-geschützter NCT6687-Fan-Helper für Systeme, auf denen Linux `pwmN` korrekt root-schreibbar (`0644`) bereitstellt; OHC selbst wird nicht als root ausgeführt.
- Der Helper besitzt keine freie Pfad-/Shell-Schnittstelle: erlaubt sind nur validierte NCT6687-Kanäle 1–8, Prozentwerte 0–100, Firmware-Rückgabe und der begrenzte Treiber-Watchdog.
- Kalibrierung: 70 % für 10 Sekunden mit RPM-Verlauf statt 5-Sekunden-Sofortprüfung. Das passt zum beobachteten trägen MSI-X870/NCT6687-EC-Verhalten.
- Bei vorheriger Firmwareautomatik stellt OHC über `pwmN_enable=2` zurück; der aktuelle nct6687d-Treiber kann dadurch seine zuvor gesicherte komplette MSI-Kurve wiederherstellen.

## Neu in 3.4.22.1 INTERN

- Stabilitäts-Hotfix für ENE-DRAM/OpenRGB: der langlebige Direct-SDK-Worker wird bei nativen NZXT-/GPU-Befehlen nicht mehr beendet und verliert dadurch nicht mehr unnötig seinen vorbereiteten Direct-Zustand.
- Der RGB-Einzeltest darf das ausgewählte Direct-Gerät einmal bewusst neu primen; damit kann OHC einen festhängenden ENE-RAM-Zustand selbst zurückholen, ohne vorher die OpenRGB-GUI öffnen zu müssen.
- Ein animiertes RGB-Design wird erst als aktiv bestätigt, wenn sowohl der erste vollständige Direct-SDK-Frame als auch alle nativen/NZXT-Fallbacks erfolgreich abgeschlossen sind.
- LCD-GIF-Regression behoben: `prepare_gif()` akzeptiert wieder den zusätzlichen Skalierungswert aus der 3.4.21-Oberfläche; eingebaute und eigene GIFs starten dadurch wieder korrekt.
- Der Sicherheitsfallback auf Flüssigkeitstemperatur bleibt bei einem fehlgeschlagenen LCD-Start aktiv.
- „Profil und empfohlene Kraken-Kurven laden“ aktiviert bei verfügbarem CPU-Sensor jetzt direkt beide empfohlenen CPU-Kurven statt im manuellen Modus zu verbleiben.

## Neu in 3.4.21 INTERN

- Neuer zentraler Kraken-USB-Koordinator mit Request-IDs, Prioritäten, Besitzerstatus, Fehler-/Retry-Logging und Latest-request-wins für ersetzbare LCD-Aufträge.
- Laufende LCD-Designs werden beim Anklicken eines neuen mitgelieferten Designs gezielt ersetzt; ein Klick auf die Designkachel aktiviert das Design direkt.
- RGB-Studio erhält einen eigenen Request-Koordinator: identische Kurzzeitaufträge werden zusammengefasst, veraltete Effektwechsel verworfen und der langlebige SDK-Worker wiederverwendet.
- Gespeicherte RGB-Profile werden beim Start erst nach stabiler OpenRGB-Inventarisierung vollständig angewendet; später erscheinende Geräte können nachgezogen werden.
- Der in 3.4.20 elternlos erzeugte Schnellprofile-Kasten wird wieder korrekt in die Übersicht eingebettet. Beim Tray-Autostart bleiben zusätzliche modale Startfenster weiterhin gesperrt.
- Beim System-Shutdown bzw. kontrollierten Beenden erhält die LCD-Sicherheitsroutine höchste Priorität: Animation beenden und, solange USB noch verfügbar ist, auf Flüssigkeitstemperatur zurückstellen.
- Importierte NZXT-ESC-Profile nutzen einen Live-Renderer im bestehenden CAM-Raw-Streamer statt eines langsamen statischen Aktualisierungspfads. Eingebettete ESC-Vorschauen dienen bei blockierten externen Medien als sichtbare Hintergrundbasis.
- LCD-Zielauflösung und Rendering-Skalierung werden aus den Gerätefähigkeiten abgeleitet, statt eingebaute Designs in mehreren identischen Auflösungsdateien mitzuliefern. Der bekannte Raw-USB-Pfad bleibt aus Sicherheitsgründen auf verifizierte Geräteprofile beschränkt.
- Mitgelieferte LCD-Designs erhalten eine gespeicherte Designgröße (60–160 % bzw. geräteabhängig begrenzt), animierte Hover-Vorschauen und eine optional animierte große LCD-Vorschau.
- LCD-Arbeitskacheln können wieder sortiert werden; bei langen Seiten bleibt eine kompakte Vorschau erreichbar und Mittelklick-Scrolling unterstützt schnelles Navigieren.
- Profilimport verwendet künftig den aktuellen Dateinamen als vorgeschlagenen Profilnamen; Namenskollisionen werden eindeutig behandelt.
- Privacy-/Release-Prüfung wurde erweitert: persönliche Testbezeichnungen werden neutralisiert und Diagnoseausgaben sollen zusätzlich IP-, IPv6- und MAC-Adressen anonymisieren.

## Neu in 3.4.20 INTERN

- ENE-/OpenRGB-RAM wird pro frischer RGB-Worker-Sitzung genau einmal in Direct/Custom geprimt. Dadurch entfällt der beobachtete Workaround, OpenRGB nach dem Boot einmal manuell öffnen und den RAM ansprechen zu müssen; während laufender Effekte wird der Modus weiterhin nicht ständig neu gesetzt.
- Beim Start mit `--autostart` bleiben Ersteinrichtung, Lüfterprofil-Auswahl und andere modale Startdialoge verborgen. Eine noch offene Einrichtung wird bis zum bewussten Öffnen des Hauptfensters zurückgestellt.
- Bei einer wirklich frischen Installation ist die Sprachauswahl jetzt die erste Assistentenseite. Deutsch, Englisch, Spanisch und Französisch werden sofort auf die folgenden Assistentenseiten angewendet.
- Fester Hilfe-Button unten links plus `F1`: integrierte, durchsuchbare Erste-Schritte-, LCD-, Kühlungs-, RGB-, Profil-, OpenLinkHub-, Design-, Autostart- und Diagnoseanleitungen mit direkten Sprüngen zu den passenden Programmseiten.
- LCD-Arbeitsbereich weiter zusammengefasst: Vorschau/Display/Uhr oben, gemeinsamer Bereich für statische und animierte Inhalte samt Bild/GIF-Import und mitgelieferter Galerie, gemeinsamer Hardware-/Ebenenbereich sowie eingeklappte erweiterte FPS-/Transportoptionen.
- Acht eigene, reproduzierbar aus OHC-Projektcode erzeugte LCD-GIFs sind direkt als Galerie eingebaut: Nebula Vanguard, Ringworld Runner, Singularity Dive, Abyssal Bloom, Neon Rain, Magma Heart, Polar Aurora und Firefly Grove.
- Uhr kann zusätzlich als Ebene über GIF/animiertem Hintergrund und Hardwaredaten eingeblendet werden; die vorhandenen Uhroptionen für Format, Datum, Schriftgröße und Farben werden wiederverwendet.
- Aktuelle NZXT-ESC-v3-Dateien mit `preset.background`, `preset.overlay`, `elementType`, `transform` und `config` werden korrekt importiert. Die eingebettete `previewImage`-Grafik dient als sichere Vorschau/Fallback; CSS-`rgb()`/`rgba()`-Farben und aktuelle Elemente wie Metric, Text, Shape, Clock, Analog Clock, Radial Graphic und Sensor Chart werden erkannt bzw. sinnvoll angenähert.
- Externe URL-/Video-Hintergründe werden weiterhin nicht automatisch aus dem Internet geladen. Das ist eine bewusste Sicherheitsgrenze; der Importbericht weist solche Teile aus und nutzt vorhandene eingebettete Vorschauen.

## Neu in 3.4.19 INTERN

- LCD als übersichtliche Kachelansicht mit drei Spalten statt einer langen vertikalen Bereichsliste; die große Import-Profilverwaltung nutzt die volle Breite.
- Start von Hardwareanimationen und Bild/GIF+Hardware-Ebenen rendert nicht mehr synchron im Qt-Hauptprozess, sondern nutzt direkt den vorhandenen externen Stream-Renderer.
- Helligkeit und Ausrichtung werden bei laufendem CAM-Raw-Stream über die koordinierte PAUSE/RESUME-USB-Übergabe angewendet, ohne den Framecache zu verwerfen.
- ENE-/RAM-Direct-Geräte werden nicht erneut unnötig in `SET_CUSTOM_MODE` versetzt, wenn OpenRGB Direct bereits bestätigt hat.
- Discover/AppStream erhält Programmsymbol, ausführliche Beschreibung, GitHub-/Issue-Links, Suchbegriffe und Screenshot-Galerie.
- Die unabhängige NZXT-ESC-Kompatibilitätsschicht und Profilbibliothek aus 3.4.18 bleiben vollständig enthalten.

- Unabhängiger Importer für kompatible `.nzxt-esc-preset`-/JSON-Exporte mit Schema-v3-Unterstützung und toleranter Erkennung älterer Feldvarianten.
- Vor jedem Import erscheint zwingend eine Vorschau mit Liste der direkt unterstützten, angenäherten, nicht unterstützten und aus Sicherheitsgründen blockierten Elemente.
- Importierte Profile werden immer als neue lokale OHC-Kopie angelegt; die ursprüngliche Importfassung bleibt separat für „Importierten Originalzustand wiederherstellen“ gespeichert.
- Profilbibliothek mit Aktivieren, Bearbeiten, Umbenennen, Duplizieren, Löschen, Einzel-Export sowie vollständigem ZIP-Backup und Wiederherstellung von Profilen, Vorschauen, lokalen Medien, Schriften und LCD-Profileinstellungen.
- Reduzierter Ebeneneditor für Sensorquelle, Text, Hex-Farben, Größen, Position, Drehung, Sichtbarkeit, Sperre und Drag-and-drop-Reihenfolge. Ein eindeutiges `CPU`-/`GPU`-Textlabel kann beim Sensorwechsel automatisch angepasst werden.
- OHC-Livedaten für CPU-/GPU-/Kühlmitteltemperatur sowie best-effort Linux-Werte für Last, Takt, Leistung, RAM und Lüfter-/Pumpen-RPM; nicht verfügbare Sensorwerte werden sicher als fehlend dargestellt.
- Externe URLs, Videos, Webmedien und NZXT-ESC-Schriften werden nie automatisch geladen. OHC enthält weder NZXT-ESC-Quellcode noch dessen mitgelieferte Designs oder Medien.

### Komplexe LCD-Designs und NZXT-ESC-Import

Open Hardware Control wird kontinuierlich um neue eigene LCD-Designs und einen grafischen Ebeneneditor erweitert. Da ich jedoch kein professioneller Designer bin, wird die mitgelieferte Auswahl voraussichtlich nicht den Umfang spezialisierter Designprojekte erreichen.

Für besonders umfangreiche und individuell gestaltete LCD-Profile empfehlen wir einen Blick auf das unabhängige Projekt NZXT-ESC:

<https://github.com/mrgogo7/nzxt-esc>

Dort erstellte oder exportierte `.nzxt-esc-preset`-Dateien können über die Importfunktion von Open Hardware Control geladen werden. Unterstützte Hardwarewerte wie CPU- und GPU-Temperatur, Auslastung, Takt, Arbeitsspeicher und Kühlmitteltemperatur werden dabei mit den von Open Hardware Control ermittelten Live-Daten verbunden.

Open Hardware Control und NZXT-ESC sind voneinander unabhängige Projekte. Open Hardware Control enthält weder Quellcode noch mitgelieferte Designs oder Medien des NZXT-ESC-Projekts. Für importierte Designs und enthaltene Medien gelten die jeweiligen Rechte und Lizenzbedingungen ihrer Urheber.

## Neu in 3.4.16 INTERN

- RGB-Tempo, Farbe, Helligkeit und Richtung werden 360 ms zusammengefasst; bei schnellen Änderungen gewinnt immer der zuletzt eingestellte Wert.
- Eine noch laufende NZXT-/GPU-Hardwareübertragung wird seriell abgeschlossen. Der neueste Stand folgt direkt danach, statt mit dem älteren Auftrag zu konkurrieren.
- Bestätigungen des dauerhaften OpenRGB-SDK-Workers sind jetzt exakt dem übertragenen Frame zugeordnet. Ein verspäteter Frame kann keinen neueren Profilstand mehr als aktiv markieren.
- Die fünf diskreten NZXT-Geschwindigkeitsstufen werden gleichmäßiger auf 10–200 % abgebildet; beispielsweise ist 75 % nun eindeutig `slower`, 100 % `normal`.
- Eine rein lesende Hintergrundprüfung fragt den Gerätebestand höchstens einmal pro Minute ab. Ein großer Sprung wie 7 → 2 wird zweimal verzögert bestätigt, während die letzte vollständige Liste sichtbar bleibt.
- Nur ein wirklich veränderter Gerätebestand baut die RGB-Geräteliste neu auf; unveränderte Prüfungen behalten Fokus und Scrollposition.

## Neu in 3.4.15 INTERN

- Neue einzelne OHC-Modusliste mit Beschreibung und sichtbarer Zahl benötigter Farben: Rainbow benötigt keine frei wählbare Farbe, Statisch/Atmen eine, alle zweifarbigen Muster zwei.
- Jede verwendete Modusfarbe kann direkt als `#RRGGBB` eingegeben, aus Standardfarben gewählt oder im Farbdialog eingestellt werden; alte RGB-Profile bleiben kompatibel.
- Neue Standardreihenfolge im RGB-Studio: Engine, Geräte und Effekte, Thermaltake-360-PC-Aufbau, eigene Gruppen.
- Hauptbereiche in RGB, LCD und Kühlung lassen sich am Griff ziehen oder mit ↑/↓ verschieben. Die Reihenfolge wird je Seite gespeichert und kann zurückgesetzt werden; die Inhalte eines Bereichs bleiben fest geordnet.
- Die Übersicht bleibt der erste App-Bereich, ergänzt Prozessor, Kern-/Thread-Aufbau, Grafikkarte, VRAM, Treiber und PCI-Pfad. Jede Hardwarekarte ist einzeln ein-/ausblendbar; ein Knopf stellt den Standard wieder her.

## Neu in 3.4.14 INTERN

- NZXT-„Abwechselnd“ verwendet den bestätigten Zweifarben-Fallback `fading` statt des fehlschlagenden Alias `alternating-4`.
- OHC-eigene OpenRGB-Clientaufträge lösen keine falsche Fremdprozess-/Wiederübernahme-Schleife mehr aus.
- Asynchrone RGB-Teilfehler erscheinen in einer begrenzten internen Liste statt in modalen Popupfenstern.
- Die Thermaltake-360-Vorlage heißt sichtbar „Frelidon PC“ bei kompatibler interner Kennung.

## Neu in 3.4.13 INTERN

- Ein Klick auf eine Designkachel startet beziehungsweise überträgt das Muster direkt; der zusätzliche Startknopf ist dafür nicht mehr erforderlich.
- Neue Kachel „Feste Farbe“; eine danach gewählte Hauptfarbe wird unmittelbar auf die aktuelle Auswahl angewendet.
- Dauerhafte, deutlichere Kachelrahmen unterscheiden „AUSGEWÄHLT“ und „AKTIV“; ein großes Statusfeld über der Galerie nennt Profil, Farbe und Übertragungszustand.
- Neuer Knopf „RGB-Steuerung neu übernehmen“ initialisiert den OHC-Steuerweg neu und wendet das ausgewählte Muster erneut an.
- Optionale, standardmäßig ausgeschaltete automatische Wiederübernahme wartet ausschließlich beobachtend auf das Ende eines separaten OpenRGB-Prozesses und startet das gewählte Muster danach erneut.
- Ein separates OpenRGB wird niemals beendet oder beschrieben. Ein fremder beziehungsweise noch unbekannter SDK-Server blockiert die Übernahme weiterhin sicher.
- Die Wiederübernahme und die Option können in RGB-/Gesamtprofilen gespeichert werden; ohne bereits bestätigte RGB-Freigabe startet keine automatische Hardwaresteuerung.

## Neu in 3.4.12 INTERN

- Kraken-Kanäle 1/2/3 sind im Thermaltake-Bild sichtbar und per Ziehen in ihre echte Einbaureihenfolge sortierbar.
- 17 eigene RGB-Designkacheln in sechs Kategorien mit laufender lokaler Vorschau.
- Ein Startprofil darf die RGB-Freigabe und sein Design ausdrücklich wiederherstellen; separates OpenRGB und eine zweite OHC-Instanz blockieren den Start weiterhin.
- Neuer LCD-Ebenenmodus: statisches Bild oder GIF im Hintergrund, feste oder animierte Hardwaredaten darüber, mit Deckkraft, Größe und Position.
- Drei zusätzliche eigene LCD-Animationen: Neonraster, Radar und Wellenkern.
- „Animation anhalten“ und serielle RGB-Aktionen erhalten die exakte Scrollposition.

## Neu in 3.4.11 INTERN

- dauerhafter Loopback-SDK-Worker statt eines Python-Prozesses und einer TCP-Verbindung pro Gerät und Animationsframe
- ein begrenzter Mehrgeräte-Frame pro Takt, 25-Hz-Ziel, genau ein offener Auftrag und Latest-frame-wins-Zusammenfassung bei langsamem Backend
- echte Übertragungswerte pro Gerät: gemessene SDK-Hz, letzte erfolgreiche Übertragung, Batch-Dauer und Zahl zusammengefasster Zwischenframes
- sechsstufiger RGB-Einrichtungsassistent für Besitzkonflikte, Umbenennen, isolierten Gerätetest, Zonen-/LED-Kalibrierung, PC-Aufbau und GPU-Modus
- Sichttest „Nur diese Zone“ im Zonendialog; andere Zonen desselben Controllers werden dabei schwarz
- automatische Bevorzugung des von der Sapphire gemeldeten Modus „External Control“ für OHC-Animationen ohne Direct Mode
- statische Änderungen bleiben seriell und bestätigt; physische ARGB-Ausgabe wird weiterhin ausdrücklich nicht als rücklesbar dargestellt
- OpenRGB bleibt separat installiert und wird unsichtbar von OHC verwaltet; keine Treiber oder Effects-Plugin-Assets wurden kopiert

## Seit 3.4.7 INTERN

- akzeptiert die von OpenRGB `1.0~rc2` gemeldete SDK-Protokollversion 5 und bleibt mit Version 4 kompatibel
- verwendet weiterhin ausschließlich Loopback, begrenzte Paketgrößen und die unveränderten Farb-/Custom-Mode-Pakete
- entfernt `marquee-4` und `moving-alternating-4` aus den Effekten des NZXT 2023 RGB Controllers
- bildet OHC-„Glut-Komet“ zuverlässig auf `pulse`, den Kreisel auf den bestätigten Regenbogenfluss und „Abwechselnd“ auf das bestätigte Zweifarben-`fading` ab
- erwirbt vor jeder Qt- und Hardwareinitialisierung eine pro Benutzer gültige Kernel-Dateisperre
- beendet einen zweiten Start mit einem klaren Hinweis, ohne OpenRGB, liquidctl, Kraken oder einen anderen Controller zu öffnen
- verweigert den Start sicher, wenn die Sperre aus einem anderen Grund nicht angelegt werden kann

## Seit 3.4.6 INTERN

- große Liste ausgewählter RGB-Geräte mit Steuerweg und letztem Status
- getrennte GPU-/Hardwaremodus-Auswahl ohne unbeabsichtigten OHC-Effekt-Fallback
- einmalige `SETCUSTOMMODE`-Vorbereitung pro Direct-Gerät und Engine-Laufzeit
- fehlertolerante Mehrgeräteaktionen, ausgeblendetes NZXT-Spiegelgerät und mehrstufiger Scrollschutz
- automatische `session.log`- und `previous-session.log`-Diagnoseprotokolle

## Seit 3.4.5 INTERN

- begrenzter Loopback-SDK-Schreibpfad für Direct-Geräte ohne OpenRGB-CLI-/`ApplyOptions`
- vollständiger editierbarer Thermaltake-12-Lüfter-Aufbau und deterministische Grundanordnung

## Seit 3.4.4 INTERN

- atomare Reset-/Engine-Neustartfolge und frische Erkennung vor erneuter Schreibfreigabe
- sichere Zusammenführung des vollständig gespiegelten 14-Geräte-Inventars auf sieben reale Meldungen
- große verschiebbare Thermaltake-PC-Ansicht und gespeicherte Gerätezuordnung

## Seit 3.4.3 INTERN

- erkennt den bestätigten OpenRGB-`ApplyOptions`-/`stl_vector`-Absturz anhand der Prozessausgabe
- isoliert nur das abstürzende Gerät bis zum nächsten OHC-Start; die Sperre wird nicht dauerhaft gespeichert
- setzt serielle Befehlsfolgen nach einem isolierten Gerät fort, damit der Einzeltest sein zuletzt angeordnetes Ziel noch erreicht
- zählt normale Direct-Mode-Fehler pro Gerät; erfolgreiche Frames anderer Geräte setzen den Zähler nicht mehr zurück
- sperrt ein Gerät nach dem ersten bestätigten Prozessabsturz beziehungsweise nach drei eigenen normalen Schreibfehlern
- protokolliert bei der Erkennung OpenRGB-Index, eigenen Gerätenamen, LED-Anzahl und Direct-Fähigkeit

## Seit 3.4.2 INTERN

- behebt den sofortigen Startabbruch `AttributeError: rgb_preview_started`
- Regressionstest für die korrekte Vorschauuhr-Initialisierung vor `build_ui()`
- automatische, anonymisierte Protokolle unter `~/.local/state/open-hardware-control/startup.log` und `last-crash.log`
- der Diagnosebericht übernimmt die letzten Startzeilen und den letzten Python-Absturz automatisch

## Seit 3.4.1 INTERN

- sicherer Einzelgerätepfad: kein OpenRGB-Aufruf enthält mehrere `--device`-Blöcke
- statische Farben, native Modi und OHC-Frames werden seriell abgearbeitet; ein fehlerhaftes Gerät beschädigt nicht den Auftrag anderer Geräte
- Geräte ohne Direct Mode verwenden passende, tatsächlich gemeldete Hardwaremodi; `Random Flicker` dient beispielsweise als Blitz-Fallback
- Gruppen und Kachelauswahl werden nicht mehr gelöscht, bevor die RGB-Erkennung fertig ist
- „Alle auswählen“ oben und als großer Knopf unter den Gerätegruppen
- neue Gruppen übernehmen auf Wunsch sofort die aktuell ausgewählten Kacheln
- doppelte Gerätenamen erhalten unterscheidbare Nummern und können über das Stiftsymbol frei benannt werden
- eigener Geräte-Testmodus mit Testfarbe, „nur dieses Gerät an“, „nächstes Gerät“ und sicherem Ausschalten aller von OHC steuerbaren Komponenten
- PC-Skizze für Oben, Vorne, Seite, Unten, Hinten, GPU, GPU-Halterung, RAM und Pumpenkopf
- pro Position: eigener Name, Anzahl, Anschlussnotiz, RGB-Gruppe und zugeordnete Gerätekacheln
- mitgelieferte Vorlage „Frelidon PC“ mit Kraken-Radiator, A1, A2, B6, B7 und SYS-FAN6
- die separate sichtbare NZXT-RGB-Box entfällt; `led1` bis `led3` liegen im gemeinsamen Arbeitsbereich
- Profile speichern zusätzlich Gerätenamen und die komplette PC-Skizze, starten aber weiterhin keine Hardwareanimation automatisch
- der große Komplett-Zurücksetzen-Knopf bleibt erhalten

## Seit 3.4.0 INTERN

- automatisch verwaltete, fensterlose RGB-Engine ohne manuellen Serverstart
- Gerätekacheln, Drag-&-Drop-Gruppen, ENE-DRAM-Deduplizierung und gemeinsame NZXT-/OpenRGB-Auswahl
- topology-sichere NZXT-Effekte und bestätigter Komplett-Reset

## Seit 3.3.0 INTERN

- zehn originale OHC-Effekte und sieben Designvorlagen mit Live-Vorschau
- native, vom jeweiligen Gerät gemeldete OpenRGB-Modi
- Loopback-only SDK-Verbindung, Sitzungsfreigabe und automatische Fehlerabschaltung
- Desktop-Designs standardmäßig ausgeschaltet, experimentell und aus dem Menü verborgen

## Seit 3.2.0 INTERN

- Windows-8- und Windows-8.1-artige KDE-Designs mit bildschirmfüllender lokaler Kachelübersicht
- schwarze Charms-Leiste an oberer/unterer rechter Ecke und über `Super+C`, für mehrere Bildschirme
- freie OHC-Symbole und Mauszeiger für Windowed 11, Orchard und Metro 8 sowie KDE-Standardauswahl
- wählbare Backups, Aufbewahrungsgrenze, Löschen, SHA-256-Export und streng validierter Import
- automatische Transaktionswiederherstellung und KDE-Breeze-Light-Notfallfallback
- keine proprietären Microsoft-/Apple-Assets, Online-Kacheln oder fremden Designarchive
- automatische Abhängigkeitsangebote einschließlich PySide6 QtNetwork und QtDBus

## Seit 3.1.1 INTERN

- Fedora-44-Korrektur: `qdbus-qt6` wird ohne Kompatibilitätslink direkt erkannt
- sichere Erkennung von `qdbus6`, `qdbus-qt6` und den Qt6-Systempfaden
- bestätigte Installation optionaler Desktop-Werkzeuge über DNF, APT, Pacman und Zypper

## Seit 3.1.0 INTERN

- hierarchischer Menüpunkt **System → Desktop-Designs**
- Windows-11-Stil mit unterer 48-Pixel-Leiste und mittigem Starter-/Programmbereich
- macOS-Stil mit oberer Systemleiste und zentriertem, automatisch ausblendbarem Dock
- heller und dunkler Farbmodus für beide Anordnungen
- unverändernde Vorschau und eigener Bestätigungsdialog vor jedem Anwenden
- datiertes Backup der berührten KDE-/Plasma-Konfiguration vor jeder Änderung
- automatische Rückkehr zum unmittelbar vorherigen Zustand, falls das Anwenden fehlschlägt
- manuelle Schaltfläche zum Wiederherstellen des letzten Desktop-Backups
- keine Administratorrechte, keine fremden Paketquellen und keine Design-Downloads
- keine Microsoft-/Apple-Logos, -Schriften oder -Hintergrundbilder
- interne Paketkennzeichnung verhindert eine versehentliche öffentliche GitHub-Veröffentlichung

## Seit 3.0.9

- Klick auf eine gemeldete Maustaste öffnet den neuen Belegungsdialog
- Funktionsarten: keine Funktion, Medien-, DPI-, Tastatur-, Sniper-, Maus- oder vorhandene Makrofunktion
- Originalfunktion, Gedrückthalten und Ausführen beim Loslassen werden entsprechend der offiziellen OpenLinkHub-API unterstützt
- Tastaturmakros lassen sich mit Pausen innerhalb des aktiven Aufnahmedialogs erstellen; keine verdeckte systemweite Eingabeaufzeichnung
- Schreibaktionen bleiben sitzungsweise gesperrt, streng validiert und ausschließlich auf die lokale Loopback-API begrenzt
- LCD-Hardwarebilder enthalten keine kleinen `LIVE`, `LETZTER WERT` oder `KRAKEN CONTROL`-Zusätze mehr
- getrennte Hex-Farben und 60–200-%-Größenregler für Sensorbeschriftung und Temperaturzahl
- globale Einheit Celsius/Fahrenheit für Dashboard, Status, Kurventabellen/-diagramme, Sicherheitsgrenzen, Profile und LCD-Hardwareanimationen
- Kühlberechnung und gespeicherte Sicherheitswerte bleiben intern unverändert in Celsius

## Seit 3.0.6

- der aktive LCD-Modus wird ausdrücklich im Gesamt- oder LCD-Profil gespeichert
- normale GIFs und animierte Hardwaredesigns werden nach dem Neustart wieder als Animation gestartet
- ältere 3.0.5-LCD-Profile erkennen eine gespeicherte GIF-Datei automatisch als GIF-Modus
- beim Desktop-Autostart wartet die LCD-Wiederherstellung fünf Sekunden ab Programmstart
- der im Gesamtprofil gespeicherte maximierte Fensterzustand darf den minimierten Tray-Autostart nicht mehr überschreiben
- SIGTERM/Sitzungsende wird sauber verarbeitet, damit ein normaler Desktop-Neustart nicht fälschlich als LCD-Absturz gilt

## Seit 3.0.5

- Pumpenkurve und Radiatorlüfterkurve verwenden jetzt CPU-Temperatur statt Wassertemperatur
- echte laufende Software-Regelung über den Linux-CPU-Sensor (`k10temp`/hwmon)
- lineare Berechnung zwischen den Kurvenpunkten, geglättete CPU-Werte, Hysterese und begrenzte Schreibintervalle
- Pumpen- und Lüfteränderungen werden bei Bedarf in einem gemeinsamen USB-Fenster übertragen
- die CPU-Kurvenregelung bleibt auch während einer LCD-GIF- oder Hardwareanimation aktiv
- bisherige 20–50-°C-Wasserkurven werden beim Upgrade sicher durch CPU-Kurven ersetzt
- alle AMD-AM5-Profile besitzen angepasste CPU-Kurven; Ryzen 9000/8000G/7000 und 7000 X3D behalten getrennte Temperaturgrenzen
- die Wassertemperatur bleibt unabhängig als Warn-, Kritisch- und 100-%-Notfallschutz erhalten
- fällt der CPU-Sensor mehrfach aus, werden aktive Kurvenkanäle vorsorglich auf 75 % gesetzt
- bei einem echten Programmende wird für aktive CPU-Kanäle eine konservative autonome Wasser-Hardwarekurve hinterlegt

Eine CPU-Kurve benötigt die laufende Anwendung. Das Schließen in den System-Tray beendet die Regelung nicht. Beim echten Beenden wird deshalb automatisch der sichere Hardware-Fallback gesetzt.

## Seit 3.0.4

- vorhandene OpenLinkHub-Temperaturprofile oder manuelle Werte auf gemeldete Lüfter-/Pumpenkanäle anwenden
- vorhandene RGB-Profile, Gerätehelligkeit, Kanalbezeichnungen und LCD-Ausrichtung ändern
- Maus-DPI-Stufen, Abfragerate, Ruhemodus, Angle Snapping und Tastenoptimierung steuern
- Tastaturprofile, Layout sowie gerätespezifische Drehregler-, Ruhemodus- und Abfrageratenwerte übertragen
- Headset-Ruhemodus, ANC/Transparenz, Stummschaltanzeige und Sidetone steuern
- gemeldeten Corsair-Netzteilen einen unterstützten Lüftermodus zuweisen
- Schreibzugriffe bleiben pro Programmsitzung gesperrt, bis sie ausdrücklich bestätigt wurden
- feste API-Aktionsliste, strenge Wertebereiche, nur Loopback und keine vollständigen Seriennummern in Oberfläche oder Log

## Seit 3.0.3

- die beiden Modusschaltflächen verwenden keinen vorzeitig umspringenden Qt-Checkzustand mehr
- nur der zuletzt erfolgreich auf die Kraken übertragene Modus erhält die feste grüne Aktivfarbe
- Hover- und Gedrückt-Zustand des aktiven Schalters bleiben eindeutig lesbar
- ein fehlgeschlagener oder noch laufender Hardwarebefehl verändert die Aktivmarkierung nicht
- USB-Protokoll, Kurvenübertragung und GIF-Übergabe bleiben gegenüber 3.0.2 unverändert

## Seit 3.0.2

- Pumpe und Radiatorlüfter besitzen jeweils eigene Schaltflächen für **Manuell aktivieren** und **Kurve aktivieren**
- die markierte Schaltfläche zeigt den zuletzt erfolgreich auf die Kraken übertragenen Modus
- der Wechsel zu Manuell überträgt den aktuellen Prozentwert als feste Drehzahl
- der Wechsel zur Kurve validiert und überträgt die angezeigte Wassertemperaturkurve
- Schalter, bisherige Anwenden-Knöpfe, Schnellprofile und gespeicherte Profile bleiben synchron
- die koordinierte GIF-USB-Übergabe aus 3.0.1 wird für beide Umschaltwege verwendet

## Seit 3.0.1

- feste Pumpen- und Lüfterwerte bei laufender GIF-Animation ändern
- Pumpen- und Lüfterkurven bei laufender GIF-Animation übertragen
- Schnell-, Sicherheits- und gespeicherte Kühlprofile während der Animation anwenden
- der Streamer gibt den USB-Zugriff koordiniert frei, bleibt aber mit dem vorbereiteten Framecache aktiv
- nach dem Kühlbefehl verbindet sich derselbe Streamer neu und setzt die Animation automatisch fort
- PAUSE-/RESUME-Bestätigungen und Zeitlimits verhindern parallele oder hängende USB-Zugriffe
- ACK-Prüfung, Watchdog und LCD-Sicherheitsfallback bleiben erhalten

## Seit 3.0.0

- linke, hierarchische Navigation
- hardwareabhängige Sichtbarkeit der Gerätemodule
- Option „Nicht erkannte Geräte/Module anzeigen“
- automatische Übernahme bisheriger Kraken-Control-Einstellungen
- OpenLinkHub-Installation, Dienstkontext und lokale API erkennen
- Corsair-Geräte und Telemetrie aus der OpenLinkHub-API anzeigen
- OpenLinkHub-Benutzerdienst starten, stoppen und neu starten
- lokales Web-Dashboard öffnen
- Warnung bei Systemkontext und doppeltem Dienst

## Module

### NZXT Kraken 2023

Der komplette Funktionsumfang aus 2.9.23 bleibt erhalten. Version 3.0.5 ersetzt die sichtbaren Wasser-Hardwarekurven durch softwaregeregelte CPU-Temperaturkurven für Pumpe und Lüfter. RGB, Bilder, Uhr, statische und animierte Live-Hardwaredesigns, CPU-/GPU-Livewerte, Profile, vier Sprachen, adaptive Oberfläche und LCD-Sicherheitsfallback bleiben enthalten.

Unterstützte Hauptgeräte:

| Gerät | USB-ID | Umfang |
|---|---|---|
| NZXT Kraken 2023 | `1e71:300e` | Wasser, Pumpe, Radiatorlüfter, LCD |
| NZXT 2023 RGB Controller | `1e71:2012` | drei RGB-Kanäle |

### Corsair · OpenLinkHub

Open Hardware Control spricht OpenLinkHub ausschließlich über die lokale API `http://127.0.0.1:27003` an. Die seit Version 3.0.4 enthaltenen dokumentierten Schreibbefehle für Kühlung, RGB/LCD, Maus, Tastatur und Headset bleiben unverändert verfügbar. Die App zeigt nur Bedienfelder für passende erkannte Geräte; besonders komplexe Funktionen wie eigene Makrofolgen, vollständiger RGB-Editor oder neue LCD-Mediendateien bleiben im lokalen OpenLinkHub-Web-Dashboard.

Das Modul erkennt Benutzer- und Systemdienst getrennt. Systemweite Dienständerungen werden nicht automatisch durchgeführt. Medienwiedergabe und virtuelles Audio benötigen den OpenLinkHub-Benutzerkontext.

### RGB-Studio · OpenRGB-SDK

Das RGB-Studio nutzt einen separat installierten OpenRGB-Prozess als Gerätebackend. Die App startet diesen bei Bedarf selbst als privaten fensterlosen Kindprozess, akzeptiert nur den lokalen SDK-Endpunkt `127.0.0.1:6742` und verwendet den OpenRGB-CLI ausschließlich mit einem ausdrücklichen `--client`-Ziel. Dadurch übernimmt Open Hardware Control keine ungeprüften Mainboard-, RAM-, Tastatur- oder Lüftertreiber.

Erkannte Geräte, Zonen, LED-Anzahl und Modi werden angezeigt. Statische Farben und native Hardwaremodi funktionieren pro Gerät. Die eigenen OHC-Animationen benötigen einen gemeldeten Direct Mode. Um USB-Kollisionen zu vermeiden, sind erkannte NZXT-Geräte gesperrt, solange das NZXT-Modul sie besitzt; dasselbe gilt für Corsair-Geräte bei erkanntem OpenLinkHub.

## Kühlung während einer LCD-Animation

Normale Kraken-Statusabfragen bleiben während des CAM-Raw-Streams pausiert. Der Linux-CPU-Sensor wird davon nicht berührt und die CPU-Kurvenregelung läuft weiter. Nur wenn sich die berechnete Leistung relevant ändert, verwendet Open Hardware Control eine kurze, sichere Transaktion:

1. Der Streamer beendet den aktuellen vollständigen Frame und schließt seine Kraken-Verbindung.
2. Die App überträgt exklusiv den neu berechneten Pumpen- und/oder Lüfterwert.
3. Derselbe Streamer übernimmt die Kraken wieder, primt die vorgemerkte Cachephase und setzt die Animation fort.

Die Animation kann dabei kurz stehen bleiben, muss aber weder neu eingelesen noch vollständig vorbereitet werden. Glättung, Hysterese, 2-%-Stufen sowie getrennte Mindestzeiten für steigende und fallende Werte verhindern unnötige USB-Unterbrechungen. Schutzfunktionen, die eine aktuelle Wassertemperatur aus der normalen Kraken-Statusabfrage benötigen, bleiben während des Streams eingeschränkt; die CPU-Kurve selbst bleibt aktiv.

## Installation

### Fedora und Nobara – RPM

Lade `open-hardware-control-3.4.28-0.intern2.noarch.rpm` in deinen Downloads-Ordner und führe aus:

```bash
cd ~/Downloads
sudo dnf install ./open-hardware-control-3.4.28-0.intern2.noarch.rpm
```

### Debian, Ubuntu und Linux Mint – DEB

Lade `open-hardware-control_3.4.28~intern2_all.deb` in deinen Downloads-Ordner und führe aus:

```bash
cd ~/Downloads
sudo apt install './open-hardware-control_3.4.28~intern2_all.deb'
```

### Universelles Installationspaket

Das ZIP funktioniert auf Fedora/Nobara, Debian/Ubuntu/Mint, Arch/Manjaro/EndeavourOS und openSUSE. Lade `open_hardware_control_v3_4_28_INTERN.zip` herunter und führe aus:

```bash
cd ~/Downloads
unzip open_hardware_control_v3_4_28_INTERN.zip
cd open-hardware-control-3.4.28-INTERN
chmod +x install.sh
./install.sh
```

Die vorhandene Version wird aktualisiert. Anschließend findest du **Open Hardware Control by Frelidon** im Anwendungsmenü. Die Abhängigkeitsprüfung erkennt die gängigen Paketmanager automatisch. Alle distributionsspezifischen Befehle und Hinweise stehen in [INSTALL.md](INSTALL.md).

Start im Terminal:

```bash
~/.local/bin/open-hardware-control
```

Der alte Befehl `kraken-control` startet aus Kompatibilitätsgründen ebenfalls die neue App. OpenLinkHub wird separat nach dessen offizieller Anleitung installiert und von Open Hardware Control nicht verändert oder mitgeliefert.

## Sicherheit

- Kraken-Schreibzugriffe bleiben auf passende liquidctl-Geräte begrenzt.
- OpenLinkHub-Zugriff ist auf Loopback beschränkt.
- OpenRGB-Zugriff ist auf `127.0.0.1:6742`, ausdrücklichen Clientmodus und eine bereits erreichbare Serverinstanz begrenzt.
- OpenRGB-Schreibrechte gelten nur für die aktuelle Sitzung; konkurrierende NZXT-/Corsair-Geräte bleiben gesperrt.
- OpenLinkHub-Seriennummern werden gekürzt.
- Corsair-Schreibbefehle sind auf eine feste dokumentierte Aktionsliste und validierte Werte begrenzt.
- Die Freigabe gilt nur für die aktuelle Programmsitzung und ist bei einem Dienstkonflikt gesperrt.
- Der systemweite OpenLinkHub-Dienst wird nie automatisch geändert.
- Firmwareaktualisierungen gehören nicht zum Funktionsumfang.

## Dokumentation

- `Open_Hardware_Control_Projekt.md` – zentrale Architektur- und Projektdokumentation
- `OPENLINKHUB_INTEGRATION.md` – Umfang und Sicherheitsgrenzen der Corsair-Anbindung
- `RGB_STUDIO.md` – Bedienung, Effekte, Gerätebesitz und OpenRGB-Serverstart
- `RGB_SECURITY_AUDIT.md` – Lizenzentscheidung, Quellcodegrenzen und Sicherheitsprüfung
- `Kraken_Control_Projekt.md` – vollständige Vorgängerdokumentation des NZXT-Moduls
- `USB_CAPTURE_FINDINGS.md` – technische LCD-Mitschnittauswertung
- `SECURITY.md`, `SUPPORTED_DEVICES.md`, `PROFILES.md`, `CPU_PROFILES.md`

## Status

Öffentliche experimentelle Beta. Die Software wird ohne Garantie bereitgestellt. Open Hardware Control ist ein unabhängiges Projekt und wird nicht offiziell von NZXT, Corsair oder OpenLinkHub unterstützt.

Lizenz: GPL-3.0-or-later.
