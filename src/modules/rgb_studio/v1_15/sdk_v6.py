# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure bounded SDK6 envelopes, based on the official OpenRGB SDK contract.

No hardware discovery or writes take place here. Controller indices used by
OHC's inventory are translated through the SDK6 controller-ID list, never used
as wire IDs directly. Source: Documentation/OpenRGBSDK.md and NetworkProtocol.h
in https://gitlab.com/CalcProgrammer1/OpenRGB (checked 2026-10-06).
"""

import struct

PACKET_ACK = 10
PACKET_SERVER_NAME = 51
PACKET_SERVER_FLAGS = 53
PACKET_SERVER_HOSTNAME = 55
PACKET_LIST_UPDATED = 100
PACKET_DETECTION_STARTED = 101
PACKET_DETECTION_PROGRESS = 102
PACKET_DETECTION_COMPLETE = 103
PACKET_ACTIVE_PROFILE_CHANGED = 157
PACKET_SIGNAL_UPDATE = 1150
MAX_PENDING_PACKETS = 64


def controller_ids(payload, maximum_count):
    if len(payload) < 4:
        raise ValueError("OpenRGB lieferte keine gültige Geräte-ID-Liste.")
    count = struct.unpack_from("<I", payload)[0]
    if count > maximum_count or len(payload) != 4 + count * 4:
        raise ValueError("OpenRGB lieferte keine gültige Geräte-ID-Liste.")
    ids = struct.unpack_from(f"<{count}I", payload, 4) if count else ()
    if len(set(ids)) != count:
        raise ValueError("OpenRGB meldet doppelte Geräte-IDs.")
    return ids


def ack_fields(payload):
    if len(payload) != 8:
        raise ValueError("Ungültige OpenRGB-SDK-Bestätigung.")
    packet_id, status = struct.unpack("<II", payload)
    if status:
        raise ValueError(f"OpenRGB-SDK-Auftrag {packet_id} wurde abgelehnt (Status {status}).")
    return packet_id


def notification(packet_type, payload):
    """Validate only documented unsolicited packets; unknown packets fail shut.

    Inventory/detection invalidation is handled by the caller, which must stop
    using every cached OHC-index to wire-ID mapping before another write.
    """
    if packet_type in {PACKET_SERVER_NAME, PACKET_SERVER_HOSTNAME}:
        if not 1 <= len(payload) <= 65536 or payload[-1:] != b"\0":
            raise ValueError("Ungültige OpenRGB-SDK-Serverkennung.")
        return True
    if packet_type == PACKET_SERVER_FLAGS:
        if len(payload) != 4:
            raise ValueError("Ungültige OpenRGB-SDK-Serverfähigkeiten.")
        return True
    if packet_type in {PACKET_LIST_UPDATED, PACKET_DETECTION_STARTED, PACKET_DETECTION_COMPLETE}:
        if payload:
            raise ValueError("Ungültige OpenRGB-SDK-Inventarmeldung.")
        return True
    if packet_type == PACKET_DETECTION_PROGRESS:
        if len(payload) < 10:
            raise ValueError("Ungültige OpenRGB-SDK-Erkennungsmeldung.")
        size, percentage, string_size = struct.unpack_from("<IIH", payload)
        if size != len(payload) or percentage > 100 or string_size != len(payload) - 10:
            raise ValueError("Ungültige OpenRGB-SDK-Erkennungsmeldung.")
        return True
    if packet_type == PACKET_ACTIVE_PROFILE_CHANGED:
        # OpenRGB 1.x may emit this documented ProfileManager callback while
        # another local client changes controller state.  OHC does not act on
        # profiles, but it must consume the complete callback before waiting
        # for the ACK belonging to its own RGB write.
        if not 1 <= len(payload) <= 65536 or payload[-1:] != b"\0":
            raise ValueError("Ungültige OpenRGB-SDK-Profilmeldung.")
        return True
    if packet_type == PACKET_SIGNAL_UPDATE:
        if len(payload) < 8 or struct.unpack_from("<I", payload)[0] != len(payload):
            raise ValueError("Ungültige OpenRGB-SDK-Aktualisierungsmeldung.")
        return True
    return False
