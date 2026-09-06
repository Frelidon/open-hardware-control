# Open Hardware Control 3.4.13 INTERN

Diese interne Version macht die RGB-Galerie eindeutig direkt bedienbar und ergänzt eine sichere Wiederübernahme, wenn OpenRGB versehentlich parallel geöffnet wurde.

## RGB-Galerie

- Ein Klick auf eine Musterkachel startet die Übertragung direkt; der bisherige zusätzliche Startknopf bleibt nur für den manuellen Editorweg erhalten.
- Die neue Kachel „Feste Farbe“ verwendet die gewählte Hauptfarbe und überträgt spätere Farbänderungen unmittelbar.
- Eine starke blaue Umrandung und das Kennzeichen „AUSGEWÄHLT“ bleiben an der gewählten Kachel sichtbar.
- Eine grüne Umrandung und „AKTIV“ erscheinen erst nach einer bestätigten lokalen Übertragung.
- Das neue Statusfeld über der Galerie nennt Auswahl, Farbe, Helligkeit und den aktuellen Hardwarestatus. Bei einem Konflikt bleibt die Auswahl sichtbar und wird als pausiert oder vorgemerkt gekennzeichnet.

## Sichere RGB-Wiederübernahme

- „RGB-Steuerung neu übernehmen“ erkennt die Geräte neu, baut nur OHCs eigenen SDK-Zustand neu auf und wendet anschließend das ausgewählte Muster an.
- Die optionale automatische Wiederübernahme ist standardmäßig aus. Nach ausdrücklicher Aktivierung wartet sie beobachtend, bis ein separat gestartetes OpenRGB vollständig beendet wurde.
- OHC beendet keinen fremden OpenRGB-Prozess. Solange ein fremder Prozess oder ein nicht zugeordneter lokaler SDK-Server vorhanden ist, bleiben Schreibzugriffe blockiert.
- Ein kurz nachlaufender SDK-Server wird zeitlich begrenzt erneut geprüft. Ohne bereits bestätigte Sitzungs- oder Startprofilfreigabe erfolgt keine automatische Hardwareübernahme.

## Projektstatus

Open Hardware Control ist ein unabhängiges, inoffizielles Open-Source-Community-Projekt. Bisher besteht keine offizielle Unterstützung, Kooperation, Freigabe oder Verbindung zu NZXT, Corsair, be quiet!, OpenLinkHub, OpenRGB oder anderen genannten Herstellern und Projekten.
