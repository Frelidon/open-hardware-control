"""Public API for bounded TRCC daemon health and recovery checks."""

from .model import (
    DAEMON_HEALTH_INTERVAL_MS,
    DAEMON_RECOVERY_COOLDOWN_SECONDS,
    PLAYBACK_HEALTH_INTERVAL_MS,
    PLAYBACK_RECOVERY_COOLDOWN_SECONDS,
    DAEMON_RSS_LIMIT_BYTES,
    DaemonMemorySample,
    daemon_memory_exceeded,
    find_trcc_daemon_memory,
    is_probable_daemon_failure,
    is_owned_trcc_daemon_pid,
    is_trcc_daemon_command,
    replacement_owned_trcc_pid,
    signal_trcc_daemon,
)
from .playback import (
    PlaybackHealth,
    PlaybackRecoveryPolicy,
    parse_playback_status,
    parse_video_playback_status,
    recent_trcc_cause,
)

__all__ = [
    "DAEMON_HEALTH_INTERVAL_MS",
    "DAEMON_RECOVERY_COOLDOWN_SECONDS",
    "PLAYBACK_HEALTH_INTERVAL_MS",
    "PLAYBACK_RECOVERY_COOLDOWN_SECONDS",
    "DAEMON_RSS_LIMIT_BYTES",
    "DaemonMemorySample",
    "daemon_memory_exceeded",
    "find_trcc_daemon_memory",
    "is_probable_daemon_failure",
    "is_owned_trcc_daemon_pid",
    "is_trcc_daemon_command",
    "replacement_owned_trcc_pid",
    "signal_trcc_daemon",
    "PlaybackHealth",
    "PlaybackRecoveryPolicy",
    "parse_playback_status",
    "parse_video_playback_status",
    "recent_trcc_cause",
]
