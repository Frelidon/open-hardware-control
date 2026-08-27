# Open Hardware Control 3.4.21 INTERN

## Schwerpunkt

3.4.21 ist ein Stabilitäts- und Koordinator-Release. Vor dem später geplanten Cooling-Center werden die bereits stark ausgelasteten Kraken-/OpenRGB-Pfade zentralisiert, protokolliert und gegen konkurrierende oder veraltete Aufträge abgesichert.

## Wesentliche Änderungen

- Zentraler `USB-COORD` für Kraken-Zugriffe mit Request-IDs, Prioritäten, Besitzerstatus, Retry/Fehlerzuständen und Latest-request-wins.
- `RGB-COORD` für schnelle Effektwechsel und wiederverwendeten SDK-Worker.
- Stabiler RGB-Autostart: gespeichertes Profil wird erst nach stabiler OpenRGB-Geräteerkennung vollständig angewendet.
- Schnellprofile-Widget korrekt in die Übersicht eingebettet; keine versehentliche Top-Level-Anzeige beim Tray-Autostart.
- Shutdown-Fallback auf Kraken-Flüssigkeitstemperatur, solange USB noch verfügbar ist.
- Direkte Aktivierung der mitgelieferten LCD-Designs sowie per Design gespeicherte Skalierung.
- Animierte Hover- und Hauptvorschau optional abschaltbar.
- NZXT-ESC-Live-Renderer im CAM-Streamer mit eingebetteter Preview als Fallback für externe Medien.
- Geräteabhängige LCD-Zielauflösung in Rendering/Vorschau; Raw-USB bleibt capability-gated.
- Sortierbare LCD-Kacheln, Sticky-Vorschau und Mittelklick-Scrolling.
- Profilimport schlägt den aktuellen Dateinamen als Profilnamen vor.
- Erweiterte Privacy-/Release-Prüfung.

## Bewusst verschoben

Die Mainboard-Lüftersteuerung/Cooling-Center-Erweiterung mit NCT6687, Kurven und MSI-/Secure-Boot-/MOK-Assistent ist bewusst nicht Teil dieses Releases. Sie soll erst auf dem stabilisierten Koordinator-Unterbau folgen.

## Testziel

Besonders relevant sind Boot ohne manuelles OpenRGB, gespeichertes RGB-Profil, schnelle LCD-/RGB-Wechsel, Shutdown-Rückstellung des LCD und importierte NZXT-ESC-Live-Designs.
