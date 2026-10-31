# Open Hardware Control 3.4.29.54 INTERN

Datum: 09.09.2026
Kanal: INTERN
Veröffentlichung: kein GitHub-Push, Tag oder öffentliches Release

## Display-Effekte für Thermalright Levita

- Ein neuer, eigener Navigationsbereich **Display-Effekte** liegt direkt neben LCD und bietet eine große 1600×720-Vorschau mit dem aktuellen Sensorlayout aus Ebene 2.
- Der erste Effekt ist ein prozedural erzeugter, nahtloser Rauch-Loop mit Primär-/Sekundärfarbe, Schärfe, Dichte, Geschwindigkeit, Turbulenz, Leuchten, Richtung und drei Ausgangsvoreinstellungen.
- Die Vorschau bleibt lokal. Erst **Effekt auf Gerät anwenden** rendert einen begrenzten 4-Sekunden-/24-FPS-H.264-Loop über einen Offscreen-Helfer und übergibt ihn als Ebene 1 an das bestehende Levita-Studio.
- Es existiert kein zweiter Hardware-Schreibpfad: Testmodus, Ebene 2, Masken, TRCC-Warteschlange, USB-Schutz und Firmware-Rückgabe bleiben beim vorhandenen LCD-Studio.

## OpenLinkHub einschließlich Web-UI aktualisieren

- Der OpenLinkHub-Bereich prüft die feste offizielle GitHub-Release-Schnittstelle und vergleicht die lokale mit der neuesten Version. Am 09.09.2026 erkennt die Prüfung auf dem Referenzsystem `0.9.0` und offiziell `0.9.1`.
- RPM/DEB-Installationen werden nach Bestätigung ausschließlich über bereits eingerichtete DNF-/APT-Quellen und feste Argumentlisten aktualisiert.
- Die auf dem Referenzsystem vorhandene Benutzerinstallation unter dem in `OpenLinkHub.service` festgelegten Home-Verzeichnis wird ebenfalls unterstützt: Das offizielle amd64-Archiv wird nur mit veröffentlichter GitHub-SHA-256 akzeptiert, ohne Links/Pfadtraversierung entpackt und nach Dienststopp atomar eingesetzt.
- Konfiguration und Datenbank/Profile werden bewahrt. Die vorige Installation bleibt als lokales Geschwister-Backup erhalten; startet der neue Benutzerdienst nicht, wird automatisch zurückgerollt.
- Das Web-Dashboard ist Teil des OpenLinkHub-Pakets und wird damit gemeinsam erneuert. OHC lädt kein unbestätigtes Remote-Installationsskript mit Root-Rechten.

## Sprache, Start und Abschluss

- Die Navigationsleiste, dynamischen Gehäuselüfterkarten, Seitenüberschriften und Über-Seite wechseln jetzt vollständig mit Deutsch, Englisch, Spanisch und Französisch. Display-Effekte und OpenLinkHub-Update wurden im selben Schritt in allen vier Einzeldateien ergänzt.
- KDE-Startfeedback wird nur beim Tray-Autostart unterdrückt; ein normaler manueller Start behält seine Startanzeige.
- Startet der Benutzer OHC erneut, fordert die zweite Instanz die bereits laufende über einen privaten lokalen Socket zum Anzeigen/Aktivieren auf. Hardwarezugriff bleibt durch die bestehende Prozesssperre geschützt.
- Die asynchrone Prozesswarteschlange hält beim Beenden eine konkrete QProcess-Referenz, sodass ein synchron geliefertes `finished`-Signal keinen Abschlusswettlauf mehr erzeugt.

## Weiterhin enthalten

- Der 100-%-Leistungs-Override für aktivierte Gehäuselüfter, der rückstellende 0-%-/10-s-Test und die echte PWM/DC-Umschaltung ausschließlich über vorhandenes `pwmN_mode` bleiben unverändert.
- Die drei projekt-eigenen Levita-3D-Loops aus 3.4.29.50 und die Levita-/Kraken-Abschlussroutinen aus 3.4.29.53 sind enthalten.
- Ein temperaturzielgeregelter Kühlungsmodus und CPU-Taktsteuerung bleiben bewusst Zukunftsthemen; diese Version führt dafür keinen ungetesteten Hardware-Regler ein.
