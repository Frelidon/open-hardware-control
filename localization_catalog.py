#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Frelidon contributors
"""Static interface translations and the built-in help catalog.

This module intentionally has no Qt or hardware dependencies.  German source
strings remain the stable lookup keys for settings and profile compatibility.
"""

from __future__ import annotations

# First localization stage carried forward in the internal 2.9.8 build.  German remains the
# canonical source language so existing profiles/settings and hardware strings
# do not need a migration.  Static UI strings can be switched live; dynamic
# hardware/log messages deliberately keep their original technical wording for
# now so diagnostics remain unambiguous during the internal test phase.
UI_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "Übersicht": "Overview", "Kühlung": "Cooling", "Einstellungen": "Settings", "Profile": "Profiles", "Über": "About",
        "&Datei": "&File", "&Gerät": "&Device", "&Ansicht": "&View", "&Profile": "&Profiles", "&Hilfe": "&Help",
        "&Beenden": "&Quit", "Geräte &aktualisieren": "&Refresh devices", "&Sicheres Profil anwenden": "Apply &safe profile",
        "&Berechtigungen reparieren": "&Repair permissions", "Profile verwalten": "Manage profiles", "&Tastaturbedienung": "&Keyboard controls",
        "Zum Bereich &Über": "Open &About", "Bereit": "Ready", "Systemzustand": "System status", "Gerät wird geprüft …": "Checking device …",
        "Geräte initialisieren": "Initialize devices", "Schnellprofile": "Quick profiles", "Anwenden": "Apply", "Leise": "Quiet",
        "Ausgeglichen": "Balanced", "Leistung": "Performance", "Maximum": "Maximum", "Manuelle Steuerung": "Manual control",
        "Pumpe": "Pump", "Radiatorlüfter": "Radiator fans", "&Pumpe anwenden": "Apply &pump", "&Lüfter anwenden": "Apply &fans",
        "Aktiver Kühlmodus": "Active cooling mode", "Pumpenkurve nach Wassertemperatur": "Pump curve by liquid temperature",
        "Lüfterkurve nach Wassertemperatur": "Fan curve by liquid temperature", "&Standardwerte": "&Defaults", "Kurve &anwenden": "Apply &curve",
        "AMD-AM5-Prozessorprofil und CPU-Temperatur-Assistenz": "AMD AM5 CPU profile and CPU temperature assist",
        "Bitte Prozessor auswählen": "Select processor", "CPU &automatisch erkennen": "&Detect CPU automatically",
        "Profil und empfohlene Kraken-Kurven &laden": "&Load profile and recommended Kraken curves",
        "Prozessor": "Processor", "Kraken-Wassertemperatur – Sicherheitsgrenzen": "Kraken liquid temperature – safety limits",
        "Warnung ab": "Warning at", "Kritisch ab": "Critical at", "Bei kritischer Wassertemperatur automatisch 100 % setzen": "Set 100% automatically at critical liquid temperature",
        "Sicheres Standardprofil anwenden · 65 % / 65 %": "Apply safe default profile · 65% / 65%", "Beleuchtung": "Lighting",
        "Kanal": "Channel", "Effekt": "Effect", "Geschwindigkeit": "Speed", "Richtung": "Direction", "Farben": "Colors", "RGB anwenden": "Apply RGB",
        "Eigenes Bild": "Custom image", "PNG, JPG oder GIF auswählen": "Select PNG, JPG or GIF", "Kein Bild ausgewählt": "No image selected",
        "Bild einmal übertragen": "Upload image once", "Automatisch erneut senden (Fallback)": "Automatically resend (fallback)",
        "Helligkeit": "Brightness", "Ausrichtung": "Orientation", "Helligkeit und Ausrichtung anwenden": "Apply brightness and orientation",
        "Zur Flüssigkeitstemperatur zurück": "Return to liquid temperature", "Uhr auf dem LCD": "Clock on LCD", "Zeitformat": "Time format",
        "Datum unter der Uhrzeit anzeigen": "Show date below time", "Schriftgröße": "Font size", "Uhr automatisch erneut senden": "Automatically resend clock",
        "Erneut senden alle": "Resend every", "Vorschau": "Preview", "Uhr starten": "Start clock", "Uhr anhalten": "Stop clock",
        "Automatisches Wiederherstellen": "Automatic restore", "Gewähltes Bild beim Programmstart wieder anzeigen": "Restore selected image at application startup",
        "Design": "Design", "Darstellung": "Appearance", "Systemmodus": "System mode", "Hell": "Light", "Dunkel": "Dark",
        "Eigene Akzentfarbe": "Custom accent color", "Farbe auswählen": "Choose color", "Voreinstellungen": "Presets", "Design anwenden": "Apply design",
        "Anzeige und DPI": "Display and DPI", "Monitor wird erkannt …": "Detecting monitor …", "Automatisch an Monitor und Seitenverhältnis anpassen": "Automatically adapt to monitor and aspect ratio",
        "App-Skalierung": "App scaling", "Layoutvorgabe": "Layout preset", "Automatisch": "Automatic", "Kompakt · 16:10": "Compact · 16:10",
        "Standard · 16:9": "Standard · 16:9", "Ultrawide · 21:9": "Ultrawide · 21:9", "Super-Ultrawide · 32:9": "Super ultrawide · 32:9",
        "Monitor neu erkennen": "Detect monitor again", "Anzeige anwenden": "Apply display settings", "Animierter Hintergrund": "Animated background",
        "Animation aktivieren": "Enable animation", "Pausieren, wenn die App nicht aktiv ist": "Pause when app is inactive", "Hintergrund anwenden": "Apply background",
        "Animation ausschalten": "Disable animation", "Thema": "Theme", "Bildrate": "Frame rate", "Intensität": "Intensity",
        "Programm": "Application", "Mit dem Desktop starten": "Start with desktop", "Beim Schließen im Infobereich weiterlaufen": "Keep running in system tray when closing",
        "Status-Aktualisierung": "Status refresh", "Einrichtungsassistent erneut starten": "Run setup wizard again", "Abhängigkeiten": "Dependencies",
        "Wird geprüft …": "Checking …", "Abhängigkeiten &prüfen": "&Check dependencies", "Fehlende Pakete &installieren": "&Install missing packages",
        "Gerätezugriff": "Device access", "Zugriff ohne sudo &testen": "&Test access without sudo", "Berechtigungen mit Administratorabfrage &reparieren": "&Repair permissions with administrator prompt",
        "Hinweis": "Notice", "Profil beim Start": "Profile at startup", "Automatisch laden": "Load automatically", "Kein automatisches Profil": "No automatic profile",
        "Zuletzt verwendetes Profil": "Last used profile", "Profil erstellen oder aktualisieren": "Create or update profile", "Name": "Name", "Kategorie": "Category",
        "Beschreibung": "Description", "Als neues Profil speichern": "Save as new profile", "Ausgewähltes Profil aktualisieren": "Update selected profile",
        "Profil anwenden": "Apply profile", "Duplizieren": "Duplicate", "Umbenennen": "Rename", "Löschen": "Delete", "Importieren": "Import", "Exportieren": "Export",
        "Noch kein Profil ausgewählt.": "No profile selected yet.", "Kraken Control by Frelidon": "Kraken Control by Frelidon",
        "Komponenten- und Laufzeitversionen": "Component and runtime versions", "Unterstützte Geräte und offizielle Herstellerseiten": "Supported devices and official manufacturer pages",
        "Verwendete Software – Website, Quellcode und Lizenz": "Software used – website, source code and license", "Entwicklung und KI-Unterstützung": "Development and AI assistance",
        "Lizenz von Kraken Control": "Kraken Control license", "Projektumfang – bewusst auf die Kraken begrenzt": "Project scope – intentionally limited to Kraken",
        "Log leeren": "Clear log", "Alles kopieren": "Copy all", "Log speichern": "Save log", "Sprache": "Language", "Sprache der Oberfläche": "Interface language",
        "Experimentalhinweise und LCD-Sicherheit": "Experimental notices and LCD safety", "Experimentalhinweise zurücksetzen": "Reset experimental notices",
        "Hinweise bestätigt": "Notices acknowledged", "Hinweise werden wieder angezeigt": "Notices will be shown again",
    },
    "es": {
        "Übersicht": "Resumen", "Kühlung": "Refrigeración", "Einstellungen": "Ajustes", "Profile": "Perfiles", "Über": "Acerca de",
        "&Datei": "&Archivo", "&Gerät": "&Dispositivo", "&Ansicht": "&Vista", "&Profile": "&Perfiles", "&Hilfe": "A&yuda",
        "&Beenden": "&Salir", "Geräte &aktualisieren": "&Actualizar dispositivos", "Bereit": "Listo", "Systemzustand": "Estado del sistema",
        "Gerät wird geprüft …": "Comprobando dispositivo …", "Geräte initialisieren": "Inicializar dispositivos", "Schnellprofile": "Perfiles rápidos",
        "Anwenden": "Aplicar", "Leise": "Silencioso", "Ausgeglichen": "Equilibrado", "Leistung": "Rendimiento", "Maximum": "Máximo",
        "Manuelle Steuerung": "Control manual", "Pumpe": "Bomba", "Radiatorlüfter": "Ventiladores del radiador", "&Pumpe anwenden": "Aplicar &bomba",
        "&Lüfter anwenden": "Aplicar &ventiladores", "Aktiver Kühlmodus": "Modo de refrigeración activo", "Pumpenkurve nach Wassertemperatur": "Curva de bomba por temperatura del líquido",
        "Lüfterkurve nach Wassertemperatur": "Curva de ventiladores por temperatura del líquido", "&Standardwerte": "Valores &predeterminados", "Kurve &anwenden": "&Aplicar curva",
        "AMD-AM5-Prozessorprofil und CPU-Temperatur-Assistenz": "Perfil de CPU AMD AM5 y asistencia por temperatura de CPU", "Bitte Prozessor auswählen": "Seleccionar procesador",
        "CPU &automatisch erkennen": "Detectar CPU &automáticamente", "Profil und empfohlene Kraken-Kurven &laden": "&Cargar perfil y curvas Kraken recomendadas", "Prozessor": "Procesador",
        "Kraken-Wassertemperatur – Sicherheitsgrenzen": "Temperatura del líquido Kraken – límites de seguridad", "Warnung ab": "Aviso desde", "Kritisch ab": "Crítico desde",
        "Bei kritischer Wassertemperatur automatisch 100 % setzen": "Establecer 100% automáticamente con temperatura crítica del líquido",
        "Sicheres Standardprofil anwenden · 65 % / 65 %": "Aplicar perfil seguro predeterminado · 65% / 65%", "Beleuchtung": "Iluminación", "Kanal": "Canal",
        "Effekt": "Efecto", "Geschwindigkeit": "Velocidad", "Richtung": "Dirección", "Farben": "Colores", "RGB anwenden": "Aplicar RGB", "Eigenes Bild": "Imagen personalizada",
        "PNG, JPG oder GIF auswählen": "Seleccionar PNG, JPG o GIF", "Kein Bild ausgewählt": "Ninguna imagen seleccionada", "Bild einmal übertragen": "Enviar imagen una vez",
        "Automatisch erneut senden (Fallback)": "Reenviar automáticamente (respaldo)", "Helligkeit": "Brillo", "Ausrichtung": "Orientación",
        "Helligkeit und Ausrichtung anwenden": "Aplicar brillo y orientación", "Zur Flüssigkeitstemperatur zurück": "Volver a temperatura del líquido", "Uhr auf dem LCD": "Reloj en LCD",
        "Zeitformat": "Formato de hora", "Datum unter der Uhrzeit anzeigen": "Mostrar fecha debajo de la hora", "Schriftgröße": "Tamaño de fuente",
        "Uhr automatisch erneut senden": "Reenviar reloj automáticamente", "Erneut senden alle": "Reenviar cada", "Vorschau": "Vista previa", "Uhr starten": "Iniciar reloj", "Uhr anhalten": "Detener reloj",
        "Automatisches Wiederherstellen": "Restauración automática", "Gewähltes Bild beim Programmstart wieder anzeigen": "Restaurar imagen seleccionada al iniciar la aplicación",
        "Design": "Diseño", "Darstellung": "Apariencia", "Systemmodus": "Modo del sistema", "Hell": "Claro", "Dunkel": "Oscuro", "Eigene Akzentfarbe": "Color de acento personalizado",
        "Farbe auswählen": "Elegir color", "Voreinstellungen": "Preajustes", "Design anwenden": "Aplicar diseño", "Anzeige und DPI": "Pantalla y DPI", "Monitor wird erkannt …": "Detectando monitor …",
        "Automatisch an Monitor und Seitenverhältnis anpassen": "Adaptar automáticamente al monitor y relación de aspecto", "App-Skalierung": "Escala de la aplicación", "Layoutvorgabe": "Preajuste de diseño",
        "Automatisch": "Automático", "Monitor neu erkennen": "Detectar monitor de nuevo", "Anzeige anwenden": "Aplicar pantalla", "Animierter Hintergrund": "Fondo animado",
        "Animation aktivieren": "Activar animación", "Pausieren, wenn die App nicht aktiv ist": "Pausar cuando la aplicación esté inactiva", "Hintergrund anwenden": "Aplicar fondo",
        "Animation ausschalten": "Desactivar animación", "Thema": "Tema", "Bildrate": "Fotogramas", "Intensität": "Intensidad", "Programm": "Programa",
        "Mit dem Desktop starten": "Iniciar con el escritorio", "Beim Schließen im Infobereich weiterlaufen": "Seguir ejecutándose en la bandeja al cerrar", "Status-Aktualisierung": "Actualización de estado",
        "Einrichtungsassistent erneut starten": "Ejecutar de nuevo el asistente", "Abhängigkeiten": "Dependencias", "Wird geprüft …": "Comprobando …", "Abhängigkeiten &prüfen": "&Comprobar dependencias",
        "Fehlende Pakete &installieren": "&Instalar paquetes faltantes", "Gerätezugriff": "Acceso al dispositivo", "Zugriff ohne sudo &testen": "&Probar acceso sin sudo",
        "Berechtigungen mit Administratorabfrage &reparieren": "&Reparar permisos con autorización de administrador", "Hinweis": "Aviso", "Profil beim Start": "Perfil al iniciar",
        "Automatisch laden": "Cargar automáticamente", "Kein automatisches Profil": "Sin perfil automático", "Zuletzt verwendetes Profil": "Último perfil usado",
        "Profil erstellen oder aktualisieren": "Crear o actualizar perfil", "Name": "Nombre", "Kategorie": "Categoría", "Beschreibung": "Descripción", "Als neues Profil speichern": "Guardar como perfil nuevo",
        "Ausgewähltes Profil aktualisieren": "Actualizar perfil seleccionado", "Profil anwenden": "Aplicar perfil", "Duplizieren": "Duplicar", "Umbenennen": "Renombrar", "Löschen": "Eliminar",
        "Importieren": "Importar", "Exportieren": "Exportar", "Noch kein Profil ausgewählt.": "Aún no hay perfil seleccionado.", "Log leeren": "Vaciar registro", "Alles kopieren": "Copiar todo", "Log speichern": "Guardar registro",
        "Sprache": "Idioma", "Sprache der Oberfläche": "Idioma de la interfaz", "Experimentalhinweise und LCD-Sicherheit": "Avisos experimentales y seguridad LCD",
        "Experimentalhinweise zurücksetzen": "Restablecer avisos experimentales", "Hinweise bestätigt": "Avisos confirmados", "Hinweise werden wieder angezeigt": "Los avisos se mostrarán de nuevo",
    },
    "fr": {
        "Übersicht": "Vue d’ensemble", "Kühlung": "Refroidissement", "Einstellungen": "Paramètres", "Profile": "Profils", "Über": "À propos",
        "&Datei": "&Fichier", "&Gerät": "&Appareil", "&Ansicht": "&Affichage", "&Profile": "&Profils", "&Hilfe": "&Aide",
        "&Beenden": "&Quitter", "Geräte &aktualisieren": "&Actualiser les appareils", "Bereit": "Prêt", "Systemzustand": "État du système",
        "Gerät wird geprüft …": "Vérification de l’appareil …", "Geräte initialisieren": "Initialiser les appareils", "Schnellprofile": "Profils rapides",
        "Anwenden": "Appliquer", "Leise": "Silencieux", "Ausgeglichen": "Équilibré", "Leistung": "Performance", "Maximum": "Maximum",
        "Manuelle Steuerung": "Contrôle manuel", "Pumpe": "Pompe", "Radiatorlüfter": "Ventilateurs du radiateur", "&Pumpe anwenden": "Appliquer la &pompe",
        "&Lüfter anwenden": "Appliquer les &ventilateurs", "Aktiver Kühlmodus": "Mode de refroidissement actif", "Pumpenkurve nach Wassertemperatur": "Courbe de pompe selon la température du liquide",
        "Lüfterkurve nach Wassertemperatur": "Courbe des ventilateurs selon la température du liquide", "&Standardwerte": "Valeurs par &défaut", "Kurve &anwenden": "&Appliquer la courbe",
        "AMD-AM5-Prozessorprofil und CPU-Temperatur-Assistenz": "Profil CPU AMD AM5 et assistance selon la température CPU", "Bitte Prozessor auswählen": "Sélectionner le processeur",
        "CPU &automatisch erkennen": "Détecter le CPU &automatiquement", "Profil und empfohlene Kraken-Kurven &laden": "&Charger le profil et les courbes Kraken recommandées", "Prozessor": "Processeur",
        "Kraken-Wassertemperatur – Sicherheitsgrenzen": "Température du liquide Kraken – limites de sécurité", "Warnung ab": "Alerte à", "Kritisch ab": "Critique à",
        "Bei kritischer Wassertemperatur automatisch 100 % setzen": "Passer automatiquement à 100 % à température critique du liquide",
        "Sicheres Standardprofil anwenden · 65 % / 65 %": "Appliquer le profil sûr par défaut · 65 % / 65 %", "Beleuchtung": "Éclairage", "Kanal": "Canal",
        "Effekt": "Effet", "Geschwindigkeit": "Vitesse", "Richtung": "Direction", "Farben": "Couleurs", "RGB anwenden": "Appliquer RGB", "Eigenes Bild": "Image personnalisée",
        "PNG, JPG oder GIF auswählen": "Sélectionner PNG, JPG ou GIF", "Kein Bild ausgewählt": "Aucune image sélectionnée", "Bild einmal übertragen": "Envoyer l’image une fois",
        "Automatisch erneut senden (Fallback)": "Renvoyer automatiquement (secours)", "Helligkeit": "Luminosité", "Ausrichtung": "Orientation",
        "Helligkeit und Ausrichtung anwenden": "Appliquer luminosité et orientation", "Zur Flüssigkeitstemperatur zurück": "Revenir à la température du liquide", "Uhr auf dem LCD": "Horloge sur l’écran LCD",
        "Zeitformat": "Format de l’heure", "Datum unter der Uhrzeit anzeigen": "Afficher la date sous l’heure", "Schriftgröße": "Taille de police",
        "Uhr automatisch erneut senden": "Renvoyer automatiquement l’horloge", "Erneut senden alle": "Renvoyer toutes les", "Vorschau": "Aperçu", "Uhr starten": "Démarrer l’horloge", "Uhr anhalten": "Arrêter l’horloge",
        "Automatisches Wiederherstellen": "Restauration automatique", "Gewähltes Bild beim Programmstart wieder anzeigen": "Restaurer l’image sélectionnée au démarrage",
        "Design": "Design", "Darstellung": "Apparence", "Systemmodus": "Mode système", "Hell": "Clair", "Dunkel": "Sombre", "Eigene Akzentfarbe": "Couleur d’accent personnalisée",
        "Farbe auswählen": "Choisir la couleur", "Voreinstellungen": "Préréglages", "Design anwenden": "Appliquer le design", "Anzeige und DPI": "Affichage et DPI", "Monitor wird erkannt …": "Détection de l’écran …",
        "Automatisch an Monitor und Seitenverhältnis anpassen": "Adapter automatiquement à l’écran et au format", "App-Skalierung": "Mise à l’échelle de l’application", "Layoutvorgabe": "Préréglage de mise en page",
        "Automatisch": "Automatique", "Monitor neu erkennen": "Redétecter l’écran", "Anzeige anwenden": "Appliquer l’affichage", "Animierter Hintergrund": "Arrière-plan animé",
        "Animation aktivieren": "Activer l’animation", "Pausieren, wenn die App nicht aktiv ist": "Mettre en pause lorsque l’application est inactive", "Hintergrund anwenden": "Appliquer l’arrière-plan",
        "Animation ausschalten": "Désactiver l’animation", "Thema": "Thème", "Bildrate": "Fréquence d’images", "Intensität": "Intensité", "Programm": "Programme",
        "Mit dem Desktop starten": "Démarrer avec le bureau", "Beim Schließen im Infobereich weiterlaufen": "Continuer dans la zone de notification à la fermeture", "Status-Aktualisierung": "Actualisation de l’état",
        "Einrichtungsassistent erneut starten": "Relancer l’assistant de configuration", "Abhängigkeiten": "Dépendances", "Wird geprüft …": "Vérification …", "Abhängigkeiten &prüfen": "&Vérifier les dépendances",
        "Fehlende Pakete &installieren": "&Installer les paquets manquants", "Gerätezugriff": "Accès à l’appareil", "Zugriff ohne sudo &testen": "&Tester l’accès sans sudo",
        "Berechtigungen mit Administratorabfrage &reparieren": "&Réparer les permissions avec autorisation administrateur", "Hinweis": "Remarque", "Profil beim Start": "Profil au démarrage",
        "Automatisch laden": "Charger automatiquement", "Kein automatisches Profil": "Aucun profil automatique", "Zuletzt verwendetes Profil": "Dernier profil utilisé",
        "Profil erstellen oder aktualisieren": "Créer ou mettre à jour un profil", "Name": "Nom", "Kategorie": "Catégorie", "Beschreibung": "Description", "Als neues Profil speichern": "Enregistrer comme nouveau profil",
        "Ausgewähltes Profil aktualisieren": "Mettre à jour le profil sélectionné", "Profil anwenden": "Appliquer le profil", "Duplizieren": "Dupliquer", "Umbenennen": "Renommer", "Löschen": "Supprimer",
        "Importieren": "Importer", "Exportieren": "Exporter", "Noch kein Profil ausgewählt.": "Aucun profil sélectionné.", "Log leeren": "Effacer le journal", "Alles kopieren": "Tout copier", "Log speichern": "Enregistrer le journal",
        "Sprache": "Langue", "Sprache der Oberfläche": "Langue de l’interface", "Experimentalhinweise und LCD-Sicherheit": "Avertissements expérimentaux et sécurité LCD",
        "Experimentalhinweise zurücksetzen": "Réinitialiser les avertissements expérimentaux", "Hinweise bestätigt": "Avertissements confirmés", "Hinweise werden wieder angezeigt": "Les avertissements seront de nouveau affichés",
    },
}

