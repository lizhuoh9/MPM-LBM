import csv
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D
from src.mpm_lbm.sim.geometry.config import GeometryConfig
from src.mpm_lbm.sim.geometry.utils import as_vec3, inside_ellipsoid
from src.mpm_lbm.sim.squid_proxy.region_config import (
    REQUIRED_REGION_IDS,
    SquidProxyRegionConfig,
    default_squid_proxy_region_config,
    load_squid_proxy_region_config,
    validate_squid_region_config,
)


def sample_squid_proxy_region_points(
    geometry_config: GeometryConfig,
    count: int | None = None,
    seed: int = 30,
) -> np.ndarray:
    sample_count = int(count or max(geometry_config.n_particles, 32**3))
    if sample_count <= 0:
        raise ValueError("sample count must be positive")
    domain_min = as_vec3(geometry_config.domain_min, "domain_min")
    domain_max = as_vec3(geometry_config.domain_max, "domain_max")
    resolution = int(math.ceil(sample_count ** (1.0 / 3.0)))
    coords = [
        np.linspace(domain_min[axis], domain_max[axis], resolution, endpoint=False, dtype=np.float64)
        + (domain_max[axis] - domain_min[axis]) / float(resolution * 2)
        for axis in range(3)
    ]
    x, y, z = np.meshgrid(coords[0], coords[1], coords[2], indexing="ij")
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    if len(points) == sample_count:
        return points.copy()
    rng = np.random.default_rng(int(seed))
    indices = np.arange(len(points), dtype=np.int64)
    rng.shuffle(indices)
    return points[np.sort(indices[:sample_count])].copy()


def sample_squid_proxy_regions(
    geometry_config: GeometryConfig,
    region_config: SquidProxyRegionConfig,
    points: np.ndarray,
) -> dict[str, np.ndarray]:
    if geometry_config.geometry_type != "squid_proxy":
        raise ValueError("Step 30 region masks require geometry_type='squid_proxy'")
    validation = validate_squid_region_config(region_config)
    if not validation["schema_pass"]:
        raise ValueError(f"invalid squid region config: {validation}")

    pts = _as_points(points)
    sampler = GeometrySampler3D(geometry_config)
    component_masks = sampler.component_masks(pts)
    mantle_center = as_vec3(geometry_config.mantle_center, "mantle_center")
    mantle_radii = as_vec3(geometry_config.mantle_radii, "mantle_radii")
    cavity_center = mantle_center + np.array([0.0, mantle_radii[1] * 0.08, 0.0], dtype=np.float64)
    cavity_radii = mantle_radii * np.array([0.55, 0.50, 0.55], dtype=np.float64)
    outlet_center = mantle_center + np.array([0.0, -mantle_radii[1] * 0.78, 0.0], dtype=np.float64)
    outlet_radii = np.array(
        [
            max(float(geometry_config.arm_radius) * 1.6, mantle_radii[0] * 0.20),
            mantle_radii[1] * 0.18,
            max(float(geometry_config.arm_radius) * 1.6, mantle_radii[2] * 0.22),
        ],
        dtype=np.float64,
    )
    masks = {
        "mantle_outer": np.asarray(component_masks["mantle"], dtype=bool),
        "mantle_cavity_proxy": inside_ellipsoid(pts, cavity_center, cavity_radii),
        "funnel_outlet_proxy": inside_ellipsoid(pts, outlet_center, outlet_radii),
        "head_proxy": np.asarray(component_masks["head"], dtype=bool),
        "arms_proxy": np.asarray(component_masks["arms"], dtype=bool),
        "left_fin_proxy": np.asarray(component_masks["left_fin"], dtype=bool),
        "right_fin_proxy": np.asarray(component_masks["right_fin"], dtype=bool),
    }
    return {region_id: masks[region_id].copy() for region_id in REQUIRED_REGION_IDS}


