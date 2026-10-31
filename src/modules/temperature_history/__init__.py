"""Current in-memory temperature history module."""

from . import v1_2
__all__ = v1_2.__all__


def __getattr__(name):
    return getattr(v1_2, name)
