# Komponenten- und Versionsübersicht – Version 3.4.29.183 INTERN

## Paketabschluss .183 · 14.11.26

Alle sechs Artefakte gebaut und unabhängig geprüft: Laufzeit-/Entwickler-ZIP,
Quell-TAR, vollständiges Local-AI-Gitbundle, DEB und RPM. Sechs Dist-SHA256,
ZIP-CRCs und vollständige Manifeste, Quell-TAR-Manifest, Bundle-Historie,
DEB-Metadaten/Root-Eigentümer sowie RPM-Header-/Payload-Digests bestanden.
474 Python-Laufzeitquellen und 169 Assets sind in ZIP/TAR/DEB/RPM bytegleich.
Genau beide .182/.183-Sicherungen bleiben erhalten; je acht Hashes verifiziert.
Der RPM-Bau nutzte den vorhandenen Standardbibliothek-Writer, da rpmbuild hier
nicht installiert ist. Keine neue Fedora-Liveprüfung wird daraus abgeleitet.

Benutzer- und Systeminstallation wurden durch diesen Auftrag nicht aktualisiert;
die .182-Benutzerkopie behält den vorangegangenen kleinen VRR-Hotfix. Es wurde
kein Anwendungs-/Systemneustart ausgeführt. Pakete und Sicherungen bleiben
unveränderte Schnappschüsse vor diesem nachträglichen Verifikationsnachweis.
Der Snapshotcommit im vollständigen Gitbundle ist `8169680`; GitHub unverändert.

## Quellfreigabe .183 · 13.11.26

1.763 Tests und fünf Untertests bestanden, einschließlich echter Qt-Oberfläche
in vier Sprachen, drei Fenstergrößen und beiden Themen. 474 Python-Laufzeitquellen,
2.658 gemeinsame Nachrichten-IDs. Kompilierung, Sicherheit/Datenschutz,
Modulregister und sämtliche restlichen Release-Prüfungen bestanden. Die erste
Gesamtsuite scheiterte nur an zwölf gesperrten Testsockets; der Wiederholungslauf
mit freigegebenen lokalen Sockets und deaktivierten Hardwarezugriffen bestand
vollständig. Danach wurde der alte ZIP-Dateiname in beiden Installationsanleitungen
berichtigt und der unveränderte restliche Wächterteil erfolgreich fortgesetzt.
Keine Prüfung wurde ausgelassen oder abgeschwächt. Zehn vollständige
Hauptfensteraufnahmen samt Hashes stehen unter `docs/images/rendering-evidence/`
(`hardware-fix-183.json`); Fixstatus ist synthetisch. Vorbauabschnitte darunter
bleiben historische Schritte. Paketbau und abschließende Artefaktprüfung folgen.
Die laufende Benutzer-/Systeminstallation bleibt .182; kein neuer Fedora-Live-
oder physischer Boot-/Deinstallationstest. GitHub bleibt unverändert.

## Entwicklung .183 · 13.11.26 — Hardware Fix lokal und übersichtlich

Hardware Fix bleibt 1.0. Zwei Hauptaktionen installieren den lokalen Fix oder
entfernen ihn einschließlich Ubuntu-Automatik. Anbieterwahl und bloßes
Umetikettieren entfallen auf Eigentümerwunsch. Der lokale Benutzerdienst läuft
unabhängig vom OHC-Fenster; es gibt weiterhin nur einen Wächter und denselben
Dienstnamen. Erfolgreiche explizite Installation speichert local/local.
Diagnose, Spieltest und einzelne Reparaturschritte bleiben in Weitere Optionen.
Technische Zustände stehen standardmäßig eingeklappt und vollständig übersetzt.

