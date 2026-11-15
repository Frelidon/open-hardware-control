# Open Hardware Control 3.4.29.183 STABLE

Öffentliche Freigabe · 15.11.26

## Neuerungen seit dem öffentlichen Release .176

- Hardware Fix zeigt Installieren und Deinstallieren als Hauptaktionen. Die
  lokale Installation ist Standard; Diagnose, Spieltest und einzelne Reparaturen
  bleiben unter Weitere Optionen erreichbar. Technische Details sind eingeklappt.
- Die MSI-VRR-Erkennung verwendet wieder die tatsächlich ausgelieferte anonymisierte
  EDID. Terminalergebnisse werden über eindeutige Jobs zugeordnet; schnelle
  Abschlüsse, veraltete Resultate, Doppelklicks und Startfehler sind abgesichert.
- LCD-Arbeitsbereiche gliedern Bibliothek, Komposition und Displaybetrieb. Die
  gemeinsame GPU-Seite verbindet Gerätebild, Livewerte, Übertaktung und Lüfterkurve.
  Häufige Darstellungsoptionen und animierte Hintergründe stehen vorn in den Einstellungen.
- Profile sind als lesbare Karten organisiert; frische CPU-Messwerte werden vor
  dem automatischen Profilstart abgewartet. Originale Matrix-/RGB-/LCD-Designs,
  Größenwahl und gemeinsame UI-Bereiche aus .177 bis .182 sind enthalten.

Vollständige Einzeländerungen: [Changelog](https://github.com/Frelidon/open-hardware-control/blob/v3.4.29.183/docs/CHANGELOG.md) und die bisherigen
Release Notes von .177 bis .182. Bestehende Einstellungen, Profile, Designs und
Hardwarebesitzer bleiben erhalten. Alle neuen UI-Texte unterstützen Deutsch,
Englisch, Spanisch und Französisch.

## Hardware Fix

Installieren nutzt die bisherigen festen Installer. Gesunde Bootressourcen
werden nicht erneut geschrieben. Ubuntu/GNOME richtet nach geladener EDID den
variablen Desktopmodus und denselben lokalen Benutzerdienst ein. Der Dienst
läuft unabhängig vom OHC-Fenster. Fedora behält seinen getrennten Bootpfad und
führt diese Ubuntu-AppIndicators-Automatik nicht aus. Ein nötiger Neustart
bleibt manuell; anschließend schließt Installieren die Einrichtung ab.
Bereits aktiviertes und dauerhaft gespeichertes GNOME-VRR wird nicht erneut gesetzt.

Der Fix ändert keine EDID-Timings und flasht keine Monitorfirmware. Er ist für
exakt erkannte MSI MAG 274QPF X30MV über DisplayPort bestimmt; die vorhandene
Zuordnung zu allen DP-Anschlüssen erfordert, andere DP-Monitore vorher zu trennen.

## Prüfung und Grenzen

Die INTERN-Freigabe bestand 1.763 Tests und fünf Untertests sowie die Release-
Wächter; vor dem Quellupload bestanden zusätzlich 43 gezielte Regressionen.
Die erste lokale STABLE-Prüfung bestand 1.763 Tests und fünf Untertests.
Die GitHub-CI deckte danach zwei Umgebungsunterschiede auf: andere Schriftmaße
im Gehäuse-Editor und eine vom realen USB-Gerät abhängige LCD-Testannahme.
Der Footer wird jetzt nach abgeschlossenem Layout neu angepasst; die LCD-
Prüfung verwendet eine feste Erkennungsfixture. Bestehende Prüfungen bleiben
erhalten und der Gehäuse-Test ergänzt eine zweite Schriftfamilie. Der finale
`check_release.sh`-Lauf bestand unter Qt 6.12.0 mit 1.764 Tests und fünf Untertests;
unter Qt 6.11.2 bestanden zusätzlich beide Schrift- und die LCD-Regressionsprüfung.
Alle Sicherheits-, Datenschutz- und Release-Wächter bestanden. Die Pakete werden
aus diesem korrigierten Stand neu gebaut. Sicherheits-/Datenschutzscan, vollständige vierfache
UI-Lokalisierung, Kompilierung, Modulbudgets und getrennte Ubuntu-/Fedora-Verträge
gehören zur Freigabe. Zehn echte Qt-Hauptfensteraufnahmen mit synthetischem
Fixstatus dokumentieren drei Größen und beide Themen; sie sind kein Hardwaretest.

Ubuntu-Live: Mirage im Randlosmodus meldete vor der EDID-Erkennungskorrektur
VRR_ENABLED=0, danach nach einem begrenzten AppIndicators-Reset 1. Dies ist
Treiberreadback, keine optische Frequenzmessung. Ein Gegenversuch ohne EDID-
Override wurde nicht durchgeführt; dessen Entbehrlichkeit ist damit nicht belegt.
Die .183-INTERN-Benutzer- und Systeminstallation wurde normal gestartet:
CPU-Kurve und RGB aktiv, gespeichertes Levita-Design nach automatisch behobenem
eigenem TRCC-Startkonflikt im Dauerbetrieb. Der STABLE-Release ergänzt außerdem die nachgelagerte Footer-Anpassung für
unterschiedliche Schriftmaße im Gehäuse-Editor; das Hardwareverhalten bleibt gleich.

Fedora hat isolierte Vertragstests; ein neuer realer Fedora-/KDE-Hardwarelauf,
optischer Frequenztest, Boot-/Deinstallationstest und Windows-Test wurden für
diese Veröffentlichung nicht neu durchgeführt. Die laufende lokale INTERN-
Installation und ihre persönlichen Daten werden durch den Release nicht ersetzt.

## Downloads und Prüfsummen

- `open_hardware_control_v3_4_29_183.zip` — universelles Laufzeitpaket.
- `open-hardware-control_3.4.29.183_all.deb` — Debian/Ubuntu/Mint.
- `open-hardware-control-3.4.29.183-1.noarch.rpm` — Fedora/Nobara.
- `Entwicklerpaket.3.4.29.183.zip` — vollständiges Entwicklerpaket (öffentlicher GitHub-Dateiname).
- `open-hardware-control-3.4.29.183-source.tar.gz` — Quellarchiv.
- `Open_Hardware_Control_3.4.29.183_LOCAL_AI.gitbundle` — vollständige lokale Git-Übergabe.

`SHA256SUMS` gilt für die exakten öffentlichen Dateinamen. `SHA256SUMS.local`
behält zusätzlich die lokale Liste mit dem ursprünglichen Entwickler-ZIP-Namen.
Pakete, Archive, Manifeste und externe rollierende Sicherungen werden vor der
Veröffentlichung geprüft. Private Einstellungen, Pluginsicherungen und persönliche
Protokolle sind kein Bestandteil der Downloads.
