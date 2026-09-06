# Open Hardware Control 3.4.29.42 INTERN

Diese interne Version repariert die Wallpaper-Engine-Wiedergabesteuerung, ergänzt die originalen Skalierungsmodi, führt eine persistente Startbildschirmwahl ein und vereinheitlicht die Scrollleisten.

## Wallpaper Engine for KDE 1.2

- Pause, Fortsetzen, Weiter und Ton umschalten verwenden nun das tatsächlich unter `org.kde.plasmashell` registrierte `/WallpaperEngine`-Objekt samt vollständigem CaptSilver-Interfacenamen. Zurück wählt die vorherige validierte lokale Workshop-Karte, weil CaptSilver v1.4 seine veröffentlichte Previous-Methode noch nicht als Rücksprung implementiert.
- Seitenverhältnis beibehalten, Skalieren und zuschneiden sowie Auf Vollbild strecken stehen für alle oder einen ausdrücklich gewählten Plasma-Bildschirm zur Verfügung.
- Die Skalierung wird über CaptSilvers `DisplayMode` 0/1/2 geschrieben. Steam-Workshop-Dateien und das installierte Plugin bleiben unangetastet.
- Assistent, Fünf-Workshop-Checkliste, zweistufig bestätigter Fedora-Installer, feste Kartenmaße, Originalprofil und optionale rücksetzbare Optimierung bleiben erhalten.

## Fenster und Oberfläche

- Standardmäßig wird der Qt-/KDE-Hauptbildschirm als Startziel verwendet.
- Unter Einstellungen → Anzeige und DPI kann ein konkreter Monitor dauerhaft anhand seines Bildschirmnamens gewählt werden. Ist er beim nächsten Start nicht verbunden, verwendet OHC den Hauptbildschirm, ohne die Auswahl zu vergessen.
- Wiederhergestellte Fenstergrößen werden auf die verfügbare Fläche des Ziels begrenzt. Unter Wayland darf KWin die endgültige Top-Level-Position weiterhin bestimmen.
- Alle Scrollbereiche, Listen, Bäume, Textfelder und Tabellen erhalten ein gemeinsames acht Pixel schmales Scrollleisten-Design.

## Prüfung

Die reine Bildschirmrichtlinie, Plasma-Skript- und D-Bus-Befehlserzeugung sowie der vollständige PySide6-Offscreen-Aufbau werden regressionsgetestet. Der Build bleibt `INTERN`; es wird kein Tag, Push oder öffentliches Release erzeugt.
