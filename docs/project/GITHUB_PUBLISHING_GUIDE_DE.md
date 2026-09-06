# Open Hardware Control 3.4.29.47 STABLE – GitHub-Veröffentlichung

Repository: <https://github.com/Frelidon/open-hardware-control>

Dieser Stand ist mit `BUILD_CHANNEL=STABLE` für eine öffentliche Veröffentlichung vorbereitet. Ein Push, Tag oder GitHub-Release erfolgt ausschließlich nach einem ausdrücklichen Auftrag des Projektinhabers, erfolgreicher vollständiger Prüfung, sauberem Commit und realem KDE-/Hardwaretest.

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
./scripts/build_release.sh 3.4.29.47
cd dist
sha256sum -c SHA256SUMS
```

Erwartete Dateien:

- `open_hardware_control_v3_4_29_47.zip`
- `open-hardware-control_3.4.29.47_all.deb`
- `open-hardware-control-3.4.29.47-1.noarch.rpm`
- `open-hardware-control-3.4.29.47-source.tar.gz`
- `Entwicklerpaket 3.4.29.47.zip`
- `Open_Hardware_Control_3.4.29.47_LOCAL_AI.gitbundle`
- `SHA256SUMS`

Der Build muss außerdem die externe Zwei-Versionen-Sicherung aus `RELEASE_BACKUP_POLICY.md` vollständig aktualisieren; beide aufbewahrten Versionen werden in ihren jeweiligen Ordnern erneut mit `sha256sum -c SHA256SUMS` geprüft.

## GitHub veröffentlichen

Nach sauberem Commit wird der geprüfte Stand zuerst ohne Force-Push auf `main` übertragen. Anschließend erzeugt der ausdrücklich freigegebene Tag den öffentlichen GitHub-Release-Workflow:

```bash
git push origin main
git tag -a v3.4.29.47 -m "Open Hardware Control v3.4.29.47"
git push origin v3.4.29.47
```

Der Workflow `.github/workflows/release.yml` wiederholt die Tests, baut sämtliche Artefakte aus genau diesem Tag und erstellt den öffentlichen Release mit `docs/releases/RELEASE_NOTES_v3.4.29.47.md`.

Kontrolle:

```bash
gh release view v3.4.29.47 --web
```

## Repository-Beschreibung und Topics

Empfohlene Beschreibung:

> Linux hardware control with Thermalright Levita Vision display studio, NZXT Kraken LCD, fan and RGB control, OpenRGB, OpenLinkHub and Wallpaper Engine.

Empfohlene Topics:

`linux`, `thermalright`, `thermalright-levita`, `lcd-display`, `nzxt`, `nzxt-kraken`, `kraken-lcd`, `aio-cooler`, `liquidctl`, `fan-control`, `rgb-control`, `openrgb`, `openlinkhub`, `corsair`, `wallpaper-engine`, `python`, `pyside6`, `fedora`

Die Erlaubnis für den normalen Branch-Push erlaubt niemals automatisch Force-Push, Branch-/Tag-Löschung oder andere destruktive Remote-Aktionen.
