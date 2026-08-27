# Open Hardware Control 3.4.6 INTERN

Diese interne Fehlerbehebung konzentriert sich auf die im realen RGB-Test gemeldeten Bedien- und Mehrgeräteprobleme. Sie bleibt ausdrücklich unveröffentlicht.

## Sichtbare Auswahl und klare Zuständigkeit

- Die bisherige Mini-Zeile „Ausgewählte Kacheln“ ist jetzt eine große Geräteliste.
- Jede Zeile zeigt Gerätename, Steuerweg und den letzten Schreibstatus.
- Der OpenRGB-Spiegeleintrag des bereits von `liquidctl` besessenen NZXT-Controllers wird ausgeblendet. Sichtbar bleiben die drei echten NZXT-Kanäle.
- „Nativer Gerätemodus“ heißt nun „Grafikkarte / Hardwaremodus“ und nennt die tatsächlich betroffenen Geräte ohne Direct Mode – in Frelidons System vor allem die Sapphire RX 9070 XT.

## Verlässlicheres Anwenden

- Der ausdrücklich gewählte GPU-Hardwaremodus wird nicht mehr als automatische Vorgabe für einen OHC-Effekt verwendet. Ein zufällig sichtbarer Off-/Dark-Modus kann die Sapphire dadurch nicht mehr unbeabsichtigt ausschalten.
- `SETCUSTOMMODE` wird je Direct-Gerät und Engine-Laufzeit höchstens einmal gesendet. Statische Farbe, Einzeltest und Folgeframes wiederholen die empfindliche Modusinitialisierung nicht unnötig.
- Ein gewöhnlicher Fehler bei RAM, Airgoo, MSI oder NZXT beendet nicht mehr die gesamte Befehlsfolge. Alle übrigen Geräte werden weiter verarbeitet; Fehler werden anschließend gerätebezogen zusammengefasst.
- Ein bestätigter OpenRGB-`ApplyOptions`-Absturz bleibt weiterhin nur für das verursachende Gerät quarantänisiert.

## Scroll- und Diagnosekorrekturen

- Seiten- und Navigationsposition werden bei Kachelumbau und nach RGB-Befehlen über mehrere Qt-Ereignisrunden wiederhergestellt.
- Doppelte aufeinanderfolgende Arbeitsbereich-Neuaufbauten nach Geräteerkennung und NZXT-Statuswechseln wurden entfernt.
- `session.log` und `previous-session.log` werden automatisch im XDG-State-Verzeichnis geführt.
- `open-hardware-control-diagnostics` übernimmt diese Protokolle sowie begrenzte OpenRGB-Coredump- und Journal-Auszüge.
- Der Bericht erfasst OpenRGB-Paket, laufende Prozesse samt Elternprozess und den Listener auf Port 6742. So lässt sich eindeutig unterscheiden, ob OHC die Engine gestartet hat oder eine fremde Instanz die Steuerung blockiert.

## Noch benötigter Hardwaretest

Für RAM und Airgoo ist weiterhin das neue Terminal-/Coredump-Protokoll erforderlich, weil der zuletzt übermittelte Ausschnitt ausschließlich LCD-Messungen und keine RGB-Schreibaktion enthält. Version 3.4.6 verhindert jedoch bereits, dass ein Einzelgerätefehler alle folgenden Geräte der Aktion blockiert.
