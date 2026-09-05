# Open Hardware Control 3.4.29.41 INTERN

Diese interne Version vervollständigt die erste Einrichtung von Wallpaper Engine und behebt die nach einem Apply schrumpfende Galerie.

- Beim ersten bewussten Öffnen erscheint eine vollständige Anleitung. Sie führt durch Steam-Installation, mindestens fünf Workshop-Abonnements, Plugin-Aktivierung, Steam-Bibliothek, ersten Test und die erst danach optionale Optimierung. Der Assistent bleibt jederzeit wiederaufrufbar.
- Auf Fedora kann ein ausdrücklicher Button das offizielle CaptSilver-Plugin installieren. OHC wählt nur ein stabiles, exakt zur Fedora-Hauptversion und Architektur passendes RPM vom offiziellen GitHub-Release, begrenzt die Downloadgröße und verlangt dessen veröffentlichte SHA256-Prüfsumme.
- Download und Installation sind getrennt: Der Download läuft ohne Administratorrechte. Nach erfolgreicher Prüfung fragt OHC ein zweites Mal; nur bei Zustimmung startet `pkexec dnf install`. Die sichtbare Systemabfrage erhält das Passwort direkt, OHC sieht und speichert es nicht.
- Systeme ohne den geprüften Fedora-/DNF-/Polkit-Pfad bekommen weiterhin die offiziellen manuellen Hinweise; OHC führt dort keine geratenen Root-Befehle aus.
- Wallpaper- und Videokarten behalten nach dem Anwenden ihre festen 192×108-Vorschauen und 224×154-Karten. OHC stößt die Qt-Layoutberechnung nach dem Bibliotheksrefresh selbst an, statt auf einen Fenstergrößenwechsel zu warten.
- Die neue Standardreihenfolge lautet Übersicht, Kühlung, RGB-Studio, LCD, Wallpaper Engine, optional Corsair/OpenLinkHub, Profile, Einstellungen, Über und Log. Exakt alte Standardfolgen werden migriert; echte eigene Sortierungen bleiben erhalten.

Die gewünschte zum OHC-Design passende Hauptfenster-Titelleiste ist nicht Teil dieser Version. KWin bleibt für 3.4.29.41 Eigentümer der Dekoration; eine spätere rahmenlose Variante erhält eigene KDE-Wayland-/X11-, Resize-, Maximierungs-, Barrierefreiheits- und Tray-Starttests.
