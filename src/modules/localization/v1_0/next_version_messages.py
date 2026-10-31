# SPDX-License-Identifier: GPL-3.0-or-later
"""Four-language data for the measured case-space and compact GPU/RGB UI."""

from __future__ import annotations


NEXT_VERSION_MESSAGES = {
    "de": dict(enumerate(
        "Räumliche Abstände und Tiefe§Nur selbst gemessene Werte werden gespeichert. Sie ändern weder PWM- noch RGB-Zuordnungen.§Direkter Abstand§Tiefe§Millimeter§Inch§Messart§Von Lüfter / Komponente§Zu Lüfter / Komponente§Abstand§Abstand speichern§Ausgewählten Abstand löschen§Abstand gespeichert.§Bitte zwei unterschiedliche Komponenten und einen gültigen Abstand wählen.§Räumlichen Ablauf einstellen§Eigenes GPU-Bild importieren§GPU-Bild zurücksetzen§GPU-Last-Kurztest läuft · LACT stellt die Änderung automatisch zurück.§GPU-Lüfter-Kurztest läuft · ohne Grafiklast; LACT stellt die Änderung automatisch zurück.§Weitere Aktionen§Nur testen§Testen + anwenden§Getestet speichern§CoolerControl: GPU-Lüfter muss dort „Unmanaged“ sein.§Test§Räumliche Laufrichtung§Räumlichen Ablauf speichern§LED- und Lüfterreihenfolge bearbeiten§Die Reihenfolge wird am gewählten Komponentenblock anhand des echten LED-Verlaufs festgelegt.§Räumlicher Ablauf gespeichert.§TRCC Linux für Thermalright-LCD installieren§TRCC Linux für diese Distribution anhand der offiziellen Anleitung installieren.§Das TRCC-Installationsskript fehlt.§TRCC-Linux-Installation konnte nicht geprüft werden: {reason}§TRCC Linux ist bereits installiert.§TRCC Linux 9.10.4 aus dem offiziellen Projektpaket installieren? Administratorrechte sind erforderlich.§TRCC Linux wurde installiert. Die LCD-Bibliothek wird neu geladen.§TRCC-Linux-Installation fehlgeschlagen: {reason}".split("§"), 1808
    )),
    "en": dict(enumerate(
        "Spatial distances and depth§Only values you measure yourself are saved. They do not change PWM or RGB assignments.§Direct distance§Depth§Millimetres§Inches§Measurement type§From fan / component§To fan / component§Distance§Save distance§Delete selected distance§Distance saved.§Select two different components and enter a valid distance.§Configure spatial flow§Import custom GPU image§Reset GPU image§GPU load trial running · LACT automatically reverts the change.§GPU fan trial running · without graphics load; LACT automatically reverts the change.§More actions§Test only§Test + apply§Save tested§CoolerControl: Set the GPU fan to “Unmanaged” there.§Test§Spatial travel direction§Save spatial flow§Edit LED and fan order§The order is defined on the selected component block using its actual LED path.§Spatial flow saved.§Install TRCC Linux for the Thermalright LCD§Install TRCC Linux for this distribution using the official guide.§The TRCC installation script is missing.§The TRCC Linux installation could not be checked: {reason}§TRCC Linux is already installed.§Install TRCC Linux 9.10.4 from the official project package? Administrator privileges are required.§TRCC Linux was installed. The LCD library will be reloaded.§TRCC Linux installation failed: {reason}".split("§"), 1808
    )),
    "es": dict(enumerate(
        "Distancias espaciales y profundidad§Solo se guardan los valores medidos por ti. No cambian las asignaciones PWM ni RGB.§Distancia directa§Profundidad§Milímetros§Pulgadas§Tipo de medición§Desde ventilador / componente§Hasta ventilador / componente§Distancia§Guardar distancia§Eliminar distancia seleccionada§Distancia guardada.§Selecciona dos componentes distintos e introduce una distancia válida.§Configurar recorrido espacial§Importar imagen propia de GPU§Restablecer imagen de GPU§Prueba breve de carga de GPU en curso · LACT revierte el cambio automáticamente.§Prueba breve del ventilador de GPU en curso · sin carga gráfica; LACT revierte el cambio automáticamente.§Más acciones§Solo probar§Probar + aplicar§Guardar probado§CoolerControl: configura allí el ventilador de la GPU como «Unmanaged».§Prueba§Dirección del recorrido espacial§Guardar recorrido espacial§Editar orden de LED y ventiladores§El orden se define en el bloque de componentes seleccionado mediante su recorrido LED real.§Recorrido espacial guardado.§Instalar TRCC Linux para la pantalla LCD Thermalright§Instala TRCC Linux para esta distribución siguiendo la guía oficial.§Falta el script de instalación de TRCC.§No se pudo comprobar la instalación de TRCC Linux: {reason}§TRCC Linux ya está instalado.§¿Instalar TRCC Linux 9.10.4 desde el paquete oficial del proyecto? Se requieren privilegios de administrador.§TRCC Linux se ha instalado. Se volverá a cargar la biblioteca LCD.§La instalación de TRCC Linux ha fallado: {reason}".split("§"), 1808
    )),
    "fr": dict(enumerate(
        "Distances spatiales et profondeur§Seules les valeurs que vous mesurez sont enregistrées. Elles ne modifient aucune affectation PWM ou RGB.§Distance directe§Profondeur§Millimètres§Pouces§Type de mesure§Du ventilateur / composant§Au ventilateur / composant§Distance§Enregistrer la distance§Supprimer la distance sélectionnée§Distance enregistrée.§Sélectionnez deux composants différents et saisissez une distance valide.§Configurer le parcours spatial§Importer une image GPU personnalisée§Réinitialiser l’image GPU§Test bref de charge GPU en cours · LACT rétablit automatiquement la modification.§Test bref du ventilateur GPU en cours · sans charge graphique ; LACT rétablit automatiquement la modification.§Autres actions§Tester seulement§Tester + appliquer§Enregistrer le test§CoolerControl : réglez-y le ventilateur GPU sur « Unmanaged ».§Test§Direction du parcours spatial§Enregistrer le parcours spatial§Modifier l’ordre des LED et ventilateurs§L’ordre est défini sur le bloc de composants sélectionné à partir de son parcours LED réel.§Parcours spatial enregistré.§Installer TRCC Linux pour l’écran LCD Thermalright§Installez TRCC Linux pour cette distribution à l’aide du guide officiel.§Le script d’installation de TRCC est manquant.§Impossible de vérifier l’installation de TRCC Linux : {reason}§TRCC Linux est déjà installé.§Installer TRCC Linux 9.10.4 depuis le paquet officiel du projet ? Des droits administrateur sont nécessaires.§TRCC Linux a été installé. La bibliothèque LCD va être rechargée.§Échec de l’installation de TRCC Linux : {reason}".split("§"), 1808
    )),
}

