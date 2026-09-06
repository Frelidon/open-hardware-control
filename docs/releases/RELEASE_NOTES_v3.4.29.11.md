# Open Hardware Control 3.4.29.11 INTERN

## Neues Logo und Programmsymbol

Das neue, bereitgestellte Open-Hardware-Control-Logo ist jetzt oben in die linke Programmleiste eingelassen. Eine daraus eigens erzeugte kompakte Variante ohne Schrift dient als Fenster-, Tray-, Taskleisten- und Desktop-Symbol. Das RPM enthält dafür zusätzlich passende PNG-Größen von 32 bis 512 Pixeln.

## Installierte Levita-Standarddesigns

OHC erkennt die von TRCC Linux installierten 1600×720-Landschaftsdesigns nun automatisch unter `~/.trcc/data/theme1600720l`. Ein vollständiges Design lässt sich direkt mit seinem eigenen Hintergrund sowie den in `config1.dc` gespeicherten Positionen, Farben, Sensoren und Live-Werten laden. Alternativ bleibt derselbe Entwurf als obere Hardwaredaten-Ebene über einem anderen lokalen Video verwendbar. Quadratische und hochformatige TRCC-Ordner werden nicht als Levita-Layout angeboten; der sichere Testmodus bleibt Standard und es erfolgt kein automatischer USB-Schreibzugriff.

Der portable ZIP-Installer kopiert nun außerdem die Thermalright-Module und die neue Startfensterdiagnose vollständig in die Benutzerinstallation.

## Vorübergehende Fensterdiagnose

OHC protokolliert jetzt jedes eigene Top-Level-, Dialog-, Popup- und Werkzeugfenster beim Öffnen, Ausblenden und Schließen. Zusätzlich wird die Erzeugung nativer Qt-Fensteroberflächen erfasst. Die Einträge enthalten Fensterklasse, Titel, Objektname, Typ, Geometrie, Modalstatus, Elternfenster und den Zustand `WA_DontShowOnScreen`. Dadurch lässt sich beim weiterhin beobachteten leeren Startfenster erkennen, ob OHC selbst eine sichtbare Oberfläche erzeugt hat.

Gestartete Python- und Qt-Hilfsprozesse werden mit Programmname, sicheren Befehls-Tokens, Argumentanzahl, Sitzungstyp und `QT_QPA_PLATFORM` protokolliert. Potenziell geheime Argumentwerte werden nicht übernommen; schnelle identische Wiederholungen werden zusammengefasst. Die Diagnose erscheint im sichtbaren OHC-Log und bereits ab dem frühesten Programmstart dauerhaft in `~/.local/state/open-hardware-control/startup.log`. Sie kann nach Klärung der Ursache wieder entfernt werden.

Wayland erlaubt einer normalen Anwendung keine vollständige systemweite Auflistung fremder Fenster. Die Kombination aus eigenen Qt-Fensterereignissen und allen von OHC gestarteten Helferprozessen bildet deshalb die sichere Diagnosegrenze.

## Levita-Balkenkante

Die 18-Pixel-Rundung liegt ausschließlich an der linken, zum Displayinhalt zeigenden Ober- und Unterkante des schwarzen Balkens. Seine rechte physische Außenkante bleibt vollständig bündig und schwarz. Vorschau, Cachekennung und reale TRCC-Maske verwenden dieselbe korrigierte Form.
