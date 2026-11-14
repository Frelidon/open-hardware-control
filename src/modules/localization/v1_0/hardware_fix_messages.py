# SPDX-License-Identifier: GPL-3.0-or-later
"""Atomic Hardware Fix installation and status messages."""
HARDWARE_FIX_MESSAGES = {'de': {3720: 'Hardware Fix',
        3721: 'Status wird geprüft …',
        3722: 'Gezielte, rücknehmbare Korrekturen für exakt erkannte Hardware. Keine Firmware wird in das '
              'Gerät geflasht.',
        3723: 'Achtung: Das Profil weist die MSI-EDID allen DisplayPort-Anschlüssen zu. Andere, gleichzeitig '
              'angeschlossene DP-Monitore vorher trennen oder die Aktion abbrechen.',
        3724: 'Fix: korrigierte VRR-Kennung in einer anonymisierten EDID für DisplayPort. Die persönliche '
              'Monitor-Seriennummer ist nicht enthalten. HDMI bleibt unverändert.',
        3725: 'Installieren',
        3726: 'Deinstallieren',
        3727: 'Weitere Optionen',
        3728: 'Protokoll anzeigen',
        3729: 'Technischer Status',
        3730: 'Lokale Installation · empfohlen',
        3731: 'Der Fix läuft unabhängig von Open Hardware Control. Installieren richtet die benötigten '
              'Schritte ein oder aktualisiert den vorhandenen lokalen Dienst.',
        3732: 'Ausführliche Diagnose',
        3733: 'Ubuntu-Automatik reparieren',
        3734: 'Nur die Ubuntu-Automatik entfernen',
        3735: 'Boot-Fix erneut installieren',
        3736: 'Profilressourcen sind beschädigt. Open Hardware Control erneut installieren.',
        3737: 'MSI-Monitor über DisplayPort anschließen.',
        3738: 'Neustart erforderlich. Danach mit Installieren die Einrichtung abschließen.',
        3739: 'Dieser Fix unterstützt Ubuntu und Fedora.',
        3740: 'Installieren prüft und aktualisiert die Einrichtung. Deinstallieren entfernt den Fix '
              'einschließlich der Ubuntu-Automatik.',
        3741: 'Mit Installieren beginnen. Eine nötige Administratorabfrage öffnet sich im Terminal.',
        3742: 'Alle Spiele vorher beenden. Der lokale Dienst und die eindeutig zu diesem Profil gehörenden '
              'Bootdateien werden entfernt. Ein nötiger Neustart erfolgt nicht automatisch.',
        3743: 'Der Fix wird lokal eingerichtet. Ubuntu/GNOME erhält zusätzlich Desktop-VRR und die '
              'Spielautomatik. Andere DP-Monitore vorher trennen. Ein nötiger Neustart erfolgt nicht '
              'automatisch.',
        3744: 'Dieser einzelne Reparaturschritt verändert die vorhandene Einrichtung. Vor dem Entfernen der '
              'Automatik alle Spiele beenden.',
        3745: 'Terminal konnte nicht geöffnet werden. Ein unterstütztes Terminal und Python 3 werden '
              'benötigt.',
        3746: 'Hardware-Fix-Aktion läuft im Terminal …',
        3747: 'Kein Ergebnis vom Terminal erhalten. Terminal und Protokoll prüfen.',
        3748: 'Die Aktion wurde nicht erfolgreich abgeschlossen. Details stehen im Protokoll.',
        3749: 'Noch kein Hardware-Fix-Protokoll vorhanden.',
        3750: 'Statusprüfung fehlgeschlagen. Diagnose und Protokoll öffnen.',
        3751: 'Lokal installiert',
        3752: 'Noch nicht installiert',
        3753: 'ja',
        3754: 'nein',
        3755: 'System: {system}',
        3756: 'Monitor: {monitor}',
        3757: 'Korrigierte EDID geladen: {value}',
        3758: 'Boot-Fix gespeichert: {value}',
        3759: 'Ubuntu-Automatik installiert / aktiv: {installed} / {active}'},
 'en': {3720: 'Hardware Fix',
        3721: 'Checking status…',
        3722: 'Targeted, reversible fixes for precisely identified hardware. No firmware is flashed to the '
              'device.',
        3723: 'Warning: This profile assigns the MSI EDID to all DisplayPort connectors. Disconnect other DP '
              'monitors first or cancel.',
        3724: 'Fix: corrected VRR flag in an anonymized DisplayPort EDID. The personal monitor serial number '
              'is excluded. HDMI is unchanged.',
        3725: 'Install',
        3726: 'Uninstall',
        3727: 'More options',
        3728: 'Show log',
        3729: 'Technical status',
        3730: 'Local installation · recommended',
        3731: 'The fix runs independently of Open Hardware Control. Install sets up the required steps or '
              'updates the existing local service.',
        3732: 'Detailed diagnostics',
        3733: 'Repair Ubuntu automation',
        3734: 'Remove only Ubuntu automation',
        3735: 'Reinstall boot fix',
        3736: 'Profile resources are damaged. Reinstall Open Hardware Control.',
        3737: 'Connect the MSI monitor via DisplayPort.',
        3738: 'Restart required. Then select Install to finish setup.',
        3739: 'This fix supports Ubuntu and Fedora.',
        3740: 'Install checks and updates the setup. Uninstall removes the fix including Ubuntu automation.',
        3741: 'Select Install to begin. Any required administrator prompt opens in the terminal.',
        3742: 'Close all games first. The local service and boot files clearly belonging to this profile '
              'will be removed. Any required restart is manual.',
        3743: 'The fix is installed locally. Ubuntu/GNOME also gets desktop VRR and game automation. '
              'Disconnect other DP monitors first. Any required restart is manual.',
        3744: 'This individual repair step changes the existing setup. Close all games before removing '
              'automation.',
        3745: 'Could not open a terminal. A supported terminal and Python 3 are required.',
        3746: 'Hardware Fix action is running in the terminal…',
        3747: 'No result received from the terminal. Check the terminal and log.',
        3748: 'The action did not complete successfully. See the log for details.',
        3749: 'No Hardware Fix log available yet.',
        3750: 'Status check failed. Open diagnostics and log.',
        3751: 'Installed locally',
        3752: 'Not installed yet',
        3753: 'yes',
        3754: 'no',
        3755: 'System: {system}',
        3756: 'Monitor: {monitor}',
        3757: 'Corrected EDID loaded: {value}',
        3758: 'Boot fix saved: {value}',
        3759: 'Ubuntu automation installed / active: {installed} / {active}'},
 'es': {3720: 'Hardware Fix',
        3721: 'Comprobando estado…',
        3722: 'Correcciones específicas y reversibles para hardware identificado con precisión. No se graba '
              'firmware en el dispositivo.',
        3723: 'Atención: Este perfil asigna el EDID de MSI a todos los conectores DisplayPort. Desconecta '
              'primero los otros monitores DP o cancela.',
        3724: 'Corrección: indicador VRR corregido en un EDID DisplayPort anonimizado. No incluye el número '
              'de serie personal del monitor. HDMI no cambia.',
        3725: 'Instalar',
        3726: 'Desinstalar',
        3727: 'Más opciones',
        3728: 'Mostrar registro',
        3729: 'Estado técnico',
        3730: 'Instalación local · recomendada',
        3731: 'La corrección funciona independientemente de Open Hardware Control. Instalar configura los '
              'pasos necesarios o actualiza el servicio local existente.',
        3732: 'Diagnóstico detallado',
        3733: 'Reparar automatización de Ubuntu',
        3734: 'Eliminar solo la automatización de Ubuntu',
        3735: 'Reinstalar corrección de arranque',
        3736: 'Los recursos del perfil están dañados. Reinstala Open Hardware Control.',
        3737: 'Conecta el monitor MSI mediante DisplayPort.',
        3738: 'Es necesario reiniciar. Después selecciona Instalar para terminar la configuración.',
        3739: 'Esta corrección es compatible con Ubuntu y Fedora.',
        3740: 'Instalar comprueba y actualiza la configuración. Desinstalar elimina la corrección y la '
              'automatización de Ubuntu.',
        3741: 'Selecciona Instalar para empezar. La solicitud de administrador se abre en el terminal si es '
              'necesaria.',
        3742: 'Cierra todos los juegos antes. Se eliminarán el servicio local y los archivos de arranque '
              'propios de este perfil. El reinicio necesario será manual.',
        3743: 'La corrección se instala localmente. Ubuntu/GNOME recibe además VRR de escritorio y '
              'automatización para juegos. Desconecta primero los otros monitores DP. El reinicio necesario '
              'será manual.',
        3744: 'Este paso de reparación cambia la configuración existente. Cierra todos los juegos antes de '
              'eliminar la automatización.',
        3745: 'No se pudo abrir el terminal. Se necesitan un terminal compatible y Python 3.',
        3746: 'La acción de Hardware Fix se ejecuta en el terminal…',
        3747: 'No se recibió ningún resultado del terminal. Comprueba el terminal y el registro.',
        3748: 'La acción no terminó correctamente. Consulta el registro.',
        3749: 'Todavía no hay un registro de Hardware Fix.',
        3750: 'Falló la comprobación de estado. Abre el diagnóstico y el registro.',
        3751: 'Instalado localmente',
        3752: 'Todavía no instalado',
        3753: 'sí',
        3754: 'no',
        3755: 'Sistema: {system}',
        3756: 'Monitor: {monitor}',
        3757: 'EDID corregido cargado: {value}',
        3758: 'Corrección de arranque guardada: {value}',
        3759: 'Automatización Ubuntu instalada / activa: {installed} / {active}'},
 'fr': {3720: 'Hardware Fix',
        3721: 'Vérification de l’état…',
        3722: 'Corrections ciblées et réversibles pour le matériel précisément identifié. Aucun '
              'micrologiciel n’est flashé sur l’appareil.',
        3723: 'Attention : ce profil attribue l’EDID MSI à tous les connecteurs DisplayPort. Débranchez '
              'd’abord les autres écrans DP ou annulez.',
        3724: 'Correction : indicateur VRR corrigé dans un EDID DisplayPort anonymisé. Le numéro de série '
              'personnel de l’écran est exclu. HDMI reste inchangé.',
        3725: 'Installer',
        3726: 'Désinstaller',
        3727: 'Autres options',
        3728: 'Afficher le journal',
        3729: 'État technique',
        3730: 'Installation locale · recommandée',
        3731: 'La correction fonctionne indépendamment d’Open Hardware Control. Installer configure les '
              'étapes nécessaires ou actualise le service local existant.',
        3732: 'Diagnostic détaillé',
        3733: 'Réparer l’automatisation Ubuntu',
        3734: 'Retirer uniquement l’automatisation Ubuntu',
        3735: 'Réinstaller la correction au démarrage',
        3736: 'Les ressources du profil sont endommagées. Réinstallez Open Hardware Control.',
        3737: 'Connectez l’écran MSI via DisplayPort.',
        3738: 'Un redémarrage est nécessaire. Choisissez ensuite Installer pour terminer la configuration.',
        3739: 'Cette correction prend en charge Ubuntu et Fedora.',
        3740: 'Installer vérifie et actualise la configuration. Désinstaller retire la correction et '
              'l’automatisation Ubuntu.',
        3741: 'Choisissez Installer pour commencer. Toute demande d’administration nécessaire s’ouvre dans '
              'le terminal.',
        3742: 'Fermez d’abord tous les jeux. Le service local et les fichiers de démarrage propres à ce '
              'profil seront retirés. Tout redémarrage nécessaire reste manuel.',
        3743: 'La correction est installée localement. Ubuntu/GNOME reçoit aussi le VRR du bureau et '
              'l’automatisation des jeux. Débranchez d’abord les autres écrans DP. Tout redémarrage '
              'nécessaire reste manuel.',
        3744: 'Cette étape de réparation modifie la configuration existante. Fermez tous les jeux avant de '
              'retirer l’automatisation.',
        3745: 'Impossible d’ouvrir un terminal. Un terminal pris en charge et Python 3 sont nécessaires.',
        3746: 'L’action Hardware Fix s’exécute dans le terminal…',
        3747: 'Aucun résultat reçu du terminal. Consultez le terminal et le journal.',
        3748: 'L’action n’a pas abouti. Consultez le journal.',
        3749: 'Aucun journal Hardware Fix disponible.',
        3750: 'La vérification de l’état a échoué. Ouvrez le diagnostic et le journal.',
        3751: 'Installé localement',
        3752: 'Pas encore installé',
        3753: 'oui',
        3754: 'non',
        3755: 'Système : {system}',
        3756: 'Écran : {monitor}',
        3757: 'EDID corrigé chargé : {value}',
        3758: 'Correction au démarrage enregistrée : {value}',
        3759: 'Automatisation Ubuntu installée / active : {installed} / {active}'}}