for _code, _messages in {
    "de": ("TRCC-Katalog", "Eigene TRCC-Dateien"),
    "en": ("TRCC catalog", "Custom TRCC files"),
    "es": ("Catálogo TRCC", "Archivos TRCC propios"),
    "fr": ("Catalogue TRCC", "Fichiers TRCC personnalisés"),
}.items():
    NEXT_VERSION_MESSAGES[_code].update(enumerate(_messages, 1846))

for _code, _messages in {
    "de": (
        "Open Hardware Control neu starten",
        "Open Hardware Control wird kontrolliert beendet und danach automatisch wieder geöffnet. Fortfahren?",
        "Der sichere Programmneustart konnte nicht vorbereitet werden.",
    ),
    "en": (
        "Restart Open Hardware Control",
        "Open Hardware Control will shut down cleanly and then open again automatically. Continue?",
        "The safe application restart could not be prepared.",
    ),
    "es": (
        "Reiniciar Open Hardware Control",
        "Open Hardware Control se cerrará de forma controlada y después se abrirá de nuevo automáticamente. ¿Continuar?",
        "No se pudo preparar el reinicio seguro de la aplicación.",
    ),
    "fr": (
        "Redémarrer Open Hardware Control",
        "Open Hardware Control va s’arrêter proprement puis se rouvrir automatiquement. Continuer ?",
        "Le redémarrage sécurisé de l’application n’a pas pu être préparé.",
    ),
}.items():
    NEXT_VERSION_MESSAGES[_code].update(enumerate(_messages, 1848))

