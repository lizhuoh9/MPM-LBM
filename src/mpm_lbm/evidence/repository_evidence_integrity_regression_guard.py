"""Canonical repository evidence regression-guard surface."""

from .._legacy import legacy_getattr

_LEGACY_MODULE = "src.repository_evidence_integrity_regression_guard"
__all__ = ("step53_regression_rows",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
