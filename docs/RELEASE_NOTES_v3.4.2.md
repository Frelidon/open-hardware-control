# Open Hardware Control 3.4.2 INTERN

## Behobener Startfehler

Das von Frelidon bereitgestellte Fedora-Protokoll zeigt den vollständigen Fehlerpfad: Während `make_rgb_tab()` wurde über `rebuild_rgb_workspace()` bereits `update_rgb_studio_preview()` ausgeführt. Zu diesem Zeitpunkt war `rgb_preview_started` in Version 3.4.1 noch nicht angelegt, weil die Initialisierung erst nach `build_ui()` erfolgte.

Version 3.4.2 setzt die Vorschauuhr vor `build_ui()` und prüft im Aktualisierungspfad zusätzlich defensiv, ob der Wert vorhanden ist. Ein statischer Regressionstest erzwingt diese Reihenfolge künftig im Release-Check.

## Automatische Diagnose

Die Anwendung schreibt nun mit privaten Dateirechten:

- `~/.local/state/open-hardware-control/startup.log` für Start und normalen Abschluss;
- `~/.local/state/open-hardware-control/last-crash.log` für die letzte unbehandelte Python-Ausnahme.

Persönliche Home-Pfade und bekannte Gerätekennungen werden vor dem Schreiben gefiltert. Das bestehende read-only Diagnosewerkzeug übernimmt die letzten Startzeilen und den letzten Absturz automatisch in seinen ebenfalls anonymisierten Bericht.

## Unverändert aus 3.4.1

Die seriellen OpenRGB-Einzelgerätetransaktionen, nativen Fallbacks, Gerätegruppen, dauerhaften Namen, PC-Skizze, Frelidons Hub-/Lüfterprofil, der Geräte-Testmodus und der vollständige RGB-Reset bleiben enthalten.

Diese Version bleibt intern und ist nicht für ein öffentliches GitHub-Release vorgesehen.
