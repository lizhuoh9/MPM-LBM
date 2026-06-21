import csv
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from src.mpm_lbm.sim.motion.boundary_motion_config import (
    BoundaryMotionInterfaceConfig,
    summarize_boundary_motion_config_validation,
    validate_boundary_motion_interface_config,
)
from src.mpm_lbm.sim.motion.boundary_motion_interface import build_boundary_motion_interface_report
from src.mpm_lbm.sim.geometry.config import GeometryConfig
from src.mpm_lbm.sim.geometry.utils import as_vec3
from src.mpm_lbm.sim.squid_proxy.motion_mapping import compute_region_motion_rows, load_motion_mapping_inputs
from src.mpm_lbm.sim.squid_proxy.regions import sample_squid_proxy_region_points, sample_squid_proxy_regions
from src.mpm_lbm.sim.squid_proxy.region_config import load_squid_proxy_region_config
from src.mpm_lbm.sim.wall_velocity.config import (
    EXPECTED_WALL_VELOCITY_ROW_COUNT,
    WallVelocityFieldConfig,
    assert_valid_wall_velocity_config,
)


WALL_VELOCITY_SCOPE_NOTE = "Step 35 diagnostic wall velocity field only; no LBM population update"

WALL_VELOCITY_FIELDS = [
    "grid_size",
    "phase",
    "region_id",
    "active_cell_count",
    "sample_point_count",
    "velocity_norm_min",
    "velocity_norm_max",
    "velocity_norm_mean",
    "velocity_x_mean",
    "velocity_y_mean",
    "velocity_z_mean",
    "displacement_norm_max",
    "source_motion_model",
    "source_motion_velocity_norm_max",
    "mantle_radius_rate",
    "volume_rate",
    "aperture_rate",
    "finite_pass",
    "bounds_pass",
    "diagnostic_only",
    "apply_to_lbm",
    "lbm_population_update_enabled",
    "moving_bounceback_update_enabled",
    "driver_integration_enabled",
    "scope_note",
]

_MOTION_NUMERIC_FIELDS = (
    "sample_index",
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
)


def load_wall_velocity_inputs(config_path) -> dict:
    config = WallVelocityFieldConfig.from_json(_resolve_path(config_path))
    assert_valid_wall_velocity_config(config, root=_repo_root())
    boundary_report = _load_boundary_motion_report(config)
    mapping_inputs = load_motion_mapping_inputs(config.motion_mapping_config_path)
    motion_rows = _load_motion_rows(config, mapping_inputs)
    geometry_config = GeometryConfig.from_json(_resolve_path(config.geometry_config_path))
    region_config = load_squid_proxy_region_config(_resolve_path(config.region_config_path))
    region_samples = {
        int(grid_size): _region_samples_for_grid(geometry_config, region_config, int(grid_size))
        for grid_size in config.grid_sizes
    }
    return {
        "config": config,
        "boundary_report": boundary_report,
        "mapping_inputs": mapping_inputs,
        "motion_rows": motion_rows,
        "geometry_config": geometry_config,
        "region_config": region_config,
        "region_samples": region_samples,
    }


def interpolate_motion_rows_to_phase(motion_rows: list[dict], phase: float) -> dict[str, dict]:
    phase_value = float(phase)
    regions = sorted({str(row["region_id"]) for row in motion_rows})
    interpolated = {}
    for region_id in regions:
        region_rows = sorted([row for row in motion_rows if row["region_id"] == region_id], key=lambda row: float(row["phase"]))
        exact = [row for row in region_rows if math.isclose(float(row["phase"]), phase_value, abs_tol=1.0e-12)]
        if exact:
            interpolated[region_id] = dict(exact[0])
            continue
        lower, upper = _bracket_rows(region_rows, phase_value)
        weight = 0.0 if math.isclose(float(upper["phase"]), float(lower["phase"])) else (
            (phase_value - float(lower["phase"])) / (float(upper["phase"]) - float(lower["phase"]))
        )
        row = dict(lower)
        for field in _MOTION_NUMERIC_FIELDS:
            row[field] = (1.0 - weight) * float(lower[field]) + weight * float(upper[field])
        row["phase"] = phase_value
        row["sample_index"] = -1
        interpolated[region_id] = row
    return interpolated


