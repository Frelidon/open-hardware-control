# SPDX-License-Identifier: GPL-3.0-or-later
"""Deliver durable worker/Qt errors to the general log on the GUI thread."""
from PySide6.QtCore import QObject, QTimer


class ErrorLogBridge(QObject):
    def __init__(self, host, capture):
        super().__init__(host)
        self.host, self.capture = host, capture
        self.timer = QTimer(self); self.timer.setInterval(250)
        self.timer.timeout.connect(self.flush); self.timer.start()
        self.flush()

    def flush(self):
        for text in self.capture.drain():
            self.host.log_message(text, persist_error=False)