UI_TRANSLATIONS["en"].update({
    "Unabhängige Open-Source-Steuerung · NZXT Kraken 2023 · liquidctl": "Independent open-source control · NZXT Kraken 2023 · liquidctl",
    "● Suche Geräte …": "● Searching for devices …", "↻ &Aktualisieren": "↻ &Refresh",
    "Kraken-Wassertemperatur": "Kraken liquid temperature", "CPU-Temperatur": "CPU temperature", "Firmware": "Firmware",
    "Sensor in der Pumpeneinheit": "Sensor in pump unit", "Wasser °C": "Liquid °C", "Leistung %": "Power %", "Typ": "Type",
    "24 Stunden · 13:30": "24 hour · 13:30", "12 Stunden · 1:30 PM": "12 hour · 1:30 PM",
    "Runde LCD-Vorschau · 240 × 240": "Round LCD preview · 240 × 240", "LCD-Modus: bereit": "LCD mode: ready",
})
UI_TRANSLATIONS["es"].update({
    "Unabhängige Open-Source-Steuerung · NZXT Kraken 2023 · liquidctl": "Control independiente de código abierto · NZXT Kraken 2023 · liquidctl",
    "● Suche Geräte …": "● Buscando dispositivos …", "↻ &Aktualisieren": "↻ &Actualizar",
    "Kraken-Wassertemperatur": "Temperatura del líquido Kraken", "CPU-Temperatur": "Temperatura de CPU", "Firmware": "Firmware",
    "Sensor in der Pumpeneinheit": "Sensor en la unidad de bomba", "Wasser °C": "Líquido °C", "Leistung %": "Potencia %", "Typ": "Tipo",
    "24 Stunden · 13:30": "24 horas · 13:30", "12 Stunden · 1:30 PM": "12 horas · 1:30 PM",
    "Runde LCD-Vorschau · 240 × 240": "Vista previa LCD circular · 240 × 240", "LCD-Modus: bereit": "Modo LCD: listo",
})
UI_TRANSLATIONS["fr"].update({
    "Unabhängige Open-Source-Steuerung · NZXT Kraken 2023 · liquidctl": "Contrôle open source indépendant · NZXT Kraken 2023 · liquidctl",
    "● Suche Geräte …": "● Recherche des appareils …", "↻ &Aktualisieren": "↻ &Actualiser",
    "Kraken-Wassertemperatur": "Température du liquide Kraken", "CPU-Temperatur": "Température CPU", "Firmware": "Firmware",
    "Sensor in der Pumpeneinheit": "Capteur dans l’unité de pompe", "Wasser °C": "Liquide °C", "Leistung %": "Puissance %", "Typ": "Type",
    "24 Stunden · 13:30": "24 heures · 13:30", "12 Stunden · 1:30 PM": "12 heures · 1:30 PM",
    "Runde LCD-Vorschau · 240 × 240": "Aperçu LCD circulaire · 240 × 240", "LCD-Modus: bereit": "Mode LCD : prêt",
})


# 2.9.20: simplified CAM-near GIF controls with diagnostics kept under Advanced.
UI_TRANSLATIONS["en"].update({
    "Beim Systemstart minimiert/im Tray starten": "Start minimized/in the system tray at system login",
    "GIF-Animation · Firmware 2.x · Experimentell": "GIF animation · Firmware 2.x · Experimental",
    "GIF-Bildrate": "GIF frame rate",
    "CAM-nah · automatisch · empfohlen · max. 25 FPS": "CAM-near · automatic · recommended · max. 25 FPS",
    "Erweiterte GIF-Optionen anzeigen": "Show advanced GIF options",
    "Bewegungsglättung (Motion-Interpolation)": "Motion smoothing (motion interpolation)",
    "GIF-Animation starten · Experimentell": "Start GIF animation · Experimental",
    "Animation stoppen": "Stop animation",
    "GIF-Stream: bereit": "GIF stream: ready",
})
UI_TRANSLATIONS["es"].update({
    "Beim Systemstart minimiert/im Tray starten": "Iniciar minimizado/en la bandeja al iniciar el sistema",
    "GIF-Animation · Firmware 2.x · Experimentell": "Animación GIF · Firmware 2.x · Experimental",
    "GIF-Bildrate": "Frecuencia del GIF",
    "CAM-nah · automatisch · empfohlen · max. 25 FPS": "Similar a CAM · automático · recomendado · máx. 25 FPS",
    "Erweiterte GIF-Optionen anzeigen": "Mostrar opciones GIF avanzadas",
    "Bewegungsglättung (Motion-Interpolation)": "Suavizado de movimiento (interpolación de movimiento)",
    "GIF-Animation starten · Experimentell": "Iniciar animación GIF · Experimental",
    "Animation stoppen": "Detener animación",
    "GIF-Stream: bereit": "Flujo GIF: listo",
})
UI_TRANSLATIONS["fr"].update({
    "Beim Systemstart minimiert/im Tray starten": "Démarrer minimisé/dans la zone de notification au démarrage du système",
    "GIF-Animation · Firmware 2.x · Experimentell": "Animation GIF · Firmware 2.x · Expérimental",
    "GIF-Bildrate": "Fréquence du GIF",
    "CAM-nah · automatisch · empfohlen · max. 25 FPS": "Proche de CAM · automatique · recommandé · max. 25 FPS",
    "Erweiterte GIF-Optionen anzeigen": "Afficher les options GIF avancées",
    "Bewegungsglättung (Motion-Interpolation)": "Lissage du mouvement (interpolation de mouvement)",
    "GIF-Animation starten · Experimentell": "Démarrer l’animation GIF · Expérimental",
    "Animation stoppen": "Arrêter l’animation",
    "GIF-Stream: bereit": "Flux GIF : prêt",
})

# 2.9.20: CAM/raw transport-mode labels.
UI_TRANSLATIONS["en"].update({
    'LCD-Transport': 'LCD transport',
    '25,6 Hz · Sicher · bewährt': '25.6 Hz · Safe · proven',
    'CAM-Takt · 26,667 Hz · phasenstabil · Standard': 'CAM cadence · 26.667 Hz · phase-stable · Standard',
})
UI_TRANSLATIONS["es"].update({
    'LCD-Transport': 'Transporte LCD',
    '25,6 Hz · Sicher · bewährt': '25,6 Hz · Seguro · probado',
    'CAM-Takt · 26,667 Hz · phasenstabil · Standard': 'Ritmo CAM · 26,667 Hz · fase estable · Estándar',
})
UI_TRANSLATIONS["fr"].update({
    'LCD-Transport': 'Transport LCD',
    '25,6 Hz · Sicher · bewährt': '25,6 Hz · Sûr · éprouvé',
    'CAM-Takt · 26,667 Hz · phasenstabil · Standard': 'Cadence CAM · 26,667 Hz · phase stable · Standard',
})

# 2.9.21: complete menu/control switching and rounded live hardware dashboards.
UI_TRANSLATIONS["en"].update({
    "Sicher": "Safe", "Beenden": "Quit", "Displayeinstellungen": "Display settings", "Schnellfarben": "Quick colors",
    "Kraken-Wassertemperatur": "Kraken liquid temperature", "CPU-Temperatur": "CPU temperature", "GPU-Temperatur": "GPU temperature",
    "Sensor in der Pumpeneinheit": "Sensor in pump unit", "AMD amdgpu · dedizierte GPU bevorzugt": "AMD amdgpu · dedicated GPU preferred",
    "Runde LCD-Vorschau · 240 × 240": "Round LCD preview · 240 × 240", "Vorschau nicht verfügbar": "Preview unavailable",
    "Hardwaredaten-Designs · Live": "Hardware data designs · Live", "Layout": "Layout", "Farbvoreinstellung": "Color preset",
    "Hex-Farbwert": "Hex color value", "Aktualisierung": "Refresh", "Designvorschau": "Design preview",
    "Live-Design starten": "Start live design", "Live-Design anhalten": "Stop live design", "Eigener Farbwert": "Custom color value",
    "Wasser · Halo": "Liquid · Halo", "CPU · Orbit": "CPU · Orbit", "GPU · Arc": "GPU · Arc",
    "CPU + GPU · Dual": "CPU + GPU · Dual", "Wasser + CPU + GPU · Trio": "Liquid + CPU + GPU · Trio",
    "Eisblau": "Ice blue", "Neongrün": "Neon green", "Weiß": "White", "Rot": "Red", "Gold": "Gold", "Grün": "Green", "Lila": "Purple", "Orange": "Orange", "Blau": "Blue",
    "Live-Hardwaredesign: bereit · Eisblau ist die Standardfarbe.": "Live hardware design: ready · Ice blue is the default color.",
    "Live-Hardwaredesign": "Live hardware design", "Live-Hardwaredesign aktiv": "Live hardware design active",
    "Live-Hardwaredesign angehalten": "Live hardware design stopped", "Live aktiv": "Live active", "Aktualisierung alle": "Refresh every", "Sekunden": "seconds",
    "Designvorschau aktualisiert · noch nicht auf das LCD übertragen.": "Design preview updated · not uploaded to the LCD yet.",
    "Die Designvorschau konnte nicht erzeugt werden:": "The design preview could not be created:",
    "LCD-Akzentfarbe auswählen": "Choose LCD accent color", "Experimentelles Live-Hardwaredesign": "Experimental live hardware design",
    "Bitte einen gültigen Hex-Farbwert im Format #RRGGBB eingeben.": "Enter a valid hex color in #RRGGBB format.",
    "Die Kraken ist noch nicht verbunden.": "The Kraken is not connected yet.",
    "Der LCD-Sicherheitsmodus wartet noch auf die Wiederherstellung der Flüssigkeitstemperatur.": "LCD safety mode is still waiting to restore the liquid-temperature screen.",
    "Text": "Text", "Hintergrund": "Background", "Farbe 1": "Color 1", "Farbe 2": "Color 2",
    "Gesamt": "All", "Statisch": "Static", "Aus": "Off", "Überblenden": "Fading", "Pulsieren": "Pulse", "Atmen": "Breathing",
    "Kerze": "Candle", "Sternennacht": "Starry night", "Spektrum-Welle": "Spectrum wave", "Regenbogenfluss": "Rainbow flow",
    "Super-Regenbogen": "Super rainbow", "Regenbogen-Puls": "Rainbow pulse", "Abwechselnd": "Alternating", "Bewegend abwechselnd": "Moving alternating", "Flügel": "Wings",
    "Am langsamsten": "Slowest", "Langsamer": "Slower", "Normal": "Normal", "Schneller": "Faster", "Am schnellsten": "Fastest", "Vorwärts": "Forward", "Rückwärts": "Backward",
    "24 FPS Inhalt": "24 FPS content", "25 FPS Inhalt · empfohlen": "25 FPS content · recommended", "Status aktuell": "Status current",
})
UI_TRANSLATIONS["es"].update({
    "&Sicheres Profil anwenden": "Aplicar perfil &seguro", "&Berechtigungen reparieren": "&Reparar permisos", "Profile verwalten": "Gestionar perfiles",
    "&Tastaturbedienung": "&Control por teclado", "Zum Bereich &Über": "Abrir &Acerca de", "Sicher": "Seguro", "Beenden": "Salir",
    "Displayeinstellungen": "Ajustes de pantalla", "Schnellfarben": "Colores rápidos", "Kraken-Wassertemperatur": "Temperatura del líquido Kraken",
    "CPU-Temperatur": "Temperatura de CPU", "GPU-Temperatur": "Temperatura de GPU", "Sensor in der Pumpeneinheit": "Sensor en la unidad de bomba",
    "AMD amdgpu · dedizierte GPU bevorzugt": "AMD amdgpu · GPU dedicada preferida", "Runde LCD-Vorschau · 240 × 240": "Vista previa LCD redonda · 240 × 240",
    "Vorschau nicht verfügbar": "Vista previa no disponible", "Hardwaredaten-Designs · Live": "Diseños de datos de hardware · En vivo", "Layout": "Diseño",
    "Farbvoreinstellung": "Color predefinido", "Hex-Farbwert": "Valor de color hexadecimal", "Aktualisierung": "Actualización", "Designvorschau": "Vista previa del diseño",
    "Live-Design starten": "Iniciar diseño en vivo", "Live-Design anhalten": "Detener diseño en vivo", "Eigener Farbwert": "Color personalizado",
    "Wasser · Halo": "Líquido · Halo", "CPU · Orbit": "CPU · Órbita", "GPU · Arc": "GPU · Arco", "CPU + GPU · Dual": "CPU + GPU · Dual",
    "Wasser + CPU + GPU · Trio": "Líquido + CPU + GPU · Trío", "Eisblau": "Azul hielo", "Neongrün": "Verde neón", "Weiß": "Blanco", "Rot": "Rojo", "Gold": "Dorado", "Grün": "Verde", "Lila": "Morado", "Orange": "Naranja", "Blau": "Azul",
    "Live-Hardwaredesign: bereit · Eisblau ist die Standardfarbe.": "Diseño de hardware en vivo: listo · Azul hielo es el color predeterminado.",
    "Live-Hardwaredesign": "Diseño de hardware en vivo", "Live-Hardwaredesign aktiv": "Diseño de hardware en vivo activo", "Live-Hardwaredesign angehalten": "Diseño de hardware en vivo detenido",
    "Live aktiv": "En vivo activo", "Aktualisierung alle": "Actualizar cada", "Sekunden": "segundos", "Designvorschau aktualisiert · noch nicht auf das LCD übertragen.": "Vista previa actualizada · aún no enviada al LCD.",
    "Die Designvorschau konnte nicht erzeugt werden:": "No se pudo crear la vista previa del diseño:", "LCD-Akzentfarbe auswählen": "Elegir color de acento del LCD",
    "Experimentelles Live-Hardwaredesign": "Diseño de hardware en vivo experimental", "Bitte einen gültigen Hex-Farbwert im Format #RRGGBB eingeben.": "Introduce un color hexadecimal válido en formato #RRGGBB.",
    "Die Kraken ist noch nicht verbunden.": "La Kraken aún no está conectada.", "Der LCD-Sicherheitsmodus wartet noch auf die Wiederherstellung der Flüssigkeitstemperatur.": "El modo de seguridad LCD aún espera restaurar la pantalla de temperatura del líquido.",
    "Text": "Texto", "Hintergrund": "Fondo", "Farbe 1": "Color 1", "Farbe 2": "Color 2", "Gesamt": "Todo", "Statisch": "Estático", "Aus": "Apagado",
    "Überblenden": "Fundido", "Pulsieren": "Pulso", "Atmen": "Respiración", "Kerze": "Vela", "Sternennacht": "Noche estrellada", "Spektrum-Welle": "Onda de espectro",
    "Regenbogenfluss": "Flujo arcoíris", "Super-Regenbogen": "Súper arcoíris", "Regenbogen-Puls": "Pulso arcoíris", "Abwechselnd": "Alternado", "Bewegend abwechselnd": "Alternado móvil", "Flügel": "Alas",
    "Am langsamsten": "Más lento", "Langsamer": "Lento", "Normal": "Normal", "Schneller": "Rápido", "Am schnellsten": "Más rápido", "Vorwärts": "Adelante", "Rückwärts": "Atrás",
    "24 FPS Inhalt": "Contenido a 24 FPS", "25 FPS Inhalt · empfohlen": "Contenido a 25 FPS · recomendado", "Status aktuell": "Estado actualizado",
})
UI_TRANSLATIONS["fr"].update({
    "&Sicheres Profil anwenden": "Appliquer le profil &sûr", "&Berechtigungen reparieren": "&Réparer les autorisations", "Profile verwalten": "Gérer les profils",
    "&Tastaturbedienung": "&Commandes au clavier", "Zum Bereich &Über": "Ouvrir À &propos", "Sicher": "Sûr", "Beenden": "Quitter",
    "Displayeinstellungen": "Paramètres d’affichage", "Schnellfarben": "Couleurs rapides", "Kraken-Wassertemperatur": "Température du liquide Kraken",
    "CPU-Temperatur": "Température CPU", "GPU-Temperatur": "Température GPU", "Sensor in der Pumpeneinheit": "Capteur dans l’unité de pompe",
    "AMD amdgpu · dedizierte GPU bevorzugt": "AMD amdgpu · GPU dédiée privilégiée", "Runde LCD-Vorschau · 240 × 240": "Aperçu LCD rond · 240 × 240",
    "Vorschau nicht verfügbar": "Aperçu indisponible", "Hardwaredaten-Designs · Live": "Designs de données matérielles · En direct", "Layout": "Disposition",
    "Farbvoreinstellung": "Préréglage couleur", "Hex-Farbwert": "Valeur couleur hexadécimale", "Aktualisierung": "Actualisation", "Designvorschau": "Aperçu du design",
    "Live-Design starten": "Démarrer le design en direct", "Live-Design anhalten": "Arrêter le design en direct", "Eigener Farbwert": "Couleur personnalisée",
    "Wasser · Halo": "Liquide · Halo", "CPU · Orbit": "CPU · Orbite", "GPU · Arc": "GPU · Arc", "CPU + GPU · Dual": "CPU + GPU · Double",
    "Wasser + CPU + GPU · Trio": "Liquide + CPU + GPU · Trio", "Eisblau": "Bleu glacier", "Neongrün": "Vert néon", "Weiß": "Blanc", "Rot": "Rouge", "Gold": "Or", "Grün": "Vert", "Lila": "Violet", "Orange": "Orange", "Blau": "Bleu",
    "Live-Hardwaredesign: bereit · Eisblau ist die Standardfarbe.": "Design matériel en direct : prêt · Le bleu glacier est la couleur par défaut.",
    "Live-Hardwaredesign": "Design matériel en direct", "Live-Hardwaredesign aktiv": "Design matériel en direct actif", "Live-Hardwaredesign angehalten": "Design matériel en direct arrêté",
    "Live aktiv": "Direct actif", "Aktualisierung alle": "Actualisation toutes les", "Sekunden": "secondes", "Designvorschau aktualisiert · noch nicht auf das LCD übertragen.": "Aperçu actualisé · pas encore envoyé au LCD.",
    "Die Designvorschau konnte nicht erzeugt werden:": "Impossible de créer l’aperçu du design :", "LCD-Akzentfarbe auswählen": "Choisir la couleur d’accent du LCD",
    "Experimentelles Live-Hardwaredesign": "Design matériel en direct expérimental", "Bitte einen gültigen Hex-Farbwert im Format #RRGGBB eingeben.": "Saisissez une couleur hexadécimale valide au format #RRGGBB.",
    "Die Kraken ist noch nicht verbunden.": "Le Kraken n’est pas encore connecté.", "Der LCD-Sicherheitsmodus wartet noch auf die Wiederherstellung der Flüssigkeitstemperatur.": "Le mode de sécurité LCD attend encore la restauration de l’écran de température du liquide.",
    "Text": "Texte", "Hintergrund": "Arrière-plan", "Farbe 1": "Couleur 1", "Farbe 2": "Couleur 2", "Gesamt": "Tout", "Statisch": "Fixe", "Aus": "Désactivé",
    "Überblenden": "Fondu", "Pulsieren": "Pulsation", "Atmen": "Respiration", "Kerze": "Bougie", "Sternennacht": "Nuit étoilée", "Spektrum-Welle": "Onde spectrale",
    "Regenbogenfluss": "Flux arc-en-ciel", "Super-Regenbogen": "Super arc-en-ciel", "Regenbogen-Puls": "Pulsation arc-en-ciel", "Abwechselnd": "Alterné", "Bewegend abwechselnd": "Alterné mobile", "Flügel": "Ailes",
    "Am langsamsten": "Très lent", "Langsamer": "Lent", "Normal": "Normal", "Schneller": "Rapide", "Am schnellsten": "Très rapide", "Vorwärts": "Avant", "Rückwärts": "Arrière",
    "24 FPS Inhalt": "Contenu 24 FPS", "25 FPS Inhalt · empfohlen": "Contenu 25 FPS · recommandé", "Status aktuell": "État à jour",
})

