# SPDX-License-Identifier: GPL-3.0-or-later
"""Temporary, isolated hardware preview for a paired GPU/support ARGB path."""
import time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from command_backend import Backend
from nzxt_rgb import build_nzxt_effect_arguments, coalesce_selected_channels
from .gpu_motion import RANGES
from .gpu_support_sync import pair


HOLD_SECONDS = 10


def smoother(values):
    """One bounded, visible change; never touch brightness or the support strip."""
    candidate = dict(values)
    candidate['tempo'] = max(RANGES['tempo'][0], candidate['tempo'] - 10)
    candidate['gpu_lead'] = min(RANGES['gpu_lead'][1], candidate['gpu_lead'] + 2)
    candidate['gpu_tail'] = min(RANGES['gpu_tail'][1], candidate['gpu_tail'] + 2)
    return candidate if candidate != values else None


def prepare(host, editor):
    """Check the real running path before changing a single LED."""
    tr = host.tr_static
    if (not host.openrgb_write_enabled or host.openrgb_external_server_detected
            or not host.openrgb_effect_active or getattr(host, 'rgb_manual_write_active', False)
            or getattr(host, 'explicit_quit_requested', False)):
        return None, tr('Zuerst ein OHC-Lauflicht starten und den RGB-Schreibzugriff prüfen.')
    if editor.effect().effect_id not in {'spinner', 'comet'}:
        return None, tr('Für den Assistenten zuerst Lauflicht oder Komet als OHC-Design starten.')
    linked = pair(host, editor.effect())
    if (linked is None or linked['gpu'] != (editor.gpu_controller, editor.gpu_zone)
            or not editor.sync_enabled):
        return None, tr('GPU und Halterung zuerst mit festen ARGB-Anschlüssen synchronisieren und speichern.')
    targets = {linked['gpu'][0], linked['support'][0]}
    if not targets.issubset(host.openrgb_effect_assignments):
        return None, tr('Beide LED-Anschlüsse müssen im laufenden OHC-Effekt aktiv sein.')
    visible = {}
    for controller, zone in (linked['gpu'], linked['support']):
        visible.setdefault(controller, set()).add(zone)
    for device in host.selected_openrgb_devices():
        stable_id = host.openrgb_stable_ids.get(device.index)
        if device.supports_direct:
            sizes = host.openrgb_device_write_shape(device)[1]
            if stable_id not in host.openrgb_effect_assignments or sizes is None:
                return None, tr('Alle gewählten Direct-Geräte benötigen aktive, bekannte LED-Zonen.')
            continue
        if stable_id == editor.gpu_id or stable_id in targets:
            continue
        if not any(mode.casefold() in {'static', 'off'} for mode in device.modes):
            return None, tr('Ein gewähltes Gerät lässt sich für den Sichttest nicht sicher ausschalten.')
    commands = []
    blackout = getattr(host, 'build_rgb_device_test_commands', None)
    if callable(blackout):
        commands, blocked = blackout('', exclude_ids={*targets, editor.gpu_id}, only_selected=True)
        if blocked:
            host.log_message('RGB-KALIBRIERUNG: nicht schreibbare LEDs bleiben unverändert · ' + ', '.join(blocked))
    else:
        # Small host stubs can run the pure visual preview without device
        # inventory. Production uses the selected-device blackout builder.
        for device in host.selected_openrgb_devices():
            stable_id = host.openrgb_stable_ids.get(device.index)
            if device.supports_direct or stable_id == editor.gpu_id or stable_id in targets:
                continue
            mode = next(mode for preferred in ('Static', 'Off') for mode in device.modes
                        if mode.casefold() == preferred.casefold())
            commands.append(host.openrgb_client.native_mode_command(device.index, mode, ['000000'], 0))
        for channel in coalesce_selected_channels(host.selected_nzxt_rgb_channels()):
            commands.extend(build_nzxt_effect_arguments(Backend.rgb_args(), channel, 'fixed', ['000000']))
    return (visible, targets, commands), ''


