# Open Hardware Control 3.4.29.183 INTERN

Hardware Fix erhält zwei Hauptaktionen: Installieren und Deinstallieren. Der
lokale Fix läuft unabhängig vom OHC-Fenster; die verwirrende Anbieterwahl entfällt.
Weitere Optionen bewahrt Diagnose, DRM-Spieltest und einzelne Reparaturschritte.
Technische Details sind standardmäßig eingeklappt. Vier Sprachen sind vorhanden.

Installieren verwendet die bisherigen festen Installer. Vorhandene gesunde
Bootressourcen bleiben erhalten; Ubuntu/GNOME richtet nach aktivierter EDID den
variablen Desktopmodus und den bekannten lokalen Benutzerdienst ein. Fedora
führt diese Ubuntu-Automatik nie aus. Bei nötigem Neustart endet die erste Stufe;
danach lässt sich die Einrichtung über Installieren abschließen. Bereits aktives,
dauerhaft gespeichertes GNOME-VRR wird nicht erneut gesetzt. Keine automatische
Änderung der EDID-Timings und kein automatischer Systemneustart.

Der MSI-Fix verwendet in Fenstererkennung und DRM-Diagnose die ausgelieferte
anonymisierte EDID. Der vorherige Ubuntu-Livenachweis zeigt Mirage im Randlosmodus
vor der Korrektur mit VRR_ENABLED=0 und nach einem begrenzten AppIndicators-Reset
mit VRR_ENABLED=1. Das ist Treiberreadback, keine optische Frequenzmessung.
Ein Live-Gegenversuch ohne EDID-Override wurde nicht vorgenommen.

Terminaljobs verwenden feste Aktionsnamen und validierte UUIDs. Schnelle Resultate
werden schon beim ersten Poll erkannt, alte Resultate und Doppelklicks verworfen.
Fehler beim Prozessstart liefern ein abgeschlossenes Fehlerergebnis. Anbieterstatus
wird erst nach Erfolg lokal gespeichert; Ergebnisstatus folgt danach. Protokolle
werden begrenzt, redigiert und als Klartext angezeigt. Bootparameter werden exakt
statt als Teilzeichenfolge erkannt; fehlerhafte Metadaten bleiben sicher lesbar.

Freigabe: 1.763 Tests und fünf Untertests bestanden; 474 Python-Laufzeitquellen
und 2.658 gemeinsame Nachrichten-IDs. Vollständige vierfache UI-Lokalisierung,
Sicherheit/Datenschutz, Kompilierung, Modulbudgets und restliche Release-Wächter
bestanden. Zehn echte Qt-Hauptfensteraufnahmen mit synthetischem Fixstatus prüfen
drei Größen, beide Themen sowie offene Details und längere Übersetzungen.
Die anfängliche Sandbox sperrte zwölf lokale Testsockets; der komplette Lauf
mit erlaubten lokalen Sockets und deaktivierten Hardwarezugriffen bestand.
Nach Korrektur eines alten ZIP-Dateinamens bestanden auch die unveränderten
abschließenden Wächter. Keine Prüfung wurde ausgelassen oder abgeschwächt.

Aus dieser geprüften Quellfreigabe werden Laufzeit-/Entwickler-ZIP, Quell-TAR,
Local-AI-Gitbundle, DEB und RPM gebaut. Paket- und Sicherungsnachweise werden
nach dem Bau im lokalen PROJECT_STATUS.md dokumentiert. Fedora nur isolierte
Vertragstests; kein neuer Fedora-Hardwarelauf. Die normale installierte Anwendung
wurde durch diesen Paketbau noch nicht aktualisiert. GitHub bleibt unverändert.

Lokaler Nachweis nach Paketbau · 14.11.26: Alle sechs Artefakte, vollständige
Archive/Manifeste, 474 identische Pythonquellen und 169 Assets sowie genau beide
.182/.183-Sicherungen mit je acht Prüfsummen verifiziert. RPM-Header-/Payload-
Digests und DEB-Metadaten/Eigentümer geprüft. Keine Installation oder neuer
Hardwarelauf. Die Pakete/Sicherungen bleiben unveränderte Schnappschüsse vor
diesem nachträglichen Nachweis; vollständige lokale Evidenz in PROJECT_STATUS.md.

Nachfolgende lokale Aktualisierung · 14.11.26: Benutzer- und Systeminstallation
sind auf .183 aktualisiert und normal gestartet. 716 lokale Laufzeitdateien und
799 DEB-Paketdateien wurden bytegleich geprüft. Einstellungen vor dem Neustart,
Profile und Plugins zusätzlich danach unverändert. CPU-Kurve und RGB aktiv;
gespeichertes Levita-Design nach automatisch behobenem eigenem TRCC-Startkonflikt
im Dauerbetrieb. VRR-Dienst durchgehend aktiv; kein neuer Spiel-/Boot-/Fedora-Test.

GitHub-Quellupload · 14.11.26: Der Eigentümer hat den Upload des INTERN-Standes
auf `codex/hardware-fix-3.4.29.183` beauftragt. Dieser Entwicklungsbranch enthält
Quellen, Tests und Dokumentation; Downloadpakete und öffentlicher Release bleiben
getrennt. Frühere Aussagen über unverändertes GitHub beschreiben den Stand vor
diesem Folgeauftrag. Die gebauten Pakete bleiben unveränderte Schnappschüsse.
