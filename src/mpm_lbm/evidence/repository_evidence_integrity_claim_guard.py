"""Canonical repository claim-guard surface."""

from .._legacy import legacy_getattr

_LEGACY_MODULE = "src.repository_evidence_integrity_claim_guard"
__all__ = ("claim_guard_rows",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
