# Open Hardware Control — verbindliches Modulregister

Entwicklung 11.11.26 (.179): Profil-Kühlungsbereitschaft 1.0 unter
`src/modules/profile_cooling/v1_0/` ergänzt `restore.py` für höchstens zehn Sekunden
Warten auf frische Sensordaten. Keine Änderung an ProcessRuntime 1.1s 2,5-s-Frische,
Timeout oder Hardwarebesitz. Hauptorchestrator verwirft alte Profil-/Kühlaufträge;
Bedienungsänderung/Shutdown/Frist/fehlendes Gerät verhindern spätes Anwenden.
Laufzeitprotokoll 1.0 ergänzt `error_capture.py` und `error_bridge.py`: begrenzte
thread-sichere Python-/Thread-/Unraisable-/Qt-Erfassung, zentraler Privatlog-Sink
in `src/privacy_logging.py` und GUI-seitige Übernahme durch `src/log_view_support.py`
ohne Rückkopplung oder doppeltes Fehlerdateischreiben. Hauptfenster verbindet
und löst Hooks explizit. Bestehende Sys-/Native-Crash-Protokolle bleiben erhalten.
Lokalisierung 1.0 ergänzt `profile_cooling_messages.py`, atomar DE/EN/ES/FR:
2.507 gemeinsame IDs. Keine Firmware-/PWM-/RGB-/LCD-Transportänderung.
ProcessRuntime 1.1-Diagnose bewahrt die bekannte APP_VERSION als technische
Buildangabe; sie wird nicht mehr fälschlich als IPv4 in [IP] umgewandelt.
Private Detailwerte bleiben weiterhin redigiert. Die gemeinsame Fehlerdatei
serialisiert Rotation und Schreiben über einen reentranten Thread-Lock.

Entwicklung 11.11.26 (.178): Profil-Arbeitsbereich 1.0 unter
`src/modules/profiles_workspace/v1_0/` trennt `model.py`, `cards.py` und `page.py`.
Die unsichtbare elterngebundene Kompatibilitätstabelle bewahrt bestehende
Profil-ID-/CRUD-/Bundle-Verträge; der Haupteinstieg delegiert nur den Aufbau.
Programm-Hintergründe 1.0 unter `src/modules/app_backgrounds/v1_0/` trennt
`catalog.py`, `media.py` und `profile.py`: sechs lokale Videos, ein sichtbarkeits-
gebundener Decoder, CPU-RGB32-Komposition und temporärer angewendeter Profilzustand.
LCD-Medium hat Vorrang vor RGB; Auswahl/Bearbeitung erzeugt keinen Aktivzustand.
`tools/render_app_backgrounds.py` erzeugt fünf originale periodische Videostudien;
`tools/render_code_rain.py` erzeugt additive +30-/+50-/+100-Prozent-Varianten.
Display-Effekte 1.11 bewahrt bisherige Design-/Varianten-IDs, wählt bei neuer
Matrix-Auswahl +30 Prozent vor. Lokalisierung 1.0 ergänzt
`profile_background_messages.py` atomar in DE/EN/ES/FR: 2.501 gemeinsame IDs.
Globale Hintergrundauswahl verwendet stabile Komboboxdaten auch nach Sprachwechsel.
UI-Themes 1.0 aktualisiert Karten-/Symbolpaletten nach dem Themenwechsel;
der bestehende Shutdown-Orchestrator gibt den Hintergrunddecoder ausdrücklich frei.
Backend-/Schreibbesitz und Fedora-/Ubuntu-Installationspfade bleiben unverändert.

Entwicklung 11.11.26 (.177): Neues Modul Designs & Spiele 1.0 unter
`src/modules/design_hub/v1_0/` enthält `catalog.py`, `rain.py`, `controller.py`,
`page.py`, `preview.py`, `games.py` und `navigation.py`. Fünf stabile Designpaare
verbinden bestehende RGB-Vorlagen und LCD-Assets. Matrix Code Rain ergänzt
additiv den extensiblen RGB-Effekt-/Vorlagenkatalog in `src/rgb_effects.py` und
den unveränderten Display-Effekte-1.11-Katalogvertrag; bestehende IDs/Indizes
bleiben erhalten. `tools/render_code_rain.py` erzeugt den originalen 1600×720-
Hintergrund ohne Demo-Messwerte, mit periodisch überblendeten Glyphen.
Navigationseinstellungen 1.0/Temperatur-Navigationsmixin hängen Spiele,
Designpaare und die unveränderte Designautomatik 1.0 unter einen neuen Bereich;
eigene Reihenfolgen und bisherige Sichtbarkeitsschlüssel bleiben erhalten.
Lokalisierung 1.0 ergänzt `design_hub_messages.py` in allen vier Sprachdateien;
Feature-Reifegrade 1.0 kennzeichnet den neuen Bereich als Alpha. Artwork ergänzt
eigene Designs-/Spielesymbole. Keine Bildschirmaufnahme, Telemetrie oder neue
Hardwarebesitz-/Schreibschnittstelle. Vollständiger Wächter: 1.609 Tests und fünf Untertests bestanden, vier Sprachen und 448 echte Zeigergesten; 424 Laufzeitquellen und 2.468 Sprach-IDs. Matrix-MP4 vollständig dekodiert und periodisch geprüft; helle/dunkle Oberfläche geprüft. Alle sechs Pakete, beide .176/.177-INTERN-Sicherungen und 424 identische Quellen in ZIP/DEB/RPM geprüft. Benutzer- und Systeminstallation .177 abgeschlossen (DPKG 3.4.29.177~intern2); beide installierten Quellbäume und Matrix-Assets bytegleich. Native RGB-Arbeiter ohne gemeldete Fehler und gespeicherte Levita-Komposition nach Start bestätigt. Keine optische Matrix-/Fedora-Liveprüfung oder GitHub-Veröffentlichung.


Veröffentlichung 11.11.26 (.176): Auf ausdrücklichen Eigentümerauftrag wird
nur der Build-Kanal von INTERN auf STABLE angehoben. Keine Modulschnittstelle,
Hardwarefunktion oder Einstellung wird geändert; Versions-/Fenstertiteltests
prüfen den STABLE-Kanal. Die laufende lokale INTERN-Installation bleibt erhalten.
Vollständige STABLE-Prüfung: 1.587 Tests und fünf Untertests bestanden.
Alle sechs Pakete, 414 Quellen in ZIP/DEB/RPM und beide aufbewahrten
.176-INTERN/STABLE-Sicherungen geprüft. Öffentlich als Latest veröffentlicht:
`v3.4.29.176` zeigt auf `34c64d3`; alle sechs Paket-Hashes und heruntergeladene
öffentliche SHA256SUMS stimmen. Wegen DNS-Ausfall der Ubuntu-Paketserver im
GitHub-Runner erfolgte der Upload der lokal geprüften Pakete über die Release-
Oberfläche; kein bestandener entfernter CI-Lauf wird behauptet. Die originale
lokale Liste bleibt SHA256SUMS.local; öffentliche Dateinamen stehen in
SHA256SUMS. Beide Sicherungen erneut geprüft (INTERN acht, STABLE neun Hashes).

Entwicklung 11.11.26 (.176): Neues Modul Lüfterzuordnung 1.0 unter
`src/modules/fan_mapping/v1_0/` enthält `wizard.py`, `runtime.py` und
`lighting.py`. Der vorhandene Assistent wird aus dem Hauptfenster ausgelagert;
explizit nicht angeschlossene Kanäle behalten Kurven und werden kompakt unter
Ungenutzt angezeigt. 120-s-Stopptests nutzen eine erneuerte kurze Treiberlease,
stellen bei Weiter/Abbruch/Kanalwechsel sämtliche Kontrastzustände zurück und
bleiben ohne Watchdog gesperrt. RGB-Weißhilfe nutzt die bestehende Preview-
Sperre und eine bestätigte native STOP-Übergabe. Temperaturverlauf 1.2 erhält
Auswahl per Ziehen und kompakte Messwertkarten; vorhandener RAM-Puffer,
Sensor-IDs, gespeicherte Auswahl und Berichte bleiben unverändert.
`selection.py` und `readings.py` ergänzen Icons, begrenzte ID-MIME-Daten,
Auswahl per Ziehen/Knopf/Checkbox und wiederverwendete Messwertkarten. Resizable
Sensorpanels nutzen `keepViewportHeight`; die versteckte Kompatibilitätstabelle
bleibt erhalten und besitzt einen Elterncontainer. Lokalisierung 1.0 ergänzt
`fan_history_messages.py`; DE/EN/ES/FR werden gemeinsam geladen, 2.444 IDs.
Synthetische hwmon-Tests decken Teilfehler, fehlende Lease, Abbruch, Weiter,
Shutdown und verlorenen Zielkanal ab; echte Qt-Prüfungen decken Drag-Auswahl,
Einheiten, leere Auswahl und Geometrie ab. Vollständiger Wächter: 1.587 Tests
und fünf Untertests bestanden; vier Sprachen, 414 Python-Quellen, Datenschutz,
Sicherheit und Modulbudgets geprüft. Helle/dunkle Beispieldarstellung geprüft.
Alle sechs Artefakte und beide .175/.176-Sicherungen geprüft; ZIP/DEB/RPM
enthalten 414 identische Python-Quellen. Benutzer- und Systeminstallation .176
abgeschlossen (DPKG 3.4.29.176~intern2); beide installierten Quellbäume bytegleich.
Einstellungen vor Start erhalten; Profile und Plugin auch nach Start identisch.
Fünf native Arbeiter ohne gemeldete Fehler, Sapphire External Control und
wiederhergestelltes Levita-Design bestätigt. Kein physischer Stopptest oder
absichtlicher Prozessabsturz; GitHub bleibt beim bisherigen .175-Checkpoint.

Entwicklung 11.11.26 (.175): Hardwareprüfung 1.0 ergänzt `device_catalog.py`
für 41 Modell-/Backend-Einträge mit Geräteart, Hersteller und getrennten,
geprüften Hersteller-/Produktlinks. `supported_devices.py` filtert acht
Kategorien und Hersteller; fehlende Produktziele erzeugen keinen Knopf.
GPU-Namen aus GPU-Profile 1.0 sind ausdrücklich nur Modellprofile mit
Backend-Voraussetzung; bisherige Hardwaregrenzen bleiben erhalten.
Navigationseinstellungen 1.0 ergänzt `sidebar.py:NavigationTree`; der
Orchestrator verbindet `pageRequested` statt des rohen currentItemChanged.
Seitenwechsel erfolgt nach dem vollständigen Mausklick, bevor Untermenüs
Zeilen verschieben können. Tastatur, programmatische Auswahl und vorhandenes
Drag-and-drop der Anpassung bleiben erhalten. Lokalisierung 1.0 ergänzt
`device_catalog_messages.py`, gemeinsam in DE/EN/ES/FR geladen: 2.381 IDs.
Regressionen: `tests/test_catalog_navigation_3429175.py` und echte Gesten in
der vollständigen viersprachigen Oberfläche: 220 echte Zeigergesten bestanden.
1.556 Tests und fünf Untertests bestanden; 406 Python-Laufzeitquellen.
Isolierte helle/dunkle Katalogdarstellung geprüft. Alle sechs Artefakte und
beide .174/.175-Sicherungen geprüft; ZIP/DEB/RPM mit 406 Quellen identisch.
Benutzerinstallation gestartet, vor Start alle Einstellungs-/Profil-/Plugin-
Hashes erhalten. Native Engine: fünf Arbeiter, null gemeldete Fehler;
Sapphire External Control und gespeichertes Levita-Design aktiv. Nach bestätigter
Linux-Abfrage ist auch die Systemkopie .175 (DPKG 3.4.29.175~intern2); beide
installierten Bäume entsprechen allen 406 Python-Quellen bytegenau. Laufende
Benutzerinstanz und fünf native Arbeiter ohne gemeldete Fehler bestätigt.
Interner GitHub-Upload
auf `codex/3.4.29-intern` bestätigt (Quellcommit `5fd7989`); kein öffentlicher
Release-Tag und keine Änderung des Standardzweigs.

**Stand:** 11.11.26
**Anwendung:** 3.4.29.179 INTERN

Lokaler Stand 11.11.26: .174-Benutzerinstallation mit allen 403 Python-Quellen
verifiziert und gestartet. Fünf native RGB-Arbeiter ohne gemeldete Fehler,
Sapphire External Control und gespeichertes Levita-Design aktiv. Einstellungen,
Profile und Plugin vor Neustart bytegleich. Nach bestätigter Linux-Abfrage ist
auch die Systemkopie .174 (DPKG 3.4.29.174~intern2); beide installierten Bäume
entsprechen allen 403 Python-Quellen. OpenLinkHub-Benutzerdienst aktiv;
keine optionale DPI-Regel und kein Vorstart-Drop-in automatisch angelegt.
Beide .173/.174-Versionssicherungen und ZIP/DEB/RPM-Inhalte sind geprüft.

Standard-DPI 11.11.26 (.174): OpenLinkHub Update 1.0 ergänzt
`startup_defaults.py` und `before_start.py`. Die vom Benutzer ausdrücklich
gewählte Standardstufe wird unabhängig von OpenLinkHubs aktiver `Profile`-Stufe
privat je Mausprofil gespeichert. Ein optionaler fester Benutzer-ExecStartPre
stellt sie vor dem USB-Besitzerstart wieder her; ein fehlender OHC-Helfer
blockiert den Dienst nicht. Keine Systemrechte oder direkten USB-Schreibwege.
Die native Vorgabe ist wieder auswählbar; Rollback umfasst Profil, Regel und
Drop-in. Sprachwechsel erneuert den einen dynamischen Vorgabetext; 2.324 IDs.
Neue Regressionen prüfen DPI-Tastendruck/Neustart, getrennte Profile, Rücksetzen,
inaktive/fremde/unsichere Dateien und fremde Drop-ins. .174: Voller Wächter mit 1.544 Tests und fünf Untertests bestanden; der
echte systemd-Parser akzeptiert den optionalen Befehl. 403 Python-Laufzeitquellen.

Nachkontrolle 11.11.26 (.173): OpenLinkHub Update 1.0 ergänzt
`mouse_ui.py:refresh_mouse_icons`; UI-Themes 1.0 erneuert die eigenen
Haussymbole beim Paletten-/Akzentwechsel. Der echte Qt-Sprach-/Thementest
prüft die erneuerte Icon-Generation. Alle .172-Verträge bleiben erhalten;
.173 ist der neue abschließende interne Kandidat. Voller Wächter: 1.529 Tests
und fünf Untertests bestanden. Beide .172-Installationen entsprechen 401
Python-Quellen; Profile und natives Plugin sind bytegleich erhalten.

Abschlussprüfung 11.11.26 (.172): Vollständiger Wächter mit 1.529 Tests und
fünf Untertests bestanden. Neun Geräte-/Backend-Karten, vier Sprachen und
erhaltene helle/dunkle Paletten sowie native RGB-/Inline-Geometrie-Prüfungen
sind abgedeckt. Bau und lokale Installation folgen; kein GitHub-Upload.

Entwicklung 11.11.26 (.172, laufender Umbau): Navigationseinstellungen 1.0
enthält `artwork.py` mit gerundeter Originalgrafik und originalen, palettenabhängigen
Kategoriesymbolen. Hardwareprüfung 1.0 ergänzt `navigation.py` und
`supported_devices.py` für zwei feste Unterpunkte, übersetzte Beschreibungen,
Herstellerlinks und klare lokale/Backend-Unterstützungsgrenzen. UI-Leistung 1.1
ergänzt `adaptive_views.py` und `compact_panels.py`; späte Formen übernehmen
die ereignisgesteuerte Höhenanpassung ohne Polling. PC-Gehäuseprofile 1.5 ergänzt
`component_summary.py`, teilt vorhandene Widgets in drei Ansichten auf und erhält
Inline-Editor, Profile und animiertes Diagramm. RGB Studio 1.15 ergänzt
`generic_fans.py`: eigene Zeichnungen für 21 deklarierte LED-Zahlen; Auswahl ist
nur ein Entwurf. OpenLinkHub Update 1.0 extrahiert `device_ui.py` und ergänzt
`mouse_ui.py`, `mouse_profiles.py`, `stage_integrity.py`: DPI-/Profilmetadaten aus
.9.4-Detailabfragen, getrennte Maus-/Tabellengeometrie, Startstufe mit Backup und
Dienststopp sowie offizielle benannte Profilaktionen. UI-Themes 1.0 aktualisiert
Kategoriesymbole bei Palettenwechsel; Hintergrund-/Levita-/RGB-Transport bleiben
bestehen. Lokalisierung 1.0 ergänzt `redesign_messages.py` gemeinsam für alle vier
Sprachdateien auf 2.324 IDs. Hauptorchestrator, Temperatur-Navigation, Setup-
Funktionsmodell, GPU-Prüfaktion und Branding verbinden diese vorhandenen Module.
Der reale Benutzer-Backendwechsel .9.2→.9.4 ist mit vorherigem privatem Backup
und gesunder Loopback-API bestätigt. Gezielte Prüfungen laufen; noch kein
.172-Paket oder GitHub-Upload.

Entwicklung 11.11.26 (laufender Umbau): OpenLinkHub Update 1.0 ergänzt
`health.py` für eine begrenzte Start-/PID-/Loopback-API-Prüfung. Der getrennte
Apply-Helfer stoppt bei Fehlern den neuen Dienst vor der Rückkehr zum Backup;
auch ein fehlgeschlagener erster Verzeichniswechsel liegt im Recovery-Pfad.
UI-Umbau und nächste Versionspaketierung sind noch in Arbeit.

Entwicklung 11.11.26 (.171): OpenRGB Studio 1.15 und die reine Effektengine
`src/rgb_effects.py` schließen harte Schleifengrenzen bei Doppelpuls und Fusion.
Die RGB-Galerie ordnet vier Vorlagen unter gleichen stabilen Indizes in
Räumlich/Energie/Bewegung ein; die redundante Kategorie OHC Originale entfällt
nur dort. OpenRGB-Originale, LCD-Medien, Favoriten und Transport bleiben gleich.
Je ein neuer Caption-Eintrag in allen vier Sprachdateien deckt den bisherigen
Galerie-Accessible-Name ab; 2.259 gemeinsame IDs. Hardwarefreie Vollkatalog-
Regressionen prüfen Galerie-, physische, Worker- und GPU-Pfade. Voller Wächter:
1.514 Tests und fünf Untertests einschließlich vier Sprachen bestanden. .170 ist nach
Rechnerneustart flüssig bestätigt; .171 bleibt ohne Installation/Veröffentlichung.

Entwicklung 11.11.26: Navigationseinstellungen 1.0 behalten alle 17 Statuskarten,
zeigen für Einstellungen aber keinen Ausschalter. Der Hauptorchestrator filtert
alte Ausblendungen und schützt beide Editierwege. UI-Leistung 1.1 trennt
`page_transition.py` für echte Inhaltsseitenübergänge (vier Stile,
220/380/550 ms) vom Controller; Navigation bleibt ruhig. RGB Studio 1.15 bietet
zwölf Vorschläge und trennt `native_stream.py` für bevorzugte native Übertragung,
begrenzte Wiederholungen und bestätigte STOP-Barriere vor SDK-Fallback.
`native_plugin.py` schließt fehlgeschlagene Verbindungsversuche und validiert
Antwortobjekte. `content_ui_messages.py` aktualisiert alle vier Kataloge unter
gleichen IDs; fünf neue Quellen ergeben 2.258 Einträge. Hostdiagnose bestätigt
Autostart auf installierter .168/OpenRGB 1.0 statt des vorbereiteten nativen
.169/.170-Stands. Lokale Installation ist inzwischen ausdrücklich freigegeben; GitHub bleibt bis
zur Sicht-/Neustartbestätigung zurückgestellt.
Anwendungsaktivierung 1.0 ergänzt `autostart.py`; `packaging/install.sh`
aktualisiert vorhandene erkannte OHC-Autostarts auf den gerade erneuerten
Benutzerstarter. Fehlende/deaktivierte Einträge, eigene Wrapper, Symlinks
und Zusatzargumente bleiben erhalten. Separate Ubuntu-/Fedora-Fixtures prüfen
den echten begrenzten Helfer ohne Hostinstallation.

Installationsnachweis 11.11.26: Sechs Artefakte gebaut, .169/.170-Backups mit
je acht Prüfsummen bestätigt. APT und Benutzerinstaller installieren .170;
beide Kopien entsprechen 388 Python-Quellen. Bestehender Autostart zeigt auf
den aktualisierten Benutzerstarter. Tatsächliches OpenRGB 1.1 mit fünf nativen
Arbeitern, null gemeldeten Fehlern und bestätigtem Sapphire External Control.
Optische Prüfung und Eigentümer-Neustart stehen aus; kein GitHub-Upload.

Nach Tag-Veröffentlichung 10.11.26: Reiner Testfix im Hauptzweig ergänzt
`Callable` im isolierten AST-Namensraum von `test_rgb_stream_reclaim_342990.py`.
Explizite Typauflösung prüft denselben Fehler auch unter Python 3.14. Keine
Produktionsquelle, Hardwarefunktion oder Verschiebung des unveränderten Tags.

Release 10.11.26: Anwendung 3.4.29.169 dokumentiert den vom Eigentümer
bestätigten RGB-/GPU-/LCD-Funktionsstand. `docs/hardware/NATIVE_RGB_SETUP.md`
trennt das plattformneutrale OHC-Paket vom optionalen Qt-6-/OpenRGB-1.1-Bau,
dem MSI-Patch und privaten Wiederherstellungsdaten. Native C++-Farbtests
erhalten ihre explizite JSON-/Compiler-Abhängigkeit in beiden GitHub-Workflows;
Versionsanker, DE/EN-README, Installations-/Entwickler-/Quellanleitung und
Release Notes sind synchronisiert. Hardwarepfade bleiben unverändert.
`ram_bank.py:RgbRamBankMixin` übernimmt den vorhandenen gemeinsamen RAM-
Inspektionsdialog unverändert aus dem Hauptfenster, damit dessen feste
Größengrenze erhalten bleibt. Die öffentliche Methoden-/Persistenz-/Schreib-
Schnittstelle bleibt gleich; eigene Regressionen prüfen serielle Inspektion
und Fremdbesitzsperren. Der vollständige Qt-Sprachtest bleibt verpflichtend.
Vollständiger lokaler Release-Wächter: 1.347 Tests und fünf Untertests bestanden,
einschließlich echter viersprachiger Qt-UI, Sicherheits-/Datenschutzprüfung,
nativer C++-Fixtures und unveränderter Modul-/Größengrenzen. Paket-/Upload-
Nachweise sind separat nach dem Bau kontrolliert: ZIP-Manifeste, nativer
Quell-/Patchbestand, DEB-/RPM-Laufzeitparität und Root-Rechte sowie vollständiges
Git-Bundle bestanden. .168/.169-Sicherungen sind SHA256-bestätigt; nur .167
wurde regulär rotiert. Private Funktionssicherung bleibt separat erhalten.
Fedora-Liveprüfung offen; keine Veränderung der bestätigten laufenden Installation.

Entwicklung 10.11.26: RGB Studio 1.15 priorisiert den exakten OHC-Stream für
jedes ausgewählte Direct-Gerät; native Hardwareeffekte bleiben auf Geräte ohne
vollständigen Softwareframe begrenzt. `src/native/openrgb/LatestFrameWorker.h`
besitzt je Controller einen persistenten 60-Hz-Arbeiter mit einem neuesten
wartenden Frame. `OHCNativePlugin.cpp` validiert Identität und vollständige
LED-Zahlen, liefert getrennte Queue-/API-Statistiken und leert laufende Writes
vor STOPP. `native_plugin.py` bestätigt erst nach API-Übergabe aller Geräte der
aktuellen Generation. `tools/openrgb/msi-761-dirty-zones.patch` dokumentiert
die begrenzte OpenRGB-Korrektur für unveränderte MSI-Zonen. Reale USB-Zeitmessung:
Airgoo steigt von 3,83 auf 58,52 vollständige Frames/s; MSI-Feature-Reports
benötigen hier einzeln rund 93 ms. Nach Installation der Dirty-Zone-Korrektur
erreichen einzelne geänderte MSI-Zonen rund 10,64 vollständige Frames/s.
`src/native/openrgb/ColorCodec.h` validiert Hex-/Array-Farben und packt die
Kanäle ausdrücklich nach 0x00BBGGRR, ohne das fehleranfällige OpenRGB-Makro
mit Bitoperator-Ausdrücken aufzurufen. Der kompilierte Regressionstest
`tests/fixtures/native_color_codec.cpp` prüft Grundfarben, Verläufe und Grenzen.
Der Eigentümer bestätigt flüssige Gehäuse-/GPU-Bewegung, korrekte GPU-Farben
und das nach normalem Neustart wieder laufende unveränderte LCD-Design.
Eine Sapphire-GPU mit externem Eingang bleibt während eines ausgewählten
Direct-Signals auf External Control; ungültige explizite Routen bleiben
gesperrt. Die verwaltete System-Qt-Engine verwendet das geprüfte Offscreen-QPA.

Entwicklung 09.11.26: RGB Studio 1.15 hält Mehrgeräte-Animationen auf der
vollständigen monotonen Zeitbasis. Der SDK-Arbeiter hält eine geordnete
Loopback-Verbindung je Controller und schreibt verschiedene Controller
parallel; der Satz wartet damit auf den langsamsten statt auf die Summe aller
Bestätigungen. GPU-/Halterungsstreifen übernehmen die Galerie-Umlaufdauer.
`shutdown_lighting.py` ergänzt die Abschlussbeleuchtung. Beim
echten Programmende wird nach Effektstopp und vor Besitzfreigabe Weiß, eine
gewählte Einzelfarbe oder ein tatsächlich gemeldeter nativer Rainbow-Modus auf
ausgewählte konfliktfreie Geräte geschrieben. Tray-Verbergen und Neustart
bleiben wirkungslos. Abschlusslicht und Design-Tempo ergänzen zwanzig neue
Sprachquellen in allen Katalogen auf 2.248 Einträge; physische Sichtprüfung
bleibt offen.

Entwicklung 05.11.26: Anwendung 3.4.29.168 trennt echte, deterministische
Scroll-Viewport-Sichtbarkeit von der vollständigen Levita-UI-Integration. Diese
prüft weiterhin Medienwahl, Pause/Fortsetzung, Bestätigungsfallback und vier
Sprachen ohne virtuelle Desktopannahme. Ein später Snapshot-Prozesscallback
greift nicht mehr auf einen bereits zerstörten Qt-Eigentümer zu. Produktive
Geräteerkennung, Oberfläche, Einstellungen und Hardwarepfade bleiben unverändert.

Entwicklung 04.11.26: Feature Lifecycle 1.0 hält unabhängige semantische
Feature-Versionen und die Reifegrade Alpha, Beta, Release Candidate und Stabil
als reine Darstellungsmetadaten. Funktionen-&-Bereiche-Karten,
Navigationsverwaltung lesen dieselbe Registry; weder
Featureaktivierung noch Einstellungen, Hardwarebesitz oder Schreibpfade werden
verändert. Vier neue Sprachquellen ergänzen alle Kataloge auf 2.228 Einträge.
Der öffentliche Designkatalog enthält nur projekt-eigene OHC-Medien; Import,
Editor, Vorschau, Gehäuse-Lüfteranimation und Hardwareübergabe bleiben erhalten.

Entwicklung 20.10.26: Programme 1.0 trennt begrenzte Desktop-Inventur,
validierte Installationsprofile und Qt-Seite. Der Dateiscan läuft nicht im
Qt-Hauptthread; er führt keine Desktopbefehle, Paketmanager oder Netzwerkanfragen
aus. Grundordner und maximal 300 Profile werden über die vorhandenen Einstellungen
gespeichert. Der ausdrückliche GitHub-Weg prüft Release-Metadaten, lädt begrenzt
alle Assets und beide Source-Archive, erzeugt SHA-256-Metadaten und veröffentlicht
einen neuen Versionsordner atomar. `install_plan.py` erstellt ausschließlich
validierte Argumentlisten für benutzerbezogenes Flatpak, Polkit/Snap oder eine
lokale AppImage-Modusänderung; Systempakete bleiben ohne bestätigte Quelle aus.
Profile speichern GitHub-Repository und Source-Version getrennt vom Flatpak-
Branch/Snap-Channel. Sprach-IDs 2825–2893 ergänzen alle vier Kataloge auf 2.224
Quellen.

