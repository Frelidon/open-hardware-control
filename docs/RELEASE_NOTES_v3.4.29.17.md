# Open Hardware Control 3.4.29.17 INTERN

## Eigenes Symbol im KDE-Plasma-Systemabschnitt

Die Plasma-Einstellung „Einträge“ zeigte für Open Hardware Control bislang ein kleines generisches Symbol. Ursache war nicht der Icon-Cache und auch keine Besonderheit des Rechners: `setup_tray()` forderte ausdrücklich das fremde Theme-Symbol `preferences-system-cooling` an. Das bereits korrekte OHC-Fenster- und Startmenüsymbol wurde nur als Rückfall verwendet, wenn dieses Standardsymbol fehlte.

3.4.29.17 übergibt dem `QSystemTrayIcon` immer das projektbezogene kompakte Emblem. Dafür enthält das Programm nun eine eigene transparente 22×22-Datei sowie die vorhandenen 32×32-, 48×48- und 64×64-Varianten in einem gemeinsamen `QIcon`. RPM und portabler Installer legen die neue Größe zusätzlich im freedesktop-Iconpfad `hicolor/22x22/apps/open-hardware-control.png` ab.

Als Referenz wurde die aktuelle ckb-next-Umsetzung geprüft: Sie installiert ebenfalls mehrere `hicolor`-Größen und begrenzt ihre Tray-Ausgabe ausdrücklich auf eine geeignete 22×22-Darstellung. OHC übernimmt das robuste Größenprinzip, bleibt aber bei Qt/PySide6s portablem `QSystemTrayIcon`, sodass keine zusätzliche KDE-Bibliothek zur Laufzeit nötig wird.

Nach einer Aktualisierung muss die laufende alte OHC-Instanz vollständig beendet und neu gestartet werden. Plasma erhält den Tray-Pixmap beim Registrieren des neuen Prozesses; ein bloßes Schließen des Hauptfensters beendet OHC bei aktiviertem Traybetrieb nicht.
