import hashlib
import os
from pathlib import Path


def sha256_file(path) -> str:
    resolved = _require_file(path)
    digest = hashlib.sha256()
    with resolved.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_size_bytes(path) -> int:
    resolved = _require_file(path)
    return int(resolved.stat().st_size)


def fingerprint_geometry_file(path, *, root=None, redact_absolute=True, large_threshold_bytes=1_000_000) -> dict:
    resolved = _require_file(path)
    if int(large_threshold_bytes) < 0:
        raise ValueError("large_threshold_bytes must be non-negative")

    root_path = Path(root).resolve() if root is not None else None
    display_path, path_policy = _display_path(resolved, root_path, bool(redact_absolute))
    size_bytes = file_size_bytes(resolved)
    return {
        "path": display_path,
        "filename": resolved.name,
        "extension": resolved.suffix.lower(),
        "size_bytes": size_bytes,
        "sha256": sha256_file(resolved),
        "is_large": bool(size_bytes >= int(large_threshold_bytes)),
        "path_policy": path_policy,
        "mtime_policy_note": "mtime excluded from fingerprint; content hash and exact size define identity",
    }


def _require_file(path) -> Path:
    resolved = Path(os.fspath(path)).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"geometry file does not exist: {path}")
    if not resolved.is_file():
        raise ValueError(f"geometry path is not a file: {path}")
    return resolved


def _display_path(path: Path, root: Path | None, redact_absolute: bool) -> tuple[str, str]:
    if root is not None:
        try:
            return path.relative_to(root).as_posix(), "repo_relative"
        except ValueError:
            pass
    if path.is_absolute() and redact_absolute:
        return f"<redacted>/{path.name}", "absolute_redacted"
    if path.is_absolute():
        return path.as_posix(), "absolute_unredacted"
    return path.as_posix(), "relative"