Entwicklung 06.10.26: PC-Gehäuseprofile 1.5 und RGB Studio 1.15 korrigieren
die LED-Entwurfsbedienung, räumliche Richtung und animierte RGB-Lüftervorschau.
`led_topology_editor.py` hält optionale Entwurfsfelder auch vor einem gespeicherten
Pfad bedienbar; nur ausdrückliche Nutzeränderungen aktivieren dessen Commit,
Öffnen/Anzahl-/Testindexänderung erfinden keinen LED-Weg. Qt-Polish/Reparent,
Maus/Tastatur, Speichern/Abbrechen und vier Sprachen werden tatsächlich geprüft.
`spatial_layout.py` erhält ungespeicherte Auswahl bei normaler Aktualisierung,
zeigt geänderte Profilwerte und meldet einen fehlenden LED-Weg ausdrücklich;
Sprach-ID 2824 ergänzt alle vier Kataloge auf 2.154 Quellen.
`render_plan.py` und `gpu_lighting.py` projizieren ausdrücklich räumliche
Anschlusswege auch bei global lokalem Modus; `led_topology.py` und
`gpu_strip_sampling.py` korrigieren sichtbare Wave-Richtung und lokale
Effektumkehr ohne Änderung der physischen Reihenfolge. `case_animation.py`
und `diagram.py` verwenden denselben bestätigten Effektzeitpunkt; das reine
`fan_preview.py` zeichnet begrenzte schematische RGB-Segmente aus bestehenden
Farben, keine Rotor-/Drehzahlsimulation. Keine neue Transportverbindung,
LED-/PWM-Zuordnung, Detektorerkennung oder Hardwarefreigabe. Gezielte Tests:
`test_led_topology_draft_interaction_3429156.py`,
`test_spatial_flow_editor_3429156.py`, `test_spatial_direction_pipeline_3429156.py`
und `test_case_fan_animation_3429156.py`; Fedora und Ubuntu getrennte Fixtures,
echter Fedora-Hardwaretest weiterhin offen. Der volle Release-Wächter besteht
mit 1.301 Tests und fünf Untertests. Echte DEB-/RPM-Quellen, Root-Verzeichnisse,
Helfermodi, RPM-Digests und unveränderte Fedora-Abhängigkeiten unabhängig geprüft;
beide externen `.155`/`.156`-Sicherungen SHA256-bestätigt, ältere `.154` regulär
rotiert. Lokale Ubuntu-Installation nach Eigentümerbestätigung abgeschlossen:
DPKG und 365 Python-Quellen identisch, Profile vor Neustart bytegleich, enge
Lüfter-/Metadatenfreigaben nichtinteraktiv bestätigt. Automatischer RGB-/LCD-
Start und wiederholter Videofortschritt protokolliert; optische Kontrolle und
echter Fedora-Hardwaretest bleiben offen. Abschlussnachweis ist nachgebaut
dokumentiert, Paketsnapshots behalten den Vorinstallationsbericht.

Entwicklung 06.10.26: Kühlungszustand 1.0 ergänzt die reine
`startup_policy.py:pending_setup_blocks_profile_start`-Richtlinie. Die beiden
Profilstart-/LCD-Payload-Guards im Hauptfenster unterscheiden bekannte alte
NZXT-Assistentenwünsche von einem ausdrücklich gewählten PC-Startprofil nur
auf bestätigtem Ubuntu/Levita ohne bereites NZXT. Pendingwert, User-Kühlung,
Kalibrierung und andere Distributionen bleiben erhalten; Regressionen in
`tests/test_profile_startup_policy_3429155.py`.
Levita-Daemongesundheit 1.1 ergänzt in `model.py` die reine Klassifizierung
`is_usb_owner_conflict` und die primäre Fehlerauswahl `backend_failure_detail`.
Die Ubuntu-Orchestrierung in `src/thermalright_display_ui.py` stoppt eigene
Apply-/Startup-/Ticker-Wiederholungen bei ausdrücklicher USB-Belegung, ohne
fremde Prozesse, gespeicherte Designs oder Fedora-Recovery zu verändern.
`tests/test_lcd_usb_owner_conflict_3429155.py` prüft Besitz-/Recoverygrenzen
und dynamische Statusübersetzung in vier Sprachen. Die erfolgreiche LCD-
Statusabfrage bindet die kanonische `THERMALRIGHT_DEVICE_KEY` aus dem bestehenden
Display-Adapter ausdrücklich ein; `tests/test_lcd_health_module_globals_3429155.py`
prüft echte Qt-Klassenmethoden mit realen Modulglobals für statische und animierte
gesunde Antworten auf Ubuntu und Fedora, ohne Konstanten per AST einzuspritzen.
Sprach-ID 2823 liegt im
gemeinsamen `next_version_messages.py`; alle vier Kataloge besitzen 2.153
Nachrichtenquellen. Verbindliche getrennte Fedora-/Ubuntu-Prüfung ist in
`docs/ai/AGENTS.md` und `AI_DEVELOPMENT_GUIDE.md` festgehalten. `.155` ist vor
dem vollständigen Release-Gate/Paket-/Installationsnachweis entwickelt worden.
Abschlussnachweis: 1.132 Tests plus fünf Untertests, tatsächliche DEB-/RPM-
Dateien und sichere Verzeichnisrechte sowie beide `.154`/`.155`-Sicherungen
geprüft. Die endgültige Ubuntu-Installation und ihr RGB/LCD-Start sind bestätigt;
optische Kontrolle und echter Fedora-Hardwaretest bleiben getrennt offen.

Release-Paketierung 1.0 normalisiert für `.155` alle tatsächlichen Verzeichnisse
ausschließlich im isolierten `install_runtime_tree`-Stage einschließlich dessen
Wurzel auf 0755. Gruppenbeschreibbare Build-umask-/Copytree-Modi gelangen damit
nicht als Helper-Vorfahren in frische DEB-Installationen; Symlinkziele, Stage-Eltern,
Quellbaum und bestehende Hostverzeichnisse bleiben unangetastet. Dateiinhalt,
Helper-/Policy-Modi und RPM-Abhängigkeiten bleiben erhalten. Der zusätzliche
umask-002-Vertrag in `tests/test_polkit_package_permissions_3429154.py` führt
den echten vollständigen Stage-Aufbau mit isolierten Quellen aus.

Entwicklung 06.10.26: Ubuntu-OpenRGB 1.0 verwendet ausschließlich im
vertrauenswürdig ausgewählten Backend `--list-detailed`; alte/Fedora-Befehle
bleiben unverändert. Reine Namenslisten ohne Gerätetyp werden vor jeder
Identitäts-/Profiländerung verworfen. Der Adapter verwendet zusätzlich
`backend_updates/v1_0/executables.py:preferred_backend_version`.
RGB Studio 1.15 und PC-Gehäuseprofile 1.5 erlauben bestätigte externe
GPU-Blockrouten ohne nativen GPU-Detektor; Gruppe und Strip-Renderer folgen
dem tatsächlichen Direct-Controller/Anschluss. Tests:
`tests/test_openrgb_inventory_3429154.py` und
`tests/test_external_gpu_argb_3429153.py`.

TRCC Backend 1.0 ergänzt `runtime.py` und `launcher.py` für den getrennten
Ubuntu-Kindprozess. Nur die exakte RAM-DMI-Abfrage erreicht den neuen festen
`src/ohc_trcc_dmi_helper.py`; dessen argumentfreier read-only Vertrag und die
dedizierte `packaging/io.github.Frelidon.OpenHardwareControl.dmi.policy` geben
keine allgemeine Systemprogrammberechtigung. Kennungen werden entfernt,
weitere automatische Metadatenabfragen bleiben unprivilegiert. Die
Paketierung installiert den root-owned Helfer getrennt vom unveränderten
TRCC-Paket; unabhängige Programme und Fedora-Kommandos bleiben unangetastet.
Regressionsvertrag: `tests/test_trcc_startup_permissions_3429154.py`, inklusive
Argument-/Dateischreibverweigerung, Kennungsfilter und echtem TRCC-RAM-Parser.
Release-Paketierung 1.0 setzt die neue DMI-Policy im gemeinsamen DEB-/RPM-Stage
ausdrücklich auf 0644, unabhängig vom Checkout-Modus. Der zusätzliche Vertrag
`tests/test_polkit_package_permissions_3429154.py` prüft fünf Quellmodi,
unveränderte Inhalte/Quelldateirechte und die gemeinsame Builder-Anbindung.
`scripts/build_rpm_fallback.py` führt die bereits im normalen RPM-Spec
registrierten DMI-/Snapshot-Systemhelfer und Policies ebenfalls im expliziten
Payload-Manifest. `tests/test_rpm_fallback.py` prüft echte Header-/CPIO-Daten
einschließlich Root-Besitz, Modi, Inhalte und vollständiger Systempfade.

Entwicklung 06.10.26: `.148`-Vergleich stellt fehlende Funktionsschalter,
Steuerbesitz, Designautomatik, Snapshot-Bedienung, Hardwarekarten, GPU-Grafiken,
Dashboard-Anpassung und vier originale LCD-Animationen additiv wieder her.
Ubuntu-LACT liest über begrenzte abbrechbare Hintergrundprozesse; Fedora behält
den bisherigen Lesepfad. Backend-Prüfungen verwenden offizielle Quellen und
native Paketmetadaten. SDK 6 ist ausdrücklich auf die Ubuntu-Spur begrenzt;
Fedora-Installationsbefehle bleiben erhalten. Navigation und Featureaktivierung
besitzen getrennte Persistenz. AIO-Rollen bleiben im jeweiligen PC-Profil.

Entwicklung 05.10.26: CPU-Standardkurven werden beim Start anhand der erkannten
CPU nur solange geladen, bis der Nutzer Profil oder Kurve ändert. Die Steuerung
steht direkt unter dem Besitz-/Konfliktschutz. PC-Gehäuseprofile speichern nun
auch CPU_FAN, PUMP_FAN, Radiator und Pumpe; Konflikte werden bestätigt. Die
bestätigte MSI-X870-Belegung wird einmalig über eindeutige Anschlussnamen
ergänzt, ohne PWM-Schreibzugriff. Navigationseinstellungen 1.0 stellen die
sichtbare Modulliste wieder her. Die vier Sprachkataloge besitzen 1.916 Einträge.

Entwicklung 05.10.26: Mainboard-Treiber-/MOK-Assistent 1.1 trennt unter Ubuntu
Paketlisten-Aktualisierung und Installation, verändert defekte Fremdquellen
nicht automatisch und verwendet einen vorhandenen festen nct6687d-Checkout nur
mit `pull --ff-only`. Ein fremder gleichnamiger Ordner führt zum sicheren
Abbruch. Die optionale benutzerspezifische Polkit-Dauerfreigabe ist als fünfter
Schritt sichtbar und bleibt auf den festen Lüfterhelfer begrenzt. Die vier
Sprachkataloge besitzen 1.901 Einträge.

Entwicklung 05.10.26: Mainboard-Treiber-/MOK-Assistent 1.1 erkennt Ubuntu,
Fedora und Arch Linux über `/etc/os-release` und zeigt je Familie einen festen
Abhängigkeitsbefehl. Gemeinsame nct6687d-/DKMS-Schritte bleiben identisch;
`nct6683`-Blacklist und `msi_fan_brute_force=1` werden nur auf einem per DMI
erkannten MSI-X870-System ergänzt. Unbekannte Distributionen bleiben gesperrt.
Die vier Sprachkataloge besitzen 1.895 Einträge.

Entwicklung 05.10.26: Release-Paketierung 1.0 akzeptiert im DEB entweder das
historische `policykit-1` oder die aktuelle Ubuntu-Aufteilung `polkitd` plus
`pkexec`. Damit ist die `.148`-zu-`.149`-Aktualisierung auf Ubuntu 26.04 wieder
auflösbar; RPM/Fedora bleiben unverändert. X blendet OHC weiterhin absichtlich
in den Infobereich aus, nur dessen Rechtsklickaktion **Beenden** stoppt die
laufende Instanz vor einem Paketwechsel.

Entwicklung 05.10.26: `rgb_studio/v1_15/startup_status.py` liefert den großen
Start-/Wiederaufnahmestatus und `openrgb_profiles.py` die begrenzte private
Profilbibliothek. `lcd_media_manager/v1_0` bedient jetzt Levita und Kraken mit
Ordnern, Einzeldateien und GIF. `openlinkhub_nexus/v1_0` installiert
Nexus-Hintergründe/Touch-Manifeste nur in einer erkannten Benutzerinstallation,
sichert `nexus.json` und überlässt USB vollständig OpenLinkHub. Vier
Sprachkataloge besitzen 1.888 Einträge; Fedora bleibt unverändert.

Entwicklung 05.10.26: RGB Studio fasst erkannte Direct-RAM-Module nur in der
Oberfläche zu einer Bank zusammen; Persistenz, LED-Grenzen und Frames bleiben je
stabiler Modul-ID. Manueller Designstart nutzt vor dem ersten Frame den
vorhandenen begrenzten ENE-Reclaim. Levita wählt bei erkanntem Display plus
TRCC automatisch Hardwaremodus, sonst weiterhin Testmodus. Anwendungsschluss
besitzt einen PID-startzeitgeprüften verzögerten Neustart, der die
Einzelinstanzsperre abwartet. Vier Sprachkataloge besitzen 1.851 Einträge.

Entwicklung 05.10.26: TRCC Backend 1.0 kapselt die ausdrückliche, auf Ubuntu
begrenzte Installation des offiziellen, SHA-256-geprüften 9.10.4-Pakets. Der
LCD-Bereich und der Einrichtungsassistent bieten sie nur bei erkannter Levita
und fehlendem Backend an. Die bestehende LACT-Installation unterstützt
zusätzlich das offizielle Ubuntu-26.04-Paket; Fedora-/Arch-Zweige bleiben
unverändert. Die Levita-Bibliothek lädt mitgelieferte OHC-Designs auch ohne
vorherige externe Quelle und ergänzt validierte TRCC-Standard-, Katalog- und
Benutzermedien. Vier Sprachkataloge besitzen 1.848 gemeinsame Einträge.

Version 3.4.29.131: TRCC Linux 9.10.4 besitzt Video- und Sensor-Takt im
Daemon. OHC erkennt dessen exakte Erfolgsübergabe, hält die Speicheraufsicht
aktiv und verbraucht kein Neustartbudget für den planmäßig beendeten
CLI-Helfer. Der getrennte Levita-Abschaltwächter stellt seinen installierten
Modulpfad vor dem Import selbst her.

Version 3.4.29.130: Das GPU-Cockpit ist höhenkompakt, besitzt direkt ziehbare
Lüfterpunkte und trennt reine Lüftertests verbindlich von Grafiklast. RGB Studio
ordnet bis zu sechs Designkarten an und hält Navigation/Galerie synchron.
Gehäuse-Raumdaten ergänzen Richtung, Tempo, echte LED-Reihenfolge und selbst
gemessene Abstände/Tiefe in mm oder Inch. Cachepflege wartet auf Eingaberuhe
und läuft mit niedriger CPU-/I/O-Priorität.

Version 3.4.29.128: Snapshot-Schwellen und Btrfs-Raten besitzen gekoppelte
Regler-/Zahlenkarten. Die geladene Liste lässt sich atomar als JSON-Metadaten
exportieren; nur positive Snapper-Nummern dürfen nach Bestätigung über den
festen Helfer gelöscht werden. Das GPU-Cockpit verwendet kompakte Live-Kacheln,
breite Taktbahnen und eine früher sichtbare Lüfterkurve nach der freigegebenen
Designreferenz.

Version 3.4.29.127: Der neue Snapshot-Manager 1.0 erkennt Linux,
Dateisysteme, verfügbare Sicherungssysteme, Snapper-Zeitpläne und
Btrfs-Discard-Zustand. GameMode, Gamescope, Programmliste und KDE-Vollbild sind
bevorzugte Pausensignale; eine optionale kombinierte Mehrkern-CPU-/GPU-Heuristik
besitzt Hysterese. Zeit-/Dauersperren und Desktop-/Spiel-Drosselung laufen nur
über einen festen root-owned Polkit-Helfer ohne beliebige Befehle, Units oder
Pfade. Snapper-Stände sind lesend; Rollback bleibt absichtlich manuell.

Version 3.4.29.126: Die GPU-Hauptarbeit liegt gemeinsam in einem responsiven
Drei-Spalten-Cockpit. Die fünf LACT-Lüfterpunkte besitzen exakte Eingaben,
direkt ziehbare Grafikpunkte und drei sichere Entwürfe. Ein eigener kombinierter
Knopf testet und bestätigt erst nach gemessener Lüfterreaktion dauerhaft; der
Rückstelltest bleibt getrennt. OHC-/LACT-Protokolle lassen sich einzeln oder
gemeinsam kopieren. Der Offscreen-Render ist Teil der UI-Regression.

Version 3.4.29.125: 0 MHz ist für den AMD-GPU-Takt ein gültiger
Power-Gating-Zustand; identische Prozessstarts und Mainboard-Kurvenzeilen werden
begrenzt gebündelt. Die Gehäuseseite zeigt nur mögliche LED-/PWM-Funktionen und
fasst gespeicherte Zuordnungen lesend zusammen. RGB Studio besitzt 13 eigene
Algorithmen und 30 Vorlagen, darunter sechs räumliche Designs, und nutzt seine
animierten Karten statt einer zweiten großen Vorschau. Ein bestandener
GPU-Lüftertest darf nur nach ausdrücklicher standardmäßig deaktivierter Wahl
automatisch in LACT gespeichert werden. Vier Sprachdateien enthalten jeweils
1.736 gemeinsame IDs und bleiben unter 78.000 Zeichen.

Entwicklung bis 3.4.29.124: RGB-Vorschau-Wiederherstellung ohne verzögerten
QObject-Callback, erhaltene Lüftereinheiten, komponentenweise Bewegungsumkehr,
animierte Gehäuselüfter, automatisch übernommene Lüfterbankgrößen ohne
Anordnungszwang, unabhängige Pfadrichtungen und eine gemeinsame begrenzte
Effektuhr. Neue Pfade beginnen als Reihe; gespeicherte Reihen/Ringe bleiben
unverändert. Das Log trennt Gesamt-, RGB-/Lüfter- und Hardware-Auffälligkeitsansicht. Renderpläne
laufen weiterhin im SDK-Unterprozess und sind dort zusätzlich pro Gerät
abgeschottet. Die GPU-Seite trennt Lüftertest und dauerhafte Übernahme.

Entwicklung für 3.4.29.120: GPU-Unterprofile binden vollständige LACT-,
Lüfter-/Zero-RPM- und Lasttestwerte an die exakte GPU; Hauptprofile übernehmen
das gewählte Unterprofil, aber nur lokal geprüfte Daten dürfen Hardware
aktivieren. Maximiert mit sichtbarer Taskleiste ist Standard, Minimieren und
Vollbild sind wählbar; Gamescope trennt 4K/8K-Rendergröße von der
Monitor-Ausgabe. Transparente eigene GPU-Bilder werden nur als private Kopie
verwaltet. Der RX-9000/7000-/RTX-50/40-Katalog ist reine Darstellung ohne
erfundene Grenzen. 1.722 gemeinsame Sprach-IDs und gezielte Regressionen.
Das reale Qt-Dashboard zeigt GPU-/Hotspot-Temperatur, Lüfter-RPM und Leistung
in vier Live-Karten; Profil- und Lüfteransicht verwenden die dunkle gerenderte
Referenzsprache statt der früheren technischen Testdarstellung.

Entwicklung für 3.4.29.119: Der GPU-Kurztest erkennt Lüfteränderungen jetzt
über die Schlüssel des Änderungs-Dictionaries. `slot_route_editor.py` hält den
Python-Wrapper seines Inventar-Timers und stoppt/trennt ihn vor dem Übergang
in den LED-Editor. `editor_sections.py` verschiebt die lebende Vorschau ohne
einen verworfenen Qt-Formzeilen-Wrapper. Das neue Modul `crash_recovery/v1_0`
führt einen privaten, begrenzten Ring aus bereits bereinigten Logzeilen und
stellt nach unvollständigem Ende exakt die letzten fünf Minuten in Datei,
Sitzungslog und sichtbarem Log wieder her. `privacy_logging.py` aktiviert
zusätzlich Fatal-Signal-Tracebacks aller Python-Threads und archiviert sie
beim Neustart. Keine Hardware-Schreibaktion während der Entwicklung.

Entwicklung für 3.4.29.118: `gpu_motion_wizard.py` führt den zehnsekündigen
Sichttest für explizit synchronisierte GPU-/Halterungs-ARGB-Zonen. Vor jedem
Zeitfenster bestätigt der einzige SDK-Worker einen neuen Geräteframe beider
Controller. `render_plan.py` blendet währenddessen alle anderen ausgewählten
Direct-Zonen im selben Geräteframe schwarz aus; kompatible ausgewählte
native OpenRGB- und NZXT-LEDs werden ebenfalls temporär ausgeschaltet.
`gpu_motion_editor.py` stellt nur begrenzte Kandidaten vor; Übernahme speichert
über den bestehenden GPU-Dialog, Abbruch setzt die Regler zurück. Der
ursprüngliche Effekt wird nach Ende über die normale RGB-Koordination neu
angefordert, sofern die Engine noch im OHC-Besitz ist. Der Assistent zeigt
Blau/Weiß; Pixel- und Lüfterzonen-Sichttests zeigen nur das Ziel weiß und
setzen andere OHC-LEDs vorübergehend schwarz. `header_preview.py` fordert
das Design auch nach teilweisem Testfehler bei gesundem Besitz zurück.
Alle vier Sprachdateien
haben nun 1.674 IDs. Keine Zonen-SDK-Pakete und keine Hardware-Taktänderung.

Entwicklung für 3.4.29.117: Das Nutzerprotokoll der installierten `.116`
belegt funktionierende Geräteframes, danach zwei aktivierte Zonenversuche,
Zeitüberschreitungen und ein unerwartetes OpenRGB-Engine-Ende. Ein OHC-
Neustart stellte sechs Geräte und Geräteframes wieder her. `gpu_lighting.py`
entfernt beide Versuchsschalter und übergibt keine Zonenanforderung mehr.
`openrgb_sdk.py` ignoriert auch alte Worker-Felder und schreibt nach der
bewährten Direct-Vorbereitung nur vollständige Geräteframes. Der Host
protokolliert die Komponente weiterhin; versuchsbedingte Rückstelllogik
entfällt. Bestätigte LED-Zahlen bleiben erhalten. Optische Untersuchung
des älteren GPU-Verlaufs bleibt offen.

Entwicklung für 3.4.29.116: Das Nutzerprotokoll der installierten `.115`
zeigt nach `zones` auf MSI einen OpenRGB-Zeitfehler und ein unerwartetes
Engine-Ende. `gpu_lighting.py` verwendet daher für GPU und Halterung wieder
Geräteframes als Standard, ignoriert die alte Testeinstellung und besitzt
zwei neue, getrennte Opt-in-Schalter. Nur ausdrücklich erkannte MSI-/Airgoo-
Routen können Zonenpakete anfordern. `kraken_control.py` loggt Komponente,
Schreibweg und Rückstellung und deaktiviert einen aktiven Test bei SDK-Fehler
oder Engine-Ende. `openrgb_sdk.py` hält den Geräteframe als Standard.
Vier Sprachen besitzen 1.656 IDs. Die optischen Tests bleiben offen.

Entwicklung für 3.4.29.115: `openrgb_sdk.py` kann für die ausdrücklich
zugeordnete MSI-Mystic-Light-GPU nach dem ersten vollständigen Direct-Frame
validierte SDK-Zonenpakete senden; der GPU-Dialog schaltet diesen Testweg
umkehrbar. Socket-Antworten und Schreibweg stehen im Log, eine optische
Bestätigung ist damit nicht verbunden. `case_animation.py` berechnet aus
vorhandenen GPU-/Halterungs-/RAM-Zuordnungen eine rein lesende Vorschau;
`diagram.py` animiert sie nur bei sichtbarer Gehäuse-Seite. Fehlende
physische Wegdeklarationen bleiben schematisch. Vier Sprachen haben jetzt
1.655 IDs; der optische Vergleich an der GPU steht aus.

Entwicklung für 3.4.29.114: `gpu_motion_editor.py` übergibt Reglerstände
während eines bereits aktiven RGB-Effekts als flüchtigen Entwurf an
`render_plan.py`; Schließen löscht ihn, Speichern persistiert ihn.
`gpu_motion.py` ergänzt eine begrenzte GPU-Weißspitze; `gpu_strip_sampling.py`
hebt schwache GPU-Kanten an, ohne den Halterungstakt zu verändern.
`gpu_routing.py` lässt GPU-Renderfehler nicht mehr still auf den alten
sprunghaften Generator zurückfallen. `argb_controls.py` bietet GPU-Steuerweg
im Gehäuse, getrennte Anschlusswahl und direkten LED-Editor bei eindeutigem
Ziel. `gpu_led_editor.py` und der Komponenten-Editor zeigen den Blocknamen.
`topology_labels.py` und `diagram.py` zeichnen nur gespeicherte physische
LED-Verläufe. Vier Sprachen haben jetzt 1.654 IDs. Optischer Nachtest offen.

Entwicklung für 3.4.29.113: `gpu_strip_sampling.strip_clock()` nutzt einen
festen gemeinsamen Streifenzyklus, damit getrennte Vorlauf-/Auslaufwerte die
Phase der jeweils anderen Reihe nicht verschieben. Der GPU-Standard ist nun
40 % Vorlauf / 38 % Auslauf, die Halterung bleibt bei 32 % / 36 %.
Optische Bestätigung auf beiden echten Geräten steht noch aus.

Entwicklung für 3.4.29.112: `rgb_studio/v1_15/gpu_motion.py` besitzt begrenzte
Vorlauf-/Auslauf-/Tempo-Einstellungen und einen pro übertragenem Batch
begrenzten gemeinsamen GPU-/Halterungs-Zeittakt. `gpu_motion_editor.py`
zeigt beide deklarierten LED-Reihen und bestätigte SDK-Hz im GPU-Dialog;
Regler schreiben erst beim Speichern. `render_plan.py` transportiert
denselben Zeitwert und dieselben Einstellungen zum einzigen SDK-Arbeiter.
RGB-Profile sichern die Parameter; vier Sprachen haben 1.653 IDs.
Keine neue Schreibautorität oder optische Rücklesung.

Entwicklung für 3.4.29.111: `gpu_control/v1_0/stress.py` wählt die
LACT-GPU per PCI-Hersteller-/Gerätekennung statt über `DRI_PRIME=1`;
`stress_ui.py` prüft die tatsächliche vkmark-Gerätemeldung, passt die
Szenendauer an 15–120 s an, protokolliert Takt/Leistung/Drosselung und
stoppt bei zehn aufeinanderfolgenden Überschreitungen der LACT-Standardleistung.
`page.py` nutzt dieselbe GPU-Auswahl im kurzen Tuningtest und verlangt bei
neuer LACT-Lüfterübernahme nach 3,8 s ein gemessenes Anlaufen, bevor
`fan_profile.py` das Speichern freigibt. `diagnostics_ui.py` zeigt bei
deaktiviertem Lüfterprofil keinen irreführenden gespeicherten Sollwert.
`power_policy.py` validiert LACTs Geräte-/Standardgrenzen; `power_ui.py`
begrenzt OHC standardmäßig auf den gemeldeten Werkswert und entsperrt
höhere Werte nur nach ausdrücklicher Bestätigung, begrenzt durch LACTs
gemeldetes Maximum. Ein externer hoher LACT-Wert wird sichtbar und nicht
stillschweigend geändert.
`tables.py` hält die begrenzte lesende GPU-/Hardwaretabelle aus der
Steuerungsseite heraus und bewahrt denselben Darstellungsvertrag.
Regressionen: `tests/test_gpu_fan_stress_3429107.py` und vier Sprachen.

Entwicklung für 3.4.29.110: `gpu_control/v1_0/fan_profile.py` und
`client.py` validieren auch statische LACT-Lüfterwerte und prüfen die
Konfigurationsrückgabe unter Berücksichtigung optionaler Null-Standardwerte.
`fan_ui.py` startet den abgesicherten Kurztest jetzt tatsächlich.
`reset_ui.py` trennt lokales Verwerfen von bestätigt zurückgesetzten
LACT-Profilwerten; `page.py` lässt die Lüfterfreigabe nach externen
LACT-Änderungen zu. `diagnostics_ui.py` zeigt OHC-Aktionen, GPU-Messwerte
und begrenzte LACT-Dienstmeldungen mit ausdrücklich ausgelöstem privatem
Export. `stress.py`/`stress_ui.py` bieten 8K-Phong-Last und verlangen
beobachtete hohe GPU-Auslastung. Regressionen: GPU-Steuerung,
Lüfter/Lasttest und Offscreen-Lokalisierung.

Entwicklung für 3.4.29.109: `gpu_control/v1_0/page.py` aktiviert den
GPU-Langtest auch ohne OHC-Snapshot. `stress_ui.py` überwacht dann die
aktuell aus LACT gelesene Konfiguration ohne Schreibzugriff; nur ein
passender OHC-Snapshot ermöglicht bei erkanntem Fehler die Rückstellung.
Die Übersetzungen unterscheiden offene Tuning-Eingaben vom aktiven
LACT-Zustand. `tests/test_gpu_fan_stress_3429107.py` prüft den reinen
Ausgangswert-Test ohne Hardware oder GPU-Schreibbefehl.