for _code, _messages in {
    "de": (
        "RGB-START UND WIEDERAUFNAHME", "Keins", "Zuletzt verwendet", "Nicht mehr vorhanden",
        "EIN", "AUS", "STARTET …", "bestätigt", "noch nicht bestätigt",
        "Startprofil: {profile} · Automatik: {autostart} · Wiederaufnahme: {reclaim} · RGB-Steuerung: {control} ({consent})",
        "Eigene LCD-Designs · Quellen und Dateien", "LCD-Designmanager öffnen", "Auswahl laden",
        "OpenRGB-Profile importieren", "OpenRGB-Profil importieren", "Profil vollständig laden",
        "OpenRGB-Profile (*.orp *.json)", "iCUE NEXUS · OHC-Designmanager",
        "Design / Paket importieren", "Auf NEXUS anzeigen", "NEXUS-Design importieren",
        "NEXUS-Designs (*.png *.jpg *.jpeg *.webp *.json)", "NEXUS-Design übernehmen",
        "Bitte zuerst NEXUS-Gerät und Design auswählen.",
    ),
    "en": (
        "RGB START AND RESUME", "None", "Last used", "No longer available",
        "ON", "OFF", "STARTING …", "confirmed", "not confirmed yet",
        "Startup profile: {profile} · Automation: {autostart} · Resume: {reclaim} · RGB control: {control} ({consent})",
        "Custom LCD designs · sources and files", "Open LCD design manager", "Load selection",
        "Import OpenRGB profiles", "Import OpenRGB profile", "Load full profile",
        "OpenRGB profiles (*.orp *.json)", "iCUE NEXUS · OHC design manager",
        "Import design / package", "Show on NEXUS", "Import NEXUS design",
        "NEXUS designs (*.png *.jpg *.jpeg *.webp *.json)", "Add NEXUS design",
        "Select a NEXUS device and design first.",
    ),
    "es": (
        "INICIO Y REANUDACIÓN RGB", "Ninguno", "Último utilizado", "Ya no está disponible",
        "ACTIVADO", "DESACTIVADO", "INICIANDO …", "confirmado", "aún sin confirmar",
        "Perfil de inicio: {profile} · Automatización: {autostart} · Reanudación: {reclaim} · Control RGB: {control} ({consent})",
        "Diseños LCD propios · fuentes y archivos", "Abrir gestor de diseños LCD", "Cargar selección",
        "Importar perfiles OpenRGB", "Importar perfil OpenRGB", "Cargar perfil completo",
        "Perfiles OpenRGB (*.orp *.json)", "iCUE NEXUS · gestor de diseños OHC",
        "Importar diseño / paquete", "Mostrar en NEXUS", "Importar diseño NEXUS",
        "Diseños NEXUS (*.png *.jpg *.jpeg *.webp *.json)", "Añadir diseño NEXUS",
        "Selecciona primero un dispositivo NEXUS y un diseño.",
    ),
    "fr": (
        "DÉMARRAGE ET REPRISE RGB", "Aucun", "Dernier utilisé", "N’est plus disponible",
        "ACTIVÉ", "DÉSACTIVÉ", "DÉMARRAGE…", "confirmé", "pas encore confirmé",
        "Profil de démarrage : {profile} · Automatisation : {autostart} · Reprise : {reclaim} · Contrôle RGB : {control} ({consent})",
        "Designs LCD personnalisés · sources et fichiers", "Ouvrir le gestionnaire de designs LCD", "Charger la sélection",
        "Importer des profils OpenRGB", "Importer un profil OpenRGB", "Charger le profil complet",
        "Profils OpenRGB (*.orp *.json)", "iCUE NEXUS · gestionnaire de designs OHC",
        "Importer un design / paquet", "Afficher sur NEXUS", "Importer un design NEXUS",
        "Designs NEXUS (*.png *.jpg *.jpeg *.webp *.json)", "Ajouter le design NEXUS",
        "Sélectionnez d’abord un appareil NEXUS et un design.",
    ),
}.items():
    NEXT_VERSION_MESSAGES[_code].update(enumerate(_messages, 1851))

