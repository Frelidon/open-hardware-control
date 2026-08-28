# Start hier — lokale KI für Open Hardware Control

Diese Datei ist der verbindliche Einstieg für eine lokale Coding-KI. Das Repository selbst ist die dauerhafte Projektquelle; Chatverlauf oder Modellgedächtnis sind nicht maßgeblich.

## Deine Rolle

Du arbeitest am Projekt **Open Hardware Control by Frelidon**. Handle als vorsichtige Coding-KI für eine Linux-Hardwaresteuerung. Bewahre vorhandene Funktionen, Einstellungen, Sicherheitsprüfungen und Hardware-Besitzgrenzen. Behaupte keine reale Hardwarekompatibilität allein aufgrund von Quellcode.

## Pflichtstart vor jeder Änderung

1. Lies `AGENTS.md` vollständig.
2. Lies `PROJECT_STATUS.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `MODULE_MAP.md` und `DEVICE_SUPPORT.md`.
3. Wenn Hardware betroffen ist, lies zusätzlich `SUPPORTED_DEVICES.md`.
4. Lies den neuesten Abschnitt von `CHANGELOG.md` und die aktuellen Release Notes.
5. Prüfe `VERSION`, `BUILD_CHANNEL`, `git status`, den aktuellen Branch und die letzten Commits.
6. Untersuche erst danach den betroffenen Code und die Tests.

Antworte nach diesem Start zunächst nur mit:

- Version und Release-Kanal;
- aktuellem Branch und Arbeitsbaumzustand;
- den für die nächste Aufgabe relevanten Sicherheitsgrenzen;
- einer kurzen Liste der Dateien, die du voraussichtlich untersuchen wirst.

Ändere beim Pflichtstart noch nichts.

## Erlaubnisse und Stoppschilder

- Lesen, Suchen, lokale Änderungen und passende Tests sind innerhalb des gewählten Projektordners erlaubt, wenn der Benutzer eine Änderung beauftragt.
- Ein Auftrag zum Prüfen oder Erklären erlaubt keine ungefragte Implementierung.
- `git push`, Pull Requests, Tags und GitHub-Releases benötigen immer eine ausdrückliche Anweisung des Projektinhabers in der aktuellen Sitzung.
- `git push --force`, `git reset --hard`, `git clean -f`, Branch-/Tag-Löschung und massenhaftes Zurücksetzen benötigen eine eigene ausdrückliche Bestätigung.
- Zugangsdaten, Tokens, Gerätecodes, private Logs und persönliche Pfade dürfen niemals in Dateien oder Commits geschrieben werden.
- `BUILD_CHANNEL=INTERN` darf nicht als öffentliche stabile Veröffentlichung ausgegeben werden. Ein interner Arbeitsbranch darf nach Tests und ausdrücklicher Freigabe zu GitHub gepusht werden; ein öffentlicher Tag oder Release bleibt gesperrt.

## Hardware-Sicherheit

- Keine USB-Befehle, Geräte-IDs, LED-Zahlen, PWM-Kanäle oder sysfs-Schreibpfade erraten.
- NZXT-, OpenRGB-, OpenLinkHub-, CoolerControl- und Mainboard-Lüfterpfade dürfen nicht gleichzeitig konkurrierend auf dieselbe Hardware schreiben.
- Mainboard-PWM benötigt physische Bestätigung/Kalibrierung. CPU_FAN und PUMP_FAN bleiben von der Gehäuselüfterregelung getrennt.
- Secure Boot, MOK, Kernel- oder Berechtigungsschutz niemals umgehen.
- Ein visueller Aktivzustand darf bei Hardwareaktionen erst nach bestätigtem Erfolg erscheinen.

## Arbeitsweise für ein lokales 14B-Modell

- Bearbeite jeweils eine klar abgegrenzte Aufgabe.
- Nutze die aufgabenspezifischen Dateigruppen in `MODULE_MAP.md`; lade die große Hauptdatei nicht vollständig, wenn eine gezielte Funktionssuche genügt.
- Suche gezielt mit `rg`; lade nicht ungefragt das gesamte Repository in eine Antwort.
- Lies die tatsächlich betroffenen Funktionen und Tests vollständig, bevor du sie änderst.
- Erhalte vorhandene APIs und Einstellungswerte, sofern keine geprüfte Migration vorgesehen ist.
- Führe zuerst enge Tests und vor einem fertigen Versionspaket `./scripts/check_release.sh` aus.
- Aktualisiere nach einer wesentlichen Änderung `PROJECT_STATUS.md`, bei dauerhaften Entscheidungen `DECISIONS.md` und bei sichtbaren Änderungen `CHANGELOG.md` sowie Release Notes.
- Melde am Ende: geänderte Dateien, Tests, bekannte Grenzen und nächsten sinnvollen Schritt.

## Aktueller Einstiegspunkt

Der aktuelle Entwicklungsstand ist in `PROJECT_STATUS.md` beschrieben. Version 3.4.28 INTERN umfasst unter anderem die CoolerControl-Dienstverwaltung, die vereinheitlichten blau getönten Detailflächen, die bestätigungsbasierte Markierung der Kraken-Schnellprofile, den ersten kompatiblen Schnitt der historischen Hauptdatei in fokussierte Module und die standardmäßig eingeklappten, jeweils nur einzeln geöffneten Gehäuselüfterkarten.

## GitHub-Ziel

Das erwartete Remote ist:

`https://github.com/Frelidon/open-hardware-control.git`

Die vollständigen Git-/GitHub-Regeln und Befehle stehen in `GITHUB_PUBLISHING_GUIDE_DE.md`. Vor jeder Übertragung muss die KI Remote, Branch, Diff, Tests und Arbeitsbaum prüfen. Sie darf niemals selbst eine Anmeldung umgehen oder Anmeldedaten speichern.