Entwicklung für 3.4.29.108: `gpu_control/v1_0/page.py` zeigt die
`vkmark`-Installation auch neben dem GPU-Kurztest an und bietet sie beim
fehlenden Lastprogramm unmittelbar an. `stress_ui.py` nutzt denselben
bestätigten Pakethelfer für beide GPU-Reiter, hält den GPU-Kurztest nach
der Installation bis zum nächsten ausdrücklichen Klick angehalten und
meldet Erfolg/Fehler in beiden Ansichten. `tests/test_gpu_fan_stress_3429107.py`
prüft das Angebot ohne GPU-Schreibzugriff, `tests/test_dependency_helper.py`
den Fedora-Paketcheck.

Entwicklung für 3.4.29.107: `gpu_control/v1_0/fan_profile.py` prüft eine
fünfpunktige GPU-Lüfterkurve gegen LACTs gemeldete Temperatur- und
PWM-Grenzen; `fan_ui.py` macht die Kurve ohne vorheriges LACT-Profil
editierbar. `stress.py` und `stress_ui.py` wählen einen stärkeren
Vulkan-Benchmark und überwachen einen abbrechbaren 15–120-Sekunden-Test
bereits bestätigter OHC-Einstellungen mit Rückstellung des passenden
Snapshots bei erkanntem Fehler. `hardware_checker/v1_0/probe.py` erfasst
vkmark, `page.py` bevorzugt es gegenüber glmark2/vkcube.

Entwicklung für 3.4.29.106: `gpu_control/v1_0/client.py` leitet RDNA4-
Taktgrenzen und ungespeicherte Ausgangswerte aus LACTs lesendem
`device_clocks_info` ab; `page.py` aktiviert nur die tatsächlich gemeldeten
Regler. Der Kurztest, die LACT-Rückstellung und die getrennte dauerhafte
Bestätigung bleiben vorgeschaltet. `lcd_levita_shutdown/v1_0/guard.py`
prüft bei einer abweichenden TRCC-PID die ursprünglich erfasste PID direkt
über `levita_daemon_health/v1_1/model.py`. Bereits beendete eigene Prozesse
gelten als freigegeben, eine andere Instanz bleibt unangetastet.

Entwicklung für 3.4.29.105: Qt meldete DP-1 als Fenster-Surface und Geometrie,
obwohl der Besitzer das OHC-Fenster sichtbar auf dem linken HDMI-A-1 sah. KDE
meldet DP-1 (3440×1440, Priorität 1) rechts bei 1920,0, HDMI-A-1 (1920×1080,
Priorität 2) links. Fensterplatzierung 1.5 fragt deshalb KWin selbst über einen
kurzlebigen, PID- und titelgebundenen Skript-/D-Bus-Weg; nur KWin darf im Log
eine Ausgabe bestätigen. Bei Abweichung wird allein das OHC-Hauptfenster auf
den gewählten Ausgang verschoben. Kein globaler KWin-Regelsatz, keine
Dauerkorrektur. Der Live-KWin-Rückkanal wurde mit nicht vorhandener Test-PID
ohne Fensteränderung bestätigt; optische Prüfung nach Installation offen.

Die GPU-Seite bietet nach Bestätigung LACTs eigene Overdrive-Bootvorbereitung über einen begrenzten Hilfsprozess an; kein automatischer Neustart. Regression in `tests/test_gpu_control_3429102.py` und allen vier Sprachkatalogen.

Entwicklung und lokaler Bau für 3.4.29.104: Der LACT-Socket meldet bei einer frischen GPU
`get_gpu_config: null`; das ist ein leeres Profil. GPU-Messwerte bleiben
sichtbar, die dedizierte Karte wird bevorzugt und `system_info` steuert die
Overdrive-Sperre. Die Seite öffnet LACT zur ausdrücklichen Aktivierung und
zeigt den inaktiven CoolerControl-Dienst als konfliktfrei. Keine automatische
Kerneländerung oder GPU-Schreibprobe. 742 Release-Tests und Sicherheits-,
Datenschutz- und Modulprüfung bestanden; RPM, ZIPs und zwei vollständige
externe Backup-Manifeste verifiziert. Regressionen in
`tests/test_gpu_control_3429102.py` und allen vier Sprachkatalogen.

Entwicklung für 3.4.29.103: LACT 0.10.1 besitzt kein `lact --version`.
`gpu_control/v1_0/version.py` prüft die installierte RPM-/Pacman-/DEB-Version
vor GPU-Schreibzugriffen, und `install-lact.sh` beendet eine bereits teilweise
erfolgreiche Installation ohne erneutes COPR-Einrichten. Der bestätigte Dienst
läuft nach dem Abschluss; read-only meldet LACT zwei GPUs. Die Wayland-
Platzierung bewertet nach dem Mapping die tatsächliche Fenstersurface vor
Qt-Geometrie und wiederholt die Zielprüfung nach 1400 ms. Der konkrete
`.102`-Startlog meldete DP-1 als Ziel und Qt-Ist, obwohl der Besitzer das
Fenster links sah. Kein Live-Fensterneustart oder GPU-Schreibtest.

Entwicklung für 3.4.29.102: GPU Control 1.0 nutzt LACT 0.10.1+ über den
lokalen Unix-Socket, begrenzten Last-Kurztest, automatisch verworfene
Testkonfiguration und getrennte dauerhafte Bestätigung. Vor jedem Schreiben
wird CoolerControls GPU-Lüfterbelegung geprüft; GPU-Lüfter können an Firmware
oder CoolerControl zurückgegeben werden. Vorwerte bleiben pro GPU für eine
spätere ausdrückliche Rückstellung gespeichert. Der Einrichtungsassistent
bietet LACT und OpenRGB optional an. Der unabhängige Lebenszeitwächter
protokolliert fehlgeschlagene Abschlüsse und stoppt nur exakt zugeordnete
OHC-Kindprozesse; der CoolerControl-Dienst wird nach temporärer Übernahme
zurückgegeben. Kein Live-Hardwaretest oder Installation dieser Entwicklung.

Diese Datei ist der verpflichtende erste Wegweiser für lokale und webbasierte Coding-KIs. Sie beantwortet, welches Modul für eine Aufgabe zuständig ist, wo ausschließlich dessen aktuelle Version liegt und welche Dateien dafür gelesen werden müssen. Änderungen an Quellcode, Modulstruktur, Modulversionen oder Verantwortlichkeiten müssen dieses Register im selben Arbeitsschritt aktualisieren. Das Auslassen ist nicht zulässig.

## Pflichtablauf für jede KI

Entwicklung 19.09.26 / 3.4.29.101: Der live installierte `.98`-Fensterschluss
ging am Nachmittag in den Infobereich; das spätere ausdrückliche Beenden
erreichte Qt-Rückkehr und Elternprozessende. Der danach verbliebene TRCC-Daemon
gehörte demselben OHC-Autostartdienst an und belegte rund 1,3 GiB RSS.
`lcd_levita_shutdown/v1_0/guard.py` vermeidet einen neuen Daemon beim
Abschalten ohne laufenden Besitzer und stoppt nach Firmware-Rückgabe nur den
seit OHC-Start beobachteten Daemon. Vorhandene/fremd ersetzte PIDs bleiben
unangetastet. Der konkrete Restprozess wurde mit `trcc kill` beendet und sein
Verschwinden bestätigt. 81 gezielte und 723 vollständige Release-Tests sowie
Sicherheits-/Datenschutz-/Modulprüfung bestanden. Die installierte Version
bleibt `.98` bis zu einer separaten Aktualisierung.
Die interne `.101` ist lokal als RPM, Laufzeit-/Entwickler-ZIP,
Quellarchiv und Local-AI-Gitbundle gebaut; Dist und die beiden externen
`.100`/`.101`-Sicherungen bestehen SHA-256. DEB mangels `dpkg-deb` ausgelassen.

Entwicklung 19.09.26: Hardware-Checker 1.0 nutzt neben glmark2 einen begrenzten
Vulkan-`vkcube`-Lasttest nach direkter Erstprüfung mit tatsächlichem Prozesslauf als Bedingung für
PCIe-Unter-Last-Bewertungen. Seine Tabelle misst lange Mainboardnamen.
PC-Gehäuseprofile 1.5, Temperaturverlauf 1.2 und UI-Themes 1.0 teilen eine
klarere dynamische Tabellenansicht. `temperature_history/v1_2/gauge.py` zeichnet
dieselbe zwölfteilige Anzeige für Übersicht, Kühlung und Temperaturaufzeichnung;
es liest nur vorhandene Celsiuswerte. RGB Studio 1.15 verkleinert nach Video-
Abgleich den weißen GPU-Lichtkopf und hält die blaue Basis sichtbar, ohne
LED-Zahl, 25-Hz-Ziel oder Hardwarebesitz zu ändern. Vier Sprachdateien haben
1.532 gemeinsame IDs. Fünf Offscreen-Ansichten und eine GPU-Animationsskizze
liegen unter `docs/images/rendering-evidence/`. 70 gezielte und 721 vollständige
Release-Tests sowie Sicherheits-/Datenschutz-/Modulprüfung bestanden;
der feste Vulkan-Befehl lief für zwei bis drei Sekunden auf der lokalen RX 9070 XT.
Kein vollständiger In-App-Linktest, optischer RGB-Abgleich oder Installation.
Diese Änderungen wurden als interne Version 3.4.29.100 gebaut: RPM,
Laufzeit-/Entwickler-ZIP, Quellarchiv und Local-AI-Gitbundle sind geprüft;
die beiden externen `.99`/`.100`-Sicherungen bestehen ihre SHA-256-Prüfung.
DEB mangels `dpkg-deb` ausgelassen. Keine Installation oder Veröffentlichung.

Abgeschlossen .96: Hardware-Checker 1.0 liegt ausschließlich in
`src/modules/hardware_checker/v1_0/`. `probe.py` liest CPU/SMT/Virtualisierung, Board,
PCIe-GPUs, NVMe und RAM-Gesamtgröße begrenzt in einem Hilfsprozess; `model.py`
besitzt reine Link-/DMI-/Sollwertbewertung. `page.py` führt die feste optionale
Polkit-DMI-Abfrage und den ausdrücklichen begrenzten glmark2-Test aus. Keine
Takt-/Spannungs-/Lüfter-/BIOS-/Firmwareänderung und kein SSD-Schreibbenchmark.
PCIe-Leerlaufdrosselung bleibt Warnung; ein GPU-Fehler braucht den Lasttest,
NVMe-Lane-Abweichungen sind statisch sichtbar. 1.530 Sprach-IDs. Regression:
`tests/test_hardware_checker_342996.py`; 708 Release-Tests, Paketbau und
SHA-256-geprüfte `.95`/`.96`-Sicherungen abgeschlossen. DEB mangels lokalem
`dpkg-deb` nicht erzeugt; keine Installation oder Veröffentlichung.

Abgeschlossen .95: Display-Effekte 1.11 entfernt feste Lichtband-Randkonturen und
rendert acht Richtungen mit tatsächlichen hochaufgelösten Quellframes neu.
Sichtbarkeitsgebundene ausgewählte LCD-Videovorschau liegt in
`lcd_levita/v1_7/media_preview.py`; eine bestätigte getrennte Vorschaukopie
verhindert, dass Browsing als aktives Hardwaredesign angezeigt wird.
`lcd_media_manager/v1_0/preview_visibility.py` und `video_preview.py` begrenzt beide Decoder auf den
sichtbaren Vorschau-Viewport; transiente Effektwahl fällt nach Abwahl/Seitenwechsel
auf das zuletzt bestätigte Design zurück. Galeriegrößen werden stabil reserviert.
73 gezielte Tests nach Sprachdetailkorrekturen bestanden; DE/FR-Vorschau
gerendert und geprüft. Acht Videos vollständig dekodiert und Geometrie/FPS/
Dauer verifiziert. Vollständige Vier-Sprachen-UI bestanden. UI-Leistung 1.1
bindet verzögerte Tab-/Animationsaufrufe an den QObject-Lebenszyklus und
sperrt Tab-Scans bei gelöschtem Host; echter Qt-Regressionstest ergänzt.
Synthetische Engine-Tests setzen fremde Eigentümerschaft explizit zurück.
Vorschaupfade sind für Decoderidentität normalisiert. Alle 701 Release-Tests
und vollständige Vier-Sprachen-UI/Sicherheit/Datenschutz/Modulprüfung bestanden.
RPM/Archive/komplettes Git-Bundle gebaut und verifiziert: beide ZIP-CRCs,
233 aktuelle Pythonquellen und alle 16 neu gerenderten Bandmedien in beiden
ZIPs/Quelle/RPM, RPM-Digests/Metadaten und Git-Bundle bestanden. Dist und beide
externen .94/.95-SHA256-Manifeste bestanden. Genau zwei vollständige
Sicherungen; .93 gemäß Dauerfreigabe rotiert. Kein DEB mangels Toolchain.
Keine Installation/Hardwareaktion/Veröffentlichung. Abschluss nach Paketbau;
archivierte Dokumente enthalten den Vorbau-Prüfstand. Optischer Dauerlauf am
Gerät nicht durchgeführt.

Entwicklung .94: PC-Gehäuseprofile 1.5 besitzt `editor_sections.py` für dieselben
lebenden Formularfelder in Spalten oder Reitern, ohne inneren Scrollbereich.
`inline_editor.py` reserviert adaptiv 430–860 px nach links; Komponenten-/Lüfter-
und LED-Verlaufsformulare bleiben unterteilt, Speichern/Abbrechen außerhalb.
UI-Leistung 1.1 verfolgt auch späte Reitertitel bei Live-Sprachwechseln.
RGB Studio 1.15 verbreitert offene GPU-/Halterungslichtköpfe und Ausläufe mit
quintischem Übergang; gemeinsame virtuelle Zeit und Flächenabtastung sind von
der tatsächlichen LED-Anzahl getrennt. Keine Layout-/RGB/PWM-Speicherung allein
durch Reiterwechsel oder Resize, keine neue Hardwareverbindung. 1.483 Sprach-IDs.
Regressionen: `test_case_editor_layout_342994.py`, `test_gpu_blending_342994.py`.
54 gezielte Tests und erweiterte GPU-/PWM-Menüprüfung bestanden. DE/FR breite/
schmale Formulare und LED-Verlauf gerendert und geprüft. Alle 697 Tests samt
Vier-Sprachen-UI/Sicherheits-/Datenschutz-/Modulprüfung bestanden. RPM/Archive/
Git-Bundle gebaut und verifiziert: beide ZIP-CRCs, 230 aktuelle Pythonquellen,
RPM-Digests/Metadaten, komplettes Git-Bundle und Dist/.93/.94-SHA256 bestanden.
Genau zwei vollständige Sicherungen; .92 gemäß Dauerfreigabe rotiert. Kein DEB
mangels Toolchain. Keine Installation/Hardwareaktion/Veröffentlichung; optische
Prüfung und LCD-Dauerlauf am Gerät stehen aus. Abschluss nach Paketbau,
archivierte Dokumente enthalten den Vorbau-Prüfstand.

Entwicklung .93: LCD Runtime 1.1 trennt in `design_state.py` den ausdrücklich
gespeicherten Standard, Vorschau und zuletzt beauftragte immutable Befehlsfolge.
Automatische Profile ersetzen keinen vorhandenen Standard, auch nicht bei
fehlender Datei oder ausgeschalteter Automatik; ausdrückliches Profil-Laden
ersetzt denselben Standard vollständig einschließlich FPS/Bewegung.
Effektvorschauen schreiben keine Profilvormerkung. Speichern/Anwenden entwertet
veraltete Start-Retries. Wiederherstellung verwendet vorbereitete Medien statt
der Vorschau. `memory_guard.py` toleriert stabiles Video-RSS über 1 GiB;
Neustart bei 3 GiB, tatsächlichem MemAvailable <256 MiB ab 1 GiB oder drei
aufeinanderfolgenden Anstiegen von mindestens 64 MiB mit insgesamt 256 MiB.
Exakte Eigenprozess-/USB-/Quarantänegrenzen bleiben erhalten. Native Cache-
Identität umfasst effektive Konfiguration und Quellassets. 1.482 Sprach-IDs.
Regressionen: `test_lcd_design_authority_342993.py`, Layout-/Effekt-/Vier-Sprachen-UI.
Alle 686 Tests samt Vier-Sprachen-UI/Sicherheits-/Datenschutz-/Modulprüfung bestanden.
RPM/Archive/Git-Bundle gebaut und verifiziert: beide ZIP-CRCs, 229 aktuelle
Pythonquellen in ZIP/Quelle/RPM (vier Standard-Shebang-Anpassungen), RPM-Digests/
Metadaten, komplettes Git-Bundle und Dist/.92/.93-SHA256 bestanden. Genau zwei
vollständige Sicherungen; .91 gemäß Dauerfreigabe rotiert. Kein DEB mangels
Toolchain, keine Installation/Hardwareaktion/Veröffentlichung. Abschluss nach
Paketbau; archivierte Dokumente enthalten den Vorbau-Prüfstand.

Entwicklung .92: Prozesslaufzeit 1.1 enthält zusätzlich `diagnostics.py`,
`restart_policy.py` und `sdk_supervisor.py`: private begrenzte Modulereignisse,
5-s-SDK-Ready-/Framefristen und bestätigungsabhängiges 1/2/4-s-Wiederanlaufbudget.
Sensorfehler erfassen Ursache, PID, Exit-Code und begrenzte stderr/Tracebacks;
`health.py` zeigt LCD-Transfers und erlaubt ausdrücklich read-only Sensor-Neustart.
LCD Runtime 1.0 besitzt `progress.py`, `controller.py`, `game_probe.py` und
`game_activity.py`: bestätigte CLI-Sendefortschritte, 45-s-Start-/Befehlsfrist,
15-s-Fortschrittsfrist sowie ausgelagerte begrenzte Spielerkennung.
Statische Designs nutzen denselben einzigen Daemon-IPC-Taktgeber wie Videos.
Keine Vorschau autorisiert USB; Testmodus/Shutdown bleiben Sperren, native
Hardwarecrashes bleiben isoliert. Regression: `test_module_supervision_342992.py`.
Vier Sprachdateien haben 1.481 identische IDs. 17 neue Fehlertests und das
vollständige 673-Test-Gate einschließlich Vier-Sprachen-UI/Sicherheit/Module
bestanden; DE/FR-Systemstatus gerendert und geprüft. RPM/Archive/Git-Bundle
gebaut und 227 Pythonquellen/ZIP-CRC/RPM-Digests/Metadaten/Bundle/SHA256 geprüft.
Genau zwei vollständige Sicherungen .91/.92; .90 gemäß Dauerfreigabe rotiert.
Kein DEB mangels dpkg-deb, keine Installation/Hardwareaktion/Veröffentlichung.


Entwicklung .91: Process Runtime 1.0 besitzt `controller.py`, `sensor_worker.py`
und `health.py`: ein Qt-freier read-only Sensorprozess, begrenzte Überwachung,
frische gemeinsame CPU/GPU/Systemwerte und eingebetteter echter Prozessstatus.
RGB Studio 1.14 besitzt `render_plan.py`: Hardwareautorisierung bleibt im Host,
reine Berechnung läuft vor dem bestehenden SDK-Schreibpfad im vorhandenen Worker.
PC-Gehäuseprofile 1.4 teilt gezeichnete Beschriftungen mit ihrer Klickgeometrie.
Anwendungsabschluss 1.1 besitzt zusätzlich `journal.py`, `watcher.py` und
`qt_processes.py`: privates begrenztes Phasenjournal, einmaliger verzögerter
Stack-Dump und maximal 90 Sekunden unabhängige Beobachtung des exakten Eltern-PID
mit Startzeitprüfung; keine Signale an die Anwendung. Übrige eigene Qt-Prozesse
werden erst nach Hardware-Rückgabe begrenzt beendet. Tests und Pakete ausstehend.
Die autonome Kühlungs-/Core-Migration ist eine spätere hardwarevalidierte Stufe,
nicht Bestandteil dieser read-only Prozessgrenze. 1.476 atomare Sprachtexte.
`temperature_history/__init__.py`, `v1_2/__init__.py` und `panel.py` behalten den
Vertrag, importieren GUI-Exporte lazy und konsumieren den frischen Sensorkatalog.
`resource_metrics.py` liest eigene /proc-CPU/RSS ohne irreführende Speichersumme.
Der bestehende ausdrückliche `collect-diagnostics.sh`-Export nimmt begrenzte
Beenden-Dateien in die vorhandene Anonymisierung auf; kein automatisches Teilen.
`tests/test_process_runtime_342991.py` und `test_exit_journal_labels_342991.py`
prüfen Isolation/Protokoll/Grenzen/identische RGB-Mathematik und Persistenz/Klicks.

| Modul | Modulversion | Aktueller Pfad | Einstieg / Verantwortung | Status |
|---|---:|---|---|---|
| LCD-Prozessüberwachung | 1.1 | `src/modules/lcd_runtime/v1_1/` | Sendefortschritt, Befehlsfristen, Spielerkennung, expliziter Standard und immutable Wiederherstellung/Speicherpolitik | Bestehender sole-owner IPC; `tests/test_module_supervision_342992.py` |
| Prozesslaufzeit | 1.1 | `src/modules/process_runtime/v1_1/` | Sensorprozess, begrenzter Supervisor und Systemstatus | Keine Hardwarewrites oder autonome PWM-Regelung; `tests/test_process_runtime_342991.py` |

Entwicklung .90: UI-Leistung 1.1 besitzt Navigation-only Übergänge und begrenzte
Leerlauf-/LCD-Kartenarbeit in `gallery_preparation.py` und späte werttreue
Sprachwechsel in `dynamic_text.py`.
Bildkarten verwenden `thumbnails.py` für verkleinerte, quellversionierte PNGs;
eigene UI-Cachepflege wird beim Ende begrenzt gestoppt. Tests zusätzlich in
`test_gallery_preparation_342990.py`; keine Originalmedienänderung.
PC-Gehäuseprofile 1.3 besitzt eingebettete Komponenten-/ARGB-/PWM-Bearbeitung.
RGB Studio 1.13 isoliert RAM-Nachprüfungen
vom übrigen laufenden RGB-Strom. Kühlungszustand und ausdrückliches Beenden
werden separat auf Persistenz-/Ereignisschleifengrenzen geprüft. Tests/Paketierung
offen; keine Hardwareprüfung oder neue Schreibautorität. `inline_editor.py`
besitzt rechten Inspector/Abbruch/Generation, `component_editor.py` Aufbau und
Bestätigung; `stream_reclaim.py` besitzt validierte RAM-IDs/Frame-Drain/Lease.
Kühlungszustand 1.0 in `cooling_state/v1_0/controller.py` trennt Startabsicht,
frischen Besitzerstatus und aktive Anzeige. 1.467 atomare Sprachtexte; Regressionen
`test_cooling_state_342990.py`, `test_rgb_stream_reclaim_342990.py` und
`test_inline_lcd_shutdown_342990.py` ergänzen bestehende Pflichtprüfungen.

Aktuelle Ergänzung .89: RGB Studio 1.12 besitzt weiche offene GPU-Streifen
und optionale gemeinsame Zeit-/Effektberechnung mit der ausdrücklich zugeordneten
GPU-Halterung. Pure Abtastung und begrenzte Paarauflösung sind getrennt; keine
neue Transportverbindung, LED-/PWM-Änderung oder automatische Geräteauswahl.
Zwei atomare Sprachtexte ergänzt. 105 gezielte und alle 597 vollständigen Tests,
Vier-Sprachen-UI, Sicherheits-/Datenschutz-/Modulprüfung bestanden; DE/FR-
GPU-Dialog visuell geprüft. Wiederholtes 597-Test-Baugate und lokale .89-
Paketierung abgeschlossen. RPM-Digests/Metadaten, 44 aktuelle Quellen,
ZIP-CRC/44 Quellen und Quellarchiv geprüft; Git-Bundle mit vollständiger Historie.
Dist und .88/.89-SHA256 bestanden, genau zwei vollständige private Sicherungen;
.87 nach dauerhafter Freigabe rotiert. Keine Installation/Hardwareoperation.
Datum: 13.09.26.

1. `docs/ai/AGENTS.md` und anschließend dieses Modulregister vollständig lesen.
2. In der Tabelle genau das betroffene Modul bestimmen.
3. Für Umsetzungsschritte `docs/ai/AI_DEVELOPMENT_GUIDE.md` lesen und danach nur den aktuellen Modulordner, dessen README, öffentliche Schnittstellen und gezielte Tests laden.
4. Keine ältere Modulversion im Arbeitsbaum suchen oder neu anlegen.
5. Bei einer Änderung Modulversion, Pfad, Abhängigkeiten, Tests und Änderungsregister hier aktualisieren.
6. Datumsangaben ausschließlich als `TT.MM.JJ` erfassen. Keine Uhrzeit und keine lokalen Benutzer-/Rechnerdaten eintragen.

## Größenbudget für lokale KI mit 16 GB VRAM

- Zielwert einer normalen handgeschriebenen Quelldatei: höchstens **600 Zeilen** und **32.000 Zeichen**.
- Ab **800 Zeilen** oder **40.000 Zeichen** muss vor weiterer Fachlogik in Unterdateien aufgeteilt werden.
- Neue handgeschriebene Dateien über **1.200 Zeilen** oder **60.000 Zeichen** sind verboten. Ausnahmen gelten nur für generierte Dateien oder ausdrücklich hier dokumentierte Legacy-Dateien mit aktivem Zerlegungsplan.
- Eine Funktion soll höchstens 80 Zeilen, eine Klasse höchstens 300 Zeilen besitzen. UI-Aufbau, Zustandsmodell, Persistenz, Rendering und Hardwarebefehle gehören in getrennte Dateien.
- Wenn eine Aufgabe das Budget überschreiten würde, wird ein Untermodul angelegt; beispielsweise `layout_model.py`, `layout_canvas.py` und `theme_adapter.py` statt eines neuen großen `display_ui.py`-Blocks.

## Ordner- und Versionsregel

- Neue oder migrierte Fachmodule liegen unter `src/modules/<modulname>/v<major>_<minor>/`.
- Jeder aktuelle Versionsordner enthält ein `__init__.py`, ein kurzes `README.md` und kleine Dateien nach Verantwortlichkeit.
- Die Modulversion beginnt bei `1.0`. Eine neue Funktion oder ein geänderter Vertrag erhöht sie nachvollziehbar, beispielsweise auf `1.1`; ein grundlegender inkompatibler Vertrag auf `2.0`.
- Im Arbeitsbaum bleibt nur der aktuelle Versionsordner. Git-Historie, Tags und Releases sind die Rückfallebene; parallele `old`, `backup`, `copy` oder veraltete Versionsordner sind nicht erlaubt.
- Ein bestehender Root-Einstieg darf während der schrittweisen Migration als dünne Kompatibilitätsschicht bleiben. Neue Fachlogik darf dort nicht weiter anwachsen.
- Abhängigkeiten zeigen nach innen: Versionsmodule importieren niemals den großen UI-Orchestrator `src/kraken_control.py` und niemals ihre aufrufende Root-UI-Datei zurück.

## Aktuelle Modulübersicht

