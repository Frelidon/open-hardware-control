"""Public setup feature-selection API."""

from .model import FeatureChoice, feature_choices, normalize_selection

__all__ = ["FeatureChoice", "feature_choices", "normalize_selection"]
