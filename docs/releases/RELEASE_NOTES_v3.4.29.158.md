# Open Hardware Control 3.4.29.158 INTERN

Diese interne Wartungsversion behebt zwei im Besitzerlog von 3.4.29.157
reproduzierbar sichtbare Laufzeitfehler. Hardwarezuordnungen, LED-Zahlen,
Profile, Berechtigungen und Schreibbesitz bleiben unverändert.

## OpenRGB SDK 6

- Paket 157 ist die dokumentierte asynchrone OpenRGB-Meldung
  `PROFILEMANAGER_ACTIVE_PROFILE_CHANGED`. OHC validiert und verbraucht ihren
  nullterminierten Profilnamen nun, bevor es auf die Bestätigung des eigenen
  RGB-Schreibvorgangs wartet.
- Die Meldung unterbricht dadurch keine MSI-Mystic-Light-Frames mehr und wird
  nicht mehr fälschlich als Antwort statt ACK 10 gezählt.
- Unbekannte, abgeschnittene oder nicht nullterminierte Pakete bleiben Fehler;
  Inventarwechsel stoppen weiterhin die gecachte Sitzung fail-closed.

## Thermalright Levita / GPU-Takt

- Der bekannte TRCC-9.9.11-Grenzfall bei `freq1_input=1000000 Hz` bleibt
  read-only korrekt zu 1 MHz normalisiert.
- Nach einer Grenzwertkorrektur muss die AMD-GPU-Taktquelle jetzt drei
  aufeinanderfolgende gültige 5-Sekunden-Messungen liefern, bevor OHC zur
  dynamischen TRCC-Liveanzeige zurückschaltet. Kurze Idle-Übergänge erzeugen
  dadurch kein wiederholtes Korrektur-/Wiederherstellungs-Pingpong mehr.
- Fehlende oder fehlerhafte Messungen gelten ausdrücklich nicht als Erholung.

## Grenzen

- Die Tests simulieren das OpenRGB-Protokoll und die Sensormessungen ohne
  Hardwarezugriff. Optische RGB-Ausgabe und reale Fedora-Hardware bleiben
  getrennte Eigentümerprüfungen.
- Kanal: **INTERN**. Kein öffentlicher Tag oder GitHub-Release ist durch den
  Versionsbau allein freigegeben.
