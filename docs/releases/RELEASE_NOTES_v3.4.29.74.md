# Open Hardware Control 3.4.29.74 INTERN

Interner Linux-Teststand vom 12. September 2026. Kein GitHub-Tag und kein öffentliches Release.

## Hauptbildschirm unter KDE/Wayland

- Der gelieferte 3.4.29.73-Log und die lokale KWin-Ausgangskonfiguration stimmen überein: `DP-1` ist der 3440×1440-Hauptbildschirm bei `1920,0`, und OHC hatte eine passende Geometrie angefordert. Damit lag die verbleibende Abweichung nach der OHC-Auswahl im ersten Compositor-Mapping.
- OHC bildet das Fenster nun zunächst im normalen Zustand auf dem ausgewählten Bildschirm ab. Ein gespeicherter maximierter Zustand wird erst im folgenden Qt-Ereigniszyklus angewendet, damit KWin den richtigen Ausgang aus der Normalposition ableiten kann.
- 350 ms nach dem sichtbaren Mapping vergleicht OHC den tatsächlich beobachteten Bildschirm mit dem gespeicherten Ziel. Nur bei einer Abweichung wird die vorhandene sichere Platzierung einmalig erneut ausgeführt.
- Die Diagnose meldet danach entweder den bestätigten Bildschirm und die Geometrie oder Ziel, Ist-Bildschirm und die erfolgte Nachkorrektur. Dadurch zeigt ein neuer Log nicht mehr nur den ursprünglichen Platzierungswunsch.
- Beim Öffnen aus dem Infobereich wird ein minimiertes Fenster zuerst normal sichtbar gemacht und erst danach auf den Zielmonitor gesetzt und bestätigt.

## Grenzen

- OHC führt keine dauerhafte Bildschirmkorrektur aus und verschiebt das Fenster nicht gegen spätere bewusste Benutzerbewegungen.
- Hardware-, Profil-, LCD-, RGB- und Kühlungspfade wurden nicht verändert.
- Die Korrektur ist mit simulierten Mehrmonitorobjekten und im vollständigen Offscreen-UI prüfbar. Das reale Discover-/KWin-Verhalten muss nach Installation des RPM erneut bestätigt werden.
