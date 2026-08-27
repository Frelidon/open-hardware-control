# Open Hardware Control 3.4.7 INTERN

Diese interne Korrektur behebt drei im Fedora-44-Hardwaretest eindeutig bestätigte Fehler: OpenRGB-SDK-Protokoll 5 bei den beiden ENE-RAM-Riegeln, den ungültigen liquidctl-Effekt `marquee-4` am NZXT 2023 RGB Controller und einen möglichen zweiten OHC-Prozess.

## RAM und OpenRGB-SDK 5

- Der lokale OHC-Schreiber fordert nun OpenRGB-SDK-Revision 5 an.
- Er bleibt mit Revision 4 kompatibel und verwendet die niedrigere gemeinsam unterstützte Revision.
- Server unter Revision 4 werden vor jedem Farbschreibpaket abgelehnt.
- Loopback-Bindung, kurze Zeitlimits sowie Geräte-, LED-, Farb- und Paketgrenzen bleiben unverändert.
- Regressionstests decken Serverrevision 5, Revision 4 und die Ablehnung von Revision 3 ab.

Damit werden `RAM-Riegel 1` und `RAM-Riegel 2` nicht mehr allein wegen der Antwort „Protokollversion 5“ aus der Aktion entfernt.

## NZXT-2023-Effekte

Das Testprotokoll zeigt für alle drei Kraken-Radiatorlüfter `KeyError('marquee-4')` aus liquidctl 1.16.0. OHC sendet diesen Alias nicht mehr:

- Glut-Komet → `pulse`
- Kreisel → `rainbow-flow`
- Abwechselnd → `alternating-4`

Der ebenfalls nicht bestätigte Alias `moving-alternating-4` wurde aus der NZXT-Auswahl entfernt. Die übrigen Geräte einer gemischten Aktion werden weiterhin unabhängig verarbeitet.

## Genau eine OHC-Instanz

- Noch vor `QApplication`, Fensteraufbau, Backend und Hardwarezugriff wird `application-instance.lock` im privaten XDG-State-Verzeichnis exklusiv gesperrt.
- Die Sperre verwendet Linux `flock`, bleibt bis zum Prozessende geöffnet und wird nicht an Kindprozesse vererbt.
- Ein zweiter Start zeigt die PID der laufenden Instanz und beendet sich ohne OpenRGB-, liquidctl- oder Kraken-Zugriff.
- Kann die Sperre wegen eines unerwarteten Dateisystemfehlers nicht sicher angelegt werden, startet OHC absichtlich nicht.
- Nach einem Absturz gibt der Kernel die Sperre automatisch frei; eine alte PID-Zeile blockiert keinen späteren Start.

## Diagnoseergebnis

Der eingesandte Bericht zeigt OpenRGB als Kindprozess des laufenden OHC-Prozesses und den lokalen Listener auf Port 6742. Ein manuell geöffnetes OpenRGB war bei diesem Fehler daher nicht die Ursache. Derselbe Bericht bestätigt zwei überlappende OHC-Starts; die neue frühe Sperre schließt genau diesen Pfad.

Version 3.4.7 bleibt intern und wird nicht auf GitHub veröffentlicht.
