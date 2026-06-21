"""Canonical proxy-diagnostic truthfulness surface."""

from .._legacy import legacy_getattr

_LEGACY_MODULE = "src.proxy_diagnostic_truthfulness"
__all__ = (
    "PROXY_RECORD_METADATA",
    "add_proxy_record_metadata",
    "add_proxy_step_metadata",
    "proxy_metadata_fields",
    "proxy_metadata_present",
)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