def compute_wall_velocity_summary(
    config: WallVelocityFieldConfig,
    phase: float,
    grid_size: int,
    region_id: str,
    motion_rows: list[dict],
    points: np.ndarray,
    masks: dict[str, np.ndarray],
    geometry_config: GeometryConfig,
) -> dict:
    pts = _as_points(points)
    mask = np.asarray(masks[region_id], dtype=bool)
    if mask.shape != (len(pts),):
        raise ValueError(f"mask for {region_id} must have shape ({len(pts)},)")
    selected = pts[mask]
    motion_by_region = interpolate_motion_rows_to_phase(motion_rows, phase)
    motion_row = motion_by_region[region_id]
    vectors, displacement_norms = _region_velocity_vectors(region_id, selected, geometry_config, motion_row)
    norms = np.linalg.norm(vectors, axis=1) if len(vectors) else np.zeros(0, dtype=np.float64)
    row = {
        "grid_size": int(grid_size),
        "phase": float(phase),
        "region_id": region_id,
        "active_cell_count": int(len(selected)),
        "sample_point_count": int(len(pts)),
        "velocity_norm_min": _safe_min(norms),
        "velocity_norm_max": _safe_max(norms),
        "velocity_norm_mean": _safe_mean(norms),
        "velocity_x_mean": _safe_mean(vectors[:, 0]) if len(vectors) else 0.0,
        "velocity_y_mean": _safe_mean(vectors[:, 1]) if len(vectors) else 0.0,
        "velocity_z_mean": _safe_mean(vectors[:, 2]) if len(vectors) else 0.0,
        "displacement_norm_max": _safe_max(displacement_norms),
        "source_motion_model": motion_row["motion_model"],
        "source_motion_velocity_norm_max": float(motion_row["velocity_norm_max"]),
        "mantle_radius_rate": float(motion_row["mantle_radius_rate"]),
        "volume_rate": float(motion_row["volume_rate"]),
        "aperture_rate": float(motion_row["aperture_rate"]),
        "diagnostic_only": True,
        "apply_to_lbm": bool(config.apply_to_lbm),
        "lbm_population_update_enabled": bool(config.lbm_population_update_enabled),
        "moving_bounceback_update_enabled": bool(config.moving_bounceback_update_enabled),
        "driver_integration_enabled": bool(config.driver_integration_enabled),
        "scope_note": WALL_VELOCITY_SCOPE_NOTE,
    }
    row["finite_pass"] = _finite_wall_velocity_row(row)
    row["bounds_pass"] = (
        int(row["active_cell_count"]) > 0
        and _ordered_with_tolerance(float(row["velocity_norm_min"]), float(row["velocity_norm_mean"]), float(row["velocity_norm_max"]))
        and float(row["velocity_norm_max"]) <= float(config.max_velocity_norm_allowed)
    )
    return row


def generate_wall_velocity_field_rows(config_or_path) -> list[dict]:
    if isinstance(config_or_path, WallVelocityFieldConfig):
        config = config_or_path
        assert_valid_wall_velocity_config(config, root=_repo_root())
        inputs = load_wall_velocity_inputs("configs/step35_squid_proxy_wall_velocity_field.json")
        if inputs["config"].to_dict() != config.to_dict():
            inputs = _inputs_from_config(config)
    else:
        inputs = load_wall_velocity_inputs(config_or_path)
        config = inputs["config"]

    rows = []
    for grid_size in config.grid_sizes:
        samples = inputs["region_samples"][int(grid_size)]
        for phase in config.phase_samples:
            for region_id in config.tracked_regions:
                rows.append(
                    compute_wall_velocity_summary(
                        config,
                        phase,
                        int(grid_size),
                        region_id,
                        inputs["motion_rows"],
                        samples["points"],
                        samples["masks"],
                        inputs["geometry_config"],
                    )
                )
    return rows


def summarize_wall_velocity_rows(rows: list[dict]) -> dict:
    if not rows:
        return {"row_count": 0, "quality_ready": False}
    region_ids = sorted({row["region_id"] for row in rows})
    grid_sizes = sorted({int(row["grid_size"]) for row in rows})
    phases = sorted({float(row["phase"]) for row in rows})
    return {
        "row_count": len(rows),
        "expected_row_count": EXPECTED_WALL_VELOCITY_ROW_COUNT,
        "grid_size_count": len(grid_sizes),
        "phase_sample_count": len(phases),
        "tracked_region_count": len(region_ids),
        "grid_sizes": grid_sizes,
        "phase_samples": phases,
        "tracked_regions": region_ids,
        "finite_pass": all(bool(row["finite_pass"]) for row in rows),
        "bounds_pass": all(bool(row["bounds_pass"]) for row in rows),
        "coverage_pass": all(int(row["active_cell_count"]) > 0 for row in rows),
        "diagnostic_only_pass": all(bool(row["diagnostic_only"]) for row in rows),
        "no_lbm_update_pass": all(not bool(row["apply_to_lbm"]) and not bool(row["lbm_population_update_enabled"]) for row in rows),
        "no_bounceback_update_pass": all(not bool(row["moving_bounceback_update_enabled"]) for row in rows),
        "no_driver_integration_pass": all(not bool(row["driver_integration_enabled"]) for row in rows),
        "max_velocity_norm": max(float(row["velocity_norm_max"]) for row in rows),
        "mean_velocity_norm": float(np.mean([float(row["velocity_norm_mean"]) for row in rows])),
        "min_active_cell_count": min(int(row["active_cell_count"]) for row in rows),
        "max_active_cell_count": max(int(row["active_cell_count"]) for row in rows),
        "diagnostic_only": True,
        "apply_to_lbm_count": sum(1 for row in rows if bool(row["apply_to_lbm"])),
        "lbm_population_update_enabled_count": sum(1 for row in rows if bool(row["lbm_population_update_enabled"])),
        "moving_bounceback_update_enabled_count": sum(1 for row in rows if bool(row["moving_bounceback_update_enabled"])),
        "driver_integration_enabled_count": sum(1 for row in rows if bool(row["driver_integration_enabled"])),
        "scope_note": WALL_VELOCITY_SCOPE_NOTE,
    }


