# SPDX-License-Identifier: GPL-3.0-or-later
"""Four-language Snapshot Manager data kept separate to preserve file budgets."""

from __future__ import annotations


def _messages(values: str, authorization: str) -> dict[int, str]:
    messages = dict(enumerate(values.split("§"), 1736))
    messages[1788] = authorization
    return messages


SNAPSHOT_MESSAGES = {
    "de": _messages(
        "Snapshot-Manager§Erkennt Linux-Snapshot-Systeme, begrenzt Btrfs-Aufräumlast und verhindert neue automatische Läufe während Spielen.§DESKTOP · AUTOMATIK BEREIT§Manuelle Sperre§Blockiert neue automatische Snapshots und geplante Bereinigungen. Bereits laufende Btrfs-Kernelarbeit wird nur gedrosselt, nicht gewaltsam beendet.§Für 1 Stunde blockieren§Bis Datum/Uhrzeit blockieren§Dauerhaft blockieren§Jetzt fortsetzen§Keine manuelle Sperre aktiv.§Snapshots und Wiederherstellung§Liste mit Administratorrechten laden§Nr.§Erstellt§Bereinigung§Wiederherstellen: Einen Snapshot zuerst schreibgeschützt einhängen und Dateien prüfen. Ein vollständiger Snapper-Rollback verändert das Startsystem und bleibt deshalb bewusst außerhalb eines Ein-Klick-Knopfs.§Spiel- und Leistungsautomatik§Snapshot-Arbeit bei Spielen automatisch pausieren§KDE-Vollbildanwendungen als Spielsignal verwenden§CPU- und GPU-Last als vorsichtigen Zusatz verwenden§CPU-Schwelle§GPU-Schwelle§Desktop-Limit§Spiel-Limit§Optionale Programmliste, z. B. game.exe, gamescope§Automatik einmalig autorisieren§Aktivität wird gelesen …§Erkanntes System§Neu erkennen§Betriebssystem wird erkannt …§Zustand§Btrfs-Aufräumstatus wird gelesen …§Erkennung nicht verfügbar§Aktiv§Btrfs offen: {amount} · Limit: {iops} IOPS§CPU {cpu:.0f} % · {cores}/{total} Kerne hoch · GPU {gpu} · {reason}§Feral GameMode§Gamescope§Programmliste§Vollbildanwendung§CPU- und GPU-Last§Desktop§SPIELMODUS · SNAPSHOTS PAUSIERT§Der gewählte Zeitpunkt muss in der Zukunft liegen.§Snapshot-Arbeit blockiert bis {time}.§Snapshot-Arbeit dauerhaft blockiert, bis du sie fortsetzt.§Snapshot-Arbeit wird im gedrosselten Desktop-Modus fortgesetzt.§Snapshot-Helfer ist noch nicht installiert.§Aktion nicht ausgeführt oder abgebrochen.§Automatik autorisiert§Automatik benötigt einmalig Administratorfreigabe§Snapshots erkennen, Aufräumlast begrenzen und Spiele schützen.",
        "Administratorfreigabe wird angefordert …",
    ),
    "en": _messages(
        "Snapshot Manager§Detects Linux snapshot systems, limits Btrfs cleanup load and prevents new automatic runs while gaming.§DESKTOP · AUTOMATION READY§Manual block§Blocks new automatic snapshots and scheduled cleanup. Btrfs kernel work already running is throttled, not forcibly terminated.§Block for 1 hour§Block until date/time§Block indefinitely§Resume now§No manual block is active.§Snapshots and recovery§Load list with administrator privileges§No.§Created§Cleanup§Recovery: First mount a snapshot read-only and inspect the files. A full Snapper rollback changes the boot system and is therefore deliberately kept outside a one-click button.§Game and performance automation§Automatically pause snapshot work while gaming§Use KDE full-screen applications as a game signal§Use CPU and GPU load as a cautious additional signal§CPU threshold§GPU threshold§Desktop limit§Game limit§Optional process list, e.g. game.exe, gamescope§Authorize automation once§Reading activity …§Detected system§Detect again§Detecting operating system …§State§Reading Btrfs cleanup status …§Detection unavailable§Active§Btrfs pending: {amount} · limit: {iops} IOPS§CPU {cpu:.0f}% · {cores}/{total} cores high · GPU {gpu} · {reason}§Feral GameMode§Gamescope§Process list§Full-screen application§CPU and GPU load§Desktop§GAME MODE · SNAPSHOTS PAUSED§The selected time must be in the future.§Snapshot work blocked until {time}.§Snapshot work blocked indefinitely until you resume it.§Snapshot work is resuming in throttled desktop mode.§The snapshot helper is not installed yet.§Action was not performed or was cancelled.§Automation authorized§Automation needs one-time administrator authorization§Detect snapshots, limit cleanup load and protect games.",
        "Requesting administrator authorization …",
    ),
    "es": _messages(
        "Gestor de instantáneas§Detecta sistemas de instantáneas de Linux, limita la carga de limpieza de Btrfs e impide nuevas ejecuciones automáticas mientras juegas.§ESCRITORIO · AUTOMATIZACIÓN LISTA§Bloqueo manual§Bloquea nuevas instantáneas automáticas y limpiezas programadas. El trabajo del kernel de Btrfs ya iniciado se limita, no se finaliza a la fuerza.§Bloquear durante 1 hora§Bloquear hasta fecha/hora§Bloquear indefinidamente§Reanudar ahora§No hay ningún bloqueo manual activo.§Instantáneas y recuperación§Cargar lista con permisos de administrador§N.º§Creada§Limpieza§Recuperación: primero monta una instantánea en modo de solo lectura y comprueba los archivos. Una reversión completa de Snapper modifica el sistema de arranque, por lo que se mantiene deliberadamente fuera de un botón de un solo clic.§Automatización de juegos y rendimiento§Pausar automáticamente las instantáneas mientras juegas§Usar aplicaciones KDE a pantalla completa como señal de juego§Usar la carga de CPU y GPU como señal adicional prudente§Umbral de CPU§Umbral de GPU§Límite de escritorio§Límite de juego§Lista de procesos opcional, p. ej. game.exe, gamescope§Autorizar la automatización una vez§Leyendo actividad …§Sistema detectado§Detectar de nuevo§Detectando el sistema operativo …§Estado§Leyendo el estado de limpieza de Btrfs …§Detección no disponible§Activo§Btrfs pendiente: {amount} · límite: {iops} IOPS§CPU {cpu:.0f} % · {cores}/{total} núcleos altos · GPU {gpu} · {reason}§Feral GameMode§Gamescope§Lista de procesos§Aplicación a pantalla completa§Carga de CPU y GPU§Escritorio§MODO DE JUEGO · INSTANTÁNEAS PAUSADAS§La hora seleccionada debe estar en el futuro.§Trabajo de instantáneas bloqueado hasta {time}.§Trabajo de instantáneas bloqueado indefinidamente hasta que lo reanudes.§El trabajo de instantáneas se reanuda en el modo de escritorio limitado.§El asistente de instantáneas aún no está instalado.§La acción no se ejecutó o fue cancelada.§Automatización autorizada§La automatización requiere una autorización de administrador única§Detecta instantáneas, limita la carga de limpieza y protege los juegos.",
        "Solicitando autorización de administrador …",
    ),
    "fr": _messages(
        "Gestionnaire d’instantanés§Détecte les systèmes d’instantanés Linux, limite la charge de nettoyage Btrfs et empêche de nouveaux lancements automatiques pendant les jeux.§BUREAU · AUTOMATISATION PRÊTE§Blocage manuel§Bloque les nouveaux instantanés automatiques et les nettoyages planifiés. Le travail du noyau Btrfs déjà lancé est limité, pas arrêté de force.§Bloquer pendant 1 heure§Bloquer jusqu’à une date/heure§Bloquer indéfiniment§Reprendre maintenant§Aucun blocage manuel actif.§Instantanés et restauration§Charger la liste avec les droits d’administration§N°§Créé§Nettoyage§Restauration : montez d’abord un instantané en lecture seule et vérifiez les fichiers. Une restauration Snapper complète modifie le système de démarrage ; elle reste donc volontairement en dehors d’un bouton en un clic.§Automatisation des jeux et des performances§Suspendre automatiquement le travail des instantanés pendant les jeux§Utiliser les applications KDE en plein écran comme signal de jeu§Utiliser prudemment la charge CPU et GPU comme signal supplémentaire§Seuil CPU§Seuil GPU§Limite du bureau§Limite de jeu§Liste facultative de processus, p. ex. game.exe, gamescope§Autoriser l’automatisation une fois§Lecture de l’activité …§Système détecté§Détecter à nouveau§Détection du système d’exploitation …§État§Lecture de l’état du nettoyage Btrfs …§Détection indisponible§Actif§Btrfs en attente : {amount} · limite : {iops} IOPS§CPU {cpu:.0f} % · {cores}/{total} cœurs chargés · GPU {gpu} · {reason}§Feral GameMode§Gamescope§Liste des processus§Application en plein écran§Charge CPU et GPU§Bureau§MODE JEU · INSTANTANÉS SUSPENDUS§L’heure choisie doit être dans le futur.§Travail des instantanés bloqué jusqu’au {time}.§Travail des instantanés bloqué indéfiniment jusqu’à sa reprise.§Le travail des instantanés reprend en mode bureau limité.§L’assistant d’instantanés n’est pas encore installé.§L’action n’a pas été exécutée ou a été annulée.§Automatisation autorisée§L’automatisation nécessite une autorisation administrateur unique§Détecter les instantanés, limiter la charge de nettoyage et protéger les jeux.",
        "Demande d’autorisation administrateur …",
    ),
}

