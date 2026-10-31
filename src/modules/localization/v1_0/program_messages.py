# SPDX-License-Identifier: GPL-3.0-or-later
"""Four-language strings for the Programs 1.0 inventory/profile foundation."""

_MESSAGES = {
    "de": (
        "Programme", "Installierte Programme erkennen und wiederverwendbare Installationsprofile vorbereiten.",
        "Grundordner", "Ordner auswählen …", "Programme durchsuchen …", "Installierte Programme neu laden",
        "Programmliste wurde noch nicht geladen.", "Kennung / ausführbare Datei",
        "Auswahl als Installationsprofil speichern", "Gespeicherte Installationsprofile", "Version / Kennung",
        "Ausgewähltes Profil entfernen", "Installation und GitHub-Downloads folgen in der nächsten Stufe. Diese Ansicht führt noch keine Paket- oder Netzwerkbefehle aus.",
        "Grundordner auswählen", "Installierte Programme werden im Hintergrund gelesen …", "{count} installierte Programme erkannt.",
        "Programmliste konnte nicht gelesen werden: {reason}", "Bitte zuerst ein erkanntes Programm auswählen.",
        "Installierte Programme und wiederverwendbare Installationsprofile verwalten.",
    ),
    "en": (
        "Programs", "Detect installed programs and prepare reusable installation profiles.",
        "Base folder", "Choose folder …", "Search programs …", "Reload installed programs",
        "The program list has not been loaded yet.", "Identifier / executable",
        "Save selection as installation profile", "Saved installation profiles", "Version / identifier",
        "Remove selected profile", "Installation and GitHub downloads follow in the next stage. This view does not run package or network commands yet.",
        "Choose base folder", "Installed programs are being read in the background …", "{count} installed programs detected.",
        "The program list could not be read: {reason}", "Select a detected program first.",
        "Manage installed programs and reusable installation profiles.",
    ),
    "es": (
        "Programas", "Detectar programas instalados y preparar perfiles de instalación reutilizables.",
        "Carpeta base", "Elegir carpeta …", "Buscar programas …", "Volver a cargar programas instalados",
        "La lista de programas aún no se ha cargado.", "Identificador / ejecutable",
        "Guardar selección como perfil de instalación", "Perfiles de instalación guardados", "Versión / identificador",
        "Eliminar perfil seleccionado", "La instalación y las descargas de GitHub llegarán en la siguiente fase. Esta vista aún no ejecuta comandos de paquetes ni de red.",
        "Elegir carpeta base", "Los programas instalados se están leyendo en segundo plano …", "Se detectaron {count} programas instalados.",
        "No se pudo leer la lista de programas: {reason}", "Selecciona primero un programa detectado.",
        "Gestionar programas instalados y perfiles de instalación reutilizables.",
    ),
    "fr": (
        "Programmes", "Détecter les programmes installés et préparer des profils d’installation réutilisables.",
        "Dossier de base", "Choisir un dossier …", "Rechercher des programmes …", "Recharger les programmes installés",
        "La liste des programmes n’a pas encore été chargée.", "Identifiant / exécutable",
        "Enregistrer la sélection comme profil d’installation", "Profils d’installation enregistrés", "Version / identifiant",
        "Supprimer le profil sélectionné", "L’installation et les téléchargements GitHub suivront à l’étape suivante. Cette vue n’exécute pas encore de commande de paquet ou de réseau.",
        "Choisir le dossier de base", "Les programmes installés sont lus en arrière-plan …", "{count} programmes installés détectés.",
        "Impossible de lire la liste des programmes : {reason}", "Sélectionnez d’abord un programme détecté.",
        "Gérer les programmes installés et les profils d’installation réutilisables.",
    ),
}

PROGRAM_MESSAGES = {code: dict(enumerate(messages, 2825)) for code, messages in _MESSAGES.items()}

