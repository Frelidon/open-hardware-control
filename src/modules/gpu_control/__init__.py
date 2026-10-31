"""GPU control integration backed by the external LACT daemon."""

__all__ = ["GpuControlPage", "LactClient"]


def __getattr__(name):
    if name not in __all__:
        raise AttributeError(name)
    from . import v1_0
    return getattr(v1_0, name)