for _code, _messages in {
    "de": (
        "Status prüfen", "Für Ubuntu aktivieren", "Für Fedora aktivieren", "Desktop-VRR einrichten",
        "VRR im Spiel testen", "Ubuntu-Automatik installieren / übernehmen", "Automatik deaktivieren",
        "Fix deinstallieren", "Auswahl anwenden", "Details / Protokoll", "Hardware-Prüfung",
        "Unterstützter Monitor: MSI MAG 274QPF X30MV", "Anbieter auswählen",
    ),
    "en": (
        "Check status", "Enable for Ubuntu", "Enable for Fedora", "Set up desktop VRR",
        "Test VRR in a game", "Install / adopt Ubuntu automation", "Disable automation",
        "Uninstall fix", "Apply selection", "Details / log", "Hardware check",
        "Supported monitor: MSI MAG 274QPF X30MV", "Select provider",
    ),
    "es": (
        "Comprobar estado", "Activar para Ubuntu", "Activar para Fedora", "Configurar VRR del escritorio",
        "Probar VRR en un juego", "Instalar / adoptar automatización de Ubuntu", "Desactivar automatización",
        "Desinstalar corrección", "Aplicar selección", "Detalles / registro", "Comprobación de hardware",
        "Monitor compatible: MSI MAG 274QPF X30MV", "Seleccionar proveedor",
    ),
    "fr": (
        "Vérifier l’état", "Activer pour Ubuntu", "Activer pour Fedora", "Configurer le VRR du bureau",
        "Tester le VRR dans un jeu", "Installer / reprendre l’automatisation Ubuntu", "Désactiver l’automatisation",
        "Désinstaller le correctif", "Appliquer la sélection", "Détails / journal", "Vérification du matériel",
        "Écran pris en charge : MSI MAG 274QPF X30MV", "Sélectionner le fournisseur",
    ),
}.items():
    NEXT_VERSION_MESSAGES[_code].update(enumerate(_messages, 1875))

for _code, _messages in {
    "de": (
        "1 · Passende Treiberbefehle kopieren", "Erkannte Distribution", "Erkanntes Mainboard", "Distribution nicht unterstützt",
        "Für diese Distribution gibt es keinen festen Installationsbefehl. Unterstützt werden Fedora, Ubuntu und Arch Linux.",
        "Die zustandsfesten Befehle für {distribution} wurden kopiert. Führe sie der Reihe nach aus; ein vorhandener Git-Checkout wird aktualisiert. Behebe gemeldete fehlerhafte Paketquellen separat und kehre danach für die MOK-Schritte hierher zurück.",
        "Arch Linux: linux-headers gilt für den Standardkernel. Bei linux-lts oder linux-zen muss das passende Headerpaket verwendet werden.",
    ),
    "en": (
        "1 · Copy matching driver commands", "Detected distribution", "Detected mainboard", "Distribution not supported",
        "There is no fixed installation command for this distribution. Fedora, Ubuntu and Arch Linux are supported.",
        "The state-aware commands for {distribution} were copied. Run them in order; an existing Git checkout is updated. Fix reported broken package sources separately, then return here for the MOK steps.",
        "Arch Linux: linux-headers applies to the default kernel. Use the matching header package for linux-lts or linux-zen.",
    ),
    "es": (
        "1 · Copiar comandos de controlador adecuados", "Distribución detectada", "Placa base detectada", "Distribución no compatible",
        "No hay un comando de instalación fijo para esta distribución. Se admiten Fedora, Ubuntu y Arch Linux.",
        "Se copiaron los comandos adaptados al estado para {distribution}. Ejecútalos en orden; se actualizará un checkout Git existente. Corrige por separado las fuentes de paquetes defectuosas y después vuelve aquí para los pasos de MOK.",
        "Arch Linux: linux-headers corresponde al kernel estándar. Para linux-lts o linux-zen debe usarse el paquete de cabeceras correspondiente.",
    ),
    "fr": (
        "1 · Copier les commandes de pilote adaptées", "Distribution détectée", "Carte mère détectée", "Distribution non prise en charge",
        "Il n’existe aucune commande d’installation fixe pour cette distribution. Fedora, Ubuntu et Arch Linux sont pris en charge.",
        "Les commandes adaptées à l’état pour {distribution} ont été copiées. Exécutez-les dans l’ordre ; un checkout Git existant sera actualisé. Corrigez séparément les sources de paquets défectueuses, puis revenez ici pour les étapes MOK.",
        "Arch Linux : linux-headers s’applique au noyau standard. Pour linux-lts ou linux-zen, utilisez le paquet d’en-têtes correspondant.",
    ),
}.items():
    NEXT_VERSION_MESSAGES[_code].update(enumerate(_messages, 1888))

