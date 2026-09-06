#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small, dependency-free request coordinators for OHC hardware ownership.

The coordinator deliberately does not talk to USB itself.  It gives every
high-level hardware intent a monotonically increasing request id, records
ownership transitions and makes "latest request wins" decisions explicit.
The GUI can therefore keep the proven liquidctl/CAM-raw transports while
having one auditable state machine above them.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, replace
from enum import IntEnum
from typing import Callable


class RequestPriority(IntEnum):
    BACKGROUND = 10
    NORMAL = 30
    HIGH = 60
    CRITICAL = 100


@dataclass(frozen=True)
class HardwareRequest:
    request_id: int
    domain: str
    action: str
    priority: RequestPriority
    replace_key: str
    created_at: float
    state: str = "pending"
    owner: str = ""
    finished_at: float = 0.0
    detail: str = ""

    @property
    def elapsed_ms(self) -> int:
        end = self.finished_at or time.monotonic()
        return max(0, round((end - self.created_at) * 1000))


class HardwareRequestCoordinator:
    """Track serialized hardware intents and stale/replaced requests.

    ``replace_key`` is the important bit for UI actions.  A new LCD design can
    immediately supersede the previous LCD-design request without affecting a
    CRITICAL shutdown request or a pump write in another domain.
    """

    def __init__(self, name: str, logger: Callable[[str], None] | None = None) -> None:
        self.name = str(name).strip() or "HW-COORD"
        self._logger = logger
        self._next_id = 1
        self._requests: dict[int, HardwareRequest] = {}
        self._latest_by_key: dict[str, int] = {}
        self._owner = "idle"
        self._owner_request_id = 0
        self._errors = 0
        self._retries = 0
        self._superseded = 0

    def set_logger(self, logger: Callable[[str], None] | None) -> None:
        self._logger = logger

    def _log(self, message: str) -> None:
        if self._logger is not None:
            self._logger(f"{self.name}: {message}")

    def request(
        self,
        domain: str,
        action: str,
        *,
        priority: RequestPriority = RequestPriority.NORMAL,
        replace_key: str = "",
        detail: str = "",
    ) -> HardwareRequest:
        request_id = self._next_id
        self._next_id += 1
        key = str(replace_key).strip()
        if key:
            previous_id = self._latest_by_key.get(key, 0)
            previous = self._requests.get(previous_id)
            if previous is not None and previous.state in {"pending", "running", "paused"}:
                previous = replace(
                    previous,
                    state="superseded",
                    finished_at=time.monotonic(),
                    detail=f"durch Request #{request_id} ersetzt",
                )
                self._requests[previous_id] = previous
                self._superseded += 1
                self._log(
                    f"Request #{previous_id} verworfen · neuerer Request #{request_id} · Schlüssel {key}"
                )
            self._latest_by_key[key] = request_id
        req = HardwareRequest(
            request_id=request_id,
            domain=str(domain)[:48],
            action=str(action)[:160],
            priority=RequestPriority(priority),
            replace_key=key,
            created_at=time.monotonic(),
            detail=str(detail)[:300],
        )
        self._requests[request_id] = req
        suffix = f" · {detail}" if detail else ""
        self._log(
            f"Request #{request_id} · {req.domain} · {req.action} · Priorität {req.priority.name}{suffix}"
        )
        self._trim()
        return req

    def current(self, request_id: int) -> HardwareRequest | None:
        return self._requests.get(int(request_id))

    def is_current(self, request_id: int) -> bool:
        req = self._requests.get(int(request_id))
        if req is None or req.state in {"superseded", "cancelled", "failed", "done"}:
            return False
        return not req.replace_key or self._latest_by_key.get(req.replace_key) == req.request_id

    def begin(self, request_id: int, owner: str) -> bool:
        if not self.is_current(request_id):
            return False
        req = self._requests[int(request_id)]
        req = replace(req, state="running", owner=str(owner)[:80])
        self._requests[req.request_id] = req
        self._owner = req.owner or req.domain
        self._owner_request_id = req.request_id
        self._log(f"Besitzer → {self._owner} · Request #{req.request_id}")
        return True

    def pause(self, request_id: int, detail: str = "") -> None:
        req = self._requests.get(int(request_id))
        if req is None or req.state not in {"running", "pending"}:
            return
        self._requests[req.request_id] = replace(req, state="paused", detail=str(detail)[:300])
        self._log(f"Request #{req.request_id} pausiert" + (f" · {detail}" if detail else ""))

    def retry(self, request_id: int, detail: str = "") -> None:
        req = self._requests.get(int(request_id))
        if req is None:
            return
        self._retries += 1
        self._log(f"Request #{req.request_id} Wiederholungsversuch" + (f" · {detail}" if detail else ""))

    def complete(self, request_id: int, detail: str = "") -> None:
        req = self._requests.get(int(request_id))
        if req is None:
            return
        if req.state == "superseded":
            return
        req = replace(req, state="done", finished_at=time.monotonic(), detail=str(detail)[:300])
        self._requests[req.request_id] = req
        if self._owner_request_id == req.request_id:
            self._owner = "idle"
            self._owner_request_id = 0
        suffix = f" · {detail}" if detail else ""
        self._log(f"Request #{req.request_id} abgeschlossen · {req.elapsed_ms} ms{suffix}")

    def fail(self, request_id: int, detail: str) -> None:
        req = self._requests.get(int(request_id))
        if req is None:
            return
        self._errors += 1
        req = replace(req, state="failed", finished_at=time.monotonic(), detail=str(detail)[:300])
        self._requests[req.request_id] = req
        if self._owner_request_id == req.request_id:
            self._owner = "idle"
            self._owner_request_id = 0
        self._log(f"FEHLER · Request #{req.request_id} · {detail}")

    def cancel(self, request_id: int, detail: str = "") -> None:
        req = self._requests.get(int(request_id))
        if req is None or req.state in {"done", "failed", "cancelled", "superseded"}:
            return
        req = replace(req, state="cancelled", finished_at=time.monotonic(), detail=str(detail)[:300])
        self._requests[req.request_id] = req
        if self._owner_request_id == req.request_id:
            self._owner = "idle"
            self._owner_request_id = 0
        self._log(f"Request #{req.request_id} abgebrochen" + (f" · {detail}" if detail else ""))

    def claim_owner(self, owner: str, *, request_id: int = 0, detail: str = "") -> None:
        self._owner = str(owner).strip()[:80] or "unknown"
        self._owner_request_id = int(request_id) if request_id else 0
        suffix = f" · {detail}" if detail else ""
        ref = f" · Request #{request_id}" if request_id else ""
        self._log(f"Besitzer → {self._owner}{ref}{suffix}")

    def release_owner(self, owner: str = "", *, detail: str = "") -> None:
        if owner and self._owner != owner:
            return
        previous = self._owner
        self._owner = "idle"
        self._owner_request_id = 0
        suffix = f" · {detail}" if detail else ""
        if previous != "idle":
            self._log(f"Besitzer freigegeben · {previous}{suffix}")

    def status(self) -> dict[str, object]:
        active = [req for req in self._requests.values() if req.state in {"pending", "running", "paused"}]
        return {
            "owner": self._owner,
            "owner_request_id": self._owner_request_id,
            "active": len(active),
            "errors": self._errors,
            "retries": self._retries,
            "superseded": self._superseded,
            "latest_request_id": self._next_id - 1,
        }

    def _trim(self) -> None:
        if len(self._requests) <= 256:
            return
        keep_ids = set(sorted(self._requests)[-192:])
        self._requests = {rid: req for rid, req in self._requests.items() if rid in keep_ids}


class KrakenUsbCoordinator(HardwareRequestCoordinator):
    def __init__(self, logger: Callable[[str], None] | None = None) -> None:
        super().__init__("USB-COORD", logger)


class RgbRequestCoordinator(HardwareRequestCoordinator):
    def __init__(self, logger: Callable[[str], None] | None = None) -> None:
        super().__init__("RGB-COORD", logger)
