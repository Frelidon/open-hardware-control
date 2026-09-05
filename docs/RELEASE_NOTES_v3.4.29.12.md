# Open Hardware Control 3.4.29.12 INTERN

## Neues Levita Display Studio

Die beiden Display-Ebenen werden jetzt als moderne Kartenbibliotheken dargestellt. Hintergrundbilder, Videos und vollständige TRCC-Layouts erscheinen mit Vorschau direkt nebeneinander; die Kategorien Gallery, Tech, HUD, Light, Nature, Aesthetic, eigene Dateien und OHC-Designs sind unmittelbar als Schaltflächen erreichbar. Die sehr großen Kombobox-Popups entfallen vollständig.

Die Hauptvorschau hält das echte Levita-Format 1600×720 ein. Bei einem Video werden lokal erzeugte, begrenzte Vorschauframes direkt auf dieser großen Fläche animiert. Die bisherige kleine linke Hover-Vorschau wurde entfernt. Zuschnitt/Notch und die einzeln verschiebbaren OHC-Werte bleiben erhalten, öffnen sich aber erst über kompakte Einstellschaltflächen.

## Drei eigene OHC-Hintergründe

Das Paket enthält drei neu erstellte, projektbezogene 1600×720-Hintergründe: **Carbon Blue**, **Titanium Blue** und **Plasma Circuit**. Sie liegen vollständig lokal unter `assets/levita-designs`, enthalten keine Herstellerdesigns und werden in einer eigenen OHC-Kategorie angezeigt. Die vorhandenen frei verschiebbaren CPU-, GPU-, RAM- und Uhrzeit-Einblendungen können weiterhin darübergelegt werden.

## Zuverlässiger Display-Autostart

Hintergrund und Datenebene werden nun gemeinsam gespeichert. Mit „Ausgewähltes Levita-Design bei OHC-Start automatisch laden“ lässt sich der Autostart ausdrücklich aktivieren; „Aktuelle Auswahl als Startdesign speichern“ setzt beide Ebenen noch einmal bewusst als Startzustand. Bei aktivierter Automatik folgen spätere Kartenänderungen dem gespeicherten Startdesign.

Nach einem Desktop-Autostart wartet OHC die bereits vorhandene Ruhezeit ab, stellt exakt diese Auswahl wieder her und startet die Levita-Übertragung. Ist TRCC beziehungsweise das Display beim ersten Versuch noch belegt, folgt genau ein zweiter Versuch nach drei Sekunden. Kraken-LCD-Profile und das getrennte Levita-Studio erhalten keine konkurrierenden Schreibaufträge. Der sichere Testmodus bleibt Standard und blockiert auch einen aktivierten Display-Autostart weiterhin zuverlässig.

Breit importierte TRCC-Datenordner werden zusätzlich nach der Zielgeometrie gefiltert. Quadratische 480×480- und hochformatige Layouts mit `config1.dc` erscheinen nicht mehr in der Levita-Datenebene; geprüft passende 1600×720-Layouts bleiben verfügbar.

## Fedora-/Plasma-Taskleistensymbol

Das laufende Qt-Fenster setzt nun neben seinem Fenstericon auch die Desktop-Datei-ID `open-hardware-control`. Die Desktop-Datei enthält zusätzlich `StartupWMClass=open-hardware-control`. Dadurch kann KDE Plasma das bereits installierte kompakte OHC-Symbol auch dem minimierten beziehungsweise laufenden Programmfenster korrekt zuordnen.

## Sicherheit und Teststatus

Die neue Automatik ist eine ausdrückliche Benutzereinstellung. Medienerkennung, Kartenwechsel und Vorschau erzeugen keinen USB-Schreibzugriff. TRCC Linux bleibt der einzige Display-Backendprozess; Befehle werden weiterhin seriell ausgeführt. Mainboard-PWM, OpenRGB, OpenLinkHub und Kraken besitzen unveränderte, voneinander getrennte Hardwaregrenzen.
