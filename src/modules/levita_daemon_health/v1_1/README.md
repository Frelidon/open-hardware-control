# Levita-Daemongesundheit 1.1

Dieses reine Standardbibliothek-Modul erkennt ausschließlich den eigenen,
exakten `trcc daemon`-Prozess über `/proc`, liest dessen RSS und klassifiziert
bekannte IPC-Verbindungsabbrüche. Vor einem Signal werden PID, aktueller
Benutzer und die exakte Befehlsform unmittelbar erneut geprüft. Das Modul
öffnet kein USB-Gerät und enthält keine Qt- oder UI-Abhängigkeit. Der
Orchestrator besitzt weiterhin allein Neustart und Designübertragung.
