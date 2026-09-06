# Open Hardware Control 3.4.29.46

Wartungsrelease der stabilen 3.4.29-Reihe: kein OpenRGB-Prozess-Spam mehr im Hintergrund, aufgeräumtes Repository und eine neue, kompakte README mit aktuellen Screenshots.

## Fehlerkorrektur

- Die minütliche RGB-Geräteinventur startete `openrgb --client 127.0.0.1:6742 --list-devices` auch dann, wenn Open Hardware Control nur im Infobereich lief. Der Hintergrundscan pausiert jetzt, solange das Hauptfenster verborgen ist und weder ein gespeichertes RGB-Startprofil noch eine Schreibfreigabe oder eine bereits geplante Wiederholung ausstehen. Sobald das Fenster geöffnet wird oder eine RGB-Aktion anliegt, läuft die Inventur wie bisher.
- Regressionstest: `tests/test_rgb_inventory_tray_guard_342946.py`.

## Repository-Struktur

| Neuer Ort | Inhalt |
|---|---|
| `docs/project/` | Architektur, Entscheidungen, Projektstatus, Roadmap, Modulregister, Komponenten-/Funktionsversionen, Projektdokumentationen, Release-Backup-Richtlinie, Veröffentlichungsleitfaden |
| `docs/ai/` | KI-Arbeitsanleitungen, Cursor-/LM-Studio-Einrichtung, lokaler KI-Startprompt |
| `docs/hardware/` | Gerätelisten, Profile, CPU-Profile, RGB-Studio, OpenLinkHub-Anbindung, USB-Mitschnittauswertung, Desktop-Designs, animierte Hintergründe |
| `docs/security/` | Sicherheitsaudits, Datenschutz, `SECURITY_SCAN_REPORT.json` |
| `docs/releases/` | alle `RELEASE_NOTES_v*.md`, Release-Checkliste |
| `packaging/` | udev-Regel, Polkit-Policy, Metainfo, Desktop-Vorlage, SVG-Icon, `install-dependencies.sh`, `install-fan-helper.sh`, `install-udev-rule.sh`, `collect-diagnostics.sh` |
| `.github/` | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md` |

Die installierte Programmstruktur unter `~/.local/share/open-hardware-control` beziehungsweise `/usr/share/open-hardware-control` bleibt flach und unverändert. `install.sh`, RPM und DEB kopieren aus den neuen Quellpfaden; `app_constants.helper_script_path` findet die Hilfsskripte in beiden Layouts.

## README

- Anklickbare Galerie mit sieben aktuellen Screenshots in der Reihenfolge der Seitenleiste.
- Installation, Sicherheit, Dokumentation und Status stehen direkt nach dem Levita-Highlight.
- Versionshistorie nur noch für die letzten vier Versionen; ältere Stände in `CHANGELOG.md` und `docs/releases/`.

## Sicherheit und Besitzgrenzen

Unverändert: OpenRGB, OpenLinkHub, NZXT, Mainboard-PWM und TRCC bleiben getrennte, koordinierte Besitzerpfade; Hardware-Schreibzugriffe bleiben bestätigungs-, konflikt- und testmodusgeschützt.

## Pakete

Die Veröffentlichung enthält das universelle ZIP, RPM, DEB, Quellarchiv, vollständige Entwicklerpaket und Local-AI-Git-Bundle. Alle Dateien werden gemeinsam über `SHA256SUMS` geprüft.
