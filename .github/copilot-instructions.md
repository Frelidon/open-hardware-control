# Open Hardware Control – GitHub-Coding-Agenten

Vor Änderungen vollständig `AGENTS.md`, `docs/project/MODULE_REGISTRY.md`, `docs/ai/AI_DEVELOPMENT_GUIDE.md` und `docs/project/RELEASE_BACKUP_POLICY.md` lesen und deren Pflichtreihenfolge befolgen. Das Repository ist die dauerhafte Projektquelle; Chat- oder Agentengedächtnis ist nicht maßgeblich.

- Keine alten Modulkopien oder Backup-Ordner im Repository anlegen.
- Ein fertiger Versionsbau muss über `scripts/build_release.py` zusätzlich in den neben dem Repository liegenden Ordner `Open Hardware Control Backup` gesichert werden.
- Dort müssen stets mindestens die zwei neuesten vollständigen Versionsordner einschließlich Laufzeit-ZIP, Entwicklerpaket, Quellarchiv, Git-Bundle, erzeugten DEB/RPM-Paketen, Release Notes und SHA256-Prüfsummen liegen.
- Die konkrete Aufbewahrungs- und Prüfregel steht in `docs/project/RELEASE_BACKUP_POLICY.md`; sie gilt auch für GitHub Copilot und andere GitHub-Coding-Agenten.
- Vor Abschluss `./scripts/check_release.sh` ausführen und `docs/project/MODULE_REGISTRY.md`, Projektstatus, Changelog und Release Notes passend aktualisieren.
- Push, Tag, Pull Request oder Veröffentlichung nur nach der in `AGENTS.md` verlangten ausdrücklichen Freigabe.
