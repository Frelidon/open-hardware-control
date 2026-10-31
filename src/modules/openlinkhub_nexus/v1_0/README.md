# OpenLinkHub Nexus bridge 1.0

This module imports bounded local artwork and optional Schema-1 touch manifests
into an existing OpenLinkHub user installation. It accepts no arbitrary target
path outside the user's home, resizes artwork to 640×48, backs up `nexus.json`
and replaces files atomically. It never opens a Corsair USB device.

Generic profiles support static backgrounds and OpenLinkHub's existing action
codes. New dynamic widgets require implementation in OpenLinkHub itself.

OpenLinkHub 0.9.2 uses `touchPositionMax` (lower-case) and inclusive 0–639
touch ranges. The earlier OHC manifest spelling remains accepted on import,
but export follows upstream exactly. Unique temporary/backup files and rejection
of linked database directories protect the atomic import. API mutations require
OpenLinkHub's explicit `status=1`; HTTP 200 alone is not a success acknowledgement.
