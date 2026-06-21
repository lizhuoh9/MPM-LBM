"""Canonical run-utils surface."""

from ..._legacy import legacy_getattr

_LEGACY_MODULE = "src.run_utils"
__all__ = ("ensure_dir", "write_json", "write_csv")


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
