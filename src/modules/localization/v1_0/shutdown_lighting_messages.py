# SPDX-License-Identifier: GPL-3.0-or-later
"""Four-language RGB shutdown-lighting controls."""

SHUTDOWN_LIGHTING_MESSAGES = {}

for _code, _messages in {
    "de": (
        "BELEUCHTUNG NACH PROGRAMMENDE",
        "Wenn Open Hardware Control beendet ist:",
        "Einzelfarbe",
        "Rainbow · Hardwaremodus",
        "Standard ist Weiß. Die Einstellung wird nur beim echten Beenden angewendet, nicht beim Minimieren in den Infobereich. Rainbow verwendet ausschließlich einen vom Gerät gemeldeten Hardwaremodus; fehlt er, bleibt die gewählte Einzelfarbe als Rückfall erhalten.",
        "Wunschfarbe wählen",
        "Wunschfarbe nach Programmende",
    ),
    "en": (
        "LIGHTING AFTER APPLICATION EXIT",
        "When Open Hardware Control is closed:",
        "Solid colour",
        "Rainbow · hardware mode",
        "White is the default. This setting is applied only on a real exit, not when minimizing to the tray. Rainbow uses only a hardware mode reported by the device; if none exists, the selected solid colour remains the fallback.",
        "Choose desired colour",
        "Desired colour after application exit",
    ),
    "es": (
        "ILUMINACIÓN TRAS CERRAR EL PROGRAMA",
        "Cuando Open Hardware Control esté cerrado:",
        "Color uniforme",
        "Arcoíris · modo de hardware",
        "El valor predeterminado es blanco. Este ajuste solo se aplica al cerrar realmente, no al minimizar a la bandeja. Arcoíris usa únicamente un modo de hardware indicado por el dispositivo; si no existe, el color uniforme elegido se conserva como alternativa.",
        "Elegir color deseado",
        "Color deseado tras cerrar el programa",
    ),
    "fr": (
        "ÉCLAIRAGE APRÈS LA FERMETURE DU PROGRAMME",
        "Quand Open Hardware Control est fermé :",
        "Couleur unie",
        "Arc-en-ciel · mode matériel",
        "Le blanc est utilisé par défaut. Ce réglage ne s’applique qu’à une fermeture réelle, pas à la réduction dans la zone de notification. L’arc-en-ciel utilise uniquement un mode matériel signalé par l’appareil ; s’il n’existe pas, la couleur unie choisie reste la solution de repli.",
        "Choisir la couleur souhaitée",
        "Couleur souhaitée après la fermeture du programme",
    ),
}.items():
    SHUTDOWN_LIGHTING_MESSAGES[_code] = dict(enumerate(_messages, 2905))
