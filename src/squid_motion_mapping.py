import csv
import json
import math
import os
from pathlib import Path

import numpy as np

from .geometry_config import GeometryConfig
from .geometry_utils import as_vec3
from .squid_kinematics_config import SquidKinematicsScheduleConfig
from .squid_kinematics_schedule import schedule_rows
from .squid_motion_mapping_config import REQUIRED_TRACKED_REGIONS, SquidMotionMappingConfig
from .squid_proxy_regions import sample_squid_proxy_region_points, sample_squid_proxy_regions
from .squid_region_config import load_squid_proxy_region_config


MOTION_SCOPE_NOTE = "Step 33 motion diagnostics only; no driver integration and no LBM wall velocity application"

MOTION_FIELDS = [
    "sample_index",
    "phase",
    "region_id",
    "motion_model",
    "point_count",
    "displacement_norm_min",
    "displacement_norm_max",
    "displacement_norm_mean",
    "velocity_norm_min",
    "velocity_norm_max",
    "velocity_norm_mean",
    "mantle_radius_scale",
    "mantle_radius_rate",
    "volume_scale",
    "volume_rate",
    "aperture_scale",
    "aperture_rate",
    "finite_pass",
    "bounds_pass",
    "driver_integration_enabled",
    "lbm_wall_velocity_enabled",
    "jet_model_enabled",
    "actuation_enabled",
    "scope_note",
]


def load_motion_mapping_inputs(mapping_config_path) -> dict:
    mapping_config = SquidMotionMappingConfig.from_json(_resolve_path(mapping_config_path))
    schedule_config = SquidKinematicsScheduleConfig.from_json(_resolve_path(mapping_config.schedule_config_path))
    geometry_config = GeometryConfig.from_json(_resolve_path(mapping_config.geometry_config_path))
    region_config = load_squid_proxy_region_config(_resolve_path(mapping_config.region_config_path))
    rows = schedule_rows(schedule_config)
    points = sample_squid_proxy_region_points(geometry_config, count=mapping_config.sample_count, seed=33)
    masks = sample_squid_proxy_regions(geometry_config, region_config, points)
    return {
        "mapping_config": mapping_config,
        "schedule_config": schedule_config,
        "geometry_config": geometry_config,
        "region_config": region_config,
        "schedule_rows": rows,
        "points": points,
        "masks": masks,
    }


def compute_region_motion_rows(
    mapping_config: SquidMotionMappingConfig,
    kinematics_rows: list[dict],
    geometry_config: GeometryConfig,
    region_config,
    points: np.ndarray,
    masks: dict[str, np.ndarray],
) -> list[dict]:
    del region_config
    pts = _as_points(points)
    mantle_center = as_vec3(geometry_config.mantle_center, "mantle_center")
    mantle_radii = as_vec3(geometry_config.mantle_radii, "mantle_radii")
    rows = []
    for schedule_row in kinematics_rows:
        for region_id in mapping_config.tracked_regions:
            mask = np.asarray(masks[region_id], dtype=bool)
            selected = pts[mask]
            motion_model = _motion_model_for_region(region_id, mapping_config)
            displacement = _region_displacement_norms(region_id, selected, mantle_center, mantle_radii, schedule_row)
            velocity = _region_velocity_norms(region_id, selected, mantle_center, mantle_radii, schedule_row)
            row = {
                "sample_index": int(schedule_row["sample_index"]),
                "phase": float(schedule_row["phase"]),
                "region_id": region_id,
                "motion_model": motion_model,
                "point_count": int(len(selected)),
                "displacement_norm_min": _safe_min(displacement),
                "displacement_norm_max": _safe_max(displacement),
                "displacement_norm_mean": _safe_mean(displacement),
                "velocity_norm_min": _safe_min(velocity),
                "velocity_norm_max": _safe_max(velocity),
                "velocity_norm_mean": _safe_mean(velocity),
                "mantle_radius_scale": float(schedule_row["mantle_radius_scale"]),
                "mantle_radius_rate": float(schedule_row["mantle_radius_rate"]),
                "volume_scale": float(schedule_row["cavity_volume_scale"]),
                "volume_rate": cavity_volume_rate_proxy(schedule_row["cavity_volume_rate"]),
                "aperture_scale": float(schedule_row["funnel_aperture_scale"]),
                "aperture_rate": funnel_aperture_rate_proxy(schedule_row["funnel_aperture_rate"]),
                "driver_integration_enabled": bool(mapping_config.driver_integration_enabled),
                "lbm_wall_velocity_enabled": bool(mapping_config.lbm_wall_velocity_enabled),
                "jet_model_enabled": bool(mapping_config.jet_model_enabled),
                "actuation_enabled": bool(mapping_config.actuation_enabled),
                "scope_note": MOTION_SCOPE_NOTE,
            }
            row["finite_pass"] = _finite_motion_row(row)
            row["bounds_pass"] = _bounds_motion_row(row)
            rows.append(row)
    return rows