def wall_velocity_hashes(rows: list[dict], precision=12) -> dict:
    fields = [
        "grid_size",
        "phase",
        "region_id",
        "active_cell_count",
        "velocity_norm_max",
        "velocity_norm_mean",
        "velocity_x_mean",
        "velocity_y_mean",
        "velocity_z_mean",
        "displacement_norm_max",
    ]
    return {
        "velocity_field_hash": canonical_wall_velocity_hash(rows, fields, precision=precision),
        "mantle_velocity_hash": canonical_wall_velocity_hash(
            [row for row in rows if row["region_id"] == "mantle_outer"],
            fields,
            precision=precision,
        ),
        "cavity_velocity_hash": canonical_wall_velocity_hash(
            [row for row in rows if row["region_id"] == "mantle_cavity_proxy"],
            fields,
            precision=precision,
        ),
        "funnel_velocity_hash": canonical_wall_velocity_hash(
            [row for row in rows if row["region_id"] == "funnel_outlet_proxy"],
            fields,
            precision=precision,
        ),
    }


def canonical_wall_velocity_hash(rows: list[dict], fields: list[str], precision=12) -> str:
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


def write_wall_velocity_rows(rows: list[dict], csv_path, json_path, summary=None) -> None:
    summary_payload = summarize_wall_velocity_rows(rows) if summary is None else summary
    _write_csv(csv_path, rows, WALL_VELOCITY_FIELDS)
    _write_json(json_path, {"summary": summary_payload, "rows": rows})


def _inputs_from_config(config: WallVelocityFieldConfig) -> dict:
    boundary_report = _load_boundary_motion_report(config)
    mapping_inputs = load_motion_mapping_inputs(config.motion_mapping_config_path)
    motion_rows = _load_motion_rows(config, mapping_inputs)
    geometry_config = GeometryConfig.from_json(_resolve_path(config.geometry_config_path))
    region_config = load_squid_proxy_region_config(_resolve_path(config.region_config_path))
    region_samples = {
        int(grid_size): _region_samples_for_grid(geometry_config, region_config, int(grid_size))
        for grid_size in config.grid_sizes
    }
    return {
        "config": config,
        "boundary_report": boundary_report,
        "mapping_inputs": mapping_inputs,
        "motion_rows": motion_rows,
        "geometry_config": geometry_config,
        "region_config": region_config,
        "region_samples": region_samples,
    }


def _load_boundary_motion_report(config: WallVelocityFieldConfig) -> dict:
    boundary_config = BoundaryMotionInterfaceConfig.from_json(_resolve_path(config.boundary_motion_config_path))
    validation_rows = validate_boundary_motion_interface_config(boundary_config, root=_repo_root())
    validation_summary = summarize_boundary_motion_config_validation(validation_rows)
    if not validation_summary["validation_pass"]:
        raise ValueError(f"Step 34 boundary-motion config is not valid for Step 35: {validation_rows}")
    report = build_boundary_motion_interface_report(config.boundary_motion_config_path)
    if not report["summary"]["no_op_pass"]:
        raise ValueError(f"Step 35 requires a passing Step 34 no-op interface report: {report['summary']}")
    return report


def _load_motion_rows(config: WallVelocityFieldConfig, mapping_inputs: dict) -> list[dict]:
    boundary_config = BoundaryMotionInterfaceConfig.from_json(_resolve_path(config.boundary_motion_config_path))
    if boundary_config.motion_mapping_output_path:
        output_path = _resolve_path(boundary_config.motion_mapping_output_path)
        if output_path.is_file():
            payload = _read_json(output_path)
            rows = payload.get("rows")
            if isinstance(rows, list):
                return rows
    return compute_region_motion_rows(
        mapping_inputs["mapping_config"],
        mapping_inputs["schedule_rows"],
        mapping_inputs["geometry_config"],
        mapping_inputs["region_config"],
        mapping_inputs["points"],
        mapping_inputs["masks"],
    )


