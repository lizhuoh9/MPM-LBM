import csv
import json
import os
import re
from pathlib import Path

from .geometry_fingerprint import fingerprint_geometry_file


VALID_GEOMETRY_TYPES = {"mesh", "voxel"}
VALID_COMMIT_POLICIES = {
    "small_controlled_fixture_allowed",
    "do_not_commit_large_raw_geometry",
    "local_candidate_only",
}
VALIDATION_SCOPE = "intake_qa_normalization_sampling_projection_only"
LOCAL_ONLY_POLICIES = {"local_candidate_only", "do_not_commit_large_raw_geometry"}

MANIFEST_FIELDS = [
    "candidate_id",
    "geometry_type",
    "descriptor_path",
    "source_file",
    "source_file_redacted",
    "source_policy",
    "license_status",
    "commit_policy",
    "validation_scope",
    "n_particles",
    "normalize_to_domain",
    "preserve_aspect_ratio",
    "padding",
    "quality_check_enabled",
    "quality_check_strict",
    "size_bytes",
    "sha256",
    "is_large",
    "manifest_pass",
    "notes",
]


def load_candidate_descriptor(path) -> dict:
    resolved = _resolve_path(path, root=None)
    with resolved.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"candidate descriptor must be a JSON object: {path}")
    return payload


def validate_candidate_descriptor(payload, *, descriptor_path=None) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("candidate descriptor must be a dict")

    normalized = dict(payload)
    required = [
        "candidate_id",
        "geometry_type",
        "source_file",
        "source_policy",
        "license_status",
        "commit_policy",
        "normalize_to_domain",
        "preserve_aspect_ratio",
        "padding",
        "n_particles",
        "quality_check_enabled",
        "quality_check_strict",
        "artifact_policy",
        "validation_scope",
    ]
    missing = [key for key in required if key not in normalized]
    if missing:
        raise ValueError(f"candidate descriptor missing fields {missing}: {descriptor_path}")

    candidate_id = str(normalized["candidate_id"])
    if not candidate_id or not re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", candidate_id):
        raise ValueError(f"candidate_id must be lowercase snake case: {candidate_id!r}")
    forbidden_identity_terms = ("validated", "swimming", "actuation", "anatomical")
    if any(term in candidate_id for term in forbidden_identity_terms):
        raise ValueError(f"candidate_id must not imply validation or anatomy: {candidate_id!r}")

    geometry_type = str(normalized["geometry_type"])
    if geometry_type not in VALID_GEOMETRY_TYPES:
        raise ValueError(f"geometry_type must be one of {sorted(VALID_GEOMETRY_TYPES)}")

    commit_policy = str(normalized["commit_policy"])
    if commit_policy not in VALID_COMMIT_POLICIES:
        raise ValueError(f"commit_policy must be one of {sorted(VALID_COMMIT_POLICIES)}")

    if str(normalized["validation_scope"]) != VALIDATION_SCOPE:
        raise ValueError(f"validation_scope must be {VALIDATION_SCOPE!r}")
    if normalized["quality_check_enabled"] is not True:
        raise ValueError("quality_check_enabled must be true")
    if normalized["quality_check_strict"] is not True:
        raise ValueError("quality_check_strict must be true")

    n_particles = int(normalized["n_particles"])
    if n_particles <= 0:
        raise ValueError("n_particles must be positive")
    normalized["n_particles"] = n_particles

    padding = float(normalized["padding"])
    if padding < 0.0 or padding >= 0.5:
        raise ValueError("padding must satisfy 0 <= padding < 0.5")
    normalized["padding"] = padding

    source_file = str(normalized["source_file"])
    if not source_file:
        raise ValueError("source_file must be non-empty")
    source_path_text = source_file.replace("\\", "/")
    if "external/taichi_LBM3D" in source_path_text:
        raise ValueError("source_file must not point under external/taichi_LBM3D")
    if _looks_absolute_private_path(source_file) and commit_policy != "local_candidate_only":
        raise ValueError("absolute source_file paths require local_candidate_only commit_policy")

    source_available = bool(normalized.get("source_available", True))
    if source_available is False and commit_policy not in LOCAL_ONLY_POLICIES:
        raise ValueError("unavailable sources must be marked local_candidate_only or do_not_commit_large_raw_geometry")
    normalized["source_available"] = source_available
    return normalized