_GITHUB_MESSAGES = {
    "de": (
        "Installationsbefehle bleiben getrennt. GitHub wird nur nach einem ausdrücklichen Prüfen- oder Download-Klick kontaktiert.",
        "GitHub-Release herunterladen", "Besitzer/Repository oder GitHub-URL",
        "Version leer lassen für neuestes Release", "Release prüfen", "Noch kein GitHub-Release geprüft.",
        "Alle Dateien und Source-Code herunterladen",
        "{count} Dateien einschließlich beider Source-Code-Archive nach {folder} herunterladen?",
        "GitHub-Anfrage läuft im Hintergrund …", "Release {tag} · {count} Dateien · gemeldete Assets {size}",
        "Release vollständig geprüft gespeichert: {folder}", "GitHub-Vorgang fehlgeschlagen: {reason}",
    ),
    "en": (
        "Installation commands remain separate. GitHub is contacted only after an explicit Check or Download click.",
        "Download GitHub release", "Owner/repository or GitHub URL",
        "Leave version empty for latest release", "Check release", "No GitHub release checked yet.",
        "Download all files and source code",
        "Download {count} files including both source archives to {folder}?",
        "GitHub request is running in the background …", "Release {tag} · {count} files · reported assets {size}",
        "Release saved and fully verified: {folder}", "GitHub operation failed: {reason}",
    ),
    "es": (
        "Los comandos de instalación permanecen separados. GitHub solo se contacta tras pulsar explícitamente Comprobar o Descargar.",
        "Descargar versión de GitHub", "Propietario/repositorio o URL de GitHub",
        "Dejar la versión vacía para la última", "Comprobar versión", "Aún no se ha comprobado ninguna versión de GitHub.",
        "Descargar todos los archivos y el código fuente",
        "¿Descargar {count} archivos, incluidos ambos archivos de código fuente, en {folder}?",
        "La solicitud de GitHub se ejecuta en segundo plano …", "Versión {tag} · {count} archivos · recursos declarados {size}",
        "Versión guardada y verificada por completo: {folder}", "La operación de GitHub ha fallado: {reason}",
    ),
    "fr": (
        "Les commandes d’installation restent séparées. GitHub n’est contacté qu’après un clic explicite sur Vérifier ou Télécharger.",
        "Télécharger la version GitHub", "Propriétaire/dépôt ou URL GitHub",
        "Laisser la version vide pour la dernière", "Vérifier la version", "Aucune version GitHub encore vérifiée.",
        "Télécharger tous les fichiers et le code source",
        "Télécharger {count} fichiers, dont les deux archives source, dans {folder} ?",
        "La requête GitHub s’exécute en arrière-plan …", "Version {tag} · {count} fichiers · ressources déclarées {size}",
        "Version enregistrée et entièrement vérifiée : {folder}", "Échec de l’opération GitHub : {reason}",
    ),
}

for _code, _messages in _GITHUB_MESSAGES.items():
    PROGRAM_MESSAGES[_code].update(enumerate(_messages, 2844))

_INSTALL_MESSAGES = {
    "de": (
        "App-ID, Snap-Name oder AppImage-Pfad", "Flatpak-Branch oder Snap-Channel (optional)",
        "Profil hinzufügen", "Ausgewähltes Profil installieren", "Keine Installation aktiv.",
        "Profilname und Programmkennung sind erforderlich.", "Das Installationsprofil ist ungültig.",
        "Bitte zuerst ein Installationsprofil auswählen.", "Installation nicht möglich", "Installation bestätigen",
        "Diesen geprüften Plan jetzt ausführen?\n\n{summary}\n\nBefehl: {command}",
        "Installation fehlgeschlagen: {reason}", "AppImage wurde für den aktuellen Benutzer ausführbar gemacht.",
        "Installation läuft …", "Installation abgeschlossen.", "Installation konnte nicht gestartet werden: {reason}",
        "Die Programmkennung enthält ungültige Zeichen.", "Flatpak ist auf diesem System nicht verfügbar.",
        "Der Flatpak-Branch ist ungültig.", "Snap und Polkit sind für diese Installation erforderlich.",
        "Der Snap-Channel ist ungültig.", "Das AppImage muss im gewählten Grundordner liegen.",
        "Die gewählte Datei ist kein reguläres AppImage.", "Die AppImage-Größe liegt außerhalb der Sicherheitsgrenze.",
        "Die Datei besitzt keinen erkannten AppImage-Kopf.",
        "Systempakete werden ohne bestätigte distributionsspezifische Paketquelle nicht automatisch installiert.",
        "Dies ist kein AppImage-Plan.",
    ),
    "en": (
        "App ID, snap name or AppImage path", "Flatpak branch or snap channel (optional)",
        "Add profile", "Install selected profile", "No installation active.",
        "Profile name and program identifier are required.", "The installation profile is invalid.",
        "Select an installation profile first.", "Installation unavailable", "Confirm installation",
        "Run this verified plan now?\n\n{summary}\n\nCommand: {command}",
        "Installation failed: {reason}", "The AppImage was made executable for the current user.",
        "Installation running …", "Installation completed.", "Installation could not be started: {reason}",
        "The program identifier contains invalid characters.", "Flatpak is not available on this system.",
        "The Flatpak branch is invalid.", "Snap and Polkit are required for this installation.",
        "The snap channel is invalid.", "The AppImage must be inside the selected base folder.",
        "The selected file is not a regular AppImage.", "The AppImage size is outside the safety limit.",
        "The file has no recognized AppImage header.",
        "System packages are not installed automatically without a confirmed distribution-specific package source.",
        "This is not an AppImage plan.",
    ),
    "es": (
        "ID de app, nombre snap o ruta AppImage", "Rama Flatpak o canal snap (opcional)",
        "Añadir perfil", "Instalar perfil seleccionado", "No hay ninguna instalación activa.",
        "Se requieren el nombre del perfil y el identificador del programa.", "El perfil de instalación no es válido.",
        "Selecciona primero un perfil de instalación.", "Instalación no disponible", "Confirmar instalación",
        "¿Ejecutar ahora este plan verificado?\n\n{summary}\n\nComando: {command}",
        "La instalación ha fallado: {reason}", "El AppImage se hizo ejecutable para el usuario actual.",
        "Instalación en curso …", "Instalación completada.", "No se pudo iniciar la instalación: {reason}",
        "El identificador del programa contiene caracteres no válidos.", "Flatpak no está disponible en este sistema.",
        "La rama Flatpak no es válida.", "Se requieren Snap y Polkit para esta instalación.",
        "El canal snap no es válido.", "El AppImage debe estar dentro de la carpeta base seleccionada.",
        "El archivo seleccionado no es un AppImage normal.", "El tamaño del AppImage supera el límite de seguridad.",
        "El archivo no tiene una cabecera AppImage reconocida.",
        "Los paquetes del sistema no se instalan automáticamente sin una fuente específica de la distribución confirmada.",
        "Este no es un plan AppImage.",
    ),
    "fr": (
        "ID d’application, nom snap ou chemin AppImage", "Branche Flatpak ou canal snap (facultatif)",
        "Ajouter le profil", "Installer le profil sélectionné", "Aucune installation active.",
        "Le nom du profil et l’identifiant du programme sont requis.", "Le profil d’installation est invalide.",
        "Sélectionnez d’abord un profil d’installation.", "Installation indisponible", "Confirmer l’installation",
        "Exécuter ce plan vérifié maintenant ?\n\n{summary}\n\nCommande : {command}",
        "Échec de l’installation : {reason}", "L’AppImage a été rendu exécutable pour l’utilisateur actuel.",
        "Installation en cours …", "Installation terminée.", "Impossible de démarrer l’installation : {reason}",
        "L’identifiant du programme contient des caractères non valides.", "Flatpak n’est pas disponible sur ce système.",
        "La branche Flatpak est invalide.", "Snap et Polkit sont requis pour cette installation.",
        "Le canal snap est invalide.", "L’AppImage doit se trouver dans le dossier de base sélectionné.",
        "Le fichier sélectionné n’est pas un AppImage régulier.", "La taille de l’AppImage dépasse la limite de sécurité.",
        "Le fichier ne possède pas d’en-tête AppImage reconnu.",
        "Les paquets système ne sont pas installés automatiquement sans source propre à la distribution confirmée.",
        "Ce plan n’est pas un plan AppImage.",
    ),
}