UI_TRANSLATIONS["en"].update({
    "Zuletzt durch Kraken Control gesetzt: Pumpe unbekannt · Radiatorlüfter unbekannt": "Last set by Kraken Control: pump unknown · radiator fans unknown",
    "Ein fester Prozentwert oder ein Schnellprofil ersetzt die jeweilige Kurve in der Kraken-Firmware.": "A fixed percentage or quick profile replaces the respective curve in the Kraken firmware.",
    "Bei hoher CPU-Temperatur Kraken automatisch verstärken (mit 5 °C Hysterese)": "Automatically boost Kraken at high CPU temperature (with 5 °C hysteresis)",
    "Die CPU-Tjmax ist nicht die Wassertemperatur. Für die Kraken-Flüssigkeit gelten die separaten Grenzen unten.": "CPU Tjmax is not the liquid temperature. The separate limits below apply to Kraken liquid.",
    "CPU-Sensor: wird gesucht …": "CPU sensor: searching …", "Expertenmodus: Sicherheitsgrenzen frei einstellen": "Expert mode: freely adjust safety limits",
    "Diese Werte gelten ausschließlich für die Kraken-Flüssigkeit, nicht für die CPU. Eine CPU-Tjmax von 89 oder 95 °C darf niemals als Wassergrenze übernommen werden. Im normalen Modus bleiben vorsichtige Einstellbereiche aktiv.": "These values apply only to Kraken liquid, not the CPU. A CPU Tjmax of 89 or 95 °C must never be used as a liquid limit. Conservative ranges remain active in normal mode.",
    "Die drei F140/F120-RGB-Core-Lüfter werden über den separaten NZXT 2023 RGB Controller gesteuert.": "The three F140/F120 RGB Core fans are controlled through the separate NZXT 2023 RGB Controller.",
    "Die Hardware nimmt ein quadratisches 240×240-Bild an. Die Vorschau zeigt den tatsächlich sichtbaren runden Bereich.": "The hardware accepts a square 240×240 image. The preview shows the round area that is actually visible.",
    "Sicherheitshinweis: Der Fallback sendet das Bild wiederholt an die Kraken. Langzeitwirkungen auf den Displayspeicher sind nicht ausreichend bekannt. Nur aktivieren, wenn das Display wirklich zurückspringt; standardmäßig bleibt diese Funktion ausgeschaltet.": "Safety notice: fallback repeatedly sends the image to the Kraken. Long-term effects on display memory are not sufficiently known. Enable only if the display actually reverts; this feature is off by default.",
    "Einmalige GIF-Übertragung verwendet weiterhin nur das erste Bild. Der experimentelle Stream darunter emuliert Animation auf Firmware 2.x durch vorbereitete statische Frames über den liquidctl-Treiber.": "A one-time GIF upload still uses only the first frame. The experimental stream below emulates animation on firmware 2.x using prepared static frames through the liquidctl driver.",
    "Experimentell: Das Live-Design rendert Wasser-, CPU- und GPU-Sensordaten als statisches 240×240-Bild und überträgt es im gewählten Intervall. Die Mindestzeit beträgt 5 Sekunden; Langzeitwirkungen häufiger LCD-Uploads sind nicht ausreichend bekannt.": "Experimental: the live design renders liquid, CPU and GPU sensor data as a static 240×240 image and uploads it at the selected interval. The minimum is 5 seconds; long-term effects of frequent LCD uploads are not sufficiently known.",
    "Experimentell: Die Uhr überträgt einmal pro Minute ein neues statisches Bild. Langzeitwirkungen häufiger LCD-Uploads sind nicht ausreichend bekannt; Sekunden werden bewusst nicht übertragen.": "Experimental: the clock uploads a new static image once per minute. Long-term effects of frequent LCD uploads are not sufficiently known; seconds are intentionally omitted.",
    "Akzentvorschau · Schaltflächen, Tabs, Regler und Kurven": "Accent preview · buttons, tabs, sliders and curves",
    "Die App ändert nicht die Linux-Bildschirmauflösung. Qt arbeitet mit geräteunabhängigen Pixeln; hier werden App-Skalierung und responsives Layout angepasst.": "The app does not change the Linux screen resolution. Qt uses device-independent pixels; app scaling and the responsive layout are adjusted here.",
    "Bestätigte LCD-Hinweise werden dauerhaft gespeichert. Nach einem verdächtigen Absturz oder wiederholten LCD-Fehlern stoppt Kraken Control experimentelle LCD-Funktionen und versucht automatisch die Standardanzeige der Flüssigkeitstemperatur wiederherzustellen.": "Acknowledged LCD notices are stored permanently. After a suspicious crash or repeated LCD errors, Kraken Control stops experimental LCD features and automatically attempts to restore the default liquid-temperature screen.",
    "Open Hardware Control erkennt DNF, APT, Pacman und Zypper und installiert nach Bestätigung nur die fest zugeordneten Pakete aus bereits eingerichteten Quellen. Es werden keine fremden Paketquellen hinzugefügt.": "Open Hardware Control detects DNF, APT, Pacman and Zypper and, after confirmation, installs only fixed packages from already configured repositories. No third-party repositories are added.",
    "Schreibzugriff auf /dev/hidraw ist für Pumpen-, Lüfter- und Kurvenänderungen erforderlich. Nach einer neuen udev-Regel kann Ab- und Anstecken oder ein Neustart nötig sein.": "Write access to /dev/hidraw is required for pump, fan and curve changes. Reconnecting the device or restarting may be required after a new udev rule.",
    "Experimentelle Open-Source-Beta: Nutzung auf eigenes Risiko. Die Anwendung nutzt ausschließlich liquidctl. Die automatische Temperatursicherung wirkt nur, solange Programm, USB-Verbindung und Statusabfrage funktionieren. Wiederholte LCD-Uploads sind standardmäßig deaktiviert.": "Experimental open-source beta: use at your own risk. The application uses liquidctl exclusively. Automatic temperature protection works only while the program, USB connection and status polling are functioning. Repeated LCD uploads are disabled by default.",
    "Profile speichern Einstellungen kategorisiert. Gesamtprofile können Kühlung, LCD, RGB, Design, Hintergrund und Anzeige gemeinsam wiederherstellen.": "Profiles store settings by category. Full profiles can restore cooling, LCD, RGB, design, background and display together.",
    "Kühlungsprofile werden erst nach erfolgreicher Kraken-Erkennung übertragen.": "Cooling profiles are uploaded only after successful Kraken detection.",
    "z. B. Gaming, Leise Nacht oder Sommer": "e.g. Gaming, Quiet night or Summer", "Kurze Beschreibung": "Short description",
    "Öffentliches Projekt-Repository und Downloads: https://github.com/Frelidon/open-hardware-control": "Public project repository and downloads: https://github.com/Frelidon/open-hardware-control",
    "<b>Enthalten:</b> Wassertemperatur, Kraken-Pumpe, von der Kraken gemeldete beziehungsweise gesteuerte Radiatorlüfter, LCD, der separate NZXT 2023 RGB Controller sowie sicher kalibrierte Mainboard-/Gehäuselüfter über kompatibles Linux-hwmon.": "<b>Included:</b> liquid temperature, Kraken pump, radiator fans reported or controlled by the Kraken, LCD, and the separate NZXT 2023 RGB Controller.",
    "<b>Nicht enthalten:</b> GPU-Lüftersteuerung, AMD-Grafik-Tuning, Firmware-Updates, allgemeines Mainboard-Tuning sowie unbestätigte direkte Controllerzugriffe. Mainboard-/Gehäuselüfter werden nur über erkannte, schreibbare Linux-hwmon-Kanäle und nach physischer Kalibrierung geregelt.": "<b>Not included:</b> motherboard fan headers, additional case fans, GPU fans, AMD graphics controls, or general system tuning. Such features should be developed as separate tools and can later be connected through a shared interface.",
    "Projektleitung und Veröffentlichung: Frelidon. Mit Unterstützung von ChatGPT (GPT-5.6 Thinking) von OpenAI bei Programmierung, Dokumentation und Tests. ChatGPT ist kein Laufzeitbestandteil der App. Die Nennung stellt keine offizielle Unterstützung oder Partnerschaft durch OpenAI dar.": "Project lead and publication: Frelidon. With support from OpenAI's ChatGPT (GPT-5.6 Thinking) for programming, documentation and testing. ChatGPT is not a runtime component of the app. This mention does not imply official OpenAI support or partnership.",
    "AMD-AM5-Temperaturprofile": "AMD AM5 temperature profiles",
    "Die auswählbaren CPU-Profile nutzen die von AMD veröffentlichte maximale Betriebstemperatur (Tjmax). Ryzen 9000, Ryzen 8000G und normale Ryzen-7000-Modelle sind in den aufgenommenen Profilen mit 95 °C hinterlegt; Ryzen 7000 X3D mit 89 °C. Die Kraken-Wassergrenzen bleiben davon unabhängig.": "The selectable CPU profiles use AMD's published maximum operating temperature (Tjmax). Ryzen 9000, Ryzen 8000G and regular Ryzen 7000 models use 95 °C in the included profiles; Ryzen 7000 X3D uses 89 °C. Kraken liquid limits remain independent.",
    "Kraken Control by Frelidon steht unter GNU General Public License v3.0 oder später (GPL-3.0-or-later). Die vollständige Lizenz liegt dem Paket als LICENSE bei.": "Kraken Control by Frelidon is licensed under GNU General Public License v3.0 or later (GPL-3.0-or-later). The full license is included as LICENSE.",
    "liquidctl-Gerätename: NZXT Kraken 2023 · USB 1e71:300e · LCD 240×240 · Temperatur, Pumpe, Radiatorlüfter und LCD": "liquidctl device name: NZXT Kraken 2023 · USB 1e71:300e · LCD 240×240 · temperature, pump, radiator fans and LCD",
    "USB 1e71:2012 · separate RGB-Steuerung über liquidctl. Der Controller wird auf der offiziellen Kraken-(2023)-Seite als Bestandteil der RGB-Varianten aufgeführt.": "USB 1e71:2012 · separate RGB control through liquidctl. The controller is listed on the official Kraken (2023) page as part of the RGB variants.",
    "Kraken-Radiatorlüfter werden weiterhin über die Kraken gesteuert. Zusätzlich kann Open Hardware Control ab 3.4.23 physisch bestätigte Mainboard-/Gehäuselüfter über kompatible Linux-hwmon-PWM-Kanäle regeln. GPU-Lüfter werden nicht verändert.": "Only fans reported and controlled through the Kraken device as part of Kraken cooling are supported. Kraken Control does not access other fans installed in the PC.",
    "Alle Links öffnen sich im Standardbrowser. Das bloße Anzeigen dieser Seite überträgt keine Daten; erst das Anklicken eines Links öffnet die jeweilige externe Internetseite.": "All links open in the default browser. Merely viewing this page sends no data; an external website opens only after clicking a link.",
    "Dieses Protokoll erfasst Hardwarebefehle, Fehler, Schaltflächenklicks, Tastaturaktionen und vom Benutzer geänderte Einstellungen. Private Pfade und Kennungen werden weiterhin bereinigt.": "This log records hardware commands, errors, button clicks, keyboard actions and user-changed settings. Private paths and identifiers continue to be redacted.",
    "Das Live-Design überträgt im gewählten Intervall ein neues statisches Bild mit aktuellen Sensordaten. Die langfristige Wirkung häufiger Uploads auf den Displayspeicher ist nicht ausreichend bekannt. Live-Design trotzdem starten?": "The live design uploads a new static image with current sensor data at the selected interval. The long-term effect of frequent uploads on display memory is not sufficiently known. Start the live design anyway?",
})
UI_TRANSLATIONS["es"].update({
    "Kompakt · 16:10": "Compacto · 16:10", "Standard · 16:9": "Estándar · 16:9", "Ultrawide · 21:9": "Ultraancho · 21:9", "Super-Ultrawide · 32:9": "Súper ultraancho · 32:9",
    "Zuletzt durch Kraken Control gesetzt: Pumpe unbekannt · Radiatorlüfter unbekannt": "Último ajuste de Kraken Control: bomba desconocida · ventiladores desconocidos",
    "Ein fester Prozentwert oder ein Schnellprofil ersetzt die jeweilige Kurve in der Kraken-Firmware.": "Un porcentaje fijo o perfil rápido sustituye la curva correspondiente en el firmware de Kraken.",
    "Bei hoher CPU-Temperatur Kraken automatisch verstärken (mit 5 °C Hysterese)": "Reforzar Kraken automáticamente con temperatura alta de CPU (histéresis de 5 °C)",
    "Die CPU-Tjmax ist nicht die Wassertemperatur. Für die Kraken-Flüssigkeit gelten die separaten Grenzen unten.": "La Tjmax de CPU no es la temperatura del líquido. Se aplican los límites separados de abajo.",
    "CPU-Sensor: wird gesucht …": "Sensor de CPU: buscando …", "Expertenmodus: Sicherheitsgrenzen frei einstellen": "Modo experto: ajustar libremente los límites de seguridad",
    "Diese Werte gelten ausschließlich für die Kraken-Flüssigkeit, nicht für die CPU. Eine CPU-Tjmax von 89 oder 95 °C darf niemals als Wassergrenze übernommen werden. Im normalen Modus bleiben vorsichtige Einstellbereiche aktiv.": "Estos valores se aplican solo al líquido Kraken, no a la CPU. Una Tjmax de 89 o 95 °C nunca debe usarse como límite del líquido. En modo normal siguen activos rangos prudentes.",
    "Die drei F140/F120-RGB-Core-Lüfter werden über den separaten NZXT 2023 RGB Controller gesteuert.": "Los tres ventiladores F140/F120 RGB Core se controlan mediante el NZXT 2023 RGB Controller separado.",
    "Die Hardware nimmt ein quadratisches 240×240-Bild an. Die Vorschau zeigt den tatsächlich sichtbaren runden Bereich.": "El hardware acepta una imagen cuadrada de 240×240. La vista previa muestra el área redonda realmente visible.",
    "Sicherheitshinweis: Der Fallback sendet das Bild wiederholt an die Kraken. Langzeitwirkungen auf den Displayspeicher sind nicht ausreichend bekannt. Nur aktivieren, wenn das Display wirklich zurückspringt; standardmäßig bleibt diese Funktion ausgeschaltet.": "Aviso de seguridad: el respaldo envía la imagen repetidamente a Kraken. No se conocen suficientemente los efectos a largo plazo. Actívalo solo si la pantalla realmente vuelve atrás; está desactivado de forma predeterminada.",
    "Einmalige GIF-Übertragung verwendet weiterhin nur das erste Bild. Der experimentelle Stream darunter emuliert Animation auf Firmware 2.x durch vorbereitete statische Frames über den liquidctl-Treiber.": "La carga única de GIF sigue usando solo el primer fotograma. El flujo experimental emula la animación en firmware 2.x con fotogramas estáticos preparados mediante liquidctl.",
    "Experimentell: Das Live-Design rendert Wasser-, CPU- und GPU-Sensordaten als statisches 240×240-Bild und überträgt es im gewählten Intervall. Die Mindestzeit beträgt 5 Sekunden; Langzeitwirkungen häufiger LCD-Uploads sind nicht ausreichend bekannt.": "Experimental: el diseño en vivo renderiza los sensores de líquido, CPU y GPU como imagen estática de 240×240 y la envía en el intervalo elegido. El mínimo es 5 segundos; no se conocen suficientemente los efectos de cargas frecuentes.",
    "Experimentell: Die Uhr überträgt einmal pro Minute ein neues statisches Bild. Langzeitwirkungen häufiger LCD-Uploads sind nicht ausreichend bekannt; Sekunden werden bewusst nicht übertragen.": "Experimental: el reloj envía una imagen estática nueva una vez por minuto. No se conocen suficientemente los efectos a largo plazo; los segundos se omiten intencionadamente.",
    "Akzentvorschau · Schaltflächen, Tabs, Regler und Kurven": "Vista del acento · botones, pestañas, controles y curvas",
    "Die App ändert nicht die Linux-Bildschirmauflösung. Qt arbeitet mit geräteunabhängigen Pixeln; hier werden App-Skalierung und responsives Layout angepasst.": "La aplicación no cambia la resolución de Linux. Qt usa píxeles independientes del dispositivo; aquí se ajustan la escala y el diseño adaptable.",
    "Bestätigte LCD-Hinweise werden dauerhaft gespeichert. Nach einem verdächtigen Absturz oder wiederholten LCD-Fehlern stoppt Kraken Control experimentelle LCD-Funktionen und versucht automatisch die Standardanzeige der Flüssigkeitstemperatur wiederherzustellen.": "Los avisos LCD confirmados se guardan permanentemente. Tras un cierre sospechoso o errores repetidos, Kraken Control detiene las funciones experimentales e intenta restaurar la pantalla estándar del líquido.",
    "Open Hardware Control erkennt DNF, APT, Pacman und Zypper und installiert nach Bestätigung nur die fest zugeordneten Pakete aus bereits eingerichteten Quellen. Es werden keine fremden Paketquellen hinzugefügt.": "Open Hardware Control detecta DNF, APT, Pacman y Zypper e instala, tras confirmación, solo paquetes fijos de repositorios ya configurados. No se añaden repositorios externos.",
    "Schreibzugriff auf /dev/hidraw ist für Pumpen-, Lüfter- und Kurvenänderungen erforderlich. Nach einer neuen udev-Regel kann Ab- und Anstecken oder ein Neustart nötig sein.": "Se requiere escritura en /dev/hidraw para cambiar bomba, ventiladores y curvas. Tras una nueva regla udev puede ser necesario reconectar o reiniciar.",
    "Experimentelle Open-Source-Beta: Nutzung auf eigenes Risiko. Die Anwendung nutzt ausschließlich liquidctl. Die automatische Temperatursicherung wirkt nur, solange Programm, USB-Verbindung und Statusabfrage funktionieren. Wiederholte LCD-Uploads sind standardmäßig deaktiviert.": "Beta experimental de código abierto: uso bajo tu responsabilidad. La aplicación usa solo liquidctl. La protección automática funciona únicamente mientras programa, USB y consulta de estado funcionen. Las cargas LCD repetidas están desactivadas por defecto.",
    "Profile speichern Einstellungen kategorisiert. Gesamtprofile können Kühlung, LCD, RGB, Design, Hintergrund und Anzeige gemeinsam wiederherstellen.": "Los perfiles guardan ajustes por categoría. Los perfiles completos restauran refrigeración, LCD, RGB, diseño, fondo y pantalla juntos.",
    "Kühlungsprofile werden erst nach erfolgreicher Kraken-Erkennung übertragen.": "Los perfiles de refrigeración se envían solo tras detectar Kraken correctamente.",
    "z. B. Gaming, Leise Nacht oder Sommer": "p. ej., Juegos, Noche silenciosa o Verano", "Kurze Beschreibung": "Descripción breve",
    "Kraken Control by Frelidon": "Kraken Control by Frelidon", "Projektumfang – bewusst auf die Kraken begrenzt": "Alcance del proyecto: limitado deliberadamente a Kraken",
    "Entwicklung und KI-Unterstützung": "Desarrollo y asistencia de IA", "Verwendete Software – Website, Quellcode und Lizenz": "Software utilizada: web, código fuente y licencia",
    "Komponenten- und Laufzeitversionen": "Versiones de componentes y ejecución", "AMD-AM5-Temperaturprofile": "Perfiles de temperatura AMD AM5",
    "Lizenz von Kraken Control": "Licencia de Kraken Control", "Unterstützte Geräte und offizielle Herstellerseiten": "Dispositivos compatibles y páginas oficiales",
    "Öffentliches Projekt-Repository und Downloads: https://github.com/Frelidon/open-hardware-control": "Repositorio público y descargas: https://github.com/Frelidon/open-hardware-control",
    "<b>Enthalten:</b> Wassertemperatur, Kraken-Pumpe, von der Kraken gemeldete beziehungsweise gesteuerte Radiatorlüfter, LCD, der separate NZXT 2023 RGB Controller sowie sicher kalibrierte Mainboard-/Gehäuselüfter über kompatibles Linux-hwmon.": "<b>Incluye:</b> temperatura del líquido, bomba Kraken, ventiladores informados o controlados por Kraken, LCD y NZXT 2023 RGB Controller separado.",
    "<b>Nicht enthalten:</b> GPU-Lüftersteuerung, AMD-Grafik-Tuning, Firmware-Updates, allgemeines Mainboard-Tuning sowie unbestätigte direkte Controllerzugriffe. Mainboard-/Gehäuselüfter werden nur über erkannte, schreibbare Linux-hwmon-Kanäle und nach physischer Kalibrierung geregelt.": "<b>No incluye:</b> conectores de ventilador de placa, ventiladores de caja, ventiladores GPU, controles gráficos AMD ni ajuste general. Esas funciones se desarrollarán como herramientas separadas.",
    "Projektleitung und Veröffentlichung: Frelidon. Mit Unterstützung von ChatGPT (GPT-5.6 Thinking) von OpenAI bei Programmierung, Dokumentation und Tests. ChatGPT ist kein Laufzeitbestandteil der App. Die Nennung stellt keine offizielle Unterstützung oder Partnerschaft durch OpenAI dar.": "Dirección y publicación: Frelidon. Con ayuda de ChatGPT (GPT-5.6 Thinking) de OpenAI en programación, documentación y pruebas. ChatGPT no forma parte de la ejecución ni implica soporte oficial de OpenAI.",
    "Die auswählbaren CPU-Profile nutzen die von AMD veröffentlichte maximale Betriebstemperatur (Tjmax). Ryzen 9000, Ryzen 8000G und normale Ryzen-7000-Modelle sind in den aufgenommenen Profilen mit 95 °C hinterlegt; Ryzen 7000 X3D mit 89 °C. Die Kraken-Wassergrenzen bleiben davon unabhängig.": "Los perfiles usan la temperatura máxima publicada por AMD (Tjmax). Ryzen 9000, 8000G y Ryzen 7000 normales usan 95 °C; Ryzen 7000 X3D usa 89 °C. Los límites del líquido Kraken son independientes.",
    "Kraken Control by Frelidon steht unter GNU General Public License v3.0 oder später (GPL-3.0-or-later). Die vollständige Lizenz liegt dem Paket als LICENSE bei.": "Kraken Control by Frelidon usa GNU GPL v3.0 o posterior. La licencia completa se incluye como LICENSE.",
    "liquidctl-Gerätename: NZXT Kraken 2023 · USB 1e71:300e · LCD 240×240 · Temperatur, Pumpe, Radiatorlüfter und LCD": "Dispositivo liquidctl: NZXT Kraken 2023 · USB 1e71:300e · LCD 240×240 · temperatura, bomba, ventiladores y LCD",
    "USB 1e71:2012 · separate RGB-Steuerung über liquidctl. Der Controller wird auf der offiziellen Kraken-(2023)-Seite als Bestandteil der RGB-Varianten aufgeführt.": "USB 1e71:2012 · control RGB separado mediante liquidctl. El controlador figura en la página oficial Kraken (2023) como parte de las variantes RGB.",
    "Kraken-Radiatorlüfter werden weiterhin über die Kraken gesteuert. Zusätzlich kann Open Hardware Control ab 3.4.23 physisch bestätigte Mainboard-/Gehäuselüfter über kompatible Linux-hwmon-PWM-Kanäle regeln. GPU-Lüfter werden nicht verändert.": "Solo se admiten ventiladores informados y controlados por el dispositivo Kraken. Kraken Control no accede a otros ventiladores del PC.",
    "Alle Links öffnen sich im Standardbrowser. Das bloße Anzeigen dieser Seite überträgt keine Daten; erst das Anklicken eines Links öffnet die jeweilige externe Internetseite.": "Los enlaces se abren en el navegador predeterminado. Ver esta página no transmite datos; solo un clic abre el sitio externo.",
    "Dieses Protokoll erfasst Hardwarebefehle, Fehler, Schaltflächenklicks, Tastaturaktionen und vom Benutzer geänderte Einstellungen. Private Pfade und Kennungen werden weiterhin bereinigt.": "Este registro guarda comandos, errores, clics, teclado y ajustes cambiados. Las rutas e identificadores privados se ocultan.",
    "Das Live-Design überträgt im gewählten Intervall ein neues statisches Bild mit aktuellen Sensordaten. Die langfristige Wirkung häufiger Uploads auf den Displayspeicher ist nicht ausreichend bekannt. Live-Design trotzdem starten?": "El diseño en vivo envía una nueva imagen con sensores actuales en el intervalo elegido. No se conoce suficientemente el efecto de cargas frecuentes. ¿Iniciarlo de todos modos?",
})
UI_TRANSLATIONS["fr"].update({
    "Kompakt · 16:10": "Compact · 16:10", "Standard · 16:9": "Standard · 16:9", "Ultrawide · 21:9": "Ultra-large · 21:9", "Super-Ultrawide · 32:9": "Super ultra-large · 32:9",
    "Zuletzt durch Kraken Control gesetzt: Pumpe unbekannt · Radiatorlüfter unbekannt": "Dernier réglage par Kraken Control : pompe inconnue · ventilateurs inconnus",
    "Ein fester Prozentwert oder ein Schnellprofil ersetzt die jeweilige Kurve in der Kraken-Firmware.": "Un pourcentage fixe ou un profil rapide remplace la courbe correspondante dans le micrologiciel Kraken.",
    "Bei hoher CPU-Temperatur Kraken automatisch verstärken (mit 5 °C Hysterese)": "Renforcer automatiquement Kraken à haute température CPU (hystérésis de 5 °C)",
    "Die CPU-Tjmax ist nicht die Wassertemperatur. Für die Kraken-Flüssigkeit gelten die separaten Grenzen unten.": "La Tjmax du CPU n’est pas la température du liquide. Les limites séparées ci-dessous s’appliquent.",
    "CPU-Sensor: wird gesucht …": "Capteur CPU : recherche …", "Expertenmodus: Sicherheitsgrenzen frei einstellen": "Mode expert : régler librement les limites de sécurité",
    "Diese Werte gelten ausschließlich für die Kraken-Flüssigkeit, nicht für die CPU. Eine CPU-Tjmax von 89 oder 95 °C darf niemals als Wassergrenze übernommen werden. Im normalen Modus bleiben vorsichtige Einstellbereiche aktiv.": "Ces valeurs concernent uniquement le liquide Kraken, pas le CPU. Une Tjmax de 89 ou 95 °C ne doit jamais servir de limite du liquide. Les plages prudentes restent actives en mode normal.",
    "Die drei F140/F120-RGB-Core-Lüfter werden über den separaten NZXT 2023 RGB Controller gesteuert.": "Les trois ventilateurs F140/F120 RGB Core sont pilotés par le NZXT 2023 RGB Controller séparé.",
    "Die Hardware nimmt ein quadratisches 240×240-Bild an. Die Vorschau zeigt den tatsächlich sichtbaren runden Bereich.": "Le matériel accepte une image carrée de 240×240. L’aperçu montre la zone ronde réellement visible.",
    "Sicherheitshinweis: Der Fallback sendet das Bild wiederholt an die Kraken. Langzeitwirkungen auf den Displayspeicher sind nicht ausreichend bekannt. Nur aktivieren, wenn das Display wirklich zurückspringt; standardmäßig bleibt diese Funktion ausgeschaltet.": "Avis de sécurité : le secours renvoie l’image régulièrement. Les effets à long terme sont insuffisamment connus. Activez-le seulement si l’écran revient réellement ; il est désactivé par défaut.",
    "Einmalige GIF-Übertragung verwendet weiterhin nur das erste Bild. Der experimentelle Stream darunter emuliert Animation auf Firmware 2.x durch vorbereitete statische Frames über den liquidctl-Treiber.": "L’envoi unique d’un GIF utilise toujours sa première image. Le flux expérimental émule l’animation sur le micrologiciel 2.x avec des images statiques via liquidctl.",
    "Experimentell: Das Live-Design rendert Wasser-, CPU- und GPU-Sensordaten als statisches 240×240-Bild und überträgt es im gewählten Intervall. Die Mindestzeit beträgt 5 Sekunden; Langzeitwirkungen häufiger LCD-Uploads sind nicht ausreichend bekannt.": "Expérimental : le design en direct rend les capteurs liquide, CPU et GPU en image statique 240×240 et l’envoie à l’intervalle choisi. Le minimum est 5 secondes ; les effets d’envois fréquents sont insuffisamment connus.",
    "Experimentell: Die Uhr überträgt einmal pro Minute ein neues statisches Bild. Langzeitwirkungen häufiger LCD-Uploads sind nicht ausreichend bekannt; Sekunden werden bewusst nicht übertragen.": "Expérimental : l’horloge envoie une nouvelle image statique une fois par minute. Les effets à long terme sont insuffisamment connus ; les secondes sont volontairement omises.",
    "Akzentvorschau · Schaltflächen, Tabs, Regler und Kurven": "Aperçu de l’accent · boutons, onglets, curseurs et courbes",
    "Die App ändert nicht die Linux-Bildschirmauflösung. Qt arbeitet mit geräteunabhängigen Pixeln; hier werden App-Skalierung und responsives Layout angepasst.": "L’application ne modifie pas la résolution Linux. Qt utilise des pixels indépendants ; l’échelle et la disposition adaptative se règlent ici.",
    "Bestätigte LCD-Hinweise werden dauerhaft gespeichert. Nach einem verdächtigen Absturz oder wiederholten LCD-Fehlern stoppt Kraken Control experimentelle LCD-Funktionen und versucht automatisch die Standardanzeige der Flüssigkeitstemperatur wiederherzustellen.": "Les avis LCD confirmés sont conservés. Après un arrêt suspect ou des erreurs répétées, Kraken Control arrête les fonctions expérimentales et tente de restaurer l’écran standard du liquide.",
    "Open Hardware Control erkennt DNF, APT, Pacman und Zypper und installiert nach Bestätigung nur die fest zugeordneten Pakete aus bereits eingerichteten Quellen. Es werden keine fremden Paketquellen hinzugefügt.": "Open Hardware Control détecte DNF, APT, Pacman et Zypper et, après confirmation, installe uniquement les paquets définis depuis les dépôts déjà configurés. Aucun dépôt tiers n’est ajouté.",
    "Schreibzugriff auf /dev/hidraw ist für Pumpen-, Lüfter- und Kurvenänderungen erforderlich. Nach einer neuen udev-Regel kann Ab- und Anstecken oder ein Neustart nötig sein.": "L’écriture sur /dev/hidraw est requise pour la pompe, les ventilateurs et les courbes. Une reconnexion ou un redémarrage peut être nécessaire après une règle udev.",
    "Experimentelle Open-Source-Beta: Nutzung auf eigenes Risiko. Die Anwendung nutzt ausschließlich liquidctl. Die automatische Temperatursicherung wirkt nur, solange Programm, USB-Verbindung und Statusabfrage funktionieren. Wiederholte LCD-Uploads sind standardmäßig deaktiviert.": "Bêta open source expérimentale : utilisation à vos risques. L’application utilise uniquement liquidctl. La protection automatique fonctionne tant que le programme, l’USB et l’état fonctionnent. Les envois LCD répétés sont désactivés par défaut.",
    "Profile speichern Einstellungen kategorisiert. Gesamtprofile können Kühlung, LCD, RGB, Design, Hintergrund und Anzeige gemeinsam wiederherstellen.": "Les profils enregistrent les réglages par catégorie. Les profils complets restaurent ensemble refroidissement, LCD, RGB, design, fond et affichage.",
    "Kühlungsprofile werden erst nach erfolgreicher Kraken-Erkennung übertragen.": "Les profils de refroidissement sont envoyés après détection réussie de Kraken.",
    "z. B. Gaming, Leise Nacht oder Sommer": "p. ex. Jeu, Nuit calme ou Été", "Kurze Beschreibung": "Description courte",
    "Kraken Control by Frelidon": "Kraken Control by Frelidon", "Projektumfang – bewusst auf die Kraken begrenzt": "Portée du projet : volontairement limitée à Kraken",
    "Entwicklung und KI-Unterstützung": "Développement et assistance IA", "Verwendete Software – Website, Quellcode und Lizenz": "Logiciels utilisés : site, source et licence",
    "Komponenten- und Laufzeitversionen": "Versions des composants et d’exécution", "AMD-AM5-Temperaturprofile": "Profils de température AMD AM5",
    "Lizenz von Kraken Control": "Licence de Kraken Control", "Unterstützte Geräte und offizielle Herstellerseiten": "Appareils compatibles et pages officielles",
    "Öffentliches Projekt-Repository und Downloads: https://github.com/Frelidon/open-hardware-control": "Dépôt public et téléchargements : https://github.com/Frelidon/open-hardware-control",
    "<b>Enthalten:</b> Wassertemperatur, Kraken-Pumpe, von der Kraken gemeldete beziehungsweise gesteuerte Radiatorlüfter, LCD, der separate NZXT 2023 RGB Controller sowie sicher kalibrierte Mainboard-/Gehäuselüfter über kompatibles Linux-hwmon.": "<b>Inclus :</b> température du liquide, pompe Kraken, ventilateurs signalés ou contrôlés par Kraken, LCD et NZXT 2023 RGB Controller séparé.",
    "<b>Nicht enthalten:</b> GPU-Lüftersteuerung, AMD-Grafik-Tuning, Firmware-Updates, allgemeines Mainboard-Tuning sowie unbestätigte direkte Controllerzugriffe. Mainboard-/Gehäuselüfter werden nur über erkannte, schreibbare Linux-hwmon-Kanäle und nach physischer Kalibrierung geregelt.": "<b>Non inclus :</b> ventilateurs de carte mère ou boîtier, ventilateurs GPU, commandes graphiques AMD et réglage général. Ces fonctions seront des outils séparés.",
    "Projektleitung und Veröffentlichung: Frelidon. Mit Unterstützung von ChatGPT (GPT-5.6 Thinking) von OpenAI bei Programmierung, Dokumentation und Tests. ChatGPT ist kein Laufzeitbestandteil der App. Die Nennung stellt keine offizielle Unterstützung oder Partnerschaft durch OpenAI dar.": "Direction et publication : Frelidon. Avec l’aide de ChatGPT (GPT-5.6 Thinking) d’OpenAI pour le code, la documentation et les tests. ChatGPT ne fait pas partie de l’exécution et n’implique aucun soutien officiel d’OpenAI.",
    "Die auswählbaren CPU-Profile nutzen die von AMD veröffentlichte maximale Betriebstemperatur (Tjmax). Ryzen 9000, Ryzen 8000G und normale Ryzen-7000-Modelle sind in den aufgenommenen Profilen mit 95 °C hinterlegt; Ryzen 7000 X3D mit 89 °C. Die Kraken-Wassergrenzen bleiben davon unabhängig.": "Les profils utilisent la température maximale publiée par AMD (Tjmax). Ryzen 9000, 8000G et Ryzen 7000 standard utilisent 95 °C ; Ryzen 7000 X3D utilise 89 °C. Les limites du liquide Kraken sont indépendantes.",
    "Kraken Control by Frelidon steht unter GNU General Public License v3.0 oder später (GPL-3.0-or-later). Die vollständige Lizenz liegt dem Paket als LICENSE bei.": "Kraken Control by Frelidon est sous GNU GPL v3.0 ou ultérieure. La licence complète est incluse dans LICENSE.",
    "liquidctl-Gerätename: NZXT Kraken 2023 · USB 1e71:300e · LCD 240×240 · Temperatur, Pumpe, Radiatorlüfter und LCD": "Appareil liquidctl : NZXT Kraken 2023 · USB 1e71:300e · LCD 240×240 · température, pompe, ventilateurs et LCD",
    "USB 1e71:2012 · separate RGB-Steuerung über liquidctl. Der Controller wird auf der offiziellen Kraken-(2023)-Seite als Bestandteil der RGB-Varianten aufgeführt.": "USB 1e71:2012 · commande RGB séparée via liquidctl. Le contrôleur figure sur la page officielle Kraken (2023) avec les variantes RGB.",
    "Kraken-Radiatorlüfter werden weiterhin über die Kraken gesteuert. Zusätzlich kann Open Hardware Control ab 3.4.23 physisch bestätigte Mainboard-/Gehäuselüfter über kompatible Linux-hwmon-PWM-Kanäle regeln. GPU-Lüfter werden nicht verändert.": "Seuls les ventilateurs signalés et contrôlés par l’appareil Kraken sont pris en charge. Kraken Control n’accède pas aux autres ventilateurs du PC.",
    "Alle Links öffnen sich im Standardbrowser. Das bloße Anzeigen dieser Seite überträgt keine Daten; erst das Anklicken eines Links öffnet die jeweilige externe Internetseite.": "Les liens s’ouvrent dans le navigateur par défaut. Afficher cette page n’envoie aucune donnée ; seul un clic ouvre le site externe.",
    "Dieses Protokoll erfasst Hardwarebefehle, Fehler, Schaltflächenklicks, Tastaturaktionen und vom Benutzer geänderte Einstellungen. Private Pfade und Kennungen werden weiterhin bereinigt.": "Ce journal enregistre commandes, erreurs, clics, clavier et réglages modifiés. Les chemins et identifiants privés restent masqués.",
    "Das Live-Design überträgt im gewählten Intervall ein neues statisches Bild mit aktuellen Sensordaten. Die langfristige Wirkung häufiger Uploads auf den Displayspeicher ist nicht ausreichend bekannt. Live-Design trotzdem starten?": "Le design en direct envoie une nouvelle image avec les capteurs à l’intervalle choisi. L’effet d’envois fréquents est insuffisamment connu. Démarrer quand même ?",
})
UI_TRANSLATIONS["en"].update({
    "Hell (Standard)": "Light (default)", "Akzentfarbe": "Accent color", "Leise · 45 % / 35 %": "Quiet · 45% / 35%",
    "Ausgeglichen · 55 % / 50 %": "Balanced · 55% / 50%", "Leistung · 75 % / 75 %": "Performance · 75% / 75%",
    "Sicher · 65 % / 65 %": "Safe · 65% / 65%", "Kühlprofil": "Cooling profile", "Öffnen": "Open",
    "Flüssigkeitstemperatur anzeigen": "Show liquid temperature", "Farbe 1 · #00aaff": "Color 1 · #00aaff",
    "Farbe 2 · #ffffff": "Color 2 · #ffffff", "Text · #ffffff": "Text · #ffffff", "Hintergrund · #10141c": "Background · #10141c",
    "Eisblau · #00c8ff": "Ice blue · #00c8ff", "Neongrün · #39ff88": "Neon green · #39ff88", "Orange · #ff9a32": "Orange · #ff9a32",
    "Rot · #ff4058": "Red · #ff4058", "Gold · #ffd54a": "Gold · #ffd54a", "Weiß · #f4f7ff": "White · #f4f7ff", "Lila · #a855f7": "Purple · #a855f7",
})
UI_TRANSLATIONS["es"].update({
    "Hell (Standard)": "Claro (predeterminado)", "Akzentfarbe": "Color de acento", "Leise · 45 % / 35 %": "Silencioso · 45% / 35%",
    "Ausgeglichen · 55 % / 50 %": "Equilibrado · 55% / 50%", "Leistung · 75 % / 75 %": "Rendimiento · 75% / 75%",
    "Sicher · 65 % / 65 %": "Seguro · 65% / 65%", "Kühlprofil": "Perfil de refrigeración", "Öffnen": "Abrir",
    "Flüssigkeitstemperatur anzeigen": "Mostrar temperatura del líquido", "Farbe 1 · #00aaff": "Color 1 · #00aaff",
    "Farbe 2 · #ffffff": "Color 2 · #ffffff", "Text · #ffffff": "Texto · #ffffff", "Hintergrund · #10141c": "Fondo · #10141c",
    "Eisblau · #00c8ff": "Azul hielo · #00c8ff", "Neongrün · #39ff88": "Verde neón · #39ff88", "Orange · #ff9a32": "Naranja · #ff9a32",
    "Rot · #ff4058": "Rojo · #ff4058", "Gold · #ffd54a": "Dorado · #ffd54a", "Weiß · #f4f7ff": "Blanco · #f4f7ff", "Lila · #a855f7": "Morado · #a855f7",
})
UI_TRANSLATIONS["fr"].update({
    "Hell (Standard)": "Clair (par défaut)", "Akzentfarbe": "Couleur d’accent", "Leise · 45 % / 35 %": "Silencieux · 45% / 35%",
    "Ausgeglichen · 55 % / 50 %": "Équilibré · 55% / 50%", "Leistung · 75 % / 75 %": "Performance · 75% / 75%",
    "Sicher · 65 % / 65 %": "Sûr · 65% / 65%", "Kühlprofil": "Profil de refroidissement", "Öffnen": "Ouvrir",
    "Flüssigkeitstemperatur anzeigen": "Afficher la température du liquide", "Farbe 1 · #00aaff": "Couleur 1 · #00aaff",
    "Farbe 2 · #ffffff": "Couleur 2 · #ffffff", "Text · #ffffff": "Texte · #ffffff", "Hintergrund · #10141c": "Arrière-plan · #10141c",
    "Eisblau · #00c8ff": "Bleu glacier · #00c8ff", "Neongrün · #39ff88": "Vert néon · #39ff88", "Orange · #ff9a32": "Orange · #ff9a32",
    "Rot · #ff4058": "Rouge · #ff4058", "Gold · #ffd54a": "Or · #ffd54a", "Weiß · #f4f7ff": "Blanc · #f4f7ff", "Lila · #a855f7": "Violet · #a855f7",
})
UI_TRANSLATIONS["en"].update({
    "Sehr guter Bereich": "Excellent range", "Normal unter Last": "Normal under load", "Erhöht – Kurve prüfen": "Elevated – check curve", "Kritisch – Kühlung prüfen": "Critical – check cooling",
    "⚠ Pumpendrehzahl ungewöhnlich niedrig.": "⚠ Pump speed unusually low.", "⚠ Kritische Wassertemperatur": "⚠ Critical liquid temperature", "⚠ Erhöhte Wassertemperatur": "⚠ Elevated liquid temperature",
    "⚠ Lüfter stehen trotz erhöhter Temperatur.": "⚠ Fans are stopped despite elevated temperature.", "✅ Kühlung arbeitet normal.": "✅ Cooling is operating normally.",
    "LCD-Uhr-Hinweis": "LCD clock notice", "LCD-Fallback-Hinweis": "LCD fallback notice", "GIF-Streamer-Hinweis": "GIF streamer notice", "Live-Hardwaredesign-Hinweis": "Live hardware design notice", "LCD-Sicherheitswiederherstellung vorgemerkt": "LCD safety recovery pending",
})
UI_TRANSLATIONS["es"].update({
    "Sehr guter Bereich": "Rango excelente", "Normal unter Last": "Normal bajo carga", "Erhöht – Kurve prüfen": "Elevado – comprobar curva", "Kritisch – Kühlung prüfen": "Crítico – comprobar refrigeración",
    "⚠ Pumpendrehzahl ungewöhnlich niedrig.": "⚠ Velocidad de bomba inusualmente baja.", "⚠ Kritische Wassertemperatur": "⚠ Temperatura crítica del líquido", "⚠ Erhöhte Wassertemperatur": "⚠ Temperatura elevada del líquido",
    "⚠ Lüfter stehen trotz erhöhter Temperatur.": "⚠ Los ventiladores están parados con temperatura elevada.", "✅ Kühlung arbeitet normal.": "✅ La refrigeración funciona normalmente.",
    "LCD-Uhr-Hinweis": "Aviso del reloj LCD", "LCD-Fallback-Hinweis": "Aviso de respaldo LCD", "GIF-Streamer-Hinweis": "Aviso del flujo GIF", "Live-Hardwaredesign-Hinweis": "Aviso del diseño en vivo", "LCD-Sicherheitswiederherstellung vorgemerkt": "Recuperación segura del LCD pendiente",
})
UI_TRANSLATIONS["fr"].update({
    "Sehr guter Bereich": "Excellente plage", "Normal unter Last": "Normal en charge", "Erhöht – Kurve prüfen": "Élevé – vérifier la courbe", "Kritisch – Kühlung prüfen": "Critique – vérifier le refroidissement",
    "⚠ Pumpendrehzahl ungewöhnlich niedrig.": "⚠ Vitesse de pompe anormalement basse.", "⚠ Kritische Wassertemperatur": "⚠ Température critique du liquide", "⚠ Erhöhte Wassertemperatur": "⚠ Température élevée du liquide",
    "⚠ Lüfter stehen trotz erhöhter Temperatur.": "⚠ Les ventilateurs sont arrêtés malgré une température élevée.", "✅ Kühlung arbeitet normal.": "✅ Le refroidissement fonctionne normalement.",
    "LCD-Uhr-Hinweis": "Avis de l’horloge LCD", "LCD-Fallback-Hinweis": "Avis de secours LCD", "GIF-Streamer-Hinweis": "Avis du flux GIF", "Live-Hardwaredesign-Hinweis": "Avis du design matériel en direct", "LCD-Sicherheitswiederherstellung vorgemerkt": "Récupération de sécurité LCD en attente",
})

