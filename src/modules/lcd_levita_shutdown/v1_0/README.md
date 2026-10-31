# Levita-Abschaltwächter 1.0

Beim Beenden wird die ursprünglich eigene TRCC-PID direkt geprüft, falls
die allgemeine Daemon-Suche inzwischen eine andere PID liefert. Ein bereits
beendeter eigener Prozess ist kein fehlgeschlagener Abschluss; die andere
Instanz bleibt unangetastet.

Dieses Modul gibt die Levita beim kontrollierten Programmende an ihre Firmware
zurück. Nach einem echten OHC-Hardwarezugriff überwacht außerdem ein kleiner,
getrennter Prozess die Lebensdauer des Hauptprozesses über eine Pipe. Endet OHC
unerwartet, sendet der Wächter genau einen begrenzten, daemonbasierten
`device disconnect`-Aufruf. Ohne weitere Frames zeigt die Levita-Firmware nach
ihrem eigenen Zeitlimit wieder das eingebaute Thermalright-Standardlogo.

Der Wächter erfindet kein USB-Protokoll, öffnet das Gerät nicht direkt und läuft
im Testmodus nicht. Ein sauberer Exit bestätigt die Rückgabe und beendet den
Wächter ohne einen zweiten Hardwarezugriff. Danach stoppt OHC einen von ihm
gestarteten TRCC-Daemon über dessen IPC-`kill`-Befehl. Ein bereits vorher
laufender oder inzwischen ersetzter Daemon bleibt unangetastet. Ohne laufenden
Daemon wird für die Firmware-Rückgabe kein neuer gestartet.

Der dateibasiert gestartete Wächter ergänzt seinen installierten
Anwendungsstamm selbst auf `sys.path`. Er bleibt dadurch auch nach dem Ende des
OHC-Elternprozesses importfähig und fällt nicht vor dem Pipe-Warten aus.
Ein Pipe-Ende allein löst keine Rückgabe aus: Der Wächter prüft zusätzlich die
genaue Eltern-PID samt Linux-Startzeit. Solange dieser Prozess lebt oder seine
Identität nicht lesbar ist, bleibt das aktive LCD erhalten. Eine wiederverwendete
PID oder ein Zombie beendet die Beobachtung. Hardwarefreie Tests starten den
Wächter nie. Diese bereits in `.148` vorhandenen Grenzen sind wiederhergestellt.
`SIGKILL`, Stromverlust oder das
gleichzeitige Beenden aller Prozesse durch das Betriebssystem können keine
absolute Abschlussgarantie erhalten.
