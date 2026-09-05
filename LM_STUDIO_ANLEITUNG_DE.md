# LM Studio mit Qwen2.5-Coder-14B für dieses Projekt

Diese Anleitung beschreibt die sichere Übergabe des vollständigen Open-Hardware-Control-Projekts an `qwen2.5-coder-14b-instruct` in LM Studio.

## Empfohlene Variante: Bionic-Projekt mit direktem Ordnerzugriff

1. Verwende auf diesem Rechner am einfachsten direkt den vorhandenen Git-Repository-Ordner. Für eine Übertragung auf einen anderen Rechner oder in einen neuen Ordner verwende das mitgelieferte `Open_Hardware_Control_3.4.29.45_LOCAL_AI.gitbundle` wie im nächsten Abschnitt beschrieben. Das Entwickler-ZIP ist eine vollständige Quelldatei-Sicherung, enthält aber absichtlich keinen `.git`-Ordner.
2. Öffne LM Studio und erstelle ein neues **Project**.
3. Aktiviere **Allow coding / Coding erlauben**.
4. Wähle über **Choose a folder** genau den Ordner, in dem `AGENTS.md`, `START_HIER_LOKALE_KI.md`, `kraken_control.py` und `.git` liegen. Wähle nicht nur `dist` und nicht einen übergeordneten Sammelordner.
5. Wähle `qwen2.5-coder-14b-instruct` als Modell.
6. Beginne konservativ mit etwa **16.384 Kontext-Tokens**. Wenn genügend RAM/VRAM frei bleibt, kannst du auf 32.768 erhöhen. Die ungefähr 12 GB große Modelldatei ist nicht dasselbe wie die Kontextgröße; ein längerer Kontext benötigt zusätzlichen Speicher.
7. Stelle GPU Offload auf **Auto**. Wenn LM Studio Speicherfehler meldet, senke zuerst die Kontextlänge, bevor du das Projekt oder Dateien entfernst.
8. Öffne `LOCAL_AI_STARTPROMPT.txt`, kopiere den Inhalt in die erste Sitzung und sende ihn unverändert ab.
9. Prüfe die von der KI gemeldete Version, den Branch und den Arbeitsbaum, bevor du ihr eine Änderungsaufgabe gibst.

LM Studio beschreibt dieses Vorgehen offiziell so: Ein Bionic-Projekt mit aktiviertem Coding darf den ausgewählten Codeordner durchsuchen, bearbeiten, Git verwenden und Shell-Befehle ausführen. Dateien und Ordner können außerdem als Projektmaterial angehängt werden: <https://lmstudio.ai/docs/bionic/quick-start>

## Portables Projekt mit vollständigem Git-Verlauf einrichten

Das lokale-KI-Git-Bundle enthält den aktuellen Branch und seine vollständige benötigte Historie, jedoch keine Passwörter oder Tokens. Ersetze den ersten Pfad durch den tatsächlichen Downloadpfad:

```bash
git clone --branch codex/3.4.29-intern \
  /vollstaendiger/pfad/Open_Hardware_Control_3.4.29.45_LOCAL_AI.gitbundle \
  open-hardware-control-local-ai
cd open-hardware-control-local-ai
git remote set-url origin https://github.com/Frelidon/open-hardware-control.git
git remote -v
```

Wähle anschließend `open-hardware-control-local-ai` als LM-Studio-Projektordner. So kann die Coding-KI lokal suchen, ändern, testen und committen. Ein Push bleibt trotzdem bis zu deiner ausdrücklichen Freigabe verboten.

## Falls das Modell als einzelne GGUF-Datei vorliegt

LM Studio muss einmal gestartet worden sein. Danach kannst du im Terminal prüfen:

```bash
lms --help
lms ls
```

Eine vorhandene GGUF-Datei lässt sich unter Beibehaltung des Originals importieren:

```bash
lms import /vollstaendiger/pfad/qwen2.5-coder-14b-instruct.gguf --copy
```

Danach erscheint sie unter **My Models**. Die offizielle Importanleitung erklärt auch Dry-Run, Hardlink und Symlink: <https://lmstudio.ai/docs/cli/local-models/import>

## Normaler Chat ohne Coding-Zugriff

Ein normaler LM-Studio-Chat kann angehängte Dokumente lesen, besitzt aber nicht automatisch Shell-, Git- oder vollständigen Ordnerzugriff. Für reine Fragen kannst du `START_HIER_LOKALE_KI.md` und einzelne relevante Dateien hineinziehen. Für Entwicklung, Tests, Commits und GitHub ist das Bionic-Projekt mit Coding-Zugriff die passende Variante.

## GitHub einmalig für den Benutzer anmelden

Die KI bekommt niemals ein GitHub-Passwort oder Token in ihren Prompt. Öffne selbst ein Terminal im Projektordner und prüfe:

```bash
gh auth status
git remote -v
```

Falls GitHub CLI noch nicht angemeldet ist:

```bash
gh auth login --web
```

Schließe die Anmeldung selbst im Browser ab. Danach darf die KI `gh auth status` prüfen. Das erwartete Remote ist `https://github.com/Frelidon/open-hardware-control.git`.

## So beauftragst du Änderungen

Gib pro Sitzung eine kleine, überprüfbare Aufgabe, zum Beispiel:

> Lies zuerst START_HIER_LOKALE_KI.md und führe den Pflichtstart aus. Untersuche danach nur die standardmäßig aufgeklappten Gehäuselüfterkarten. Erkläre zunächst Ursache und betroffene Tests; ändere noch nichts.

Nach der Diagnose:

> Implementiere die beschriebene Einzelkarten-Aufklappung, bewahre Hardware-Sicherheitsgrenzen, ergänze Regressionstests und aktualisiere die Projektunterlagen. Nicht pushen.

Vor GitHub:

> Prüfe Diff, Tests, Datenschutz, Branch und Arbeitsbaum. Zeige mir exakt, was auf `origin` gepusht würde. Noch nicht pushen.

Erst wenn das Ergebnis stimmt:

> Du darfst jetzt den geprüften Commit auf den aktuellen internen Branch zu `origin` pushen. Keinen Tag und kein GitHub-Release erstellen.

## Lokaler LM-Studio-Server ist optional

Für das Bionic-Projekt ist kein eigener API-Aufbau nötig. Falls später ein anderes Coding-Programm das lokale Modell verwenden soll, kann der LM-Studio-Server im Developer-Bereich oder per `lms server start --port 1234` gestartet werden. Standardmäßig sollte er nur an `127.0.0.1` gebunden bleiben. Offizielle Dokumentation: <https://lmstudio.ai/docs/developer/core/server> und <https://lmstudio.ai/docs/cli/serve/server-start>.

## Wichtige Grenzen

- Qwen2.5-Coder-14B kann gut programmieren, ersetzt aber keine reale Hardwareprüfung.
- Nie mehrere große Aufgaben in einen einzigen Prompt packen.
- Vor jedem Push den Diff selbst ansehen.
- Interne Builds dürfen als Arbeitsbranch gesichert werden, aber `BUILD_CHANNEL=INTERN` sperrt öffentliche Tags/Releases.
- Wenn die KI behauptet, sie habe getestet, müssen die tatsächlichen Terminalausgaben sichtbar sein.