for _code, _messages in _INSTALL_MESSAGES.items():
    PROGRAM_MESSAGES[_code].update(enumerate(_messages, 2856))

for _code in PROGRAM_MESSAGES:
    PROGRAM_MESSAGES[_code].update({2883: "Flatpak", 2884: "Snap", 2885: "AppImage"})

for _code, _messages in {
    "de": ("GitHub-Projekt", "GitHub-Projekt zuordnen", "GitHub-Projekt {repository} wurde dem Profil zugeordnet."),
    "en": ("GitHub project", "Assign GitHub project", "GitHub project {repository} was assigned to the profile."),
    "es": ("Proyecto de GitHub", "Asignar proyecto de GitHub", "El proyecto de GitHub {repository} se asignó al perfil."),
    "fr": ("Projet GitHub", "Associer le projet GitHub", "Le projet GitHub {repository} a été associé au profil."),
}.items():
    PROGRAM_MESSAGES[_code].update(enumerate(_messages, 2886))

for _code, _messages in {
    "de": (
        "Heruntergeladenes AppImage", "Kein heruntergeladenes AppImage verfügbar",
        "AppImage dem ausgewählten Profil zuweisen", "Bitte zuerst ein AppImage-Profil auswählen.",
        "Das ausgewählte AppImage wurde dem Profil zugeordnet.",
    ),
    "en": (
        "Downloaded AppImage", "No downloaded AppImage available",
        "Assign AppImage to selected profile", "Select an AppImage profile first.",
        "The selected AppImage was assigned to the profile.",
    ),
    "es": (
        "AppImage descargado", "No hay ningún AppImage descargado disponible",
        "Asignar AppImage al perfil seleccionado", "Selecciona primero un perfil AppImage.",
        "El AppImage seleccionado se asignó al perfil.",
    ),
    "fr": (
        "AppImage téléchargée", "Aucune AppImage téléchargée disponible",
        "Associer l’AppImage au profil sélectionné", "Sélectionnez d’abord un profil AppImage.",
        "L’AppImage sélectionnée a été associée au profil.",
    ),
}.items():
    PROGRAM_MESSAGES[_code].update(enumerate(_messages, 2889))
