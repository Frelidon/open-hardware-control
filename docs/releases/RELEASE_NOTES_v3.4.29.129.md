# Open Hardware Control 3.4.29.129 INTERN

Datum: 01.10.2026

## Behobener Programmabschluss

- Nach einem von OHC kontrollierten Neustart des Levita-/TRCC-Daemons wird die
  neue Prozess-ID nun als eigener Ersatzprozess übernommen.
- Die Übernahme erfolgt nur, wenn die bisherige eigene PID nachweislich nicht
  mehr existiert und der neu beobachtete Prozess exakt als TRCC-Daemon erkannt
  wurde. Fremde TRCC-Instanzen bleiben unangetastet.
- Das neue Journalereignis überträgt die Zuordnung auch an den unabhängigen
  Abschlusswächter. Damit werden sowohl beim normalen Beenden als auch nach
  einem späteren Absturz keine veralteten Kindprozessdaten verwendet.

## Prüfung

- Regressionstests decken den kontrollierten PID-Wechsel, die Ablehnung eines
  noch laufenden alten Prozesses und die Journalwiedergabe ab.
- Der vollständige Release-Check und die erzeugten Pakete werden vor Übergabe
  erneut geprüft.
