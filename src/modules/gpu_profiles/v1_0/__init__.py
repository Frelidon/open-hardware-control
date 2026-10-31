"""Safe local GPU profiles for the LACT-backed GPU page."""

from .catalog import GPU_MODELS, detect_model, model_by_id
from .model import (
    PRESENTATION_MAXIMIZED,
    append_or_replace_profile,
    config_digest,
    load_profiles,
    normalize_presentation,
    normalize_profile,
    remove_profile,
    save_profiles,
    zero_rpm_state,
)

__all__ = [
    "GPU_MODELS", "PRESENTATION_MAXIMIZED", "append_or_replace_profile",
    "config_digest", "detect_model", "load_profiles", "model_by_id",
    "normalize_presentation", "normalize_profile", "remove_profile",
    "save_profiles", "zero_rpm_state",
]
