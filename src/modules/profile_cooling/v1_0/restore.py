# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded sensor readiness, latest request wins; never a new hardware writer."""
from copy import deepcopy
import math
import time
from PySide6.QtCore import QObject, QTimer
from modules.cooling_state.v1_0.controller import closing

WAIT_SECONDS = 10.0


def context(host):
    runtime = getattr(host, 'process_runtime', None)
    if runtime is None: return 'sensor-runtime=unavailable'
    received = getattr(runtime, 'received', 0.)
    age = f'{max(0., time.monotonic()-received):.2f}s' if received else 'none'
    return (f'snapshot_age={age} · pending={bool(getattr(runtime, "pending", False))}'
            f' · failures={getattr(runtime, "failures", 0)}'
            f' · reason={str(getattr(runtime, "failure_reason", "") or "none")[:256]}')


class ProfileCoolingWait(QObject):
    def __init__(self, host):
        super().__init__(host)
        self.host = host
        self.timer = QTimer(self); self.timer.setInterval(200)
        self.timer.timeout.connect(self.check)
        self.pending = None
        self.deadline = 0.
        self.baseline = None

    def cancel(self, reason='superseded'):
        had_pending = self.pending is not None
        self.timer.stop(); self.pending = None; self.baseline = None
        if had_pending:
            self.host.log_message(self.host.tr_static('PROFIL-KÜHLUNG: Ausstehende Anwendung verworfen · Grund={reason}').format(reason=reason))

    def wait(self, cooling, name):
        self.cancel()
        self.pending = (deepcopy(cooling), str(name))
        self.baseline = deepcopy(self.host.capture_profile_payload('Kühlung'))
        self.deadline = time.monotonic()+WAIT_SECONDS
        self.host.log_message(self.host.tr_static(
            'PROFIL-KÜHLUNG: Profil „{name}“ wartet bis zu 10 Sekunden auf einen frischen CPU-Messwert. {detail}'
        ).format(name=name, detail=context(self.host)))
        self.host.footer_status.setText(self.host.tr_static('Kühlprofil wartet auf frische CPU-Temperatur.'))
        self.timer.start()
        self.request_sample()

    def request_sample(self):
        runtime = getattr(self.host, 'process_runtime', None)
        # Existing one-in-flight/timeout supervisor keeps ownership of requests.
        if runtime is not None and not getattr(runtime, 'pending', False):
            runtime.poll()

    def check(self):
        if self.pending is None: self.timer.stop(); return
        host = self.host
        if closing(host): self.cancel('shutdown'); return
        if host.capture_profile_payload('Kühlung') != self.baseline:
            self.cancel('controls-changed'); return
        cooling, name = self.pending
        # A single expired sample is not proof that the CPU sensor disappeared.
        # Never relax ProcessRuntime's 2.5-s freshness or read sysfs on the GUI.
        value, label = host.read_amd_cpu_temperature()
        valid = type(value) in (int, float) and math.isfinite(value) and 0 < value < 150
        if time.monotonic() >= self.deadline:
            self.pending = None; self.baseline = None; self.timer.stop()
            detail = host.tr_static('Auch nach 10 Sekunden ist keine frische CPU-Temperatur verfügbar. Die Profilkurve wurde nicht übertragen.')
            host.report_profile_apply_error(name, f'{detail} {label} · {context(host)}', component='Kühlung')
            return
        if valid:
            self.pending = None; self.baseline = None; self.timer.stop()
            if not host.cooling_device_ready():
                host.report_profile_apply_error(name, host.tr_static('Kühlgerät ist nicht mehr verfügbar.'), component='Kühlung')
                return
            host.log_message(host.tr_static('PROFIL-KÜHLUNG: Frischer CPU-Messwert verfügbar; Profil „{name}“ wird erneut geprüft.').format(name=name))
            host.transmit_profile_cooling(cooling, name)
        else:
            self.request_sample()


def cancel(host):
    controller = getattr(host, 'profile_cooling_wait', None)
    if controller is not None: controller.cancel()


def wait_for_cpu(host, cooling, name):
    if not hasattr(host, 'profile_cooling_wait'):
        host.profile_cooling_wait = ProfileCoolingWait(host)
    if not closing(host): host.profile_cooling_wait.wait(cooling, name)
