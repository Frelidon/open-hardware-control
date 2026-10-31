# Open Hardware Control 3.4.29.157 INTERN

Diese interne Version schließt die aktuell noch umsetzbaren Repository-Punkte:
Sie ergänzt den Programme-Reiter bis zur sicheren AppImage-Zuordnung und
repariert den im Besitzerlog belegten Levita-Daemon-Übergabefehler.

## Programme und GitHub-Releases

- Installierte Anwendungen werden begrenzt und außerhalb des Qt-Hauptthreads
  aus Desktop-Einträgen gelesen; deren `Exec`-Inhalt wird nie ausgeführt.
- Profile unterstützen getrennte Ziele für Flatpak, Snap und AppImage. Der
  exakte Installationsplan wird vor einer Aktion angezeigt und erneut bestätigt.
- Ein GitHub-Release wird nur nach einem ausdrücklichen Klick geprüft und lädt
  höchstens 100 offizielle Assets sowie beide Source-Code-Archive. Größen,
  erlaubte Hosts und Bytezahlen werden kontrolliert; SHA256SUMS und ein Manifest
  werden in einem atomar veröffentlichten neuen Versionsordner geschrieben.
- Ein bestimmtes AppImage aus diesem Download kann nun direkt einem ausgewählten
  AppImage-Profil zugeordnet werden. Die Datei muss im inspizierten Plan stehen,
  regulär und nicht verlinkt sein sowie die von GitHub gemeldete Größe besitzen.
  Vor der späteren Aktivierung gelten zusätzlich die bestehenden Pfad-, Größen-,
  ELF- und AppImage-Headerprüfungen.
- Uneindeutige Systempakete bleiben ohne bestätigte distributionsspezifische
  Paketquelle deaktiviert.

## Thermalright Levita

- Das Nutzerlog zeigte einen USB-Konflikt direkt nach dem Start des in derselben
  OHC-Sitzung registrierten TRCC-Daemons. OHC unterscheidet diesen belegten Fall
  jetzt von einem wirklich fremden Besitzer.
- Stimmen Sitzungsbesitz, PID, Benutzer und exaktes `trcc daemon`-Kommando überein,
  wird einmal der vorhandene begrenzte Neustart mit Wiederherstellung des zuletzt
  akzeptierten Designs ausgeführt.
- Vorhandene, fremde, nicht lesbare oder PID-abweichende Prozesse bleiben
  unangetastet. Die Schutzzeit verhindert eine automatische Endlosschleife.

## Weitere Änderungen und Grenzen

- Die Gehäuselüftervorschau hebt nichtschwarze Lichtsegmente geringfügig und
  gecacht an; Effektphase, physische Zuordnung und Hardwareausgabe bleiben gleich.
- Python/PySide6 bleibt die modulare Architektur. Performanceänderungen benötigen
  weiterhin eine reproduzierbare Messung; ein vollständiger Rust-Neubau ist kein
  offener Umsetzungspunkt.
- Die Code-/Fixture-Prüfungen ersetzen keine reale Fedora-Hardwareprüfung und
  keine optische Bestätigung von RGB-Helligkeit, Richtung oder LED-Reihenfolge.
  Diese beiden Nachweise bleiben ausdrücklich offen.

## Veröffentlichung

Kanal: **INTERN**. Diese Version wird lokal paketiert und gesichert; sie ist kein
öffentlicher GitHub-Tag oder GitHub-Release.
