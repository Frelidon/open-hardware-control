# SPDX-License-Identifier: GPL-3.0-or-later
"""Thread-safe bounded diagnostics; no GUI calls from Python/Qt worker threads."""
from collections import deque
import sys
import threading
import time
import traceback
from privacy_logging import append_error_event, redact_private_text, set_error_listener


class ErrorCapture:
    def __init__(self):
        self.queue = deque(maxlen=64)
        self.lock = threading.Lock()
        self.recent = {}
        self.installed = False
        self.original = None
        self.qt_original = None

    def record(self, source, text, *, persist=True, warning=False):
        prefix = 'LAUFZEIT-WARNUNG' if warning else 'LAUFZEIT-FEHLER'
        clean = redact_private_text(f'{prefix}: {source} · {text}')[:16384]
        now = time.monotonic()
        with self.lock:
            # Recurring Qt warnings must not fill disk or stall the event loop.
            if now-self.recent.get(clean, -100.) < 5.: return
            if len(self.recent) >= 64: self.recent.pop(next(iter(self.recent)))
            self.recent[clean] = now
            self.queue.append(clean)
        if persist: append_error_event(clean, notify=False)

    def receive_durable(self, text):
        self.record('module', text, persist=False)

    def drain(self):
        with self.lock:
            result = list(self.queue); self.queue.clear()
        return result

    def exception(self, source, kind, value, trace, *, persist=True):
        text = ''.join(traceback.format_exception(kind, value, trace))
        self.record(source, text, persist=persist)

    def install(self):
        if self.installed: return
        from PySide6.QtCore import qInstallMessageHandler, QtMsgType
        self.original = (sys.excepthook, threading.excepthook, sys.unraisablehook)

        def python_error(kind, value, trace):
            # The existing hook retains last-crash.log/native crash recording.
            self.exception('Python', kind, value, trace, persist=False)
            self.original[0](kind, value, trace)

        def thread_error(args):
            self.exception('Python thread', args.exc_type, args.exc_value, args.exc_traceback)
            self.original[1](args)

        def unraisable_error(args):
            self.exception('Python unraisable', args.exc_type, args.exc_value, args.exc_traceback)
            self.original[2](args)

        def qt_error(kind, context, message):
            if kind in (QtMsgType.QtWarningMsg, QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg):
                category = str(getattr(context, 'category', '') or 'Qt')[:128]
                self.record(category, message, warning=kind == QtMsgType.QtWarningMsg)
            if self.qt_original is not None:
                self.qt_original(kind, context, message)
            else:
                # Retain console diagnostics as well as the durable error file.
                try: sys.stderr.write(redact_private_text(str(message))+'\n')
                except (OSError, RuntimeError, ValueError): pass

        self.hooks = (python_error, thread_error, unraisable_error)
        self.qt_handler = qt_error
        sys.excepthook, threading.excepthook, sys.unraisablehook = self.hooks
        self.qt_original = qInstallMessageHandler(qt_error)
        self.previous_listener = set_error_listener(self.receive_durable)
        self.installed = True

    def restore(self):
        if not self.installed: return
        from PySide6.QtCore import qInstallMessageHandler
        for owner, field, installed, original in zip((sys, threading, sys),
                ('excepthook', 'excepthook', 'unraisablehook'), self.hooks, self.original):
            if getattr(owner, field) is installed: setattr(owner, field, original)
        qInstallMessageHandler(self.qt_original)
        set_error_listener(self.previous_listener)
        self.installed = False
