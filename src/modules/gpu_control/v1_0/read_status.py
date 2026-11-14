# SPDX-License-Identifier: GPL-3.0-or-later
"""Honest read-only LACT badges and bounded privacy-filtered failure reporting."""
import time
from privacy_logging import redact_private_text
from .client import clock_controls

LABELS = {
    "unknown": "LACT · nicht geprüft", "loading": "LACT · wird abgefragt",
    "connected": "LACT · Daten verfügbar", "failed": "LACT · Daten nicht verfügbar",
    "empty": "LACT · keine GPU",
}


def connected_message(page):
    if page.gpu_vendor != "NVIDIA" and page.overdrive_enabled is False:
        return ("AMD-Overdrive ist vorbereitet. Bitte den Rechner neu starten und danach GPU und LACT aktualisieren."
                if page.overdrive_prepared else
                "AMD-Overdrive ist aus. In LACT aktivieren, neu starten und hier aktualisieren.")
    if page.gpu_vendor != "NVIDIA" and page.overdrive_enabled is None:
        return "Overdrive-Status unbekannt. GPU-Steuerung gesperrt."
    if not page.baseline and not clock_controls({}, page.clocks):
        return "Noch kein LACT-GPU-Profil. Grundwerte in LACT setzen und hier aktualisieren."
    return "LACT verbunden · GPU-Werte sind ausgelesen. Schreibzugriff erst nach dem Kurztest."


def refresh(page):
    badge = getattr(page, "gpu_service_badge", None)
    if badge is None: return
    state = getattr(page, "gpu_read_state", "unknown")
    if state not in LABELS: state = "unknown"
    badge.setText(("● " if state in {"connected", "failed"} else "○ ") + page.tr(LABELS[state]))
    badge.setObjectName("gpuServiceBadge" if state == "connected" else
                        "healthCritical" if state == "failed" else "muted")
    badge.setAccessibleName(page.tr(LABELS[state]))
    badge.style().unpolish(badge); badge.style().polish(badge)
    page.gpu_service_note.setText(page.tr("Lesestatus"))
    explanation = page.tr("Letzte Abfrage fehlgeschlagen. Frühere Werte sind nicht aktuell.") if state == "failed" else ""
    badge.setToolTip(explanation)
    for name in ("gpu_temperature_value", "gpu_hotspot_value", "gpu_fan_rpm_value", "gpu_power_value"):
        label = getattr(page, name, None)
        if label is not None: label.setToolTip(explanation)
    status = getattr(page, "status", None)
    if status is not None and state == "failed":
        kind, reason = getattr(page, "gpu_read_failure", ("device", ""))
        template = "LACT-Dienst nicht erreichbar: {reason}" if kind == "inventory" else "GPU-Daten konnten nicht gelesen werden: {reason}"
        status.setText(page.tr(template).format(reason=reason))
    elif status is not None and state == "connected":
        status.setText(page.tr(connected_message(page)))


def set_state(page, state, *, kind="", reason=""):
    if state not in LABELS: state = "unknown"
    if state == "connected" and getattr(page, "gpu_read_state", "unknown") == "failed":
        page.gpu_read_failure_log = {}
    page.gpu_read_state = state
    if state == "failed": page.gpu_read_failure = (kind, str(reason))
    refresh(page)


def log_failure(page, kind, reason, *, now=None):
    """At most one identical stage/reason per ten seconds, with 16 bounded keys."""
    clean = redact_private_text(" ".join(str(reason).split()))[:300]
    stage = kind if kind in {"inventory", "device", "metrics"} else "read"
    key = (stage, clean)
    stamp = time.monotonic() if now is None else now
    previous = getattr(page, "gpu_read_failure_log", {})
    if key in previous and stamp - previous[key] < 10: return False
    previous[key] = stamp
    if len(previous) > 16:
        previous.pop(min(previous, key=previous.get))
    page.gpu_read_failure_log = previous
    if callable(getattr(page.host, "log_message", None)):
        page._gpu_log(f"GPU-LACT-FEHLER: Leseabfrage · {stage} · {clean}")
    return True
