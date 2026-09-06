# Open Hardware Control 3.4.29.48

Wartungsrelease: Die in 3.4.29.47 eingeführte Ordnerstruktur wird zur dauerhaften Projektregel für alle Coding-KIs, und der GitHub-Release-Workflow ist an die neuen Pfade angepasst. Am Programm selbst ändert sich nichts.

## Verbindliche Ablage- und README-Regel

- `docs/ai/AGENTS.md` enthält den Pflichtabschnitt „Repository layout and README“: eine Tabelle, welche Datei in welchen Ordner gehört (`src/`, `packaging/`, `docs/<thema>/`, `.github/`), die Regel, dass im Wurzelverzeichnis keine neuen Dateien entstehen dürfen, und die README-Regeln (feste Abschnittsreihenfolge, unter 200 Zeilen, genau ein „Neu in“-Abschnitt, höchstens vier Verlaufsversionen; alles Ältere in `docs/CHANGELOG.md` und `docs/releases/`).
- Gespiegelt in `.cursor/rules/70-repository-layout.mdc`, `.github/copilot-instructions.md`, `docs/ai/CLAUDE.md`, dem Root-Wegweiser `AGENTS.md` und als Eigentümerentscheidung in `docs/project/DECISIONS.md`.
- `tests/test_repository_layout_342947.py` erzwingt Root-Allowlist, README-Länge und Verlaufslänge in `check_release.sh` und der CI.

## Korrekturen

- Der Release-Workflow liest `packaging/VERSION` und `packaging/BUILD_CHANNEL`; der Lauf für den Tag `v3.4.29.47` war daran gescheitert, dieser Tag bleibt ohne veröffentlichtes Release.
- Cursor-Regel-Globs zeigen auf `src/`.

## Enthalten aus 3.4.29.47 und 3.4.29.46

- Gesamter Anwendungscode in `src/`, Installer und Versionsdateien in `packaging/`, alle Dokumente in `docs/`; installierte Struktur unverändert.
- Die minütliche OpenRGB-Geräteinventur pausiert, solange OHC im Infobereich verborgen ist und keine RGB-Aktion aussteht.

## Pakete

Die Veröffentlichung enthält das universelle ZIP, RPM, DEB, Quellarchiv, vollständige Entwicklerpaket und Local-AI-Git-Bundle. Alle Dateien werden gemeinsam über `SHA256SUMS` geprüft.
