# Open Hardware Control 3.4.29.47

Wartungsrelease: Das Repository ist jetzt vollständig in Ordner sortiert. Am Programm selbst ändert sich nichts; installierte Struktur und Paketinhalte bleiben identisch.

## Neue Repository-Struktur

| Ort | Inhalt |
|---|---|
| `src/` | Gesamter Anwendungscode: alle Python-Module (Einstieg `kraken_control.py`), `assets/`, `modules/`, `test-gifs/`. Der Ordner spiegelt die flache installierte Programmstruktur. |
| `packaging/` | `install.sh`, `uninstall.sh`, `VERSION`, `BUILD_CHANNEL`, udev-Regel, Polkit-Policy, Metainfo, Desktop-Vorlage, SVG-Icon, Hilfsskripte |
| `docs/` | `INSTALL.md`, `CHANGELOG.md`, `README.en.md` sowie `project/`, `ai/`, `hardware/`, `security/`, `releases/`, `images/` |
| `docs/ai/` | vollständige Agentenanweisungen `AGENTS.md`, `CLAUDE.md`, KI-Arbeitsanleitungen |
| `.github/` | Workflows, Vorlagen, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, `SECURITY.md` |
| `scripts/`, `tests/`, `tools/` | unverändert |
| Wurzelverzeichnis | nur noch `README.md`, `LICENSE`, `CITATION.cff` und ein kurzer `AGENTS.md`-Wegweiser |

## Technische Anpassungen

- `install.sh` erkennt `src/` sowohl im entpackten ZIP (Skript liegt im Paketwurzelordner) als auch im Quellbaum (`packaging/install.sh`).
- `scripts/build_release.py` kopiert Laufzeitdateien aus `src/`, legt `install.sh`, `uninstall.sh` und `SECURITY.md` in die ZIP-Wurzel und installiert weiterhin flach nach `/usr/share/open-hardware-control`.
- `app_constants.helper_script_path` und das SVG-Fallback in `branding.py` finden Hilfsdateien im Quellbaum unter `../packaging/`.
- Tests importieren aus `ROOT / "src"`; Modulregisterprüfung, Release-Prüfung, Cursor-Regel-Globs und GitHub-Workflows verwenden die neuen Pfade.

## Aus 3.4.29.46 enthalten

- Die minütliche OpenRGB-Geräteinventur pausiert, solange OHC im Infobereich verborgen ist und keine RGB-Aktion aussteht.
- Sieben aktuelle Screenshots und kompakte README.

## Pakete

Die Veröffentlichung enthält das universelle ZIP, RPM, DEB, Quellarchiv, vollständige Entwicklerpaket und Local-AI-Git-Bundle. Alle Dateien werden gemeinsam über `SHA256SUMS` geprüft.
