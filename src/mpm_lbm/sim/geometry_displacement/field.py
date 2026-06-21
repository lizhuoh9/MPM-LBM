import csv
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from src.mpm_lbm.sim.geometry.config import GeometryConfig
from src.mpm_lbm.sim.geometry.utils import as_vec3
from src.mpm_lbm.sim.geometry_displacement.config import GeometryDisplacementConfig, REQUIRED_TRACKED_REGIONS
from src.mpm_lbm.sim.squid_proxy.kinematics_config import SquidKinematicsScheduleConfig
from src.mpm_lbm.sim.squid_proxy.kinematics_schedule import schedule_rows
from src.mpm_lbm.sim.squid_proxy.regions import sample_squid_proxy_region_points, sample_squid_proxy_regions
from src.mpm_lbm.sim.squid_proxy.region_config import load_squid_proxy_region_config


DISPLACEMENT_SCOPE_NOTE = "Step 42 geometry displacement diagnostics only; no driver-coupled geometry update"

DISPLACEMENT_FIELDS = [
    "sample_index",
    "phase",
    "region_id",
    "displacement_model",
    "point_count",
    "displacement_norm_min",
    "displacement_norm_max",
    "displacement_norm_mean",
    "bbox_min_x",
    "bbox_min_y",
    "bbox_min_z",
    "bbox_max_x",
    "bbox_max_y",
    "bbox_max_z",
    "mantle_radius_scale",
    "mantle_radius_rate",
    "volume_scale",
    "volume_rate",
    "aperture_scale",
    "aperture_rate",
    "diagnostic_only",
    "apply_to_driver",
    "apply_to_lbm",
    "apply_to_mpm",
    "apply_to_projection",
    "update_dynamic_solid",
    "driver_integration_enabled",
    "finite_pass",
    "bounds_pass",
    "scope_note",
]


def load_geometry_displacement_inputs(config_path) -> dict:
    config = GeometryDisplacementConfig.from_json(_resolve_path(config_path))
    schedule_config = SquidKinematicsScheduleConfig.from_json(_resolve_path(config.schedule_config_path))
    geometry_config = GeometryConfig.from_json(str(_resolve_path(config.geometry_config_path)))
    region_config = load_squid_proxy_region_config(_resolve_path(config.region_config_path))
    points = sample_squid_proxy_region_points(geometry_config, count=config.sample_count, seed=42)
    masks = sample_squid_proxy_regions(geometry_config, region_config, points)
    return {
        "config": config,
        "schedule_config": schedule_config,
        "geometry_config": geometry_config,
        "region_config": region_config,
        "schedule_rows": schedule_rows(schedule_config),
        "points": points,
        "masks": masks,
    }


def compute_geometry_displacement_rows(
    config: GeometryDisplacementConfig,
    kinematics_rows: list[dict],
    geometry_config: GeometryConfig,
    points: np.ndarray,
    masks: dict[str, np.ndarray],
) -> list[dict]:
    pts = _as_points(points)
    rows = []
    for schedule_row in kinematics_rows:
        for region_id in config.tracked_regions:
            selected = pts[np.asarray(masks[region_id], dtype=bool)]
            vectors = displacement_vectors_for_region(region_id, selected, geometry_config, schedule_row)
            displaced = selected + vectors
            norms = np.linalg.norm(vectors, axis=1) if len(vectors) else np.zeros(0, dtype=np.float64)
            bbox_min, bbox_max = _bbox(displaced)
            row = {
                "sample_index": int(schedule_row["sample_index"]),
                "phase": float(schedule_row["phase"]),
                "region_id": region_id,
                "displacement_model": _model_for_region(region_id, config),
                "point_count": int(len(selected)),
                "displacement_norm_min": _safe_min(norms),
                "displacement_norm_max": _safe_max(norms),
                "displacement_norm_mean": _safe_mean(norms),
                "bbox_min_x": float(bbox_min[0]),
                "bbox_min_y": float(bbox_min[1]),
                "bbox_min_z": float(bbox_min[2]),
                "bbox_max_x": float(bbox_max[0]),
                "bbox_max_y": float(bbox_max[1]),
                "bbox_max_z": float(bbox_max[2]),
                "mantle_radius_scale": float(schedule_row["mantle_radius_scale"]),
                "mantle_radius_rate": float(schedule_row["mantle_radius_rate"]),
                "volume_scale": float(schedule_row["cavity_volume_scale"]),
                "volume_rate": float(schedule_row["cavity_volume_rate"]),
                "aperture_scale": float(schedule_row["funnel_aperture_scale"]),
                "aperture_rate": float(schedule_row["funnel_aperture_rate"]),
                "diagnostic_only": True,
                "apply_to_driver": bool(config.apply_to_driver),
                "apply_to_lbm": bool(config.apply_to_lbm),
                "apply_to_mpm": bool(config.apply_to_mpm),
                "apply_to_projection": bool(config.apply_to_projection),
                "update_dynamic_solid": bool(config.update_dynamic_solid),
                "driver_integration_enabled": bool(config.driver_integration_enabled),
                "scope_note": DISPLACEMENT_SCOPE_NOTE,
            }
            row["finite_pass"] = _finite_displacement_row(row)
            row["bounds_pass"] = _bounds_displacement_row(row, config)
            rows.append(row)
    return rows