| Modul | Modulversion | Aktueller Pfad | Einstieg / Verantwortung | Status |
|---|---:|---|---|---|
| Plattformunterstützung | 1.0 | `src/modules/platform_support/v1_0/`, `packaging/windows/`, `scripts/build_windows.ps1`, `.github/workflows/windows-preview.yml` | Reine Plattform-/Helper-Auflösung, Linux-/Windows-Vorschau und eingefrorene Helper-Kommandos | Keine Windows-Hardwarefreigabe; vorhandene Linux-Sicherheitsgrenzen bleiben |
| Funktionsmodule/Einrichtung | 1.0 | `src/modules/setup_features/v1_0/` | Persistente Funktionskarten und Einrichtungsseite, getrennte Navigation, sichere Migration alter Sichtbarkeitsschlüssel; `ownership.py` kapselt die bestehenden Host-Verträge | Deaktivierte Features sperren Hardwarepfade; keine pauschale Löschung von Einstellungen |
| Feature-Reifegrade | 1.0 | `src/modules/feature_lifecycle/v1_0/` | Zentrale unabhängige Feature-Versionen und Alpha-/Beta-/Release-Candidate-/Stabil-Einstufung für Hauptbereiche | Reine Darstellungsmetadaten; keine Persistenz, Hardwareaktivierung, Steuerhoheit oder Migration |
| Steuerbesitz | 1.0 | `src/modules/control_authority/v1_0/` | Bestätigte Besitzerwahl je Fachbereich und fail-closed Schreibfreigabe | Kein zusätzlicher Gerätebesitzer oder direkter Hardwarebefehl |
| Designs & Spiele | 1.0 | `src/modules/design_hub/v1_0/` | Stabile RGB/LCD-Paare, eigene Matrix-Abtastung, sichtbare Vorschau, Spielregel-Entwurf und feste Untermenüs | Bestehende RGB-/Levita-Anwendenpfade und Automationsregeln; keine Telemetrie-/Screen-Capture-Freigabe |
| Designautomatik | 1.0 | `src/modules/design_automation/v1_0/` | Wiederhergestellter lokaler Plan-/Programm-/Profilmanager und eigener Navigationsbereich | Bestehende Hardware- und Besitzerprüfungen bleiben maßgeblich |
| Externe Backend-Versionen | 1.0 | `src/modules/backend_updates/v1_0/` | Begrenzte read-only Prüfworker, offizielle Releasequellen, native Paketmetadaten und Ubuntu-spezifische root-owned Pfad-/Manifestprüfung in `executables.py` | Keine automatische Installation/Serviceänderung; fremde Paketmanager bestimmen nicht die Distribution |
| Levita LCD-Datenoberfläche | 1.7 | `src/modules/lcd_levita/v1_7/` | Layout-/Geometrie-/Theme-Staging, feste 1600:720-Vorschaugeometrie, bis zu zwölf eigene Texte, vier originale Glow-/Partikelrenderer und lokale Ebenenkomposition | Animiertes Dekor läuft als ein Cache-Videostrom unter editierbaren Daten; kein wiederholtes Maskenschreiben und kein zusätzlicher USB-Besitzer |
| Levita LCD-Orchestrierung | Legacy 3.4.29.95 | `src/thermalright_display_ui.py`, `src/thermalright_display.py`, `tools/render_levita_loops.py`, `tools/render_levita_overlays.py`, `tools/render_levita_motion.py` | `lcd_levita/v1_7/media_preview.py` besitzt ausgewählte Videovorschau und pending/bestätigte Kompositionskopie; sichtbarkeitsgebundene Galerien, Vorschau-Timer und Thumbnail-Arbeiter nur im tatsächlichen Karten-Viewport; zentral zwischengespeicherter Medienkatalog und Vorschaubilder; getrennte Vorschau-/LCD-FPS, Profilpersistenz, TRCC-Speicherwächter, Wiederherstellung und Display-Freigabe; vorhandene TRCC-Warteschlange ist einziger Hardware-Schreibpfad | Reine Thumbnail-Prozesse werden beim Verlassen unterbrechbar zurückgestellt; Originalmedien liegen nie im zentralen Cache; gestufte RSS-/Wachstums-/MemAvailable-Politik in LCD Runtime 1.1 und fünf Minuten Erholungssperre; 15 FPS Standard, 60 FPS nur experimentell |
| TRCC Backend | 1.0 | `src/modules/trcc_backend/v1_0/`, `packaging/install-trcc.sh` | Explizite Ubuntu-Installation des getrennten GPL-Backends über offizielles festes DEB und veröffentlichte SHA-256-Prüfsumme; UI-Rückmeldung und anschließende reine Backend-/Bibliotheksneuerkennung | Nur bei erkannter Levita und fehlendem `trcc`; keine Designanwendung oder USB-Schreibaktion; Fedora bleibt beim bestehenden manuellen/Upstream-Weg |
| Levita LCD-Abschaltwächter | 1.0 | `src/modules/lcd_levita_shutdown/v1_0/` | `guard.py` validiert den ausführbaren TRCC-Pfad, löst die feste Levita-ID beim kontrollierten Ende begrenzt aus dem Daemon, stoppt danach nur einen OHC-eigenen Daemon und überwacht nach einem bestätigten echten Schreibzugriff die Elternprozess-Pipe für denselben einmaligen Rückfall bei unerwartetem Ende | Versioniertes, Qt- und USB-protokollfreies Sicherheitsmodul |
| Levita-Daemongesundheit | 1.1 | `src/modules/levita_daemon_health/v1_1/` | Exakte Eigenprozess-Erkennung über `/proc`, RSS-Messung, Klassifizierung verlorener/besetzter TRCC-Verbindungen und unmittelbar erneut validierte Signalübergabe; `model.py:is_usb_owner_conflict` trennt USB-Belegung, `backend_failure_detail` wählt den primären Fehler statt letzter Hintzeile | Keine Qt- oder USB-Operation; Ubuntu-Orchestrierung stoppt nur eigene Wiederholungen bei Fremdbesitz, Fedora-Recovery bleibt unverändert; signalisiert ausschließlich einen exakten Prozess desselben Benutzers |
| Display-Effekte | 1.11 | `src/modules/display_effects/v1_11/` | `page.py` besitzt transiente Auswahl und bestätigte Vorschau-Rückkehr, `library.py` aktualisiert aktuelle Sprachdetails; `light_bands_renderer.py` rendert echte 4800×2160 Quellen; responsive Ebene-1-/Sensorlayout-Kacheln, sichtbarkeitsgebundene 20-FPS-Vorschau, unabhängiger Ebene-2-Animationsschalter, kanonisches Levita-Startdesign, sichere Übergabe und direkter Firmware-Rückgabeknopf | Auswahl und Breitenanpassung bleiben hardwarefrei; Startdesign schreibt nur geprüfte Persistenz, Anwenden beziehungsweise Rückgabe nutzt den bestehenden TRCC-Pfad |
| Responsive Galerien | 1.0 | `src/modules/responsive_gallery/v1_0/` | Reine Breiten-/Spaltenberechnung, gebündelter Qt-Viewport-Resize-Relay und gleichmäßige Kachelverteilung für LCD- und Effektgalerien | Keine Persistenz und kein Hardwarezugriff |
| LCD-Medienmanager | 1.0 | `src/modules/lcd_media_manager/v1_0/` | `preview_visibility.py` clippt alle Vorschau-Ahnen/Scroll-Viewports, `video_preview.py` besitzt geteiltes lokales Qt-Decoding und entlädt auf verborgenen Seiten Decoderquelle/Framepuffer vollständig; begrenzte Verwaltung mehrerer lokaler Ordner, einzelner Bilder/Videos, nicht-destruktiver Ausblendungen und eigener Anzeigenamen | Ändert, verschiebt und löscht keine Quelldateien; sichtbare Auswahl wird beim Zurückkehren neu geladen; Fremdmedien werden nicht mit OHC ausgeliefert |
| Anzeigeeinstellungen | 1.0 | `src/modules/display_settings/v1_0/` | Kleine Qt-Oberfläche für Bildschirm, Fensterstartzustand, Geometrie/Skalierung und experimentelle Levita-Bildrate | Nur Aufbau und Signalverbindungen; Persistenz, Platzierung und Hardware-Orchestrierung bleiben beim jeweiligen Besitzer |
| Levita Leistung/Spielerkennung | 1.1 | `src/modules/levita_performance/v1_1/` | Reine Normalisierung der sicheren/experimentellen FPS, Rückstufungskette, konservative GameMode-/Gamescope-/Programmlisten-Signale und Zehn-Sekunden-Abfrageintervall | Keine Lastheuristik, kein Hardwarezugriff, keine allgemeine Wayland-Fensterbeobachtung |
| Bereichs-Unterreiter | 1.0 | `src/modules/section_tabs/v1_0/` | Wiederverwendbare browserähnliche Unterreiter für Hauptbereiche mit Seitenleisten-Unterpunkten; mehrere Leisten und Hauptseite bleiben über stabile Seiten-IDs synchron | Reines Navigationsmodul ohne Hardwarezugriff; zunächst für LCD verwendet |
| Reaktionsfähiger Start | 1.0 | `src/modules/responsive_startup/v1_0/` | `probe.py` koordiniert eine begrenzte, zusammengefasste Qt-Hintergrundprüfung, `ownership_probe.py` kapselt die blockierenden read-only Systemabfragen und `controller.py` hält Mainboard-PWM bis zum bestätigten Besitzerstatus fail-closed | Versioniertes Start-/Besitzmodul; keine Hardware-Schreibbefehle |
| Profil-Kühlungsbereitschaft | 1.0 | `src/modules/profile_cooling/v1_0/` | `restore.py`: asynchroner frischer CPU-Wert, Zehn-Sekunden-Frist, neuester Auftrag und Bedien-/Shutdown-Abbruch | Keine neue Hardwarefreigabe oder synchrone Sensorlesung |
| Profil-Arbeitsbereich | 1.0 | `src/modules/profiles_workspace/v1_0/` | Reine Filter/Zusammenfassung, auswählbare Karten, responsive Bibliothek, Bearbeitung/Details/Transfers; versteckte ID-Tabelle | Keine neue Persistenz und keine Hardwareaktion bei Auswahl |
| Programm-Hintergründe | 1.0 | `src/modules/app_backgrounds/v1_0/` | Feste lokale Videos, ein Decoder, Profil-Snapshot und bestehende CPU-Komposition; Offline-Renderer unter tools | Sichtbarkeitsgebunden, keine Netzwerk-/Hardware-Schreibwege |
| Hauptfenster und Seitenkomposition | Legacy 3.4.29.99 | `src/kraken_control.py`, `src/dashboard_layout.py`, `src/localization_catalog.py` | Anwendungseinstieg und noch nicht extrahierte Controller; aufklappbare Kühlungs-/LCD-Unterseiten, hardwareabhängige Lüfterquellen, Zuordnungsreset/-assistent, unabhängige Bildschirm-/Fensterzustandswahl, globale leichte Seitenübergänge und 60-Minuten-Logansicht | X/Fensterschließen hält OHC im Infobereich am Leben; sichtbares manuelles Programmende ausschließlich über **Beenden** im Rechtsklickmenü des Tray-Symbols, Sitzungsende separat |
| Hardware-Unterbauten | 1.0 | `src/modules/hardware_backends/v1_0/` | Reine Normalisierung und fail-closed Auflösung persistierter Automatik-/Direktauswahl für vorhandenes TRCC Linux und OHC Linux-hwmon | OHC-nativer Levita- und CoolerControl-Adapter bleiben bis zu Implementierung/Validierung nicht auswählbar; keine Hardwarebefehle |
| Hardware-Checker | 1.0 | `src/modules/hardware_checker/v1_0/` | Begrenzte read-only Linux-/Windows-CIM-Erkennung, serialfreie DMI-Sockel-/RAM-Daten, responsive Übersicht in `cards.py`, separate Detailtabelle und erhaltener Hardware-Fix-/Lasttestpfad | Aktiv; keine Hardwarefreigabe aus Darstellung/Erkennung; bestehende bestätigte Schreib- und Besitzergrenzen bleiben |
| Hardware Fix | 1.0 | `src/modules/hardware_fix/v1_0/` | Profilregistrierung und Hardware-Checker-Unterseite für MSI MAG 274QPF X30MV – VRR; anonymisierte EDID, Modell-/Ressourcenprüfung, gesperrte feste Terminaljobs, Anbieterübernahme, echte DRM-Messung und profilbezogene Rücknahme | Keine persönliche Seriennummer, keine beliebigen Root-Skripte/Pfade, kein automatischer Neustart; Ubuntu-AppIndicators-Automatik läuft nie auf Fedora |
| Snapshot-Manager | 1.0 | `src/modules/snapshot_manager/v1_0/` | Reine Richtlinie/Hysterese, persistente bounded Aktivitätsprobe in `activity_runtime.py`, Qt-Ansicht in `page.py`/`views.py`, Lebensdauer in `process_runtime.py` und bestätigte Aktionen in `snapshot_actions.py`; Erstellung, Root-Einrichtung, Herkunftsfilter, ProgramManager, Zeit-/CPU-/I/O-Regler und getrennte Admin-/Automatikrechte | Aktiv; keine Hardwarefreigabe aus Darstellung/Erkennung; bestehende bestätigte Schreib- und Besitzergrenzen bleiben |
| GPU-Steuerung | 1.0 | `src/modules/gpu_control/v1_0/`, `packaging/install-lact.sh` | LACT-Client, fail-closed Feature-/Besitzschutz, responsive Cockpit-/Kurven-/Leistungsansicht; `cockpit_ui.py` trennt Widgetaufbau; `read_worker.py`, `read_probe.py`, `read_ui.py` kapseln Ubuntu-Abfragen mit Frist/Abbruch/Stale-Schutz; explizite Inline-Leistungsbestätigung, getrennte Profile/Tests/Reset/Overdrive und nativer Installer | Aktiv; keine Hardwarefreigabe aus Darstellung/Erkennung; bestehende bestätigte Schreib- und Besitzergrenzen bleiben |
| GPU-Profile | 1.0 | `src/modules/gpu_profiles/v1_0/` | Begrenzte exakte GPU-Profile mit SHA-256, nur darstellende RX-/RTX-Kataloge, normalisierte lokale Artwork-Kopien und wiederhergestellter `visual_catalog.py` mit originalen schematischen Grafiken unter `src/assets/gpu/` | Aktiv; keine Hardwarefreigabe aus Darstellung/Erkennung; bestehende bestätigte Schreib- und Besitzergrenzen bleiben |
| Temperaturverlauf | 1.2 | `src/modules/temperature_history/v1_2/` | Begrenzter RAM-Puffer, datierte Qt-Zeitachse/Hoveranzeige, skalierbare Splitter, read-only Linux-hwmon-Erkennung und CSV-/JSON-Berichte; `gauge.py` zeigt dieselbe kompakte Celsius-Skala in Übersicht, Kühlung und Aufzeichnung | Höchstens 24 Stunden/28.800 Punkte im RAM; keine automatische Persistenz, kein Hardwarebesitz und Berichtsschreiben nur nach Benutzerauswahl |
| Kühlungssicherheit | 1.0 | `src/modules/cooling_safety/v1_0/` | Modellabhängige fail-closed Untergrenzen und letzte Begrenzung vor dem Hardware-Schreibpfad | Levita: eigenes vorsichtiges OHC-Minimum 50 % Pumpe/25 % Radiator, da der Hersteller nur Maximal-RPM veröffentlicht; NZXT-Bereich unverändert |
| Kühlungszustand | 1.0 | `src/modules/cooling_state/v1_0/` | `controller.py` trennt gespeicherte Startabsicht von tatsächlicher Hauptregelung; `cpu_defaults.py` trennt erkannte Standardkurven von nutzereigenen Änderungen; `startup_policy.py` trennt bekannte NZXT-Pendingpresets nur bei bestätigtem Ubuntu/Levita ohne bereites NZXT vom expliziten PC-Startprofil | Keine PWM-Befehle; Pendingwert und ausdrückliche Profilkühlung bleiben unverändert; Kalibrierung/Besitzsperren maßgeblich; Tests in `test_cooling_state_342990.py`, `test_cpu_defaults_and_case_pwm_3429152.py`, `test_profile_startup_policy_3429155.py` |
| Navigationseinstellungen | 1.0 | `src/modules/navigation_settings/v1_0/` | 17 zweispaltige Statuskarten, davon 16 mit Sichtbarkeitsschalter; Einstellungen bleiben ohne Ausschalter erreichbar; Wiederherstellung aller optionalen Module | Reine Sichtbarkeit; Übersicht, Einstellungen, Navigationsanker und Hilfe bleiben erreichbar; keine Hardwareaktivierung/-beendigung |
| Anwendungsaktivierung | 1.0 | `src/modules/application_activation/v1_0/` | Private lokale `show`-Nachricht aktiviert das vorhandene Hauptfenster; ausschließlich `--autostart` entfernt Desktop-Starttokens; `autostart.py` korrigiert beim expliziten Benutzerupdate alte Startziele unter Erhalt der Aktivierungswahl | Versioniertes Koordinationsmodul unterhalb der bestehenden Prozess-/Hardware-Sperre |
| Anwendungsabschluss | 1.1 | `src/modules/application_shutdown/v1_1/` | `process_cleanup.py` beendet den eigenen Pipe-Helfer zuerst über EOF; `sequence.py` isoliert Abschaltphasen; `diagnostics.py` interpretiert das begrenzte Journal; `watcher.py` erkennt Elternprozessende und räumt ausschließlich dokumentierte OHC-Kinder auf; `restart.py` wartet PID-startzeitgeprüft auf das Ende der alten Einzelinstanz vor dem Relaunch. Der RGB-Abschlusslichtschritt liegt nach Effektstopp und vor Sperren-/Enginefreigabe | Firmware-Guard behält seinen eigenen Pfad; Wiederanlauf von CoolerControl ist bei fehlender Polkit-Freigabe best-effort und wird protokolliert; Neustart überspringt Abschlusslicht |
| Fensterleiste | 1.2 | `src/modules/window_chrome/v1_2/` | Eigene Hauptfensterleiste, compositor-delegierte Größenänderung, explizit verfolgte Randcursor-Freigabe und 48×42-Pixel-Schließfläche bis in die obere rechte Ecke | Fensteraktionen umgehen den Größenänderungsrand; OHC bewegt/fängt die Maus nicht und ändert kein KDE-Zeigerthema außerhalb des ausdrücklichen Desktop-Designwegs |
| UI-Leistung und SSD-Cache | 1.1 | `src/modules/ui_performance/v1_1/` | `gallery_preparation.py` reserviert endgültige Reihenhöhe; `dynamic_text.py` verfolgt späte Reitertitel; `memory.py` sammelt nach Navigation/Minimieren verzögert Zyklen; `controller.py` verschiebt Cachepflege bis vier bis fünf Sekunden nach der letzten Eingabe und startet sie mit niedriger Nice-/Idle-I/O-Priorität; `maintenance.py` arbeitet in kooperativen Portionen und liefert begrenzte Laufzeittelemetrie | Keine periodische Speicheraufgabe oder private SSD-Auslagerung; Cache enthält nur regenerierbare OHC-Dateien, Originale und aktive Hardwaredateien bleiben unverändert |
| UI-Themes | 1.0 | `src/modules/ui_themes/v1_0/` | `light.py`, `dark.py` und `studio.py` liefern Paletten-/Semantikwerte; `controller.py` wendet die getrennten reinen `style_base.py`-/`style_controls.py`-Qt-Selektoren einschließlich Kühlungs-Sicherheitsfläche und adaptiver Diagnose-/Gehäuse-/Temperaturtabellen an | Reines Darstellungsmodul; Systemmodus übernimmt die native Palette und passende Semantikwerte, keine Hardwarelogik |
| PC-Gehäuseprofile | 1.5 | `src/modules/pc_case_profiles/v1_5/` | `editor_sections.py` ordnet lebende Felder in Spalten/Reitern; `inline_editor.py` hält Entwürfe bis Speichern/Abbrechen/Escape/Schließen offen; `profiles.py` validiert den vollständigen einstellungsbasierten RGB-/Lüfter-Topologiesnapshot; `controller.py` synchronisiert CPU_FAN-/PUMP_FAN-/Gehäusezuordnungen in das ausgewählte Profil und bestätigt Konflikte; `case_renderer.py` zeichnet 30 originale Modellansichten; `workspace.py`/`case_page.py` besitzen Gehäuse-Seite und fähigkeitsabhängige Topologie; `spatial_layout.py` verwaltet Richtung, Tempo, echten LED-Reihenfolgeeditor und selbst gemessene Beziehungen | Raumdaten und Zuordnungen sind Einstellungen, keine elektrische Erkennung; Profilübernahme schreibt keine Hardware; keine Kalibrierung/Aktivierung oder Hardwarewrites durch Zuordnung/Abstand; keine Herstellerbilder oder erfundene Maße/LED-Topologie |
| Programme | 1.0 | `src/modules/programs/v1_0/` | `model.py` liest begrenzt Desktop-Einträge und validiert Profile/Grundordner; `github_release.py` prüft offizielle GitHub-Releasepläne, schreibt Assets, beide Source-Archive, Manifest und SHA256SUMS atomar und liefert nur tatsächlich vorhandene größenpassende AppImages zur Profilwahl; `install_plan.py` baut validierte Flatpak-/Snap-/AppImage-Pläne; `page.py` besitzt Inventar, Suche, Profilverwaltung und getrennte Hintergrundarbeiter | Keine Ausführung entdeckter Desktop-`Exec`; GitHub nur nach Klick, erlaubte HTTPS-Hosts, höchstens 100 Assets/1 GiB je Datei/4 GiB gesamt, keine Überschreibung; AppImage-Zuordnung nur aus dem geprüften heruntergeladenen Plan; Installationsplan sichtbar und nochmals bestätigt, kein Shellaufruf, Systempakete fail-closed |
| Lokalisierung | 1.0 | `src/modules/localization/v1_0/` | Je ein vollständiges Laufzeitmodul für Deutsch, Englisch, Spanisch und Französisch; 2.507 gleiche Nachrichten-Einträge; reine vierfache Zusatzblöcke liegen budgetgerecht in `snapshot_messages.py`, `next_version_messages.py`, `program_messages.py`, `lifecycle_messages.py`, `shutdown_lighting_messages.py`, `rgb_speed_messages.py`, `retained_lcd_messages.py`, `retained_feature_messages.py`, `retained_ui_messages.py`, `content_ui_messages.py`, `profile_background_messages.py`; Programme sowie Reifegrad-, Snapshot-, GPU-, RGB-, Gehäuse-, CPU- und Hardwaretexte werden werttreu übersetzt | Versionierter Modulordner; alle vier Sprachmodule bei jeder sichtbaren Änderung atomar pflegen |
| NZXT Kraken | 1.0 legacy | `src/nzxt_backend.py`, `src/kraken_sensors.py`, `src/kraken_cam_streamer.py`, `src/kraken_lcd_designs.py`, `src/nzxt_rgb.py` | Erkennung, Sensoren, LCD-Transport und RGB | Ordner-Migration ausstehend |
| Mainboard-Kühlung | 1.0 legacy | `src/mainboard_fan_control.py`, `src/ohc_fan_helper.py`, `src/cooling_ownership.py` | hwmon/NCT6687, Polkit-Helfer und Besitzschutz; freundlicher Kernelname getrennt von `PWM N`; bestätigter Gesamtzuordnungsreset bei Kurvenerhalt; konstantes 100-%-Leistungsprofil und optionale `pwmN_mode`-Umschaltung; Kurvenschreibvorgänge werden bei Zustandsänderung, Notfall oder spätestens nach 60 Sekunden einmal gebündelt protokolliert | Ordner-Migration ausstehend; Rücksetzen stoppt laufende OHC-Regelung und gibt zuerst an Firmware/BIOS zurück |
| Mainboard-Treiber-/MOK-Assistent | 1.1 | `src/modules/mainboard_driver_setup/v1_1/` | Asynchron geprüfter read-only Distributions-/DMI-/Secure-Boot-/MOK-/Modulstatus; getrennte feste Ubuntu-/Fedora-/Arch-Abhängigkeitsbefehle; Ubuntu-Update und Installation separat; vorhandener fester Checkout nur per `pull --ff-only`; gemeinsame DKMS-Schritte; MSI-X870-Optionen nur bei passender DMI-Erkennung; optionale per-user Polkit-Dauerfreigabe als fünfter Schritt | Fremdquellen werden nie automatisch verändert; Konfliktordner/Distributionen fallen geschlossen aus; Dauerfreigabe gilt nur für den festen Lüfterhelfer; kein Passwortzugriff, automatischer Neustart oder Secure-Boot-Umbau |
| OpenRGB Studio | 1.15 | `src/modules/rgb_studio/v1_15/`, `src/openrgb_integration.py`, `src/openrgb_sdk.py`, `src/rgb_devices.py`, `src/rgb_effects.py`, Legacy-UI in `src/kraken_control.py` | Kompakte Designkarten skalieren bis sechs Spalten; 13 eigene Algorithmen und 34 Vorlagen enthalten acht räumliche Designs; Doppelpuls/Fusion wiederholen sich nahtlos. Kategorie-/Galeriewechsel synchronisieren die Hauptnavigation. `led_topology.py`/`led_topology_store.py`/`led_topology_editor.py` besitzen umkehrbare physische Lüfterketten, globale räumliche Richtung und pro Anschluss echte LED-Reihenfolge; GPU-Lichtverlauf, Sichtassistent, Geräteframe-Schreibweg und Besitzmodule behalten ihre Grenzen. Die gemeinsame monotone Effektzeit bleibt auch bei langsamen Mehrgeräte-Batches zeitgetreu. `shutdown_lighting.py` persistiert Weiß/Einzelfarbe/nativen Rainbow und schreibt synchron vor Besitzfreigabe. Unter Ubuntu verwenden reine CLI-Clients `--nodetect`; Fedora behält den bestehenden Befehl | Native GPU-Effekte bleiben Standard; External Control nur bei ausdrücklich zugeordneter ausgewählter Direct-Quelle; keine elektrische LED-Erkennung, keine zusätzliche Transportverbindung, keine garantierte optische FPS; Abschlusslicht nur beim echten Beenden unter bestehender Auswahl/Freigabe; Host besitzt Loopback-Transport und Besitzprüfung |
| Profile Bundle | 1.0 | `src/modules/profile_bundle/v1_0/` | `values.py` verlustfreie Typen/Pfadumsetzung; `archive.py` begrenztes lokales ZIP/Prüfsummen; `controller.py`/`worker.py` UI/eigener Datei-Arbeiter; `restore.py` bestätigte Start-Wiederherstellung/Rückfallkopie; `legacy_profiles.py` bestehender JSON-Austausch | Keine Hardwarewrites; importierte Automatik/Regelung/Kalibrierung bis zur lokalen Bestätigung deaktiviert; bestehender JSON-Austausch bleibt |
| Corsair/OpenLinkHub | 1.0 legacy | `src/openlinkhub_integration.py`, `src/openlinkhub_mouse_visuals.py` | Validierte lokale API und Mausdarstellung | Geräteintegration bleibt ohne direkten USB-Pfad |
| OpenLinkHub-Update | 1.0 | `src/modules/openlinkhub_update/v1_0/` | `policy.py` prüft festen offiziellen Release-Endpunkt, Paket-/User-Service-Pfade, Archivgröße und GitHub-SHA-256; `controller.py` baut Seite/Bestätigungsablauf; `apply_user_space.py` setzt mit Datenübernahme, Backup und Rollback ein | Nur nach UI-Bestätigung; Web-UI ist Bestandteil desselben Pakets; kein Remote-Skript-Piping |
| OpenLinkHub Nexus | 1.0 | `src/modules/openlinkhub_nexus/v1_0/` | Validiert und installiert 640×48-Hintergründe sowie begrenzte Touch-Manifeste mit Backup und atomarem Datenbanktausch | Ausschließlich erkannte Benutzerinstallation; OpenLinkHub bleibt USB-Besitzer |
| Wallpaper Engine for KDE | 1.3 | `src/modules/wallpaper_engine/v1_3/` | Schreibgeschützte Steam-/Video-Erkennung mit zentralem Katalogcache; Plasma-/D-Bus-Steuerung; SHA256-geprüfter optionaler Fedora-Installer; lokalisierter Assistent mit bestätigter KDE-Hilfspaketinstallation; sichtbarkeitsgebundene Galerie mit persistenten Vorschaubildern | Versteckte Seite stoppt die Thumbnail-Warteschlange; keine Upstream-Dateien oder Medien enthalten; Paketquellen bleiben unverändert und das Passwort ausschließlich bei Polkit |
| Fensterplatzierung | 1.5 | `src/modules/window_placement/v1_5/` | Bildschirmwahl, normale Geometrie und unabhängige Startmodi; `confirmation.py` trennt Qt-Hinweise von KWin-Bestätigung; `kwin_controller.py` startet einen begrenzten Hintergrundprozess; `kwin_bridge.py` nutzt einen temporären, PID-/titelgebundenen KWin-Skript-/D-Bus-Rückkanal zur Ist-Ausgabe und gezielten OHC-Verschiebung | Tray-Autostart bleibt verborgen; keine globale KWin-Regel oder Dauerkorrektur, Startprofile dürfen keine zweite Platzierungsfolge auslösen; Fremdfenster bleiben unberührt |
| Desktop-Designs | 1.0 legacy | `src/desktop_shell.py`, `src/desktop_designs.py`, `src/desktop_assets.py` | KDE-Designvorschau, Backup und Anwendung | Ordner-Migration ausstehend |
| Gemeinsame Infrastruktur | 1.0 legacy | `src/app_constants.py`, `src/command_backend.py`, `src/privacy_logging.py`, `src/window_diagnostics.py`, `src/hardware_diagnostics.py`, `src/log_view_support.py`, `src/temperature_utils.py`, `src/ui_layout.py`, `src/dashboard_layout.py` | Identität, Prozesse, Datenschutz, read-only Sensor-Plausibilitätsprüfung, getrennte Log-Ansichten, Diagnose, Dashboard-Raster und Übersichtshinweise ohne Hardware-Schreibzugriff | Ordner-Migration nur bei konkreter Änderung |
| Laufzeitprotokoll | 1.0 | `src/modules/runtime_logging/v1_0/`, `src/log_view_support.py`, `src/privacy_logging.py` | Reiner 60-Minuten-Ringpuffer für allgemeine/Hardware-Ansicht und Klassifizierung dauerhaft zu sichernder Fehler | 30.000 Zeilen/4 MiB im RAM; privates `errors.log` rotiert bei 2 MiB auf ungefähr 1 MiB |
| Absturzwiederherstellung | 1.0 | `src/modules/crash_recovery/v1_0/`, `src/log_view_support.py`, `src/privacy_logging.py` | Privater begrenzter JSONL-Ring, Fünf-Minuten-Snapshot und Wiederaufnahme im nächsten sichtbaren/Sitzungslog; Fatal-Signal-Python-Stacks | Nur bereits datenschutzbereinigte Anwendungszeilen im Ring; `0600`, kein Folgen symbolischer Links, höchstens 2 MiB; keine Hardwareaktion |
| Release-Paketierung | 1.0 | `scripts/build_release.py`, `scripts/build_rpm_fallback.py`, `scripts/backup_release.py`, `scripts/check_release.sh`, `packaging/` | Reproduzierbare Pakete plus atomare externe Sicherung der zwei neuesten vollständigen Versionssätze nach `RELEASE_BACKUP_POLICY.md`; das DEB akzeptiert altes `policykit-1` oder aktuelles `polkitd` plus `pkexec`; normale RPM-Spec und Standardbibliothek-Fallback enthalten dieselben Systemhelfer/Policies; `install_runtime_tree` normalisiert nur eigene Stage-Verzeichnisse auf 0755; `packaging/` bündelt udev-Regel, Polkit-Policy, Metainfo, Desktop-Vorlage, Icon und Hilfsskripte, die installiert flach neben `src/kraken_control.py` liegen | Aktiv; Fedora/RPM-Abhängigkeiten, Host-/Quellrechte und Dateiinhalte unverändert |

