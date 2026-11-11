# Open Hardware Control 3.4.29.174 INTERN

Alle Oberflächen- und Backendänderungen aus .172/.173 sind enthalten.
Die Haus-Auswahl speichert die Standard-DPI jetzt unabhängig von OpenLinkHubs
aktiver Stufe. OpenLinkHub speichert bei einem DPI-Tastendruck auch seine
aktive Stufe; eine reine Änderung dieses Felds reicht deshalb nicht als
unabhängiger Standard. OHC bewahrt die ausdrückliche Vorgabe privat je
Mausprofil auf und stellt sie vor dem Start des OpenLinkHub-Benutzerdienstes
wieder her. Der feste optionale ExecStartPre-Helfer arbeitet ohne USB, Netzwerk
oder Administratorrechte. Ein fehlender Helfer blockiert OpenLinkHub nicht.

„OpenLinkHub-Vorgabe beibehalten“ entfernt die OHC-Vorgabe. Andere Profile und
Einstellungen bleiben erhalten. Speichern und Rückkehr sichern Profil, Regel
und Drop-in. Ohne ausdrückliches Speichern wird kein Drop-in eingerichtet und
keine DPI geändert. Alle vier Sprachen enthalten den neuen Vorgabetext.
Prüfnachweis: vollständiger Wächter mit 1.544 Tests und fünf Untertests,
einschließlich viersprachiger Qt-UI, physischem DPI-Tastendruck als Simulation,
Neustart-/Profil-/Rückkehr- und Besitzschutzprüfungen, bestanden. Der echte
systemd-Parser akzeptiert den optionalen Befehl. Paket-/Installationsnachweis
steht im Projektstatus. Reale Fedora-Hardwareprüfung bleibt offen; kein Upload.
