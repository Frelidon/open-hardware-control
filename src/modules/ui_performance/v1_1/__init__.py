"""Public UI-performance and bounded SSD-cache API."""

from .cache import (
    cache_budget_mb,
    cached_catalog_records,
    preview_cache_path,
    save_catalog_records,
)
from .controller import build_performance_settings, install_ui_performance
from .memory import ReclaimResult, release_idle_memory

__all__ = [
    "build_performance_settings",
    "cache_budget_mb",
    "cached_catalog_records",
    "install_ui_performance",
    "preview_cache_path",
    "ReclaimResult",
    "release_idle_memory",
    "save_catalog_records",
]
