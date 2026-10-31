"""GPU control module version 1.0."""

from .client import LactClient, LactError
MODULE_VERSION = "1.0"
__all__ = ["GpuControlPage", "LactClient", "LactError", "MODULE_VERSION"]


def __getattr__(name):
    if name == "GpuControlPage":
        from .page import GpuControlPage
        return GpuControlPage
    raise AttributeError(name)
