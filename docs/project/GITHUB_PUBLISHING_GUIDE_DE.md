# Open Hardware Control 3.4.29.182 STABLE – GitHub-Veröffentlichung (noch nicht beauftragt)

Aktuelle Entwicklung: 3.4.29.182 INTERN. Kein Tag oder Upload ist beauftragt.
Der folgende Veröffentlichungsnachweis betrifft weiterhin die öffentliche .176.

## Abschluss und Installationsprüfung

Der Eigentümer beauftragt am 11.11.26 ausdrücklich die Veröffentlichung von
`.176`. Die vorherige interne Freigabe für `.175` ist damit um STABLE-Pakete,
normalen Quell-Push, Versionstag und öffentlichen GitHub-Release erweitert.
Die laufende lokale `.176 INTERN`-Installation wird dabei nicht ersetzt.

Repository: <https://github.com/Frelidon/open-hardware-control>

Nach vollständiger lokaler Prüfung und Paket-/Sicherungsverifikation wurde
`34c64d3` ohne Force-Push auf `main` und `publish/v3.4.29.176` übertragen.
Der reguläre Workflow würde erneut prüfen/bauen und anschließend einen
annotierten Tag setzen. Dieser Lauf konnte jedoch die Ubuntu-Paketserver
nicht per DNS auflösen und wurde vor der Veröffentlichung abgebrochen.

Die lokal vollständig geprüften sechs Pakete wurden stattdessen über die
angemeldete GitHub-Release-Oberfläche veröffentlicht. Der dort erzeugte
Versionstag zeigt direkt auf `34c64d3` (Lightweight-Tag). Die Veröffentlichung
ist Latest, kein Entwurf und kein Pre-release. Alle öffentlichen Paket-Digests
sowie die direkt heruntergeladene SHA256SUMS sind abgeglichen. Ein entfernter
CI-Erfolg wird wegen des DNS-Problems ausdrücklich nicht behauptet.

GitHub ersetzt das Leerzeichen im Entwickler-ZIP durch einen Punkt. Die
öffentliche SHA256SUMS verwendet exakt diesen Namen; SHA256SUMS.local erhält
die unveränderte lokale Liste. Die heruntergeladene öffentliche Liste liegt
zusätzlich als SHA256SUMS.github in der geprüften STABLE-Sicherung.
Vor dem Archivupload wurde gesondert geprüft, dass die Bundle-Historie bereits
öffentlich ist und Entwickler-/Quellarchive keine privaten Dateien enthalten.

Veröffentlichungen erfolgen nach erfolgreicher vollständiger Prüfung, sauberem Commit und realem KDE-/Hardwaretest.
Der Eigentümer hat die flüssige RGB-/GPU-Darstellung und den Neustartbetrieb
zuvor bestätigt; .176 wurde lokal gestartet und beide Installationen geprüft.
Der neue lange Stopptest und ein erzwungener Prozessabsturz wurden nicht am
realen PC ausgeführt. Diese Grenzen bleiben in den Release Notes ausdrücklich
sichtbar, ebenso die noch offene reale Fedora-Prüfung.

## Repository und Anmeldung prüfen

Die Anmeldung führt der Benutzer über die GitHub CLI selbst aus:

```bash
gh auth login --web
```

Danach nur lesend prüfen:

```bash
gh auth status
git remote -v
git branch --show-current
git status --short
git diff --check
```

Das erwartete Remote ist `https://github.com/Frelidon/open-hardware-control.git`. Tokens, Passwörter und GitHub-Gerätecodes gehören niemals in Prompts, Projektdateien oder Commits.

## Release lokal prüfen

```bash
./scripts/check_release.sh
./scripts/build_release.sh 3.4.29.176
cd dist
sha256sum -c SHA256SUMS
```

Erwartete Dateien:

- `open_hardware_control_v3_4_29_176.zip`
- `open-hardware-control_3.4.29.176_all.deb`
- `open-hardware-control-3.4.29.176-1.noarch.rpm`
- `open-hardware-control-3.4.29.176-source.tar.gz`
- `Entwicklerpaket.3.4.29.176.zip` (öffentlicher GitHub-Dateiname)
- `Open_Hardware_Control_3.4.29.176_LOCAL_AI.gitbundle`
- `SHA256SUMS`

Der Build muss außerdem die externe Zwei-Versionen-Sicherung aus `RELEASE_BACKUP_POLICY.md` vollständig aktualisieren; beide aufbewahrten Versionen werden in ihren jeweiligen Ordnern erneut mit `sha256sum -c SHA256SUMS` geprüft.

## GitHub veröffentlichen

Nach sauberem Commit wird der geprüfte Stand ohne Force-Push übertragen:

```bash
git push --atomic origin HEAD:refs/heads/main HEAD:refs/heads/publish/v3.4.29.176
```

Der Veröffentlichungszweig löst den vorhandenen Workflow aus. Dieser erstellt
den Tag `v3.4.29.176` erst nach erfolgreicher Prüfung und Paketierung.

Der Workflow `.github/workflows/release.yml` wiederholt die Tests, baut sämtliche Artefakte aus genau diesem Tag und erstellt den öffentlichen Release mit `docs/releases/RELEASE_NOTES_v3.4.29.176.md`.

Kontrolle:

```bash
gh release view v3.4.29.176 --web
```

## Repository-Beschreibung und Topics

Empfohlene Beschreibung:

> Linux hardware control with Thermalright Levita Vision display studio, NZXT Kraken LCD, fan and RGB control, OpenRGB, OpenLinkHub and Wallpaper Engine.

Empfohlene Topics:

`linux`, `thermalright`, `thermalright-levita`, `lcd-display`, `nzxt`, `nzxt-kraken`, `kraken-lcd`, `aio-cooler`, `liquidctl`, `fan-control`, `rgb-control`, `openrgb`, `openlinkhub`, `corsair`, `wallpaper-engine`, `python`, `pyside6`, `fedora`

Die Erlaubnis für den normalen Branch-Push erlaubt niemals automatisch Force-Push, Branch-/Tag-Löschung oder andere destruktive Remote-Aktionen.
