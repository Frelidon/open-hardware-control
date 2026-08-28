# Open Hardware Control 3.4.27 INTERN – Veröffentlichung derzeit gesperrt

Repository: <https://github.com/Frelidon/kraken-control-linux>

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
gh repo edit Frelidon/kraken-control-linux \
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

## Release lokal prüfen

```bash
./scripts/check_release.sh
sudo apt install rpm
./scripts/build_release.sh 3.4.27
cd dist
sha256sum -c SHA256SUMS
```

Erwartete Dateien:

- `open_hardware_control_v3_4_27_INTERN.zip`
- `open-hardware-control_3.4.27~intern1_all.deb`
- `open-hardware-control-3.4.27-0.intern1.noarch.rpm`
- `open-hardware-control-3.4.27-INTERN-source.tar.gz`
- `Entwicklerpaket 3.4.27 INTERN.zip`
- `SHA256SUMS`

## Spätere Veröffentlichung

Nach einem grünen Pull Request und sauberem `main`:

```bash
git tag -a v3.4.27 -m "Open Hardware Control v3.4.27"
git push origin v3.4.27
```

Der Workflow `.github/workflows/release.yml` darf erst nach der STABLE-Umstellung verwendet werden. Er führt die Tests erneut aus, baut sämtliche Release-Dateien aus demselben Tag und erstellt anschließend das öffentliche GitHub-Release.

Kontrolle:

```bash
gh release view v3.4.27 --web
```

## Sicherheitsprüfung vor GitHub

Vor einem Push müssen der beabsichtigte Stand vollständig committed, der Arbeitsbaum sauber und die relevanten Tests erfolgreich sein. Öffentliche Tags und Releases benötigen zusätzlich `BUILD_CHANNEL=STABLE` und eine ausdrückliche Freigabe des Projektinhabers. Eine Google-Drive- oder andere externe Backup-Pflicht besteht nicht.