for _code, _messages in {
    "de": (
        "5 · Dauerhafte Lüfterberechtigung",
        "Ubuntu: Paketlisten-Aktualisierung und Paketinstallation sind getrennte Schritte. Eine fehlerhafte Fremdquelle wird gemeldet, aber OHC verändert sie nicht automatisch.",
        "Die dauerhafte Lüfterfreigabe ist aktiv und bleibt bei OHC-Updates sowie Neustarts erhalten.",
        "Richte die optionale Dauerfreigabe einmalig ein. Sie gilt nur für den begrenzten NCT6687-Lüfterhelfer; Paketinstallationen bleiben normale Administratoraktionen.",
        "Dauerhafte Lüfterberechtigung",
        "Die Dauerfreigabe kann nur aus dem Hauptfenster von Open Hardware Control eingerichtet werden.",
    ),
    "en": (
        "5 · Persistent fan authorization",
        "Ubuntu: Package-list refresh and package installation are separate steps. A broken third-party source is reported, but OHC does not change it automatically.",
        "Persistent fan authorization is active and remains in place across OHC updates and restarts.",
        "Set up the optional persistent authorization once. It applies only to the restricted NCT6687 fan helper; package installation remains a normal administrator action.",
        "Persistent fan authorization",
        "Persistent authorization can only be configured from the Open Hardware Control main window.",
    ),
    "es": (
        "5 · Autorización permanente de ventiladores",
        "Ubuntu: La actualización de listas y la instalación de paquetes son pasos separados. Se informa de una fuente externa defectuosa, pero OHC no la modifica automáticamente.",
        "La autorización permanente de ventiladores está activa y se conserva tras actualizaciones y reinicios de OHC.",
        "Configura una vez la autorización permanente opcional. Solo se aplica al ayudante limitado de ventiladores NCT6687; la instalación de paquetes sigue siendo una acción de administrador normal.",
        "Autorización permanente de ventiladores",
        "La autorización permanente solo puede configurarse desde la ventana principal de Open Hardware Control.",
    ),
    "fr": (
        "5 · Autorisation permanente des ventilateurs",
        "Ubuntu : l’actualisation des listes et l’installation des paquets sont des étapes séparées. Une source tierce défectueuse est signalée, mais OHC ne la modifie pas automatiquement.",
        "L’autorisation permanente des ventilateurs est active et reste valable après les mises à jour et redémarrages d’OHC.",
        "Configurez une fois l’autorisation permanente facultative. Elle s’applique uniquement à l’assistant NCT6687 restreint ; l’installation de paquets reste une action d’administration normale.",
        "Autorisation permanente des ventilateurs",
        "L’autorisation permanente ne peut être configurée que depuis la fenêtre principale d’Open Hardware Control.",
    ),
}.items():
    NEXT_VERSION_MESSAGES[_code].update(enumerate(_messages, 1895))

