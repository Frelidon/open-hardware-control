# Open Hardware Control 3.4.9 INTERN

Diese interne Korrektur richtet die in den realen OpenRGB-SDK-Protokollen sichtbaren Null-Zonen von MSI MYSTIC LIGHT und Airgoo AG-DRGB16 ein. Der Controller wurde erkannt, seine Kanalnamen waren vorhanden, aber OpenRGB hatte noch keine LED-Farbplätze angelegt. Normale Farbpakete konnten deshalb physisch nichts bewirken.

## LED-Zonen und verkettete Lüfter

- Neuer Dialog „LED-Zonen und Lüfter einrichten“ für Direct-Mode-Geräte.
- Pro OpenRGB-Kanal werden Lüfter/Geräte und LEDs je Lüfter/Gerät eingetragen; die Gesamtzahl wird automatisch berechnet.
- Aktuelle, minimale und maximale Zonengröße sowie Änderbarkeit werden direkt über SDK 4/5 gelesen.
- Bekannte Lüfterzahlen aus Frelidons Thermaltake-Retro-360-TG-Ansicht werden für A1/A2 vorgeschlagen. Die reale LED-Zahl pro Lüfter bleibt eine bewusste Eingabe, weil sie sich elektrisch nicht zuverlässig erkennen lässt.
- Zonengrößen werden in den Einstellungen und in exportierbaren RGB-/Gesamtprofilen gespeichert.

## Sicherer SDK-Ablauf

1. Controllerzahl und aktuelle Gerätebeschreibung synchronisieren.
2. Jede gewünschte Zonengröße gegen OpenRGBs Mindest-/Höchstwert prüfen.
3. Nur geänderte, vergrößerbare Zonen mit dem offiziell dokumentierten `RGBCONTROLLER_RESIZEZONE`-Paket setzen.
4. Neue Größen zurücklesen und vollständig bestätigen.
5. Direct Mode aktivieren, Farben zoneweise senden und Modus/Farbpuffer zurücklesen.

Ein Gerät mit null angelegten LEDs wird nicht mehr nach drei Frames sicherheitsgesperrt. OHC zeigt stattdessen „LED-Zonen und Lüfter noch einzurichten“ und verarbeitet die übrigen Geräte weiter.

## NZXT und Diagnose

- Bei einer gemischten Auswahl wird der getrennte NZXT-/liquidctl-Auftrag zuerst gesendet; die Kraken wartet dadurch nicht hinter mehreren seriellen OpenRGB-Rücklesungen.
- Die Oberfläche unterscheidet wirklich von OpenRGB gelistete LEDs, gespeicherte OHC-Zonengrößen und die bloße serverseitige Rücklesebestätigung.
- Neue Tests decken leere vergrößerbare Zonen, `RESIZEZONE`, anschließende Zonenwrites, Rücklesung und die persistente `Lüfter × LEDs`-Berechnung ab.

Die Version bleibt intern und wird nicht als öffentliches GitHub-Release veröffentlicht.