## Ordnerstruktur der Dokumentation

| Ordner | Inhalt |
|---|---|
| Repository-Wurzel | `README.md`, `LICENSE`, `CITATION.cff`, `AGENTS.md` (kurzer Wegweiser auf `docs/ai/AGENTS.md`) |
| `src/` | Gesamter Anwendungscode: alle `*.py` (Einstieg `kraken_control.py`), `assets/`, `modules/`, `test-gifs/`. Der Ordner spiegelt die flache installierte Programmstruktur; Tests importieren aus `ROOT / "src"` |
| `docs/` | `INSTALL.md`, `CHANGELOG.md`, `README.en.md` sowie die Unterordner unten |
| `docs/project/` | Architektur, Entscheidungen, Projektstatus, Roadmap, Modulregister/-karte, Komponenten- und Funktionsversionen, Projektdokumentationen, Release-Backup-Richtlinie, Veröffentlichungsleitfaden, Autoren, Drittanbieter-Hinweise |
| `docs/ai/` | `AGENTS.md` (vollständige Agentenanweisungen), `CLAUDE.md`, KI-Arbeitsanleitungen (`AI_DEVELOPMENT_GUIDE.md`, `AI_HANDOFF.md`, `AI_ASSISTANCE.md`, Cursor-/LM-Studio-Einrichtung, lokaler KI-Startprompt) |
| `docs/hardware/` | Gerätelisten, Profile, CPU-Profile, RGB-Studio, OpenLinkHub-Anbindung, USB-Mitschnittauswertung, Desktop-Designs, animierte Hintergründe |
| `docs/security/` | Sicherheitsaudits, Datenschutz, `SECURITY_SCAN_REPORT.json` |
| `docs/releases/` | `RELEASE_NOTES_v*.md`, `RELEASE_CHECKLIST.md` |
| `docs/images/` | Screenshots und Render-Belege |
| `packaging/` | `install.sh`, `uninstall.sh`, `VERSION`, `BUILD_CHANNEL` sowie Distributionsdateien (siehe Release-Paketierung) |
| `.github/` | Workflows, Vorlagen, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, `SECURITY.md` |

## Erlaubte Abhängigkeiten für Levita LCD 1.7

```text
src/thermalright_display_ui.py
  -> src/modules/lcd_levita_shutdown/v1_0/guard.py
  -> src/modules/levita_daemon_health/v1_1/model.py
  -> src/modules/lcd_levita/v1_7/layout_canvas.py
  -> src/modules/lcd_levita/v1_7/layout_model.py
  -> src/modules/lcd_levita/v1_7/theme_adapter.py
  -> src/modules/lcd_levita/v1_7/panel_geometry.py
  -> src/modules/lcd_levita/v1_7/runtime_policy.py
  -> src/modules/lcd_levita/v1_7/motion_renderer.py
  -> src/modules/lcd_levita/v1_7/motion_compositor.py
  -> src/modules/levita_performance/v1_1/policy.py
  -> src/modules/lcd_media_manager/v1_0/model.py + dialog.py
  -> src/modules/responsive_gallery/v1_0/layout.py
  -> src/thermalright_display.py

layout_canvas.py -> layout_model.py + panel_geometry.py + stabile Geometrie aus src/thermalright_display.py
theme_adapter.py -> layout_model.py + optional installiertes TRCC-Lesemodul
panel_geometry.py -> keine Qt-, UI- oder Hardwareabhängigkeit
runtime_policy.py -> keine Qt-, UI- oder Hardwareabhängigkeit
stream_recovery.py -> keine Qt-, UI- oder Hardwareabhängigkeit
layout_model.py  -> keine Qt-, UI- oder Hardwareabhängigkeit
lcd_levita_shutdown/v1_0/guard.py -> Python-Standardbibliothek + vorhandener TRCC-Daemon; kein direkter USB-Zugriff
levita_daemon_health/v1_1/model.py -> Python-Standardbibliothek + read-only /proc sowie erneut validiertes Signal an den exakten Eigenprozess; kein USB-Zugriff
```

`config1.dc` wird ausschließlich gelesen und niemals verändert. Editierbare Laufzeit-Themes liegen im OHC-Cache, verwenden `trcc.json` und verweisen nur symbolisch auf lokale Originalmedien.

## Gezielte Tests

PC-Gehäuseprofile 1.2: `topology_labels.py` liest deklarierte LED-Zonenlängen
und gemeldete SYS_FAN-Zuordnungen für dreizeilige Seitenbeschriftungen mit
Hinweislinien. Unbekannt bleibt —; mehrere Controllerzonen werden nicht als
erratene Komponenten-Gesamtlänge summiert. Anschlussnotizen begrenzen nur die
Anzeige, niemals die bestehende Route. Regressionen prüfen 30 persönliche
GPU-/24-Halterungs-LEDs, SYS_FAN4 bei unverändertem pwm6 und kollisionsfreie
dreizeilige persönliche Callouts.

| Modul | Pflichttests |
|---|---|
| Levita LCD 1.7 / Leistung 1.1 | `tests/test_levita_layout_module_342918.py`, `tests/test_levita_performance_342972.py`, `tests/test_studio_library_342933.py`, `tests/test_thermalright_display_3429.py`, `tests/test_thermalright_preview_queue_342914.py`, `tests/test_thermalright_ui_static_3429.py`, Offscreen-UI-Aufbau |
| Laufzeitprotokoll 1.0 / Levita-Daemongesundheit | `tests/test_runtime_logging_342976.py`, `tests/test_runtime_logic_stub.py`, `tests/test_security_static.py`, `tests/test_thermalright_ui_static_3429.py`, `tests/test_lcd_usb_owner_conflict_3429155.py`, `tests/test_lcd_health_module_globals_3429155.py` |
| Absturzwiederherstellung 1.0 | `tests/test_crash_recovery_3429119.py`, `tests/test_exit_journal_labels_342991.py`, `tests/test_slot_argb_routes_342985.py`, `tests/test_gpu_fan_stress_3429107.py`, `tests/test_security_static.py` |
| Levita LCD-Abschaltwächter 1.0 | `tests/test_levita_shutdown_guard_342953.py`, `tests/test_thermalright_preview_queue_342914.py`, `tests/test_security_static.py`, Offscreen-UI-Aufbau |
| Display-Effekte 1.11 / Responsive Galerien 1.0 / LCD-Medienmanager 1.0 | `tests/test_display_preview_342995.py`, `tests/test_display_effects_342954.py`, `tests/test_media_manager_reports_342975.py`, `tests/test_full_ui_build_34291.py`, `tests/test_thermalright_ui_static_3429.py`, echter Offscreen-MP4-Decodiertest |
| Anzeigeeinstellungen 1.0 | `tests/test_full_ui_build_34291.py`, `tests/test_window_placement_342942.py`, `tests/test_levita_performance_342972.py` |
| UI-Themes 1.0 | `tests/test_ui_themes_342961.py`, `tests/test_full_ui_build_34291.py`, helle/dunkle Offscreen-Sichtprüfung |
| Hauptfenster und Seitenkomposition | `tests/test_ui_layout.py`, `tests/test_thermalright_cooling_3429.py`, `tests/test_mainboard_fan_ui_static.py`, Offscreen-UI-Aufbau |
| Kühlungszustand 1.0 / Profilstart | `tests/test_cooling_state_342990.py`, `tests/test_cpu_defaults_and_case_pwm_3429152.py`, `tests/test_profile_startup_policy_3429155.py`, `tests/test_rgb_profile_autostart_342943.py` |
| Hardware-Unterbauten / Temperaturverlauf 1.2 / Kühlungssicherheit 1.0 / Profile | `tests/test_hardware_backends_temperature_history_342966.py`, `tests/test_temperature_profiles_safety_342967.py`, `tests/test_media_manager_reports_342975.py`, `tests/test_full_ui_build_34291.py`, Offscreen-Canvas-Aufbau |
| Hardware-Checker 1.0 | `tests/test_hardware_checker_342996.py`, `tests/test_full_ui_build_34291.py`, `tests/test_localization_module_342952.py`, `tests/test_security_static.py` |
| Hardware Fix 1.0 | `tests/test_hardware_fix_3429149.py`, `tests/test_full_ui_build_34291.py`, `tests/test_security_static.py` |
| Snapshot-Manager 1.0 | `tests/test_snapshot_manager_3429127.py`, `tests/test_full_ui_build_34291.py`, `tests/test_localization_module_342952.py`, `tests/test_security_static.py`, `tools/render_snapshot_manager.py` |
| GPU-Steuerung / GPU-Profile 1.0 | `tests/test_gpu_profiles_3429120.py`, `tests/test_gpu_control_3429102.py`, `tests/test_gpu_fan_stress_3429107.py`, `tests/test_gpu_backend_version_3429103.py`, `tests/test_dependency_helper.py`, `tests/test_full_ui_build_34291.py`, `tests/test_localization_module_342952.py`, `tests/test_security_static.py` |
| Anwendungsaktivierung 1.0 | `tests/test_application_activation_342954.py`, `tests/test_full_ui_build_34291.py` |
| Anwendungsabschluss 1.1 | `tests/test_application_shutdown_342986.py`, `tests/test_rgb_shutdown_lighting_3429169.py`, `tests/test_exit_journal_labels_342991.py`, `tests/test_mainboard_fan_control.py`, `tests/test_levita_shutdown_guard_342953.py`, `tests/test_security_static.py`, Offscreen-UI-Aufbau |
| Lokalisierung 1.0 | `tests/test_localization_module_342952.py`, `tests/test_full_ui_build_34291.py`, `tests/test_runtime_logic_stub.py`, `tests/test_security_static.py`, Offscreen-UI-Aufbau |
| OpenLinkHub-Update 1.0 | `tests/test_openlinkhub_update_342954.py`, `tests/test_openlinkhub_integration.py`, `tests/test_security_static.py` |
| Profile Bundle 1.0 / OpenRGB Studio 1.13 / PC-Gehäuseprofile 1.3 | `tests/test_gpu_strip_smoothing_342989.py`, `tests/test_profile_bundle_led_topology.py`, `tests/test_personal_wiring_fan_library.py`, `tests/test_rgb_recovery_342986.py`, `tests/test_slot_argb_routes_342985.py`, `tests/test_case_resize_342984.py`, `tests/test_rgb_selection_342984.py`, `tests/test_case_workspace_342983.py`, `tests/test_effect_sampling_342983.py`, `tests/test_compact_ui_case_profiles_342959.py`, `tests/test_gpu_header_342982.py`, `tests/test_gpu_lighting_342981.py`, `tests/test_rgb_profile_autostart_342943.py`, `tests/test_openrgb_integration.py`, `tests/test_openrgb_sdk.py`, `tests/test_ene_dram_cold_boot_34221.py`, `tests/test_rgb_studio_ui_342937.py`, `tests/test_visibility_rendering_342978.py`, Offscreen-UI-Aufbau |
| Wallpaper Engine for KDE 1.3 / UI-Leistung 1.1 | `tests/test_wallpaper_engine_342942.py`, `tests/test_ui_performance_342979.py`, `tests/test_full_ui_build_34291.py`, `tests/test_ui_customization_3425.py` |
| Fensterplatzierung 1.5 / Fensterleiste 1.2 | `tests/test_window_placement_342942.py`, `tests/test_window_mapping_confirmation_342974.py`, `tests/test_kwin_compositor_3429105.py`, `tests/test_compact_ui_case_profiles_342959.py`, `tests/test_visibility_rendering_342978.py`, `tests/test_full_ui_build_34291.py` |
| Modulstruktur/Regeln | `tests/test_module_registry_342918.py`, `tests/test_modularization_3427.py`, `tests/test_agent_project_memory_3426.py` |
| Release-Paket | `tests/test_release_backup_342936.py`, `tests/test_polkit_package_permissions_3429154.py`, `tests/test_rpm_fallback.py`, `tests/test_thermalright_ui_static_3429.py`, `scripts/check_release.sh` |

## Legacy-Ausnahmen mit aktivem Zerlegungsplan

| Datei | Grund | Nächster Schnitt |
|---|---|---|
| `src/kraken_control.py` | Historischer Anwendungseinstieg mit Kompatibilitätsnamen | Jeweils eine Seite oder einen Controller pro Version in einen Modulordner extrahieren |
| `src/thermalright_display_ui.py` | Bereits laufend entwickelte Karten-, Vorschau- und Prozessoberfläche | Katalog/Thumbnail-Warteschlange als nächstes getrennt auslagern; keine neue Layout-Fachlogik mehr hier ablegen |
| `src/modules/localization/v1_0/{de,en,es,fr}.py`, `snapshot_messages.py`, `next_version_messages.py` | Vier vollständige Laufzeit-Sprachmodule mit 1.851 stabilen Daten-IDs; verlustfrei komprimierte Datenliterale ohne Fachlogik, Zusatztexte als gemeinsame reine Vier-Sprachen-Datenblöcke | Vier-Sprachen-Vertrag und Grenze jeder Sprachdatei unter 78.000 Zeichen beibehalten; alle Sprachen/IDs gemeinsam ändern |

## Änderungsregister