`workflow.py` koordiniert nur bestehende feste Schritte: fehlender Boot-Fix,
nach geladenem Override Desktop und Automatik ausschließlich auf Ubuntu/GNOME.
Gesunde Bootressourcen und bereits dauerhaft aktives GNOME-VRR werden nicht
erneut geschrieben. Erstinstallation wartet auf nötigen Neustart und kann über
Installieren fortgesetzt werden. Fedora behält seinen bisherigen Bootpfad.
UUID-gebundene Terminalergebnisse beheben übersehene schnelle Abschlüsse;
veraltete Resultate, Doppelklicks und Startfehler werden abgefangen. Protokolle
sind begrenzt, redigiert und im Dialog als Klartext behandelt. Exakte Boottoken
und fehlerhafte Anbieter-JSON sind zusätzlich abgesichert. Der MSI-Hashfix aus
dem vorangegangenen Live-Nachweis ist enthalten. Keine Änderung an EDID/Timings.

Lokalisierung 1.0 ergänzt `hardware_fix_messages.py`, atomar über
`content_ui_messages.py` und die vier Sprachdateien: 2.658 gemeinsame IDs.
Neue Regressionen `test_hardware_fix_setup_3429183.py` und
`test_hardware_fix_vrr_identity.py`. Vollständige Release-Prüfung, Sichtkontrolle,
Paketierung und beide rollierenden Sicherungen folgen. Kein GitHub-Auftrag.

Lokaler Abschluss 12.11.26 (.182): 1.736 Tests/fünf Untertests und alle Release-
Wächter bestanden. Sechs Pakete und beide .181/.182-Sicherungen verifiziert;
Benutzer-/Systemkopie .182 mit je 472 Quellen/169 Assets bytegleich installiert.
Installierte Wayland-Ansichten in beiden Themen, Erhalt der Profile/Plugins und
normaler Start geprüft. Paket-/Sicherungsstände bleiben unverändert vor diesem
nachträglichen Nachweis; kein GitHub-Upload. Ältere Vorbauangaben sind historisch.

## Entwicklung .182 · 12.11.26

LCD-Arbeitsbereich 1.0 ist eine neue reine Kompositions-/Navigationsschicht.
GPU-Steuerung 1.0 erhält einen gemeinsamen Arbeitsbereich mit bestehenden
Widgets/IDs. Host-Einstellungen werden nach Wichtigkeit geordnet. Bestehende
LCD-/GPU-/Treiber-/Backendversionen und Hardwarebesitzer ändern sich nicht.
472 Python-Laufzeitquellen, 2.618 Nachrichten-IDs in vier Sprachen; gezielte
UI-/Entwurfs-/Sprach-/Sichtbarkeitsprüfungen und drei Qt-Fenstergrößen in beiden
Themen bestanden. Vollprüfung mit 1.736 Tests/fünf Untertests, Kompilierung,
Sicherheit/Datenschutz und Modulbudgets bestanden. Pakete/Installation folgen.
Installiert .181.

Lokaler Abschluss 12.11.26: .181 in Benutzer- und Systemkopie installiert;
beide Bäume mit 464 Pythonquellen geprüft. 1.732 Tests/fünf Untertests,
2.584 Sprach-IDs, sechs Pakete und beide .180/.181-Sicherungen verifiziert.
Installierte Wayland-Ansichten in beiden Themen, Profile/Plugin-Erhalt und
normaler RGB-/Levita-Start geprüft. Backendversionen bleiben unverändert.
Nachfolgende Vorbauangaben dokumentieren den zeitlichen Entwicklungsstand.

## Entwicklung .181 · 12.11.26 — noch nicht installiert

Gemeinsame UI-Bereiche 1.0, Hilfe 1.0 und Übersichtserkennung 1.0 sind neue
Darstellungs-/Lesemodule. Designs & Spiele 1.1 erweitert auf 15 unterschiedliche
Paare und reale je-Paar-LCD-Größen; LCD-Medienmanager 1.1 ist eingebettet.
PC-Gehäuseprofile 1.5, Profil-Arbeitsbereich 1.1, GPU-Steuerung 1.0 und UI-Leistung
1.1 behalten ihre öffentlichen Verträge und delegieren neue Darstellung bzw.
eindeutigen Lesestatus. Bestehende Backend-/Treiber-/Hardwareversionen ändern sich
nicht. Lokalisierung 1.0 hat aktuell 2.584 gemeinsame IDs in DE/EN/ES/FR.
30 aktuelle Hub-/Größen-/Metadatentests und 184 RGB-Schleifenprüfungen bestehen.
Zwölf Abschnitts-/Gehäusetests prüfen vollständige Hauptfenster-Grabs in drei
Größen und beiden Themen; Hub, Gehäuse und Hilfe sind im echten Qt-Hauptfenster
geprüft. Der Qt-Eigentümerfehler beim Umhängen vorhandener Comboboxen und schmale
Inhaltsbreiten sind korrigiert. Vier vollständige UI-/Lokalisierungstests
bestätigen 2.584 IDs. Neuere LCD-Absichten und Seitenverbergen verwerfen
Encoderaufträge; eine begrenzte H.264-/MP4-Metadatenprüfung schützt Cache-Ergebnisse.
Quellfreigabe mit 1.732 Tests/fünf Untertests, Sicherheit, Datenschutz und
Modulbudgets bestanden; 464 Laufzeitquellen. Pakete/Sicherungen und Installation folgen.
Letzte verifizierte Benutzer-/Systemversion bleibt .180.

