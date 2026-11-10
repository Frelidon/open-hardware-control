# Entwicklerpaket 3.4.29.169 STABLE

Dies beschreibt das Entwicklerpaket, nicht die Projektstartseite:
[README.md](../../README.md).

Das Entwickler-ZIP und Quellarchiv enthalten den vollständigen editierbaren
Stand: Python- und nativen C++-Quellcode, eigene Ressourcen, vier Sprachkataloge,
Tests/C++-Fixtures, Werkzeuge, Installer, Dokumentation, CI und Release-Workflows.
Das normale Benutzer-ZIP ist schlanker und enthält keine Tests/Release-Skripte.
Der Builder vergleicht den Entwicklerbestand mit dem Projekt und bricht bei
fehlenden Dateien ab. Private Einstellungen, Logs und Aufnahmen fehlen bewusst.

## Prüfen und bauen

Python-Testabhängigkeiten sind pytest, Pillow und PySide6; zusätzlich werden
ffmpeg und die Qt-Laufzeitbibliotheken benötigt. Die kompilierten nativen
Regressionsfixtures benötigen einen C++17-Compiler und `nlohmann-json3-dev`
(Ubuntu) beziehungsweise die entsprechende Distributions-Entwicklerbibliothek.
Die GitHub-Workflows installieren diese Abhängigkeiten ausdrücklich.

```bash
./scripts/check_release.sh
./scripts/build_release.sh 3.4.29.169
cd dist
sha256sum -c SHA256SUMS
```

Der Builder erzeugt ZIP, Entwickler-ZIP, Quellarchiv, Git-Bundle und die
verfügbaren DEB-/RPM-Pakete. Ohne `rpmbuild` existiert ein geprüfter Python-
RPM-Builder. Ohne `dpkg-deb` wird das DEB ausdrücklich übersprungen; für eine
vollständige Veröffentlichung muss es tatsächlich erzeugt und geprüft werden.
Es gibt keine erfundenen Paket- oder Hardwareerfolge.

## Native Engine und Hardwaretests

Die [native RGB-Anleitung](../hardware/NATIVE_RGB_SETUP.md) erklärt den passenden
OpenRGB-1.1-/Qt-6-Bau, das Plugin und den kleinen MSI-Patch. Ein noarch-Paket
installiert keinen architekturspezifischen RGB-Treiber. Ein C++-Plugin ist immer
an die passende OpenRGB-/Qt-ABI gebunden. SDK-/Queue-Erfolg ist keine optische
Bestätigung. Ubuntu-Liveergebnisse und offene Fedora-Liveprüfungen sind getrennt.

GUI-/Hardwaretests niemals vollständig mit `sudo` starten. Schreibtests erfordern
passende Geräte, ausdrückliche Freigabe und einen einzigen Eigentümer.
`OHC_INSTALL_HOME=/absoluter/testpfad ./packaging/install.sh` erlaubt einen
isolierten Benutzerinstallationstest ohne Veränderung der echten Installation.

## Sicherungen

Jeder erfolgreiche Bau ergänzt die vollständige atomare Zwei-Versionen-Sicherung
außerhalb des Repositorys. Beide aufbewahrten `SHA256SUMS` kontrollieren.
Das lokale private Funktionsbackup umfasst zusätzlich installierte RGB-Binärdateien,
Plugin und Konfiguration; es gehört nicht auf GitHub. Siehe
[SOURCE_CODE.md](SOURCE_CODE.md) und [RELEASE_BACKUP_POLICY.md](RELEASE_BACKUP_POLICY.md).
