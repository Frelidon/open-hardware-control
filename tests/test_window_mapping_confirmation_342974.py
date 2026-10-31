from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules.window_placement.v1_5 import confirmation  # noqa: E402


class Screen:
    def __init__(self, name: str) -> None:
        self._name = name

    def name(self) -> str:
        return self._name


class Rect:
    def x(self) -> int:
        return 1920

    def y(self) -> int:
        return 0

    def width(self) -> int:
        return 1600

    def height(self) -> int:
        return 1000

    def center(self) -> object:
        return object()


class Handle:
    def __init__(self, screen: Screen) -> None:
        self._screen = screen

    def screen(self) -> Screen:
        return self._screen


class Window:
    def __init__(self, target: Screen, handle_screen: Screen) -> None:
        self.target = target
        self.handle = Handle(handle_screen)
        self.rect = Rect()
        self.logs: list[str] = []
        self.corrections: list[str] = []

    def isVisible(self) -> bool:
        return True

    def isMinimized(self) -> bool:
        return False

    def preferred_window_screen(self) -> tuple[Screen, bool]:
        return self.target, True

    def windowHandle(self) -> Handle:
        return self.handle

    def frameGeometry(self) -> Rect:
        return self.rect

    def geometry(self) -> Rect:
        return self.rect

    def log_message(self, message: str) -> None:
        self.logs.append(message)

    def position_window_on_preferred_screen(self, reason: str) -> bool:
        self.corrections.append(reason)
        return True


def test_confirmed_compositor_screen_is_not_repositioned(monkeypatch) -> None:
    monkeypatch.setattr(confirmation, "is_kwin_wayland", lambda: False)
    primary = Screen("DP-1")
    window = Window(primary, primary)
    monkeypatch.setattr(confirmation.QApplication, "screenAt", lambda _point: primary)

    assert confirmation.confirm_window_screen_after_mapping(window, "Start")
    assert window.corrections == []
    assert "bestätigt=DP-1" in window.logs[-1]


def test_wrong_compositor_screen_is_corrected_once(monkeypatch) -> None:
    monkeypatch.setattr(confirmation, "is_kwin_wayland", lambda: False)
    primary = Screen("DP-1")
    secondary = Screen("HDMI-A-1")
    window = Window(primary, secondary)
    monkeypatch.setattr(confirmation.QApplication, "screenAt", lambda _point: secondary)

    assert not confirmation.confirm_window_screen_after_mapping(window, "Start")
    assert len(window.corrections) == 1
    assert "Ziel=DP-1" in window.logs[-1]
    assert "Ist=HDMI-A-1" in window.logs[-1]


def test_wayland_handle_screen_wins_over_stale_requested_geometry(monkeypatch) -> None:
    monkeypatch.setattr(confirmation, "is_kwin_wayland", lambda: False)
    primary = Screen("DP-1")
    secondary = Screen("HDMI-A-1")
    window = Window(primary, secondary)
    monkeypatch.setattr(confirmation.QApplication, "screenAt", lambda _point: primary)

    assert not confirmation.confirm_window_screen_after_mapping(window, "Start")
    assert window.corrections == ["Start · Nachkorrektur"]
    assert "Ist=HDMI-A-1" in window.logs[-1]


def test_kwin_wayland_does_not_claim_qt_screen_is_compositor_truth(monkeypatch) -> None:
    primary = Screen("DP-1")
    window = Window(primary, primary)
    monkeypatch.setattr(confirmation, "is_kwin_wayland", lambda: True)
    monkeypatch.setattr(confirmation.QApplication, "screenAt", lambda _point: primary)

    assert not confirmation.confirm_window_screen_after_mapping(window, "Start")
    assert window.corrections == []
    assert "Qt-Sicht=DP-1" in window.logs[-1]
    assert "bestätigt=DP-1" not in window.logs[-1]


def test_initial_mapping_guard_is_released_after_optional_maximize() -> None:
    class InitialWindow:
        _window_screen_repositioning = True
        _state = confirmation.Qt.WindowState.WindowNoState
        visible = False
        suppressed = True

        def windowState(self):
            return self._state

        def setWindowState(self, state) -> None:
            self._state = state

        def setAttribute(self, attribute, enabled) -> None:
            assert attribute == confirmation.Qt.WidgetAttribute.WA_DontShowOnScreen
            self.suppressed = enabled

        def show(self) -> None:
            self.visible = True

    normal = InitialWindow()
    confirmation.finish_initial_window_mapping(normal, False)
    assert not normal._state & confirmation.Qt.WindowState.WindowMaximized
    assert normal.visible and not normal.suppressed
    assert not normal._window_screen_repositioning

    maximized = InitialWindow()
    confirmation.finish_initial_window_mapping(maximized, True)
    assert maximized._state & confirmation.Qt.WindowState.WindowMaximized
    assert maximized.visible and not maximized.suppressed
    assert not maximized._window_screen_repositioning
