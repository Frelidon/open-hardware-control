# SPDX-License-Identifier: GPL-3.0-or-later
"""Four-language RGB design-speed controls."""

RGB_SPEED_MESSAGES = {}

for _code, _messages in {
    "de": ("Design-Geschwindigkeit", "100 % · Designstandard", "100 % verwendet das für dieses Design abgestimmte Originaltempo. Langsamere Werte helfen besonders bei kurzen LED-Ringen und vielen Direct-Geräten.", "Vorschläge:", "Empfohlen", "Design mit {scale} % des Standardtempos", "Auf 100 % zurücksetzen", "Designstandard", "Effekttempo", "Bitte Design auswählen", "Tempo auf 100 % zurücksetzen", "Farben auf Designstandard zurücksetzen", "Design vollständig zurücksetzen"),
    "en": ("Design speed", "100% · design default", "100% uses the original speed tuned for this design. Slower values are especially useful for short LED rings and many Direct devices.", "Suggestions:", "Recommended", "Design at {scale}% of the default speed", "Reset to 100%", "Design default", "Effect speed", "Select a design", "Reset speed to 100%", "Reset colours to design default", "Reset design completely"),
    "es": ("Velocidad del diseño", "100 % · valor predeterminado del diseño", "El 100 % usa la velocidad original ajustada para este diseño. Los valores más lentos son especialmente útiles con anillos LED cortos y muchos dispositivos Direct.", "Sugerencias:", "Recomendado", "Diseño al {scale} % de la velocidad predeterminada", "Restablecer al 100 %", "Valor predeterminado del diseño", "Velocidad del efecto", "Seleccionar un diseño", "Restablecer la velocidad al 100 %", "Restablecer los colores del diseño", "Restablecer el diseño por completo"),
    "fr": ("Vitesse du design", "100 % · valeur par défaut du design", "100 % utilise la vitesse d’origine réglée pour ce design. Les valeurs plus lentes sont particulièrement utiles pour les anneaux LED courts et de nombreux appareils Direct.", "Suggestions :", "Recommandé", "Design à {scale} % de la vitesse par défaut", "Rétablir à 100 %", "Valeur par défaut du design", "Vitesse de l’effet", "Sélectionner un design", "Rétablir la vitesse à 100 %", "Rétablir les couleurs du design", "Réinitialiser complètement le design"),
}.items():
    RGB_SPEED_MESSAGES[_code] = dict(enumerate(_messages, 2912))

# Complete all four data catalogs through their existing supplemental import.
for _code, _messages in {
    'de': ('▶ PLAY', '■ STOPP', 'OpenRGB Originale', 'OpenRGB Originalmodi', 'Ausgewählten OpenRGB-Originalmodus anwenden'),
    'en': ('▶ PLAY', '■ STOP', 'OpenRGB originals', 'OpenRGB original modes', 'Apply selected OpenRGB original mode'),
    'es': ('▶ REPRODUCIR', '■ DETENER', 'Originales de OpenRGB', 'Modos originales de OpenRGB', 'Aplicar el modo original de OpenRGB seleccionado'),
    'fr': ('▶ LECTURE', '■ ARRÊT', 'Originaux OpenRGB', 'Modes originaux OpenRGB', 'Appliquer le mode original OpenRGB sélectionné'),
}.items():
    RGB_SPEED_MESSAGES[_code].update(enumerate(_messages, 2940))
