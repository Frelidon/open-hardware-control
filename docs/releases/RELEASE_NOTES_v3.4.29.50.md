# Open Hardware Control 3.4.29.50 INTERN

Diese interne Kühlungsfassung macht das globale Leistungsprofil eindeutig, bringt den sicheren Stopptest direkt an jede Gehäuselüfterkarte und erklärt den Unterschied zwischen elektrischer PWM/DC-Auswahl und der über `pwmN` regelbaren Leistung.

## Levita-Animationen

- **Orbital Ring** zeigt ein rotierendes Raumtor mit Planet und kleinem Aufklärungsschiff.
- **Neon Apex** präsentiert einen futuristischen Sportwagen auf einem cyan-/magentafarbenen Raster als vollständigen 360-Grad-Loop.
- **Quantum Core** kombiniert einen pulsierenden Energiekern mit gegenläufigen Ringen und umlaufenden Steuerpods.
- Alle drei Loops sind exakt 1600×720 Pixel groß, 10 Sekunden lang, nahtlos, stumm und als H.264/yuv420p für die bestehende Levita-Wiedergabe vorbereitet. Geometrie, Materialien und Bewegung sind projekt-eigen; es werden keine Hersteller-/Stockmedien mitgeliefert.

## Gehäuselüfter

- Die obere Kühlprofilwahl und gespeicherte Kühlprofile werden mit den Gehäuselüfterprofilen synchronisiert. **Leistung** setzt Pumpe, Radiator und alle aktiven Gehäuselüfter auf konstante 100 % statt auf eine temperaturabhängige Kurve.
- Läuft die OHC-Mainboardregelung bereits, wird die Vorgabe sofort auf alle bestätigten, einzeln aktivierten und schreibbaren Kanäle angewendet.
- Kalibrierung, Einzelaktivierung, CoolerControl-Sperre, Sensor-Fallback, Watchdog und Firmware-Rückgabe bleiben verpflichtend.
- Jede Gehäuselüfterkarte bietet **0 % / 10 s testen**. Der Nutzer bestätigt den Test vorher; OHC beobachtet die RPM und stellt anschließend den vorherigen Zustand wieder her.

## PWM und DC

- Eine echte elektrische Umschaltung bleibt ausschließlich möglich, wenn Linux für den konkreten Kanal `pwmN_mode` meldet. Sie war bereits vorhanden und verlangt weiterhin Warnbestätigung und neue Kalibrierung.
- Der auf dem Referenzsystem geladene NCT6687-Treiber meldet `pwm1` bis `pwm8`, aber kein `pwmN_mode`. Dort bestimmt das BIOS, ob der Header elektrisch als PWM oder DC arbeitet; OHC regelt anschließend den gemeldeten Duty-/DC-Wert über `pwmN`.
- OHC schreibt keine geratenen Super-I/O-Register. Die Oberfläche nennt deshalb den BIOS-Zustand offen und bietet für die praktische Lüfterzuordnung den sicheren Stopptest an.

## Prüfung und Kanal

Die reine Profilentscheidung, UI-Verkabelung, Hilfsprozessgrenzen und vorhandenen Kühlungsregressionen werden ohne dauerhafte Hardwareänderung getestet. Build-Kanal bleibt `INTERN`; kein Tag, Push oder öffentliches Release.