UI_TRANSLATIONS["en"].update({
    "Große LCD-Vorschau animieren": "Animate large LCD preview",
    "Designvorschau bei Maus darüber animieren": "Animate design preview on hover",
    "Kleine Vorschau beim Scrollen sichtbar halten": "Keep a small preview visible while scrolling",
    "LCD-Kacheln zurücksetzen": "Reset LCD tiles",
    "Mitgelieferte Animationen": "Bundled animations",
    "Keine Fremdmedien · acht originale OHC-Designs": "No third-party media · eight original OHC designs",
    "Designgröße": "Design size", "Originalgröße": "Original size",
    "✥ Kachel verschieben": "✥ Move tile",
    "Ein Klick aktiviert das Design · Maus darüber zeigt eine sparsame Live-Vorschau": "Click to activate the design · hover for a lightweight live preview",
})
UI_TRANSLATIONS["es"].update({
    "Große LCD-Vorschau animieren": "Animar vista previa LCD grande",
    "Designvorschau bei Maus darüber animieren": "Animar vista previa al pasar el ratón",
    "Kleine Vorschau beim Scrollen sichtbar halten": "Mantener una vista previa pequeña al desplazarse",
    "LCD-Kacheln zurücksetzen": "Restablecer mosaicos LCD",
    "Mitgelieferte Animationen": "Animaciones incluidas",
    "Keine Fremdmedien · acht originale OHC-Designs": "Sin medios de terceros · ocho diseños OHC originales",
    "Designgröße": "Tamaño del diseño", "Originalgröße": "Tamaño original",
    "✥ Kachel verschieben": "✥ Mover mosaico",
    "Ein Klick aktiviert das Design · Maus darüber zeigt eine sparsame Live-Vorschau": "Un clic activa el diseño · al pasar el ratón se muestra una vista previa ligera",
})
UI_TRANSLATIONS["fr"].update({
    "Große LCD-Vorschau animieren": "Animer le grand aperçu LCD",
    "Designvorschau bei Maus darüber animieren": "Animer l’aperçu au survol",
    "Kleine Vorschau beim Scrollen sichtbar halten": "Garder un petit aperçu visible pendant le défilement",
    "LCD-Kacheln zurücksetzen": "Réinitialiser les tuiles LCD",
    "Mitgelieferte Animationen": "Animations incluses",
    "Keine Fremdmedien · acht originale OHC-Designs": "Aucun média tiers · huit designs OHC originaux",
    "Designgröße": "Taille du design", "Originalgröße": "Taille d’origine",
    "✥ Kachel verschieben": "✥ Déplacer la tuile",
    "Ein Klick aktiviert das Design · Maus darüber zeigt eine sparsame Live-Vorschau": "Un clic active le design · le survol affiche un aperçu léger",
})