def displacement_vectors_for_region(region_id: str, points: np.ndarray, geometry_config: GeometryConfig, schedule_row: dict) -> np.ndarray:
    selected = _as_points(points)
    if region_id == "mantle_outer":
        return mantle_radial_displacement_vectors(selected, geometry_config, schedule_row["mantle_radius_scale"])
    if region_id == "mantle_cavity_proxy":
        return cavity_volume_displacement_vectors(selected, geometry_config, schedule_row["cavity_volume_scale"])
    if region_id == "funnel_outlet_proxy":
        return funnel_aperture_displacement_vectors(selected, geometry_config, schedule_row["funnel_aperture_scale"])
    raise ValueError(f"unsupported tracked region: {region_id}")


def mantle_radial_displacement_vectors(points: np.ndarray, geometry_config: GeometryConfig, mantle_radius_scale) -> np.ndarray:
    pts = _as_points(points)
    if len(pts) == 0:
        return np.zeros((0, 3), dtype=np.float64)
    center = as_vec3(geometry_config.mantle_center, "mantle_center")
    radii = as_vec3(geometry_config.mantle_radii, "mantle_radii")
    offsets = pts - center
    offset_norms = np.linalg.norm(offsets, axis=1)
    unit = np.zeros_like(offsets)
    nonzero = offset_norms > 1.0e-14
    unit[nonzero] = offsets[nonzero] / offset_norms[nonzero, None]
    normalized_radius = np.linalg.norm(offsets / radii, axis=1)
    physical_radius = normalized_radius * float(np.mean(radii))
    magnitude = physical_radius * (float(mantle_radius_scale) - 1.0)
    return unit * magnitude[:, None]


def cavity_volume_displacement_vectors(points: np.ndarray, geometry_config: GeometryConfig, cavity_volume_scale) -> np.ndarray:
    pts = _as_points(points)
    if len(pts) == 0:
        return np.zeros((0, 3), dtype=np.float64)
    center, _ = cavity_center_radii(geometry_config)
    linear_scale = max(float(cavity_volume_scale), 0.0) ** (1.0 / 3.0)
    return (pts - center) * (linear_scale - 1.0)


def funnel_aperture_displacement_vectors(points: np.ndarray, geometry_config: GeometryConfig, funnel_aperture_scale) -> np.ndarray:
    pts = _as_points(points)
    if len(pts) == 0:
        return np.zeros((0, 3), dtype=np.float64)
    center, _ = funnel_center_radii(geometry_config)
    rest = 0.35
    max_scale = 1.0
    openness = np.clip((float(funnel_aperture_scale) - rest) / (max_scale - rest), 0.0, 1.0)
    transverse = pts - center
    transverse[:, 1] = 0.0
    return transverse * openness


def cavity_center_radii(geometry_config: GeometryConfig) -> tuple[np.ndarray, np.ndarray]:
    mantle_center = as_vec3(geometry_config.mantle_center, "mantle_center")
    mantle_radii = as_vec3(geometry_config.mantle_radii, "mantle_radii")
    return (
        mantle_center + np.array([0.0, mantle_radii[1] * 0.08, 0.0], dtype=np.float64),
        mantle_radii * np.array([0.55, 0.50, 0.55], dtype=np.float64),
    )


def funnel_center_radii(geometry_config: GeometryConfig) -> tuple[np.ndarray, np.ndarray]:
    mantle_center = as_vec3(geometry_config.mantle_center, "mantle_center")
    mantle_radii = as_vec3(geometry_config.mantle_radii, "mantle_radii")
    return (
        mantle_center + np.array([0.0, -mantle_radii[1] * 0.78, 0.0], dtype=np.float64),
        np.array(
            [
                max(float(geometry_config.arm_radius) * 1.6, mantle_radii[0] * 0.20),
                mantle_radii[1] * 0.18,
                max(float(geometry_config.arm_radius) * 1.6, mantle_radii[2] * 0.22),
            ],
            dtype=np.float64,
        ),
    )


