# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded private module lifecycle records; output never proves root cause."""
import json
import os
import time
import uuid
from app_constants import APP_VERSION
from privacy_logging import application_state_directory, append_error_event, append_startup_event, redact_private_text

SESSION = uuid.uuid4().hex
MAX_BYTES = 1024 * 1024


def record(module, event, **details):
    """Only the GUI writes this journal; no worker/user data is uploaded."""
    data = dict(time=time.strftime('%Y-%m-%dT%H:%M:%S%z'), monotonic=round(time.monotonic(), 3),
                session=SESSION, version=APP_VERSION, module=module, event=event)
    data.update(details)
    # Redact before JSON escaping too (e.g. an address/serial on a stderr line).
    data = {key: (APP_VERSION if key == 'version' else redact_private_text(value)[:8192])
            if isinstance(value, str) else value for key, value in data.items()}
    clean = json.loads(redact_private_text(json.dumps(data, ensure_ascii=False, default=str)))
    # Only the trusted build constant is restored after recursive redaction;
    # arbitrary/nested detail fields retain the privacy filter.
    clean['version'] = APP_VERSION
    payload = json.dumps(clean, ensure_ascii=False) + '\n'
    try:
        directory = application_state_directory()
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        path = directory / 'module-events.jsonl'
        if path.is_symlink(): return None
        if path.exists() and path.stat().st_size + len(payload.encode()) > MAX_BYTES:
            with path.open('rb') as handle:
                handle.seek(max(0, path.stat().st_size - MAX_BYTES // 2))
                tail = handle.read(MAX_BYTES // 2).split(b'\n', 1)[-1]
            path.write_bytes(tail)
        with path.open('a', encoding='utf-8') as handle:
            handle.write(payload)
        os.chmod(path, 0o600)
        if event in {'failure', 'exhausted'}:
            append_error_event(f'MODULE: {module} {event} · Version {APP_VERSION} · {payload.rstrip()}')
        append_startup_event(f'MODULE: {module} {event} · reason={data.get("reason", "—")} · retry_ms={data.get("retry_ms", "—")}')
        return path
    except OSError:
        return None
