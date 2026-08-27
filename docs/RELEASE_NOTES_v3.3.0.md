# Open Hardware Control 3.3.0 INTERN

## Schwerpunkt

Diese interne Version führt das eigene RGB-Studio ein. Zusätzliche RGB-Geräte werden über einen separat installierten lokalen OpenRGB-SDK-Server erkannt. Oberfläche, Profile, Vorschau und Effekte sind eigener OHC-Code; OpenRGB- und Effects-Plugin-Quellcode wird nicht eingebettet.

## Neu

- statische Farbe pro erkanntem OpenRGB-Gerät;
- gemeldete native Hardwaremodi;
- zehn eigene prozedurale OHC-Effekte;
- sieben mitgelieferte RGB-Designvorlagen;
- Live-Vorschau, Helligkeit, Geschwindigkeit, Richtung und zwei Farben;
- RGB-Studio-Daten in exportierbaren Gesamt-/RGB-Profilen;
- optionaler OpenRGB-Paketinstaller für DNF, APT, Pacman und Zypper;
- Fedora-Zuordnung für `openrgb` und `openrgb-udev-rules`;
- lokale Clientbindung an `127.0.0.1:6742`;
- sitzungsweise Schreibfreigabe und automatische Gerätebesitzsperre;
- höchstens ein OpenRGB-Frameprozess sowie Stopp nach drei Fehlern;
- experimentelle Desktop-Designs standardmäßig ausgeschaltet und verborgen.

## Bewusst noch begrenzt

- Softwareanimationen sind in dieser ersten Stufe auf höchstens 10 Hz begrenzt.
- Zonen werden angezeigt, aber noch nicht getrennt als Animationsflächen angesteuert.
- Es gibt noch keine geräteübergreifende 2D-LED-Karte oder Audiosynchronisation.
- OpenRGB muss vom Benutzer selbst als lokaler SDK-Server gestartet werden.
- Reale OpenRGB-Hardwaretests mit mehreren Herstellergeräten stehen aus.

## Sicherheit und Lizenzen

OpenRGB und das OpenRGB Effects Plugin sind GPL-2.0-or-later. Eine Kombination wäre unter GPLv3 grundsätzlich möglich; 3.3.0 übernimmt den Quellcode dennoch nicht. Der Client ist auf Loopback, validierte Argumente, expliziten Clientmodus und bereits erreichbaren Server begrenzt. Fremde NZXT-/Corsair-Schreibpfade werden bei aktivem OHC-Modul gesperrt.

Details: `RGB_STUDIO.md`, `RGB_SECURITY_AUDIT.md`, `SECURITY.md`.
