import json
import math
from pathlib import Path

import numpy as np

from .geometry_candidate_manifest import validate_candidate_descriptor
from .geometry_config import GeometryConfig
from .geometry_fingerprint import fingerprint_geometry_file
from .mesh_io import load_obj, mesh_bounds, normalize_vertices
from .voxel_io import load_voxel_geometry


def normalize_mesh_candidate(descriptor) -> dict:
    payload = validate_candidate_descriptor(descriptor)
    if payload["geometry_type"] != "mesh":
        raise ValueError("normalize_mesh_candidate requires geometry_type='mesh'")

    config = geometry_config_from_descriptor(payload)
    vertices, _ = load_obj(config.geometry_file)
    source_min, source_max = mesh_bounds(vertices)
    normalized = normalize_vertices(
        vertices,
        domain_min=config.domain_min,
        domain_max=config.domain_max,
        padding=config.padding,
        preserve_aspect_ratio=config.preserve_aspect_ratio,
    )
    normalized_min, normalized_max = mesh_bounds(normalized)
    scale_factor, translation = _fit_transform(
        source_min,
        source_max,
        np.asarray(config.domain_min, dtype=np.float64),
        np.asarray(config.domain_max, dtype=np.float64),
        config.padding,
        bool(config.preserve_aspect_ratio),
    )
    return _report(
        payload,
        source_file=config.geometry_file,
        source_bounds_min=source_min,
        source_bounds_max=source_max,
        normalized_bounds_min=normalized_min,
        normalized_bounds_max=normalized_max,
        domain_min=config.domain_min,
        domain_max=config.domain_max,
        scale_factor=scale_factor,
        translation=translation,
        normalization_changed_coordinates=not np.allclose(vertices, normalized),
        notes="mesh coordinates normalized in memory for intake reporting only; no repair or remeshing",
    )


def normalize_voxel_candidate(descriptor) -> dict:
    payload = validate_candidate_descriptor(descriptor)
    if payload["geometry_type"] != "voxel":
        raise ValueError("normalize_voxel_candidate requires geometry_type='voxel'")

    config = geometry_config_from_descriptor(payload)
    voxel = load_voxel_geometry(config.geometry_file, metadata_path=config.metadata_file, threshold=config.voxel_threshold)
    occupied = np.argwhere(voxel.occupancy)
    shape = np.asarray(voxel.occupancy.shape, dtype=np.float64)
    source_min = occupied.min(axis=0).astype(np.float64)
    source_max = (occupied.max(axis=0) + 1).astype(np.float64)
    normalized_min = source_min / shape
    normalized_max = source_max / shape
    return _report(
        payload,
        source_file=config.geometry_file,
        source_bounds_min=source_min,
        source_bounds_max=source_max,
        normalized_bounds_min=normalized_min,
        normalized_bounds_max=normalized_max,
        domain_min=config.domain_min,
        domain_max=config.domain_max,
        scale_factor=1.0,
        translation=[0.0, 0.0, 0.0],
        normalization_changed_coordinates=False,
        notes="voxel candidate normalization records occupancy-to-domain mapping only; source .npy is unchanged",
    )


def write_normalization_report(report, path):
    _assert_report(report)
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with path_obj.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")


def geometry_config_from_descriptor(descriptor) -> GeometryConfig:
    payload = validate_candidate_descriptor(descriptor)
    values = {
        "geometry_type": payload["geometry_type"],
        "n_particles": int(payload["n_particles"]),
        "geometry_file": payload["source_file"],
        "normalize_to_domain": bool(payload["normalize_to_domain"]),
        "preserve_aspect_ratio": bool(payload["preserve_aspect_ratio"]),
        "padding": float(payload["padding"]),
        "quality_check_enabled": bool(payload["quality_check_enabled"]),
        "quality_check_strict": bool(payload["quality_check_strict"]),
        "deterministic": True,
    }
    if payload["geometry_type"] == "voxel":
        values["metadata_file"] = payload.get("metadata_file")
        values["voxel_threshold"] = float(payload.get("voxel_threshold", 0.5))
    if payload["geometry_type"] == "mesh":
        values["mesh_inside_method"] = payload.get("mesh_inside_method", "ray_cast")
        values["mesh_voxel_resolution"] = int(payload.get("mesh_voxel_resolution", 32))
    return GeometryConfig(**values)


