# Open Hardware Control 3.4.10 INTERN

Diese interne Reparaturversion korrigiert den OpenRGB-Direct-Ausgabepfad nach der in 3.4.9 ergänzten ARGB-Zoneneinrichtung. Ein erfolgreicher, zurückgelesener OpenRGB-Farbpuffer beweist nicht, dass ein konkreter Controller den Zonen-Callback physisch ausgegeben hat. Deshalb deckt OHC jetzt sowohl den vollständigen Gerätepfad als auch einen einmaligen Zonen-Fallback ab.

## Direct-Ausgabe

- Statische Farben und jeder OHC-Animationsschritt werden als vollständiger `UPDATELEDS`-Geräteframe gesendet.
- Beim ersten Wechsel in Direct Mode werden vollständig abgebildete Zonen zusätzlich einmal über `UPDATEZONELEDS` übertragen.
- Folgeframes verwenden nur den Geräteframe und verursachen keine dauerhafte doppelte USB-Last.
- SDK-Protokoll 4 und 5, Loopback-Zwang, Paket-/LED-Grenzen, serielle Geräteaufträge und Rücklesung bleiben erhalten.
- Der Status lautet „Serverzustand bestätigt“ und weist darauf hin, dass die sichtbare ARGB-Ausgabe nicht elektrisch rücklesbar ist.

## Interstellar V2 und Zonengrößen

- Eigene Lüfterprofile für TZMRIT/Jungle-Leopard Interstellar V2 Normal und Reverse mit jeweils 24 LEDs.
- Die Zahl der Lüfter stammt aus den in der verschiebbaren Thermaltake-PC-Ansicht einem Anschluss zugeordneten Blöcken.
- Nicht zugeordnete Hub-Zonen werden beim Anwenden des Lüftermodells auf 0 vorbereitet; bekannte Komponentenanschlüsse bleiben manuell.
- Ungewöhnlich hohe Werte erzeugen eine Plausibilitätswarnung und benötigen eine Bestätigung.
- OHC behauptet keine automatische elektrische Erkennung: ARGB-Datenleitungen melden die Anzahl verketteter Lüfter und LEDs nicht zurück.

## Bedienung und Prozesskonflikte

- Größere Liste ausgewählter Geräte mit Steuerweg und letztem Ergebnis.
- Mehrstufige Wiederherstellung der RGB-Seiten- und Navigationsscrollposition nach Dialog, Befehlsende und Kachelumbau.
- Konflikthinweise für separates OpenRGB, OpenLinkHub und ckb-next; OHC beendet keine fremden Prozesse.
- Die bestehende Einzelinstanz-Sperre greift weiterhin vor Qt- und Hardwareinitialisierung.
- Konfigurationsfehler lösen keine Gerätesperre aus; bestätigte Backend-Abstürze werden weiterhin auf das betroffene Gerät begrenzt.

## Teststatus

Die automatisierten Tests prüfen Paketformen, Geräte- und Zonenframes, SDK 4/5, Folgeframes ohne wiederholten Zonen-Fallback, Interstellar-Profile, Prozesskonflikte, Plausibilitätswarnungen, Quellpaketvollständigkeit und statische Sicherheitsregeln. Ein realer Test an MSI MYSTIC LIGHT und Airgoo AG-DRGB16 bleibt erforderlich, weil Software die sichtbare LED-Ausgabe nicht zurücklesen kann.

Die Version bleibt intern und wird nicht als öffentliches GitHub-Release veröffentlicht.
