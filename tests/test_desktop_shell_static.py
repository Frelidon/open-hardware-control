#!/usr/bin/env python3
"""Dependency-free security checks for the optional desktop shell."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "src/desktop_shell.py").read_text(encoding="utf-8")
kwin = (ROOT / "src/assets/desktop-designs/kwin/ohc-charms/contents/code/main.js").read_text(encoding="utf-8")

assert "shell=True" not in source
assert "requests" not in source
assert "urllib" not in source
assert "http://" not in source and "https://" not in source
assert "discover_applications" in source
assert "FORBIDDEN_PROGRAMS" in source
assert "QProcess.startDetached" in source
assert "registerScreenEdge(KWin.ElectricTopRight" in kwin
assert "registerScreenEdge(KWin.ElectricBottomRight" in kwin
assert '"Meta+C"' in kwin
assert '"Meta+Space"' in kwin
assert "callDBus" in kwin
assert "if args.quit:" in source
assert "QCoreApplication(sys.argv[:1])" in source
assert "QLocalServer.removeServer(SOCKET_NAME)" in source
assert source.index("if args.quit:") < source.index("app = QApplication(sys.argv[:1])")

print("Desktop shell static safety checks passed.")
