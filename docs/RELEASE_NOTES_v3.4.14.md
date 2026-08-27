# Open Hardware Control 3.4.14 INTERN

Diese interne Korrekturversion behebt die wiederkehrende RGB-Fehlerschleife aus 3.4.13.

## Behoben

- Das OHC-Design „Abwechselnd“ erzeugt für den NZXT 2023 RGB Controller nicht länger `alternating-4`. liquidctl 1.16.0 brach damit auf der realen Hardware mit `KeyError` ab. Als sicherer Hardwarefallback wird nun `fading` mit zwei Farben verwendet.
- Kurzlebige OpenRGB-CLI-Befehle, die OHC selbst für Inventar oder native Gerätemodi startet, werden nicht mehr als separates OpenRGB gewertet.
- Damit entfällt die Stop-/Wiederübernahme-Schleife, bei der ein eigener Sapphire-`External Control`-Befehl die Animation fälschlich sperrte und anschließend immer wieder neu startete.
- Asynchrone RGB-Teilfehler öffnen kein modales KDE-Dialogfenster mehr.

## Neue RGB-Fehlerliste

- Das RGB-Studio zeigt Fehler und Warnungen mit Zeit, Stufe, Aktion/Gerät und Detailtext.
- Die Liste ist auf 100 Einträge begrenzt und kann geleert werden.
- Ein fehlerhaftes Gerät unterbricht die übrigen Geräte derselben Aktion weiterhin nicht.

## PC-Profil

- Die sichtbare Thermaltake-360-Vorlage heißt jetzt „Frelidon PC“.
- Die interne Kennung bleibt unverändert, damit bestehende Profile weiterhin geladen werden können.

## Status

Die Version bleibt intern. Die Sicherheits-, Quellcode- und Paketprüfungen werden vor der Weitergabe vollständig ausgeführt.