def _region_samples_for_grid(geometry_config, region_config, grid_size: int) -> dict:
    points = sample_squid_proxy_region_points(geometry_config, count=int(grid_size) ** 3, seed=35 + int(grid_size))
    masks = sample_squid_proxy_regions(geometry_config, region_config, points)
    return {"points": points, "masks": masks}


def _bracket_rows(rows: list[dict], phase: float) -> tuple[dict, dict]:
    if phase < float(rows[0]["phase"]) or phase > float(rows[-1]["phase"]):
        raise ValueError(f"phase {phase} is outside motion row bounds")
    lower = rows[0]
    upper = rows[-1]
    for index, row in enumerate(rows):
        row_phase = float(row["phase"])
        if row_phase <= phase:
            lower = row
        if row_phase >= phase:
            upper = row
            break
        if index == len(rows) - 1:
            upper = row
    return lower, upper


def _region_velocity_vectors(region_id: str, points: np.ndarray, geometry_config: GeometryConfig, motion_row: dict) -> tuple[np.ndarray, np.ndarray]:
    pts = _as_points(points)
    if len(pts) == 0:
        return np.zeros((0, 3), dtype=np.float64), np.zeros(0, dtype=np.float64)
    if region_id == "mantle_outer":
        return _mantle_velocity_vectors(pts, geometry_config, motion_row)
    if region_id == "mantle_cavity_proxy":
        return _axis_velocity_vectors(
            pts,
            scale=float(motion_row["volume_rate"]) * 0.05,
            displacement_norm=abs(1.0 - float(motion_row["volume_scale"])) * 0.05,
        )
    if region_id == "funnel_outlet_proxy":
        return _axis_velocity_vectors(
            pts,
            scale=float(motion_row["aperture_rate"]) * 0.08,
            displacement_norm=abs(float(motion_row["aperture_scale"]) - 0.35) * 0.08,
        )
    raise ValueError(f"unsupported Step 35 region: {region_id}")


def _mantle_velocity_vectors(points: np.ndarray, geometry_config: GeometryConfig, motion_row: dict) -> tuple[np.ndarray, np.ndarray]:
    center = np.asarray(as_vec3(geometry_config.mantle_center, "mantle_center"), dtype=np.float64)
    radii = np.asarray(as_vec3(geometry_config.mantle_radii, "mantle_radii"), dtype=np.float64)
    normalized = (points - center) / radii
    norms = np.linalg.norm(normalized, axis=1)
    safe_norms = np.where(norms > 1.0e-12, norms, 1.0)
    unit = normalized / safe_norms[:, None]
    physical_radius = float(np.mean(radii))
    radial_distance = norms * physical_radius
    signed_velocity = radial_distance * float(motion_row["mantle_radius_rate"])
    vectors = unit * signed_velocity[:, None]
    displacement = radial_distance * abs(1.0 - float(motion_row["mantle_radius_scale"]))
    return vectors, displacement


def _axis_velocity_vectors(points: np.ndarray, scale: float, displacement_norm: float) -> tuple[np.ndarray, np.ndarray]:
    vectors = np.zeros((len(points), 3), dtype=np.float64)
    vectors[:, 1] = float(scale)
    displacement = np.full(len(points), float(displacement_norm), dtype=np.float64)
    return vectors, displacement


def _finite_wall_velocity_row(row: dict) -> bool:
    numeric_fields = [
        "grid_size",
        "phase",
        "active_cell_count",
        "sample_point_count",
        "velocity_norm_min",
        "velocity_norm_max",
        "velocity_norm_mean",
        "velocity_x_mean",
        "velocity_y_mean",
        "velocity_z_mean",
        "displacement_norm_max",
        "source_motion_velocity_norm_max",
        "mantle_radius_rate",
        "volume_rate",
        "aperture_rate",
    ]
    return all(math.isfinite(float(row[field])) for field in numeric_fields)


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


def _safe_mean(values) -> float:
    return float(np.mean(values)) if len(values) else 0.0


def _ordered_with_tolerance(minimum: float, mean: float, maximum: float, tolerance=1.0e-12) -> bool:
    return minimum >= -tolerance and minimum <= mean + tolerance and mean <= maximum + tolerance


def _read_json(path):
    with _resolve_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_csv(path, rows: list[dict], fieldnames: list[str]) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field, "")) for field in fieldnames})


def _write_json(path, payload) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
