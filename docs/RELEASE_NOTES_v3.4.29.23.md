# Open Hardware Control 3.4.29.23 INTERN

**Datum:** 02.09.26

Interner Zwischenstand aus der vertieften ZIP-Prüfung: Neue und beschädigte Split-Modus-Einstellungen fallen sicher auf „Aus“ zurück. Ein Levita-Livestream wird erst nach dem `QProcess.started`-Signal als aktiv gemeldet; ein Startfehler bleibt sichtbar und verwendet beim Autostart den begrenzten Wiederholungsversuch. Timer und `ffmpeg` der animierten Hover-Vorschau werden beim Beenden geschlossen.

Der Vergleichsstand enthielt nur zwei ergänzte Testdateien und keinen vollständigen `scripts/`-Ordner. Die vollständige Integration und Releaseprüfung erfolgt daher in 3.4.29.24.