# 3.4.23 mainboard-fan and ENE-DRAM interface translations.
UI_TRANSLATIONS["en"].update({
    "Mainboard-Lüftersteuerung · Linux hwmon": "Motherboard fan control · Linux hwmon",
    "Hardware neu erkennen": "Detect hardware again",
    "Treiber-/Secure-Boot-Status": "Driver / Secure Boot status",
    "NCT6687-Einrichtung anzeigen": "Show NCT6687 setup",
    "Automatische Mainboard-Lüfterkurven aktivieren": "Enable automatic motherboard fan curves",
    "Ausgewählten PWM-Kanal konfigurieren": "Configure selected PWM channel",
    "Kanaleinstellungen speichern": "Save channel settings",
    "Kanal sicher testen · 70 % / 10 s": "Safely test channel · 70% / 10 s",
    "Firmwaresteuerung wiederherstellen": "Restore firmware control",
    "ℹ ENE-DRAM · zusätzliche Initialisierung": "ℹ ENE DRAM · additional initialization",
    "ENE-RAM erneut initialisieren": "Reinitialize ENE RAM",
    "Initialisierung: wartet auf Geräte …": "Initialization: waiting for devices …",
    "Öffentliches Projekt-Repository und Downloads: https://github.com/Frelidon/open-hardware-control": "Public project repository and downloads: https://github.com/Frelidon/open-hardware-control",
    "<b>Enthalten:</b> Wassertemperatur, Kraken-Pumpe, von der Kraken gemeldete beziehungsweise gesteuerte Radiatorlüfter, LCD, der separate NZXT 2023 RGB Controller sowie sicher kalibrierte Mainboard-/Gehäuselüfter über kompatibles Linux-hwmon.": "<b>Included:</b> liquid temperature, Kraken pump, Kraken-reported radiator fans, LCD, the separate NZXT 2023 RGB Controller, and safely calibrated motherboard/case fans through compatible Linux hwmon.",
    "<b>Nicht enthalten:</b> GPU-Lüftersteuerung, AMD-Grafik-Tuning, Firmware-Updates, allgemeines Mainboard-Tuning sowie unbestätigte direkte Controllerzugriffe. Mainboard-/Gehäuselüfter werden nur über erkannte, schreibbare Linux-hwmon-Kanäle und nach physischer Kalibrierung geregelt.": "<b>Not included:</b> GPU fan control, AMD graphics tuning, firmware updates, general motherboard tuning, or unverified direct controller access. Motherboard/case fans are controlled only through detected writable Linux hwmon channels after physical calibration.",
    "Kraken-Radiatorlüfter werden weiterhin über die Kraken gesteuert. Zusätzlich kann Open Hardware Control ab 3.4.23 physisch bestätigte Mainboard-/Gehäuselüfter über kompatible Linux-hwmon-PWM-Kanäle regeln. GPU-Lüfter werden nicht verändert.": "Kraken radiator fans remain controlled through the Kraken. Starting with 3.4.23, Open Hardware Control can also regulate physically confirmed motherboard/case fans through compatible Linux hwmon PWM channels. GPU fans are not modified.",
})
UI_TRANSLATIONS["es"].update({
    "Mainboard-Lüftersteuerung · Linux hwmon": "Control de ventiladores de placa · Linux hwmon",
    "Hardware neu erkennen": "Detectar hardware de nuevo",
    "Treiber-/Secure-Boot-Status": "Estado del controlador / Secure Boot",
    "NCT6687-Einrichtung anzeigen": "Mostrar configuración NCT6687",
    "Automatische Mainboard-Lüfterkurven aktivieren": "Activar curvas automáticas de ventiladores de placa",
    "Ausgewählten PWM-Kanal konfigurieren": "Configurar canal PWM seleccionado",
    "Kanaleinstellungen speichern": "Guardar ajustes del canal",
    "Kanal sicher testen · 70 % / 10 s": "Probar canal con seguridad · 70% / 10 s",
    "Firmwaresteuerung wiederherstellen": "Restaurar control del firmware",
    "ℹ ENE-DRAM · zusätzliche Initialisierung": "ℹ ENE DRAM · inicialización adicional",
    "ENE-RAM erneut initialisieren": "Reinicializar RAM ENE",
    "Initialisierung: wartet auf Geräte …": "Inicialización: esperando dispositivos …",
    "Öffentliches Projekt-Repository und Downloads: https://github.com/Frelidon/open-hardware-control": "Repositorio público y descargas: https://github.com/Frelidon/open-hardware-control",
    "<b>Enthalten:</b> Wassertemperatur, Kraken-Pumpe, von der Kraken gemeldete beziehungsweise gesteuerte Radiatorlüfter, LCD, der separate NZXT 2023 RGB Controller sowie sicher kalibrierte Mainboard-/Gehäuselüfter über kompatibles Linux-hwmon.": "<b>Incluye:</b> temperatura del líquido, bomba Kraken, ventiladores del radiador, LCD, controlador NZXT 2023 RGB y ventiladores de placa/caja calibrados de forma segura mediante Linux hwmon compatible.",
    "<b>Nicht enthalten:</b> GPU-Lüftersteuerung, AMD-Grafik-Tuning, Firmware-Updates, allgemeines Mainboard-Tuning sowie unbestätigte direkte Controllerzugriffe. Mainboard-/Gehäuselüfter werden nur über erkannte, schreibbare Linux-hwmon-Kanäle und nach physischer Kalibrierung geregelt.": "<b>No incluye:</b> control de ventiladores GPU, ajuste gráfico AMD, actualizaciones de firmware, ajuste general de placa ni acceso directo no verificado. Los ventiladores de placa/caja solo se controlan mediante canales Linux hwmon detectados y escribibles tras calibración física.",
    "Kraken-Radiatorlüfter werden weiterhin über die Kraken gesteuert. Zusätzlich kann Open Hardware Control ab 3.4.23 physisch bestätigte Mainboard-/Gehäuselüfter über kompatible Linux-hwmon-PWM-Kanäle regeln. GPU-Lüfter werden nicht verändert.": "Los ventiladores del radiador Kraken siguen controlándose mediante Kraken. Desde 3.4.23, OHC también puede regular ventiladores de placa/caja confirmados físicamente mediante canales PWM Linux hwmon compatibles. No modifica los ventiladores GPU.",
})
UI_TRANSLATIONS["fr"].update({
    "Mainboard-Lüftersteuerung · Linux hwmon": "Contrôle des ventilateurs carte mère · Linux hwmon",
    "Hardware neu erkennen": "Redétecter le matériel",
    "Treiber-/Secure-Boot-Status": "État du pilote / Secure Boot",
    "NCT6687-Einrichtung anzeigen": "Afficher la configuration NCT6687",
    "Automatische Mainboard-Lüfterkurven aktivieren": "Activer les courbes automatiques des ventilateurs carte mère",
    "Ausgewählten PWM-Kanal konfigurieren": "Configurer le canal PWM sélectionné",
    "Kanaleinstellungen speichern": "Enregistrer le canal",
    "Kanal sicher testen · 70 % / 10 s": "Tester le canal en sécurité · 70% / 10 s",
    "Firmwaresteuerung wiederherstellen": "Restaurer le contrôle du firmware",
    "ℹ ENE-DRAM · zusätzliche Initialisierung": "ℹ ENE DRAM · initialisation supplémentaire",
    "ENE-RAM erneut initialisieren": "Réinitialiser la RAM ENE",
    "Initialisierung: wartet auf Geräte …": "Initialisation : attente des périphériques …",
    "Öffentliches Projekt-Repository und Downloads: https://github.com/Frelidon/open-hardware-control": "Dépôt public et téléchargements : https://github.com/Frelidon/open-hardware-control",
    "<b>Enthalten:</b> Wassertemperatur, Kraken-Pumpe, von der Kraken gemeldete beziehungsweise gesteuerte Radiatorlüfter, LCD, der separate NZXT 2023 RGB Controller sowie sicher kalibrierte Mainboard-/Gehäuselüfter über kompatibles Linux-hwmon.": "<b>Inclus :</b> température du liquide, pompe Kraken, ventilateurs du radiateur, LCD, contrôleur NZXT 2023 RGB et ventilateurs carte mère/boîtier calibrés en sécurité via Linux hwmon compatible.",
    "<b>Nicht enthalten:</b> GPU-Lüftersteuerung, AMD-Grafik-Tuning, Firmware-Updates, allgemeines Mainboard-Tuning sowie unbestätigte direkte Controllerzugriffe. Mainboard-/Gehäuselüfter werden nur über erkannte, schreibbare Linux-hwmon-Kanäle und nach physischer Kalibrierung geregelt.": "<b>Non inclus :</b> contrôle des ventilateurs GPU, réglage graphique AMD, mises à jour de micrologiciel, réglage général de carte mère ou accès direct non vérifié. Les ventilateurs carte mère/boîtier ne sont contrôlés que via des canaux Linux hwmon détectés et inscriptibles après calibration physique.",
    "Kraken-Radiatorlüfter werden weiterhin über die Kraken gesteuert. Zusätzlich kann Open Hardware Control ab 3.4.23 physisch bestätigte Mainboard-/Gehäuselüfter über kompatible Linux-hwmon-PWM-Kanäle regeln. GPU-Lüfter werden nicht verändert.": "Les ventilateurs du radiateur Kraken restent contrôlés via Kraken. À partir de 3.4.23, OHC peut aussi réguler les ventilateurs carte mère/boîtier physiquement confirmés via des canaux PWM Linux hwmon compatibles. Les ventilateurs GPU ne sont pas modifiés.",
})

_GIF_SAFETY_TEXT = (
    "Kein nativer Firmware-2.x-GIF-Modus: Version 3.4.23.1 INTERN verwendet im NZXT-Modul einen exklusiven CAM-nahen Roh-Framepfad. "
    "Jeder Frame verwendet explizit Start → ACK → 20-Byte-Header → 115.200 Byte RGB565 → "
    "Ende → ACK. Standard ist eine phasenstabile 26,667-Hz-Folge ohne Frame-Sprünge; 25,6 Hz bleibt als sicherer Rückfallmodus. Die Bewegungsglättung arbeitet "
    "bewegungskompensiert statt mit reinem Crossfade. Transfers werden nie überlappt und Catch-up-Bursts bleiben verboten. "
    "Kraken-Statusabfragen pausieren während des Streams. Die CPU-Kurvenregelung liest Linux-hwmon weiter und verwendet nur bei "
    "einer relevanten Drehzahländerung die koordinierte Kurzpause: USB freigeben → Kühlbefehl übertragen → denselben Stream fortsetzen. "
    "Bei falschen ACKs oder ausbleibenden Lebenszeichen folgt der sichere Fallback auf die Flüssigkeitstemperatur."
)
_ABOUT_SUMMARY_TEXT = (
    "Gemeinsame, quelloffene Linux-Hardwarezentrale. Version 3.4.23 INTERN ergänzt die koordinierte Kraken-/RGB-Basis um sichere Mainboard-Lüftersteuerung und zentralisiert konkurrierende Kraken-USB- "
    "und RGB-Aufträge, wartet beim RGB-Profilstart auf einen stabilen OpenRGB-Gerätebestand und protokolliert "
    "Request-IDs, Besitzerwechsel, Retries und Fehler. Importierte NZXT-ESC-Profile nutzen einen Live-Renderer, "
    "LCD-Designs lassen sich direkt aktivieren und skalieren, und beim Systemende wird nach Möglichkeit zuerst auf "
    "die Flüssigkeitstemperatur zurückgestellt. Open Radeon Control Center bleibt ein eigenständiges Projekt. "
    "Experimentelle interne Beta, Nutzung auf eigenes Risiko; unabhängiges Projekt ohne offizielle Verbindung zu "
    "den genannten Herstellern."
)
UI_TRANSLATIONS["en"].update({
    "Menüs, Tabs, Schaltflächen, Gruppen und Auswahlfelder wechseln vollständig mit der gewählten Sprache. Rein technische Diagnosezeilen im Log bleiben für vergleichbare Hardwaretests teilweise Deutsch.": "Menus, tabs, buttons, groups and choices switch completely with the selected language. Purely technical log diagnostics remain partly in German for comparable hardware tests.",
    "Diese Version enthält fünf runde Live-Hardwaredesigns für Wasser, CPU und GPU, Eisblau als Standardakzent, Farbvorlagen und freie Hex-Farben. Die sichtbare Grundoberfläche unterstützt Deutsch, Englisch, Spanisch und Französisch. Der exklusive CAM-nahe Firmware-2.x-LCD-Streamer, passende ACK-Prüfung, ein 12-Sekunden-Watchdog und der gemeinsame LCD-Sicherheitsfallback bleiben enthalten. ": "This version includes five rounded live hardware designs for liquid, CPU and GPU, ice blue as the default accent, color presets and custom hex colors. The visible base interface supports German, English, Spanish and French. The exclusive CAM-near firmware-2.x LCD streamer, matched ACK checks, a 12-second watchdog and the shared LCD safety fallback remain included. ",
    _GIF_SAFETY_TEXT: "No native firmware-2.x GIF mode: version 3.4.23 INTERNAL uses an exclusive CAM-near raw-frame path in the NZXT module. Every frame explicitly uses Start → ACK → 20-byte header → 115,200 bytes RGB565 → End → ACK. Kraken status polling pauses, while CPU-curve sensing through Linux hwmon continues. Relevant duty changes use a coordinated short USB handoff before the same cached stream resumes. Invalid ACKs or missing heartbeats trigger the safe fallback.",
    "Log: 0 / 10.000 Zeichen": "Log: 0 / 10,000 characters",
    _ABOUT_SUMMARY_TEXT: "Shared open-source Linux hardware hub. Version 3.4.23 INTERNAL adds safety-gated motherboard fan control through Linux hwmon/NCT6687, ENE-DRAM reinitialization, and retains coordinated Kraken USB/RGB handling, stable OpenRGB profile restore and safe LCD shutdown recovery.",
})
UI_TRANSLATIONS["es"].update({
    "Menüs, Tabs, Schaltflächen, Gruppen und Auswahlfelder wechseln vollständig mit der gewählten Sprache. Rein technische Diagnosezeilen im Log bleiben für vergleichbare Hardwaretests teilweise Deutsch.": "Menús, pestañas, botones, grupos y selecciones cambian completamente con el idioma elegido. Algunas líneas técnicas del registro permanecen en alemán para comparar pruebas.",
    "Diese Version enthält fünf runde Live-Hardwaredesigns für Wasser, CPU und GPU, Eisblau als Standardakzent, Farbvorlagen und freie Hex-Farben. Die sichtbare Grundoberfläche unterstützt Deutsch, Englisch, Spanisch und Französisch. Der exklusive CAM-nahe Firmware-2.x-LCD-Streamer, passende ACK-Prüfung, ein 12-Sekunden-Watchdog und der gemeinsame LCD-Sicherheitsfallback bleiben enthalten. ": "Esta versión incluye cinco diseños redondos en vivo para líquido, CPU y GPU, azul hielo predeterminado, colores predefinidos y hexadecimales personalizados. La interfaz visible admite alemán, inglés, español y francés. Se mantienen el flujo LCD exclusivo similar a CAM, las respuestas ACK verificadas, el vigilante de 12 segundos y el respaldo seguro del LCD. ",
    _GIF_SAFETY_TEXT: "No existe modo GIF nativo en firmware 2.x: la versión 3.4.23 INTERNA usa una ruta exclusiva similar a CAM. Las consultas Kraken se pausan, pero el sensor de las curvas de CPU sigue activo mediante hwmon. Los cambios relevantes usan una entrega USB coordinada y después continúa el mismo flujo.",
    "Log: 0 / 10.000 Zeichen": "Registro: 0 / 10.000 caracteres",
    _ABOUT_SUMMARY_TEXT: "Centro de hardware Linux de código abierto. La versión 3.4.23 INTERNA añade control seguro de ventiladores de placa mediante Linux hwmon/NCT6687, reinicialización ENE-DRAM y conserva la coordinación USB/RGB y la recuperación segura del LCD.",
})
UI_TRANSLATIONS["fr"].update({
    "Menüs, Tabs, Schaltflächen, Gruppen und Auswahlfelder wechseln vollständig mit der gewählten Sprache. Rein technische Diagnosezeilen im Log bleiben für vergleichbare Hardwaretests teilweise Deutsch.": "Menus, onglets, boutons, groupes et sélections changent entièrement avec la langue choisie. Certaines lignes techniques du journal restent en allemand pour comparer les tests.",
    "Diese Version enthält fünf runde Live-Hardwaredesigns für Wasser, CPU und GPU, Eisblau als Standardakzent, Farbvorlagen und freie Hex-Farben. Die sichtbare Grundoberfläche unterstützt Deutsch, Englisch, Spanisch und Französisch. Der exklusive CAM-nahe Firmware-2.x-LCD-Streamer, passende ACK-Prüfung, ein 12-Sekunden-Watchdog und der gemeinsame LCD-Sicherheitsfallback bleiben enthalten. ": "Cette version contient cinq designs matériels ronds en direct pour liquide, CPU et GPU, le bleu glacier par défaut, des préréglages et des couleurs hexadécimales personnalisées. L’interface visible prend en charge l’allemand, l’anglais, l’espagnol et le français. Le flux LCD exclusif proche de CAM, les ACK vérifiés, le watchdog de 12 secondes et le secours LCD commun restent inclus. ",
    _GIF_SAFETY_TEXT: "Pas de mode GIF natif sur le micrologiciel 2.x : la version 3.4.23 INTERNE utilise un chemin exclusif proche de CAM. Les états Kraken sont suspendus, mais les courbes CPU continuent de lire hwmon. Les changements utiles emploient une courte remise USB coordonnée puis reprennent le même flux.",
    "Log: 0 / 10.000 Zeichen": "Journal : 0 / 10 000 caractères",
    _ABOUT_SUMMARY_TEXT: "Centre matériel Linux open source. La version 3.4.23 INTERNE ajoute un contrôle sécurisé des ventilateurs de carte mère via Linux hwmon/NCT6687, la réinitialisation ENE-DRAM et conserve la coordination USB/RGB ainsi que la restauration LCD sécurisée.",
})

