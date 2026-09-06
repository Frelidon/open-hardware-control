# Open Hardware Control 3.4.29.37 INTERN

Diese interne Version verbessert die beiden eigenen Levita-Weltraumlayouts und die Diagnose unplausibler Hardwarewerte.

- Das RGB-Studio bündelt Engine-Freigabe und Details direkt unter „Geräte und Effekte“, zeigt native Hardwarekanäle in einer eingebetteten Liste und bietet die Gesamthelligkeit direkt neben „Design direkt anwenden“ an.
- Ein Rechtsklick auf eine RGB-Vorlage oder einen Modus bietet genau die vom Effekt verwendeten Farben an und bewahrt die bestehende persistente Vorlagenanpassung. Abgewiesene RGB-Aufträge lassen eine ENE-Reinitialisierung nicht mehr dauerhaft als laufend stehen.
- Prozentzeichen, Temperaturen, Taktraten und Speichereinheiten bleiben in „Nebula Drift“ und „Orbital Command“ auch auf dem physischen Display sichtbar. Bereits gespeicherte OHC-Anpassungen werden automatisch korrigiert.
- Direkt über Ebene 1 und Ebene 2 stehen Intensitätsregler von 25 bis 150 Prozent. Ebene 1 wird global, Ebene 2 je Design gespeichert. Orbital Command startet bei kräftigeren 130 Prozent; Nebula Drift bleibt unverändert bei 100 Prozent.
- Der bekannte TRCC-9.9.11-Grenzbereich bei niedrigen Hz-Rohwerten bis einschließlich 1.000.000 Hz wird read-only erkannt und korrekt in MHz angezeigt. Sobald normale Werte zurückkehren, läuft wieder das dynamische Format.
- Der Log-Tab besitzt die Ansicht „Hardware · Auffälligkeiten“. Sie enthält nur neue unplausible Zustände und Erholungen, keine sekündlichen Messwertzeilen.
- Der TRCC-Daemon bleibt der einzige USB-Besitzer. Die Sicherung der zwei neuesten vollständigen Builds im externen Backup-Ordner bleibt aktiv.