| Datum | Modul | Version | Änderung |
|---|---|---:|---|
| 09.11.26 | OpenRGB Studio / PC-Gehäuseprofile / Anwendungsabschluss / Lokalisierung | 1.15 / 1.5 / 1.1 / 1.0 | Gemeinsame Hardware-/Gehäuse-Effektzeit übernimmt das vollständige monotone Zeitintervall. Der Nutzerlog belegt 350–370 ms für fünf seriell bestätigte Direct-Geräte (ca. 2,7 Gesamtframes/s); eine geordnete persistente Loopback-Verbindung je Controller überträgt verschiedene Controller nun parallel, bei weiter einem OHC-Arbeiter, vollständigen Frames, Latest-frame-wins und 25-Hz-Obergrenze. GPU-/Halterungsstreifen erhalten dieselbe Umlaufdauer wie die Galerie. Abschlussbeleuchtung setzt beim echten Beenden Weiß, Einzelfarbe oder gemeldeten nativen Rainbow; Tray und Neustart bleiben wirkungslos. Reine Regressionen ergänzt; optische Prüfung am Gerät bleibt offen. |
| 05.11.26 | LCD-Vorschau / Snapshot-Prozesslaufzeit / Release-Test | Testfix / 1.0 / Testfix · Anwendung 3.4.29.168 | Echte verschachtelte Scroll-Sichtbarkeit wird in einer kontrollierten Qt-Hierarchie geprüft; vollständige Anwendung prüft getrennt Medienwahl, Pause/Fortsetzung, Bestätigung und vier Sprachen ohne virtuelle Desktopannahme. Spätes Activity-Probe-Signal nach Zerstörung seines Qt-Eigentümers wird ohne Neustart verworfen. Produktive UI-, Profil-, Vorschau- und Hardwarepfade unverändert. |
| 05.11.26 | LCD-Vorschau / Release-Test | Testfix / Testfix · Anwendung 3.4.29.167 | Isolierter Vorschauvertrag setzt vor Fensterbau den Levita-Kühlertyp in seinem privaten QSettings-Bereich, sodass die LCD-Seite auf hardwarefreiem Runner und Besitzerrechner gleich vorhanden ist. Produktive USB-Erkennung und Hardwarepfade unverändert. |
| 05.11.26 | LCD-Vorschau / Release-Test | Testfix / Testfix · Anwendung 3.4.29.166 | Isolierter Vorschau-Kindprozess erhält `QT_QPA_PLATFORM=minimal` ausdrücklich in seiner eigenen Umgebung, sodass ein zuvor von der Gesamtsuite geerbtes `offscreen` den Sichtbarkeitsvertrag nicht überschreibt. Produktive QPA-/Vorschaupfade unverändert. |
| 05.11.26 | LCD-Vorschau / Release-Test | Testfix / Testfix · Anwendung 3.4.29.165 | Isolierte echte Viewport-Prüfung nutzt Qt `minimal`, das headless eine definierte Fensterexposition liefert; GitHubs `offscreen`-Backend garantiert diese Semantik nicht. Responsives 760×700-Fenster sowie Scroll-, Sichtbarkeits- und Videoverträge bleiben geprüft; produktive QPA-Auswahl unverändert. |
| 05.11.26 | LCD-Vorschau / responsive Oberfläche / Release-Test | Testfix / geprüft / Testfix · Anwendung 3.4.29.164 | Reale Offscreen-Viewport-Prüfung verwendet ein responsives 760×700-Fenster innerhalb der kleinsten virtuellen CI-Bildschirmfläche statt eines dort unmöglichen nativen 1600×1000-Fensters. Echtes Scrollen, Sichtbarkeit und Video-Pause/-Fortsetzung bleiben geprüft; produktive Oberfläche unverändert. |
| 04.11.26 | LCD-Vorschau / Release-Test | Testfix / Testfix · Anwendung 3.4.29.163 | Isolierte Offscreen-Prüfung wiederholt den echten Scrollbereich-Sichtbarkeitsaufruf während der begrenzten Layoutstabilisierung. Damit wird auch ein Runner geprüft, dessen endgültige Geometrie erst nach dem ersten Aufruf steht; produktive Vorschau unverändert. |
| 04.11.26 | LCD-Vorschau / Snapshot-Prozesslaufzeit / Release-Test | Testfix / 1.0 / Testfix · Anwendung 3.4.29.162 | Isolierte Offscreen-Vorschau wartet begrenzt auf die reale Viewport-Geometrie statt eine feste Runner-Geschwindigkeit vorauszusetzen und beendet ihren Snapshot-Probe vor dem Testfenster. Produktive Vorschau-, Snapshot- und Hardwarepfade bleiben unverändert. |
| 04.11.26 | LCD-Medienverwaltung / Release-Test | 1.0 / Testfix · Anwendung 3.4.29.161 | Gemerkte eigene Medien bleiben beim Abwählen auch auf Rechnern ohne systemweiten TRCC-Standardkatalog ausgeblendet; der eingebaute OHC-Katalog bleibt verfügbar und Dateien werden nicht verändert. Hardwarefreier Levita-Test wählt weiterhin den isolierten Kühlertyp. |
| 04.11.26 | Release-Test / Feature-Reifegrade / Funktionsmodule / Navigation / Lokalisierung | Testfix / 1.0 / 1.0 / 1.0 / 1.0 · Anwendung 3.4.29.160 | Vollständiger Levita-UI-Test wählt isolierten Kühlertyp unabhängig von Host-USB; produktive Erkennung unverändert. Zentrale unabhängige Feature-Versionen und Alpha/Beta/Release-Candidate/Stabil-Reifegrade in Funktionen-&-Bereiche- und Navigationskarten; reine Darstellung ohne Persistenz-/Besitz-/Hardwarewirkung. Vier Sprachquellen, OHC-eigener öffentlicher Designkatalog; Import-, Editor-, Vorschau-, Gehäuse-Lüfteranimations- und Übergabefunktionen erhalten. |
| 31.10.26 | OpenRGB Studio / gemeinsame Infrastruktur / Levita-Orchestrierung | 1.15 / 1.0 legacy / Legacy · Anwendung 3.4.29.158 | Dokumentierte SDK-6-Profiländerungsmeldung 157 mit begrenztem nullterminiertem Payload als asynchrone Meldung verarbeitet, ohne ACK-10-Schreibbestätigung oder MSI-Mystic-Light-Frame zu verwerfen; unbekannte/malformed Pakete bleiben gesperrt. TRCC-GPU-Taktgrenzkorrektur erst nach drei aufeinanderfolgenden gültigen 5-s-Proben aufgehoben; fehlende/fehlerhafte Messung setzt Erholungsnachweis zurück. Keine Hardwarehoheit, LED-Zahl, Profil-, Berechtigungs- oder Schreibpfadänderung. |
| 20.10.26 | Programme / Levita-Orchestrierung / Lokalisierung | 1.0 / Legacy 3.4.29.157 / 1.0 · Anwendung 3.4.29.157 | Letzten umsetzbaren Roadmap-Punkt geschlossen: nur ein tatsächlich heruntergeladenes, im inspizierten Releaseplan enthaltenes und größenpassendes AppImage kann direkt einem ausgewählten AppImage-Profil zugeordnet werden; spätere Pfad-/ELF-/AppImage-Prüfung bleibt getrennt. Belegten Levita-Eigenkonflikt anhand registrierter Sitzungs-PID, UID und exaktem Daemonkommando vom fremden USB-Besitzer getrennt; eigener Daemon erhält einmal den bestehenden begrenzten Neustart mit Designwiederherstellung, fremde/vorhandene/abweichende Prozesse bleiben unangetastet. Fünf neue Quellen in vier Sprachen und gezielte Regressionen ergänzt; reale Fedora- und optische RGB-Nachweise bleiben offen. |
| 20.10.26 | Programme / Navigation / Lokalisierung | 1.0 / 1.0 / 1.0 · Anwendung 3.4.29.156 | Eigenständiger optionaler Programme-Reiter mit begrenzter asynchroner Desktop-Inventur, Suche, frei wählbarem absolutem Grundordner und validierten Profilen für System/Flatpak/Snap/AppImage. Getrennter ausdrücklicher GitHub-Check/Download für höchstens 100 offizielle Assets plus beide Source-Archive; Host-/Größen-/Byteprüfung, SHA256SUMS, JSON-Manifest, atomarer neuer Versionsordner und keine Überschreibung. Validierte Flatpak-/Snap-/AppImage-Pläne zeigen vor Ausführung den exakten Vorgang und benötigen Bestätigung; keine entdeckte Desktop-Ausführung, Shell oder uneindeutiges Systempaket. Navigation/Modulsichtbarkeit und 58 neue Quellen in vier Sprachen ergänzt. `.151`–`.156` gegen Code/Tests/Status abgeglichen; nur echte Fedora- und optische RGB-Nachweise bleiben offen. |
| 20.10.26 | PC-Gehäuseprofile / Projektarchitektur | 1.5 / 1.0 · Anwendung 3.4.29.156 | Reine, auf 512 Farben begrenzte Cachefunktion hebt nur die Darstellung der Lüfter-RGB-Segmente moderat an; Schwarz bleibt aus, Farbabstufungen, Effektphase, physische Wege, Hardwareausgabe und versteckte Timer bleiben unverändert. Aktive Roadmap in Repository-, Hardware- und Langfristarbeit getrennt; profilgetriebene Optimierung und schrittweise Modultrennung festgehalten, vollständiger Rust-Neubau verworfen. Gezielte Pure-/Qt-Regression erweitert; Release/Paket/optische Hardwarebestätigung offen. |
| 06.10.26 | PC-Gehäuseprofile / RGB Studio / Lokalisierung | 1.5 / 1.15 / 1.0 · Anwendung 3.4.29.156 | Frische LED-Entwürfe bei Qt-Polish/Reparent/Eltern-Reaktivierung bedienbar, explizite Usergesten aktivieren Commit ohne automatische Geometrie. Spatial-Wave, lokale Effektumkehr und individuelle Anschlussrechtecke im Worker/Fallback korrigiert; physische Nummerierung bleibt erhalten. Neuer reiner `fan_preview.py` zeichnet begrenzte RGB-Segmente aus gemeinsamer bestätigter Phase; sichtbarer 40-ms-Timer stoppt verborgen, Gehäuserechtecke im Specaufbau gecacht. Draftrefresh/Profilrichtung und fehlender Pfadstatus mit ID 2824 / 2.154 Quellen; vier neue Qt-/Pure-Regressionsdateien, getrennte Fedora-/Ubuntu-Fixtures. Release/Paket/Installation offen. |
| 06.10.26 | Release-Paketierung | 1.0 · Anwendung 3.4.29.155 | Echte Verzeichnisse ausschließlich innerhalb des isolierten DEB-/RPM-Stages einschließlich seiner Wurzel auf 0755 normalisiert; keine chmod-Änderung an Quellen, Symlinkzielen, Stage-Eltern oder bestehenden Hostpfaden. Echter vollständiger Stage-Aufbau unter umask 002 prüft sichere Helper-/Policy-Vorfahren und unveränderte Quellrechte/-inhalte; RPM-Datei-/Abhängigkeitsvertrag bleibt erhalten. |
| 06.10.26 | Kühlungszustand / Levita-Daemongesundheit / LCD-Orchestrierung / Lokalisierung / KI-Anleitungen | 1.0 / 1.1 / Legacy / 1.0 / Anwendung 3.4.29.155 | Reine bekannte NZXT-Setup-/PC-Profilstarttrennung nur bei bestätigtem Ubuntu/Levita ohne bereites NZXT; Pendingwert und explizite Profilkühlung unverändert. Ausdrücklicher USB-Fremdbesitz stoppt unter Ubuntu nur OHC-eigene Wiederholungen und hält Designabsicht; primärer Fehler statt Hintzeile, kein Fremdprozesssignal/FPS-Fallback. Neue Startup-/USB-/dynamische Vier-Sprachen-Regressionen, Sprachquelle 2823 und 2.153 gemeinsame Katalogeinträge. Getrennte Fedora-/Ubuntu-Pfade, native Befehle, Feature-/Design-/Einstellungsbewahrung und ehrlich getrennte Live-Testnachweise verbindlich; Fedora-Codepfade bleiben erhalten. Release-Gate/Paket/Installation noch offen. |
| 06.10.26 | OpenRGB Studio / PC-Gehäuseprofile / TRCC Backend / Release-Paketierung | 1.15 / 1.5 / 1.0 / Anwendung 3.4.29.154 | Vertrauenswürdige Ubuntu-OpenRGB-1.0-Inventur mit vollständigem Listenbefehl; Namenslisten vor Persistenz verworfen; externe GPU-Blockrouten, Gruppenrenderer und Vorschau ohne nativen Detektor. Ubuntu-TRCC-Kindadapter liest RAM-DMI nur über festen argumentfreien root-owned Helfer und eigene Polkit-Aktion; optionale allgemeine Metadaten bleiben unprivilegiert, kein globales Passwortlos-Root. Bestehende vier Sprachvarianten wiederverwendet; Fedora-Kommandos unverändert. |
| 05.10.26 | Levita-Vorschauwarteschlange / Snapshot-Manager / Navigationseinstellungen / UI-Themes / Release-Paketierung | Legacy-Hotfix / 1.0 / 1.0 / 1.0 / Anwendung 3.4.29.153 | Beim schnellen Wechsel von LCD-Designkategorien werden schwache Referenzen auf bereits gelöschte Qt-Vorschaukacheln vor Sichtbarkeitsprüfung und Ergebniszustellung verworfen; Scrollsignale können die Ausnahme nicht wiederholen. Verzögerte Snapshot-Prozessfristen prüfen beim Programmende ebenfalls die Qt-Lebensdauer. Modul-Sichtbarkeit als zweispaltige Karten mit Symbol, Statuspunkt und Schalter; Sidebar-Synchronisierung und Hardwarezustand unverändert. Gelöschte-C++-Kachel-Regressionsprüfung und vollständiger Offscreen-Render bestanden; Fedora unverändert. |
| 05.10.26 | Kühlungszustand / PC-Gehäuseprofile / Navigationseinstellungen / Lokalisierung / Release-Paketierung | 1.0 / 1.5 / 1.0 / 1.0 / Anwendung 3.4.29.152 | Erkannte CPU lädt Standardkurven nur bis zur ersten Nutzeränderung; vollständige CPU_FAN-/PUMP_FAN-/SYS_FAN-Topologie wird konfliktbestätigt im aktiven PC-Profil gespeichert; MSI-X870-Referenzbelegung einmalig nach echten Anschlussnamen; vollständige Modul-Sichtbarkeitsverwaltung; 1.916 gemeinsame Sprachtexte; Fedora-Setup unverändert. |
| 05.10.26 | Mainboard-Treiber-/MOK-Assistent / Lokalisierung / Release-Paketierung | 1.1 / 1.0 / Anwendung 3.4.29.151 | Ubuntu-Aktualisierung und Paketinstallation nach beobachtetem CKB-Next-PPA-Fehler getrennt; Fremdquellen bleiben unverändert; vorhandener fester nct6687d-Checkout wird nur per Fast-Forward aktualisiert; optionale eng begrenzte Lüfter-Dauerfreigabe als Schritt fünf; 1.901 gemeinsame Sprachtexte. |
| 05.10.26 | Mainboard-Treiber-/MOK-Assistent / Lokalisierung / Release-Paketierung | 1.1 / 1.0 / Anwendung 3.4.29.150 | `/etc/os-release` und DMI liefern getrennte Ubuntu-, Fedora- und Arch-Befehle sowie die sichtbare Boardidentität; gemeinsame DKMS-Schritte bleiben gleich, MSI-X870-Optionen werden nur passend ergänzt, unbekannte Distributionen bleiben gesperrt; Arch-Sonderkernel benötigen passende Header; 1.895 gemeinsame Sprachtexte. |
| 05.10.26 | Release-Paketierung | 1.0 · Anwendung 3.4.29.149 | DEB-Abhängigkeit für aktuelle Ubuntu-Versionen repariert: `polkitd` plus `pkexec` sind die installierbare Alternative zum nicht mehr angebotenen `policykit-1`. Installationshelfer und Anleitung verwenden die aktuellen Paketnamen; RPM/Fedora unverändert. Die Paketaktualisierung wird gegen die installierte `.148` simuliert. |
| 05.10.26 | RGB Studio / PC-Gehäuseprofile / Levita-Orchestrierung / Anwendungsabschluss / Lokalisierung | 1.15 / 1.5 / Legacy / 1.1 / 1.0 | Direct-RAM wird als gemeinsame Bank mit getrennten physischen IDs/Frames und gemeinsamer validierter LED-Zahl dargestellt; der erste manuelle Effekt führt den vorhandenen ENE-Reclaim aus. Erkanntes Levita plus verfügbares TRCC startet im Hardwaremodus, fehlende Voraussetzungen bleiben im Testmodus. Ein PID-startzeitgeprüfter Relaunch wartet die alte Einzelinstanz ab. Drei Neustarttexte in vier Sprachen ergänzt; Fedora bleibt unverändert. |
| 05.10.26 | PC-Gehäuseprofile / RGB Studio | 1.5 / 1.15 | Eigene PC-Profile speichern und laden neben Blöcken/Gruppen nun validierte ARGB-Controller-/Anschlussrouten, aufgelöste persönliche Lüfter-/LED-Zahlen, manuelle Header, LED-Wege, RAM-/Gerätezuordnung und -Namen, Auswahl, GPU-Routen sowie bekannte PWM-Plätze; fehlende stabile IDs bleiben ohne Ausweichroute. Ein veralteter Einzel-Riegel-Weg darf einen RAM-Block mit zwei direkten Geräten nicht mehr verengen. Eingebettete Bearbeitung bleibt bis zu einer ausdrücklichen Abschlussaktion geöffnet. Nutzerlog bestätigt beide ENE-DRAM-Riegel wiederholt mit vollständigen 8-LED-Frames; keine Hardwarewerte im Prüflauf geändert. |
| 05.10.26 | OpenRGB Studio / OpenRGB-Integration | 1.15 / Legacy-Hotfix | Nur unter Ubuntu erhalten reine SDK-Clientbefehle `--nodetect`; Fedora behält seinen bisherigen Befehl unverändert. Auf dem betroffenen RX-9070-XT-System bleibt der konkrete Sapphire-Detektor in OHCs privater Konfiguration aus; sechs andere RGB-Geräte blieben im begrenzten Test verfügbar, ohne neue amdgpu-SMU-, GFX- oder Ring-Timeouts. |
| 01.10.26 | LCD-Laufzeit / Levita-Abschaltwächter / Levita-Daemongesundheit | 1.1 / 1.0 / 1.1 · Anwendung 3.4.29.131 | Exakte TRCC-9.10.4-Übergabe an den daemoninternen VideoLoop ohne falsche Wiederanläufe; Speicher-Notbremse bleibt aktiv. Separater Wächter ergänzt seinen installierten OHC-Modulpfad und stürzt nicht mehr vor dem Pipe-Warten ab. Live-Referenzlauf mit fortlaufenden 1600×720-Frames sowie stabilen RSS-/Thread-/FD-Werten. |
| 01.10.26 | GPU-Steuerung / RGB Studio / PC-Gehäuseprofile / UI-Leistung / Lokalisierung | 1.0 / 1.15 / 1.5 / 1.1 / 1.0 · Anwendung 3.4.29.130 | Scrollfreies kompaktes GPU-Cockpit, ziehbare Lüfterkurve, Bildimport und Fan-only ohne Grafiklast; synchronisierte kompakte Sechs-Spalten-RGB-Galerie; räumliche Richtung/Tempo/echte Reihenfolge und gemessene mm-/Inch-Abstände/Tiefe; Cachepflege nach Eingaberuhe mit niedriger Priorität; 1.838 vierfach lokalisierte IDs und Offscreen-Render. Keine Live-Hardwareoperation. |
| 01.10.26 | Levita-Daemon-Gesundheit / Anwendungsabschluss | 1.1 / 1.1 · Anwendung 3.4.29.129 | Exakt geprüfte Übertragung der TRCC-Kindprozesszuordnung nach kontrolliertem Neustart; UI-Laufzeit und Abschlusswächter bereinigen dieselbe aktuelle PID, ohne fremde Instanzen anzutasten. |
| 01.10.26 | Snapshot-Manager / GPU-Steuerung / UI-Themes / Lokalisierung | 1.0 / 1.0 / 1.0 / 1.0 · Anwendung 3.4.29.128 | Moderne Snapshot-Reglerkarten, atomarer JSON-Metadatenexport und einzeln bestätigtes Snapper-Löschen ab Nummer 1; GPU-Cockpit mit kompakten Live-Kacheln, breiten Taktbahnen und früher sichtbarer Kurve; 1.808 vierfach lokalisierte IDs und echte Offscreen-Render beider Seiten. Keine Live-Hardware-/Snapshotoperation. |
| 01.10.26 | Snapshot-Manager / UI-Themes / Hauptfenster / Lokalisierung / Release-Paketierung | 1.0 / 1.0 / Legacy 3.4.29.127 / 1.0 / 1.0 | Konfigurierbare Hauptseite mit read-only System-/Backend-/Snapper-/Btrfs-Erkennung; Spiel-/Vollbild-/Programmlisten- und optionale Last-Hysterese; Zeit-/Dauersperre, Desktop-/Spiel-Drosselung und fester Polkit-Helfer ohne beliebige Befehle/Units/Pfade; Snapper-Liste und sichere Wiederherstellungserklärung; 1.791 vierfach lokalisierte IDs und echter Offscreen-Render. 828 Tests sowie Sicherheit/Datenschutz/Module bestanden; ZIPs, Quelle, Bundle und RPM samt `.126`/`.127`-Sicherung geprüft, kein DEB mangels `dpkg-deb`; keine Live-Hardware-/Snapshotoperation, Installation oder Veröffentlichung. |
| 25.09.26 | GPU-Steuerung / PC-Gehäuseprofile / RGB Studio / Mainboard-Kühlung / Infrastruktur / Lokalisierung | 1.0 / 1.5 / 1.15 / Legacy / Legacy / 1.0 | 0-MHz-AMDGPU-Leerlauf akzeptiert; QProcess- und Fan-Kurvenprotokolle gebündelt; fähigkeitsabhängige Gehäusetabelle samt lesender Analyse; redundante RGB-Vorschau entfernt, sechs räumliche Vorlagen/13 Algorithmen/30 Designs; optionaler bestätigter reiner Lüfter-LACT-Dauer-Commit; 1.736 vierfach lokalisierte IDs. Vollständige 821 Tests und Offscreen-Sichtprüfung bestanden; keine Live-Hardwareoperation. |
| 22.09.26 | OpenRGB Studio / Laufzeitprotokoll / Hauptfenster / Lokalisierung | 1.15 / 1.0 / Legacy 3.4.29.124 / 1.0 | Lüfterzahl von Reihe/Ring entkoppelt; Reihe ist Standard und gespeicherte Wahl bleibt erhalten. Ring segmentiert weiterhin jeden Lüfter. Gesamt-, RGB-/Lüfter- und Hardware-Logansicht sowie exakte Topologieangaben bei Pfadspeicherung/Effektstart; 1.722 gemeinsame Sprach-IDs. |
| 22.09.26 | GPU-Steuerung / GPU-Profile / Hauptprofile / Lokalisierung | 1.0 / 1.0 / Legacy 3.4.29.120 / 1.0 | Exakt GPU-gebundene Unterprofile mit LACT-Konfiguration, Lüfter/Zero-RPM und Lasttest; nur lokal geprüfte Nutzdaten dürfen über vorhandene Sicherheitsbarrieren automatisch schreiben. KWin-Darstellung mit maximiertem Standard, Minimieren/Vollbild und Gamescope-Skalierung. Private transparente Bildkopien, zwei originale neutrale GPU-Familiengrafiken, Montageauswahl, animierte Lüfterkurve, reine RX-9000/7000-/RTX-50/40-Darstellung und 1.722 Sprach-IDs; keine Live-Hardwareoperation. |
| 20.09.26 | RGB Studio / OpenRGB-SDK / Hauptfenster | 1.15 / Legacy 3.4.29.117 · Anwendung 3.4.29.117 | Nach `.116`-Sichttest beide Zonenversuche vollständig entfernt: OHC- und SDK-Arbeiter ignorieren alte Einstellungen/Felder, laufende Effekte senden nur Geräteframes. Einmalige bewährte Direct-Vorbereitung, bestätigte LED-Zahlen, Komponentenlog und Gehäusevorschau bleiben. OHC-Neustart stellte auf dem Referenzsystem sechs Geräte wieder her; ältere optische Fluidität weiterhin zu untersuchen. |
| 20.09.26 | RGB Studio / OpenRGB-SDK / Hauptfenster / Lokalisierung | 1.15 / Legacy 3.4.29.116 / 1.0 · Anwendung 3.4.29.116 | Nach MSI-Zonenversuch in `.115` Zeitüberschreitungen und unerwartetes Engine-Ende im Nutzerlog: vollständige Geräteframes für GPU und Halterung wieder Standard; `.115`-Teststellung ignoriert. Zwei getrennte ausdrückliche MSI-/Airgoo-Versuche, Rückstellung bei SDK-Fehler oder Engine-Ende, komponentenbezogene Schreibwegdiagnose. 1.656 vierfach lokalisierte IDs; optischer Vergleich offen. |
| 20.09.26 | RGB Studio / OpenRGB-SDK / PC-Gehäuseprofile / Lokalisierung | 1.15 / 1.5 / 1.0 · Anwendung 3.4.29.115 | Umkehrbarer GPU-Schreibwegvergleich für explizit zugeordnetes MSI Mystic Light: validierte SDK-Zonenpakete nach dem vollständigen Startframe; gemessene Socket-Antwort und aktiver Weg im Log. Sichtbarkeitsgebundene Gehäusepunkt-Animation aus bestehenden GPU-/Halterungs-/RAM-Deklarationen, ohne Schreibzugriff oder erfundene physische Wege. 1.655 vierfach lokalisierte IDs; SDK-/UI-Regressionen geprüft. Optischer Vergleich offen. |
| 20.09.26 | RGB Studio / PC-Gehäuseprofile / Lokalisierung | 1.15 / 1.5 / 1.0 · Anwendung 3.4.29.114 | Live-Regler über denselben seriellen SDK-Arbeiter mit Rückkehr zu gespeicherten Werten bei Abbrechen; GPU-Weißspitze, weichere schwache Kanten und Standardwerte. Gehäuse-GPU-Button, getrennte Anschlusswahl, direkter LED-Editor und sichtbare Komponentennamen. Nur gespeicherte eindeutige LED-Wege erscheinen als Punkte in der Gehäusezeichnung; 1.654 vierfach lokalisierte IDs. Optischer Gerätetest offen. |
| 20.09.26 | RGB Studio | 1.15 / Anwendung 3.4.29.113 | GPU-Standardkante verbreitert; fester gemeinsamer Streifenzyklus trennt den Zeitpunkt des Lichtkopfs von den verschiedenen GPU-/Halterungs-Kanten. Vorschau und Worker nutzen dieselbe Berechnung; optische Prüfung ausstehend. |
| 20.09.26 | RGB Studio / Lokalisierung / Hauptfenster | 1.15 / 1.0 / Legacy 3.4.29.112 | GPU-Dialog mit zwei deklarierten LED-Reihen, getrenntem GPU-/Halterungs-Vorlauf und -Auslauf, gemeinsamem Tempo und bestätigter SDK-Hz-Anzeige. Reine Einstellungen bleiben bis zum Speichern im Entwurf; `gpu_motion.py` begrenzt Phasensprünge nach langsamem SDK-Batch, `render_plan.py` übergibt Takt und Parameter an den einzigen Worker. RGB-Profile speichern die Einstellungen; 1.653 vierfach lokalisierte IDs. Optische Geräteprüfung ausstehend. |
| 19.09.26 | GPU-Steuerung / Fensterplatzierung / Release-Paketierung | 1.0 / 1.4 / 1.0 | `.103`: LACT-Versionsprüfung aus Paketmetadaten statt nicht vorhandenem CLI-Flag, Wiederaufnahme einer bereits installierten Dienstaktivierung; Wayland-Nachprüfung verwendet Fenstersurface als Ist-Signal und prüft spät erneut. Dienst nach bestätigter Installation aktiv, keine GPU-Schreibänderung; echte OHC-Fensterplatzierung nach Update noch nicht optisch bestätigt. |
| 19.09.26 | GPU-Steuerung / Anwendungsabschluss / GPU-RGB / Lokalisierung / Release-Paketierung | 1.0 / 1.1 / RGB Studio 1.15 / 1.0 / 1.0 | LACT-API 0.10.1+ mit begrenztem rückfallendem GPU-Kurztest, getrenntem Commit, per GPU wiederherstellbaren Vorwerten und CoolerControl-Freigabeprüfung; OpenRGB-GPU-Controller von MSI/ASUS und anderen werden aus realem OpenRGB-Inventar im GPU-Reiter geöffnet, ohne Herstellerpauschale oder ARGB-Kabelannahme. Exakter Prozess-Lebenszeitwächter, Rückgabe temporär gestoppter CoolerControl-Dienste, optionaler LACT-Installer und vier vollständige Sprachen. Hardware-Schreibtest offen. |
| 19.09.26 | Hardware-Checker / PC-Gehäuseprofile / Temperaturverlauf / UI-Themes / RGB Studio / Lokalisierung | 1.0 / 1.5 / 1.2 / 1.0 / 1.15 / 1.0 | Direkter GPU-Klick startet die read-only Erstprüfung und danach den Lasttest; `vkcube`-Fallback mit Laufzeitprüfung und Hinweis bei fehlenden Programmen. Adaptive Tabellen mit vollem Mainboardnamen; neues `gauge.py` für zwölf Segmente in Übersicht/Kühlung/Aufzeichnung; schmalerer weißer GPU-Kopf und sichtbare blaue Basis nach Besitzer-Video. 1.532 Sprach-IDs, 70 gezielte Tests, Offscreen-Renderings und kurzer lokaler RX-9070-XT-Vulkan-Start. Kein vollständiger In-App-Linktest, RGB-Abgleich oder Paketbau. |
| 17.09.26 | Display-Effekte / Levita-Studio / LCD-Medienmanager / UI-Leistung / Hauptfenster | 1.11 / 1.7 / 1.0 / 1.1 / Legacy 3.4.29.99 | Effekt-Auswahl schreibt denselben kanonischen Levita-Startzustand wie das LCD-Studio. Minimieren-in-Tray wird aus `app/tray` nach `app/minimize_to_tray` übernommen; echtes Schließen beendet immer geordnet. Verborgene Qt-/FFmpeg-Quellen und Frames werden entladen, Navigation/Minimieren plant genau eine verzögerte GC-/optionale glibc-Heap-Freigabe. Eigentümerlog und Live-Messung belegen Tray-Weiterlauf sowie zwei retained Decoder; isolierter Test reduziert 107 auf 3 Threads. 716 Release-Tests, Sicherheits-/Datenschutz-/Modulprüfung, RPM/Archive/Entwicklerpaket/Git-Bundle und SHA-256-geprüfte `.98`/`.99`-Sicherungen abgeschlossen; DEB mangels Tool ausgelassen. Keine Installation, periodische Speicheraufgabe, private SSD-Auslagerung, neue Hardwareaktion oder Veröffentlichung. |
| 16.09.26 | Anwendungsabschluss / Hauptfenster | 1.1 / Legacy 3.4.29.98 | Ausdrücklich gewähltes Weiterlaufen im Infobereich wird als private Einstellung gespeichert; alle weiteren Schließvorgänge blenden ohne Dialog aus. Fehlt die neue Einstellung, wird ausschließlich eine echte `.97`-Journalwahl `window-close-choice=tray` einmalig übernommen; Eigentümerprotokoll und lokales Journal bestätigen sie. Beenden/Abbrechen/Sitzungsende bleiben getrennt, keine neue Hardware- oder Privilegaktion. Alle 715 Release-Tests sowie Sicherheits-/Datenschutz-/Modulprüfung bestanden; RPM/Archive/Entwicklerpaket/Git-Bundle und SHA-256-geprüfte `.97`/`.98`-Sicherungen abgeschlossen, DEB mangels Tool ausgelassen. Keine Installation oder Veröffentlichung. |
| 15.09.26 | Anwendungsabschluss / Hauptfenster / Prozessstatus | 1.1 / Legacy 3.4.29.97 / 1.1 | Eigentümerprotokoll belegt Infobereich statt Hänger: echte Beenden-Aufrufe liefen bis Qt-Schleifenrückkehr, Python-atexit und Elternprozess-Ende. Bei aktivem Tray-Modus jetzt ausdrückliche Auswahl Beenden/Weiterlaufen/Abbrechen; Beenden nutzt sofort die bestehende geordnete Rückgabe. Begrenzte read-only Journal-Auswertung mit sauber/Tray/abgebrochen/unvollständig/hängend und letzter belegter offener Phase im Systemstatus. 713 Release-Tests sowie Sicherheits-/Datenschutz-/Modulprüfung bestanden; RPM/Archive/Entwicklerpaket/Git-Bundle und SHA-256-geprüfte `.96`/`.97`-Sicherungen abgeschlossen, DEB mangels Tool ausgelassen. Keine Installation, Veröffentlichung, erzwungene Beendigung, Einstellungsrücksetzung oder neue Hardwareaktion. |
| 15.09.26 | Hardware-Checker / Hauptfenster / Lokalisierung | 1.0 / Legacy 3.4.29.96 / 1.0 | Neue konfigurierbare Hauptseite mit begrenzter read-only CPU-/SMT-/Virtualisierungs-/Board-/PCIe-GPU-/NVMe-/RAM-Abfrage außerhalb des GUI-Prozesses; grün/gelb/rot/nicht prüfbar mit Ist-/Kernel-Maximum. GPU-Leerlaufwerte erst nach ausdrücklichem glmark2-Test endgültig bewerten; NVMe ohne Schreibbenchmark. Feste optionale `pkexec dmidecode --type 17`-Abfrage, Passwort ausschließlich bei Polkit, manuelles RAM-Modell/Soll-MT/s bei unvollständigem DMI. 1.530 Sprachtexte; 708 Release-Tests, RPM/Archive/Entwicklerpaket/Git-Bundle sowie SHA-256-geprüfte `.95`/`.96`-Sicherungen abgeschlossen; DEB mangels `dpkg-deb` ausgelassen. Keine Installation, Veröffentlichung oder Takt-/Spannungs-/Lüfter-/Firmware-/BIOS-Änderung. |
| 14.09.26 | Display-Effekte / Levita-Vorschau / LCD-Medienmanager / UI-Leistung | 1.11 / 1.7 / 1.0 / 1.1 | .95: Lichtband-Rand-/Zentrumsstreifen entfernt, acht echte 4800×2160 Quellrenderings nativ/CRF 10. Ausgewählte LCD-Videos ohne Hover nur im Sichtfeld; getrennte pending/bestätigte Kompositionskopie und transiente Effektwahl mit Abwahl/Seitenrückkehr, unveränderte Start-/Profilpersistenz. Geteiltes Qt-Decoding/Viewport-Clipping, reservierte Galeriereihen und Wiederverwendung unveränderter Szenen; aktuelle Sprachdetails, lebenszyklusgebundene Tab-/Animationsaufrufe. Alle 701 Tests und Vier-Sprachen-UI/Sicherheit/Datenschutz/Module bestanden; RPM/Archive/Bundle und 233 Pythonquellen/16 Bandmedien/ZIP-CRC/RPM-Digests/SHA256 verifiziert. Genau zwei externe Sicherungen .94/.95, .93 gemäß Dauerfreigabe rotiert; kein DEB/Installieren/Hardwareaktion/Veröffentlichen. |
| 14.09.26 | PC-Gehäuseprofile / UI-Leistung / OpenRGB Studio / Lokalisierung | 1.5 / 1.1 / 1.15 / 1.0 | .94: adaptiver rechter Inspector ohne eigenen Scrollbereich; lebende Komponenten-/Lüfter- und LED-Verlaufsfelder in Spalten oder Reitern, feste Abschlussaktionen und sprachfeste späte Reitertitel. GPU-/Halterungsüberblendung mit breiteren quintischen Verläufen und gemeinsamer normalisierter Abtastung für unterschiedliche tatsächliche LED-Anzahlen. 1.483 gemeinsame Sprach-IDs; elf neue Regressionen und alle 697 Tests samt Vier-Sprachen-UI/Sicherheit/Datenschutz/Module bestanden; DE/FR breite/schmale Formulare und LED-Verlauf geprüft. RPM/Archive/Git-Bundle gebaut; beide ZIP-CRCs, 230 aktuelle Pythonquellen, RPM-Digests/Metadaten/Bundle und Dist/.93/.94-SHA256 verifiziert. Genau zwei vollständige Sicherungen, .92 gemäß Dauerfreigabe rotiert; kein DEB mangels Toolchain. Keine Installation/Hardwareaktion/Veröffentlichung, optische Prüfung am Gerät ausstehend. Abschluss nach Paketbau dokumentiert. |
| 14.09.26 | LCD-Prozessüberwachung / Levita-Orchestrierung / Display-Effekte / Lokalisierung / Release-Paketierung | 1.1 / Legacy 3.4.29.93 / 1.10 / 1.0 / 1.0 | .93: ein ausdrücklich gespeicherter Standard mit Vorrang vor automatischen Profilen; Vorschauen ohne Start-/Profilpersistenz; immutable gewünschte Befehlsfolge für Daemon-Erholung, entwertete veraltete Start-Retries, vollständige Profil-FPS/Bewegung. Gestufter Speicherwächter statt wiederkehrendem Neustart bei stabilem 1138-MiB-Video; Cache-Identität um wirksame Konfiguration/Quellassets ergänzt. 1.482 atomare Sprach-IDs; 13 neue Regressionen und alle 686 Tests samt Vier-Sprachen-UI/Sicherheit/Datenschutz/Module bestanden; RPM/Archive/Git-Bundle gebaut. Beide ZIP-CRCs, 229 aktuelle Pythonquellen, RPM-Digests/Metadaten/Bundle und Dist/.92/.93-SHA256 verifiziert. Genau zwei vollständige Sicherungen, .91 gemäß Dauerfreigabe rotiert; kein DEB mangels Toolchain. Keine Installation/Hardwareaktion/Veröffentlichung; Abschluss nach Paketbau dokumentiert. |
| 14.09.26 | Prozesslaufzeit / LCD-Prozessüberwachung / Levita-Orchestrierung / Lokalisierung / Release-Paketierung | 1.1 / 1.0 / Legacy 3.4.29.92 / 1.0 / 1.0 | .92: bestätigte Transfers für statischen und animierten Dauerbetrieb; isolierte Hänger-/Startfehlererkennung, begrenzte Wiederanläufe und privates Moduljournal mit PID/Exit/Ursache/Traceback; Spielerkennung im read-only Helfer, keine GUI-Prozesssweeps. Fünf atomare Sprachtexte, Sensor-Neustart/Systemstatus; ZIP-Installationsbefehle verwenden den tatsächlichen INTERN-Ordner. Test-Cacheumgebung isoliert, kein Benutzer-Cachezugriff. Native Quarantäne/PWM/USB-Besitz unverändert; 17 neue Fehlertests, alle 673 Tests, Vier-Sprachen-UI/Sicherheit/Module bestanden; DE/FR-Systemstatus gerendert und geprüft. RPM/Archive/Git-Bundle
gebaut und 227 Pythonquellen/ZIP-CRC/RPM-Digests/Metadaten/Bundle/SHA256 geprüft.
Genau zwei vollständige Sicherungen .91/.92; .90 gemäß Dauerfreigabe rotiert.
Kein DEB mangels dpkg-deb, keine Installation/Hardwareaktion/Veröffentlichung. |
| 14.09.26 | Prozesslaufzeit / Anwendungsabschluss / OpenRGB Studio / PC-Gehäuseprofile / Temperaturverlauf / Lokalisierung | 1.0 / 1.1 / 1.14 / 1.4 / 1.2 / 1.0 | .91: Qt-freier Sensorprozess mit einer offenen Anfrage, Frische-/Timeoutgrenzen und drei begrenzten Neustarts; gemeinsame Messwerte statt GUI-Sweeps, lazy Sensorexporte ohne Qt. Echte eigene Prozess-CPU/RSS und Sensorzustände in eingebettetem Systemstatus; keine irreführende Speichersumme. Reine RGB-Pläne im bestehenden SDK-Worker berechnet, Host bleibt Autorisierer; mathematische Gleichheit einschließlich Streifen getestet. Seitliche Beschriftungen öffnen mit einem Klick ohne Positionscommit. Dauerhaftes privates Phasenjournal, einmaliger verzögerter Stack-Dump, startzeitgesicherter read-only Elternbeobachter maximal 90 Sekunden; eigene Restprozesse erst nach Rückgabe begrenzt beendet, danach direktes Qt-Ende. Ausdrücklicher Diagnoseexport integriert anonymisierte Beenden-Dateien. 1.476 atomare Sprachtexte; 34 neue gezielte Tests und wiederholtes vollständiges 656-Test-Gate samt Vier-Sprachen-UI/Sicherheits-/Datenschutz-/Modulprüfung bestanden; DE/FR-Systemstatus gerendert und geprüft. RPM/Archive/Git-Bundle gebaut, alle 218 aktuellen Pythonquellen, ZIP-CRC, RPM-Digests/Metadaten, Bundle und Dist/.90/.91-SHA256 verifiziert. Genau zwei vollständige Sicherungen, .89 gemäß Dauerfreigabe entfernt; kein DEB mangels dpkg-deb. Autonomer Core/Kühlungsdienst und weitere LCD-Migration bleiben nachfolgende hardwarevalidierte Stufen. Keine Installation/Live-Hardwarewrites/Firmwareänderung/Veröffentlichung; Abschluss nach Paketbau dokumentiert. |
| 14.09.26 | UI-Leistung / PC-Gehäuseprofile / OpenRGB Studio / Kühlungszustand / Lokalisierung | 1.1 / 1.3 / 1.13 / 1.0 / 1.0 | .90: begrenzte Leerlauf-Kartenarbeit, kleine immutable-source Vorschaubilder, rechte eingebettete Eigenschaftsformulare und werttreue Live-Übersetzung; RAM-Wiederholung isoliert nur betroffene IDs und wartet auf deren letzten Frame, ohne übrige Effektzeit zurückzusetzen. Gespeicherte Kühlungsstartabsicht bleibt von tatsächlicher Regelung getrennt; frische Besitzprüfung vor beiden Hauptschaltern. Explizites Beenden verlässt nach isoliertem Cleanup die Qt-Schleife; Übergang nur links, eigene Cache-Arbeiter werden beendet. 1.467 gemeinsame Sprachtexte; wiederholtes vollständiges 622-Test-Gate einschließlich Vier-Sprachen-UI/Sicherheits-/Datenschutz-/Modulprüfung bestanden, DE/FR gerendert und geprüft. Lokale RPM/Archive/Git-Bundle gebaut: 208 aktuelle Pythonquellen exakt geprüft (vier übliche RPM-Shebang-Anpassungen), ZIP-CRC, RPM-Digests/Metadaten, Bundle und Dist/.89/.90-SHA256 bestanden. Genau zwei komplette Sicherungen; .88 gemäß dauerhafter Freigabe entfernt. DEB mangels dpkg-deb nicht gebaut; keine Live-Hardware-/Firmwareänderung, Installation oder Veröffentlichung. Paketsnapshots enthalten den Vorbau-Prüfstand, dieser Abschluss wurde nach dem Bau dokumentiert. |
| 13.09.26 | OpenRGB Studio / Hauptfenster / Lokalisierung | 1.12 / Legacy 3.4.29.89 / 1.0 | Weiche offene GPU-Streifen in `gpu_strip_sampling.py`, getrennte begrenzte Paarauflösung in `gpu_support_sync.py`; ausgewählte ausdrückliche GPU-/Halterungsanschlüsse teilen Zeit, Effekt und normalisierten Verlauf bei getrennten echten LED-Zahlen. GPU-Dialog speichert optionalen Schalter nur beim Bestätigen; Paketexport übernimmt ihn. Ring-/mehrdeutige/fehlende/gesperrte Partner werden nicht gekoppelt, andere Header unverändert; Startdiagnose protokolliert Renderer, echte Länge und gemeinsame Zeitbasis ohne Frame-Spam. 1.448 Sprachtexte. 105 gezielte und alle 597 vollständigen Tests, Vier-Sprachen-UI/Sicherheits-/Datenschutz-/Modulprüfung sowie wiederholtes Baugate bestanden. RPM/Archive/Git-Bundle lokal erstellt, 44 aktuelle Quellen, ZIP-CRC, RPM-Digests/Metadaten und Dist/.88/.89-SHA256 geprüft; genau zwei komplette private Sicherungen, .87 nach Freigabe rotiert; DEB mangels dpkg-deb nicht gebaut; keine neue Hardwarehoheit/Installation/Veröffentlichung. |
| 13.09.26 | OpenRGB Studio / Profile Bundle / Anwendungsabschluss / Lokalisierung | 1.11 / 1.0 / 1.0 / 1.0 | .88: umkehrbare Lüfterringketten mit eigenem LED-1-Ursprung, unabhängig von Ringrotation; Vorschau/Abtastung/Persistenz/Log verwenden dieselbe Deklaration. Paketimport prüft gleiche erlaubte Assettypen wie Export und Dateiverzeichnis-Konflikte vor Staging. Timer/Neustartabsichten stoppen vor eigenem Paketarbeiter-Abbruch. 1.446 Sprachtexte; 104 gezielte Tests und wiederholtes vollständiges 555-Test-Gate mit Vier-Sprachen-UI, Sicherheits-/Datenschutz-/Modulprüfung bestanden; DE/FR-Vorschau visuell geprüft. Lokale .88 RPM-/ZIP-/Quell-/Git-Bundle-Paketierung abgeschlossen; RPM-Digests/Metadaten und 42 Quellen (nur normale Einstiegsshebang angepasst), ZIP-CRC/42 Quellen und Quellarchiv geprüft. Dist und .87/.88-SHA256 bestanden, genau zwei vollständige Sicherungen; .86 nach dauerhafter Freigabe rotiert. DEB mangels dpkg-deb nicht gebaut. Keine Hardwareoperation/Installation/Veröffentlichung. |
| 13.09.26 | Profile Bundle / OpenRGB Studio / Hauptfenster / Lokalisierung | 1.0 / 1.10 / Legacy 3.4.29.87 / 1.0 | Vollständiges privates ZIP mit typisierten Einstellungen, Profilen, Gehäuse/RGB/PWM/Modellen/Medien; begrenzter eigener Datei-Arbeiter, strenge Pfad-/Typ-/SHA-Prüfung, neue private Staging-Dateien, bestätigte Start-Wiederherstellung mit Rückfallkopie und erneuter Hardware-/PWM-Freigabe. Physischer LED-Verlauf als unabhängige Streifen-/Ringdeklaration, Qt-Vorschau und acht räumliche Laufrichtungen mit unveränderter Testnummerierung/Transporthoheit. JSON-Austausch aus Hauptdatei ausgelagert. 1.442 atomare Sprachtexte; wiederholtes Build-Gate mit allen 546 Tests, vollständigem Vier-Sprachen-Aufbau, Sicherheits-/Datenschutz- und Modulprüfungen bestanden; Profil-/LED-Vorschauflächen gerendert und DE/FR geprüft. Lokale .87 RPM-/ZIP-/Quell-/Git-Bundle-Paketierung abgeschlossen; RPM-Digests/Metadaten und 34 exakte Quellen, ZIP-CRC/33 Quellen sowie Quellarchiv geprüft. Dist und .86/.87-SHA256 bestanden; .85 nach dauerhafter Freigabe rotiert, genau zwei vollständige Sicherungen. Keine Installation, Backend-/Firmwareänderung, Live-Hardwareoperation oder Veröffentlichung; DEB mangels dpkg-deb nicht gebaut. |
| 13.09.26 | OpenRGB Studio / Hauptfenster / Lokalisierung | 1.9 / Legacy 3.4.29.86 / 1.0 | Entwicklung nach paketierter .86: `personal_wiring.py` übernimmt fünf bestätigte persönliche AG-DRGB16-Zuordnungen einmalig, erhält Geometrie/PWM/fremde Zonen und schützt vollständige gespeicherte LED-Zahlen durch Pins; B6 jetzt zwölf statt 24, keine wiederkehrende Zwangsrücksetzung. `fan_library.py` speichert begrenzte eigene Hersteller/Modelle/Farben/LEDs zur Wiederverwendung in Block-/Zoneneditoren; Thermalright-Radiatorreferenz zehn LEDs je Lüfter. 1.395 atomare Sprachtexte; 83 gezielte und alle 516 vollständigen Tests einschließlich Vier-Sprachen-Oberflächenaufbau, Sicherheits-/Datenschutz- und Modulprüfungen bestanden; neue Editoransichten DE/FR geprüft. Keine neue Paketierung, Installation oder Hardwareoperation. |
| 13.09.26 | OpenRGB Studio / Hauptfenster / Lokalisierung | 1.8 / Legacy 3.4.29.86 / 1.0 | Eigene Engine ausdrücklich neu starten, alte Erkennungszustände invalidieren; Offline-Anschlusswahl bei fortbestehendem Besitzschutz und offene Liste aktualisieren. LED-Vorschau pausiert Erkennung/Auto-Apply, verhindert überlappende Tests und stellt unverändertes Design einmal wieder her. Kleine persönliche Lüftermodell-/Farb-/LED-Module; acht LEDs nur bestätigte persönliche Referenz, keine Massenmigration. 1.394 gemeinsame Texte; 500 Tests/Gates bestanden, lokale RPM-/ZIP-/Quell-/Bundle-Paketierung und .85/.86-Sicherungsprüfungen abgeschlossen. Keine native Absturz-/Hardwarebestätigung oder Installation. |
| 13.09.26 | Anwendungsabschluss / Mainboard-Kühlung / Prozessbackend / Hauptfenster | 1.0 / Legacy | Entwicklung nach .85: EOF zuerst statt sofortigem SIGTERM für den root-eigenen Polkit-Helfer; Signalablehnung bleibt Diagnose. Getrennte best-effort Abschaltphasen, eigene Timer stoppen, kein Backend-Callback während Shutdown; sauberer LCD-Marker erst nach Rückgabe. 72 gezielte Tests und vollständiges Release-Gate mit 474 Tests bestanden; neue Version/Paketierung noch offen. |
| 13.09.26 | OpenRGB Studio / Gehäuse-Integration / Hauptfenster | 1.7 / 1.2 / Legacy 3.4.29.85 | `slot_route_editor.py` ermöglicht direkte Controller-/Anschlusswahl auch ohne RGB-Kachel; LED-Anzahl und Pixeltest delegieren bestehenden begrenzten Editor. `slot_routes.py` persistiert explizite stabile physische Bindungen getrennt von Design/PWM; validiert aktuelle Anschlüsse und verhindert stillen Fallback. GPU behält bestehende Routenautorität; Abbruch, alle gemeldeten Anschlüsse, Wiederbindung, Neustart und vier Sprachen getestet. Keine neue Transportverbindung; 1.390 unveränderte gemeinsame Texte. |
| 13.09.26 | PC-Gehäuseprofile / OpenRGB Studio / Hauptfenster / Lokalisierung | 1.2 / 1.6 / Legacy 3.4.29.84 / 1.0 | `case_geometry.py` besitzt proportionale Render-/Treffergeometrie und ausdrückliche Montageanordnung; `resize_interaction.py` den einmaligen Eckgriff-Commit mit Abbruch; `depth_renderer.py` originale räumliche Kanten/Schatten; `channel_labels.py` gemeldete SYS_FAN-Namen bei unveränderter Treiber-ID. Visuelle Skalierung in `RGBLayoutSlot`/Normalisierung/Profilen/Moves/Splits, optional unabhängig in `view_state.py`, niemals LED/PWM/mm-Änderung. `selection.py` wählt standardmäßig alle schreibbaren RGB-Geräte, speichert explizite Einzelwahl und versieht die vollständige Liste mit Einzelhäkchen. Keine Hardwarewrites; 1.390 Sprachtexte; neue Resize-/Selektionsregressionen und modellbezogenes Rendertool. |
| 13.09.26 | Release-Paketierung / Projektgedächtnis | 1.0 | Dauerhafte Eigentümerfreigabe für automatische Rotation älterer erkannter externer Release-Sicherungen ohne neue Rückfrage dokumentiert; zwei neueste vollständige Versionen und SHA256-Prüfung bleiben Pflicht. .81 darf beim lokalen .83-Bau entfernt werden, .82 bleibt erhalten; keine allgemeine Lösch-, Installations- oder Veröffentlichungsfreigabe. |
| 13.09.26 | PC-Gehäuseprofile / OpenRGB Studio / Hauptfenster / Lokalisierung | 1.1 / 1.5 / Legacy 3.4.29.83 / 1.0 | Zentrale Gehäuse-Seite nach Übersicht mit gemeinsamem RGB/LED/PWM-Mapping und optional getrennten Positionen; Anschluss-/Pixeltest für alle gemeldeten Direct-Zonen; manuelle Anschlusswerte vor Designprofilen geschützt; 30 detaillierte originale Zeichnungen, zählabhängige weiche Effektberechnung und volle Übertragungsfläche; Qt-freie lazy Effektimporte; 1.387 gemeinsame Texte. Besitzer bestätigt 30 Sapphire-LEDs an JARGB 1 durch Sichttest; neue Animation optisch noch zu prüfen. |
| 13.09.26 | OpenRGB Studio / PC-Gehäuseprofile / Hauptfenster / Lokalisierung / Release-Paketierung | 1.4 / 1.0 / Legacy 3.4.29.82 / 1.0 / 1.0 | GPU-Routen um konkrete Zone erweitert; eigener Anschlusseditor und begrenzter Pixeltest; unabhängige Strip-Koordinaten; aktuelle GPU-Verkabelung und LED-Anzahl vor Designprofilen geschützt; GPU-Anschlussnotiz auch bei PC-Profilübernahme synchronisiert; persönliche bestätigte MSI-JARGB-1-Zuordnung einmalig migriert; keine physischen LED-Zahlen geraten; 1.381 gemeinsame Einträge, Datenkataloge mechanisch komprimiert. |
| 13.09.26 | OpenRGB Studio / PC-Gehäuseprofile / Hauptfenster / Lokalisierung / Release-Paketierung | 1.3 / 1.0 / Legacy 3.4.29.81 / 1.0 / 1.0 | Automatischen External-Control-Zwang entfernt; Sapphire-Designs auf gemeldete native Animationen abgebildet; expliziten ARGB-Steuerweg und vorhandenen manuellen LED-Editor aus der GPU-PC-Ansicht ergänzt; stabile Zuordnung mit Profilen gespeichert; bestehende persönliche Ansicht ohne LED-Anzahländerung erhalten; 1.372 gemeinsame Spracheinträge. |
| 12.09.26 | Hauptfenster / Mainboard-Kühlung / Mainboard-Treiber-/MOK-Assistent / PC-Gehäuseprofile / UI-Themes / Lokalisierung / Release-Paketierung | Legacy 3.4.29.80 / 1.0 legacy / 1.0 / 1.0 / 1.0 / 1.0 / 1.0 | MOK-Statusparser und geführten Treiber-Wizard repariert; System-Fan-Namen/PWM-Anzeige getrennt; sicheren Gesamtzuordnungsreset und Fortsetzen mit nächstem Lüfter ergänzt; fehlende Levita-Kühlmittelquellen entfernt und Warnfläche lesbar gemacht; Komponenten-Doppelklick öffnet zugeordnetes Gerät beziehungsweise Direct-Zoneneditor; KDE-StatusNotifier ohne Geometrie wieder als erreichbaren Tray anerkannt; 1.365 gemeinsame Spracheinträge. |
| 12.09.26 | UI-Leistung / Wallpaper Engine / Mainboard-Treiber-/MOK-Assistent / Fensterleiste / Hauptfenster / Levita LCD-Orchestrierung / OpenRGB Studio / Lokalisierung / Release-Paketierung | 1.0 / 1.3 / 1.0 / 1.2 / Legacy 3.4.29.79 / Legacy 3.4.29.79 / 1.2 / 1.0 / 1.0 | Leichte wählbare Übergänge ohne doppelte Seitenrenderung; zentraler begrenzter SSD-Katalog-/Vorschaucache; Wallpaper- und NCT6687/MOK-Assistenten erweitert; LCD-Erstscan und Wallpaper-Galerie beschleunigt; ENE-Wiederherstellung während Navigation verschoben; automatische Gehäuselüfterregelung zuverlässig blau; X trifft die Fensterecke und minimiert bei Tray-Wunsch auch bei vorübergehend ungültiger Symbolgeometrie ohne Display-/RGB-Abschaltung; 1.353 gemeinsame Sprach-IDs. |
| 12.09.26 | Hauptfenster / RGB-Studio / Display-Effekte / Wallpaper Engine / Levita LCD-Orchestrierung / Fensterplatzierung / Desktop-Shell / Release-Paketierung | Legacy 3.4.29.78 / 1.2 / 1.10 / 1.2 / Legacy 3.4.29.78 / 1.4 / Legacy 3.4.29.78 / 1.0 | RGB-Schriftvererbung behoben und sichtbaren Ausschnitt begrenzt; Studiohierarchie neu geordnet; Display-Effekt-Karten/Bilder wiederverwendet, Video nach erstem Bild aktiviert und Vorschau auf 20 FPS begrenzt; Levita-/Wallpaper-Thumbnails nur im sichtbaren Viewport geladen und beim Verlassen gestoppt; LCD-Filme, App-Hintergrund und Shell-Uhr außerhalb ihrer Oberfläche pausiert; physische Ausgabe/Regelung bleibt aktiv; Schließen bei nicht erreichbarem Infobereich beendet geordnet. |
| 12.09.26 | Levita-Daemongesundheit / Leistung / Levita LCD-Orchestrierung / Fensterplatzierung / Hauptfenster / Mainboard-Kühlung / gemeinsame Infrastruktur / Lokalisierung / Release-Paketierung | 1.1 / 1.1 / Legacy 3.4.29.77 / 1.4 / Legacy 3.4.29.77 / 1.0 legacy / Legacy 3.4.29.77 / 1.0 / 1.0 | Verdeckte LCD-Galerien und Vorschau-Timer pausieren; Spielprozessprüfung auf zehn Sekunden begrenzt; manuelle, eigentümer- und PID-validierte Display-Freigabe ergänzt; automatische Erholung erkennt belegte TRCC-Schnittstelle; Mainboard-Automatik/Schnellprofil wird nach Start sichtbar aktiv markiert; erster sichtbarer Fensterframe besitzt sofort den gespeicherten Zustand; Fensterdiagnose blendet versteckte Qt-Hilfsfenster aus; 1.292 gemeinsame Sprach-IDs. |
| 12.09.26 | Laufzeitprotokoll / Levita-Daemongesundheit / Levita LCD-Orchestrierung / Hauptfenster / Lokalisierung / Release-Paketierung | 1.0 / 1.0 / Legacy 3.4.29.76 / Legacy 3.4.29.76 / 1.0 / 1.0 | Gelieferten Sitzungslog und Kernel-OOM als TRCC-Daemon-Speicheranstieg bis 15,5 GB korreliert; exakten Eigenprozess-Wächter, IPC-Neustart und Designwiederherstellung ergänzt; sichtbare Logs auf 60-Minuten-Ringpuffer umgestellt und begrenztes privates Fehlerlog samt Diagnoseauszug hinzugefügt; 1.291 gemeinsame Sprach-IDs. |
| 12.09.26 | Fensterplatzierung / Display-Effekte / Responsive Galerien / LCD-Medienmanager / Temperaturverlauf / Lokalisierung / Release-Paketierung | 1.3 / 1.10 / 1.0 / 1.0 / 1.2 / 1.0 / 1.0 | Startprofil-/KWin-Größenpendeln entfernt; LCD- und Effektkarten nutzen den tatsächlichen Viewport bis zwölf Spalten; mehrere Ordner und Einzelmedien mit Aliasen und nicht-destruktivem Ausblenden; TRCC-ID-Namen lesbar; lokales Datum/Uhrzeit, skalierbare Diagramm-/Tabellenbereiche und ausdrücklicher CSV-/JSON-Zeitraumexport aller erfassten Sensoren; 1.291 gemeinsame Sprach-IDs. |
| 12.09.26 | Fensterplatzierung / Hauptfenster / Release-Paketierung | 1.2 / Legacy 3.4.29.74 / 1.0 | Gelieferten Log und KWin-Ausgangskonfiguration abgeglichen; Normalfenster wird vor der Maximierung auf dem Ziel abgebildet; tatsächlich gemappter Wayland-Bildschirm wird nach 350 ms bestätigt und nur bei Abweichung korrigiert; Tray-Öffnung folgt derselben Reihenfolge; Ziel/Ist/Geometrie werden protokolliert. |
| 12.09.26 | Display-Effekte / Levita LCD-Orchestrierung / Hauptfenster / Lokalisierung / Release-Paketierung | 1.9 / Legacy 3.4.29.73 / Legacy 3.4.29.73 / 1.0 / 1.0 | Modellabhängige Originalanzeige im Tray und direkte Thermalright-Firmware-Rückgabe auf beiden LCD-Seiten über den einzigen TRCC-Besitzer; Testmodus schreibfrei und bereits getrennte Verbindung idempotent; ausdrückliches Tray-Beenden mit einem Klick; acht OHC-Lichtbänder aus 2×-Supersampling hochwertig auf 1600×720 ausgegeben; 1.277 gemeinsame Sprach-IDs. |
| 12.09.26 | Levita LCD-Datenoberfläche / Leistung / Display-Effekte / Anzeigeeinstellungen / Fensterleiste / Fensterplatzierung / Hauptfenster / Lokalisierung | 1.7 / 1.0 / 1.8 / 1.0 / 1.1 / 1.1 / Legacy 3.4.29.72 / 1.0 | Vier originale Layer-2-Glow-/Partikelloops mit Schalter, lokaler Ein-Strom-Komposition und Profilpersistenz; 15-FPS-Standard, getrennte Vorschau-/LCD-Rate, GameMode/Gamescope/Programmlisten-Erkennung, experimentelle 60-FPS-Freigabe und Rückstufung; ausgelagerte Anzeigeoptionen, flackerfreie Zustandswiederherstellung und ausfallsichere Randcursor-Freigabe; 1.268 gemeinsame Sprach-IDs. |
| 12.09.26 | Display-Effekte / Levita LCD-Orchestrierung / Hauptfenster / Fensterplatzierung / Lokalisierung / Release-Paketierung | 1.7 / Legacy 3.4.29.71 / Legacy 3.4.29.71 / 1.0 / 1.0 / 1.0 | Ebene-1-Katalog als grafische Kacheln mit erhaltenen Quellenlinks; eigener nahtlos animierter Spektrumring samt automatischer editierbarer Ebene-2-Kopplung; OHC-Layouts mit DejaVu-Schriften und Glas-Uhrrahmen; feste Anschlusswahl einschließlich Hauptmonitor und Normalplatzierung vor erneutem Maximieren unter KWin; 1.250 gemeinsame Sprach-IDs. |
| 12.09.26 | Levita LCD-Datenoberfläche / Levita LCD-Orchestrierung / Lokalisierung / Release-Paketierung | 1.6 / Legacy 3.4.29.70 / 1.0 / 1.0 | Vier originale Regenbogen-Datenlayouts; bis zu zwölf frei positionierbare eigene Texte mit lokalen Schriften; feste 880×396-Vorschau; privates validiertes natives Theme-Staging über die vorhandene einzelne TRCC-Warteschlange; 1.226 gemeinsame Sprach-IDs; nicht-destruktiver Design-Manager für eine der nächsten zwei bis drei Versionen vorgemerkt. |
| 11.09.26 | Display-Effekte / Bereichs-Unterreiter / Hauptfenster / Lokalisierung / Release-Paketierung | 1.7 / 1.0 / Legacy 3.4.29.69 / 1.0 / 1.0 | Aktives Levita-Bibliotheksmedium synchronisiert Effektart, Kategorie, Design und Variante ohne Hardwareaktion; originaler OHC-Light-Ribbons-Loop in acht Richtungen; synchronisierte LCD-Unterreiter als wiederverwendbares Muster; 1.220 gemeinsame Sprach-IDs. |
| 11.09.26 | Temperaturverlauf / Hauptnavigation / Release-Paketierung | 1.1 / Legacy 3.4.29.68 / 1.0 | Kühlung wie LCD um feste aufklappbare Unterpunkte für Steuerung/Profile und Temperaturaufzeichnung ergänzt; Auswahl und interne Ansicht bidirektional synchronisiert; Anpassung und Navigation-Reset bewahren beide Einträge; Hardwarepfade unverändert. |
| 11.09.26 | Temperaturverlauf / Kühlungssicherheit / Hauptfenster / Profile / Lokalisierung / Release-Paketierung | 1.1 / 1.0 / Legacy 3.4.29.67 / Legacy 3.4.29.67 / 1.0 / 1.0 | Eigene Kühlungs-Unterseite mit gruppierten read-only hwmon-Sensoren, Maus-Hover und Zeitraumstatistik; konservative Levita-Untergrenzen an allen Eingabe-, Profil-, Kurven- und Schreibgrenzen; Profilbreite stabilisiert, Auswahl erhalten, Inhaltsbaum und kombinierbare Bereiche ergänzt; 1.214 gemeinsame Sprach-IDs; Sensorleser nimmt keinen GPU-/CPU-Steuerungsbesitz. |
| 11.09.26 | Hardware-Unterbauten / Temperaturverlauf / Hauptfenster / Mainboard-Kühlung / Lokalisierung / Release-Paketierung | 1.0 / 1.0 / Legacy 3.4.29.66 / 1.0 legacy / 1.0 / 1.0 | Profil-Festwert, eigener Festwert und CPU-Kurve eindeutig getrennt; gemischtes Schnellprofilverhalten erklärt; sitzungsinterner interaktiver CPU-/GPU-/Kühlmittelverlauf; persistente fail-closed Auswahl der vorhandenen TRCC-/hwmon-Unterbauten; Zukunftsadapter sichtbar, aber deaktiviert; 1.182 gemeinsame Sprach-IDs; keine neue Hardwaretransportimplementierung. |
| 11.09.26 | Levita LCD-Orchestrierung / Release-Paketierung | Legacy 3.4.29.65 / 1.0 | Fotos von Programmvorschau und echtem Levita verglichen; 22 % breitere und 12 % höhere TRCC-Schriftmetriken als automatische Reserve in die wertabhängige Rahmenberechnung übernommen; resultierende Rahmen je nach Wert etwa 16–18 % breiter und 10–12 % höher; drei Nebula-Varianten neu erzeugt; TRCC- und Hardwarepfad unverändert. |
| 11.09.26 | Levita LCD-Orchestrierung / Release-Paketierung | Legacy 3.4.29.64 / 1.0 | Ursprüngliche teiltransparente Nebula-Ebene wiederhergestellt; große deckende Karten durch kompakte wertnahe Leseflächen ersetzt; drei Varianten Minimal, System und Leistung mit unterschiedlichen Metriksätzen; Galerie-Vorschau zeigt echte Hintergrundkombination; TRCC- und Hardwarepfad unverändert. |
| 11.09.26 | Mainboard-Kühlung / Levita LCD-Orchestrierung / Hauptfenster / Lokalisierung / Release-Paketierung | 1.0 legacy / Legacy 3.4.29.63 / Legacy 3.4.29.63 / 1.0 / 1.0 | Zustandsbeschriftungen auf Gehäuselüfterkarten durch eindeutige nächste Aktionen „Automatik einschalten“/„Automatik ausschalten“ in DE/EN/ES/FR ersetzt; simuliertes kalibriertes Umschalten in beiden Richtungen; Nebula mit dunklen Datenkarten, vier OHC-Themes mit getrennten Ring-/Wellen-/Glas-/Winkelstilen und skalierbaren Vorschaufenstern; Kurven, Kalibrierung, Besitzgrenzen und Hardwarepfad unverändert; Release Notes aus dem kanonischen Verzeichnis gesichert. |
| 11.09.26 | Display-Effekte / Levita LCD-Orchestrierung / Lokalisierung / Release-Paketierung | 1.6 / Legacy 3.4.29.62 / 1.0 / 1.0 | Fünfzehn geprüfte menschenfreie Weltall-, Landschafts- und Wasserclips als attribuierte lokale 1600×720-Medien; vier Filterkategorien; fünf CC0-Kenney-basierte und vier originale OHC-Layer-2-Themes; 1.151 gemeinsame Sprach-IDs; keine abgelehnten Saturn-/3D-Fly-through-/Grand-Canyon-Medien. |
| 11.09.26 | Display-Effekte / Levita LCD-Orchestrierung / Hauptfenster / Lokalisierung | 1.5 / Legacy 3.4.29.61 / Legacy 3.4.29.61 / 1.0 | Gewählten Bibliothekseffekt samt Ebene 2 bereits bei der Auswahl automatisch oder per Schaltfläche für die nächste Profilaktualisierung vorgemerkt; erzeugte Effekte folgen nach vorhandenem Video; LCD-/Gesamtprofile restaurieren die Levita-Startauswahl vor dem verzögerten Start; sichtbarer Profilhinweis in 1.130 Sprach-IDs |
| 10.09.26 | UI-Themes / Display-Effekte / Hauptfenster / Release-Paketierung | 1.0 / 1.4 / Legacy 3.4.29.61 / 1.0 | Helles und dunkles Design getrennt registriert; verbliebene dunkle Einzelstile im hellen Modus ersetzt; alle Bibliotheksvideos animiert, Dark Smoke beginnt bei sichtbarer Bewegung und pausiert außerhalb der Seite oder bei minimiertem Fenster; Qt Multimedia als GUI-Abhängigkeit |
| 10.09.26 | Fensterplatzierung / Fensterleiste / PC-Gehäuseprofile / Hauptfenster / Lokalisierung | 1.0 / 1.0 / 1.0 / Legacy 3.4.29.60 / 1.0 | Maximierte Arbeitsflächenmaße als Normalgröße verworfen; separate Fenstermodus-Geometrie, 60–95-%-Vorgabe, HiDPI-Begrenzung und Strg+Alt+0-Rettung; zweispaltige modellabhängige OHC-Gehäuseansicht mit AIO/Luft, Reverse und Einzellüfterteilung; privater Amazon-Knopf entfernt; 1.126 gemeinsame Sprach-IDs |
| 10.09.26 | Fensterleiste / PC-Gehäuseprofile / OpenRGB Studio / Hauptfenster / Lokalisierung | 1.0 / 1.0 / 1.2 / Legacy 3.4.29.59 / 1.0 | Eigene compositor-delegierte Fensterleiste; LCD-Unterkategorien; vier RGB-Vorschläge plus Favoriten, Gesamtbibliothek und vier neue Vorlagen; kompakte Gerätebereiche; 30 Schema-Gehäuse, exaktes Retro 360 TG und lokale PC-Profile; 1.117 gemeinsame Sprach-IDs |
| 10.09.26 | Release-Paketierung | 1.0 | Interne Version 3.4.29.59 INTERN; kein GitHub-Push, Tag oder öffentliches Release |
| 09.09.26 | Display-Effekte / Levita LCD-Orchestrierung / Release-Paketierung | 1.3 / Legacy 3.4.29.58 / 1.0 | Stille Ablehnung gebündelter Bibliotheksvideos behoben: getrennte streng validierte Root-Grenzen für privaten Effektcache und feste Paketmedien, gemeinsame MP4-/Symlink-Prüfung sowie sichtbare Erfolgs-/Fehlerprotokollierung bei Auswahl und Übergabe |
| 09.09.26 | Levita LCD-Datenoberfläche / Orchestrierung / Release-Paketierung | 1.5 / Legacy 3.4.29.57 / 1.0 | Im Log bestätigtes unerwartetes Ende des daemonseitigen Video-Taktgebers; begrenzter 1/2/4-s-IPC-Wiederanlauf mit erneuertem Budget nach stabilem Lauf und datenschutzgefilterter Fehlerausgabe, ohne USB-Neuverbindung oder zweiten Hardwarebesitzer |
| 09.09.26 | Display-Effekte / Lokalisierung / gemeinsame Infrastruktur | 1.2 / 1.0 / Legacy 3.4.29.56 | Fünf transparent attribuierte freie Hauptdesigns mit je vier 1600×720-Farbvarianten und direkter Quellen-/Lizenzanzeige; leere native Fensterdiagnosezeilen durch wiederhergestellte Zusammenfassung beseitigt; 1.098 atomare IDs je DE/EN/ES/FR |
| 09.09.26 | Release-Paketierung | 1.0 | Interne Version 3.4.29.56 INTERN; kein GitHub-Push, Tag oder öffentliches Release |
| 09.09.26 | Reaktionsfähiger Start / Hauptfenster / Mainboard-Kühlung | 1.0 / Legacy 3.4.29.55 / 1.0 legacy | Geräteinitialisierung nach erstem Qt-Zyklus, direkte Laufzeitfähigkeitsprüfung statt synchronem Shell-Check und zusammengefasste CoolerControl-Prüfung außerhalb des GUI-Prozesses; unbekannter Status bleibt fail-closed |
| 09.09.26 | Display-Effekte / Levita LCD-Orchestrierung / Lokalisierung | 1.1 / Legacy 3.4.29.55 / 1.0 | Grafische Ebene-2-Vorschaukarten, Effektart oben in den Einstellungen, schnelleres H.264-Preset und direkter Cachepfad ohne redundanten Galerie-Neuaufbau; 1.083 atomare IDs je DE/EN/ES/FR einschließlich asynchron aktualisiertem Besitzerstatus |
| 09.09.26 | Release-Paketierung | 1.0 | Interne Version 3.4.29.55 INTERN; kein GitHub-Push, Tag oder öffentliches Release |
| 09.09.26 | Display-Effekte / Levita LCD-Orchestrierung | 1.0 / Legacy 3.4.29.54 | Prozeduraler Rauch mit begrenztem Offscreen-H.264-Export, großer Vorschau und bestehender Ebene 2; erzeugtes Medium wird ausschließlich an die vorhandene Levita-/TRCC-Pipeline übergeben |
| 09.09.26 | OpenLinkHub-Update / Corsair-Integration | 1.0 / Legacy | Bestätigtes RPM-/DEB-Update über vorhandene Quellen oder streng erkanntes User-Service-Update aus dem offiziellen GitHub-Archiv mit veröffentlichter SHA-256, sicherer Extraktion, Datenübernahme, lokalem Backup und Rollback; gebündelte Web-UI wird gemeinsam aktualisiert |
| 09.09.26 | Anwendungsaktivierung / Lokalisierung / Hauptfenster | 1.0 / 1.0 / Legacy 3.4.29.54 | Zweitstart aktiviert die laufende Instanz über privaten lokalen Socket; nur Tray-Autostart unterdrückt Desktop-Startfeedback; 1.061 atomare IDs je DE/EN/ES/FR decken Navigation, Seiten, Fan-Karten, Effekte und Updater ab |
| 09.09.26 | Release-Paketierung | 1.0 | Interne Version 3.4.29.54 INTERN; kein automatisches Live-Update und kein GitHub-Push, Tag oder öffentliches Release |
| 08.09.26 | Levita LCD-Abschaltwächter / Levita LCD-Orchestrierung | 1.0 / Legacy 3.4.29.53 | Kontrolliertes Ende löst die feste Levita-ID nach dem Stoppen lokaler Clients begrenzt aus dem TRCC-Daemon, sodass das Firmware-Standardbild zurückkehrt; prozessgetrennter Pipe-Wächter wird nur nach bestätigtem echtem Schreibzugriff aktiv und wiederholt denselben validierten Rückfall einmal bei unerwartetem Elternprozessende |
| 08.09.26 | NZXT Kraken / Release-Paketierung | 1.0 legacy / 1.0 | Kraken-Abschaltreihenfolge und persistenter Unsicherheitsmarker erneut geprüft; interne Version 3.4.29.53 INTERN mit neuem versioniertem Wächtermodul, ohne GitHub-Push, Tag oder öffentliches Release |
| 08.09.26 | Lokalisierung / Hauptfenster und Seitenkomposition | 1.0 / Legacy 3.4.29.52 | Gesamten Sprachbestand einschließlich UI, Einrichtungsassistent und Hilfe in den versionierten Modulordner verschoben; je eine Datei für DE/EN/ES/FR; gleiche stabile Nachrichten-IDs und Katalogprüfung für eindeutige deutsche Quellen sowie fehlende/zusätzliche IDs; Root-Katalog nur noch Kompatibilitätsschnittstelle |
| 08.09.26 | Release-Paketierung | 1.0 | Interne Version 3.4.29.52 INTERN mit Sprachmodul über den vorhandenen `src/modules/`-Paketpfad; kein GitHub-Push, Tag oder öffentliches Release |
| 08.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.51 | Sprachwechsel für alle im vollständigen UI-Aufbau übersetzungspflichtigen interaktiven Texte in DE/EN/ES/FR; getrennte Kataloge für Bedienelemente, Karten und Beschriftungen; werttreue dynamische Galerieübersetzung; vollständiger Offscreen-Wächter und verbindliche Vier-Sprachen-Regel für jede künftige UI-Änderung |
| 08.09.26 | Release-Paketierung | 1.0 | Interne Version 3.4.29.51 INTERN mit neuen Sprachmodulen in Installer, ZIP und RPM; kein GitHub-Push, Tag oder öffentliches Release |
| 08.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.50 | Drei projekt-eigene nahtlose 1600×720-3D-Loops (Orbital Ring, Neon Apex, Quantum Core) als stumme H.264-Videos über die feste Galerie-Allowlist; reproduzierbare Blender-Szenen in `tools/render_levita_loops.py`; keine Hersteller-/Stockmedien |
| 08.09.26 | Mainboard-Kühlung / Hauptfenster und Seitenkomposition | 1.0 legacy / Legacy 3.4.29.50 | Globales Leistungsprofil als konstanter 100-%-Override mit sofortiger Neuauswertung bei laufender OHC-Regelung; bestätigter, rückstellender 0-%-/10-s-Stopptest direkt je Gehäuselüfterkarte; BIOS-Erklärung statt unsicherer Modusbehauptung, wenn der NCT6687-Treiber kein `pwmN_mode` meldet |
| 08.09.26 | Release-Paketierung | 1.0 | Interne Version 3.4.29.50 INTERN; kein GitHub-Push, Tag oder öffentliches Release |
| 07.09.26 | OpenRGB Studio | 1.1 | „Geräte und Effekte“ sowie native Hardwarekanäle klappen als große Bereiche in der RGB-Studio-Seite auf; Aufbau und Zustand in `studio_panels.py`; kein Extra-Fenster, Kanalliste bleibt beim Seitenwechsel sichtbar |
| 07.09.26 | Release-Paketierung | 1.0 | Interne Version 3.4.29.49 INTERN; lokaler Paketbau und Zwei-Versionen-Sicherung; kein GitHub-Push, Tag oder öffentliches Release |
| 07.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.49 | Übersicht „Status & Hinweise“ folgt bestätigten Levita-PWM-Tests: grüner Punkt und OK nach Pumpe/Radiator-Bestätigung, roter Punkt und Fehlerhaft bei offenen Tests oder Sensorfehlern; reines Hinweis-Modell in `src/dashboard_layout.py` |
| 06.09.26 | Projektgedächtnis / Release-Paketierung | 1.0 / Legacy 3.4.29.48 | Dauerhafte Ablage- und Kurz-README-Regel in `docs/ai/AGENTS.md`, `.cursor/rules/70-repository-layout.mdc`, `.github/copilot-instructions.md`, `docs/ai/CLAUDE.md` und `docs/project/DECISIONS.md`; Wächtertest `tests/test_repository_layout_342947.py` (Root-Allowlist, README < 200 Zeilen, höchstens vier Verlaufsversionen). Release-Workflow liest `packaging/VERSION`/`packaging/BUILD_CHANNEL`; Cursor-Globs zeigen auf `src/` |
| 06.09.26 | Release-Paketierung / Gemeinsame Infrastruktur | 1.0 / Legacy 3.4.29.47 | Gesamter Anwendungscode nach `src/` (spiegelt installierte Struktur), Installer/Versionsdateien nach `packaging/`, Dokumente nach `docs/`, `AGENTS.md`/`CLAUDE.md` nach `docs/ai/`, `SECURITY.md` nach `.github/`. `install.sh` erkennt `src/` aus ZIP-Wurzel und `packaging/`; `build_release.py` kopiert aus `SRC_DIR`; Tests, Registerprüfung, Cursor-Globs und Workflows angepasst |
| 06.09.26 | OpenRGB Studio | Legacy 3.4.29.46 | Minütliche Hintergrund-Inventur (`openrgb --client --list-devices`) pausiert, solange das Hauptfenster im Infobereich verborgen ist und kein RGB-Startprofil, keine Schreibfreigabe und keine geplante Wiederholung ausstehen; Regressionstest `tests/test_rgb_inventory_tray_guard_342946.py` |
| 06.09.26 | Release-Paketierung / Gemeinsame Infrastruktur | 1.0 / Legacy 3.4.29.46 | Repository aufgeräumt: Dokumentation nach `docs/project`, `docs/ai`, `docs/hardware`, `docs/security`, `docs/releases`; Distributionsdateien nach `packaging/`; Community-Dateien nach `.github/`. `install.sh` und `scripts/build_release.py` installieren weiterhin flach; `app_constants.helper_script_path` findet Hilfsskripte in beiden Layouts; neue README-Galerie mit sieben aktuellen Screenshots |
| 05.09.26 | Levita-Testumgebung | Legacy 3.4.29.43 | Bereits gestartete Vorschauarbeit gebündelter Medien vor dem synthetischen 140-Video-Belastungstest kontrolliert beendet und Zähler geleert; Workergrenze und vollständige Warteschlange werden anschließend deterministisch geprüft |
| 05.09.26 | Release-Paketierung / Levita-Testumgebung | 1.0 / Legacy 3.4.29.43 | GitHub Actions installiert die vollständigen Python-/Qt-Testabhängigkeiten samt EGL-Laufzeit; Vorschau-Warteschlangentest misst vorhandene gebündelte Medien relativ zum echten Anfangszustand statt einen leeren Cache vorauszusetzen |
| 05.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.43 | Acht weitere eigene 1600×720-KI-Hintergründe und genau eine deduplizierte 30-Sekunden-Animation über eine feste Paket-Allowlist in die OHC-Galerie aufgenommen; Hersteller-/TRCC-Katalogmedien bleiben ausgeschlossen |
| 05.09.26 | Hauptfenster und Seitenkomposition / OpenRGB Studio | Legacy 3.4.29.43 / 1.1 | Gespeicherten RGB-Profilstart bei absichtlich zurückgehaltener erster OpenRGB-Teilerkennung vorgemerkt gehalten; begrenzte Inventarwiederholung übernimmt das Design nach vollständiger Erkennung statt den einmaligen Startwunsch zu verwerfen |
| 05.09.26 | Release-Paketierung | 1.0 | Modulregisterprüfung vom fest verdrahteten internen Kanal auf den validierten Inhalt von `packaging/BUILD_CHANNEL` umgestellt; stabilen RPM-Quellbaum unter einen eigenen temporären Elternordner gelegt, damit er nicht mit dem gleichnamigen Laufzeitbaum kollidiert |
| 05.09.26 | Wallpaper Engine for KDE | 1.2 | Pause/Fortsetzen/Weiter/Ton vom nicht vorhandenen separaten Alias auf das nachweislich unter `org.kde.plasmashell` registrierte `/WallpaperEngine`-Objekt umgestellt; Zurück wegen fehlender echter CaptSilver-v1.4-API über die vorherige validierte lokale Workshop-Karte umgesetzt; DisplayMode 0/1/2 pro Zielbildschirm ergänzt |
| 05.09.26 | Fensterplatzierung | 1.0 | Hauptbildschirm als Standard sowie persistente Auswahl über den stabilen Qt-Bildschirmnamen mit sicherem Hauptbildschirm-Rückfall eingeführt; Platzierung bleibt unter Wayland eine Anforderung an KWin |
| 05.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.42 | Wiederhergestellte Fenstergeometrie vor dem Anzeigen an die Bildschirmpräferenz gebunden und alle Scrollbereiche, Listen und Tabellen über ein gemeinsames acht Pixel schmales Scrollleisten-Design vereinheitlicht |
| 05.09.26 | Wallpaper Engine for KDE | 1.1 | Wiederaufrufbaren Erststart-Assistenten, Fünf-Workshop-Checkliste, Steam-/Workshop-Links und Fedora-Installer ergänzt; offizielles RPM wird vor der getrennt bestätigten Polkit-/DNF-Aktion anhand GitHub-Metadaten, Fedora-Version, Architektur, Größe und SHA256 geprüft; Galerie behält nach Apply-Refresh feste Kartenmaße |
| 05.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.41 | Neue Standardfolge LCD → Wallpaper Engine → optional OpenLinkHub → Profile → Einstellungen → Über → Log; nur exakt alte Standardfolgen werden migriert, eigene Sortierungen bleiben erhalten; eigene Wayland-Fensterdekoration wegen separatem Eingabe-/Resize-Testumfang bewusst auf eine Folgeversion verschoben |
| 05.09.26 | Release-Paketierung | 1.0 | Sicherheitsbericht weist den einzigen ausdrücklich ausgelösten und SHA256-verifizierten Plugin-Download getrennt von weiterhin verbotenen automatischen Desktop-Downloads aus |
| 05.09.26 | Wallpaper Engine for KDE | 1.0 | Lokale Workshop-/Video-Galerie, Multi-Monitor-Auswahl, CaptSilver-D-Bus-Steuerung, Original-KCM, sichere Videoordnergrenze und rücksetzbares Leistungsprofil ohne Upstream-Patches ergänzt |
| 05.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.40 | Wallpaper Engine als frei anordenbaren sichtbaren Navigationspunkt und zwölfte Hauptseite ergänzt; integriertes Hilfethema verweist auf den sicheren Original-/Optimierungsweg |
| 04.09.26 | Gemeinsame Infrastruktur | Legacy 3.4.29.39 | Normale Qt-Tooltips und direkte ComboBox-Popupframes aus der Fensterdiagnose gefiltert; unbekannte Popups und exakte 640×480-Quarantäne bleiben aktiv |
| 04.09.26 | OpenRGB Studio | 1.1 | Hardwarefreie Designgalerie aus dem Hauptorchestrator ausgelagert; Engine-Steuerung in „Geräte und Effekte“ eingebettet, Ein/Aus-Schalter, persistente effektabhängige Rechtsklick-Farben, Gesamthelligkeitsleiste und native Kanalergebnisse ergänzt; frühe Sequenzabbrüche schließen ENE-Callbacks zuverlässig ab |
| 03.09.26 | Release-Paketierung | 1.0 | Externen Geschwisterordner `Open Hardware Control Backup` eingeführt; erfolgreiche Builds sichern atomar alle Artefakte, Entwicklerquellen und SHA256 und bewahren ausschließlich die zwei neuesten erkannten Versionsordner auf |
| 03.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.35 | Veralteten TRCC-Handshake nach Abziehen reproduziert; vor Design, Farbtest und Displayeinstellungen eine serialisierte Trennen-/Neuverbinden-Barriere mit verpflichtendem echtem Handshake ergänzt und am 1600×720-Gerät validiert |
| 03.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.34 | Validierten privaten Cache mit verknüpften Medien wieder als Runtime-Theme zugelassen, externe Importgrenze symlink-strikt belassen und beim kontrollierten Beenden einen auf 1,5 Sekunden begrenzten `stop-video`-Daemonaufruf ergänzt |
| 01.09.26 | Levita LCD-Datenoberfläche | 1.0 | Versionierten Modulordner eingeführt; einzelne Live-Datenblöcke einschließlich zusammengefasster CPU/GPU-Beschriftung plus Auslastungswert, gemeinsamer Offset, Kontextbearbeitung, klare Cache-Statusmeldungen, OHC-Override-Persistenz und read-only TRCC-Staging getrennt |
| 01.09.26 | Projektarchitektur | 1.0 | Verbindliche Modul-, Größen-, unabhängige Anwendungs-/Modulversions-, Datums- und Registerpflege-Regeln für lokale KIs eingeführt |
| 01.09.26 | KI-Entwicklungsanleitung | 1.0 | Verbindliche Schrittfolgen für UI-, Sensor- und LCD-Erweiterungen sowie Abschlusskontrolle ergänzt |
| 01.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.19 | Editierbare Cache-Themes mit validiertem `trcc.json` als vollständige TRCC-Hardwaredesigns zugelassen; doppelte Vorschauaufbauten beim Auswahlwechsel entfernt |
| 01.09.26 | Levita LCD-Datenoberfläche | 1.1 | Vorschau auf TRCC-Mittelpunkt-Koordinaten korrigiert; Videoframes aktualisieren nur den Hintergrund und lassen aktive Drag-Objekte bestehen; Rechtsklick fordert den eingebetteten Seiteneditor statt externer Dialoge an |
| 01.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.20 | Erneute Auswahl lädt Hintergrund und Datenebene sofort; letzter gültiger Videoframe bleibt während asynchroner Vorbereitung sichtbar |
| 01.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.20 | Dashboard-Anordnung in `src/dashboard_layout.py` extrahiert; Kraken-Wassertemperaturkarte ohne verbundene Hardware oder echten Kühlmittelwert automatisch verborgen, gespeicherte Benutzerauswahl bleibt erhalten |
| 02.09.26 | Levita LCD-Datenoberfläche | 1.1 | Gerade Notch-Innenkante und abgerundete äußere rechte Displayecken in `panel_geometry.py`; Vorschau und erzeugtes Cachebild nutzen dieselbe Kontur |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.21 | Klick auf eine Ebene-1-Karte setzt Bild oder gecachten Videoframe sofort in die große Vorschau; kein erzwungenes Schwarz vor dem ersten Standbild |
| 02.09.26 | Levita LCD-Datenoberfläche | 1.2 | Fehlerhafte importierte Einzelelemente werden isoliert übersprungen; sichere Split-Modus-Richtlinie ergänzt und einzigen aktuellen Modulordner auf `v1_2` angehoben |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.24 | Symlink-Dateien in TRCC-Themes abgewiesen; Livestream erst nach `QProcess.started` als aktiv gemeldet; Startfehler in begrenzten Autostart-Retry geführt; Hover-ffmpeg und Timer beim Beenden vollständig gestoppt |
| 02.09.26 | Release-Paketierung | 3.4.29.24 | Installationspaket und vollständiges Entwicklerpaket als getrennte Profile validiert; Local-AI-Gitbundle aus einem temporären Snapshot exakt des geprüften Entwicklerbaums statt aus möglicherweise älterem Commit erzeugt |
| 02.09.26 | GitHub-/KI-Arbeitsregeln | 3.4.29.25 | Normalen, ausdrücklich beauftragten Entwicklungsbranch-Push auch bei `INTERN` eindeutig von Pull Request, Tag, öffentlichem Release, Force-Push und Remote-Löschung getrennt; widersprüchliche absolute Push-Sperre entfernt |
| 02.09.26 | Levita LCD-Datenoberfläche | 1.3 | Gewähltes Hintergrundvideo und erzeugte Displaymaske gemeinsam mit den bearbeiteten Live-Blöcken in ein Cache-Theme eingebunden; TRCC kann die komplette Komposition in einer verbundenen `load-theme`-Sitzung anwenden |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.26 | Schnelle vollständige Designwechsel auf den letzten Wunsch zusammengefasst, zehn Sekunden Schutzpause nach bestätigtem Start und Handshake-Timeout auf insgesamt einen Retry begrenzt |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.27 | Alpha-Kanal der Ebene-2-Grafik in der großen Vorschau erhalten, ausgewählte Videos als begrenzte 16-Bild-Folge animiert und externe TRCC-/libusb-Prozessabstürze ausdrücklich erkannt |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.28 | Alle TRCC-Befehle über den offiziellen Daemon-/Unix-Socket-Modus an einen einzigen USB-Besitzer geleitet und den zweiten `display play`-Prozess nach erfolgreichem `load-theme` entfernt |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.29 | Kombinierte Design-/Notch-Maske nach `load-theme` ausdrücklich aktiviert, Video über einen reinen Daemon-IPC-Taktgeber weitergeschaltet und Vorschauframes nur einmal vorab skaliert; Levita-Fachmodul bleibt 1.3 |
| 02.09.26 | Levita LCD-Datenoberfläche | 1.4 | Rechte Außenkante der sichtbaren Video-/Bildfläche am schwarzen Balken mit getrennt einstellbarem oberen und unteren Radius versehen; gekoppelte Bedienung bleibt Standard, Vorschau und Hardwaremaske verwenden dieselbe reine Geometrie |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.30 | Eingebettete Radiusregler mit 48-px-Standard, 0–240-px-Bereich und optional getrennter oberer/unterer Einstellung ergänzt; rote Fotomarkierung ist kein UI- oder Renderbestandteil |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.31 | „Design anpassen“-Felder und Auswahlfenster lesbar vergrößert: eigene Zeile für den schwarzen Balken, Mindestmaße für Zahlen- und Auswahllisten, Panel darf nicht unter seine natürliche Höhe schrumpfen |
| 02.09.26 | Gemeinsame Infrastruktur | 1.0 legacy | Fensterdiagnose löst das Log-Widget vor Qt-aboutToQuit; gelöschte Log-Widgets erzeugen beim Beenden keinen Shiboken-RuntimeError mehr |
| 02.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.32 | „Design anpassen“ rechts neben die Live-Vorschau gelegt; Hintergrund- und Datenkarten füllen 4–8 Spalten über die volle Galeriebreite |
| 02.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.32 | Helles Design: Navigationsleiste hell, Menütext und Auswahl dunkel, keine weiße Highlight-Schrift auf blassem Akzent |
| 03.09.26 | Levita LCD-Orchestrierung | Legacy 3.4.29.33 | Ebene-1/2-Galerien nebeneinander; eigener Ordner mit direkter Ebenenzuweisung; Favoritenfilter; zwei projekt-eigene Weltraum-Layouts; native `trcc.json`-Ordner im sicheren Import; einmalige Migration des Notch auf das physische 80-px-Minimum |
| 03.09.26 | OpenRGB Studio | 1.0 legacy | Ausgewählte Vorlage und je Vorlage angepasste Farben dauerhaft gespeichert; Aurora-Vortex und Galaxie-Komet ergänzt; ENE-DRAM nach direktem Startreclaim dreimal zeitversetzt und begrenzt erneut initialisiert |
| 03.09.26 | Hauptfenster und Seitenkomposition | Legacy 3.4.29.33 | Standard-Skalierung und gemeinsame Abstände verkleinert; Softwarelinks in kurzen Komponentenkarten; unterstützte Geräte in Über und Hilfe ergänzt |
| 03.09.26 | Levita LCD-Orchestrierung / gemeinsame Infrastruktur | Legacy 3.4.29.37 | Persistente Intensitätsregler für beide Ebenen, explizite Einheitenmigration, Orbital-Standard 130 %, read-only GPU-Taktgrenzfallkorrektur über Daemon-IPC und getrennte Hardware-Auffälligkeitsansicht ergänzt |