UI_TRANSLATIONS["en"].update({
    "Schrift- und Zahlen-Größe": "Text and number size", "Animierte Hardwaredaten · Ringe und Orbits": "Animated hardware data · Rings and orbits",
    "20 FPS · ruhig": "20 FPS · calm", "25 FPS · flüssig · empfohlen": "25 FPS · smooth · recommended",
    "Animierte Vorschau erzeugen": "Generate animated preview", "Hardwareanimation starten": "Start hardware animation", "Hardwareanimation anhalten": "Stop hardware animation",
    "Animationslayout": "Animation layout", "Animationsrate": "Animation rate", "Animierte Hardwaredaten": "Animated hardware data",
    "Animierte Hardwaredaten: bereit · Farbe und Schriftgröße werden vom Live-Design übernommen.": "Animated hardware data: ready · Color and text size are shared with the live design.",
    "Die Animation erzeugt einen nahtlosen GIF-Loop mit rotierenden Ringen, Lichtpunkten und Orbits. Die angezeigten Temperaturen sind eine Momentaufnahme beim Start. Während des exklusiven CAM-Raw-Streams bleiben Kraken-Statusabfragen und neue Kühlbefehle wie bisher pausiert; gespeicherte Hardwarekurven laufen weiter.": "The animation creates a seamless GIF loop with rotating rings, light points and orbits. Displayed temperatures are a snapshot taken at start. During the exclusive CAM-raw stream, Kraken status polling and new cooling commands remain paused while stored hardware curves continue.",
    "Animierte Vorschau läuft · noch nicht auf das LCD übertragen.": "Animated preview is running · not uploaded to the LCD yet.", "Die Hardwareanimation konnte nicht erzeugt werden:": "The hardware animation could not be created:",
    "Experimentelle Hardwareanimation": "Experimental hardware animation", "Hardwareanimation wird vorbereitet …": "Preparing hardware animation …",
    "Hardwareanimation vorbereitet": "Hardware animation prepared", "Frames": "frames", "LCD-Modus: animierte Hardwaredaten · experimentell": "LCD mode: animated hardware data · experimental",
    "Hardwareanimation aktiv": "Hardware animation active", "Temperaturen als Start-Momentaufnahme": "temperatures are a start snapshot", "Upload": "upload",
    "Hardwareanimation angehalten · das letzte Bild kann sichtbar bleiben.": "Hardware animation stopped · the last image may remain visible.", "Hardwareanimation angehalten": "Hardware animation stopped",
    "Hardwareanimation: Fehler": "Hardware animation: error", "Hardwareanimation: Start abgebrochen": "Hardware animation: start canceled", "Hardwareanimation: Datei nicht mehr vorhanden": "Hardware animation: file no longer available",
    "Hardwareanimation-Hinweis": "Hardware animation notice",
    "Die Animation verwendet die zuletzt gelesenen Temperaturen als Momentaufnahme. Während des Streams pausieren Kraken-Statusabfragen und neue Kühlbefehle; die in der Kraken gespeicherten Kurven laufen weiter. Häufige LCD-Uploads bleiben experimentell. Hardwareanimation trotzdem starten?": "The animation uses the last-read temperatures as a snapshot. Kraken status polling and new cooling commands pause during the stream while curves stored in the Kraken continue. Frequent LCD uploads remain experimental. Start the hardware animation anyway?",
    "LCD-Modus: Live-Hardwaredesign": "LCD mode: live hardware design",
    "Live-Hardwaredesign angehalten · das letzte Bild kann sichtbar bleiben.": "Live hardware design stopped · the last image may remain visible.",
    "Die Animation erzeugt einen nahtlosen GIF-Loop mit rotierenden Ringen, Lichtpunkten und Orbits. CPU- und GPU-Temperaturen werden währenddessen sicher über Linux-hwmon aktualisiert. Die Wassertemperatur bleibt der letzte sichere Kraken-Wert, weil Kraken-Statusabfragen während des exklusiven CAM-Raw-Streams pausiert bleiben; gespeicherte Hardwarekurven laufen weiter.": "The animation creates a seamless GIF loop with rotating rings, light points and orbits. CPU and GPU temperatures are safely refreshed through Linux hwmon. Liquid temperature remains the last safe Kraken value because Kraken status polling stays paused during the exclusive CAM-raw stream; stored hardware curves continue running.",
    "CPU/GPU live · Wasser letzter sicherer Wert": "CPU/GPU live · liquid last safe value",
    "CPU live": "CPU live", "GPU live": "GPU live", "Wasser letzter sicherer Wert": "liquid last safe value",
    "Livewerte aktualisiert": "Live values updated", "Livewert-Aktualisierung fehlgeschlagen": "Live value refresh failed", "Wasser zuletzt": "liquid last",
    "Die Animation aktualisiert CPU- und GPU-Temperaturen sicher über Linux-hwmon. Die Wassertemperatur bleibt während des exklusiven Streams der letzte sichere Kraken-Wert. Kraken-Statusabfragen und neue Kühlbefehle pausieren; die in der Kraken gespeicherten Kurven laufen weiter. Häufige LCD-Uploads bleiben experimentell. Hardwareanimation trotzdem starten?": "The animation safely refreshes CPU and GPU temperatures through Linux hwmon. During the exclusive stream, liquid temperature remains the last safe Kraken value. Kraken status polling and new cooling commands pause while curves stored in the Kraken continue. Frequent LCD uploads remain experimental. Start the hardware animation anyway?",
})
UI_TRANSLATIONS["es"].update({
    "Schrift- und Zahlen-Größe": "Tamaño de texto y números", "Animierte Hardwaredaten · Ringe und Orbits": "Datos de hardware animados · Anillos y órbitas",
    "20 FPS · ruhig": "20 FPS · tranquilo", "25 FPS · flüssig · empfohlen": "25 FPS · fluido · recomendado",
    "Animierte Vorschau erzeugen": "Generar vista animada", "Hardwareanimation starten": "Iniciar animación de hardware", "Hardwareanimation anhalten": "Detener animación de hardware",
    "Animationslayout": "Diseño de animación", "Animationsrate": "Velocidad de animación", "Animierte Hardwaredaten": "Datos de hardware animados",
    "Animierte Hardwaredaten: bereit · Farbe und Schriftgröße werden vom Live-Design übernommen.": "Datos de hardware animados: listo · El color y tamaño se comparten con el diseño en vivo.",
    "Die Animation erzeugt einen nahtlosen GIF-Loop mit rotierenden Ringen, Lichtpunkten und Orbits. Die angezeigten Temperaturen sind eine Momentaufnahme beim Start. Während des exklusiven CAM-Raw-Streams bleiben Kraken-Statusabfragen und neue Kühlbefehle wie bisher pausiert; gespeicherte Hardwarekurven laufen weiter.": "La animación crea un bucle GIF continuo con anillos, puntos luminosos y órbitas. Las temperaturas son una instantánea al iniciar. Durante el flujo CAM exclusivo se pausan el estado y nuevos comandos; las curvas guardadas continúan.",
    "Animierte Vorschau läuft · noch nicht auf das LCD übertragen.": "Vista animada en ejecución · aún no enviada al LCD.", "Die Hardwareanimation konnte nicht erzeugt werden:": "No se pudo crear la animación de hardware:",
    "Experimentelle Hardwareanimation": "Animación de hardware experimental", "Hardwareanimation wird vorbereitet …": "Preparando animación de hardware …", "Hardwareanimation vorbereitet": "Animación preparada", "Frames": "fotogramas",
    "LCD-Modus: animierte Hardwaredaten · experimentell": "Modo LCD: datos de hardware animados · experimental", "Hardwareanimation aktiv": "Animación de hardware activa", "Temperaturen als Start-Momentaufnahme": "temperaturas como instantánea inicial", "Upload": "envío",
    "Hardwareanimation angehalten · das letzte Bild kann sichtbar bleiben.": "Animación detenida · la última imagen puede seguir visible.", "Hardwareanimation angehalten": "Animación de hardware detenida", "Hardwareanimation: Fehler": "Animación de hardware: error",
    "Hardwareanimation: Start abgebrochen": "Animación de hardware: inicio cancelado", "Hardwareanimation: Datei nicht mehr vorhanden": "Animación de hardware: archivo no disponible", "Hardwareanimation-Hinweis": "Aviso de animación de hardware",
    "Die Animation verwendet die zuletzt gelesenen Temperaturen als Momentaufnahme. Während des Streams pausieren Kraken-Statusabfragen und neue Kühlbefehle; die in der Kraken gespeicherten Kurven laufen weiter. Häufige LCD-Uploads bleiben experimentell. Hardwareanimation trotzdem starten?": "La animación usa las últimas temperaturas como instantánea. Durante el flujo se pausan el estado y nuevos comandos, mientras continúan las curvas guardadas. Las cargas frecuentes siguen siendo experimentales. ¿Iniciar de todos modos?",
    "LCD-Modus: Live-Hardwaredesign": "Modo LCD: diseño de hardware en vivo",
    "Live-Hardwaredesign angehalten · das letzte Bild kann sichtbar bleiben.": "Diseño de hardware en vivo detenido · la última imagen puede seguir visible.",
    "Die Animation erzeugt einen nahtlosen GIF-Loop mit rotierenden Ringen, Lichtpunkten und Orbits. CPU- und GPU-Temperaturen werden währenddessen sicher über Linux-hwmon aktualisiert. Die Wassertemperatur bleibt der letzte sichere Kraken-Wert, weil Kraken-Statusabfragen während des exklusiven CAM-Raw-Streams pausiert bleiben; gespeicherte Hardwarekurven laufen weiter.": "La animación crea un bucle continuo con anillos, puntos luminosos y órbitas. Las temperaturas de CPU y GPU se actualizan de forma segura mediante hwmon de Linux. La temperatura del líquido conserva el último valor seguro de Kraken porque las consultas quedan pausadas durante el flujo CAM exclusivo; las curvas guardadas continúan.",
    "CPU/GPU live · Wasser letzter sicherer Wert": "CPU/GPU en vivo · líquido: último valor seguro",
    "CPU live": "CPU en vivo", "GPU live": "GPU en vivo", "Wasser letzter sicherer Wert": "líquido: último valor seguro",
    "Livewerte aktualisiert": "Valores en vivo actualizados", "Livewert-Aktualisierung fehlgeschlagen": "Error al actualizar valores en vivo", "Wasser zuletzt": "líquido último",
    "Die Animation aktualisiert CPU- und GPU-Temperaturen sicher über Linux-hwmon. Die Wassertemperatur bleibt während des exklusiven Streams der letzte sichere Kraken-Wert. Kraken-Statusabfragen und neue Kühlbefehle pausieren; die in der Kraken gespeicherten Kurven laufen weiter. Häufige LCD-Uploads bleiben experimentell. Hardwareanimation trotzdem starten?": "La animación actualiza de forma segura CPU y GPU mediante hwmon de Linux. Durante el flujo exclusivo, el líquido conserva el último valor seguro de Kraken. Se pausan las consultas y nuevos comandos, mientras continúan las curvas guardadas. Las cargas frecuentes siguen siendo experimentales. ¿Iniciar de todos modos?",
})
UI_TRANSLATIONS["fr"].update({
    "Schrift- und Zahlen-Größe": "Taille du texte et des nombres", "Animierte Hardwaredaten · Ringe und Orbits": "Données matérielles animées · Anneaux et orbites",
    "20 FPS · ruhig": "20 FPS · calme", "25 FPS · flüssig · empfohlen": "25 FPS · fluide · recommandé",
    "Animierte Vorschau erzeugen": "Générer l’aperçu animé", "Hardwareanimation starten": "Démarrer l’animation matérielle", "Hardwareanimation anhalten": "Arrêter l’animation matérielle",
    "Animationslayout": "Disposition de l’animation", "Animationsrate": "Fréquence de l’animation", "Animierte Hardwaredaten": "Données matérielles animées",
    "Animierte Hardwaredaten: bereit · Farbe und Schriftgröße werden vom Live-Design übernommen.": "Données matérielles animées : prêt · La couleur et la taille sont partagées avec le design en direct.",
    "Die Animation erzeugt einen nahtlosen GIF-Loop mit rotierenden Ringen, Lichtpunkten und Orbits. Die angezeigten Temperaturen sind eine Momentaufnahme beim Start. Während des exklusiven CAM-Raw-Streams bleiben Kraken-Statusabfragen und neue Kühlbefehle wie bisher pausiert; gespeicherte Hardwarekurven laufen weiter.": "L’animation crée une boucle GIF continue avec anneaux, points lumineux et orbites. Les températures sont un instantané au démarrage. Pendant le flux CAM exclusif, les états et nouvelles commandes sont suspendus ; les courbes enregistrées continuent.",
    "Animierte Vorschau läuft · noch nicht auf das LCD übertragen.": "Aperçu animé en cours · pas encore envoyé au LCD.", "Die Hardwareanimation konnte nicht erzeugt werden:": "Impossible de créer l’animation matérielle :",
    "Experimentelle Hardwareanimation": "Animation matérielle expérimentale", "Hardwareanimation wird vorbereitet …": "Préparation de l’animation matérielle …", "Hardwareanimation vorbereitet": "Animation préparée", "Frames": "images",
    "LCD-Modus: animierte Hardwaredaten · experimentell": "Mode LCD : données matérielles animées · expérimental", "Hardwareanimation aktiv": "Animation matérielle active", "Temperaturen als Start-Momentaufnahme": "températures comme instantané initial", "Upload": "envoi",
    "Hardwareanimation angehalten · das letzte Bild kann sichtbar bleiben.": "Animation arrêtée · la dernière image peut rester visible.", "Hardwareanimation angehalten": "Animation matérielle arrêtée", "Hardwareanimation: Fehler": "Animation matérielle : erreur",
    "Hardwareanimation: Start abgebrochen": "Animation matérielle : démarrage annulé", "Hardwareanimation: Datei nicht mehr vorhanden": "Animation matérielle : fichier indisponible", "Hardwareanimation-Hinweis": "Avis d’animation matérielle",
    "Die Animation verwendet die zuletzt gelesenen Temperaturen als Momentaufnahme. Während des Streams pausieren Kraken-Statusabfragen und neue Kühlbefehle; die in der Kraken gespeicherten Kurven laufen weiter. Häufige LCD-Uploads bleiben experimentell. Hardwareanimation trotzdem starten?": "L’animation utilise les dernières températures comme instantané. Pendant le flux, les états et nouvelles commandes sont suspendus tandis que les courbes enregistrées continuent. Les envois fréquents restent expérimentaux. Démarrer quand même ?",
    "LCD-Modus: Live-Hardwaredesign": "Mode LCD : design matériel en direct",
    "Live-Hardwaredesign angehalten · das letzte Bild kann sichtbar bleiben.": "Design matériel en direct arrêté · la dernière image peut rester visible.",
    "Die Animation erzeugt einen nahtlosen GIF-Loop mit rotierenden Ringen, Lichtpunkten und Orbits. CPU- und GPU-Temperaturen werden währenddessen sicher über Linux-hwmon aktualisiert. Die Wassertemperatur bleibt der letzte sichere Kraken-Wert, weil Kraken-Statusabfragen während des exklusiven CAM-Raw-Streams pausiert bleiben; gespeicherte Hardwarekurven laufen weiter.": "L’animation crée une boucle continue avec anneaux, points lumineux et orbites. Les températures CPU et GPU sont actualisées en toute sécurité via hwmon Linux. Le liquide conserve la dernière valeur Kraken sûre car les états restent suspendus pendant le flux CAM exclusif ; les courbes enregistrées continuent.",
    "CPU/GPU live · Wasser letzter sicherer Wert": "CPU/GPU en direct · liquide : dernière valeur sûre",
    "CPU live": "CPU en direct", "GPU live": "GPU en direct", "Wasser letzter sicherer Wert": "liquide : dernière valeur sûre",
    "Livewerte aktualisiert": "Valeurs en direct actualisées", "Livewert-Aktualisierung fehlgeschlagen": "Échec de l’actualisation en direct", "Wasser zuletzt": "liquide dernier",
    "Die Animation aktualisiert CPU- und GPU-Temperaturen sicher über Linux-hwmon. Die Wassertemperatur bleibt während des exklusiven Streams der letzte sichere Kraken-Wert. Kraken-Statusabfragen und neue Kühlbefehle pausieren; die in der Kraken gespeicherten Kurven laufen weiter. Häufige LCD-Uploads bleiben experimentell. Hardwareanimation trotzdem starten?": "L’animation actualise en toute sécurité le CPU et le GPU via hwmon Linux. Pendant le flux exclusif, le liquide conserve la dernière valeur Kraken sûre. Les états et nouvelles commandes sont suspendus tandis que les courbes enregistrées continuent. Les envois fréquents restent expérimentaux. Démarrer quand même ?",
})
UI_TRANSLATIONS["en"].update({
    "Geräte": "Devices", "Diagnose": "Diagnostics", "Corsair · OpenLinkHub": "Corsair · OpenLinkHub",
    "Nicht erkannte Geräte/Module anzeigen": "Show undetected devices/modules",
    "Gemeinsame Linux-Hardwarezentrale · NZXT Kraken · Corsair/OpenLinkHub": "Shared Linux hardware hub · NZXT Kraken · Corsair/OpenLinkHub",
    "OpenLinkHub-Status": "OpenLinkHub status", "↻ OpenLinkHub aktualisieren": "↻ Refresh OpenLinkHub",
    "Web-Dashboard öffnen": "Open web dashboard", "Benutzerdienst starten": "Start user service",
    "Benutzerdienst stoppen": "Stop user service", "Benutzerdienst neu starten": "Restart user service",
    "Beim Login aktivieren": "Enable at login",
    "Dienstkontext und Hilfe": "Service context and help", "Gerät": "Device", "Kanal": "Channel",
    "Temperatur": "Temperature", "Drehzahl": "Speed", "Firmware": "Firmware",
    "Offizielles OpenLinkHub-Projekt": "Official OpenLinkHub project", "API-Dokumentation": "API documentation",
    "Offizielle Benutzerinstallation": "Official user installation",
    "Migrationshilfe: System → Benutzer": "Migration help: system → user",
})
UI_TRANSLATIONS["es"].update({
    "Geräte": "Dispositivos", "Diagnose": "Diagnóstico", "Corsair · OpenLinkHub": "Corsair · OpenLinkHub",
    "Nicht erkannte Geräte/Module anzeigen": "Mostrar dispositivos/módulos no detectados",
    "Gemeinsame Linux-Hardwarezentrale · NZXT Kraken · Corsair/OpenLinkHub": "Centro de hardware Linux · NZXT Kraken · Corsair/OpenLinkHub",
    "OpenLinkHub-Status": "Estado de OpenLinkHub", "↻ OpenLinkHub aktualisieren": "↻ Actualizar OpenLinkHub",
    "Web-Dashboard öffnen": "Abrir panel web", "Benutzerdienst starten": "Iniciar servicio de usuario",
    "Benutzerdienst stoppen": "Detener servicio de usuario", "Benutzerdienst neu starten": "Reiniciar servicio de usuario",
    "Beim Login aktivieren": "Activar al iniciar sesión",
    "Dienstkontext und Hilfe": "Contexto del servicio y ayuda", "Gerät": "Dispositivo", "Kanal": "Canal",
    "Temperatur": "Temperatura", "Drehzahl": "Velocidad", "Firmware": "Firmware",
    "Offizielles OpenLinkHub-Projekt": "Proyecto oficial OpenLinkHub", "API-Dokumentation": "Documentación API",
    "Offizielle Benutzerinstallation": "Instalación oficial de usuario",
    "Migrationshilfe: System → Benutzer": "Ayuda de migración: sistema → usuario",
})
UI_TRANSLATIONS["fr"].update({
    "Geräte": "Appareils", "Diagnose": "Diagnostic", "Corsair · OpenLinkHub": "Corsair · OpenLinkHub",
    "Nicht erkannte Geräte/Module anzeigen": "Afficher les appareils/modules non détectés",
    "Gemeinsame Linux-Hardwarezentrale · NZXT Kraken · Corsair/OpenLinkHub": "Centre matériel Linux · NZXT Kraken · Corsair/OpenLinkHub",
    "OpenLinkHub-Status": "État OpenLinkHub", "↻ OpenLinkHub aktualisieren": "↻ Actualiser OpenLinkHub",
    "Web-Dashboard öffnen": "Ouvrir le tableau de bord web", "Benutzerdienst starten": "Démarrer le service utilisateur",
    "Benutzerdienst stoppen": "Arrêter le service utilisateur", "Benutzerdienst neu starten": "Redémarrer le service utilisateur",
    "Beim Login aktivieren": "Activer à la connexion",
    "Dienstkontext und Hilfe": "Contexte du service et aide", "Gerät": "Appareil", "Kanal": "Canal",
    "Temperatur": "Température", "Drehzahl": "Vitesse", "Firmware": "Micrologiciel",
    "Offizielles OpenLinkHub-Projekt": "Projet OpenLinkHub officiel", "API-Dokumentation": "Documentation API",
    "Offizielle Benutzerinstallation": "Installation utilisateur officielle",
    "Migrationshilfe: System → Benutzer": "Aide à la migration : système → utilisateur",
})
UI_TRANSLATIONS["en"].update({
    "Direkte Gerätesteuerung": "Direct device control", "Direkte OpenLinkHub-Schreibzugriffe für diese Programmsitzung aktivieren": "Enable direct OpenLinkHub writes for this application session",
    "Kühlung": "Cooling", "RGB und Gerät": "RGB and device", "Maus": "Mouse", "Tastatur": "Keyboard", "Headset": "Headset", "Netzteil": "Power supply",
    "Corsair-Kühlgerät": "Corsair cooling device", "Lüfter-/Pumpenkanal": "Fan/pump channel", "Vorhandenes Temperaturprofil": "Existing temperature profile",
    "Temperaturprofil auf Kanal anwenden": "Apply temperature profile to channel", "Manuelle Leistung": "Manual output", "Manuellen Wert auf Kanal anwenden": "Apply manual value to channel",
    "Vorhandenes RGB-Profil": "Existing RGB profile", "RGB-Profil auf Kanal anwenden": "Apply RGB profile to channel", "Neue Kanalbezeichnung": "New channel label",
    "Kanalbezeichnung speichern": "Save channel label", "Gerätehelligkeit": "Device brightness", "Helligkeit anwenden": "Apply brightness", "LCD-Ausrichtung": "LCD rotation", "LCD-Ausrichtung anwenden": "Apply LCD rotation",
    "Corsair-Maus": "Corsair mouse", "Fünf DPI-Stufen": "Five DPI stages", "DPI-Stufen anwenden": "Apply DPI stages", "USB-Abfragerate": "USB polling rate", "Abfragerate anwenden": "Apply polling rate", "Ruhemodus": "Sleep mode", "Ruhemodus anwenden": "Apply sleep mode",
    "Corsair-Tastatur": "Corsair keyboard", "Benutzerprofil wechseln": "Switch user profile", "Tastaturprofil wechseln": "Switch keyboard profile", "Tastaturbelegung": "Keyboard layout", "Tastaturbelegung anwenden": "Apply keyboard layout",
    "Corsair-Headset": "Corsair headset", "Geräuschmodus": "Noise mode", "Geräuschmodus anwenden": "Apply noise mode", "Sidetone-Lautstärke": "Sidetone volume", "Sidetone-Lautstärke anwenden": "Apply sidetone volume", "Corsair-Netzteil": "Corsair power supply", "Netzteil-Lüftermodus anwenden": "Apply PSU fan mode",
})
UI_TRANSLATIONS["es"].update({
    "Direkte Gerätesteuerung": "Control directo del dispositivo", "Direkte OpenLinkHub-Schreibzugriffe für diese Programmsitzung aktivieren": "Activar escritura directa de OpenLinkHub para esta sesión",
    "Kühlung": "Refrigeración", "RGB und Gerät": "RGB y dispositivo", "Maus": "Ratón", "Tastatur": "Teclado", "Headset": "Auriculares", "Netzteil": "Fuente de alimentación",
    "Corsair-Kühlgerät": "Dispositivo de refrigeración Corsair", "Lüfter-/Pumpenkanal": "Canal de ventilador/bomba", "Vorhandenes Temperaturprofil": "Perfil de temperatura existente",
    "Temperaturprofil auf Kanal anwenden": "Aplicar perfil de temperatura al canal", "Manuelle Leistung": "Potencia manual", "Manuellen Wert auf Kanal anwenden": "Aplicar valor manual al canal",
    "Vorhandenes RGB-Profil": "Perfil RGB existente", "RGB-Profil auf Kanal anwenden": "Aplicar perfil RGB al canal", "Neue Kanalbezeichnung": "Nueva etiqueta de canal", "Kanalbezeichnung speichern": "Guardar etiqueta",
    "Gerätehelligkeit": "Brillo del dispositivo", "Helligkeit anwenden": "Aplicar brillo", "LCD-Ausrichtung": "Rotación LCD", "LCD-Ausrichtung anwenden": "Aplicar rotación LCD",
    "Corsair-Maus": "Ratón Corsair", "Fünf DPI-Stufen": "Cinco niveles DPI", "DPI-Stufen anwenden": "Aplicar niveles DPI", "USB-Abfragerate": "Frecuencia USB", "Ruhemodus": "Modo de reposo",
    "Corsair-Tastatur": "Teclado Corsair", "Benutzerprofil wechseln": "Cambiar perfil de usuario", "Tastaturprofil wechseln": "Cambiar perfil de teclado", "Tastaturbelegung": "Distribución del teclado",
    "Corsair-Headset": "Auriculares Corsair", "Geräuschmodus": "Modo de ruido", "Sidetone-Lautstärke": "Volumen de sidetone", "Corsair-Netzteil": "Fuente Corsair", "Netzteil-Lüftermodus anwenden": "Aplicar modo del ventilador",
})
UI_TRANSLATIONS["fr"].update({
    "Direkte Gerätesteuerung": "Commande directe de l’appareil", "Direkte OpenLinkHub-Schreibzugriffe für diese Programmsitzung aktivieren": "Activer les écritures OpenLinkHub directes pour cette session",
    "Kühlung": "Refroidissement", "RGB und Gerät": "RGB et appareil", "Maus": "Souris", "Tastatur": "Clavier", "Headset": "Casque", "Netzteil": "Alimentation",
    "Corsair-Kühlgerät": "Appareil de refroidissement Corsair", "Lüfter-/Pumpenkanal": "Canal ventilateur/pompe", "Vorhandenes Temperaturprofil": "Profil de température existant",
    "Temperaturprofil auf Kanal anwenden": "Appliquer le profil au canal", "Manuelle Leistung": "Puissance manuelle", "Manuellen Wert auf Kanal anwenden": "Appliquer la valeur manuelle au canal",
    "Vorhandenes RGB-Profil": "Profil RGB existant", "RGB-Profil auf Kanal anwenden": "Appliquer le profil RGB", "Neue Kanalbezeichnung": "Nouveau libellé du canal", "Kanalbezeichnung speichern": "Enregistrer le libellé",
    "Gerätehelligkeit": "Luminosité de l’appareil", "Helligkeit anwenden": "Appliquer la luminosité", "LCD-Ausrichtung": "Rotation LCD", "LCD-Ausrichtung anwenden": "Appliquer la rotation LCD",
    "Corsair-Maus": "Souris Corsair", "Fünf DPI-Stufen": "Cinq niveaux DPI", "DPI-Stufen anwenden": "Appliquer les niveaux DPI", "USB-Abfragerate": "Fréquence USB", "Ruhemodus": "Mode veille",
    "Corsair-Tastatur": "Clavier Corsair", "Benutzerprofil wechseln": "Changer le profil utilisateur", "Tastaturprofil wechseln": "Changer le profil clavier", "Tastaturbelegung": "Disposition du clavier",
    "Corsair-Headset": "Casque Corsair", "Geräuschmodus": "Mode de bruit", "Sidetone-Lautstärke": "Volume du retour micro", "Corsair-Netzteil": "Alimentation Corsair", "Netzteil-Lüftermodus anwenden": "Appliquer le mode ventilateur",
})
_GIF_COOLING_WARNING = (
    "Die Animation aktualisiert CPU- und GPU-Temperaturen sicher über Linux-hwmon. Die Wassertemperatur bleibt während "
    "des exklusiven Streams der letzte sichere Kraken-Wert. Kraken-Statusabfragen pausieren, aber aktive Pumpen- und "
    "Lüfterkurven lesen die CPU weiter. Nur eine relevante Drehzahländerung unterbricht die Animation kurz; anschließend "
    "läuft derselbe Framecache automatisch weiter. Häufige LCD-Uploads bleiben experimentell. Hardwareanimation trotzdem starten?"
)
UI_TRANSLATIONS["en"][_GIF_COOLING_WARNING] = (
    "The animation safely refreshes CPU and GPU temperatures through Linux hwmon. Liquid temperature remains the last "
    "safe Kraken value while status polling is paused, but active pump and fan curves keep reading the CPU. Only a relevant "
    "duty change briefly interrupts the animation before the same cached stream continues. Frequent LCD uploads "
    "remain experimental. Start the hardware animation anyway?"
)
UI_TRANSLATIONS["es"][_GIF_COOLING_WARNING] = (
    "La animación actualiza CPU y GPU mediante hwmon de Linux. El líquido conserva el último valor seguro mientras las "
    "consultas están pausadas, pero las curvas activas siguen leyendo la CPU. Solo un cambio relevante interrumpe brevemente "
    "la animación y después continúa el mismo flujo. ¿Iniciar la animación experimental?"
)
UI_TRANSLATIONS["fr"][_GIF_COOLING_WARNING] = (
    "L’animation actualise le CPU et le GPU via hwmon Linux. Le liquide conserve la dernière valeur sûre pendant la pause "
    "des états, mais les courbes actives continuent de lire le CPU. Seule une variation utile interrompt brièvement "
    "l’animation puis reprend automatiquement le même flux. Démarrer l’animation expérimentale ?"
)