def mantle_displacement_proxy(points, mantle_center, mantle_radii, mantle_radius_scale) -> np.ndarray:
    radial_distance = _mantle_radial_distance(points, mantle_center, mantle_radii)
    return radial_distance * abs(1.0 - float(mantle_radius_scale))


def mantle_velocity_proxy(points, mantle_center, mantle_radii, mantle_radius_rate) -> np.ndarray:
    radial_distance = _mantle_radial_distance(points, mantle_center, mantle_radii)
    return radial_distance * abs(float(mantle_radius_rate))


def cavity_volume_rate_proxy(cavity_volume_rate) -> float:
    return float(cavity_volume_rate)


def funnel_aperture_rate_proxy(funnel_aperture_rate) -> float:
    return float(funnel_aperture_rate)


def summarize_motion_rows(rows: list[dict]) -> dict:
    if not rows:
        return {"row_count": 0, "quality_ready": False}
    region_ids = sorted({row["region_id"] for row in rows})
    sample_indices = sorted({int(row["sample_index"]) for row in rows})
    mantle_rows = [row for row in rows if row["region_id"] == "mantle_outer"]
    cavity_rows = [row for row in rows if row["region_id"] == "mantle_cavity_proxy"]
    funnel_rows = [row for row in rows if row["region_id"] == "funnel_outlet_proxy"]
    return {
        "row_count": len(rows),
        "schedule_sample_count": len(sample_indices),
        "tracked_region_count": len(region_ids),
        "tracked_regions": region_ids,
        "expected_row_count": len(sample_indices) * len(REQUIRED_TRACKED_REGIONS),
        "finite_pass": all(bool(row["finite_pass"]) for row in rows),
        "bounds_pass": all(bool(row["bounds_pass"]) for row in rows),
        "mantle_outer_row_count": len(mantle_rows),
        "mantle_outer_max_velocity_norm": max(float(row["velocity_norm_max"]) for row in mantle_rows),
        "mantle_outer_max_displacement_norm": max(float(row["displacement_norm_max"]) for row in mantle_rows),
        "mantle_outer_nonzero_velocity_row_count": sum(1 for row in mantle_rows if float(row["velocity_norm_max"]) > 0.0),
        "mantle_cavity_proxy_row_count": len(cavity_rows),
        "cavity_volume_rate_nonzero_row_count": sum(1 for row in cavity_rows if abs(float(row["volume_rate"])) > 0.0),
        "funnel_outlet_proxy_row_count": len(funnel_rows),
        "funnel_aperture_rate_nonzero_row_count": sum(1 for row in funnel_rows if abs(float(row["aperture_rate"])) > 0.0),
        "driver_integration_enabled_count": sum(1 for row in rows if bool(row["driver_integration_enabled"])),
        "lbm_wall_velocity_enabled_count": sum(1 for row in rows if bool(row["lbm_wall_velocity_enabled"])),
        "jet_model_enabled_count": sum(1 for row in rows if bool(row["jet_model_enabled"])),
        "actuation_enabled_count": sum(1 for row in rows if bool(row["actuation_enabled"])),
    }


