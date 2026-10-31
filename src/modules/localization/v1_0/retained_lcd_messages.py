# SPDX-License-Identifier: GPL-3.0-or-later
"""Retained multilingual UI data and additive release fixes."""

RETAINED_LCD_MESSAGES = {code: {} for code in ("de", "en", "es", "fr")}

for _code, _messages in {
    "de": (
        "OHC Originale",
        "Eigenständige, langsam driftende Prismengitter mit viel ruhiger Fläche für Sensordaten.",
        "Zwei abstrakte Lichtwesen kreisen gegenläufig um einen freien Datenkern – ohne Markenmotiv.",
        "Organische Neonpartikel wachsen, schweben und verlöschen in einem nahtlosen Zyklus.",
        "Ein eigener Energie-Kurier jagt durch ein verzweigtes Leiterbahn-Labyrinth; keine Figur oder Grafik eines Spiels wird verwendet.",
        "Circuit Chase", "Neon Particle Garden", "Prism Drift", "Twin Wyrm Orbit",
    ),
    "en": (
        "OHC originals",
        "Original, slowly drifting prism grids leave ample calm space for sensor data.",
        "Two abstract light creatures orbit a clear data core in opposite directions, without a branded motif.",
        "Organic neon particles grow, float, and fade in a seamless cycle.",
        "An original energy courier races through a branching circuit maze; no game character or artwork is used.",
        "Circuit Chase", "Neon Particle Garden", "Prism Drift", "Twin Wyrm Orbit",
    ),
    "es": (
        "Originales OHC",
        "Retículas de prismas originales derivan lentamente y dejan amplio espacio tranquilo para los datos de sensores.",
        "Dos criaturas abstractas de luz orbitan un núcleo de datos libre en direcciones opuestas, sin motivos de marca.",
        "Partículas de neón orgánicas crecen, flotan y se desvanecen en un ciclo continuo.",
        "Un mensajero de energía original recorre un laberinto de circuitos ramificados; no se usa ningún personaje ni gráfico de un juego.",
        "Circuit Chase", "Neon Particle Garden", "Prism Drift", "Twin Wyrm Orbit",
    ),
    "fr": (
        "Créations OHC",
        "Des grilles de prismes originales dérivent lentement et laissent un vaste espace calme aux données des capteurs.",
        "Deux créatures lumineuses abstraites gravitent en sens opposés autour d’un noyau de données libre, sans motif de marque.",
        "Des particules de néon organiques grandissent, flottent et s’éteignent dans un cycle continu.",
        "Un coursier d’énergie original traverse un labyrinthe de circuits ramifiés ; aucun personnage ni visuel de jeu n’est utilisé.",
        "Circuit Chase", "Neon Particle Garden", "Prism Drift", "Twin Wyrm Orbit",
    ),
}.items():
    RETAINED_LCD_MESSAGES[_code].update(enumerate(_messages, 2100))

for _code, _messages in {
    'de': ('Noch kein Programm ausgewählt', 'Programme verwalten …', 'Programme für die Spielerkennung', 'Manager schließen', 'Installierte oder gerade laufende Programme auswählen. Alternativ kann ein ausführbarer Pfad angegeben werden.', 'Programmliste durchsuchen …', 'Programmliste neu laden', 'Ausgewähltes Programm hinzufügen', 'Pfad oder Prozessname', 'Pfad auswählen …', 'Pfad hinzufügen', 'Aktive Programmauswahl', 'Ausgewähltes Programm entfernen', 'läuft gerade', 'installiert', 'Ausführbares Programm auswählen', 'LCD-Zuständigkeit liegt nicht bei OHC · keine Übertragung gestartet', 'LCD-Zuständigkeit liegt nicht bei OHC · kein Display-Test gestartet', 'Keine zusätzlichen Spiele ausgewählt', 'Spiele-Programmliste verwalten …', 'Vollbildanwendungen erkennen', 'Rahmenlose Vollbildfenster erkennen', 'zuletzt erkannt', 'Wiedergabe noch nicht geprüft', 'Design übertragen · Wiedergabeprüfung folgt automatisch', 'Wiedergabe nicht bestätigt · zweite Prüfung folgt in 5 Sekunden', 'Rahmenloses Vollbildfenster'),
    'en': ('No program selected yet', 'Manage programs …', 'Programs for game detection', 'Close manager', 'Select installed or currently running programs. Alternatively, enter an executable path.', 'Search program list …', 'Reload program list', 'Add selected program', 'Path or process name', 'Choose path …', 'Add path', 'Active program selection', 'Remove selected program', 'currently running', 'installed', 'Select executable program', 'LCD authority is not assigned to OHC · no transfer started', 'LCD authority is not assigned to OHC · no display test started', 'No additional games selected', 'Manage game program list …', 'Detect full-screen applications', 'Detect borderless full-screen windows', 'recently detected', 'Playback not checked yet', 'Design transferred · playback check will follow automatically', 'Playback not confirmed · a second check follows in 5 seconds', 'Borderless full-screen window'),
    'es': ('Aún no hay ningún programa seleccionado', 'Gestionar programas …', 'Programas para detectar juegos', 'Cerrar gestor', 'Selecciona programas instalados o en ejecución. También puedes indicar la ruta de un ejecutable.', 'Buscar en la lista de programas …', 'Recargar lista de programas', 'Añadir programa seleccionado', 'Ruta o nombre del proceso', 'Seleccionar ruta …', 'Añadir ruta', 'Selección de programas activa', 'Quitar programa seleccionado', 'en ejecución', 'instalado', 'Seleccionar programa ejecutable', 'El control del LCD no corresponde a OHC · no se inició la transferencia', 'El control del LCD no corresponde a OHC · no se inició la prueba', 'No hay juegos adicionales seleccionados', 'Gestionar lista de programas de juegos …', 'Detectar aplicaciones a pantalla completa', 'Detectar ventanas sin bordes a pantalla completa', 'detectado recientemente', 'La reproducción aún no se ha comprobado', 'Diseño transferido · la comprobación de reproducción se hará automáticamente', 'Reproducción no confirmada · habrá una segunda comprobación en 5 segundos', 'Ventana a pantalla completa sin bordes'),
    'fr': ('Aucun programme sélectionné', 'Gérer les programmes …', 'Programmes pour la détection des jeux', 'Fermer le gestionnaire', 'Sélectionnez des programmes installés ou en cours d’exécution. Vous pouvez aussi indiquer le chemin d’un exécutable.', 'Rechercher dans la liste des programmes …', 'Recharger la liste des programmes', 'Ajouter le programme sélectionné', 'Chemin ou nom du processus', 'Choisir le chemin …', 'Ajouter le chemin', 'Sélection active de programmes', 'Retirer le programme sélectionné', 'en cours d’exécution', 'installé', 'Sélectionner un programme exécutable', 'Le contrôle LCD n’est pas attribué à OHC · aucun transfert lancé', 'Le contrôle LCD n’est pas attribué à OHC · aucun test d’écran lancé', 'Aucun jeu supplémentaire sélectionné', 'Gérer la liste des programmes de jeux …', 'Détecter les applications en plein écran', 'Détecter les fenêtres plein écran sans bordure', 'détecté récemment', 'Lecture pas encore vérifiée', 'Design transféré · la lecture sera vérifiée automatiquement', 'Lecture non confirmée · une deuxième vérification aura lieu dans 5 secondes', 'Fenêtre plein écran sans bordure'),
}.items():
    RETAINED_LCD_MESSAGES[_code].update(enumerate(_messages, 2200))
