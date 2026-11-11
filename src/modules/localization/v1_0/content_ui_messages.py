# SPDX-License-Identifier: GPL-3.0-or-later
"""Atomic DE/EN/ES/FR updates for sidebar safety and content transitions.

The unchanged pixel-test caption is moved here to preserve language-file budgets.
"""

CONTENT_UI_MESSAGES = {'de': {1109: 'Vorschläge · 12',
        1465: 'Seitenwechsel animieren',
        1902: 'Module hier ein- oder ausblenden. Übersicht, Einstellungen, Navigationseinstellung '
              'und Hilfe bleiben immer erreichbar. Das Ausblenden allein beendet keine laufende '
              'Hardwaresteuerung.',
        2945: 'Von unten gleiten',
        2946: 'Zügig · 220 ms',
        2947: 'Ruhig · 380 ms',
        2948: 'Langsam · 550 ms',
        2949: 'Übergangsdauer',
        1673: 'Sichttest: Nur die gewählte LED oder Zone leuchtet weiß; andere OHC-LEDs werden '
              'schwarz. Beim Schließen kehrt das Design zurück.'},
 'en': {1109: 'Suggestions · 12',
        1465: 'Animate page changes',
        1902: 'Show or hide modules here. Overview, settings, navigation settings, and help always '
              'remain available. Hiding a module alone does not stop active hardware control.',
        2945: 'Glide up',
        2946: 'Quick · 220 ms',
        2947: 'Calm · 380 ms',
        2948: 'Slow · 550 ms',
        2949: 'Transition duration',
        1673: 'Visual test: Only the chosen LED or zone lights white; other OHC LEDs go dark. The '
              'design returns on close.'},
 'es': {1109: 'Sugerencias · 12',
        1465: 'Animar cambios de página',
        1902: 'Muestra u oculta módulos aquí. La vista general, los ajustes, los ajustes de '
              'navegación y la ayuda siempre están disponibles. Ocultar un módulo no detiene el '
              'control activo del hardware.',
        2945: 'Deslizar desde abajo',
        2946: 'Rápida · 220 ms',
        2947: 'Suave · 380 ms',
        2948: 'Lenta · 550 ms',
        2949: 'Duración de la transición',
        1673: 'Prueba visual: Solo el LED o la zona elegida se ilumina en blanco; los demás LED de '
              'OHC se apagan. El diseño vuelve al cerrar.'},
 'fr': {1109: 'Suggestions · 12',
        1465: 'Animer les changements de page',
        1902: 'Affichez ou masquez les modules ici. La vue d’ensemble, les paramètres, les '
              'réglages de navigation et l’aide restent toujours accessibles. Masquer un module ne '
              'suffit pas à arrêter un contrôle matériel actif.',
        2945: 'Glisser depuis le bas',
        2946: 'Rapide · 220 ms',
        2947: 'Douce · 380 ms',
        2948: 'Lente · 550 ms',
        2949: 'Durée de la transition',
        1673: 'Test visuel : seule la LED ou la zone choisie brille en blanc ; les autres LED OHC '
              's’éteignent. Le motif revient à la fermeture.'}}

from .redesign_messages import REDESIGN_MESSAGES
for _language, _messages in REDESIGN_MESSAGES.items():
    CONTENT_UI_MESSAGES[_language].update(_messages)
CONTENT_UI_MESSAGES['en'][1885] = 'Hardware Checker'
CONTENT_UI_MESSAGES['es'][1885] = 'Comprobación de hardware'
CONTENT_UI_MESSAGES['fr'][1885] = 'Vérification du matériel'

from .device_catalog_messages import DEVICE_CATALOG_MESSAGES
for _language, _messages in DEVICE_CATALOG_MESSAGES.items():
    CONTENT_UI_MESSAGES[_language].update(_messages)

from .fan_history_messages import FAN_HISTORY_MESSAGES
for _language, _messages in FAN_HISTORY_MESSAGES.items():
    CONTENT_UI_MESSAGES[_language].update(_messages)

from .design_hub_messages import DESIGN_HUB_MESSAGES
for _language, _messages in DESIGN_HUB_MESSAGES.items():
    CONTENT_UI_MESSAGES[_language].update(_messages)

from .profile_background_messages import PROFILE_BACKGROUND_MESSAGES
for _language, _messages in PROFILE_BACKGROUND_MESSAGES.items():
    CONTENT_UI_MESSAGES[_language].update(_messages)

from .profile_cooling_messages import PROFILE_COOLING_MESSAGES
for _language, _messages in PROFILE_COOLING_MESSAGES.items():
    CONTENT_UI_MESSAGES[_language].update(_messages)
