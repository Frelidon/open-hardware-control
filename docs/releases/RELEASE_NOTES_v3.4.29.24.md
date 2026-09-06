# Open Hardware Control 3.4.29.24 INTERN

**Datum:** 02.09.26

Diese Version integriert die fachlich geprüften Korrekturen der internen Zwischenstände 3.4.29.22 und 3.4.29.23 in den vollständigen Repository-Stand. Übernommen wurden der fehlertolerante Layoutimport, die symlink-sichere TRCC-Theme-Erkennung, der sichere Split-Modus-Standard, die bestätigte Livestream-Startmeldung mit begrenztem Autostart-Retry sowie das vollständige Shutdown der Hover-Vorschau.

Das Levita-Fachmodul steigt wegen des geänderten Layoutimportvertrags auf 1.2 und liegt ausschließlich unter `modules/lcd_levita/v1_2/`. Die sichere Split-Einstellungsrichtlinie liegt separat in `runtime_policy.py`.

Die Paketrollen sind jetzt maschinell abgesichert: Das Installations-ZIP bleibt absichtlich ohne `tests/` und `scripts/`; das Entwicklerpaket muss dagegen alle Repository-Tests, Release-Skripte, GitHub-Workflows und Werkzeuge enthalten. Der Build bricht bei einer unvollständigen Entwicklerausgabe ab.

Das Local-AI-Gitbundle wird aus einem temporären Snapshot-Commit exakt dieses validierten Entwicklerbaums erzeugt. Dadurch kann ein noch nicht committed Arbeitsstand kein veraltetes Bundle unter dem neuen Versionsnamen mehr erzeugen; das eigentliche Arbeits-Repository bleibt unverändert.

Es wurden keine USB-Protokolle, Gerätekennungen, PWM-Zuordnungen oder Hardwaregrenzen verändert. Auswahl, Vorschau und Tests autorisieren keinen Hardwarezugriff.
