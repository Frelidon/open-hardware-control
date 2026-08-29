# Open Hardware Control 3.4.29.4 INTERN – Veröffentlichung derzeit gesperrt

Repository: <https://github.com/Frelidon/open-hardware-control>

Diese interne Testversion darf noch nicht öffentlich veröffentlicht werden. `BUILD_CHANNEL=INTERN` sorgt dafür,
dass `scripts/create_release.sh` und `scripts/publish_github.sh` abbrechen. Erst nach realem KDE-/Hardwaretest,
der Umstellung auf `BUILD_CHANNEL=STABLE` und einer erneuten vollständigen Paketprüfung werden Branch, Pull Request,
Tag und GitHub-Release erstellt. Die folgenden Suchbegriffe bleiben für die spätere öffentliche Version vorgemerkt.

## Suchbeschreibung und Topics

Empfohlene Repository-Beschreibung:

> Open-source NZXT Kraken LCD, pump, fan and RGB control for Linux with Corsair/OpenLinkHub and local OpenRGB SDK integration.

Empfohlene GitHub-Topics:

`linux`, `nzxt`, `nzxt-kraken`, `kraken`, `kraken-lcd`, `aio-cooler`, `liquidctl`, `fan-control`, `rgb-control`, `openrgb`, `lcd-display`, `hardware-control`, `openlinkhub`, `corsair`, `python`, `pyside6`, `fedora`

Mit angemeldeter GitHub CLI:

```bash
gh repo edit Frelidon/open-hardware-control \
  --description "Open-source NZXT Kraken LCD, pump, fan and RGB control for Linux with Corsair/OpenLinkHub integration." \
  --add-topic linux \
  --add-topic nzxt \
  --add-topic nzxt-kraken \
  --add-topic kraken \
  --add-topic kraken-lcd \
  --add-topic aio-cooler \
  --add-topic liquidctl \
  --add-topic fan-control \
  --add-topic lcd-display \
  --add-topic hardware-control \
  --add-topic openlinkhub \
  --add-topic corsair \
  --add-topic python \
  --add-topic pyside6 \
  --add-topic fedora
```

## Internen Arbeitsstand sicher hochladen

Ein interner Entwicklungsbranch darf gesichert oder als Pull Request bereitgestellt werden, wenn der Projektinhaber dies ausdrücklich beauftragt. Das ist noch keine öffentliche Veröffentlichung.

Einmalige Anmeldung führt der Benutzer selbst aus:

```bash
gh auth login --web
```

Danach prüft die lokale KI zunächst nur lesend:

```bash
gh auth status
git remote -v
git branch --show-current
git status --short
git diff --check
```

Das erwartete Remote ist `https://github.com/Frelidon/open-hardware-control.git`. Vor dem Push müssen die beabsichtigten Änderungen committed, die passenden Tests erfolgreich und der Arbeitsbaum sauber sein. Erst nach der ausdrücklichen Freigabe des Projektinhabers:

```bash
git push -u origin "$(git branch --show-current)"
```

Optional darf danach ebenfalls nur auf ausdrücklichen Auftrag ein Pull Request erstellt werden:

```bash
gh pr create --fill
```

Tokens, Passwörter und GitHub-Gerätecodes gehören niemals in Prompts, Projektdateien oder Commits. Force-Push, Branchlöschung, Tags und Releases sind eigene, gesondert freizugebende Aktionen.

## Release lokal prüfen

```bash
./scripts/check_release.sh
sudo apt install rpm
./scripts/build_release.sh 3.4.29.4
cd dist
sha256sum -c SHA256SUMS
```

Erwartete Dateien:

- `open_hardware_control_v3_4_28_INTERN.zip`
- `open-hardware-control_3.4.29.4~intern2_all.deb`
- `open-hardware-control-3.4.29.4-0.intern2.noarch.rpm`
- `open-hardware-control-3.4.29.4-INTERN-source.tar.gz`
- `Entwicklerpaket 3.4.29.4 INTERN.zip`
- `Open_Hardware_Control_3.4.29.4_INTERN_LOCAL_AI.gitbundle`
- `SHA256SUMS`

## Spätere Veröffentlichung

Nach einem grünen Pull Request und sauberem `main`:

```bash
git tag -a v3.4.29.4 -m "Open Hardware Control v3.4.29.4"
git push origin v3.4.29.4
```

Der Workflow `.github/workflows/release.yml` darf erst nach der STABLE-Umstellung verwendet werden. Er führt die Tests erneut aus, baut sämtliche Release-Dateien aus demselben Tag und erstellt anschließend das öffentliche GitHub-Release.

Kontrolle:

```bash
gh release view v3.4.29.4 --web
```

## Sicherheitsprüfung vor GitHub

Vor einem Push müssen der beabsichtigte Stand vollständig committed, der Arbeitsbaum sauber und die relevanten Tests erfolgreich sein. Öffentliche Tags und Releases benötigen zusätzlich `BUILD_CHANNEL=STABLE` und eine ausdrückliche Freigabe des Projektinhabers. Eine Google-Drive- oder andere externe Backup-Pflicht besteht nicht.