| 19.09.26 | Fensterplatzierung / GPU-Steuerung / Lokalisierung | 1.5 / 1.0 / 1.0 | `.105`: KWin bestätigt den tatsächlichen Wayland-Ausgang statt Qt-Selbstmeldung; PID-/Titelbindung, begrenzter Hilfsprozess und einmalige Korrektur. LACTs Overdrive-Bootvorbereitung nur nach Bestätigung in getrenntem Hilfsprozess, manueller Neustart. 1.607 gemeinsame Sprach-IDs. |
| 19.09.26 | UI-Leistung / Galerievorbereitung | 1.1 | `.105`: LCD-Studio-Hostfeld `window` überschattet `QWidget.window()`; Ereignisfilter ruft die Qt-Methode für beide Widgets direkt auf. Laufender `.104`-Prozess protokollierte die Ausnahme wiederholt; Regressionstest ergänzt. |
| 19.09.26 | Anwendungsabschluss / Hauptfenster | 1.1 / Legacy 3.4.29.105 | `.105`: X/Fensterschließen blendet immer in den Infobereich aus, ohne Tray in die Taskleiste; kein Hardware-Shutdown. Datei-/Kopfmenü schließen nur das Fenster. Sichtbares manuelles Beenden ausschließlich über das Rechtsklickmenü des Tray-Symbols; Sitzungsende separat. Automatische Tray-Journalwahl migriert keine historische explizite Präferenz. |

