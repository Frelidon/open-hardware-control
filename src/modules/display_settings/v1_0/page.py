"""Small Qt builder for OHC display and Levita-FPS settings."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from modules.window_placement.v1_5 import (
    WINDOW_START_LAST, WINDOW_START_MAXIMIZED, WINDOW_START_WINDOWED,
)


def build_display_settings(host: Any, layout: QVBoxLayout) -> None:
    """Attach the display-related controls expected by the main orchestrator."""
    display_box = QGroupBox("Programmfenster, Bildschirm und DPI")
    form = QFormLayout(display_box)
    host.display_info_label = QLabel("Monitor wird erkannt …")
    host.display_info_label.setWordWrap(True)
    host.display_auto_checkbox = QCheckBox("Automatisch an Monitor und Seitenverhältnis anpassen")
    host.display_auto_checkbox.setChecked(host.display_auto)
    host.ui_scale_spin = QSpinBox()
    host.ui_scale_spin.setRange(75, 160)
    host.ui_scale_spin.setValue(host.ui_scale_percent)
    host.ui_scale_spin.setSuffix(" %")
    host.windowed_size_spin = QSpinBox()
    host.windowed_size_spin.setRange(60, 95)
    host.windowed_size_spin.setValue(host.windowed_size_percent)
    host.windowed_size_spin.setSuffix(" %")
    host.windowed_size_spin.setToolTip(
        "Legt die Standardgröße des frei schwebenden Fensters fest. Maximiert nutzt OHC weiterhin die ganze Arbeitsfläche."
    )
    host.display_layout_combo = QComboBox()
    for label, value in (("Automatisch", "auto"), ("Kompakt · 16:10", "16:10"),
                         ("Standard · 16:9", "16:9"), ("Ultrawide · 21:9", "21:9"),
                         ("Super-Ultrawide · 32:9", "32:9")):
        host.display_layout_combo.addItem(label, value)
    host.display_layout_combo.setCurrentIndex(max(0, host.display_layout_combo.findData(host.display_layout)))
    host.window_screen_combo = QComboBox()
    host.window_screen_combo.setAccessibleName("Startbildschirm des Programmfensters")
    host.window_screen_combo.setProperty("i18nTranslateItems", False)
    host.populate_window_screen_combo()
    host.window_start_mode_combo = QComboBox()
    for label, value in (("Letzten Zustand verwenden", WINDOW_START_LAST),
                         ("Immer maximiert", WINDOW_START_MAXIMIZED),
                         ("Immer als Fenster", WINDOW_START_WINDOWED)):
        host.window_start_mode_combo.addItem(label, value)
    host.window_start_mode_combo.setCurrentIndex(
        max(0, host.window_start_mode_combo.findData(host.window_start_mode))
    )
    buttons = QWidget()
    button_layout = QHBoxLayout(buttons)
    button_layout.setContentsMargins(0, 0, 0, 0)
    detect = QPushButton("Monitor neu erkennen")
    detect.clicked.connect(host.refresh_screen_inventory)
    apply_button = QPushButton("Anzeige anwenden")
    apply_button.clicked.connect(host.apply_display_settings)
    button_layout.addWidget(detect)
    button_layout.addWidget(apply_button)
    note = QLabel(
        "Standardmäßig öffnet OHC auf dem von KDE/Qt gemeldeten Hauptbildschirm. Eine feste Auswahl wird "
        "über den Bildschirmnamen gespeichert und fällt bei einem abgesteckten Monitor sicher auf den "
        "Hauptbildschirm zurück. Unter Wayland besitzt KWin die endgültige Entscheidung über die Position. "
        "Die App ändert weder die Linux-Bildschirmauflösung noch die KDE-Monitorkonfiguration."
    )
    note.setWordWrap(True)
    note.setObjectName("muted")
    for label, widget in ((None, host.display_info_label), (None, host.display_auto_checkbox),
                          ("Programmfenster starten auf", host.window_screen_combo),
                          ("Fensterzustand beim Start", host.window_start_mode_combo),
                          ("App-Skalierung", host.ui_scale_spin),
                          ("Fenstergröße im Fenstermodus", host.windowed_size_spin),
                          ("Layoutvorgabe", host.display_layout_combo), (None, buttons), (None, note)):
        form.addRow(widget) if label is None else form.addRow(label, widget)
    layout.addWidget(display_box)

    fps_box = QGroupBox("Thermalright Levita · experimentelle Bildrate")
    fps_layout = QVBoxLayout(fps_box)
    host.levita_experimental_60_checkbox = QCheckBox("60 LCD-FPS experimentell freischalten")
    host.levita_experimental_60_checkbox.setChecked(
        host.settings.value("thermalright/experimental_60_fps", False, type=bool)
    )
    warning = QLabel(
        "60 FPS sind für die Levita 1600 × 720 nicht vom Backend oder Hersteller zugesichert. "
        "Die höhere USB- und Renderlast kann zu Aussetzern, Instabilität oder im ungünstigen Fall zu "
        "Hardwareproblemen führen. Nutzung nur nach bewusster Freigabe auf eigenes technisches Risiko; "
        "OHC stuft bei einem erkannten Taktgeberfehler automatisch zurück. Gesetzliche Rechte bleiben unberührt."
    )
    warning.setWordWrap(True)
    warning.setObjectName("warningText")
    fps_layout.addWidget(host.levita_experimental_60_checkbox)
    fps_layout.addWidget(warning)
    layout.addWidget(fps_box)
