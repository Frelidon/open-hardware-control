# Open Hardware Control 3.4.29.28 INTERN

**Datum:** 02.09.26

Die neuen Laufzeitprotokolle belegen die verbliebene Transportursache: Um 15:21:05 wurde das zusammengestellte Cache-Theme erfolgreich geladen. Unmittelbar danach startete OHC einen separaten `trcc display play`-Prozess. Dieser zweite Prozess erzeugte eine neue TRCC-App, öffnete USB erneut und verlor bereits beim nächsten Handshake die Antwort. Spätere Kurzprozesse endeten schließlich in der nachgewiesenen `libusb_open`-/`hid_exit`-Race mit `SIGSEGV`.

OHC verwendet nun den von TRCC 9.9.11 ausdrücklich vorgesehenen Daemonmodus. Alle TRCC-Clients erhalten `TRCC_DAEMON=1` und reichen ihre Befehle über den Unix-Socket an einen einzigen langlebigen TRCC-Prozess weiter. Nur dieser Dienst besitzt das Levita-USB-Gerät. Split-Modus, Helligkeit, Ausrichtung und `load-theme` verwenden dieselbe verbundene App und lösen keine unabhängigen Handshakes mehr aus.

Der zusätzliche OHC-Prozess `trcc display play` entfällt vollständig. Der TRCC-Daemon startet laut installiertem Backend selbst seine Metrics-/Render-Schleife; sie aktualisiert Video und Live-Sensorwerte nach dem Theme-Laden. TRCC-Clientprozesse laufen zusätzlich mit `QT_QPA_PLATFORM=offscreen`.

Das Abziehen des Displaykabels war nicht die Ursache. Ein Kabelreset kann den Controller zurücksetzen, konnte aber die fehlerhafte Folge aus mehreren frischen Softwarebesitzern nicht beheben. Ein kompletter Rechnerneustart ist für diese Codekorrektur nicht grundsätzlich erforderlich. Das Levita-Fachmodul bleibt 1.3 unter `modules/lcd_levita/v1_3/`; geändert wurde die Legacy-Orchestrierung.
