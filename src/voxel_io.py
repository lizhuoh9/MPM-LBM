from dataclasses import dataclass
import json
import os

import numpy as np


@dataclass(frozen=True)
class VoxelGeometry:
    occupancy: np.ndarray
    metadata: dict
    stats: dict


def load_voxel_geometry(path, metadata_path=None, threshold=0.5):
    resolved_path = _resolve_path(path)
    if not resolved_path.lower().endswith(".npy"):
        raise ValueError("Step 20 voxel import supports .npy occupancy files")

    raw = np.load(resolved_path)
    occupancy = _as_occupancy(raw, threshold)
    metadata = _load_metadata(metadata_path)
    stats = _voxel_stats(occupancy, metadata)
    return VoxelGeometry(occupancy=occupancy, metadata=metadata, stats=stats)


def save_voxel_geometry(path, occupancy, metadata_path=None, metadata=None):
    resolved_path = _resolve_path(path)
    os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
    occ = _as_occupancy(occupancy, threshold=0.5)
    np.save(resolved_path, occ.astype(np.uint8))

    if metadata_path is not None:
        resolved_metadata = _resolve_path(metadata_path)
        os.makedirs(os.path.dirname(resolved_metadata), exist_ok=True)
        with open(resolved_metadata, "w", encoding="utf-8") as f:
            json.dump(metadata or {}, f, indent=2, sort_keys=True)
            f.write("\n")


def voxel_centers_to_points(occupancy, domain_min=(0, 0, 0), domain_max=(1, 1, 1)):
    occ = _as_occupancy(occupancy, threshold=0.5)
    domain_min = _as_vec3(domain_min, "domain_min")
    domain_max = _as_vec3(domain_max, "domain_max")
    if np.any(domain_min >= domain_max):
        raise ValueError("domain_min must be smaller than domain_max in every dimension")

    idx = np.argwhere(occ)
    if len(idx) == 0:
        return np.empty((0, 3), dtype=np.float32)

    shape = np.asarray(occ.shape, dtype=np.float64)
    normalized = (idx.astype(np.float64) + 0.5) / shape[None, :]
    points = domain_min[None, :] + normalized * (domain_max - domain_min)[None, :]
    return points.astype(np.float32)


def _as_occupancy(values, threshold):
    arr = np.asarray(values)
    if arr.ndim != 3:
        raise ValueError("occupancy must be a 3D array")
    if not np.all(np.isfinite(arr)):
        raise ValueError("occupancy must be finite")
    if arr.dtype == np.bool_:
        occupancy = arr.astype(bool)
    else:
        occupancy = arr.astype(np.float64) >= float(threshold)
    if int(np.count_nonzero(occupancy)) <= 0:
        raise ValueError("occupancy must contain at least one occupied voxel")
    return occupancy


def _voxel_stats(occupancy, metadata):
    occupied = np.argwhere(occupancy)
    occupied_count = int(len(occupied))
    bounds_min = occupied.min(axis=0).astype(int).tolist()
    bounds_max = occupied.max(axis=0).astype(int).tolist()
    domain_min = metadata.get("domain_min", [0.0, 0.0, 0.0])
    domain_max = metadata.get("domain_max", [1.0, 1.0, 1.0])
    voxel_order = metadata.get("voxel_order", "ijk")
    return {
        "shape": [int(v) for v in occupancy.shape],
        "occupied_count": occupied_count,
        "occupied_fraction": float(occupied_count / occupancy.size),
        "bounds_index_min": bounds_min,
        "bounds_index_max": bounds_max,
        "domain_min": [float(v) for v in domain_min],
        "domain_max": [float(v) for v in domain_max],
        "voxel_order": voxel_order,
    }


def _load_metadata(metadata_path):
    if metadata_path is None:
        return {
            "source": "unspecified",
            "description": "",
            "domain_min": [0.0, 0.0, 0.0],
            "domain_max": [1.0, 1.0, 1.0],
            "voxel_order": "ijk",
        }
    resolved = _resolve_path(metadata_path)
    with open(resolved, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    if not isinstance(metadata, dict):
        raise ValueError("voxel metadata must be a JSON object")
    metadata.setdefault("domain_min", [0.0, 0.0, 0.0])
    metadata.setdefault("domain_max", [1.0, 1.0, 1.0])
    metadata.setdefault("voxel_order", "ijk")
    return metadata


def _as_vec3(values, name):
    arr = np.asarray(values, dtype=np.float64)
    if arr.shape != (3,) or not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must contain three finite values")
    return arr


def _resolve_path(path):
    text = os.fspath(path)
    if os.path.isabs(text):
        return text
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(root, text)