## Entwicklung .180 · 11.11.26

Profil-Arbeitsbereich 1.1 ist unter `profiles_workspace/v1_1/` aktuell. Neue
Kompositions-, Layout-, Flächen- und Zusammenfassungsmodule halten Bibliothek,
Profilkarte und geöffnete Unterbereiche lesbar; der äußere Scrollbereich übernimmt
Mehrhöhe. Reine Modelle, vorhandene ID-/CRUD-/Startverträge und Hardware-Unterbauten
bleiben erhalten. Lokalisierung 1.0 besitzt 2.515 gemeinsame IDs. Vier Sprachen,
beide Themen und drei Fenstergrößen bestehen die gezielte echte Qt-Geometrieprüfung.
Vollständige Release-Prüfung, Paketbau/Sicherungen und lokale Installation folgen;
kein GitHub-Auftrag und kein realer Fedora-Hardwarelauf.

Vollständiger .180-Wächter: 1.644 Tests und fünf Untertests bestanden;
443 Python-Laufzeitquellen und 2.515 gemeinsame Sprach-IDs. Alle sechs Pakete,
beide .179/.180-Sicherungen und beide installierten Quell-/Medienstände geprüft.
Benutzer- und Systemkopie .180 laufen bzw. sind installiert; keine neue Hardware-
Kompatibilitätsbehauptung und kein GitHub-Upload.

## Entwicklung .179 · 11.11.26

Profil-Kühlungsbereitschaft 1.0 ergänzt höchstens zehn Sekunden asynchrones
Sensorwarten. Laufzeitprotokoll 1.0 ergänzt Fehler-Hooks und GUI-Brücke;
Lokalisierung 1.0 besitzt 2.507 IDs. ProcessRuntime 1.1 und sämtliche Schreib-
Unterbauten bleiben unverändert. Kein veralteter Sensorwert wird akzeptiert.

## Entwicklung .178 · 11.11.26

Profil-Arbeitsbereich 1.0 und Programm-Hintergründe 1.0 sind neue reine
Oberflächenmodule. Display-Effekte 1.11 erhält additive Matrix-Varianten;
Lokalisierung 1.0 enthält 2.501 gemeinsame IDs. Bestehende native RGB-/LCD-/GPU-
Unterbauten bleiben unverändert. Keine neue Hardware-Kompatibilitätsbehauptung.

Öffentliche .176-Veröffentlichung am 11.11.26 beauftragt. STABLE-Wächter:
1.587 Tests und fünf Untertests bestanden; alle sechs Artefakte, beide
.176-INTERN/STABLE-Sicherungen und 414 Quellen in ZIP/DEB/RPM geprüft.
GitHub-Abschluss: .176 ist Latest, Quellcommit/Tag `34c64d3`; alle sechs
öffentlichen Paket-Hashes und die heruntergeladene Prüfsummenliste stimmen.
Upload der lokal geprüften Pakete wegen DNS-Ausfall im GitHub-Runner; kein
entfernter CI-Erfolg behauptet. Installiert bleibt .176 INTERN.

