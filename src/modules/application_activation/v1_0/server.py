#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""User-local single-instance window activation and tray-start policy."""

from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import MutableMapping, Sequence

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

_SHOW_REQUEST = b"show\n"
_OPENED_REPLY = b"opened\n"
_MAX_REQUEST_BYTES = 32


def suppress_autostart_startup_feedback(
    arguments: Sequence[str], environment: MutableMapping[str, str] | None = None,
) -> bool:
    """Drop compositor activation tokens only for an intentionally hidden start."""
    if "--autostart" not in arguments:
        return False
    target = os.environ if environment is None else environment
    target.pop("DESKTOP_STARTUP_ID", None)
    target.pop("XDG_ACTIVATION_TOKEN", None)
    return True


def request_existing_instance(endpoint: Path, timeout_ms: int = 900) -> bool:
    """Ask the lock-owning process to show its window without creating Qt UI."""
    timeout_s = max(0.1, min(2.0, int(timeout_ms) / 1000.0))
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(timeout_s)
    try:
        client.connect(os.fspath(endpoint))
        client.sendall(_SHOW_REQUEST)
        reply = client.recv(_MAX_REQUEST_BYTES)
        return reply == _OPENED_REPLY
    except (OSError, TimeoutError):
        return False
    finally:
        client.close()


class ApplicationActivationServer(QObject):
    """Expose a single bounded `show` request on a user-only local socket."""

    activation_requested = Signal()

    def __init__(self, endpoint: Path, parent: QObject | None = None):
        super().__init__(parent)
        self.endpoint = Path(endpoint)
        self.server = QLocalServer(self)
        self.server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
        self.server.newConnection.connect(self._accept_connections)
        self._clients: set[QLocalSocket] = set()

    def start(self) -> bool:
        self.endpoint.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            os.chmod(self.endpoint.parent, 0o700)
        except OSError:
            return False
        QLocalServer.removeServer(os.fspath(self.endpoint))
        return bool(self.server.listen(os.fspath(self.endpoint)))

    def stop(self) -> None:
        for client in tuple(self._clients):
            client.abort()
            client.deleteLater()
        self._clients.clear()
        if self.server.isListening():
            self.server.close()
        QLocalServer.removeServer(os.fspath(self.endpoint))

    def _accept_connections(self) -> None:
        while self.server.hasPendingConnections():
            client = self.server.nextPendingConnection()
            if client is None:
                continue
            self._clients.add(client)
            client.readyRead.connect(lambda current=client: self._read_request(current))
            client.disconnected.connect(lambda current=client: self._drop_client(current))
            if client.bytesAvailable():
                self._read_request(client)

    def _read_request(self, client: QLocalSocket) -> None:
        request = bytes(client.read(_MAX_REQUEST_BYTES))
        if request == _SHOW_REQUEST:
            self.activation_requested.emit()
            client.write(_OPENED_REPLY)
        else:
            client.write(b"rejected\n")
        client.flush()
        client.disconnectFromServer()

    def _drop_client(self, client: QLocalSocket) -> None:
        self._clients.discard(client)
        client.deleteLater()