for _code, _translation in {
    "de": "Nicht installiert", "en": "Not installed",
    "es": "No instalado", "fr": "Non installé",
}.items():
    SNAPSHOT_MESSAGES[_code][1789] = _translation

for _code, _translation in {
    "de": "Automatikfreigabe entfernen", "en": "Remove automation authorization",
    "es": "Quitar autorización de automatización", "fr": "Retirer l’autorisation d’automatisation",
}.items():
    SNAPSHOT_MESSAGES[_code][1790] = _translation

_SNAPSHOT_ACTION_MESSAGES = {
    "de": (
        "Snapshot auswählen, um ihn zu löschen.",
        "Der JSON-Export enthält Snapshot-Metadaten, nicht den gesicherten Dateiinhalt.",
        "Liste als JSON exportieren", "Ausgewählten Snapshot löschen",
        "Mehrkernlast für die vorsichtige Erkennung", "Zusätzliche Grafiklast",
        "Normale Btrfs-Aufräumrate", "Schonende Rate während eines Spiels",
        "Snapshot 0 ist der aktuelle Zustand und kann hier nicht gelöscht werden.",
        "Snapshot {number} ausgewählt.",
        "Snapshot {number} aus Snapper-Konfiguration {config} wirklich dauerhaft löschen?\n\nDiese Aktion kann nicht rückgängig gemacht werden.",
        "Snapshot löschen", "Kein Snapshot zum Exportieren geladen.",
        "Snapshot-Liste konnte nicht exportiert werden.", "Snapshot-Liste wurde exportiert.",
        "{count} Snapshots geladen.", "Snapshot {number} wurde gelöscht.",
    ),
    "en": (
        "Select a snapshot to delete it.",
        "The JSON export contains snapshot metadata, not the backed-up file contents.",
        "Export list as JSON", "Delete selected snapshot",
        "Multi-core load for cautious detection", "Additional graphics load",
        "Normal Btrfs cleanup rate", "Gentle rate while gaming",
        "Snapshot 0 is the current state and cannot be deleted here.",
        "Snapshot {number} selected.",
        "Permanently delete snapshot {number} from Snapper configuration {config}?\n\nThis action cannot be undone.",
        "Delete snapshot", "No snapshots have been loaded for export.",
        "The snapshot list could not be exported.", "The snapshot list was exported.",
        "{count} snapshots loaded.", "Snapshot {number} was deleted.",
    ),
    "es": (
        "Selecciona una instantánea para eliminarla.",
        "La exportación JSON contiene metadatos, no el contenido de los archivos guardados.",
        "Exportar lista como JSON", "Eliminar instantánea seleccionada",
        "Carga multinúcleo para una detección prudente", "Carga gráfica adicional",
        "Tasa normal de limpieza Btrfs", "Tasa reducida durante un juego",
        "La instantánea 0 es el estado actual y no se puede eliminar aquí.",
        "Instantánea {number} seleccionada.",
        "¿Eliminar permanentemente la instantánea {number} de la configuración de Snapper {config}?\n\nEsta acción no se puede deshacer.",
        "Eliminar instantánea", "No hay instantáneas cargadas para exportar.",
        "No se pudo exportar la lista de instantáneas.", "La lista de instantáneas se exportó.",
        "{count} instantáneas cargadas.", "Se eliminó la instantánea {number}.",
    ),
    "fr": (
        "Sélectionnez un instantané pour le supprimer.",
        "L’export JSON contient les métadonnées, pas le contenu des fichiers sauvegardés.",
        "Exporter la liste en JSON", "Supprimer l’instantané sélectionné",
        "Charge multicœur pour une détection prudente", "Charge graphique supplémentaire",
        "Débit normal de nettoyage Btrfs", "Débit réduit pendant un jeu",
        "L’instantané 0 est l’état actuel et ne peut pas être supprimé ici.",
        "Instantané {number} sélectionné.",
        "Supprimer définitivement l’instantané {number} de la configuration Snapper {config} ?\n\nCette action est irréversible.",
        "Supprimer l’instantané", "Aucun instantané n’est chargé pour l’export.",
        "La liste des instantanés n’a pas pu être exportée.", "La liste des instantanés a été exportée.",
        "{count} instantanés chargés.", "L’instantané {number} a été supprimé.",
    ),
}

for _code, _translations in _SNAPSHOT_ACTION_MESSAGES.items():
    SNAPSHOT_MESSAGES[_code].update(enumerate(_translations, 1791))
