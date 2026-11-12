# Open Hardware Control 3.4.29.181 INTERN

Gehäuse und Profile verwenden gemeinsam große gestaltete Bereichsköpfe. Die
Gehäuseübersicht erhält eine eigene Profil-/Gehäuseauswahl, eine hervorgehobene
PC-Zeichnung und eine direkte Komponentenkarte. Erweiterte Profilaktionen,
Lüfterkatalog und Referenzwerte bleiben erreichbar. Vorhandene Gehäuse-, LED-,
ARGB-/PWM-Zuordnungen und eigene Entwürfe werden weiterverwendet.

Geöffnete Bereiche werden innerhalb ihres bestehenden Scrollbereichs mit einer
begrenzten 420-ms-Bewegung sichtbar gemacht. Schließen führt nur dann zurück,
wenn der Bereich noch die automatische Bewegung besitzt. Rad, Berührung,
Tastatur, Scrollleistenbedienung und Seitenwechsel beenden diese Führung;
abgeschaltete Animationen bleiben berücksichtigt. Es werden keine Bildschirm-
kopien oder zusätzlichen Hintergrunddecoder angelegt.

Designs & Spiele 1.1 bietet 15 unterschiedliche abgestimmte RGB/LCD-Paare.
Die fünf bisherigen Paar-IDs und 35 RGB-Vorlagenindizes bleiben erhalten;
zehn neue RGB-Vorlagen nutzen vorhandene Renderer und originale gebündelte
OHC-Videos. Jedes Paar besitzt eine echte LCD-Motivgröße von 50–200 Prozent.
Matrix bietet zusätzlich die tatsächlich vorhandenen Zeichengrößen
100/130/150/200 Prozent, mit 130 Prozent als Standard. Die Auswahl wird je Paar
bewahrt; Schieberegler und Vorschau übertragen keine Hardwarebefehle.

Eine ausdrücklich angeforderte Größenänderung wird bei Bedarf mit einem
begrenzten asynchronen ffmpeg-Prozess als unverzerrte, zentrierte lokale Kopie
vorbereitet. Neue Auswahl, neue Größe, Verlassen der Seite oder Programmende
verwerfen veraltete Aufträge. Eine inzwischen neuere LCD-Absicht verwirft auch
ein verspätet eintreffendes Ergebnis. Nur ein zum festen Originalmedium und zur
Größe passendes geprüftes Cache-Ergebnis darf den bestehenden LCD-Anwendenweg
aufrufen. Die Strukturprüfung liest höchstens 1 MiB Metadaten, 512 MP4-Atome
und acht Verschachtelungsebenen; sie verlangt H.264, 1600×720 und eine positive
Dauer bis 35 Sekunden. Sie dekodiert dabei keine Videoframes im GUI-Thread.
Originalmedien und Ebene 2 mit Sensordaten bleiben erhalten. Die Paare sind
visuell abgestimmt; sie versprechen keine Frame-Synchronisation der Geräte.

Der LCD-Medienmanager 1.1 öffnet als integrierter Editor auf der Levita- und
Kraken-Seite. Vorhandene Quellen und Medien werden aus der bestehenden Inventur
übernommen; Öffnen startet keinen rekursiven Ordnerscan. Erst Speichern übernimmt
Änderungen. Anzeigenamen und Ausblendungen verändern oder löschen keine
Originaldateien. Der Fortschrittsbalken benennt nun ausdrücklich die Vorbereitung
der Galerievorschauen mit erledigter/Gesamtzahl; er ist kein LCD-Transferstatus.

Die Hilfe erhält eine oben ausgerichtete Themenbibliothek und eine lesbare
Artikelfläche. Bestehende Suchbegriffe, vier Sprachinhalte und sichere interne
Seitenlinks bleiben erhalten. Übersichtskarten unterscheiden erkannte lokale
Hardwaredaten von aktuellen Messwerten und Steuerfreigaben. CPU-Kerne/Threads
verwenden bestätigte Daten. Die untere Hardwareliste zeigt tatsächliche bereits
vorhandene Inventuren und verwechselt Levita nicht mit NZXT.

Der GPU-Bereich zeigt den tatsächlichen LACT-Lesestatus statt einer pauschalen
Sicherheitsanzeige. Fehlgeschlagene Leseabfragen markieren frühere Werte als
nicht aktuell und protokollieren begrenzte datenschutzgefilterte Fehler.
Kurztest, CoolerControl-/Besitzschutz und bestehende Schreibwege bleiben
unverändert. Ein größerer GPU-/Lüfterkurven-Umbau und die weitere Bereinigung
der alten LCD-Oberflächen bleiben getrennte spätere Schritte mit Entwürfen.

Der beim vollständigen Rendern gefundene Qt-Layoutabsturz ist behoben: Die beiden
Gehäuse-/Profilkomboboxen erhalten vor dem Herausnehmen aus ihren bisherigen
Layouts ausdrücklich einen Qt-Eigentümer. Eine begrenzte Mindestinhaltsbreite
verhindert außerdem horizontales Abschneiden im schmalen Gehäusefenster.

Entwicklungsnachweis: 30 aktuelle Hub-/Größen-/Metadatenregressionen und
184 RGB-Schleifenprüfungen bestanden. Zwölf Abschnitts-/Gehäusetests prüfen
Scrollabbruch, Lebensdauer, unveränderte Zuordnungen und vollständige
Hauptfensterrenderings bei 2551×1337, 1440×1000 und 1000×900 in beiden Themen.
Hub, Gehäuse und Hilfe wurden im echten Qt-Hauptfenster ohne Hardwarezugriffe
aufgenommen; aufgeklappte Gehäusebereiche bleiben erreichbar. Vier vollständige
UI-/Lokalisierungstests bestätigen 2.584 gemeinsame Nachrichten in DE/EN/ES/FR.
Diese Prüfungen ersetzen keinen Paket- oder Installationsnachweis.
Quellfreigabe abgeschlossen: 1.732 Tests und fünf Untertests, Kompilierung,
Sicherheits-/Datenschutzscan, Modulbudgets und übrige Release-Prüfungen bestanden.
Alte lokale Bytecode-Caches wurden vor Fortsetzung der restlichen Wächterprüfungen
entfernt. 464 Python-Laufzeitquellen; Paket-/Zwei-Versionen-Sicherungsverifikation
und lokale Benutzer-/Systeminstallation stehen noch aus. Kein GitHub-Upload oder Release
beauftragt; keine neue Hardwarefreigabe oder reale Fedora-Prüfung behauptet.
