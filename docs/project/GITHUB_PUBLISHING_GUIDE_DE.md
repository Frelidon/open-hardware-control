# Open Hardware Control 3.4.29.183 STABLE – GitHub-Veröffentlichung

## Öffentlicher Release .183 abgeschlossen · 15.11.26

Release: <https://github.com/Frelidon/open-hardware-control/releases/tag/v3.4.29.183>

GitHub main und der öffentliche Latest-Release sind .183 STABLE. Der annotierte
Tag v3.4.29.183 zeigt unverändert auf 5f598f5; Release-Lauf 43723430535,
Paketbau, Python-3.14-Prüfung und alle vier CodeQL-Analysen bestanden.
Alle acht öffentlichen Dateien wurden tatsächlich heruntergeladen. Dateigrößen,
GitHub-SHA256 und öffentliche/local-Prüfsummenlisten stimmen. Beide ZIP-CRCs und
vollständigen Manifeste, Quell-TAR-Manifest, DEB-Metadaten/Root-Eigentümer,
RPM-Header-/Payload-/Dateidigests und komplettes Gitbundle geprüft. 474 Python-
Laufzeitquellen und 169 Assets sind in ZIP/TAR/DEB/RPM bytegleich; das Bundle
enthält die Footer-Korrektur und den STABLE-Stand. Dist und STABLE-Sicherung
enthalten exakt die veröffentlichten Paketbytes. Genau INTERN/STABLE .183
bleiben als zwei vollständige Sicherungssätze mit je acht geprüften Hashes.
Der Changelog-Link im öffentlichen Release-Text ist taggebunden korrigiert.

Python 3.13 meldete zweimal allein den 90-Sekunden-Watchdog des großen
Profil-Layouttests, keine fehlgeschlagene fachliche Assertion. Eine isolierte
Python-3.13.18-/Qt-6.12-Reproduktion mit DejaVu Sans und fehlender echter Levita
bestand; der Stack zeigt die wiederholte vollständige Theme-Anwendung.
Der reine Testnachtrag auf main erhält alle Geometrie-/Entwurfsassertionen,
setzt einen weiterhin begrenzten 180-Sekunden-Watchdog und ergänzt Stack-Diagnose
nach 60 Sekunden. Er ändert keine Anwendung, Pakete oder veröffentlichten Tags.
Die gezielte Python-3.13-Prüfung und erneute main-CI werden dazu kontrolliert.

Die laufenden lokalen INTERN-Installationen wurden nicht ersetzt. Fedora-/Boot-/
optische Prüfgrenzen bleiben dokumentiert; kein neuer Hardwarelauf behauptet.
Gebündelte Paketdokumentation ist der Schnappschuss vor diesem Nachweis.

## CI-Nachprüfung der .183-Freigabe · 15.11.26

Der erste Lauf 43721518664 stoppte vor Tag und Upload an den bekannten
Gehäuse-/LCD-Umgebungsregressionen; keine alte Paketversion wurde veröffentlicht.
Die Korrekturen werden erneut vollständig geprüft und neu paketiert. Im Release-
Workflow bleibt Check release die vollständige Freigabesperre. Der unmittelbar
folgende Paketbau nutzt build_release.py direkt, damit derselbe unveränderte
Checkout nicht ein zweites Mal dieselbe Gesamtsuite ausführt. Der allgemeine
build_release.sh-Einstieg behält seine vollständige Vorprüfung unverändert.

## Öffentliche Freigabe .183 · 15.11.26

STABLE-Quellfreigabe: 1.763 Tests und fünf Untertests sowie der komplette
unveränderte check_release.sh-Lauf bestanden. Zuvor gemeldete reine
Dokumentationsfehler (Veröffentlichungstitel und Register-Kanalanker) sind
berichtigt. Keine Prüfung wurde abgeschwächt. Der Release-Workflow benennt das
Entwickler-ZIP vor Upload exakt wie GitHub, prüft SHA256SUMS mit diesen Namen
und erhält SHA256SUMS.local; sein originaler Shellschritt bestand eine isolierte
Sechs-Artefakte-Prüfung. Paketbau und öffentlicher Upload folgen.

Der Eigentümer beauftragt ausdrücklich die vollständige Veröffentlichung auf
GitHub: Hauptbranch main und STABLE-Downloadpakete samt Versionstag.
Der vorige Upload a4d54f9 lag nur auf dem Entwicklungsbranch; main und Latest
waren weiterhin .176. .183 wird jetzt als STABLE neu gebaut und vollständig
geprüft. Aktionsumfang: normaler Fast-forward von main, Tag v3.4.29.183 und
öffentlicher Latest-Release mit sechs Paketen und Prüfsummen. Die laufende
Benutzer-/Systeminstallation bleibt unverändert auf dem geprüften INTERN-Stand.

Nur Kanalmetadaten, genaue Test-Erwartungen und Veröffentlichungsdokumentation
ändern sich gegenüber .183 INTERN. Die Sicherheits- und UI-Tests erwarten
weiterhin den exakten aktuellen Kanal, keine aufgeweichte Alternativprüfung.
Ubuntu-Livenachweise und getrennte Fedora-Vertragstests bleiben maßgeblich;
kein neuer Fedora-/KDE-Hardwarelauf wird aus dem STABLE-Bau abgeleitet.
Historische Abschnitte darunter beschreiben die jeweiligen früheren Aufträge.

Der reguläre Release-Workflow wird über `publish/v3.4.29.183` ausgelöst. Er
prüft und baut erneut, setzt den annotierten Tag erst nach Erfolg und erstellt
den öffentlichen Release. Bereits lokal geprüfte STABLE-Pakete stehen als
Rückfall zur Verfügung, falls die entfernte Buildumgebung scheitert.

Aktuelle Entwicklung: 3.4.29.183 INTERN. Der Eigentümer hat am 14.11.26 den
GitHub-Upload des neuen Standes beauftragt. Ziel ist der Entwicklungsbranch
`codex/hardware-fix-3.4.29.183`; der Upload erfolgt als normaler Quell-Push aus
einem sauberen Commit. Enthalten sind auch die lokal bereits abgeschlossenen
Entwicklungen .177 bis .182, die auf dem öffentlichen .176-Stand aufbauen.
BUILD_CHANNEL bleibt INTERN. Kein Tag, Veröffentlichungsbranch oder öffentlicher
Release wird dadurch erzeugt; die sechs geprüften Pakete bleiben lokal.

Die GitHub-Anbindung dient der Repository-/Ergebniskontrolle. Der lokale Commit
wird mit Git übertragen, damit Commitidentität und vorhandene Historie erhalten
bleiben; die Anbindung bietet keinen lokalen Git-Push. Die vollständige lokale
Testsuite und die Release-Wächter sind bestanden. Für den Quellupload bestanden
weitere 43 betroffene Regressionen sowie Datenschutz- und Registerprüfungen.
Alle 723 Quelldateien entsprechen bytegleich dem bereits geprüften Paketstand.

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

Der veröffentlichte RPM-Container verwendet RPM 6 mit Zstd und indexbasiertem
Payload. Geprüft wurden Header-SHA256/SHA3-256, komprimierte/unverpackte
Payload-SHA256, Dateihashes, Root-Eigentümer und alle Laufzeitbytes. Grundlage:
[offizielle RPM-Formatspezifikation](https://github.com/rpm-software-management/rpm/blob/master/docs/manual/format_v6.md).