class GpuMotionWizard(QDialog):
    def __init__(self, editor, plan):
        super().__init__(editor)
        self.editor = editor
        self.host = editor.host
        self.visible, self.targets, self.commands = plan
        self.original = editor.values()
        self.phase = 'starting'
        self.changed_at = self.hold_at = None
        self.required_frame_id = 0
        self.pending = bool(self.commands)
        self.restored = False
        self.setWindowTitle(self.host.tr_static('LED-Flüssigkeit abstimmen'))
        self.setMinimumWidth(490)
        layout = QVBoxLayout(self)
        info = QLabel(self.host.tr_static(
            'Andere von OHC gesteuerte LEDs bleiben während des Sichttests dunkel. Jeder Wert läuft mindestens 10 Sekunden.'))
        info.setWordWrap(True)
        layout.addWidget(info)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        buttons = QHBoxLayout()
        self.again = QPushButton(self.host.tr_static('Noch ruckelig · nächsten Wert testen'))
        self.accept_button = QPushButton(self.host.tr_static('Flüssig · übernehmen'))
        cancel = QPushButton(self.host.tr_static('Abbrechen'))
        buttons.addWidget(self.again)
        buttons.addWidget(self.accept_button)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)
        self.again.clicked.connect(self.next_value)
        self.accept_button.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.tick)
        self.update_status(self.host.tr_static('Andere LEDs werden ausgeschaltet …'))
        self.host.rgb_header_preview_depth = getattr(self.host, 'rgb_header_preview_depth', 0) + 1
        self.host.rgb_gpu_calibration_targets = self.visible
        self.host.log_message('RGB-KALIBRIERUNG: Start · andere ausgewählte Zonen dunkel · GPU/Halterung bleiben aktiv')
        if self.commands:
            self.host.run_rgb_command_sequence(self.commands, 'LED-Sichttest · andere Geräte dunkel',
                                               finished=self.blackout_finished)
        else:
            self.blackout_finished(True)

    def blackout_finished(self, ok):
        self.pending = False
        if self.restored:
            self.restore_hardware()
            return
        if not ok:
            self.abort(self.host.tr_static('Andere LEDs konnten nicht ausgeschaltet werden; Sichttest abgebrochen.'))
            return
        self.begin_candidate()
        self.timer.start()

    def begin_candidate(self):
        # A frame already in flight can still contain the previous setting.
        # Wait for a new worker request carrying this candidate on both paths.
        self.required_frame_id = self.host.openrgb_worker_frame_sequence + 1
        self.changed_at = time.monotonic()
        self.hold_at = None
        self.phase = 'waiting'
        self.host.rgb_gpu_motion_preview = self.editor.values()
        self.host.log_message(f'RGB-KALIBRIERUNG: Kandidat {self.editor.values()} · warte auf beide SDK-Frames')
        self.update_status(self.host.tr_static('Neuer Wert wird an Grafikkarte und Halterung übertragen …'))

    def update_status(self, message):
        self.status.setText(message)
        ready = self.phase == 'ready'
        self.accept_button.setEnabled(ready)
        self.again.setEnabled(ready and smoother(self.editor.values()) is not None)

    def tick(self):
        host = self.host
        now = time.monotonic()
        if (not host.openrgb_effect_active or not host.openrgb_write_enabled
                or host.openrgb_external_server_detected or getattr(host, 'explicit_quit_requested', False)
                or not self.targets.issubset(host.openrgb_effect_assignments)):
            self.abort(host.tr_static('RGB-Verbindung unterbrochen; Sichttest abgebrochen.'))
            return
        metrics = [host.openrgb_worker_metrics.get(target, {}) for target in self.targets]
        stamps = [item.get('last_success', 0.) for item in metrics]
        if self.phase == 'waiting':
            if all(item.get('last_frame_id', -1) >= self.required_frame_id
                   and stamp >= self.changed_at for item, stamp in zip(metrics, stamps)):
                self.hold_at = now
                self.phase = 'holding'
            elif now - self.changed_at > 4:
                self.abort(host.tr_static('GPU- oder Halterungsframe fehlt; Sichttest abgebrochen.'))
                return
        if self.phase in {'holding', 'ready'}:
            if any(now - stamp > 2.5 for stamp in stamps):
                self.abort(host.tr_static('GPU- oder Halterungsframe fehlt; Sichttest abgebrochen.'))
                return
            remaining = max(0, HOLD_SECONDS - int(now - self.hold_at))
            if remaining:
                self.update_status(host.tr_static('Wert beobachten: noch {seconds} Sekunden · Tempo {tempo} %').format(
                    seconds=remaining, tempo=self.editor.values()['tempo']))
            else:
                self.phase = 'ready'
                self.update_status(host.tr_static('Jetzt beurteilen: flüssig oder noch ruckelig?'))

    def next_value(self):
        if self.phase != 'ready':
            return
        candidate = smoother(self.editor.values())
        if candidate is None:
            return
        for key, value in candidate.items():
            self.editor.sliders[key].setValue(value)
        self.begin_candidate()

    def abort(self, reason):
        self.host.log_message(f'RGB-KALIBRIERUNG: {reason}')
        self.reject()

    def accept(self):
        if self.phase != 'ready':
            return
        self.host.log_message(f'RGB-KALIBRIERUNG: übernommen · {self.editor.values()}')
        super().accept()

    def reject(self):
        if not self.restored:
            for key, value in self.original.items():
                self.editor.sliders[key].setValue(value)
        super().reject()

    def done(self, result):
        self.timer.stop()
        self.restored = True
        if getattr(self.host, 'rgb_gpu_calibration_targets', None) is self.visible:
            self.host.rgb_gpu_calibration_targets = None
        self.host.rgb_header_preview_depth = max(0, self.host.rgb_header_preview_depth - 1)
        self.restore_hardware()
        super().done(result)

    def restore_hardware(self):
        if self.pending:
            return
        host = self.host
        if (host.openrgb_effect_active and host.openrgb_write_enabled
                and getattr(host, 'openrgb_server_reachable', False)
                and not host.openrgb_external_server_detected
                and not getattr(host, 'openrgb_engine_crash_quarantined', False)
                and not getattr(host, 'explicit_quit_requested', False)
                and not getattr(host, 'session_shutdown_requested', False)
                and not getattr(host, 'exit_hardware_cleanup_in_progress', False)):
            host.rgb_last_effect_request_signature = None
            host.start_openrgb_effect()
            host.log_message('RGB-KALIBRIERUNG: ursprüngliches Design für alle ausgewählten LEDs angefordert')
        else:
            host.log_message('RGB-KALIBRIERUNG: Design-Rückgabe ausgesetzt · RGB-Engine oder Besitz nicht bereit')