for _code, _messages in {
    "de": (
        "Module im Seitenmenü",
        "Module hier ein- oder ausblenden. Die Übersicht, Navigationseinstellung und Hilfe bleiben immer erreichbar. Das Ausblenden allein beendet keine laufende Hardwaresteuerung.",
        "Alle Module anzeigen", "Alle Module werden im Seitenmenü angezeigt",
        "CPU beim Start automatisch erkennen und passende Standardkurven laden",
        "Erkannte CPU-Standardkurven erneut laden",
        "CPU-Automatik ist ausgeschaltet. Die gespeicherte Auswahl und Kurve bleiben unverändert.",
        "Eigene Auswahl oder Kurve erkannt · Benutzereinstellung hat Vorrang vor der CPU-Automatik.",
        "Automatisch erkannt: {model} · passende Standardkurven sind geladen.",
        "CPU-Automatik aktiv · für die erkannte CPU ist noch kein geprüftes Standardprofil vorhanden.",
        "Erkannte CPU-Standardkurven wurden geladen",
        "Für die erkannte CPU ist kein geprüftes Standardprofil vorhanden.",
        "Bitte zuerst einen Mainboard-Anschluss und anschließend einen Lüfter- oder Pumpenplatz in der Grafik auswählen.",
        "Vorhandene Lüfterzuordnung ersetzen?",
        "Der Anschluss oder Einbauplatz ist bereits zugeordnet. Soll die bisherige Zuordnung ersetzt werden?",
    ),
    "en": (
        "Sidebar modules",
        "Show or hide modules here. Overview, navigation settings, and help always remain available. Hiding a module alone does not stop active hardware control.",
        "Show all modules", "All modules are shown in the sidebar",
        "Automatically detect the CPU at startup and load matching default curves",
        "Reload detected CPU default curves",
        "CPU automation is disabled. The saved selection and curves remain unchanged.",
        "Custom selection or curve detected · the user setting takes priority over CPU automation.",
        "Automatically detected: {model} · matching default curves are loaded.",
        "CPU automation active · no verified default profile exists for the detected CPU yet.",
        "Detected CPU default curves were loaded",
        "No verified default profile exists for the detected CPU.",
        "First select a mainboard connector and then a fan or pump position in the diagram.",
        "Replace the existing fan assignment?",
        "The connector or position is already assigned. Replace the previous assignment?",
    ),
    "es": (
        "Módulos de la barra lateral",
        "Muestra u oculta módulos aquí. El resumen, los ajustes de navegación y la ayuda permanecen siempre disponibles. Ocultar un módulo no detiene por sí solo un control de hardware activo.",
        "Mostrar todos los módulos", "Todos los módulos se muestran en la barra lateral",
        "Detectar automáticamente la CPU al iniciar y cargar las curvas predeterminadas adecuadas",
        "Volver a cargar las curvas predeterminadas de la CPU detectada",
        "La automatización de CPU está desactivada. La selección y las curvas guardadas no cambian.",
        "Se detectó una selección o curva propia · el ajuste del usuario tiene prioridad sobre la automatización de CPU.",
        "Detectada automáticamente: {model} · se cargaron las curvas predeterminadas adecuadas.",
        "Automatización de CPU activa · todavía no existe un perfil predeterminado verificado para la CPU detectada.",
        "Se cargaron las curvas predeterminadas de la CPU detectada",
        "No existe un perfil predeterminado verificado para la CPU detectada.",
        "Selecciona primero un conector de la placa base y después una posición de ventilador o bomba en el diagrama.",
        "¿Sustituir la asignación de ventilador existente?",
        "El conector o la posición ya está asignado. ¿Sustituir la asignación anterior?",
    ),
    "fr": (
        "Modules de la barre latérale",
        "Affichez ou masquez les modules ici. La vue d’ensemble, les réglages de navigation et l’aide restent toujours accessibles. Masquer un module ne suffit pas à arrêter un contrôle matériel actif.",
        "Afficher tous les modules", "Tous les modules sont affichés dans la barre latérale",
        "Détecter automatiquement le processeur au démarrage et charger les courbes par défaut adaptées",
        "Recharger les courbes par défaut du processeur détecté",
        "L’automatisation du processeur est désactivée. La sélection et les courbes enregistrées restent inchangées.",
        "Sélection ou courbe personnalisée détectée · le réglage utilisateur est prioritaire sur l’automatisation du processeur.",
        "Détecté automatiquement : {model} · les courbes par défaut adaptées sont chargées.",
        "Automatisation du processeur active · aucun profil par défaut vérifié n’existe encore pour le processeur détecté.",
        "Les courbes par défaut du processeur détecté ont été chargées",
        "Aucun profil par défaut vérifié n’existe pour le processeur détecté.",
        "Sélectionnez d’abord un connecteur de la carte mère, puis un emplacement de ventilateur ou de pompe dans le schéma.",
        "Remplacer l’affectation de ventilateur existante ?",
        "Le connecteur ou l’emplacement est déjà affecté. Remplacer l’affectation précédente ?",
    ),
}.items():
    NEXT_VERSION_MESSAGES[_code].update(enumerate(_messages, 1901))