UI_TRANSLATIONS["en"].update({
    "Betriebsart umschalten": "Switch operating mode",
    "Manuell aktivieren": "Activate manual mode",
    "Pumpenkurve aktivieren": "Activate pump curve",
    "Lüfterkurve aktivieren": "Activate fan curve",
    "Der markierte Modus wurde zuletzt erfolgreich auf die Kraken übertragen. Das Bearbeiten eines Reglers oder einer Kurve ändert den aktiven Modus erst beim Anwenden.":
        "The highlighted mode was last applied successfully to the Kraken. Editing a slider or curve does not change the active mode until it is applied.",
})
UI_TRANSLATIONS["es"].update({
    "Betriebsart umschalten": "Cambiar modo de funcionamiento",
    "Manuell aktivieren": "Activar modo manual",
    "Pumpenkurve aktivieren": "Activar curva de bomba",
    "Lüfterkurve aktivieren": "Activar curva de ventiladores",
    "Der markierte Modus wurde zuletzt erfolgreich auf die Kraken übertragen. Das Bearbeiten eines Reglers oder einer Kurve ändert den aktiven Modus erst beim Anwenden.":
        "El modo marcado es el último aplicado correctamente al Kraken. Editar un control o una curva no cambia el modo activo hasta aplicarlo.",
})
UI_TRANSLATIONS["fr"].update({
    "Betriebsart umschalten": "Changer de mode de fonctionnement",
    "Manuell aktivieren": "Activer le mode manuel",
    "Pumpenkurve aktivieren": "Activer la courbe de pompe",
    "Lüfterkurve aktivieren": "Activer la courbe des ventilateurs",
    "Der markierte Modus wurde zuletzt erfolgreich auf die Kraken übertragen. Das Bearbeiten eines Reglers oder einer Kurve ändert den aktiven Modus erst beim Anwenden.":
        "Le mode marqué est le dernier appliqué avec succès au Kraken. Modifier un réglage ou une courbe ne change le mode actif qu’après application.",
})

# 3.0.5: visible NZXT curves are evaluated from the CPU sensor.  Liquid
# temperature remains a separate emergency safeguard.
UI_TRANSLATIONS["en"].update({
    "Pumpenkurve nach CPU-Temperatur": "Pump curve by CPU temperature",
    "Lüfterkurve nach CPU-Temperatur": "Fan curve by CPU temperature",
    "AMD-AM5-Prozessorprofil für CPU-Kurven": "AMD AM5 processor profile for CPU curves",
    "CPU-Kurven werden von Open Hardware Control laufend berechnet. Ein manueller Wert oder ein Schnellprofil deaktiviert die CPU-Kurve des jeweiligen Kanals.": "Open Hardware Control continuously evaluates CPU curves. A manual value or quick profile disables the CPU curve for that channel.",
    "Die Profile setzen beide sichtbaren Kurven passend zur CPU-Temperatur. Die Wassertemperatur bleibt unabhängig davon als zusätzliche Sicherheitsüberwachung aktiv.": "Profiles configure both visible curves for CPU temperature. Liquid temperature remains active independently as an additional safety monitor.",
    "Die Animation erzeugt einen nahtlosen GIF-Loop mit rotierenden Ringen, Lichtpunkten und Orbits. CPU- und GPU-Temperaturen werden währenddessen sicher über Linux-hwmon aktualisiert. Die Wassertemperatur bleibt der letzte sichere Kraken-Wert, weil Kraken-Statusabfragen während des exklusiven CAM-Raw-Streams pausiert bleiben. Aktive Pumpen- und Lüfterkurven lesen die CPU trotzdem weiter. Eine relevante Drehzahländerung verwendet die koordinierte Kurzpause und setzt danach denselben Framecache fort.": "The animation creates a seamless GIF loop with rotating rings, light points and orbits. CPU and GPU temperatures are refreshed safely through Linux hwmon. Liquid remains the last safe Kraken value while status polling is paused. Active pump and fan curves keep reading the CPU; a relevant duty change uses the coordinated short handoff and then resumes the same frame cache.",
})
UI_TRANSLATIONS["es"].update({
    "Pumpenkurve nach CPU-Temperatur": "Curva de bomba según la temperatura de CPU",
    "Lüfterkurve nach CPU-Temperatur": "Curva de ventiladores según la temperatura de CPU",
    "AMD-AM5-Prozessorprofil für CPU-Kurven": "Perfil de procesador AMD AM5 para curvas de CPU",
    "CPU-Kurven werden von Open Hardware Control laufend berechnet. Ein manueller Wert oder ein Schnellprofil deaktiviert die CPU-Kurve des jeweiligen Kanals.": "Open Hardware Control calcula continuamente las curvas de CPU. Un valor manual o perfil rápido desactiva la curva de CPU de ese canal.",
    "Die Profile setzen beide sichtbaren Kurven passend zur CPU-Temperatur. Die Wassertemperatur bleibt unabhängig davon als zusätzliche Sicherheitsüberwachung aktiv.": "Los perfiles configuran ambas curvas visibles según la temperatura de CPU. La temperatura del líquido sigue activa como vigilancia de seguridad adicional.",
    "Die Animation erzeugt einen nahtlosen GIF-Loop mit rotierenden Ringen, Lichtpunkten und Orbits. CPU- und GPU-Temperaturen werden währenddessen sicher über Linux-hwmon aktualisiert. Die Wassertemperatur bleibt der letzte sichere Kraken-Wert, weil Kraken-Statusabfragen während des exklusiven CAM-Raw-Streams pausiert bleiben. Aktive Pumpen- und Lüfterkurven lesen die CPU trotzdem weiter. Eine relevante Drehzahländerung verwendet die koordinierte Kurzpause und setzt danach denselben Framecache fort.": "La animación crea un bucle continuo con anillos, puntos luminosos y órbitas. CPU y GPU se actualizan mediante hwmon. El líquido conserva el último valor seguro mientras las consultas Kraken están pausadas. Las curvas activas siguen leyendo la CPU; un cambio relevante usa la entrega breve coordinada y reanuda el mismo caché.",
})
UI_TRANSLATIONS["fr"].update({
    "Pumpenkurve nach CPU-Temperatur": "Courbe de pompe selon la température CPU",
    "Lüfterkurve nach CPU-Temperatur": "Courbe des ventilateurs selon la température CPU",
    "AMD-AM5-Prozessorprofil für CPU-Kurven": "Profil processeur AMD AM5 pour les courbes CPU",
    "CPU-Kurven werden von Open Hardware Control laufend berechnet. Ein manueller Wert oder ein Schnellprofil deaktiviert die CPU-Kurve des jeweiligen Kanals.": "Open Hardware Control calcule continuellement les courbes CPU. Une valeur manuelle ou un profil rapide désactive la courbe CPU du canal concerné.",
    "Die Profile setzen beide sichtbaren Kurven passend zur CPU-Temperatur. Die Wassertemperatur bleibt unabhängig davon als zusätzliche Sicherheitsüberwachung aktiv.": "Les profils configurent les deux courbes visibles selon la température CPU. La température du liquide reste active comme surveillance de sécurité supplémentaire.",
    "Die Animation erzeugt einen nahtlosen GIF-Loop mit rotierenden Ringen, Lichtpunkten und Orbits. CPU- und GPU-Temperaturen werden währenddessen sicher über Linux-hwmon aktualisiert. Die Wassertemperatur bleibt der letzte sichere Kraken-Wert, weil Kraken-Statusabfragen während des exklusiven CAM-Raw-Streams pausiert bleiben. Aktive Pumpen- und Lüfterkurven lesen die CPU trotzdem weiter. Eine relevante Drehzahländerung verwendet die koordinierte Kurzpause und setzt danach denselben Framecache fort.": "L’animation crée une boucle continue avec anneaux, points lumineux et orbites. CPU et GPU sont actualisés via hwmon. Le liquide conserve la dernière valeur sûre pendant la pause des états Kraken. Les courbes actives continuent de lire le CPU ; un changement utile emploie la remise brève coordonnée puis reprend le même cache.",
})


UI_TRANSLATIONS["en"].update({
    "Desktop-Designs": "Desktop designs",
    "Desktopumgebung und Kompatibilität": "Desktop environment and compatibility",
    "Status erneut prüfen": "Check status again",
    "Farbmodus für das Systemdesign": "System-design colour mode",
    "Windows-11-Stil": "Windows 11 style",
    "macOS-Stil": "macOS style",
    "Änderungen anzeigen": "Show changes",
    "Desktop-Design anwenden": "Apply desktop design",
    "Sicherung und Wiederherstellung": "Backup and restore",
    "Letztes Desktop-Backup wiederherstellen": "Restore latest desktop backup",
})
UI_TRANSLATIONS["es"].update({
    "Desktop-Designs": "Diseños de escritorio",
    "Desktopumgebung und Kompatibilität": "Entorno de escritorio y compatibilidad",
    "Status erneut prüfen": "Comprobar estado otra vez",
    "Farbmodus für das Systemdesign": "Modo de color del diseño del sistema",
    "Windows-11-Stil": "Estilo Windows 11",
    "macOS-Stil": "Estilo macOS",
    "Änderungen anzeigen": "Mostrar cambios",
    "Desktop-Design anwenden": "Aplicar diseño de escritorio",
    "Sicherung und Wiederherstellung": "Copia de seguridad y restauración",
    "Letztes Desktop-Backup wiederherstellen": "Restaurar la última copia del escritorio",
})
UI_TRANSLATIONS["fr"].update({
    "Desktop-Designs": "Designs du bureau",
    "Desktopumgebung und Kompatibilität": "Environnement de bureau et compatibilité",
    "Status erneut prüfen": "Vérifier à nouveau",
    "Farbmodus für das Systemdesign": "Mode de couleur du design système",
    "Windows-11-Stil": "Style Windows 11",
    "macOS-Stil": "Style macOS",
    "Änderungen anzeigen": "Afficher les changements",
    "Desktop-Design anwenden": "Appliquer le design du bureau",
    "Sicherung und Wiederherstellung": "Sauvegarde et restauration",
    "Letztes Desktop-Backup wiederherstellen": "Restaurer la dernière sauvegarde du bureau",
})



UI_TRANSLATIONS["en"].update({
    "Hilfe": "Help", "Hilfe & Anleitungen": "Help & guides", "Hilfe durchsuchen …": "Search help …", "Anleitung auswählen": "Select a guide",
    "Hilfe und Anleitungen öffnen": "Open help and guides", "Erste Schritte nach der Einrichtung öffnen": "Open getting started after setup",
    "LCD-Vorschau": "LCD preview", "Display-Einstellungen": "Display settings", "Hardwaredaten & Uhr": "Hardware data & clock",
})
UI_TRANSLATIONS["es"].update({
    "Hilfe": "Ayuda", "Hilfe & Anleitungen": "Ayuda y guías", "Hilfe durchsuchen …": "Buscar ayuda …", "Anleitung auswählen": "Seleccionar una guía",
    "Hilfe und Anleitungen öffnen": "Abrir ayuda y guías", "Erste Schritte nach der Einrichtung öffnen": "Abrir primeros pasos tras la configuración",
    "LCD-Vorschau": "Vista previa LCD", "Display-Einstellungen": "Ajustes de pantalla", "Hardwaredaten & Uhr": "Datos de hardware y reloj",
})
UI_TRANSLATIONS["fr"].update({
    "Hilfe": "Aide", "Hilfe & Anleitungen": "Aide et guides", "Hilfe durchsuchen …": "Rechercher dans l’aide …", "Anleitung auswählen": "Choisir un guide",
    "Hilfe und Anleitungen öffnen": "Ouvrir l’aide et les guides", "Erste Schritte nach der Einrichtung öffnen": "Ouvrir les premiers pas après la configuration",
    "LCD-Vorschau": "Aperçu LCD", "Display-Einstellungen": "Réglages de l’écran", "Hardwaredaten & Uhr": "Données matérielles et horloge",
})


UI_TRANSLATIONS["en"].update({
    "Schritt-für-Schritt-Anleitungen für die wichtigsten Bereiche. Über die Links in einer Anleitung kannst du direkt zum passenden Bereich springen.": "Step-by-step guides for the most important areas. Links inside a guide can take you directly to the matching section.",
    "Akzentfarbe für Ringe": "Accent colour for rings", "Farbe der Beschriftung": "Label colour", "Farbe der Temperaturzahl": "Temperature value colour",
    "Größe der Beschriftung": "Label size", "Größe der Temperaturzahl": "Temperature value size", "LCD-Ebenen · Bild/GIF + Hardwaredaten": "LCD layers · image/GIF + hardware data",
    "Ebenenmodus starten": "Start layer mode", "Ebenenmodus anhalten": "Stop layer mode", "Ebenenvorschau erzeugen": "Generate layer preview",
    "Hardwareebene fest": "Static hardware layer", "Hardwareebene animiert": "Animated hardware layer", "Hardwarebewegung": "Hardware motion", "Hardwarelayout": "Hardware layout",
    "Hintergrund: zuerst oben ein Bild oder GIF auswählen": "Background: first select an image or GIF above", "Position": "Position", "Größe": "Size", "Deckkraft": "Opacity",
    "Nur aktivieren, wenn die Kraken nach einigen Sekunden selbstständig zum Standardbild zurückwechselt.": "Only enable this if the Kraken returns to its default screen by itself after a few seconds.",
    "Sendet das aktuelle Minutenbild zusätzlich regelmäßig erneut, falls die Kraken zum Standardbild zurückspringt.": "Periodically resends the current minute image if the Kraken returns to its default screen.",
})
UI_TRANSLATIONS["es"].update({
    "Schritt-für-Schritt-Anleitungen für die wichtigsten Bereiche. Über die Links in einer Anleitung kannst du direkt zum passenden Bereich springen.": "Guías paso a paso para las áreas más importantes. Los enlaces de cada guía te llevan directamente al apartado correspondiente.",
    "Akzentfarbe für Ringe": "Color de acento de los anillos", "Farbe der Beschriftung": "Color de etiqueta", "Farbe der Temperaturzahl": "Color del valor de temperatura",
    "Größe der Beschriftung": "Tamaño de etiqueta", "Größe der Temperaturzahl": "Tamaño del valor de temperatura", "LCD-Ebenen · Bild/GIF + Hardwaredaten": "Capas LCD · imagen/GIF + datos de hardware",
    "Ebenenmodus starten": "Iniciar modo de capas", "Ebenenmodus anhalten": "Detener modo de capas", "Ebenenvorschau erzeugen": "Generar vista previa de capas",
    "Hardwareebene fest": "Capa de hardware estática", "Hardwareebene animiert": "Capa de hardware animada", "Hardwarebewegung": "Movimiento de hardware", "Hardwarelayout": "Diseño de hardware",
    "Hintergrund: zuerst oben ein Bild oder GIF auswählen": "Fondo: primero selecciona arriba una imagen o GIF", "Position": "Posición", "Größe": "Tamaño", "Deckkraft": "Opacidad",
    "Nur aktivieren, wenn die Kraken nach einigen Sekunden selbstständig zum Standardbild zurückwechselt.": "Actívalo solo si Kraken vuelve por sí sola a la pantalla predeterminada tras unos segundos.",
    "Sendet das aktuelle Minutenbild zusätzlich regelmäßig erneut, falls die Kraken zum Standardbild zurückspringt.": "Vuelve a enviar periódicamente la imagen del minuto actual si Kraken regresa a la pantalla predeterminada.",
})
UI_TRANSLATIONS["fr"].update({
    "Schritt-für-Schritt-Anleitungen für die wichtigsten Bereiche. Über die Links in einer Anleitung kannst du direkt zum passenden Bereich springen.": "Guides pas à pas pour les zones principales. Les liens d’un guide ouvrent directement la section correspondante.",
    "Akzentfarbe für Ringe": "Couleur d’accent des anneaux", "Farbe der Beschriftung": "Couleur du libellé", "Farbe der Temperaturzahl": "Couleur de la valeur de température",
    "Größe der Beschriftung": "Taille du libellé", "Größe der Temperaturzahl": "Taille de la valeur de température", "LCD-Ebenen · Bild/GIF + Hardwaredaten": "Calques LCD · image/GIF + données matérielles",
    "Ebenenmodus starten": "Démarrer le mode calques", "Ebenenmodus anhalten": "Arrêter le mode calques", "Ebenenvorschau erzeugen": "Générer l’aperçu des calques",
    "Hardwareebene fest": "Calque matériel fixe", "Hardwareebene animiert": "Calque matériel animé", "Hardwarebewegung": "Mouvement matériel", "Hardwarelayout": "Disposition matérielle",
    "Hintergrund: zuerst oben ein Bild oder GIF auswählen": "Arrière-plan : choisissez d’abord une image ou un GIF ci-dessus", "Position": "Position", "Größe": "Taille", "Deckkraft": "Opacité",
    "Nur aktivieren, wenn die Kraken nach einigen Sekunden selbstständig zum Standardbild zurückwechselt.": "Activez uniquement si la Kraken revient seule à son écran par défaut après quelques secondes.",
    "Sendet das aktuelle Minutenbild zusätzlich regelmäßig erneut, falls die Kraken zum Standardbild zurückspringt.": "Renvoie régulièrement l’image de la minute actuelle si la Kraken revient à son écran par défaut.",
})

# The first-run wizard is created after the normal static translation capture,
# so it owns a small dedicated translation table.  This also lets the very
# first page switch the rest of the wizard immediately before any setup choice
# is made.

UI_TRANSLATIONS["en"].update({
    "Inhalt & Design": "Content & design", "Mitgelieferte Animationen": "Bundled animations",
    "Eigene Datei": "Custom file", "Statisch": "Static", "Animiert": "Animated",
    "Darstellung": "Presentation", "Hardwaredaten & Ebenen": "Hardware data & layers",
    "Hardwaredaten": "Hardware data", "Bild/GIF + Hardwaredaten": "Image/GIF + hardware data",
    "Uhr zusätzlich einblenden": "Overlay clock", "Erweiterte Animationsoptionen": "Advanced animation options",
    "Erweiterte Optionen ausblenden": "Hide advanced options", "Design auswählen": "Select design",
    "Animation direkt starten": "Start animation directly", "Als Hintergrund verwenden": "Use as background",
    "Keine Fremdmedien · acht originale OHC-Designs": "No third-party media · eight original OHC designs",
})
UI_TRANSLATIONS["es"].update({
    "Inhalt & Design": "Contenido y diseño", "Mitgelieferte Animationen": "Animaciones incluidas",
    "Eigene Datei": "Archivo propio", "Statisch": "Estático", "Animiert": "Animado",
    "Darstellung": "Presentación", "Hardwaredaten & Ebenen": "Datos de hardware y capas",
    "Hardwaredaten": "Datos de hardware", "Bild/GIF + Hardwaredaten": "Imagen/GIF + datos de hardware",
    "Uhr zusätzlich einblenden": "Superponer reloj", "Erweiterte Animationsoptionen": "Opciones avanzadas de animación",
    "Erweiterte Optionen ausblenden": "Ocultar opciones avanzadas", "Design auswählen": "Seleccionar diseño",
    "Animation direkt starten": "Iniciar animación directamente", "Als Hintergrund verwenden": "Usar como fondo",
    "Keine Fremdmedien · acht originale OHC-Designs": "Sin medios de terceros · ocho diseños originales de OHC",
})
UI_TRANSLATIONS["fr"].update({
    "Inhalt & Design": "Contenu et design", "Mitgelieferte Animationen": "Animations intégrées",
    "Eigene Datei": "Fichier personnel", "Statisch": "Statique", "Animiert": "Animé",
    "Darstellung": "Présentation", "Hardwaredaten & Ebenen": "Données matérielles et calques",
    "Hardwaredaten": "Données matérielles", "Bild/GIF + Hardwaredaten": "Image/GIF + données matérielles",
    "Uhr zusätzlich einblenden": "Superposer l’horloge", "Erweiterte Animationsoptionen": "Options d’animation avancées",
    "Erweiterte Optionen ausblenden": "Masquer les options avancées", "Design auswählen": "Choisir le design",
    "Animation direkt starten": "Démarrer directement l’animation", "Als Hintergrund verwenden": "Utiliser comme arrière-plan",
    "Keine Fremdmedien · acht originale OHC-Designs": "Aucun média tiers · huit designs OHC originaux",
})

