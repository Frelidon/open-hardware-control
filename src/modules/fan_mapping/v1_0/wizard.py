# SPDX-License-Identifier: GPL-3.0-or-later
"""Compose the existing chassis-only mapping workflow with explicit skip paths."""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWizard, QWizardPage
from modules.pc_case_profiles.v1_5.diagram import CoolingLayoutDiagram
from modules.pc_case_profiles.v1_5.case_page import cooling_slots
from modules.pc_case_profiles.v1_5.channel_labels import channel_caption, channel_details
from modules.pc_case_profiles.v1_5.view_state import resize_cooling_slot
from modules.ui_performance.v1_1.dynamic_text import capture_form, refresh
from .runtime import mark_disconnected, wizard_page_changed, wizard_finished
from .lighting import begin



class MappingWizard(QWizard):
    def __init__(self, host, count):
        super().__init__(host); self.host = host; self.channel_count = count

    def refresh_language(self):
        tr = self.host.tr_static
        self.setWindowTitle(tr("Lüfter-Zuordnung & Test-Assistent"))
        for page_id in self.pageIds():
            page = self.page(page_id)
            for attribute, getter, setter in (("ohcTitle", page.title, page.setTitle), ("ohcSubtitle", page.subTitle, page.setSubTitle)):
                source = page.property(attribute)
                if source is None:
                    source = getter(); page.setProperty(attribute, source)
                setter(tr(source))
        refresh(self.host)
        for button, caption in ((QWizard.WizardButton.NextButton, "Weiter"), (QWizard.WizardButton.BackButton, "Zurück"),
                                (QWizard.WizardButton.CancelButton, "Abbrechen"), (QWizard.WizardButton.FinishButton, "Fertig")):
            self.setButtonText(button, tr(caption))
        from .lighting import status
        if hasattr(self.host, "fan_assistant_lighting_status_source"):
            status(self.host, self.host.fan_assistant_lighting_status_source)
        self.host.assistant_select_channel(str(self.host.assistant_channel_combo.currentData() or ""))
        slot_id = getattr(self.host, "cooling_layout_selected_slot_id", "")
        if slot_id: self.host.select_cooling_layout_slot(slot_id)
        self.detected_caption.setText(tr("Erkannte Gehäusekanäle: {count}. CPU_FAN und PUMP_FAN bleiben im separaten Kühlungsbereich.").format(count=self.channel_count))