from .retained_lcd_messages import RETAINED_LCD_MESSAGES
from .retained_feature_messages import RETAINED_FEATURE_MESSAGES
from .retained_ui_messages import RETAINED_UI_MESSAGES

for _code in NEXT_VERSION_MESSAGES:
    NEXT_VERSION_MESSAGES[_code].update(RETAINED_LCD_MESSAGES[_code])
    NEXT_VERSION_MESSAGES[_code].update(RETAINED_FEATURE_MESSAGES[_code])
    NEXT_VERSION_MESSAGES[_code].update(RETAINED_UI_MESSAGES[_code])

for _code, _message in {
    "de": "Levita-Display ist durch ein anderes Programm belegt · keine automatische Freigabe; das andere Programm schließen und das Design erneut anwenden",
    "en": "Another program is using the Levita display · no automatic release; close the other program and apply the design again",
    "es": "Otro programa está usando la pantalla Levita · no se liberará automáticamente; cierra el otro programa y vuelve a aplicar el diseño",
    "fr": "Un autre programme utilise l’écran Levita · aucune libération automatique ; fermez cet autre programme puis appliquez à nouveau le design",
}.items():
    NEXT_VERSION_MESSAGES[_code][2823] = _message

for _code, _message in {
    "de": "Räumlicher Ablauf gespeichert. Bitte zuerst den LED-Verlauf am Anschluss festlegen; ohne ihn bleibt die Beleuchtung lokal.",
    "en": "Spatial flow saved. First define the LED path on the header; without it, lighting remains local.",
    "es": "Recorrido espacial guardado. Define primero el recorrido LED del conector; sin él, la iluminación sigue siendo local.",
    "fr": "Parcours spatial enregistré. Définissez d’abord le parcours LED du connecteur ; sans lui, l’éclairage reste local.",
}.items():
    NEXT_VERSION_MESSAGES[_code][2824] = _message

for _code, _message in {
    "de": "Eigener Levita-Daemon ist erneut blockiert · automatische Reparatur ist bereits ausgeschöpft; Display freigeben manuell ausführen",
    "en": "The Levita daemon owned by OHC is blocked again · automatic repair has already been exhausted; run Release display manually",
    "es": "El daemon de Levita de OHC vuelve a estar bloqueado · la reparación automática ya se ha agotado; ejecuta Liberar pantalla manualmente",
    "fr": "Le daemon Levita appartenant à OHC est de nouveau bloqué · la réparation automatique est déjà épuisée ; lancez manuellement Libérer l’écran",
}.items():
    NEXT_VERSION_MESSAGES[_code][2900] = _message
