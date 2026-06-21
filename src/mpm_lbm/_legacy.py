"""Lazy compatibility helpers for Step 55 package-boundary wrappers."""

from importlib import import_module


def legacy_getattr(module_name: str, allowed_names: tuple[str, ...], name: str):
    if name not in allowed_names:
        raise AttributeError(f"{module_name!r} wrapper has no attribute {name!r}")
    module = import_module(module_name)
    return getattr(module, name)
