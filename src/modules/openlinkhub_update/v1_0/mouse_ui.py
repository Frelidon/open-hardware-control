# SPDX-License-Identifier: GPL-3.0-or-later
"""Home-marked startup DPI and named profiles from reported capabilities."""
from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QButtonGroup, QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QStyle
from modules.navigation_settings.v1_0.artwork import category_icon


def add_mouse_profile_controls(host,form):
    tr=host.tr_static
    box=QGroupBox(tr("Start-DPI und Profile"));layout=QFormLayout(box)
    host.openlinkhub_mouse_home_combo=QComboBox()
    host.openlinkhub_mouse_home_combo.setProperty("i18nTranslateItems",False)
    host.openlinkhub_mouse_home_combo.setObjectName("mouseStartupDpi")
    layout.addRow(tr("Standard-DPI-Stufe"),host.openlinkhub_mouse_home_combo)
    home=QPushButton(tr("Als Start-DPI speichern"));home.setIcon(category_icon("home",home.palette(),24))
    home.setProperty("requiresUserService", True)
    home.clicked.connect(lambda: apply_startup(host));layout.addRow(home)
    note=QLabel(tr("Der Standard bleibt unabhängig von der aktiven DPI-Stufe erhalten. Zum Speichern wird der OpenLinkHub-Benutzerdienst kurz neu gestartet."))
    note.setWordWrap(True);layout.addRow(note)
    host.openlinkhub_mouse_profile_combo=QComboBox();host.openlinkhub_mouse_profile_combo.setProperty("i18nTranslateItems",False)
    layout.addRow(tr("Profil"),host.openlinkhub_mouse_profile_combo)
    select=QPushButton(tr("Profil aktivieren"));select.clicked.connect(lambda: profile_action(host,False));layout.addRow(select)
    host.openlinkhub_mouse_profile_name=QLineEdit();host.openlinkhub_mouse_profile_name.setMaxLength(48)
    host.openlinkhub_mouse_profile_name.setPlaceholderText(tr("Neuer Profilname"))
    layout.addRow(host.openlinkhub_mouse_profile_name)
    save=QPushButton(tr("Als neues Profil speichern"));save.clicked.connect(lambda: profile_action(host,True));layout.addRow(save)
    host.openlinkhub_write_buttons.extend((home,select,save))
    host.openlinkhub_mouse_home_button=home
    host.openlinkhub_mouse_home_combo.activated.connect(lambda _i:setattr(host,"_mouse_home_dirty",True))
    return box
    for field in host.openlinkhub_mouse_dpi:
        field.valueChanged.connect(lambda _v: setattr(host,"_mouse_dpi_dirty",True))


def refresh_mouse_controls(host,device):
    if not hasattr(host,"openlinkhub_mouse_home_combo"):return
    metadata=device.get("mouse_profile",{}) if isinstance(device,dict) else {}
    stages=metadata.get("stages",[])
    combo=host.openlinkhub_mouse_home_combo
    identity=device.get("control_id","") if device else ""
    identity=(identity,metadata.get("active_profile"))
    changed=identity!=getattr(host,"_mouse_dpi_control",None)
    if changed:host._mouse_dpi_dirty=False;host._mouse_home_dirty=False
    host._mouse_dpi_control=identity
    with QSignalBlocker(combo):
        old=combo.currentData();combo.clear()
        combo.addItem(host.tr_static("OpenLinkHub-Vorgabe beibehalten"),-1)
        for stage in stages:
            combo.addItem(category_icon("home",combo.palette(),20),
                          f'{int(stage["id"])+1} · {stage["dpi"]} DPI',int(stage["id"]))
        preferred=metadata.get("preferred")
        selected=old if getattr(host,"_mouse_home_dirty",False) else preferred if preferred is not None else -1
        combo.setCurrentIndex(max(0,combo.findData(selected)))
    host.openlinkhub_mouse_home_button.setProperty("capabilityAvailable",bool(stages))
    host.openlinkhub_mouse_dpi_button.setProperty("capabilityAvailable",bool(stages))
    layout=host.openlinkhub_mouse_dpi_row_layout
    while len(host.openlinkhub_mouse_dpi)<len(stages):
        field=QSpinBox();field.setSuffix(" DPI");layout.addWidget(field)
        field.valueChanged.connect(lambda _v:setattr(host,"_mouse_dpi_dirty",True))
        host.openlinkhub_mouse_dpi.append(field)
    minimum=metadata.get("minimum",100);maximum=metadata.get("maximum",30000)
    if type(minimum) is not int or type(maximum) is not int or not 50<=minimum<=maximum<=100000:
        minimum,maximum=100,30000
    for index,field in enumerate(host.openlinkhub_mouse_dpi):
        field.setVisible(index<len(stages))
        if index<len(stages):
            with QSignalBlocker(field):
                field.setRange(minimum,maximum);field.stage_id=stages[index]["id"]
                if not getattr(host,"_mouse_dpi_dirty",False):field.setValue(stages[index]["dpi"])
    profiles=host.openlinkhub_mouse_profile_combo
    with QSignalBlocker(profiles):
        old=metadata.get("active_profile") if changed else profiles.currentText()
        profiles.clear();profiles.addItems(metadata.get("profiles",[]))
        profiles.setCurrentIndex(max(0,profiles.findText(old or "")))


def apply_startup(host):
    selected=host._openlinkhub_device_payload(host.openlinkhub_mouse_device_combo)
    stage=host.openlinkhub_mouse_home_combo.currentData()
    if selected is None or type(stage) is not int:return
    _,payload=selected;payload["stage"]=stage
    host._mouse_home_dirty=False
    host.run_openlinkhub_write("mouse-default-dpi",payload,host.tr_static("Als Start-DPI speichern"))


def profile_action(host,create):
    selected=host._openlinkhub_device_payload(host.openlinkhub_mouse_device_combo)
    if selected is None:return
    _,payload=selected
    name=host.openlinkhub_mouse_profile_name.text().strip() if create else host.openlinkhub_mouse_profile_combo.currentText()
    if not name:return
    payload["profile"]=name
    host.run_openlinkhub_write("mouse-profile-save" if create else "mouse-profile-change",payload,
                              host.tr_static("Als neues Profil speichern" if create else "Profil aktivieren"))


def refresh_mouse_icons(host):
    """Regenerate original house artwork after light/dark or accent changes."""
    button=getattr(host,"openlinkhub_mouse_home_button",None)
    combo=getattr(host,"openlinkhub_mouse_home_combo",None)
    if button is not None:button.setIcon(category_icon("home",host.palette(),24))
    if combo is not None:
        icon=category_icon("home",host.palette(),20)
        for index in range(combo.count()):combo.setItemIcon(index,icon)


def refresh_mouse_language(host):
    combo=getattr(host,"openlinkhub_mouse_home_combo",None)
    if combo is not None:
        index=combo.findData(-1)
        if index>=0:combo.setItemText(index,host.tr_static("OpenLinkHub-Vorgabe beibehalten"))
