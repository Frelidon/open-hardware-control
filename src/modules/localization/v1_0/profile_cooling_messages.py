# SPDX-License-Identifier: GPL-3.0-or-later
"""Atomic fresh-sensor profile diagnostics."""
PROFILE_COOLING_MESSAGES = {'de': {3194: 'PROFIL-KÜHLUNG: Ausstehende Anwendung verworfen · Grund={reason}',
        3195: 'PROFIL-KÜHLUNG: Profil „{name}“ wartet bis zu 10 Sekunden auf einen frischen '
              'CPU-Messwert. {detail}',
        3196: 'Kühlprofil wartet auf frische CPU-Temperatur.',
        3197: 'Kühlgerät ist nicht mehr verfügbar.',
        3198: 'PROFIL-KÜHLUNG: Frischer CPU-Messwert verfügbar; Profil „{name}“ wird erneut '
              'geprüft.',
        3199: 'Auch nach 10 Sekunden ist keine frische CPU-Temperatur verfügbar. Die Profilkurve '
              'wurde nicht übertragen.'},
 'en': {3194: 'PROFILE COOLING: Pending apply cancelled · reason={reason}',
        3195: 'PROFILE COOLING: Profile “{name}” waits up to 10 seconds for a fresh CPU reading. '
              '{detail}',
        3196: 'Cooling profile is waiting for a fresh CPU temperature.',
        3197: 'Cooling device is no longer available.',
        3198: 'PROFILE COOLING: Fresh CPU reading available; rechecking profile “{name}”.',
        3199: 'No fresh CPU temperature is available after 10 seconds. The profile curve was not '
              'transferred.'},
 'es': {3194: 'REFRIGERACIÓN DEL PERFIL: Aplicación pendiente cancelada · motivo={reason}',
        3195: 'REFRIGERACIÓN DEL PERFIL: El perfil «{name}» espera hasta 10 segundos una lectura '
              'reciente de CPU. {detail}',
        3196: 'El perfil de refrigeración espera una temperatura reciente de CPU.',
        3197: 'El dispositivo de refrigeración ya no está disponible.',
        3198: 'REFRIGERACIÓN DEL PERFIL: Lectura reciente de CPU disponible; se vuelve a comprobar '
              'el perfil «{name}».',
        3199: 'No hay temperatura reciente de CPU tras 10 segundos. No se ha transferido la curva '
              'del perfil.'},
 'fr': {3194: 'REFROIDISSEMENT DU PROFIL : application en attente annulée · raison={reason}',
        3195: 'REFROIDISSEMENT DU PROFIL : le profil « {name} » attend jusqu’à 10 secondes une '
              'nouvelle mesure CPU. {detail}',
        3196: 'Le profil de refroidissement attend une nouvelle température CPU.',
        3197: 'Le dispositif de refroidissement n’est plus disponible.',
        3198: 'REFROIDISSEMENT DU PROFIL : nouvelle mesure CPU disponible ; nouvelle vérification '
              'du profil « {name} ».',
        3199: 'Aucune température CPU récente après 10 secondes. La courbe du profil n’a pas été '
              'transmise.'}}
