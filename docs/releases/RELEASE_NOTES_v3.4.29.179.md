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
