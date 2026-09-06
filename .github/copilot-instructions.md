# Open Hardware Control – GitHub-Coding-Agenten

Vor Änderungen vollständig `docs/ai/AGENTS.md`, `docs/project/MODULE_REGISTRY.md`, `docs/ai/AI_DEVELOPMENT_GUIDE.md` und `docs/project/RELEASE_BACKUP_POLICY.md` lesen und deren Pflichtreihenfolge befolgen. Das Repository ist die dauerhafte Projektquelle; Chat- oder Agentengedächtnis ist nicht maßgeblich.

- Keine alten Modulkopien oder Backup-Ordner im Repository anlegen.
- Ein fertiger Versionsbau muss über `scripts/build_release.py` zusätzlich in den neben dem Repository liegenden Ordner `Open Hardware Control Backup` gesichert werden.
- Dort müssen stets mindestens die zwei neuesten vollständigen Versionsordner einschließlich Laufzeit-ZIP, Entwicklerpaket, Quellarchiv, Git-Bundle, erzeugten DEB/RPM-Paketen, Release Notes und SHA256-Prüfsummen liegen.
- Die konkrete Aufbewahrungs- und Prüfregel steht in `docs/project/RELEASE_BACKUP_POLICY.md`; sie gilt auch für GitHub Copilot und andere GitHub-Coding-Agenten.
- Vor Abschluss `./scripts/check_release.sh` ausführen und `docs/project/MODULE_REGISTRY.md`, Projektstatus, Changelog und Release Notes passend aktualisieren.
- Push, Tag, Pull Request oder Veröffentlichung nur nach der in `docs/ai/AGENTS.md` verlangten ausdrücklichen Freigabe.

## Feste Ablage (Wurzelverzeichnis bleibt leer)

- Im Wurzelverzeichnis dürfen nur `README.md`, `LICENSE`, `CITATION.cff`, der kurze `AGENTS.md`-Wegweiser und Dotfiles liegen. Niemals neue Dateien oder Ordner dort anlegen.
- Anwendungscode → `src/` (Fachmodule → `src/modules/<name>/v<major>_<minor>/`); Installer, `VERSION`, `BUILD_CHANNEL`, Distributionsdateien → `packaging/`; Dokumente → passender `docs/`-Unterordner (`project`, `ai`, `hardware`, `security`, `releases`, `images`), `INSTALL.md`/`CHANGELOG.md`/`README.en.md` direkt in `docs/`; Community-/Sicherheitsrichtlinien → `.github/`.
- `README.md` und `docs/README.en.md` bleiben unter 200 Zeilen: feste Abschnittsreihenfolge, genau ein „Neu in“-Abschnitt (pro Release ersetzen, nicht stapeln), Versionsverlauf mit höchstens den vier neuesten Versionen. Ausführliche Änderungstexte gehören in `docs/CHANGELOG.md` und `docs/releases/RELEASE_NOTES_v<version>.md`.
- Vollständige Tabelle in `docs/ai/AGENTS.md`; `tests/test_repository_layout_342947.py` erzwingt die Regeln und darf nicht abgeschwächt werden.
