"""Public TRCC Linux installer integration."""

def install_trcc(*args, **kwargs):
    # CLI/runtime metadata integration must not import Qt widgets.
    from .installer import install_trcc as install
    return install(*args, **kwargs)

__all__ = ["install_trcc"]