def summarize_geometry_displacement_rows(rows: list[dict], config: GeometryDisplacementConfig) -> dict:
    if not rows:
        return {"row_count": 0, "finite_pass": False, "bounds_pass": False, "diagnostic_only_pass": False}
    sample_indices = sorted({int(row["sample_index"]) for row in rows})
    region_ids = list(config.tracked_regions)
    return {
        "row_count": len(rows),
        "phase_sample_count": len(sample_indices),
        "tracked_region_count": len(region_ids),
        "tracked_regions": region_ids,
        "expected_row_count": len(sample_indices) * len(region_ids),
        "max_displacement_norm": max(float(row["displacement_norm_max"]) for row in rows),
        "max_displacement_norm_allowed": float(config.max_displacement_norm_allowed),
        "finite_pass": all(bool(row["finite_pass"]) for row in rows),
        "bounds_pass": all(bool(row["bounds_pass"]) for row in rows),
        "diagnostic_only_pass": all(bool(row["diagnostic_only"]) for row in rows),
        "driver_update_count": sum(1 for row in rows if bool(row["apply_to_driver"])),
        "lbm_update_count": sum(1 for row in rows if bool(row["apply_to_lbm"])),
        "mpm_update_count": sum(1 for row in rows if bool(row["apply_to_mpm"])),
        "projection_update_count": sum(1 for row in rows if bool(row["apply_to_projection"])),
        "dynamic_solid_update_count": sum(1 for row in rows if bool(row["update_dynamic_solid"])),
        "driver_integration_count": sum(1 for row in rows if bool(row["driver_integration_enabled"])),
    }


def write_geometry_displacement_rows(rows: list[dict], csv_path, json_path, npz_path, summary=None) -> None:
    config = _fallback_config()
    summary_payload = summarize_geometry_displacement_rows(rows, config) if summary is None else summary
    _write_csv(csv_path, rows, DISPLACEMENT_FIELDS)
    _write_json(json_path, {"summary": summary_payload, "rows": rows})
    _write_npz(npz_path, rows)


def displacement_hashes(rows: list[dict], precision=12) -> dict:
    return {
        "displacement_hash": canonical_displacement_hash(
            rows,
            [
                "sample_index",
                "phase",
                "region_id",
                "displacement_norm_max",
                "displacement_norm_mean",
                "bbox_min_x",
                "bbox_max_x",
                "mantle_radius_scale",
                "volume_scale",
                "aperture_scale",
            ],
            precision=precision,
        ),
        "mantle_displacement_hash": canonical_displacement_hash(
            [row for row in rows if row["region_id"] == "mantle_outer"],
            ["sample_index", "phase", "displacement_norm_max", "mantle_radius_scale"],
            precision=precision,
        ),
        "cavity_displacement_hash": canonical_displacement_hash(
            [row for row in rows if row["region_id"] == "mantle_cavity_proxy"],
            ["sample_index", "phase", "displacement_norm_max", "volume_scale"],
            precision=precision,
        ),
        "funnel_displacement_hash": canonical_displacement_hash(
            [row for row in rows if row["region_id"] == "funnel_outlet_proxy"],
            ["sample_index", "phase", "displacement_norm_max", "aperture_scale"],
            precision=precision,
        ),
    }


def canonical_displacement_hash(rows: list[dict], fields: list[str], precision=12) -> str:
    parts = []
    for row in rows:
        values = []
        for field in fields:
            value = row[field]
            if isinstance(value, bool):
                values.append("1" if value else "0")
            else:
                try:
                    values.append(f"{float(value):.{int(precision)}g}")
                except (TypeError, ValueError):
                    values.append(str(value))
        parts.append(",".join(values))
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def assert_geometry_displacement_summary(summary: dict) -> None:
    if not (
        int(summary.get("row_count", 0)) == 243
        and int(summary.get("phase_sample_count", 0)) == 81
        and int(summary.get("tracked_region_count", 0)) == 3
        and bool(summary.get("finite_pass", False))
        and bool(summary.get("bounds_pass", False))
        and bool(summary.get("diagnostic_only_pass", False))
        and int(summary.get("driver_update_count", -1)) == 0
        and int(summary.get("lbm_update_count", -1)) == 0
        and int(summary.get("mpm_update_count", -1)) == 0
        and int(summary.get("projection_update_count", -1)) == 0
        and int(summary.get("dynamic_solid_update_count", -1)) == 0
    ):
        raise RuntimeError(f"Step 42 geometry displacement summary failed: {summary}")