def build(host, channels):
    wizard = MappingWizard(host, len(channels))
    wizard.setObjectName("fanMappingWizard")
    wizard.setWizardStyle(QWizard.WizardStyle.ModernStyle)
    wizard.setWindowTitle("Lüfter-Zuordnung & Test-Assistent")
    wizard.setMinimumSize(1040, 760)
    wizard.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)

    detect = QWizardPage()
    detect.setTitle("1 · Erkennen")
    detect.setSubTitle("System-Fan-Header erfassen und den sicheren Test vorbereiten.")
    detect_layout = QVBoxLayout(detect)
    status = QFrame(); status.setObjectName("dashboardStatusBanner")
    sl = QHBoxLayout(status)
    sl.addWidget(QLabel("✓", objectName="dashboardStatusIcon"))
    wizard.detected_caption = QLabel(); wizard.detected_caption.setWordWrap(True)
    sl.addWidget(wizard.detected_caption, 1)
    detect_layout.addWidget(status)
    explain = QLabel(
        "Der Assistent identifiziert ausschließlich Gehäuselüfter. Für einen deutlichen, aber sicheren Kontrast "
        "werden andere steuerbare Gehäusekanäle temporär auf 30 % gesetzt und der Zielkanal auf 80 %. "
        "Alle vorherigen Zustände werden danach wiederhergestellt."
    )
    explain.setWordWrap(True); explain.setObjectName("muted")
    detect_layout.addWidget(explain)
    detected_list = QFrame(); detected_list.setObjectName("dashboardSection")
    dl = QVBoxLayout(detected_list)
    dl.addWidget(QLabel("Erkannte System-Fan-Kanäle", objectName="sectionTitle"))
    for channel in channels:
        profile = host.mainboard_profile_for(channel)
        rpm = channel.rpm if channel.rpm is not None else "—"
        row = QLabel(f"●  {channel_caption(host, channel)}  ·  {rpm} RPM")
        row.setToolTip(channel_details(channel))
        row.setObjectName("infoText")
        dl.addWidget(row)
    detect_layout.addWidget(detected_list)
    detect_layout.addStretch()

    test_page = QWizardPage()
    test_page.setTitle("2 · Testen")
    test_page.setSubTitle("Einen Anschluss prüfen oder ausdrücklich als nicht angeschlossen markieren.")
    test_layout = QVBoxLayout(test_page)
    info = QFrame(); info.setObjectName("dashboardSection")
    il = QHBoxLayout(info)
    info_text = QLabel("ⓘ  OHC pausiert die RGB-Animation und setzt zugeordnete Lüfter automatisch auf Weiß mit voller Helligkeit.")
    info_text.setWordWrap(True); il.addWidget(info_text, 1)
    test_layout.addWidget(info)
    choose = QFrame(); choose.setObjectName("coolingSummaryCard")
    cl = QVBoxLayout(choose)
    cl.addWidget(QLabel("Aktuell getesteter Kanal", objectName="sectionTitle"))
    host.assistant_channel_combo = QComboBox()
    for channel in channels:
        profile = host.mainboard_profile_for(channel)
        host.assistant_channel_combo.addItem(channel_caption(host, channel), channel.stable_id)
        host.assistant_channel_combo.setItemData(host.assistant_channel_combo.count() - 1, channel_details(channel), Qt.ItemDataRole.ToolTipRole)
    host.assistant_channel_combo.currentIndexChanged.connect(
        lambda _index: host.assistant_select_channel(str(host.assistant_channel_combo.currentData() or ""))
    )
    cl.addWidget(host.assistant_channel_combo)
    host.assistant_channel_status = QLabel("Aktueller Testkanal: wird gewählt")
    host.assistant_channel_status.setObjectName("coolingMetrics")
    cl.addWidget(host.assistant_channel_status)
    host.assistant_rgb_status = QLabel("RGB-Testhilfe noch nicht verwendet")
    host.assistant_rgb_status.setObjectName("muted")
    cl.addWidget(host.assistant_rgb_status)
    test = QPushButton("80 % / 10 s testen · andere Gehäuselüfter 30 %")
    test.setObjectName("primaryAction")
    test.setMinimumHeight(48)
    test.clicked.connect(host.assistant_test_selected_channel)
    cl.addWidget(test)
    stop_test = QPushButton("0 % / 2 min Stopp-Test · andere Gehäuselüfter 45 %")
    stop_test.setMinimumHeight(42)
    stop_test.clicked.connect(host.assistant_stop_selected_channel)
    cl.addWidget(stop_test)
    skip = QPushButton(host.tr_static("Nicht angeschlossen · überspringen"))
    skip.clicked.connect(lambda: mark_disconnected(host))
    cl.addWidget(skip)
    repeat = QPushButton("Test wiederholen")
    repeat.clicked.connect(host.assistant_test_selected_channel)
    cl.addWidget(repeat)
    test_layout.addWidget(choose)
    test_layout.addStretch()

    mapping = QWizardPage()
    mapping.setTitle("3 · Zuordnen")
    mapping.setSubTitle("Den getesteten Header einem physischen Einbauplatz im Gehäuse zuordnen.")
    mapping_layout = QHBoxLayout(mapping)
    diagram_box = QFrame(); diagram_box.setObjectName("dashboardSection")
    dbl = QVBoxLayout(diagram_box)
    dbl.addWidget(QLabel("Gehäuseansicht", objectName="sectionTitle"))
    host.assistant_layout_diagram = CoolingLayoutDiagram()
    host.assistant_layout_diagram.slot_resized.connect(lambda slot_id, scale: resize_cooling_slot(host, slot_id, scale))
    host.assistant_layout_diagram.set_slots(cooling_slots(host))
    host.assistant_layout_diagram.set_channel_assignments(host.mainboard_layout_assignments)
    host.assistant_layout_diagram.slot_focused.connect(host.select_cooling_layout_slot)
    dbl.addWidget(host.assistant_layout_diagram, 1)
    mapping_layout.addWidget(diagram_box, 2)
    side = QFrame(); side.setObjectName("coolingSummaryCard")
    side_layout = QVBoxLayout(side)
    side_layout.addWidget(QLabel("Position bestätigen", objectName="sectionTitle"))
    host.assistant_slot_label = QLabel("Ausgewählter Einbauplatz: noch keiner")
    host.assistant_slot_label.setWordWrap(True); host.assistant_slot_label.setObjectName("muted")
    side_layout.addWidget(host.assistant_slot_label)
    assign = QPushButton("✓  Dieser Lüfter ist es")
    assign.setObjectName("primaryAction")
    assign.setMinimumHeight(50)
    assign.clicked.connect(host.assign_selected_channel_to_cooling_slot)
    side_layout.addWidget(assign)
    next_fan = QPushButton("Nächsten Lüfter wählen ›")
    next_fan.clicked.connect(host.assistant_continue_with_next_fan)
    side_layout.addWidget(next_fan)
    side_layout.addStretch()
    mapping_layout.addWidget(side, 1)

    save = QWizardPage()
    save.setTitle("4 · Speichern")
    save.setSubTitle("Zuordnungen übernehmen und die Kanäle anschließend mit Profilen regeln.")
    save_layout = QVBoxLayout(save)
    save_layout.addWidget(QLabel("Aktuelle Zuordnung", objectName="sectionTitle"))
    summary = QFrame(); summary.setObjectName("dashboardSection")
    summary_layout = QVBoxLayout(summary)
    host.assistant_summary_layout = summary_layout
    host.refresh_chassis_assistant_summary()
    save_layout.addWidget(summary)
    save_text = QLabel(
        "Nach dem Speichern kann jeder bestätigte Kanal direkt in der Kühlungszentrale Leise, Ausbalanciert, "
        "Leistung oder eine eigene Kurve verwenden. Automatik bleibt bis zur ausdrücklichen Aktivierung aus."
    )
    save_text.setWordWrap(True); save_text.setObjectName("muted")
    save_layout.addWidget(save_text)
    save_button = QPushButton("Zu Profil übernehmen")
    save_button.setObjectName("primaryAction")
    save_button.setMinimumHeight(50)
    save_button.clicked.connect(host.save_mainboard_fan_settings)
    save_layout.addWidget(save_button)
    another_fan = QPushButton(host.tr_static("Nächsten Lüfter zuordnen"))
    another_fan.clicked.connect(host.assistant_continue_with_next_fan)
    save_layout.addWidget(another_fan)
    save_layout.addStretch()

    wizard.addPage(detect)
    wizard.addPage(test_page)
    wizard.addPage(mapping)
    wizard.addPage(save)
    wizard.currentIdChanged.connect(lambda page_id: wizard_page_changed(host, page_id))
    wizard.finished.connect(lambda _result: wizard_finished(host))
    host.assistant_select_channel(str(host.assistant_channel_combo.currentData() or ""))
    host.chassis_fan_wizard = wizard
    capture_form(host, wizard)
    for dynamic in (host.assistant_channel_status, host.assistant_rgb_status, host.assistant_slot_label):
        host.dynamic_ui_texts.pop(dynamic, None)
    wizard.refresh_language()
    wizard.show()
    QTimer.singleShot(0, lambda: begin(host) if wizard.isVisible() else None)
    host.log_message("MAINBOARD-FAN-ASSISTENT: 3.4.25-Assistent gestartet · Erkennen → Testen → Zuordnen → Speichern")

