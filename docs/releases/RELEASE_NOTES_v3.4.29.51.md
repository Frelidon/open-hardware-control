# Open Hardware Control 3.4.29.51 INTERN

Datum: 08.09.2026
Kanal: INTERN
Veröffentlichung: kein GitHub-Push, Tag oder öffentliches Release

## Sprachwechsel

- Alle übersetzungspflichtigen interaktiven Texte, die beim vollständigen hardwarefreien UI-Aufbau gefunden werden, sind atomar für Deutsch, Englisch, Spanisch und Französisch gepflegt.
- Das umfasst Schaltflächen, Kontrollkästchen, Auswahlwerte, Gruppen, Reiter, Menüs, Aktionen, Tabellenköpfe und Platzhalter.
- Hervorgehobene Seiten- und Statustexte für Übersicht, Kühlung, Gehäuselüfter, Levita, RGB, Profile, Einstellungen und Hilfe wurden ergänzt.
- Dynamische Galerieangaben übersetzen ihren sichtbaren Typ oder Präfix, behalten aber persönliche Dateinamen, Zahlen und Farbwerte unverändert bei.

## Dauerhafte Absicherung

- Neue getrennte Kataloge halten Bedienelemente, Karten und längere Beschriftungen überschaubar; eine gemeinsame Richtlinie behandelt begrenzte dynamische Texte.
- `tests/test_full_ui_build_34291.py` baut die echte Oberfläche offscreen auf und verlangt für jedes relevante Bedienelement Einträge in Englisch, Spanisch und Französisch. Zusätzlich prüft er den tatsächlichen Wechsel zwischen allen vier Sprachen.
- Die KI-Anweisungen für AGENTS, Cursor, Copilot und Claude schreiben ab dieser Version vor: Jede neue oder geänderte sichtbare Funktion muss ihre Übersetzungen für alle bereits unterstützten Sprachen im selben Arbeitsschritt liefern. Der Wächtertest darf nicht abgeschwächt werden.

## Paketierung und Sicherheit

- Installer, Release-Bau, Bytecode-Prüfung und Sicherheitstest enthalten die neuen Sprachmodule.
- Technische Kennungen, gemessene Werte und Eigennamen bleiben absichtlich unverändert; Steuerlogik verwendet stabile Datenwerte statt übersetzter Anzeigetexte.
- Hardware-Schreibpfade, Besitzschutz und Sicherheitsgrenzen wurden nicht verändert.
