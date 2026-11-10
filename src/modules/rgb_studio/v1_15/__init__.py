"""RGB Studio 1.15 public helpers; pure render imports never construct Qt."""

from importlib import import_module

_EXPORTS = {
    "RGBDesignGallery": "design_gallery",
    "build_category_selector": "design_gallery",
    "GpuLightingMixin": "gpu_lighting",
    "gpu_mode_for_effect": "gpu_routing",
    "choose_control_path": "openrgb_backend",
    "split_control_paths": "openrgb_backend",
    "normalize_gpu_routes": "gpu_routing",
    "ENE_DRAM_POST_START_RETRY_DELAYS_MS": "ene_start_recovery",
    "EneDramStartRecoveryMixin": "ene_start_recovery",
    "RgbStudioExpandMixin": "studio_panels",
    "build_native_hardware_channel_panel": "studio_panels",
    "startup_profile_caption": "startup_status",
    "startup_status_summary": "startup_status",
    "ShutdownLightingMixin": "shutdown_lighting",
    "DesignTuningMixin": "design_tuning",
}
__all__ = tuple(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    value = getattr(import_module(f".{_EXPORTS[name]}", __name__), name)
    globals()[name] = value
    return value