def _report(
    descriptor,
    *,
    source_file,
    source_bounds_min,
    source_bounds_max,
    normalized_bounds_min,
    normalized_bounds_max,
    domain_min,
    domain_max,
    scale_factor,
    translation,
    normalization_changed_coordinates,
    notes,
) -> dict:
    report = {
        "candidate_id": descriptor["candidate_id"],
        "geometry_type": descriptor["geometry_type"],
        "source_file_fingerprint": fingerprint_geometry_file(source_file, root=_repo_root(), redact_absolute=True),
        "source_bounds_min": _float_list(source_bounds_min),
        "source_bounds_max": _float_list(source_bounds_max),
        "normalized_bounds_min": _float_list(normalized_bounds_min),
        "normalized_bounds_max": _float_list(normalized_bounds_max),
        "domain_min": _float_list(domain_min),
        "domain_max": _float_list(domain_max),
        "padding": float(descriptor["padding"]),
        "preserve_aspect_ratio": bool(descriptor["preserve_aspect_ratio"]),
        "scale_factor": _finite_float(scale_factor, "scale_factor"),
        "translation": _float_list(translation),
        "normalized_inside_domain": _inside_domain(normalized_bounds_min, normalized_bounds_max, domain_min, domain_max),
        "normalization_changed_coordinates": bool(normalization_changed_coordinates),
        "source_file_modified": False,
        "repair_performed": False,
        "remeshing_performed": False,
        "notes": notes,
    }
    _assert_report(report)
    return report


def _fit_transform(source_min, source_max, domain_min, domain_max, padding, preserve_aspect_ratio):
    source_span = source_max - source_min
    inner_min = domain_min + float(padding) * (domain_max - domain_min)
    inner_max = domain_max - float(padding) * (domain_max - domain_min)
    inner_span = inner_max - inner_min
    if preserve_aspect_ratio:
        scale = float(np.min(inner_span / source_span))
        used_span = source_span * scale
        offset = inner_min + 0.5 * (inner_span - used_span)
        translation = offset - source_min * scale
        return scale, translation
    scale_vector = inner_span / source_span
    translation = inner_min - source_min * scale_vector
    return float(np.mean(scale_vector)), translation


def _assert_report(report):
    if report["normalized_inside_domain"] is not True:
        raise ValueError("normalized geometry must stay inside the configured domain")
    for key in ("scale_factor", "padding"):
        _finite_float(report[key], key)
    _float_list(report["translation"])
    if report["source_file_modified"] is not False:
        raise ValueError("normalization must not modify the source file")
    if report["repair_performed"] is not False:
        raise ValueError("normalization must not perform mesh repair")
    if report["remeshing_performed"] is not False:
        raise ValueError("normalization must not perform remeshing")


def _inside_domain(bounds_min, bounds_max, domain_min, domain_max) -> bool:
    bmin = np.asarray(bounds_min, dtype=np.float64)
    bmax = np.asarray(bounds_max, dtype=np.float64)
    dmin = np.asarray(domain_min, dtype=np.float64)
    dmax = np.asarray(domain_max, dtype=np.float64)
    return bool(np.all(bmin >= dmin - 1.0e-8) and np.all(bmax <= dmax + 1.0e-8))


def _float_list(values) -> list[float]:
    arr = np.asarray(values, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise ValueError("normalization report values must be finite")
    return [float(v) for v in arr.tolist()]


def _finite_float(value, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
