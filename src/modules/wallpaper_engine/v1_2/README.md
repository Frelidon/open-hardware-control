# Wallpaper Engine for KDE 1.2

Dieses Modul bindet die lokal installierte CaptSilver-Plasma-Erweiterung ein,
ohne deren QML oder Binärdateien zu kopieren oder zu verändern.

- `library.py` liest ausschließlich lokale Steam-Workshop-Metadaten und einen
  ausdrücklich gewählten, separaten Videoordner. Der begrenzte Rücksprung nutzt
  diese Liste, weil CaptSilver v1.4 selbst noch keine echte Zurück-API besitzt.
- `plasma.py` liest den aktuellen Plasma-Zustand, erzeugt begrenzte Plasma-
  Skripte für Auswahl, Skalierung und dokumentierte Einstellungsprofile und
  adressiert die Wiedergabe am tatsächlich registrierten Plasma-D-Bus-Objekt.
- `installer.py` wählt ausschließlich ein zum Fedora-Stand passendes offizielles
  CaptSilver-RPM und verlangt die von GitHub veröffentlichte SHA256-Prüfsumme.
- `onboarding.py` enthält den wiederaufrufbaren Erststart-Assistenten und trennt
  Benutzer-Download, zweite Bestätigung und sichtbare Polkit-/DNF-Installation.
- `page.py` stellt Workshop-Wallpaper, lokale Videos, Wiedergabesteuerung, Skalierungsmodi,
  Anleitung und den Sprung zur originalen Plasma-Oberfläche dar. Feste
  Galerie-Metriken verhindern schrumpfende Karten nach einem Apply-Refresh.

Der Standardpfad verwendet die originalen v1.4-Werte. Die optionale
Leistungsoptimierung ist vollständig reversibel und installiert weder lokale
Plugin-Patches noch Cache-Watcher. Steam-Workshop-Dateien werden niemals
geschrieben, verschoben oder gelöscht.
