# Open Hardware Control 3.4.29.77 INTERN

## Reaktionsfähigere LCD-/RGB-Oberfläche

- RGB-Vorschauen werden nur noch auf der sichtbaren RGB-Seite gezeichnet. Die 60-FPS-Levita-Vorschau, Kartenanimationen und neue Vorschaubild-Aufträge pausieren außerhalb der LCD-Seite.
- Verborgene Levita-Galerien erzeugen ihre zahlreichen Qt-Karten erst beim Öffnen. Die Seite selbst kann zuerst gezeichnet werden; bereits erzeugte Kacheln bleiben für spätere Wechsel erhalten.
- Die GameMode-Abfrage startet im Leerlauf nur noch alle zehn statt alle drei Sekunden einen lokalen Statusprozess.
- Die Start-Fensterdiagnose protokolliert relevante Fenster weiter vollständig, fasst versteckte Combo-/Tooltip-Hilfsflächen aber in einer Zeile zusammen.

## Levita-Notfreigabe

- Der im gelieferten Log reproduzierte Fehler `interface is in use by another process` löst einmalig den bestehenden, abgekühlten Wiederherstellungsweg aus.
- Reagiert `trcc kill` nicht, darf OHC ausschließlich einen unmittelbar erneut geprüften, zum aktuellen Benutzer gehörenden Prozess mit der exakten Befehlsform `trcc daemon` zunächst beenden und nötigenfalls hart stoppen. Fremde Prozesse oder lediglich ähnlich benannte Programme werden nie signalisiert.
- Die neue Schaltfläche **Display freigeben** bietet denselben streng begrenzten Rückweg manuell und überträgt danach das ausgewählte Design erneut. Bleibt ein anderer externer USB-Besitzer aktiv, meldet OHC den Fehler weiterhin, statt ihn ungeprüft zu beenden.

## Gespeicherter Startzustand

- Die gespeicherte Gehäuselüfter-Automatik wird nach Erkennung der bestätigten Kanäle wieder aktiviert. Automatik und einheitliche Kurvenvorlage, etwa **Leise**, erscheinen anschließend wieder blau.
- Das Hauptfenster bleibt bis zur Anwendung des gespeicherten Normal-/Maximiert-Zustands unsichtbar. Dadurch erscheint der erste sichtbare Frame sofort im gewünschten Modus.
- Deutsch, Englisch, Spanisch und Französisch bleiben mit 1.292 gemeinsamen Nachrichten-IDs vollständig. Interner Build; kein GitHub-Push, Tag oder öffentlicher Release.

## Geprüfte Unterbauten

- Die offiziellen Veröffentlichungen wurden am 12.09.2026 erneut abgeglichen: TRCC Linux 9.9.12, OpenLinkHub 0.9.1 und liquidctl 1.16.0 bleiben die aktuellen stabilen Stände. OHC bündelt diese eigenständigen Hardwaredienste weiterhin nicht und verändert keine globale Installation stillschweigend.
- OpenRGB 1.0-rc3.1 bleibt beim offiziell veröffentlichten SDK-Protokoll 5 und ist damit mit OHCs auf Loopback und Protokoll 4/5 begrenztem SDK-Pfad kompatibel. Das Referenzsystem besitzt weiterhin das Distributionspaket 1.0-rc2; eine reale Gerätebestätigung mit rc3.1 wird deshalb nicht behauptet.
- Qt/PySide 6.11.2 ersetzt den dokumentierten 6.11.1-Stand. Pillow 12.3.0 bleibt das Sicherheitsminimum: diese Version schließt mehrere 2026 veröffentlichte Speicherfehler und Dekompressionsbomben; das Referenzsystem ist bereits aktuell.
