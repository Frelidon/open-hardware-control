# SPDX-License-Identifier: GPL-3.0-or-later
"""In-page actual owned worker status; diagnostics never claim hardware health."""
import time
import os
from pathlib import Path
from PySide6.QtCore import QProcess, QTimer
from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout
from modules.application_shutdown.v1_1 import latest_shutdown_report
from privacy_logging import application_state_directory
from .resource_metrics import ResourceMetrics


def build(host, layout):
    box = QGroupBox('Systemstatus')
    row = QVBoxLayout(box)
    label = QLabel()
    label.setWordWrap(True)
    row.addWidget(label)
    note = QLabel('Prozessstatus ist keine Hardwarebestätigung. Beenden stoppt OHC; Schließen kann im Infobereich weiterlaufen.')
    note.setWordWrap(True)
    row.addWidget(note)
    retry = QPushButton('Sensorprozess neu starten')
    retry.clicked.connect(lambda: host.process_runtime.retry())
    row.addWidget(retry)
    layout.addWidget(box)
    timer = QTimer(box)
    timer.setInterval(1000)
    meter = ResourceMetrics()
    def refresh():
        if not box.isVisible(): return
        runtime = getattr(host, 'process_runtime', None)
        active = [p for p in host.findChildren(QProcess) if p.state() != QProcess.ProcessState.NotRunning]
        rows, pids = [], {os.getpid()}
        for name, pid in [('OHC UI', os.getpid()), *[(p.objectName() or Path(p.program()).name, int(p.processId())) for p in active]]:
            if pid <= 0: continue
            pids.add(pid)
            cpu, rss = meter.sample(pid)
            rows.append(f'{name} · PID {pid} · CPU {cpu:.1f}% · RAM/RSS {rss:.1f} MiB' if cpu is not None and rss is not None else f'{name} · PID {pid} · —')
        meter.retain(pids)
        available = host.tr_static('Verfügbar') if runtime and runtime.current() else host.tr_static('Nicht verfügbar')
        age = f'{time.monotonic() - runtime.received:.1f} s' if runtime and runtime.received else '—'
        retry.setEnabled(bool(runtime and not runtime.closed and runtime.process.state() == QProcess.ProcessState.NotRunning))
        studio = getattr(host, 'thermalright_display_studio', None)
        progress = getattr(getattr(studio, 'lcd_runtime', None), 'progress', None)
        lcd_age = f'{time.monotonic() - progress.last_sent:.1f} s' if progress and progress.last_sent else '—'
        shutdown = latest_shutdown_report()
        shutdown_text = {
            'clean': f"✓ {host.tr_static('Beenden')} · {host.tr_static('Status aktuell')}",
            'continued-in-tray': f"↪ {host.tr_static('Beim Minimieren im Infobereich weiterlaufen')}",
            'cancelled': host.tr_static('Abbrechen'),
            'ended-without-qt-confirmation': f"! {host.tr_static('Nicht prüfbar')}",
            'stuck': f"! {host.tr_static('Nicht prüfbar')}",
            'incomplete': f"! {host.tr_static('Nicht prüfbar')}",
        }.get(shutdown.status, '—')
        if shutdown.phase:
            shutdown_text += f' · phase={shutdown.phase}'
        label.setText(f"{host.tr_static('Sensorprozess')}: {available} · {host.tr_static('Messwertalter')}: {age}\n"
                      f"{host.tr_static('Eigene aktive Prozesse')}: {len(active)}\n"
                      f"{host.tr_static('Neustartversuche')}: {runtime.failures if runtime else 0}\n"
                      f"{host.tr_static('Beenden-Diagnose')}: {shutdown_text}\n"
                      f"{host.tr_static('Modulprotokoll')}: {application_state_directory() / 'module-events.jsonl'}\n"
                      f"{host.tr_static('LCD-Fortschritt')}: {progress.frames if progress else 0} · {host.tr_static('Letzter bestätigter Transfer')}: {lcd_age}\n" + '\n'.join(rows))
    timer.timeout.connect(refresh)
    host.refresh_runtime_health = refresh
    timer.start()
