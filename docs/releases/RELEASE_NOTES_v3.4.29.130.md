# Open Hardware Control 3.4.29.130 INTERN

Datum: 01.10.2026

## GPU-Cockpit

- Die breite Hauptansicht kommt ohne Seiten-Scrollleisten aus und skaliert ihre
  drei Spalten kompakt. Taktbahnen, Zahlenfelder und Aktionsmenü folgen dem
  freigegebenen dunklen Referenzdesign.
- Die fünf LACT-Lüfterpunkte sind in der Kurve ziehbar und bleiben mit den
  exakten Temperatur-/Prozentfeldern synchron.
- Eigene geprüfte GPU-Bilder lassen sich direkt importieren und zurücksetzen.
- Ein reiner Lüfterentwurf nutzt ausschließlich den rückstellenden physischen
  LACT-Test. Grafiklast wird nur für Tuning oder den ausdrücklichen Lasttest
  gestartet.

## RGB Studio und räumliches Gehäuse

- Galerien nutzen auf breiten Ansichten bis zu sechs kompakte Karten. Auswahl,
  Kategorie und linke Navigation bleiben synchron; Zähler werden nicht mehr
  abgeschnitten.
- Ein eigener räumlicher Ablauf verbindet Richtung und Tempo mit dem echten
  LED-/Lüfterpfad des gewählten Komponentenblocks.
- Nutzer können direkte Abstände oder Tiefe zwischen zwei vorhandenen Blöcken
  in Millimetern oder Inch eintragen. Intern werden die Werte verlustarm in
  Millimetern gespeichert; Standard ist Millimeter.
- Die Gehäusegrafik stellt diese Beziehungen mit eigener OHC-Zeichnung dar.
  Fehlende Herstellermaße werden nicht erfunden und es werden keine
  Herstellerbilder eingebettet.

## Reaktionsfähigkeit

- SSD-Cachepflege beginnt erst nach einer Eingaberuhephase, wird mit niedriger
  Prozess- und Idle-I/O-Priorität gestartet und gibt zwischen begrenzten
  Arbeitsportionen Zeit an Oberfläche und Displaypfad zurück.
- Die Laufzeit protokolliert Dauer, geprüfte/entfernte Dateien und Restgröße,
  ohne Originalmedien oder aktive Hardwaredateien anzutasten.

## Sicherheit und Prüfung

- Die räumlichen Einstellungen ändern nur gespeicherte Darstellung/LED-Pfade;
  sie erfinden keine Hardwareverbindung und verändern keine PWM-Zuordnung.
- Der reine GPU-Lüfterpfad ist durch eine Regression gegen jeden Benchmarkstart
  gesichert. Hardware-Schreibpfade wurden im Testlauf nicht ausgelöst.
- Deutsch, Englisch, Spanisch und Französisch enthalten denselben Bestand von
  1.838 Nachrichten. Der vollständige Release-Check bestand 836 Tests sowie
  Sicherheits-, Datenschutz- und Modulprüfung. Runtime-/Entwickler-ZIP,
  Quellarchiv, Local-AI-Bundle und RPM wurden lokal gebaut und einschließlich
  der rollierenden Sicherung per SHA-256 verifiziert. `dpkg-deb` ist auf diesem
  Rechner nicht verfügbar; deshalb wurde kein DEB vorgetäuscht.