SETUP_TRANSLATIONS: dict[str, dict[str, str]] = {
    "de": {
        "window": "Ersteinrichtung", "welcome": "Willkommen", "welcome_text": "Dieser Assistent richtet Design, Monitoranpassung und ein erstes Kühlprofil ein. Alle Einstellungen lassen sich später ändern.",
        "design": "Design", "appearance": "Darstellung", "light": "Hell (Standard)", "dark": "Dunkel", "system": "Systemmodus", "accent": "Akzentfarbe", "background": "Animierter Hintergrund",
        "display": "Monitor und Skalierung", "auto_scale": "Automatisch an Monitor und Seitenverhältnis anpassen", "app_scale": "App-Skalierung", "layout": "Layout", "layout_auto": "Automatisch", "layout_compact": "Kompakt · 16:10", "layout_standard": "Standard · 16:9", "layout_ultra": "Ultrawide · 21:9", "layout_super": "Super-Ultrawide · 32:9",
        "system_check": "Systemprüfung", "deps_ok": "Abhängigkeiten vollständig.", "deps_missing": "Fehlende Pakete: {packages}. Sie können später in den Einstellungen installiert werden.", "detect_after": "Kraken und RGB-Controller werden nach Abschluss des Assistenten erkannt.",
        "starter": "Startprofil", "cooling_profile": "Kühlprofil", "quiet": "Leise · 45 % / 35 %", "balanced": "Ausgeglichen · 55 % / 50 %", "performance": "Leistung · 75 % / 75 %", "safe": "Sicher · 65 % / 65 %", "profile_note": "Das Profil wird nach erfolgreicher Geräteerkennung angewendet.",
        "finish": "Bereit", "finish_text": "Die App startet standardmäßig im hellen Modus. Alle gewählten Einstellungen lassen sich später jederzeit ändern.", "open_help": "Nach Abschluss Hilfe & erste Schritte öffnen",
        "back": "Zurück", "next": "Weiter", "finish_button": "Fertig", "cancel": "Abbrechen",
    },
    "en": {
        "window": "First setup", "welcome": "Welcome", "welcome_text": "This assistant configures appearance, display scaling and a first cooling profile. Every setting can be changed later.",
        "design": "Design", "appearance": "Appearance", "light": "Light (default)", "dark": "Dark", "system": "System mode", "accent": "Accent colour", "background": "Animated background",
        "display": "Monitor and scaling", "auto_scale": "Automatically adapt to monitor and aspect ratio", "app_scale": "App scaling", "layout": "Layout", "layout_auto": "Automatic", "layout_compact": "Compact · 16:10", "layout_standard": "Standard · 16:9", "layout_ultra": "Ultrawide · 21:9", "layout_super": "Super ultrawide · 32:9",
        "system_check": "System check", "deps_ok": "All dependencies are installed.", "deps_missing": "Missing packages: {packages}. They can be installed later in Settings.", "detect_after": "Kraken and RGB controllers are detected after the assistant is completed.",
        "starter": "Starter profile", "cooling_profile": "Cooling profile", "quiet": "Quiet · 45% / 35%", "balanced": "Balanced · 55% / 50%", "performance": "Performance · 75% / 75%", "safe": "Safe · 65% / 65%", "profile_note": "The profile is applied after successful device detection.",
        "finish": "Ready", "finish_text": "The application starts in light mode by default. Every selected option can be changed later.", "open_help": "Open Help & Getting Started after setup",
        "back": "Back", "next": "Next", "finish_button": "Finish", "cancel": "Cancel",
    },
    "es": {
        "window": "Configuración inicial", "welcome": "Bienvenido", "welcome_text": "Este asistente configura el diseño, la escala de pantalla y un primer perfil de refrigeración. Todo se puede cambiar más tarde.",
        "design": "Diseño", "appearance": "Apariencia", "light": "Claro (predeterminado)", "dark": "Oscuro", "system": "Modo del sistema", "accent": "Color de acento", "background": "Fondo animado",
        "display": "Monitor y escala", "auto_scale": "Adaptar automáticamente al monitor y a la relación de aspecto", "app_scale": "Escala de la aplicación", "layout": "Diseño", "layout_auto": "Automático", "layout_compact": "Compacto · 16:10", "layout_standard": "Estándar · 16:9", "layout_ultra": "Ultrawide · 21:9", "layout_super": "Super ultrawide · 32:9",
        "system_check": "Comprobación del sistema", "deps_ok": "Todas las dependencias están instaladas.", "deps_missing": "Paquetes que faltan: {packages}. Se pueden instalar más tarde en Ajustes.", "detect_after": "Kraken y los controladores RGB se detectarán al finalizar el asistente.",
        "starter": "Perfil inicial", "cooling_profile": "Perfil de refrigeración", "quiet": "Silencioso · 45% / 35%", "balanced": "Equilibrado · 55% / 50%", "performance": "Rendimiento · 75% / 75%", "safe": "Seguro · 65% / 65%", "profile_note": "El perfil se aplica tras detectar correctamente el dispositivo.",
        "finish": "Listo", "finish_text": "La aplicación se inicia en modo claro de forma predeterminada. Todas las opciones se pueden cambiar más tarde.", "open_help": "Abrir Ayuda y primeros pasos al finalizar",
        "back": "Atrás", "next": "Siguiente", "finish_button": "Finalizar", "cancel": "Cancelar",
    },
    "fr": {
        "window": "Configuration initiale", "welcome": "Bienvenue", "welcome_text": "Cet assistant configure l’apparence, la mise à l’échelle de l’écran et un premier profil de refroidissement. Tous les réglages restent modifiables ensuite.",
        "design": "Design", "appearance": "Apparence", "light": "Clair (par défaut)", "dark": "Sombre", "system": "Mode système", "accent": "Couleur d’accent", "background": "Arrière-plan animé",
        "display": "Écran et mise à l’échelle", "auto_scale": "Adapter automatiquement à l’écran et au format", "app_scale": "Échelle de l’application", "layout": "Disposition", "layout_auto": "Automatique", "layout_compact": "Compact · 16:10", "layout_standard": "Standard · 16:9", "layout_ultra": "Ultrawide · 21:9", "layout_super": "Super ultrawide · 32:9",
        "system_check": "Vérification du système", "deps_ok": "Toutes les dépendances sont installées.", "deps_missing": "Paquets manquants : {packages}. Ils pourront être installés plus tard dans Paramètres.", "detect_after": "Kraken et les contrôleurs RGB seront détectés après la fin de l’assistant.",
        "starter": "Profil de départ", "cooling_profile": "Profil de refroidissement", "quiet": "Silencieux · 45% / 35%", "balanced": "Équilibré · 55% / 50%", "performance": "Performance · 75% / 75%", "safe": "Sûr · 65% / 65%", "profile_note": "Le profil est appliqué après la détection réussie du périphérique.",
        "finish": "Prêt", "finish_text": "L’application démarre en mode clair par défaut. Tous les choix peuvent être modifiés plus tard.", "open_help": "Ouvrir l’aide et le guide de démarrage après la configuration",
        "back": "Retour", "next": "Suivant", "finish_button": "Terminer", "cancel": "Annuler",
    },
}


def _help_topic(title: str, intro: str, steps: list[str], page: int | None = None) -> dict[str, object]:
    return {"title": title, "intro": intro, "steps": tuple(steps), "page": page}


HELP_TOPICS: dict[str, dict[str, dict[str, object]]] = {
    "de": {
        "getting_started": _help_topic("Erste Schritte", "Die wichtigsten Bereiche von Open Hardware Control in wenigen Minuten.", ["Öffne links den gewünschten Geräte- oder Systembereich.", "Nutze Profile, wenn du mehrere Einstellungen gemeinsam sichern möchtest.", "Änderungen an Hardware werden erst über die jeweilige Anwenden-/Start-Schaltfläche übertragen.", "Im Log findest du technische Details, falls etwas nicht reagiert."], 0),
        "lcd": _help_topic("LCD ändern", "Bilder, GIFs, Uhr und Hardwaredaten werden im NZXT-LCD-Arbeitsbereich verwaltet.", ["Öffne Geräte → NZXT Kraken → LCD.", "Wähle statischen oder animierten Inhalt und importiere bei Bedarf ein eigenes Bild oder GIF.", "Für Hardwaredaten kannst du CPU, GPU und Kühlmittel sowie animierte Designs verwenden.", "Helligkeit und Ausrichtung befinden sich direkt bei den Display-Einstellungen.", "Bei laufenden GIFs koordiniert OHC kurze USB-Übergaben automatisch."], 3),
        "cooling": _help_topic("Kühlung & Lüfterprofile", "Pumpe und Kraken-Radiatorlüfter lassen sich fest oder temperaturgeführt steuern.", ["Öffne Geräte → NZXT Kraken → Kühlung.", "Für einen schnellen Start kannst du Leise, Ausgeglichen, Leistung oder Sicher verwenden.", "Kurven können CPU-Temperaturen auswerten; die Kühlmitteltemperatur bleibt als Sicherheitsüberwachung aktiv.", "Prüfe vor extrem niedrigen Werten immer Temperaturen und Drehzahlen."], 1),
        "rgb": _help_topic("RGB-Studio", "RGB-Studio bündelt die von OHC verwalteten NZXT- und OpenRGB-Geräte.", ["Erkenne und benenne Geräte zunächst im Einrichtungsbereich.", "Teste LED-Zonen einzeln und speichere die erkannte LED-Anzahl.", "Wähle Geräte oder Gruppen aus und starte anschließend ein OHC-Design.", "Wenn ein anderes OpenRGB-Fenster die Hardware besitzt, wartet OHC auf eine sichere Freigabe."], 2),
        "profiles": _help_topic("Profile sichern, importieren & wiederherstellen", "Profile speichern zusammengehörige Kühlungs-, LCD-, RGB- und Designwerte.", ["Öffne System → Profile.", "Erstelle für wichtige Zustände eigene Profile und dupliziere sie vor größeren Änderungen.", "Importierte LCD-Profile zeigen vor der Aktivierung eine Vorschau sowie nicht unterstützte Elemente.", "Nutze Export oder Backup, bevor du umfangreiche Profile bearbeitest."], 5),
        "openlinkhub": _help_topic("Corsair & OpenLinkHub", "Corsair-Geräte werden über eine lokal laufende OpenLinkHub-Instanz eingebunden.", ["Öffne Geräte → Corsair · OpenLinkHub.", "Prüfe zuerst Dienstkontext, API-Status und erkannte Geräte.", "OHC verändert keinen fremden Systemdienst automatisch.", "Gerätewerte sollten bei Unsicherheit mit der OpenLinkHub-Geräteseite abgeglichen werden."], 8),
        "settings": _help_topic("Einstellungen, Sprache & Autostart", "Hier stellst du Oberfläche, Sprache, Anzeige, Abhängigkeiten und Startverhalten ein.", ["Öffne System → Einstellungen.", "Die Sprache kann jederzeit zwischen Deutsch, Englisch, Spanisch und Französisch gewechselt werden.", "Beim Systemstart kann OHC vollständig minimiert im Tray bleiben.", "Nicht erkannte Geräte/Module lassen sich für Diagnosezwecke einblenden."], 4),
        "troubleshooting": _help_topic("Fehlerbehebung & Log", "Bei Hardwareproblemen liefert das Log die wichtigste gemeinsame Diagnosebasis.", ["Öffne Diagnose → Log und reproduziere den Fehler einmal.", "Mit Alles kopieren kannst du die Sitzung für einen Fehlerbericht übernehmen.", "Prüfe bei USB-Problemen die Geräteberechtigungen in Einstellungen.", "Bei RGB-Problemen zuerst die OHC-Geräteerkennung neu ausführen, bevor andere RGB-Programme parallel gestartet werden."], 7),
        "desktop": _help_topic("Desktop-Designs", "Die experimentellen Desktop-Designs ändern ausgewählte KDE-Oberflächenbausteine mit Sicherungs- und Rückweg.", ["Aktiviere den experimentellen Bereich in den Einstellungen.", "Prüfe vor dem Anwenden die geplanten Änderungen.", "OHC legt vor Änderungen eine Sicherung an und bietet eine Wiederherstellung an."], 9),
    },
    "en": {
        "getting_started": _help_topic("Getting started", "The main Open Hardware Control areas in a few minutes.", ["Choose the required device or system area on the left.", "Use profiles when several settings should be saved together.", "Hardware changes are only transmitted by the corresponding Apply/Start action.", "Open Log for technical details when something does not respond."], 0),
        "lcd": _help_topic("Change the LCD", "Images, GIFs, clock and hardware data are managed in the NZXT LCD workspace.", ["Open Devices → NZXT Kraken → LCD.", "Choose static or animated content and import your own image or GIF when needed.", "Hardware data can show CPU, GPU and liquid values with animated designs.", "Brightness and orientation are located in Display settings.", "During GIF playback OHC coordinates short USB handovers automatically."], 3),
        "cooling": _help_topic("Cooling & fan profiles", "Pump and Kraken radiator fans can use fixed duty or temperature control.", ["Open Devices → NZXT Kraken → Cooling.", "Use Quiet, Balanced, Performance or Safe for a quick starting point.", "Software curves can use CPU temperature while liquid temperature remains a safety monitor.", "Always watch temperatures and RPM before using very low duty values."], 1),
        "rgb": _help_topic("RGB Studio", "RGB Studio combines NZXT and OpenRGB devices managed by OHC.", ["Detect and name devices in the setup section first.", "Test LED zones individually and save the detected LED count.", "Select devices or groups, then start an OHC design.", "If another OpenRGB window owns the hardware, OHC waits for a safe handover."], 2),
        "profiles": _help_topic("Profiles, import & backup", "Profiles save related cooling, LCD, RGB and appearance settings.", ["Open System → Profiles.", "Create your own profiles for important states and duplicate them before large changes.", "Imported LCD profiles show a preview and unsupported elements before activation.", "Use Export or Backup before editing complex profiles."], 5),
        "openlinkhub": _help_topic("Corsair & OpenLinkHub", "Corsair devices are integrated through a local OpenLinkHub instance.", ["Open Devices → Corsair · OpenLinkHub.", "Check service context, API status and detected devices first.", "OHC never changes a foreign system service automatically.", "When in doubt compare values with the OpenLinkHub device page."], 8),
        "settings": _help_topic("Settings, language & autostart", "Configure appearance, language, display, dependencies and startup behaviour here.", ["Open System → Settings.", "The interface can switch between German, English, Spanish and French at any time.", "At desktop startup OHC can remain fully minimized in the tray.", "Undetected devices/modules can be shown for diagnostics."], 4),
        "troubleshooting": _help_topic("Troubleshooting & Log", "For hardware problems the log is the most useful shared diagnostic source.", ["Open Diagnostics → Log and reproduce the problem once.", "Use Copy all to include the session in a bug report.", "For USB problems check device permissions in Settings.", "For RGB problems refresh OHC device detection before running other RGB applications in parallel."], 7),
        "desktop": _help_topic("Desktop designs", "Experimental desktop designs modify selected KDE appearance parts with backup and rollback.", ["Enable the experimental area in Settings.", "Review the planned changes before applying them.", "OHC creates a backup before modifications and offers restoration."], 9),
    },
    "es": {
        "getting_started": _help_topic("Primeros pasos", "Los principales apartados de Open Hardware Control en pocos minutos.", ["Elige a la izquierda el dispositivo o apartado del sistema.", "Usa perfiles para guardar varias opciones juntas.", "Los cambios de hardware solo se transmiten con la acción Aplicar/Iniciar correspondiente.", "Abre el registro si algo no responde."], 0),
        "lcd": _help_topic("Cambiar el LCD", "Imágenes, GIF, reloj y datos de hardware se gestionan en el espacio LCD de NZXT.", ["Abre Dispositivos → NZXT Kraken → LCD.", "Elige contenido estático o animado e importa una imagen o GIF propio si lo deseas.", "Los datos de hardware pueden mostrar CPU, GPU y líquido con diseños animados.", "Brillo y orientación están en los ajustes de pantalla.", "Durante un GIF OHC coordina automáticamente las breves cesiones USB."], 3),
        "cooling": _help_topic("Refrigeración y perfiles", "La bomba y los ventiladores del radiador Kraken pueden usar valores fijos o control por temperatura.", ["Abre Dispositivos → NZXT Kraken → Refrigeración.", "Usa Silencioso, Equilibrado, Rendimiento o Seguro como punto de partida.", "Las curvas pueden usar la temperatura de CPU mientras el líquido sigue como protección.", "Vigila temperaturas y RPM antes de usar valores muy bajos."], 1),
        "rgb": _help_topic("RGB Studio", "RGB Studio agrupa dispositivos NZXT y OpenRGB gestionados por OHC.", ["Detecta y nombra primero los dispositivos.", "Prueba las zonas LED y guarda su cantidad.", "Selecciona dispositivos o grupos y después inicia un diseño OHC.", "Si otra ventana de OpenRGB controla el hardware, OHC espera una cesión segura."], 2),
        "profiles": _help_topic("Perfiles, importación y copias", "Los perfiles guardan ajustes relacionados de refrigeración, LCD, RGB y diseño.", ["Abre Sistema → Perfiles.", "Crea perfiles propios y duplícalos antes de cambios grandes.", "Los perfiles LCD importados muestran vista previa y elementos no compatibles antes de activarse.", "Usa Exportar o Copia de seguridad antes de editar perfiles complejos."], 5),
        "openlinkhub": _help_topic("Corsair y OpenLinkHub", "Los dispositivos Corsair se integran mediante una instancia local de OpenLinkHub.", ["Abre Dispositivos → Corsair · OpenLinkHub.", "Comprueba contexto del servicio, API y dispositivos detectados.", "OHC nunca modifica automáticamente un servicio de sistema ajeno.", "Si hay dudas compara los valores con la página del dispositivo en OpenLinkHub."], 8),
        "settings": _help_topic("Ajustes, idioma y autoarranque", "Aquí se configuran apariencia, idioma, pantalla, dependencias y arranque.", ["Abre Sistema → Ajustes.", "Puedes cambiar entre alemán, inglés, español y francés en cualquier momento.", "Al iniciar el escritorio OHC puede permanecer totalmente minimizado en la bandeja.", "Los módulos no detectados se pueden mostrar para diagnóstico."], 4),
        "troubleshooting": _help_topic("Solución de problemas y registro", "El registro es la fuente de diagnóstico más útil para problemas de hardware.", ["Abre Diagnóstico → Registro y reproduce el fallo una vez.", "Usa Copiar todo para adjuntar la sesión a un informe.", "Para problemas USB revisa los permisos en Ajustes.", "Para RGB actualiza primero la detección de OHC antes de ejecutar otras aplicaciones RGB."], 7),
        "desktop": _help_topic("Diseños de escritorio", "Los diseños experimentales modifican partes seleccionadas de KDE con copia y restauración.", ["Activa el área experimental en Ajustes.", "Revisa los cambios antes de aplicarlos.", "OHC crea una copia antes de modificar y ofrece restauración."], 9),
    },
    "fr": {
        "getting_started": _help_topic("Premiers pas", "Les principaux espaces d’Open Hardware Control en quelques minutes.", ["Choisissez à gauche l’appareil ou l’espace système voulu.", "Utilisez les profils pour enregistrer plusieurs réglages ensemble.", "Les changements matériels ne sont transmis qu’avec l’action Appliquer/Démarrer correspondante.", "Ouvrez le journal si quelque chose ne répond pas."], 0),
        "lcd": _help_topic("Modifier le LCD", "Images, GIF, horloge et données matérielles sont gérés dans l’espace LCD NZXT.", ["Ouvrez Appareils → NZXT Kraken → LCD.", "Choisissez un contenu fixe ou animé et importez votre image ou GIF si nécessaire.", "Les données matérielles peuvent afficher CPU, GPU et liquide avec des designs animés.", "Luminosité et orientation se trouvent dans les réglages d’affichage.", "Pendant un GIF, OHC coordonne automatiquement les courtes prises USB."], 3),
        "cooling": _help_topic("Refroidissement et profils", "La pompe et les ventilateurs du radiateur Kraken peuvent être fixes ou pilotés par température.", ["Ouvrez Appareils → NZXT Kraken → Refroidissement.", "Utilisez Silencieux, Équilibré, Performance ou Sûr comme point de départ.", "Les courbes peuvent utiliser la température CPU tandis que le liquide reste surveillé pour la sécurité.", "Surveillez températures et RPM avant des valeurs très faibles."], 1),
        "rgb": _help_topic("RGB Studio", "RGB Studio regroupe les appareils NZXT et OpenRGB gérés par OHC.", ["Détectez et nommez d’abord les appareils.", "Testez les zones LED et enregistrez leur nombre.", "Sélectionnez des appareils ou groupes puis démarrez un design OHC.", "Si une autre fenêtre OpenRGB possède le matériel, OHC attend une remise sûre."], 2),
        "profiles": _help_topic("Profils, import et sauvegarde", "Les profils enregistrent ensemble refroidissement, LCD, RGB et apparence.", ["Ouvrez Système → Profils.", "Créez vos profils et dupliquez-les avant de grands changements.", "Les profils LCD importés affichent un aperçu et les éléments non pris en charge avant activation.", "Utilisez Exporter ou Sauvegarde avant de modifier des profils complexes."], 5),
        "openlinkhub": _help_topic("Corsair et OpenLinkHub", "Les appareils Corsair sont intégrés via une instance locale OpenLinkHub.", ["Ouvrez Appareils → Corsair · OpenLinkHub.", "Vérifiez d’abord le contexte du service, l’API et les appareils détectés.", "OHC ne modifie jamais automatiquement un service système tiers.", "En cas de doute comparez les valeurs avec la page d’appareil OpenLinkHub."], 8),
        "settings": _help_topic("Paramètres, langue et démarrage", "Configurez ici apparence, langue, écran, dépendances et comportement au démarrage.", ["Ouvrez Système → Paramètres.", "L’interface peut passer à tout moment entre allemand, anglais, espagnol et français.", "Au démarrage du bureau OHC peut rester entièrement minimisé dans la zone de notification.", "Les appareils/modules non détectés peuvent être affichés pour le diagnostic."], 4),
        "troubleshooting": _help_topic("Dépannage et journal", "Le journal est la meilleure base de diagnostic commune pour les problèmes matériels.", ["Ouvrez Diagnostic → Journal et reproduisez le problème une fois.", "Utilisez Tout copier pour joindre la session à un rapport.", "Pour les problèmes USB vérifiez les permissions dans Paramètres.", "Pour RGB actualisez d’abord la détection OHC avant de lancer d’autres applications RGB."], 7),
        "desktop": _help_topic("Designs du bureau", "Les designs expérimentaux modifient certains éléments KDE avec sauvegarde et retour arrière.", ["Activez l’espace expérimental dans Paramètres.", "Vérifiez les changements prévus avant application.", "OHC crée une sauvegarde avant modification et propose une restauration."], 9),
    },
}