Entwicklung .176: Lüfterzuordnung 1.0 mit ausdrücklich unbenutzten Anschlüssen,
120-s-Stopptest über die bestehenden Mainboard-Schreibwege und kurzer
10-s-Treiberlease. RGB-Weißhilfe nutzt die vorhandene Preview-Sperre und
Native-STOP-Bestätigung. Temperaturverlauf bleibt 1.2, ergänzt `selection.py`
und `readings.py` für Symbols-/Ziehauswahl und wiederverwendete Messwertkarten.
Lokalisierung 1.0: 2.444 gemeinsame Sprach-IDs. Ubuntu/Fedora-Pfade und bestehende
Backend-Versionen unverändert; keine reale Stopptest-/Absturzsimulation am PC.
Vollständiger Wächter mit 1.587 Tests und fünf Untertests bestanden;
414 Python-Laufzeitquellen. Alle sechs Pakete und beide .175/.176-Sicherungen
geprüft. Benutzer- und Systeminstallation abgeschlossen, DPKG meldet
3.4.29.176~intern2; beide Kopien entsprechen allen 414 Quellen bytegenau.
Profile und Native-Plugin erhalten, fünf native Arbeiter ohne gemeldete Fehler,
Sapphire External Control und gespeichertes Levita-Design aktiv.

Entwicklung .175: Hardwareprüfung 1.0 mit 41 kategorisierten Modellkarten;
Navigationseinstellungen 1.0 mit abgeschlossener Zeigerauswahl vor Seitenwechsel;
Lokalisierung 1.0 mit 2.381 Sprach-IDs. Hardware-/Backend-Versionen und
Einstellungen unverändert. Vollständiger Wächter: 1.556 Tests und fünf Untertests
bestanden. 406 Python-Quellen in ZIP/DEB/RPM geprüft; Benutzerinstallation .175
läuft mit fünf nativen Arbeitern ohne gemeldete Fehler. Systemkopie nach
Linux-Bestätigung ebenfalls .175 (DPKG 3.4.29.175~intern2); alle 406 Quellen
in beiden Installationen bytegleich geprüft. Profile und Plugin erhalten.

## OHC-Modulstand und aktuelle Ubuntu-Konfiguration

Lokaler Stand .174: Benutzerkopie gestartet; Benutzer- und Systemkopie mit allen
403 Python-Dateien identisch. DPKG bestätigt 3.4.29.174~intern2. Native Engine mit
fünf Arbeitern, null gemeldeten Fehlern; Sapphire External Control und gespeichertes
Levita-Design bestätigt. Keine unabhängige Standard-DPI ohne Nutzerauswahl gesetzt.


Abschluss .174: 403 Python-Laufzeitquellen, 2.324 gemeinsame Sprach-IDs und
1.544 Tests plus fünf Untertests. Standard-DPI wird privat je Mausprofil von
der aktiven Backend-Stufe getrennt und nur nach ausdrücklichem Speichern über
einen optionalen Benutzer-Vorstarthelfer wiederhergestellt. Kein USB-Zugriff
oder Administratorrecht im Helfer. Lokaler Versionswechsel abgeschlossen;
Veröffentlichung und optische Prüfung nach Rechnerneustart bleiben offen.


Entwicklung 11.11.26 (.172): Gehäuse-/Corsair-Ansichten, gemeinsame dynamische
Listenhöhen, eigene Kategoriesymbole und Gerätebeschreibungen ergänzt.
Lokalisierung: 2.324 gemeinsame Nachrichtenquellen. OpenLinkHub 0.9.4 ist nach
vollständiger privater .9.2-Sicherung im Benutzerdienst aktiv; echte lokale API
meldet sechs SABRE-DPI-Stufen und sechs Tasten. Die Auswahl einer neuen Start-
DPI wurde nicht auf der Maus ausgeführt. OHC-Paketbau und Installation folgen
nach der vollständigen Prüfung; GitHub bleibt ausstehend.


Stand 11.11.26: .170 ist in beiden Installationen vorhanden und nach
Rechnerneustart flüssig bestätigt. OpenRGB 1.1/Native Engine ist tatsächlich
aktiv; die frühere .168/OpenRGB-1.0-Autostartursache ist behoben. .171 ergänzt
nahtlose Doppelpuls-/Fusionsschleifen und ordnet vier RGB-Vorlagen in die
bestehenden Kategorien ein. Dieser neue Stand ist vorbereitet, nicht installiert
oder veröffentlicht. Persistenz und nativer Schreibweg bleiben unverändert.

