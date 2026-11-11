# Open Hardware Control 3.4.29.176 INTERN

Der Kühlungsassistent kann einen Anschluss jetzt ausdrücklich als „Nicht
angeschlossen“ überspringen. OHC blendet seine vollständige Kachel aus und
bietet ihn unten in einer kompakten Gruppe erneut zur Zuordnung an. Kurven
bleiben erhalten; eine Null-RPM-Messung allein ändert keine Zuordnung.

Der 0-%-Stopptest für Gehäuselüfter läuft höchstens zwei Minuten. Weiter,
Abbrechen, Kanalwechsel und Programmende stellen alle beteiligten Kanäle
zurück. Die kurze Treiber-Absturzsicherung wird dabei regelmäßig erneuert;
ohne diese Sicherung wird der lange Test verweigert. Bei ausbleibender
Erneuerung gibt der Treiber seine manuellen Kanäle unabhängig von OHC zurück.
CPU- und Pumpenanschlüsse bleiben ausgeschlossen. Normale Drehzahltests bleiben
zehn Sekunden lang. Ein Lüfter kann 0 % hardwarebedingt anders umsetzen;
die tatsächliche Reaktion bleibt ausdrücklich vom Benutzer zu bestätigen.

Beim Start setzt OHC bereits zugeordnete Lüfter-RGBs mit vorhandener
Schreibfreigabe automatisch weiß und pausiert die Animation. Native/SDK-
Schreiber werden geordnet übergeben. Beim Schließen kehrt das unveränderte
gewählte Design zurück; gespeicherte Farben und Profile bleiben erhalten.

Die Temperaturaufzeichnung zeigt Sensorsymbole und Messwertkarten mit
aktuellem Wert, Minimum, Maximum und Zeitpunkt. Sensoren lassen sich von
links nach rechts hineinziehen und zurück entfernen; Checkboxen, Knopf und
Tastatur bleiben verfügbar. Diagramm, Einheiten, Sitzungspuffer, gespeicherte
Auswahl und ausdrückliche Berichte bleiben erhalten.

Vollständiger Prüfnachweis: 1.587 Tests und fünf Untertests bestanden,
einschließlich echter Qt-Konstruktion in allen vier Sprachen, Rückstellung,
Absturzlease, kritischen Anschlussklassen und Ziehauswahl. Sicherheits-,
Datenschutz- und Modulprüfungen bestanden. 414 Python-Laufzeitquellen.

Alle vier Sprachen und helle/dunkle Darstellungen sind berücksichtigt.
Tests erfolgen mit isoliertem hwmon; kein physischer Stopptest oder erzwungener
Absturz am laufenden PC. Reale Fedora-Hardwareprüfung bleibt offen.
Abschlussnachweise stehen im [Projektstatus](../project/PROJECT_STATUS.md).
