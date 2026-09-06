# Hauptfenster-Platzierung 1.0

Dieses Modul hält die persistente Bildschirmwahl unabhängig von Qt-UI und
Hardwarezugriff. `primary` ist der sichere Standard. Eine feste Wahl speichert
den von Qt/KDE gemeldeten Bildschirmnamen statt der veränderlichen Position in
der Monitorliste. Fehlt der gewählte Monitor, fällt OHC für diesen Start auf den
aktuellen Hauptbildschirm zurück, ohne die feste Auswahl zu vergessen.

Der Hauptfenster-Orchestrator setzt den ausgewählten `QScreen` vor dem Anzeigen
am nativen Fenster und hält die wiederhergestellte Größe innerhalb seiner
verfügbaren Fläche. Unter Wayland bleibt die endgültige Top-Level-Position eine
Entscheidung des Compositors; OHC übergibt dort das bestmögliche Bildschirmziel.
