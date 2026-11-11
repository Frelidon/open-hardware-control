# Open Hardware Control 3.4.29.179 INTERN

Die gemeldete CPU-Sensorwarnung beim Profilstart stand bereits im Log. Kurz zuvor
war eine gültige Temperatur vorhanden; beim Profilaufruf fehlte ein frischer
Snapshot. Diese Version wartet bei einer CPU-Profilkurve bis zu zehn Sekunden
asynchron auf den bestehenden Sensorprozess. Es gibt keinen geratenen Temperatur-
oder synchronen sysfs-Ersatz; die 2,5-s-Frischegrenze bleibt unverändert.

Neue Profil-/Kühlaufträge, geänderte Bedienelemente, Shutdown, verlorenes Kühlgerät
und Fristablauf verwerfen die wartende Anwendung. Nur ein frischer Wert führt
zur erneuten Prüfung im bestehenden geschützten Kühlpfad. Bleibt er aus, wird
die Kurve nicht übertragen und der Fehler mit Sensorzustand ohne Dialog geloggt.

Python-, Thread-, Unraisable- und Qt-Warnungs-/Fehler-Hooks ergänzen die private
Fehlerdatei. Eine begrenzte thread-sichere Brücke übernimmt auch vorhandene
Modulfehler in das sichtbare allgemeine Log und Sitzungslog. Rückkopplung und
doppeltes Schreiben werden vermieden; gleiche Warnungen kurz dedupliziert.
Bestehende Crash-/Native-Protokolle und ursprüngliche Exception-Hooks bleiben.

Profilkarten, sechs Videohintergründe, Matrix-LCD-Größen und vorhandene persönliche
Einstellungen aus .178 bleiben erhalten. Keine GitHub-Veröffentlichung.
Synthetische Tests sind kein realer Fedora- oder physischer PWM-Ausfallversuch.
Prüf-, Paket- und Installationsnachweise stehen im Projektstatus.

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
