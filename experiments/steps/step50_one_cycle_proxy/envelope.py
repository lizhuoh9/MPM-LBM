"""Canonical Step 50 one-cycle proxy envelope surface."""

from src.mpm_lbm._legacy import legacy_getattr

_LEGACY_MODULE = "src.runtime_geometry_wall_velocity_one_cycle_envelope"
__all__ = ("run_one_cycle_envelope_matrix", "summarize_one_cycle_envelope_matrix", "write_one_cycle_envelope_rows")


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
