"""Canonical repository test-strength audit surface."""

from .._legacy import legacy_getattr

_LEGACY_MODULE = "src.repository_test_strength_audit"
__all__ = (
    "ALLOWED_TEST_STRENGTH_LEVELS",
    "PYTEST_RESULT_INTERPRETATION",
    "build_repository_test_strength_audit",
)


def __getattr__(name):
    return legacy_getattr(_LEGACY_MODULE, __all__, name)
