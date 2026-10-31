"""Public distribution-aware NCT6687/DKMS/MOK setup API."""

from .dialog import show_nct6687_setup_assistant
from .distribution import DistributionInfo, SetupPlan, detect_distribution, setup_plan
from .model import MokStatus, inspect_mok_status, privileged_terminal_spec

__all__ = [
    "DistributionInfo", "MokStatus", "SetupPlan", "detect_distribution",
    "inspect_mok_status", "privileged_terminal_spec", "setup_plan",
    "show_nct6687_setup_assistant",
]
