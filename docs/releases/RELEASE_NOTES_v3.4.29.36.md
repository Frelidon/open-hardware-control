# Open Hardware Control 3.4.29.36 INTERN

> Interner Entwicklungs- und Sicherungsstand. Nicht als öffentlicher GitHub-Release vorgesehen.

## Rollierende vollständige Sicherungen

- Jeder erfolgreiche Versionsbau erzeugt außerhalb des Repositorys im Geschwisterordner `Open Hardware Control Backup` einen vollständig sortierten Versionsordner.
- Gesichert werden das universelle Installationspaket, das vollständige Entwicklerpaket, Quellarchiv, Local-AI-Git-Bundle, alle tatsächlich erzeugten RPM-/DEB-Pakete, diese Release Notes und frische SHA256-Prüfsummen.
- Die zwei neuesten semantischen Versionen bleiben erhalten. Die atomare Bereinigung erkennt nur exakt benannte OHC-Versionsordner und bewahrt fremde Inhalte.
- Backups innerhalb des Repositorys werden abgewiesen, damit Archive nicht rekursiv wachsen.
- GitHub Copilot, Cursor und lokale Coding-KIs erhalten die gleiche verbindliche Regel über die Projektanweisungen.

Die bestehende Levita-Wiederverbindung aus 3.4.29.35 und alle vorherigen Hardware-Sicherheitsgrenzen bleiben unverändert.