Entwicklung 06.10.26: SDK-6-Parser und UUID-/ACK-Verträge liegen getrennt in
`rgb_studio/v1_15/sdk_v6.py`; laufende Effekte bleiben vollständige Geräteframes.
Hardwarekarten, Snapshot-Mixins, GPU-Komposition, Themefragmente und Zusatztexte
bleiben fokussiert; vier Sprachkataloge besitzen aktuell jeweils 2.228 gemeinsame IDs.
Verzögerte Hardware-Fix-/GPU-Aufrufe sind QObject-gebunden; Hardware-Checker
validiert die aktuelle Prozessidentität vor Antwort-/Fristverarbeitung.
Alle 14 verzögerten LCD-Aufrufe sind an ihr Fenster gebunden; reale Qt-Tests
prüfen Bibliotheks-/Fortschrittsabbruch nach Löschung und lebende Gegenproben.
OpenLinkHub folgt weder Weiterleitungen noch Umgebungs-Proxies. GPU-Lüftertexte
nutzen `visuals.py`/`WrappedCheckBox`; schmale Seiten bleiben vollständig scrollbar.

Prüfabschluss .178: Vollständiger Release-Wächter mit 1.624 Tests und fünf
Untertests bestanden. 433 Python-Laufzeitquellen und 2.501 gemeinsame Sprach-IDs.
Sicherheits-/Datenschutzprüfung, Modulbudgets und Repository-Verträge bestanden.
Alle acht neuen Videos vollständig dekodiert; periodische Renderer und
Schleifennaht dokumentiert. Bestehende Medien-Prüfsummen unverändert.
Dunkle, helle und schmale Qt-Ansicht geprüft. Vorhandene Fedora-/Ubuntu-Fixtures
bestanden; kein realer Fedora- oder optischer LCD-Livetest wird behauptet.
Paketbau, Sicherungsverifikation und lokaler Versionswechsel folgen.

Lokaler Abschluss .178: Alle sechs Artefakte, beide .177/.178-INTERN-Sicherungen
und 433 identische Python-Quellen in ZIP/DEB/RPM geprüft. Alle neuen Videos und
Poster sind in den drei Laufzeitpaketen bytegleich. Private .177-Installation
sowie endgültige Einstellungen/Profile/beide Plugins vor Start gesichert.
Benutzer- und Systemkopie .178 installiert; DPKG 3.4.29.178~intern2 bestätigt.
Profile und beide Plugins erhalten, gestartete Benutzerkopie ohne Python-Traceback.
Der Benutzer meldet anschließend einen CPU-Sensorfehler beim Profilstart;
dieser steht bereits im Log und wird als gesonderte .179 untersucht.
Keine GitHub-Veröffentlichung.

Prüfabschluss .179: Vollständiger Release-Wächter mit 1.642 Tests und fünf
Untertests bestanden. 438 Python-Laufzeitquellen und 2.507 gemeinsame Sprach-IDs.
Echte viersprachige Qt-Konstruktion einschließlich fehlend→frisch-Profilwarten
ohne Hardwareaktion geprüft. Strikter Fristablauf, Neuauftrag, Bedienänderung,
Shutdown, Geräteverlust, Hook-Delegation, zentraler Modul-Sink und konkurrierende
Fehlerschreiber bestehen. Sicherheit/Datenschutz/Modulbudgets unverändert erfüllt.
Bestehende Fedora-/Ubuntu-Fixtures bestanden; kein realer Fedora-/PWM-Ausfalltest.
Paketbau und lokaler Upgrade-Nachweis folgen. Keine GitHub-Veröffentlichung.

Lokaler Abschluss .179: Alle sechs Artefakte und beide .178/.179-INTERN-
Sicherungen mit SHA256 geprüft. ZIP-CRC, 438 identische Python-Quellen in
ZIP/DEB/RPM, neue Medien/Poster sowie DEB-Modi und RPM-Eigentümer geprüft.
Private .178-Installation und endgültige Einstellungen/Profile/Plugins vor
Start gesichert. Benutzer- und Systemkopie .179 installiert, DPKG bestätigt
3.4.29.179~intern2; beide Quellbäume und neuen Medien bytegleich. Profile und
beide nativen Plugins auch nach Start unverändert.

Realer Startnachweis auf dem vorhandenen Ubuntu-System: CPU-Snapshot beim
Profilaufruf 2,89 s alt, also korrekt nicht verwendbar. Das Profil wartet
asynchron und erhält noch in derselben Sekunde einen frischen Wert; der
bisherige modale CPU-Fehler tritt nicht auf. Sensorprozess mit korrekter
Versionsangabe gestartet, keine neuen expliziten Fehlerzeilen im Sitzungslog.
Fünf native RGB-Arbeiter ohne gemeldete Fehlerzähler. Eine nicht fatale
Qt-Portal-Registrierungswarnung wird jetzt ausdrücklich als Warnung im
allgemeinen Log erfasst; deren Betriebssystemursache wurde nicht geändert.
Kein Rechnerneustart-/Fedora-Livetest und kein GitHub-Upload durchgeführt.
