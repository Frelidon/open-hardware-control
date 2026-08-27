#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Original Windows-8-inspired Start screen and Charms bar for KDE Plasma 6.

This companion is intentionally unprivileged and independent from the hardware
controller.  It reads the local freedesktop application database, starts
programs without a shell, and never downloads code or artwork.
"""

from __future__ import annotations

import argparse
import configparser
import json
import os
import shlex
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, QPoint, QRect, QSize, Qt, QTimer, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QKeySequence, QShortcut
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

try:
    from PySide6.QtDBus import QDBusConnection
except ImportError:  # pragma: no cover - optional on minimal PySide packages
    QDBusConnection = None


SERVICE_NAME = "org.frelidon.OpenHardwareControl.DesktopShell"
OBJECT_PATH = "/DesktopShell"
SOCKET_NAME = "open-hardware-control-desktop-shell-v1"
SUPPORTED_STYLES = ("windows8", "windows81")
FORBIDDEN_PROGRAMS = {
    "bash", "dash", "fish", "ksh", "sh", "zsh", "cmd", "cmd.exe",
    "powershell", "pwsh", "python", "python3", "perl", "ruby", "node",
}
FIELD_CODES = {
    "%f", "%F", "%u", "%U", "%d", "%D", "%n", "%N", "%v", "%m",
}


@dataclass(frozen=True)
class DesktopApplication:
    desktop_id: str
    name: str
    icon: str
    command: tuple[str, ...]
    categories: tuple[str, ...]


def _application_directories() -> list[Path]:
    home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    system = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share")
    result = [home / "applications"]
    result.extend(Path(item) / "applications" for item in system.split(":") if item)
    return result


def _safe_command(value: str) -> tuple[str, ...] | None:
    try:
        parts = shlex.split(value, posix=True)
    except ValueError:
        return None
    if not parts:
        return None
    executable = Path(parts[0]).name.casefold()
    if executable in FORBIDDEN_PROGRAMS or executable == "env":
        return None
    clean: list[str] = []
    for part in parts:
        if part in FIELD_CODES:
            continue
        replacement = part.replace("%%", "%")
        if any(code in replacement for code in FIELD_CODES):
            continue
        if "\x00" in replacement or "\n" in replacement or "\r" in replacement:
            return None
        clean.append(replacement)
    return tuple(clean) if clean else None


def discover_applications(limit: int = 240) -> list[DesktopApplication]:
    """Return de-duplicated launchable applications from fixed XDG paths."""
    found: dict[str, DesktopApplication] = {}
    for directory in _application_directories():
        if not directory.is_dir():
            continue
        try:
            paths = sorted(directory.glob("*.desktop"), key=lambda item: item.name.casefold())
        except OSError:
            continue
        for path in paths:
            if path.name in found or path.is_symlink() or not path.is_file():
                continue
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            parser.optionxform = str
            try:
                parser.read(path, encoding="utf-8")
                entry = parser["Desktop Entry"]
            except (OSError, KeyError, configparser.Error, UnicodeError):
                continue
            if entry.get("Type", "Application") != "Application":
                continue
            if entry.get("Hidden", "false").casefold() == "true" or entry.get("NoDisplay", "false").casefold() == "true":
                continue
            only_show = {item.casefold() for item in entry.get("OnlyShowIn", "").split(";") if item}
            if only_show and not only_show.intersection({"kde", "plasma"}):
                continue
            command = _safe_command(entry.get("Exec", ""))
            name = entry.get("Name", "").strip()
            if not command or not name:
                continue
            found[path.name] = DesktopApplication(
                desktop_id=path.name,
                name=name[:80],
                icon=entry.get("Icon", "application-x-executable").strip() or "application-x-executable",
                command=command,
                categories=tuple(item for item in entry.get("Categories", "").split(";") if item),
            )
            if len(found) >= limit:
                break
    return sorted(found.values(), key=lambda item: item.name.casefold())


def launch_application(app: DesktopApplication) -> bool:
    executable = app.command[0]
    resolved = executable if Path(executable).is_absolute() else shutil.which(executable)
    if not resolved:
        return False
    return bool(QApplication.instance()) and bool(
        __import__("PySide6.QtCore", fromlist=["QProcess"]).QProcess.startDetached(resolved, list(app.command[1:]))[0]
    )


def _state_file() -> Path:
    override = os.environ.get("OHC_DESKTOP_DESIGN_STATE_DIR", "").strip()
    if override:
        return Path(override).expanduser() / "active.json"
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return base / "open-hardware-control" / "desktop-designs" / "active.json"


def configured_style(default: str = "windows8") -> str:
    try:
        value = json.loads(_state_file().read_text(encoding="utf-8")).get("style")
    except (OSError, ValueError, AttributeError):
        value = default
    return value if value in SUPPORTED_STYLES else default


class TileButton(QPushButton):
    def __init__(self, app: DesktopApplication, accent: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.app = app
        self.setText(app.name)
        icon = QIcon.fromTheme(app.icon)
        if not icon.isNull():
            self.setIcon(icon)
            self.setIconSize(QSize(48, 48))
        self.setMinimumSize(152, 112)
        self.setMaximumSize(190, 132)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            "QPushButton { background: " + accent + "; color: white; border: 0; padding: 10px; "
            "font-size: 13px; text-align: left; } QPushButton:hover { border: 3px solid white; } "
            "QPushButton:pressed { background: #174f78; }"
        )


class StartScreen(QWidget):
    def __init__(self, owner: "DesktopShell"):
        super().__init__(None, Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.owner = owner
        self.apps = discover_applications()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setObjectName("ohcStartScreen")
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(58, 36, 42, 28)
        layout.setSpacing(18)
        header = QHBoxLayout()
        self.title = QLabel("Start")
        self.title.setFont(QFont("Noto Sans", 30, QFont.Weight.Light))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Apps suchen")
        self.search.setClearButtonEnabled(True)
        self.search.setMaximumWidth(340)
        self.search.textChanged.connect(self._filter)
        user = QLabel(os.environ.get("USER", "Benutzer"))
        user.setFont(QFont("Noto Sans", 13))
        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.search)
        header.addWidget(user)
        layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tile_host = QWidget()
        self.grid = QGridLayout(self.tile_host)
        self.grid.setContentsMargins(0, 4, 0, 12)
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(10)
        self.buttons: list[TileButton] = []
        accents = ("#0078d7", "#00a300", "#7e3878", "#d24726", "#008299", "#5133ab")
        for index, app in enumerate(self.apps):
            button = TileButton(app, accents[index % len(accents)])
            button.clicked.connect(lambda _checked=False, selected=app: self._launch(selected))
            self.grid.addWidget(button, index % 5, index // 5)
            self.buttons.append(button)
        self.scroll.setWidget(self.tile_host)
        layout.addWidget(self.scroll, 1)

        self.setStyleSheet(
            "QWidget#ohcStartScreen { background: #180052; color: white; } "
            "QLineEdit { background: white; color: #202020; border: 0; padding: 9px; font-size: 14px; } "
            "QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }"
        )

    def _filter(self, query: str) -> None:
        needle = query.strip().casefold()
        for button in self.buttons:
            button.setVisible(not needle or needle in button.app.name.casefold())

    def _launch(self, app: DesktopApplication) -> None:
        if launch_application(app):
            self.hide()
        else:
            QMessageBox.warning(self, "Open Hardware Control", f"{app.name} konnte nicht gestartet werden.")

    def show_for_screen(self, geometry: QRect, style: str) -> None:
        self.title.setText("Start" if style == "windows8" else "Start · 8.1")
        background = "#180052" if style == "windows8" else "#075b9b"
        self.setStyleSheet(self.styleSheet().replace("#180052", background).replace("#075b9b", background))
        self.setGeometry(geometry)
        self.show()
        self.raise_()
        self.activateWindow()

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt API
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            return
        super().keyPressEvent(event)


class CharmsBar(QWidget):
    def __init__(self, owner: "DesktopShell"):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.owner = owner
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setObjectName("ohcCharmsBar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 36, 26, 32)
        layout.setSpacing(8)
        layout.addStretch()
        for label, icon, action in (
            ("Suchen", "system-search", self._search),
            ("Teilen", "document-share", self._share),
            ("Start", "start-here-kde", self.owner.toggle_start),
            ("Geräte", "computer", self._devices),
            ("Einstellungen", "preferences-system", self._settings),
        ):
            button = QPushButton(label)
            button.setIcon(QIcon.fromTheme(icon))
            button.setIconSize(QSize(32, 32))
            button.setMinimumHeight(58)
            button.clicked.connect(action)
            layout.addWidget(button)
        layout.addStretch()
        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.clock)
        timer = QTimer(self)
        timer.timeout.connect(self._update_clock)
        timer.start(1000)
        self._update_clock()
        self.setStyleSheet(
            "QWidget#ohcCharmsBar { background: rgba(8, 8, 12, 245); color: white; } "
            "QPushButton { color: white; background: transparent; border: 0; text-align: left; font-size: 15px; padding: 9px; } "
            "QPushButton:hover { background: #0067a6; } QLabel { color: white; font-size: 15px; }"
        )

    def _update_clock(self) -> None:
        from datetime import datetime
        self.clock.setText(datetime.now().strftime("%H:%M\n%d.%m.%Y"))

    def show_for_screen(self, geometry: QRect) -> None:
        width = min(330, max(260, geometry.width() // 5))
        self.setGeometry(geometry.right() - width + 1, geometry.top(), width, geometry.height())
        self.show()
        self.raise_()
        self.activateWindow()

    def _search(self) -> None:
        self.hide()
        self.owner.show_start(search=True)

    def _share(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Datei sicher teilen")
        if not selected:
            return
        mailer = shutil.which("xdg-email")
        if mailer:
            from PySide6.QtCore import QProcess
            QProcess.startDetached(mailer, ["--attach", selected])
        else:
            QMessageBox.information(self, "Teilen", "Kein xdg-email-Programm wurde gefunden.")

    @staticmethod
    def _start(programs: tuple[str, ...], arguments: list[str] | None = None) -> None:
        from PySide6.QtCore import QProcess
        for program in programs:
            resolved = shutil.which(program)
            if resolved:
                QProcess.startDetached(resolved, arguments or [])
                return

    def _devices(self) -> None:
        self.hide()
        self._start(("systemsettings", "systemsettings6"), ["kcm_kscreen"])

    def _settings(self) -> None:
        self.hide()
        self._start(("systemsettings", "systemsettings6"))

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt API
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            return
        super().keyPressEvent(event)


class HotCorner(QWidget):
    """Small transparent fallback corner used if a compositor edge is unavailable."""

    def __init__(self, owner: "DesktopShell", screen, bottom: bool):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.owner = owner
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.02)
        self.setMouseTracking(True)
        geometry = screen.geometry()
        self.setGeometry(geometry.right() - 2, geometry.bottom() - 2 if bottom else geometry.top(), 3, 3)
        self.show()

    def enterEvent(self, event) -> None:  # noqa: N802 - Qt API
        QTimer.singleShot(80, self.owner.show_charms)
        super().enterEvent(event)


class DesktopShell(QObject):
    def __init__(self, style: str):
        super().__init__()
        self.style = style
        self.start_screen = StartScreen(self)
        self.charms = CharmsBar(self)
        self.hot_corners = [HotCorner(self, screen, bottom) for screen in QApplication.screens() for bottom in (False, True)]

    @staticmethod
    def _active_geometry() -> QRect:
        point = __import__("PySide6.QtGui", fromlist=["QCursor"]).QCursor.pos()
        screen = QApplication.screenAt(point) or QApplication.primaryScreen()
        return screen.geometry()

    @Slot()
    def ShowStart(self) -> None:  # noqa: N802 - D-Bus API
        self.show_start()

    @Slot()
    def ToggleStart(self) -> None:  # noqa: N802 - D-Bus API
        self.toggle_start()

    @Slot()
    def ShowCharms(self) -> None:  # noqa: N802 - D-Bus API
        self.show_charms()

    @Slot()
    def ToggleCharms(self) -> None:  # noqa: N802 - D-Bus API
        self.toggle_charms()

    def show_start(self, search: bool = False) -> None:
        self.charms.hide()
        self.start_screen.show_for_screen(self._active_geometry(), self.style)
        if search:
            self.start_screen.search.setFocus()

    def toggle_start(self) -> None:
        if self.start_screen.isVisible():
            self.start_screen.hide()
        else:
            self.show_start()

    def show_charms(self) -> None:
        if not self.start_screen.isVisible():
            self.charms.show_for_screen(self._active_geometry())

    def toggle_charms(self) -> None:
        if self.charms.isVisible():
            self.charms.hide()
        else:
            self.show_charms()


def send_action(action: str) -> bool:
    socket = QLocalSocket()
    socket.connectToServer(SOCKET_NAME)
    if not socket.waitForConnected(350):
        return False
    socket.write(action.encode("ascii") + b"\n")
    socket.flush()
    socket.waitForBytesWritten(350)
    socket.disconnectFromServer()
    return True


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OHC Windows-8-inspired KDE desktop shell")
    parser.add_argument("--style", choices=SUPPORTED_STYLES)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--background", action="store_true")
    action.add_argument("--show-start", action="store_true")
    action.add_argument("--show-charms", action="store_true")
    action.add_argument("--quit", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    app = QApplication(sys.argv[:1])
    app.setApplicationName("Open Hardware Control Desktop Shell")
    action = "quit" if args.quit else "start" if args.show_start else "charms" if args.show_charms else ""
    if action and send_action(action):
        return 0

    QLocalServer.removeServer(SOCKET_NAME)
    server = QLocalServer(app)
    if not server.listen(SOCKET_NAME):
        return 1
    shell = DesktopShell(args.style or configured_style())

    def receive() -> None:
        connection = server.nextPendingConnection()
        if not connection.waitForReadyRead(200):
            return
        request = bytes(connection.readAll()).strip().decode("ascii", errors="ignore")
        if request == "start":
            shell.toggle_start()
        elif request == "charms":
            shell.toggle_charms()
        elif request == "quit":
            app.quit()

    server.newConnection.connect(receive)
    shortcut_start = QShortcut(QKeySequence("Meta"), shell.start_screen)
    shortcut_start.activated.connect(shell.toggle_start)
    shortcut_charms = QShortcut(QKeySequence("Meta+C"), shell.start_screen)
    shortcut_charms.activated.connect(shell.toggle_charms)
    # Keep shortcut objects alive even when the Start window is hidden.
    shell._shortcuts = (shortcut_start, shortcut_charms)

    if QDBusConnection is not None:
        bus = QDBusConnection.sessionBus()
        bus.registerService(SERVICE_NAME)
        try:
            bus.registerObject(OBJECT_PATH, shell, QDBusConnection.RegisterOption.ExportAllSlots)
        except (AttributeError, TypeError):
            bus.registerObject(OBJECT_PATH, shell)
    if args.show_start:
        QTimer.singleShot(0, shell.show_start)
    elif args.show_charms:
        QTimer.singleShot(0, shell.show_charms)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
