# Lokale Release-Sicherungen

Jeder erfolgreiche Versionsbau wird zusätzlich außerhalb des Git-Arbeitsbaums gesichert. Der feste Standardordner liegt direkt neben dem Repository:

```text
Open-Hardware-Control/
├── open-hardware-control-git/
└── Open Hardware Control Backup/
    ├── Version x.y.z.n INTERN/
    └── Version x.y.z.n INTERN/
```

## Verbindlicher Inhalt

Jeder Versionsordner enthält mindestens:

- universelles Laufzeit-ZIP;
- vollständiges Entwicklerpaket mit sämtlichen Projektdateien;
- Quellcode-Archiv und Local-AI-Git-Bundle;
- tatsächlich erzeugte RPM- und DEB-Pakete;
- Release Notes, `BACKUP_INFO.txt` und eine frisch berechnete `SHA256SUMS`.

Ein nicht erzeugtes Paketformat wird nicht erfunden. Bei einer Veröffentlichung müssen alle dafür erzeugten Pakete, insbesondere das DEB-Paket, mitgesichert werden.

## Automatik und Aufbewahrung

`scripts/build_release.py` ruft nach einem vollständig erfolgreichen Paketbau `scripts/backup_release.py` auf. Die Sicherung wird zuerst in einem temporären Ordner aufgebaut und erst danach als vollständiger Versionsordner eingesetzt. Anschließend bleiben mindestens die zwei neuesten, semantisch sortierten Versionen erhalten.

Die Bereinigung darf ausschließlich Ordner mit dem exakten Schema `Version <Version> INTERN` oder `Version <Version> STABLE` entfernen. Fremde Dateien und Ordner bleiben unangetastet. Der Backup-Ordner darf niemals innerhalb des Repositorys oder eines Moduls liegen, damit Archive nicht rekursiv wachsen.

Die Sicherung ersetzt weder Git-Historie noch Tags und ist keine Freigabe oder Voraussetzung für einen GitHub-Push. Der frühere Google-Drive-/Cloud-Backup-Ablauf bleibt entfernt.

## Manuelle Wiederholung

Falls die Pakete bereits in `dist/` liegen, kann die Sicherung wiederholt werden:

```bash
python3 scripts/backup_release.py "$(cat VERSION)" "$(cat BUILD_CHANNEL)" --project-root . --dist dist
```

Nach jedem Versionsbau muss geprüft werden, dass der neue Versionsordner und sein Vorgänger vorhanden sind und `sha256sum -c SHA256SUMS` in beiden Ordnern erfolgreich ist.