def summarize_region_masks(
    points: np.ndarray,
    masks: dict[str, np.ndarray],
    geometry_config: GeometryConfig,
    region_config: SquidProxyRegionConfig,
) -> list[dict]:
    pts = _as_points(points)
    domain_min = as_vec3(geometry_config.domain_min, "domain_min")
    domain_max = as_vec3(geometry_config.domain_max, "domain_max")
    domain_volume = float(np.prod(domain_max - domain_min))
    region_by_id = {region.region_id: region for region in region_config.regions}
    rows = []
    for region_id in REQUIRED_REGION_IDS:
        mask = np.asarray(masks[region_id], dtype=bool)
        if mask.shape != (len(pts),):
            raise ValueError(f"mask for {region_id} must have shape ({len(pts)},)")
        selected = pts[mask]
        count = int(np.count_nonzero(mask))
        bbox_min, bbox_max = _bbox(selected)
        region = region_by_id[region_id]
        rows.append(
            {
                "region_id": region_id,
                "name": region.name,
                "role": region.role,
                "material": region.material,
                "parent_id": region.parent_id or "",
                "active_for_actuation": bool(region.active_for_actuation),
                "point_count": count,
                "sample_count": int(len(pts)),
                "estimated_volume": domain_volume * float(count) / float(len(pts)),
                "volume_fraction": float(count) / float(len(pts)),
                "bbox_min_x": bbox_min[0],
                "bbox_min_y": bbox_min[1],
                "bbox_min_z": bbox_min[2],
                "bbox_max_x": bbox_max[0],
                "bbox_max_y": bbox_max[1],
                "bbox_max_z": bbox_max[2],
                "bbox_finite": bool(np.all(np.isfinite(bbox_min)) and np.all(np.isfinite(bbox_max))),
                "mask_is_boolean": bool(np.asarray(masks[region_id]).dtype == np.bool_),
                "diagnostics_finite": bool(count > 0 and np.all(np.isfinite(bbox_min)) and np.all(np.isfinite(bbox_max))),
                "notes": region.notes,
            }
        )
    return rows


def sampled_position_hash(points: np.ndarray) -> str:
    pts = np.ascontiguousarray(_as_points(points), dtype=np.float64)
    return hashlib.sha256(pts.tobytes()).hexdigest()


def region_assignment_hash(masks: dict[str, np.ndarray]) -> str:
    packed = np.column_stack([np.asarray(masks[region_id], dtype=np.uint8) for region_id in REQUIRED_REGION_IDS])
    return hashlib.sha256(np.ascontiguousarray(packed).tobytes()).hexdigest()


def mantle_normalized_radius(geometry_config: GeometryConfig, points: np.ndarray) -> np.ndarray:
    pts = _as_points(points)
    center = as_vec3(geometry_config.mantle_center, "mantle_center")
    radii = as_vec3(geometry_config.mantle_radii, "mantle_radii")
    q = (pts - center) / radii
    return np.sqrt(np.einsum("ij,ij->i", q, q))


def write_region_manifest(rows, csv_path, json_path, summary: dict | None = None) -> None:
    csv_file = Path(os.fspath(csv_path))
    json_file = Path(os.fspath(json_path))
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_value(row.get(key, "")) for key in fieldnames})
    json_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {"rows": rows, "summary": summary or {}}
    with json_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _as_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("points must have shape (n, 3)")
    if not np.all(np.isfinite(array)):
        raise ValueError("points must be finite")
    return array


def _bbox(points: np.ndarray) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    if len(points) == 0:
        nan = (float("nan"), float("nan"), float("nan"))
        return nan, nan
    return tuple(np.min(points, axis=0).tolist()), tuple(np.max(points, axis=0).tolist())


def _csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


__all__ = [
    "default_squid_proxy_region_config",
    "load_squid_proxy_region_config",
    "sample_squid_proxy_region_points",
    "sample_squid_proxy_regions",
    "summarize_region_masks",
    "sampled_position_hash",
    "region_assignment_hash",
    "mantle_normalized_radius",
    "write_region_manifest",
]
