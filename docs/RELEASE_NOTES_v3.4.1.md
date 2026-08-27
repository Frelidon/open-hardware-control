# Open Hardware Control 3.4.1 INTERN

## Zweck dieser internen Korrektur

Die vier Fedora-Coredumps zeigen OpenRGB `1.0~rc2` jeweils in `ApplyOptions`/`std::vector::operator[]`. Jeder abgestürzte Client wurde mit mehreren wiederholten `--device`-Blöcken gestartet. Version 3.4.1 entfernt diesen Aufruftyp vollständig: OHC erzeugt pro Gerät genau einen Befehl und führt die Befehle seriell aus.

Zusätzlich wurde ein OHC-Zustandsfehler behoben. Beim frühen Aufbau der RGB-Seite wurden gespeicherte Auswahl- und Gruppenzuordnungen gefiltert, obwohl die asynchrone Geräteerkennung noch keine Geräte geliefert hatte. Der leere Zwischenzustand darf Einstellungen nun nicht mehr löschen.

## RGB-Arbeitsbereich

- „Alle auswählen“ oberhalb und unterhalb des Kachelbereichs.
- Eine neue Gruppe übernimmt die aktuelle Auswahl.
- Gleichnamige Geräte bleiben getrennt, erhalten Nummern und können über das Stiftsymbol benannt werden.
- Ein eigener Geräte-Testmodus schaltet zunächst alle von OHC besitzbaren Geräte aus und danach nur die gewählte Komponente in einer frei wählbaren Testfarbe ein. „Nächstes Gerät“ und Umbenennen sind direkt erreichbar.
- Native Modi werden für die gesamte Auswahl mit Kompatibilitätszähler angeboten.
- Geräte ohne Direct Mode erhalten beim Start eines OHC-Designs einen passenden gemeldeten Hardwaremodus.
- Die bisher sichtbare separate NZXT-RGB-Box wurde entfernt; `led1`, `led2` und `led3` bleiben als normale Gerätekacheln verfügbar.
- Der große vollständige RGB-Reset bleibt erhalten.

## PC-Skizze und Frelidons Vorlage

Die neue generische Skizze verwaltet Oben/Radiator, Front, Seite, Boden, Heck, GPU, GPU-Halterung, RAM und Pumpenkopf. Jede Position speichert Namen, Anzahl, Anschluss, Gruppe und zugeordnete Gerätekacheln.

Die mitgelieferte Vorlage enthält die im Projektgespräch notierte Belegung:

- Kraken 360 oben, drei NZXT-RGB-Kanäle;
- A1: zwei Frontlüfter;
- A2: notierter Verbund aus zwei Front- und einem Hecklüfter;
- B7 und `SYS-FAN6`: drei Reverse-Intake-Lüfter unten/in der Mitte;
- Sapphire RX 9070 XT;
- B6: separate Grafikkartenhalterung;
- zwei RGB-Arbeitsspeicherriegel.

Die automatische Zuordnung gleichnamiger Sapphire-Einträge ist eine editierbare Startannahme. Auf dem realen System kann Gerät 1/2 beziehungsweise 2/2 über Stiftsymbol und PC-Position vertauscht werden, ohne einen Treiberzugriff auszulösen.

## Profile und Sicherheit

RGB- und Gesamtprofile enthalten jetzt eigene Gerätenamen sowie die komplette PC-Skizze. Beim Laden eines Profils werden weder RGB-Schreibfreigabe noch Hardwareanimation automatisch gestartet. Auch das alte direkte Anwenden des versteckten NZXT-Einzeleditors beim Profilimport wurde entfernt.

OpenRGB bleibt als separater, fensterloser Kindprozess erhalten. Netzwerkzugriff bleibt auf `127.0.0.1:6742` begrenzt, Fremdinstanzen bleiben schreibgesperrt und maximal ein Einzelgeräteclient läuft gleichzeitig.

Der Testmodus verändert ausschließlich Geräte, die OHC exklusiv besitzt. Durch OpenLinkHub oder einen fremden OpenRGB-Prozess gesperrte Geräte werden sichtbar genannt; bei einer fremden OpenRGB-Instanz wird der vollständige Einzeltest blockiert, damit „alle anderen aus“ keine falsche Zusage bleibt.

## Noch praktisch zu prüfen

- Gerät 1/2 und 2/2 der Sapphire-Meldung im neuen Testmodus der echten GPU und der B6-Halterung zuordnen und sofort umbenennen.
- Zwei ENE-RAM-Kacheln und sämtliche LEDs beider Riegel testen.
- Kraken `led1` bis `led3` einzeln und gemeinsam testen.
- „Alle auswählen“, Gruppenwechsel, Neustart und Profilimport mit realer Hardware prüfen.
- Direct-Mode-Animationen beobachten: Die sichere globale Obergrenze beträgt zehn Geräteframes pro Sekunde und wird bei mehreren Direct-Geräten im Round-Robin-Verfahren geteilt.

Diese Version bleibt intern und ist nicht für ein öffentliches GitHub-Release vorgesehen.