def candidate_manifest_row(descriptor_path, *, root=None) -> dict:
    root_path = Path(root).resolve() if root is not None else _repo_root()
    descriptor = validate_candidate_descriptor(load_candidate_descriptor(descriptor_path), descriptor_path=descriptor_path)

    descriptor_abs = _resolve_path(descriptor_path, root=root_path)
    source_abs = _resolve_path(descriptor["source_file"], root=root_path)
    notes = []
    size_bytes = 0
    sha256 = ""
    is_large = False
    source_redacted = "<unavailable local candidate>"

    if source_abs.exists():
        fingerprint = fingerprint_geometry_file(source_abs, root=root_path, redact_absolute=True)
        source_redacted = fingerprint["path"]
        size_bytes = int(fingerprint["size_bytes"])
        sha256 = fingerprint["sha256"]
        is_large = bool(fingerprint["is_large"])
    elif descriptor["source_available"] is False:
        notes.append("source unavailable by local-only descriptor policy")
    else:
        raise FileNotFoundError(f"candidate source file is missing: {descriptor['source_file']}")

    if is_large and descriptor["commit_policy"] == "small_controlled_fixture_allowed":
        raise ValueError(f"committed smoke fixture is too large: {descriptor['source_file']}")
    if _looks_absolute_private_path(str(descriptor["source_file"])):
        notes.append("source path redacted from committed manifest output")
    if not notes:
        notes.append("manifest checks passed")

    return {
        "candidate_id": descriptor["candidate_id"],
        "geometry_type": descriptor["geometry_type"],
        "descriptor_path": descriptor_abs.relative_to(root_path).as_posix(),
        "source_file": source_redacted,
        "source_file_redacted": source_redacted,
        "source_policy": descriptor["source_policy"],
        "license_status": descriptor["license_status"],
        "commit_policy": descriptor["commit_policy"],
        "validation_scope": descriptor["validation_scope"],
        "n_particles": int(descriptor["n_particles"]),
        "normalize_to_domain": bool(descriptor["normalize_to_domain"]),
        "preserve_aspect_ratio": bool(descriptor["preserve_aspect_ratio"]),
        "padding": float(descriptor["padding"]),
        "quality_check_enabled": bool(descriptor["quality_check_enabled"]),
        "quality_check_strict": bool(descriptor["quality_check_strict"]),
        "size_bytes": int(size_bytes),
        "sha256": sha256,
        "is_large": bool(is_large),
        "manifest_pass": True,
        "notes": "; ".join(notes),
    }


def write_candidate_manifest(rows, csv_path, json_path):
    _check_unique_candidate_ids(rows)
    _write_csv(rows, csv_path, MANIFEST_FIELDS)
    _write_json(json_path, {"row_count": len(rows), "rows": rows})


def _check_unique_candidate_ids(rows):
    ids = [row["candidate_id"] for row in rows]
    duplicates = sorted({candidate_id for candidate_id in ids if ids.count(candidate_id) > 1})
    if duplicates:
        raise ValueError(f"duplicate candidate_id values: {duplicates}")


def _looks_absolute_private_path(path: str) -> bool:
    text = path.replace("\\", "/")
    return Path(path).is_absolute() or bool(re.match(r"^[A-Za-z]:/", text))


def _resolve_path(path, *, root=None) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj.resolve()
    base = root if root is not None else _repo_root()
    return (Path(base) / path_obj).resolve()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _write_csv(rows, path, fieldnames):
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with path_obj.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _write_json(path, data):
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with path_obj.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
