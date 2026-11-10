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

`scripts/build_release.py` ruft nach einem vollständig erfolgreichen Paketbau `scripts/backup_release.py` auf. Die Sicherung wird zuerst in einem temporären Ordner aufgebaut und erst danach als vollständiger Versionsordner eingesetzt. Anschließend bleiben mindestens die zwei neuesten vollständigen, semantisch sortierten Versionen erhalten; die normale Rotation behält genau zwei. Niemals weniger als zwei bereits vorhandene vollständige Sicherungen.

**Dauerhafte Eigentümerfreigabe vom 13.09.26:** Bei angefordertem lokalem Versionsbau dürfen ältere erkannte Release-Sicherungen automatisch ohne erneute Rückfrage entfernt werden, sobald die neue vollständige Sicherung erstellt ist und die zwei neuesten Versionen erhalten bleiben. Diese eng begrenzte Freigabe gilt nur für die normale Rotation im festgelegten externen Sicherungsordner, nicht für beliebige Dateien, Profile, Quelldaten, Git-Historie oder andere Sicherungen. Bei unvollständigen/unsicheren Zielen oder wenn weniger als zwei vollständige Versionen verbleiben würden: nicht löschen, Ursache melden.

Die Bereinigung darf ausschließlich Ordner mit dem exakten Schema `Version <Version> INTERN` oder `Version <Version> STABLE` entfernen. Fremde Dateien und Ordner bleiben unangetastet. Der Backup-Ordner darf niemals innerhalb des Repositorys oder eines Moduls liegen, damit Archive nicht rekursiv wachsen.

Die Sicherung ersetzt weder Git-Historie noch Tags und ist keine Freigabe oder Voraussetzung für einen GitHub-Push. Der frühere Google-Drive-/Cloud-Backup-Ablauf bleibt entfernt.

## Zusätzlicher Funktionsstand · 10.11.26

Auf ausdrücklichen Eigentümerwunsch wird `.169` zusätzlich in einem eigenen,
nicht von der Zwei-Versionen-Rotation erfassten lokalen Ordner gesichert.
Der öffentliche Release-Satz enthält keine persönlichen Daten. Die private
Funktionssicherung enthält außerdem den vollständigen Arbeitsbaum mit Git,
die installierte Anwendung, den exakt funktionierenden OpenRGB-Binärstand,
Plugin, zugehörigen Bauquellen und persönlichen OHC-/RGB-Einstellungen.
Private Archive werden restriktiv lokal gespeichert und niemals hochgeladen.
SHA256-Prüfungen und Archivprüfung sichern die Kopien ab. Zwei Ordner auf
derselben Festplatte ersetzen keine räumlich getrennte Sicherung; GitHub
ergänzt deshalb den öffentlichen Quell-/Release-Stand, nicht die privaten Daten.

## Manuelle Wiederholung

Falls die Pakete bereits in `dist/` liegen, kann die Sicherung wiederholt werden:

```bash
python3 scripts/backup_release.py "$(cat packaging/VERSION)" "$(cat packaging/BUILD_CHANNEL)" --project-root . --dist dist
```

Nach jedem Versionsbau muss geprüft werden, dass der neue Versionsordner und sein Vorgänger vorhanden sind und `sha256sum -c SHA256SUMS` in beiden Ordnern erfolgreich ist.
