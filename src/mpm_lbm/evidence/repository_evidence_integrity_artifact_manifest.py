"""Canonical repository evidence artifact-manifest surface."""

from .._legacy import legacy_getattr

_LEGACY_MODULE = "src.repository_evidence_integrity_artifact_manifest"
__all__ = ("build_step54_artifact_manifest",)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
