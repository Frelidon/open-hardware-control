# Open Hardware Control 3.4.29.170 INTERN

Interner Prüfstand vom 11.11.26. Der Eigentümer hat die lokale Installation
freigegeben. GitHub-Veröffentlichung bleibt bis zur Sicht- und Neustartprüfung
zurückgestellt.

- Einstellungen bleiben erreichbar: Statuskarte ohne Ausschalter, geschützte
  Navigationsbearbeitung und Rücknahme alter gespeicherter Ausblendungen.
- Hauptinhalt statt linkem Menü animiert: sanftes Einblenden, seitliches oder
  vertikales Gleiten, Lichtakzent und wählbare Dauer mit ruhigem 380-ms-Standard.
- Zwölf RGB-Vorschläge nutzen die responsive Galeriefläche.
- Native RGB-Übertragung bleibt bei kurzzeitigen Verbindungsfehlern bevorzugt;
  SDK-Fallback erst nach wiederholtem Fehler und bestätigtem nativen Stopp.
- Benutzerinstallation korrigiert vorhandene OHC-Autostarts auf den erneuerten
  Starter; deaktivierter oder fehlender Autostart bleibt unverändert.
- Darstellung und native Wiederherstellung in fokussierte Module ausgelagert;
  fünf zusätzliche Sprachquellen und alle geänderten Texte in DE/EN/ES/FR.

Die Diagnose bestätigt heute eine laufende installierte .168 mit OpenRGB 1.0.
Sie enthält die gestern getestete native Anbindung noch nicht. Der neue
Quellstand bevorzugt OpenRGB 1.1 und bewahrt die .169-GPU-Übergabe an External
Control. Die bestehende Sitzung wurde zur Diagnose nicht verändert. Optische
Bestätigung und reale Fedora-Prüfung bleiben bis zum passenden Lauf offen.
Interner lokaler Paketbau für die Eigentümerprüfung; noch keine öffentliche
Veröffentlichung.

Prüfung: 1.373 Tests und fünf Untertests einschließlich echter viersprachiger
Qt-UI, nativer C++-Fixtures, Socket-/Recovery-Tests und unveränderter Fedora-
sowie Ubuntu-Richtlinien. Sicherheits-, Datenschutz-, Modul- und Größenprüfung
bestanden. Reale Hardware-/Sichtprüfung bleibt gesondert offen.

Lokale Installation am 11.11.26 abgeschlossen: System- und Benutzerkopie
stimmen mit allen 388 Python-Quellen überein. Autostart und Desktopstarter
verwenden .170. Native Engine mit fünf aktiven Arbeitern und null gemeldeten
Fehlern; Sapphire External Control lesend bestätigt. Airgoo-API etwa 59,7 Hz,
keine optische FPS-Zusage. Bestehendes RGB-/Levita-Startdesign aktiv.
Sicht- und Rechnerneustartprüfung durch den Eigentümer noch offen; GitHub
bleibt unveröffentlicht. Beide .169/.170-Sicherungen sind SHA256-bestätigt.