Aktueller RGB-Nachweis 10.11.26 für `.169`: OpenRGB 1.1 aus Commit
`8e16de27858cf2be6af54a33ce003df74cb9fd3e`, MSI-Dirty-Zone-Patch und OHC Native
Engine 0.2 gemeinsam gegen System-Qt 6.11.2 gebaut. Unabhängige Controller-
Arbeiter und korrigierte Kanalpackung sind installiert; der Eigentümer bestätigt
Gehäuse-/GPU-Flüssigkeit, GPU-Farben und das unverändert wieder laufende LCD.
Das frühere AppImage ist nicht der aktuell laufende RGB-Binärstand.
Reale Fedora-Hardwareprüfung des nativen Pfads bleibt offen.

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
| Open Hardware Control by Frelidon | 3.4.29.181 INTERN in Entwicklung; zuletzt .180 Benutzer/System verifiziert · Hauptfenster-/UI-Sprachprüfung bestanden; Gesamtwächter, Paket-/Sicherungsnachweis und Installation noch ausstehend |
| OHC Designs & Spiele | Modul 1.1 · 15 Originalpaare, je Paar LCD-Zoom 50–200 Prozent und vier Matrix-Zeichenvarianten · begrenzte asynchrone Cache-Vorbereitung mit Absichts-/Verbergeabbruch, struktureller H.264-/Geometrie-/Dauerprüfung nur nach Anwenden · Layer 2 und bestehende Besitzer erhalten; keine Frame-Synchronisation oder neue Spieltelemetrie |
| OHC UI-Bereiche / Hilfe / Übersichtserkennung | Module 1.0 / 1.0 / 1.0 · gemeinsame Themenflächen/abbrechbare Scrollführung, vorhandene Hilfeinhalte, explizite lokale Inventur · Darstellung ist keine Telemetrie-/Schreibfreigabe |
| OHC Feature Lifecycle | Modul 1.0 · reine zentrale Darstellungsmetadaten; aktiviert/deaktiviert keine Funktion und verändert weder Einstellungen noch Hardwarebesitz |
| OHC Snapshot-Manager | Modul 1.0 · read-only Distribution-/Dateisystem-/Backend-/Snapper-/Btrfs-Erkennung · GameMode/Gamescope/Programmliste/KDE-Vollbild plus optionale Mehrkern-CPU-und-GPU-Hysterese · moderne gekoppelte Regler-/Zahlenkarten · manuelle Zeit-/Dauersperre · feste Snapper-Timer und begrenzte Btrfs-Discard-Werte ausschließlich über eigenen root-owned Polkit-Helfer · atomarer JSON-Metadatenexport · einzeln bestätigtes Löschen ab Snapshot 1 · kein Ein-Klick-Rollback und keine beliebigen Befehle/Pfade |
| OHC GPU-Steuerung | Modul 1.0 · LACT 0.10.1+ als optionale lokale API · gemeinsame responsive GPU-Seite mit Grafikkartenbild/Livekarten, OC und großer Lüfterkurve sowie Detailbereichen darunter; schmale Fenster stapeln die Bereiche · vollständige umbrochene Lüftertexte · fünf direkt ziehbare und zahlengekoppelte Lüfterpunkte · lokaler GPU-Bildimport/-reset · reiner Lüftertest garantiert ohne Grafiklast · Leistungslimit standardmäßig höchstens LACT-Werkswert, darüber explizite Freischaltung · Kurztest mit automatischer LACT-Rückstellung · nur bestätigte Werte dauerhaft · CoolerControl-GPU-Lüfter muss freigegeben sein · OpenRGB-RGB getrennt |
| OHC Prozesslaufzeit / LCD Runtime | Module 1.1 / 1.1 · bestätigte Sendefortschritte, Befehls-/Framefristen, isolierte Spielerkennung und privates Moduljournal |
| OHC Levita-Daemongesundheit | Modul 1.1 · reine Klassifizierung ausdrücklicher USB-Besitzerkonflikte und primärer Backendfehler · Ubuntu stoppt nur eigene Wiederholungen und hält gespeichertes Design unverändert · kein automatisches Beenden fremder Programme; Fedora-Rückstellung unverändert |
| OHC Laufzeitprotokoll / Absturzwiederherstellung | Module 1.0 / 1.0 · sichtbarer 60-Minuten-Ringpuffer · 30.000-Zeilen-/4-MiB-Hartgrenze · vollständige aktuelle/vorherige Sitzung · privates rotiertes 2-MiB-Fehlerlog · privater 2-MiB-Absturzring mit exakt fünf Minuten Wiederherstellung nach unvollständigem Ende · Fatal-Signal-Python-Stacks aller Threads · Diagnoseauszug nur nach ausdrücklicher Sammlung |
| OHC-Lokalisierung | Modul 1.0 · DE/EN/ES/FR atomar mit aktuell 2.584 gemeinsamen IDs · vollständiger UI-/Sprachwächter vor Freigabe verpflichtend |
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
| OHC Responsive Galerien / LCD-Medienmanager | Module 1.0 / 1.1 · tatsächliche Viewportbreite; eingebetteter Quellen-/Medienentwurf für Levita und Kraken mit Save/Cancel und bestehender Inventur · Quellen, Anzeigenamen und nicht-destruktive Ausblendungen · Originale unverändert |
| OHC Bereichs-Unterreiter | Modul 1.0 · wiederverwendbare browserähnliche Unterreiter · stabile Seiten-IDs · mehrere Leisten und Seitenleiste bleiben synchron · keine Hardwareabhängigkeit |
| OHC OpenLinkHub-Update | Modul 1.0 · offizieller fester GitHub-Release-Endpunkt · vorhandene DNF-/APT-Quellen oder streng erkannter Benutzerdienst · veröffentlichte SHA-256 · Backup/Rollback · ausdrückliche Bestätigung |
| OHC Wallpaper Engine for KDE | Modul 1.3 · CaptSilver v1.4 kompatibel · Pause/Fortsetzen/Weiter/Ton über Plasmas registriertes `/WallpaperEngine`-D-Bus-Objekt · DisplayMode 0/1/2 pro Bildschirm · lokalisierter Assistent mit bestätigter KDE-Hilfspaketprüfung · offizielle SHA256-verifizierte Fedora-RPM-Installation erst nach zwei Bestätigungen über Polkit/DNF · zentral zwischengespeicherter Workshop-Katalog und Vorschaubilder · Steam-Originale unverändert |
| OHC Profile Bundle | Modul 1.0 · vollständiger privater ZIP-Export/Import mit typisierten Einstellungen, Profilen, Gehäuse/RGB/PWM/Lüftermodellen/LED-Verläufen und Medien · Datei-Hintergrundprozess · Pfad-/SHA-Prüfung und Rückfallkopie · Bestätigung beim nächsten Start und erneute Hardwarefreigabe |
| OHC RGB-Effekt-Engine | Modul 1.15 · 14 eigene Algorithmen und 45 Vorlagen, zehn nur angehängt · gemeinsame Galerie-/Worker-/physische/GPU-Berechnung, native Schreibpfade und bestätigte LED-/ARGB-Zuordnungen erhalten · keine neue Hardwarefreigabe |
| OHC Hardware-Unterbauten | Modul 1.0 · persistente Automatik-/Direktauswahl · TRCC Linux für Levita · OHC Linux-hwmon für Mainboard-PWM · ausdrückliche Auswahl fällt bei Nichtverfügbarkeit nicht still zurück · kommende Adapter deaktiviert |
| OHC NCT6687-Treiber-/MOK-Assistent | Modul 1.1 · getrennte feste Abhängigkeitsbefehle für Ubuntu, Fedora und Arch Linux anhand `/etc/os-release` · Ubuntu-Aktualisierung/Installation getrennt · vorhandener fester Git-Checkout nur per `pull --ff-only` · gemeinsame Upstream-/DKMS-Schritte · MSI-X870-Optionen nur bei passender DMI-Erkennung · optionale per-user Polkit-Dauerfreigabe als fünfter Schritt · asynchroner read-only Secure-Boot-/MOK-/Modulstatus · kein Passwortzugriff, automatischer Neustart oder Secure-Boot-Umgehung |
| OHC Temperaturverlauf | Modul 1.2 · kompakter CPU/GPU/Kühlmittel-Verlauf plus eigene Kühlungs-Unterseite · gruppierte read-only Linux-hwmon-Sensoren · höchstens 24 Stunden/28.800 Messpunkte im RAM · lokales Datum/Uhrzeit · skalierbare Splitter · ausdrücklicher CSV-/JSON-Export frei gewählter Zeiträume/Sensoren · keine automatische Persistenz und kein Steuerungsbesitz |
| OHC Kühlungssicherheit | Modul 1.0 · modellbezogene Untergrenzen an Regler-, Profil-, Kurven- und finaler Schreibgrenze · Levita vorsichtig 50 % Pumpe/25 % Radiator, da Thermalright nur Maximaldrehzahlen veröffentlicht · vorhandene NZXT-Bereiche bleiben erhalten |
| OHC Kühlungszustand | Modul 1.0 · reine Startprofilrichtlinie trennt bekannte alte NZXT-Assistentenwünsche nur auf bestätigtem Ubuntu/Levita ohne bereites NZXT vom expliziten PC-Startprofil · Pendingwert und nutzereigene Kühlung bleiben erhalten · keine PWM-Schreibfreigabe; Fedora-/NZXT-Guard unverändert |
| OHC Mainboard-Fan-Modul | 3.4.29.80 · Linux hwmon/NCT6687 · freundliche eindeutige Headernamen ohne doppelte PWM-Angabe · kalibrierungspflichtige PWM-Kanäle · schrittweiser Zuordnungsassistent mit direktem nächsten Lüfter · vollständiges Zurücksetzen aller Gehäuselüfter-Zuordnungen bei erhaltenen Kurven · persistente und sichtbar blau markierte Automatik/Schnellprofile · Backend-Auswahl und asynchroner fail-closed Besitzerstatus · 100-%-Leistungs-Override · rückstellender 0-%-/10-s-Stopptest je Gehäuselüfter · sichere PWM/DC-Umschaltung nur über vorhandenes `pwmN_mode`, sonst BIOS-Erklärung · prozessgebundene Polkit-Helfersitzung · automatische Kurvenänderungen als gebündelte Zustands-/60-s-Heartbeat-Zeile · Fallback/Firmware-Rückgabe |
| OHC Thermalright-Levita-Modul | Anwendung 3.4.29.80 · nicht vorhandene Kühlmittelquelle wird weder angezeigt noch angeboten · lesbarer separater Sicherheitshinweis · Datenoberfläche Modul 1.7 · Daemongesundheit Modul 1.1 · automatische und manuelle streng validierte Wiederherstellung · sichtbarkeitsgebundene Galerien/Vorschauen · LCD-Medienmanager Modul 1.1 · Leistung/Spielerkennung Modul 1.1 mit Zehn-Sekunden-Abfrage · 15 LCD-FPS Standard, 60 nur experimentell · Abschaltwächter Modul 1.0 mit Stopp eines OHC-eigenen Daemons beim Ende · Display-Effekte Modul 1.11 · Display USB `87ad:70db` · ein TRCC-Daemon als einziger USB-Besitzer |
| Qt Multimedia | PySide6 QtMultimedia · lokaler H.264-Lesepfad ausschließlich für sichtbare Display-Effektvorschau |
| OpenRGB | Ubuntu: 1.1, lokal gegen System-Qt 6.11.2 gebaut, mit dokumentiertem MSI-761-Patch im root-owned privaten Backend-Verzeichnis `/usr/local/lib/open-hardware-control-backends/openrgb-1.1` · unsichtbarer verwalteter Prozess · Native Engine 0.2 oder paralleler SDK-Fallback · Ubuntu SDK 6, Fedora-Standard SDK 5 · kein mitgelieferter universeller Binärtreiber |
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
