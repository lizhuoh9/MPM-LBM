"""Canonical state-guard truthfulness surface."""

from .._legacy import legacy_getattr

_LEGACY_MODULE = "src.state_guard_truthfulness"
__all__ = (
    "STATE_GUARD_METHOD_METADATA",
    "FIXED_ZERO_STATE_FIELDS",
    "add_state_guard_truthfulness_metadata",
    "state_guard_truthfulness_rows",
)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
