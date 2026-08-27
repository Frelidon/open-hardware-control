# Open Hardware Control by Frelidon v3.1.1 INTERN

## Behoben

- Fedora 44 stellt Qt 6 QDbus als `qdbus-qt6` bereit. Open Hardware Control erkennt diesen Namen jetzt direkt.
- `qdbus6` und die bekannten privaten Qt6-Binärpfade werden weiterhin beziehungsweise zusätzlich unterstützt.
- Ein korrekt eingerichtetes Fedora-KDE-System wird nicht mehr fälschlich als inkompatibel angezeigt.

## Abhängigkeiten

- Fehlende optionale KDE-Werkzeuge werden einmalig nach dem Start angeboten.
- Im Bereich **System → Desktop-Designs** steht zusätzlich **Fehlende Pakete installieren** bereit.
- DNF, APT, Pacman und Zypper erhalten feste, distributionsspezifische Paketnamen.
- Installation erfolgt ausschließlich nach Bestätigung und nur aus bereits eingerichteten Paketquellen.
- Nach erfolgreicher Installation prüft die Anwendung den Status erneut und schaltet die Designs frei.
- Fehlende Desktop-Werkzeuge blockieren keine NZXT- oder OpenLinkHub-Funktion.

## Unverändert enthalten

- reversible Windows-11- und macOS-Anordnungen für KDE Plasma 6
- schreibfreie Vorschau, Bestätigung, datiertes Backup, automatischer Rollback und manuelle Wiederherstellung
- sämtliche NZXT-Kraken-, LCD-/GIF-, Kühlungs-, Profil- und OpenLinkHub-Funktionen aus 3.1.0 INTERN

Diese Version bleibt intern. `BUILD_CHANNEL=INTERN` verhindert weiterhin eine versehentliche öffentliche
GitHub-Veröffentlichung.

---

## English summary

Open Hardware Control 3.1.1 INTERNAL recognizes Fedora's `qdbus-qt6` command as well as `qdbus6` and common
Qt6 private paths. Missing optional KDE tools can be installed after confirmation through fixed DNF, APT,
Pacman or Zypper mappings. The app rechecks compatibility afterwards, and missing desktop-only tools never
block NZXT or OpenLinkHub control. The release remains internal and publication helpers stay locked.