def write_motion_rows(rows: list[dict], csv_path, json_path, summary=None) -> None:
    summary_payload = summarize_motion_rows(rows) if summary is None else summary
    _write_csv(csv_path, rows, MOTION_FIELDS)
    _write_json(json_path, {"summary": summary_payload, "rows": rows})


def _motion_model_for_region(region_id: str, mapping_config: SquidMotionMappingConfig) -> str:
    if region_id == "mantle_outer":
        return mapping_config.mantle_motion_model
    if region_id == "mantle_cavity_proxy":
        return mapping_config.cavity_motion_model
    if region_id == "funnel_outlet_proxy":
        return mapping_config.funnel_motion_model
    raise ValueError(f"unsupported tracked region: {region_id}")


def _region_displacement_norms(region_id: str, points: np.ndarray, mantle_center, mantle_radii, schedule_row: dict) -> np.ndarray:
    if region_id == "mantle_outer":
        return mantle_displacement_proxy(points, mantle_center, mantle_radii, schedule_row["mantle_radius_scale"])
    return np.zeros(len(points), dtype=np.float64)


def _region_velocity_norms(region_id: str, points: np.ndarray, mantle_center, mantle_radii, schedule_row: dict) -> np.ndarray:
    if region_id == "mantle_outer":
        return mantle_velocity_proxy(points, mantle_center, mantle_radii, schedule_row["mantle_radius_rate"])
    return np.zeros(len(points), dtype=np.float64)


def _mantle_radial_distance(points, mantle_center, mantle_radii) -> np.ndarray:
    pts = _as_points(points)
    if len(pts) == 0:
        return np.zeros(0, dtype=np.float64)
    normalized = (pts - np.asarray(mantle_center, dtype=np.float64)) / np.asarray(mantle_radii, dtype=np.float64)
    direction_norm = np.linalg.norm(normalized, axis=1)
    physical_radius = float(np.mean(np.asarray(mantle_radii, dtype=np.float64)))
    return direction_norm * physical_radius


def _as_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("points must have shape (n, 3)")
    if not np.all(np.isfinite(array)):
        raise ValueError("points must be finite")
    return array


def _safe_min(values: np.ndarray) -> float:
    return float(np.min(values)) if len(values) else 0.0


def _safe_max(values: np.ndarray) -> float:
    return float(np.max(values)) if len(values) else 0.0


def _safe_mean(values: np.ndarray) -> float:
    return float(np.mean(values)) if len(values) else 0.0


def _finite_motion_row(row: dict) -> bool:
    numeric_fields = [
        "phase",
        "point_count",
        "displacement_norm_min",
        "displacement_norm_max",
        "displacement_norm_mean",
        "velocity_norm_min",
        "velocity_norm_max",
        "velocity_norm_mean",
        "mantle_radius_scale",
        "mantle_radius_rate",
        "volume_scale",
        "volume_rate",
        "aperture_scale",
        "aperture_rate",
    ]
    return all(math.isfinite(float(row[field])) for field in numeric_fields)


def _bounds_motion_row(row: dict) -> bool:
    return (
        int(row["point_count"]) > 0
        and 0.0 <= float(row["displacement_norm_min"]) <= float(row["displacement_norm_mean"]) <= float(row["displacement_norm_max"])
        and 0.0 <= float(row["velocity_norm_min"]) <= float(row["velocity_norm_mean"]) <= float(row["velocity_norm_max"])
        and 0.0 < float(row["mantle_radius_scale"]) <= 1.0
        and 0.0 < float(row["volume_scale"]) <= 1.0
        and 0.0 <= float(row["aperture_scale"]) <= 1.0
    )


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


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return Path(__file__).resolve().parents[1] / path_obj
