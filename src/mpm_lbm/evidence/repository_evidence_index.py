"""Canonical repository evidence index surface."""

from .._legacy import legacy_getattr

_LEGACY_MODULE = "src.repository_evidence_index"
__all__ = ("build_repository_evidence_index",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
