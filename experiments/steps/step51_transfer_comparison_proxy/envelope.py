"""Canonical Step 51 transfer comparison proxy envelope surface."""

from src.mpm_lbm._legacy import legacy_getattr

_LEGACY_MODULE = "src.runtime_geometry_wall_velocity_transfer_envelope"
__all__ = ("run_transfer_comparison_matrix", "summarize_transfer_comparison_matrix", "write_transfer_envelope_outputs")


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
