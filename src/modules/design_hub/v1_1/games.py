# SPDX-License-Identifier: GPL-3.0-or-later
"""Honest game-profile setup; no claim of unsupported live telemetry."""
from dataclasses import dataclass
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from .controller import prepare_game_rule


@dataclass(frozen=True)
class Game:
    ident: str
    title: str
    process: str


# Basenames verified from installed game executables, not launcher names.
GAMES = (
    Game("atmosfar", "ATMOSFAR", "ProjectVenus-Win64-Shipping.exe"),
    Game("mirage", "Assassin’s Creed Mirage", "ACMirage.exe"),
    Game("witcher3", "The Witcher 3", "witcher3.exe"),
)


class GamesPage(QWidget):
    def __init__(self, host):
        super().__init__()
        self.host = host
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 16)
        root.addWidget(host.make_module_hero("◇", "Spieleintegration",
            "Spiele mit vorhandenen Gesamtprofilen verbinden und nach Spielende zurückwechseln."))
        note = QLabel(host.tr_static(
            "Aktuell verfügbar: Profilwechsel. Bildschirmfarben und echte Spieldaten sind noch nicht angebunden."))
        note.setWordWrap(True)
        note.setObjectName("inlineNotice")
        root.addWidget(note)
        for game in GAMES:
            card = QFrame(); card.setObjectName("moduleHeroCard")
            row = QHBoxLayout(card)
            copy = QVBoxLayout()
            title = QLabel(game.title); title.setObjectName("sectionTitle")
            copy.addWidget(title)
            state = QLabel(host.tr_static("Profilwechsel einrichten · Prozessname ist anpassbar"))
            state.setWordWrap(True); state.setObjectName("muted")
            copy.addWidget(state)
            process = QLabel(game.process)
            process.setProperty("i18nIgnore", True)
            process.setWordWrap(True); copy.addWidget(process)
            row.addLayout(copy, 1)
            button = QPushButton(host.tr_static("Profilwechsel einrichten"))
            button.clicked.connect(lambda _checked=False, value=game: prepare_game_rule(host, value))
            row.addWidget(button)
            root.addWidget(card)
        root.addStretch()