def _model_for_region(region_id: str, config: GeometryDisplacementConfig) -> str:
    if region_id == "mantle_outer":
        return config.mantle_displacement_model
    if region_id == "mantle_cavity_proxy":
        return config.cavity_displacement_model
    if region_id == "funnel_outlet_proxy":
        return config.funnel_displacement_model
    raise ValueError(f"unsupported tracked region: {region_id}")


def _finite_displacement_row(row: dict) -> bool:
    numeric_fields = [
        "sample_index",
        "phase",
        "point_count",
        "displacement_norm_min",
        "displacement_norm_max",
        "displacement_norm_mean",
        "bbox_min_x",
        "bbox_min_y",
        "bbox_min_z",
        "bbox_max_x",
        "bbox_max_y",
        "bbox_max_z",
        "mantle_radius_scale",
        "mantle_radius_rate",
        "volume_scale",
        "volume_rate",
        "aperture_scale",
        "aperture_rate",
    ]
    return all(math.isfinite(float(row[field])) for field in numeric_fields)


def _bounds_displacement_row(row: dict, config: GeometryDisplacementConfig) -> bool:
    return (
        int(row["point_count"]) > 0
        and 0.0 <= float(row["displacement_norm_min"]) <= float(row["displacement_norm_mean"]) <= float(row["displacement_norm_max"])
        and float(row["displacement_norm_max"]) <= float(config.max_displacement_norm_allowed) + 1.0e-12
        and float(row["bbox_min_x"]) <= float(row["bbox_max_x"])
        and float(row["bbox_min_y"]) <= float(row["bbox_max_y"])
        and float(row["bbox_min_z"]) <= float(row["bbox_max_z"])
        and bool(row["diagnostic_only"])
        and not bool(row["apply_to_driver"])
        and not bool(row["apply_to_lbm"])
        and not bool(row["apply_to_mpm"])
        and not bool(row["apply_to_projection"])
        and not bool(row["update_dynamic_solid"])
        and not bool(row["driver_integration_enabled"])
    )


def _bbox(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(points) == 0:
        nan = np.array([float("nan"), float("nan"), float("nan")], dtype=np.float64)
        return nan, nan
    return np.min(points, axis=0), np.max(points, axis=0)


def _safe_min(values: np.ndarray) -> float:
    return float(np.min(values)) if len(values) else 0.0


def _safe_max(values: np.ndarray) -> float:
    return float(np.max(values)) if len(values) else 0.0


def _safe_mean(values: np.ndarray) -> float:
    return float(np.mean(values)) if len(values) else 0.0


def _as_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("points must have shape (n, 3)")
    if not np.all(np.isfinite(array)):
        raise ValueError("points must be finite")
    return array


def _write_csv(path, rows: list[dict], fieldnames: list[str]) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_json(path, payload) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _write_npz(path, rows: list[dict]) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        resolved,
        sample_index=np.asarray([int(row["sample_index"]) for row in rows], dtype=np.int32),
        phase=np.asarray([float(row["phase"]) for row in rows], dtype=np.float64),
        region_id=np.asarray([str(row["region_id"]) for row in rows]),
        displacement_norm_max=np.asarray([float(row["displacement_norm_max"]) for row in rows], dtype=np.float64),
    )


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return Path(__file__).resolve().parents[1] / path_obj


def _fallback_config() -> GeometryDisplacementConfig:
    return GeometryDisplacementConfig(
        displacement_id="step42_squid_proxy_geometry_displacement_diagnostics",
        schedule_config_path="configs/step32_squid_proxy_kinematics_schedule.json",
        motion_mapping_config_path="configs/step33_squid_proxy_motion_mapping.json",
        region_config_path="configs/step30_squid_proxy_region_config.json",
        geometry_config_path="configs/step30_squid_proxy_geometry.json",
        tracked_regions=REQUIRED_TRACKED_REGIONS,
        context_regions=("head_proxy", "arms_proxy", "left_fin_proxy", "right_fin_proxy"),
        sample_count=32768,
        phase_sample_count=81,
        grid_sizes=(32, 48, 64),
        mantle_displacement_model="radial_scale_proxy",
        cavity_displacement_model="volume_scale_proxy",
        funnel_displacement_model="aperture_scale_proxy",
        max_displacement_norm_allowed=0.25,
    )
