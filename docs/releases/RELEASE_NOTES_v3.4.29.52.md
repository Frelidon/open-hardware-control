# Open Hardware Control 3.4.29.52 INTERN

Datum: 08.09.2026
Kanal: INTERN
Veröffentlichung: kein GitHub-Push, Tag oder öffentliches Release

## Ein Sprachmodul, vier klare Dateien

- Die komplette Lokalisierung liegt im aktuellen Modul `src/modules/localization/v1_0/`.
- `de.py`, `en.py`, `es.py` und `fr.py` enthalten jeweils den vollständigen Bestand ihrer Sprache: Oberfläche, Einrichtungsassistent und integrierte Hilfethemen.
- Deutsch bleibt die kanonische Quelle. Alle vier Dateien verwenden dieselben stabilen Nachrichten-IDs; neue Texte erhalten eine neue ID, geänderte Texte behalten ihre ID.
- `catalog.py` bricht beim Import mit einer klaren Fehlermeldung ab, wenn deutsche Quellen doppelt vorkommen oder einer Sprachdatei IDs fehlen beziehungsweise zusätzliche IDs enthält.

## Kompatibilität und Paketierung

- `src/localization_catalog.py` ist nur noch eine kleine Fassade und exportiert weiterhin `UI_TRANSLATIONS`, `SETUP_TRANSLATIONS`, `HELP_TOPICS` sowie die vorhandenen Hilfsfunktionen.
- Installer, Runtime-ZIP und RPM übernehmen das Sprachmodul über den bereits bestehenden `src/modules/`-Paketpfad.
- Die bisherigen Root-Dateien `localization_controls.py`, `localization_cards.py`, `localization_labels.py` und `localization_policy.py` wurden durch das neue Modul ersetzt.

## Dauerhafte Regel und Tests

- Jede sichtbare UI-Änderung muss dieselbe Nachrichten-ID in allen vier Sprachdateien aktualisieren.
- Der Offscreen-Test prüft vier vorhandene Sprachmodule, identische ID-Mengen, eindeutige deutsche Quellen, vollständige interaktive Abdeckung und den echten Live-Sprachwechsel.
- Technische Kennungen, gemessene Werte und Eigennamen bleiben die einzigen zulässigen Übersetzungsausnahmen.
- Hardware-Schreibpfade und Sicherheitsgrenzen wurden nicht verändert.
