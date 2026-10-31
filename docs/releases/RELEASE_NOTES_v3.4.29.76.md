# Open Hardware Control 3.4.29.76 INTERN

## Behobener Levita-Langzeitfehler

- Der gelieferte vollständige Sitzungslog und das Systemjournal belegen den Abbruch: Der TRCC-Daemon wuchs nach rund acht Stunden auf etwa 15,5 GB RSS und wurde am 12.09.2026 um 11:36:54 vom Kernel-OOM-Killer beendet.
- Der danach gestartete Daemon hielt das Levita-USB-Gerät, während der vorhandene Videotaktgeber seine IPC-Verbindung verloren hatte. Die bisherigen drei Taktgeber-Wiederanläufe konnten diesen Besitzwechsel nicht reparieren.
- Das neue Modul Levita-Daemongesundheit 1.0 prüft den eigenen, exakt als `trcc daemon` identifizierten Benutzerprozess nun einmal pro Minute rein lesend. Ab 1 GiB RSS wird der Taktgeber beendet, der Daemon kontrolliert per `trcc kill` freigegeben und das ausgewählte Design über dieselbe einzelne TRCC-Warteschlange neu übertragen.
- Ein erkannter IPC-Verbindungsabbruch löst denselben begrenzten Wiederherstellungsweg sofort aus. Eine Fünf-Minuten-Sperre verhindert Neustartschleifen; fremde Prozesse und direkte USB-Abschüsse bleiben ausgeschlossen.

## Laufzeit- und Fehlerprotokoll

- Die sichtbaren allgemeinen und Hardware-Protokolle sind jetzt zeitbasierte Ringpuffer für die jeweils letzten 60 Minuten. Abgelaufene Zeilen werden fortlaufend ersetzt; harte Grenzen von 30.000 Zeilen beziehungsweise 4 MiB schützen den Arbeitsspeicher bei außergewöhnlich hoher Ereignisrate.
- `session.log` und `previous-session.log` bleiben vollständige private Sitzungsprotokolle. Erkannte Laufzeitfehler und unbehandelte Python-Abstürze werden zusätzlich datenschutzbereinigt in das auf 2 MiB begrenzte `errors.log` geschrieben.
- Die Diagnoseerfassung nimmt die letzten 400 Zeilen des Fehlerprotokolls auf. Alle privaten Zustandsdateien verwenden weiterhin Modus `0600`.
- Deutsch, Englisch, Spanisch und Französisch bleiben mit 1.291 gemeinsamen Nachrichten-IDs vollständig. Interner Build; kein GitHub-Push, Tag oder öffentlicher Release.
