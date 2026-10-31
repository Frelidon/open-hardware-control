"""Official backend release checks for the About page."""

from .policy import collect_backend_updates, version_is_newer

__all__ = ["BackendUpdatesMixin", "collect_backend_updates", "version_is_newer"]


def __getattr__(name):
    if name == "BackendUpdatesMixin":
        from .controller import BackendUpdatesMixin
        return BackendUpdatesMixin
    raise AttributeError(name)
