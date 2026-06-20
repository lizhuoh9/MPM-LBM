import json
import math
import os
from pathlib import Path

import numpy as np

from .geometry_config import GeometryConfig
from .geometry_utils import as_vec3
from .squid_kinematics_config import SquidKinematicsScheduleConfig
from .squid_proxy_regions import sample_squid_proxy_region_points, sample_squid_proxy_regions
from .squid_region_config import load_squid_proxy_region_config
from .wall_velocity_application_config import (
    WallVelocityApplicationConfig,
    assert_valid_wall_velocity_application_config,
)
from .wall_velocity_config import WallVelocityFieldConfig
from .wall_velocity_field import interpolate_motion_rows_to_phase, load_wall_velocity_inputs


APPLICATION_SCOPE_NOTE = "Step 36 opt-in experimental solid_vel application only; no bounce-back formula change"


def load_wall_velocity_application_config(path) -> WallVelocityApplicationConfig:
    config = WallVelocityApplicationConfig.from_json(_resolve_path(path))
    assert_valid_wall_velocity_application_config(config, root=_repo_root())
    return config


def phase_for_lbm_step(application_config: WallVelocityApplicationConfig, lbm_step: int) -> float:
    wall_config = WallVelocityFieldConfig.from_json(_resolve_path(application_config.wall_velocity_config_path))
    schedule_config = SquidKinematicsScheduleConfig.from_json(_resolve_path(wall_config.schedule_config_path))
    cycle_period_steps = int(schedule_config.cycle_period_steps)
    if cycle_period_steps <= 0:
        raise ValueError("cycle_period_steps must be positive")
    return float(int(lbm_step) % cycle_period_steps) / float(cycle_period_steps)


def nearest_wall_velocity_phase(application_config: WallVelocityApplicationConfig, phase: float) -> float:
    wall_config = WallVelocityFieldConfig.from_json(_resolve_path(application_config.wall_velocity_config_path))
    samples = tuple(float(value) for value in wall_config.phase_samples)
    return min(samples, key=lambda sample: abs(sample - float(phase)))


def build_wall_velocity_grid(application_config, n_grid: int, phase: float) -> tuple[np.ndarray, dict]:
    if not isinstance(application_config, WallVelocityApplicationConfig):
        application_config = load_wall_velocity_application_config(application_config)
    assert_valid_wall_velocity_application_config(application_config, root=_repo_root())

    n = int(n_grid)
    if n <= 0:
        raise ValueError("n_grid must be positive")

    requested_phase = float(phase)
    selected_phase = nearest_wall_velocity_phase(application_config, requested_phase)
    wall_inputs = load_wall_velocity_inputs(application_config.wall_velocity_config_path)
    motion_by_region = interpolate_motion_rows_to_phase(wall_inputs["motion_rows"], selected_phase)
    geometry_config = GeometryConfig.from_json(_resolve_path(application_config.geometry_config_path))
    region_config = load_squid_proxy_region_config(_resolve_path(application_config.region_config_path))
    points = sample_squid_proxy_region_points(geometry_config, count=n**3, seed=36 + n)
    masks = sample_squid_proxy_regions(geometry_config, region_config, points)
    flat_grid = np.zeros((n**3, 3), dtype=np.float64)
    active_region_counts = {}
    nonzero_region_counts = {}
    for region_id in ("mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"):
        mask = np.asarray(masks[region_id], dtype=bool)
        selected = points[mask]
        vectors = _region_velocity_vectors(region_id, selected, geometry_config, motion_by_region[region_id])
        flat_grid[mask] += vectors
        active_region_counts[region_id] = int(np.count_nonzero(mask))
        nonzero_region_counts[region_id] = int(np.count_nonzero(np.linalg.norm(vectors, axis=1) > 0.0)) if len(vectors) else 0

    uncapped = flat_grid * float(application_config.wall_velocity_scale)
    capped = _cap_vectors(uncapped, float(application_config.wall_velocity_cap_lbm))
    uncapped_norm = np.linalg.norm(uncapped, axis=1)
    capped_norm = np.linalg.norm(capped, axis=1)
    applied_mask = capped_norm > 0.0
    summary = {
        "application_id": application_config.application_id,
        "n_grid": n,
        "requested_phase": requested_phase,
        "selected_phase": selected_phase,
        "wall_velocity_row_count": 63,
        "grid_size_count": len(wall_inputs["config"].grid_sizes),
        "phase_sample_count": len(wall_inputs["config"].phase_samples),
        "tracked_region_count": len(wall_inputs["config"].tracked_regions),
        "application_scale": float(application_config.wall_velocity_scale),
        "wall_velocity_cap_lbm": float(application_config.wall_velocity_cap_lbm),
        "active_cell_count": int(sum(active_region_counts.values())),
        "applied_cell_count": int(np.count_nonzero(applied_mask)),
        "max_uncapped_velocity_norm": _safe_max(uncapped_norm),
        "max_capped_velocity_norm": _safe_max(capped_norm),
        "mean_capped_velocity_norm": _safe_mean(capped_norm[applied_mask]) if np.any(applied_mask) else 0.0,
        "cap_pass": _safe_max(capped_norm) <= float(application_config.wall_velocity_cap_lbm) + 1.0e-12,
        "finite_pass": bool(np.all(np.isfinite(capped))),
        "active_region_counts": active_region_counts,
        "nonzero_region_counts": nonzero_region_counts,
        "lbm_population_update_enabled": bool(application_config.apply_to_lbm_populations),
        "modify_bounceback_formula": bool(application_config.modify_bounceback_formula),
        "jet_model_enabled": bool(application_config.jet_model_enabled),
        "actuation_claim_enabled": bool(application_config.actuation_claim_enabled),
        "scope_note": APPLICATION_SCOPE_NOTE,
    }
    return capped.reshape((n, n, n, 3)), summary


def apply_wall_velocity_to_lbm_solid_vel(lbm, velocity_grid: np.ndarray, application_config) -> dict:
    if not isinstance(application_config, WallVelocityApplicationConfig):
        application_config = load_wall_velocity_application_config(application_config)
    assert_valid_wall_velocity_application_config(application_config, root=_repo_root())
    before = np.asarray(lbm.solid_vel.to_numpy(), dtype=np.float64)
    velocity = np.asarray(velocity_grid, dtype=np.float64)
    if before.shape != velocity.shape:
        raise ValueError(f"velocity grid shape {velocity.shape} does not match lbm.solid_vel shape {before.shape}")
    applied_mask = np.linalg.norm(velocity, axis=3) > 0.0
    after = before.copy()
    if application_config.application_policy == "replace_capped":
        after[applied_mask] = velocity[applied_mask]
    elif application_config.application_policy == "additive_capped":
        after[applied_mask] = before[applied_mask] + velocity[applied_mask]
    else:
        raise ValueError(f"unsupported application_policy: {application_config.application_policy}")
    after[applied_mask] = _cap_vectors(after[applied_mask], float(application_config.wall_velocity_cap_lbm))
    lbm.solid_vel.from_numpy(after.astype(np.float32))

    delta = after - before
    delta_norm = np.linalg.norm(delta, axis=3)
    before_norm = np.linalg.norm(before, axis=3)
    after_norm = np.linalg.norm(after, axis=3)
    return {
        "applied_cell_count": int(np.count_nonzero(applied_mask)),
        "max_applied_velocity_norm": _safe_max(delta_norm[applied_mask]) if np.any(applied_mask) else 0.0,
        "mean_applied_velocity_norm": _safe_mean(delta_norm[applied_mask]) if np.any(applied_mask) else 0.0,
        "before_solid_vel_norm_max": _safe_max(before_norm),
        "after_solid_vel_norm_max": _safe_max(after_norm),
        "after_solid_vel_norm_mean_active": _safe_mean(after_norm[applied_mask]) if np.any(applied_mask) else 0.0,
        "cap_pass": _safe_max(after_norm[applied_mask]) <= float(application_config.wall_velocity_cap_lbm) + 1.0e-12 if np.any(applied_mask) else True,
        "lbm_population_update_count": 0,
        "apply_to_lbm_solid_vel": bool(application_config.apply_to_lbm_solid_vel),
        "apply_to_lbm_populations": bool(application_config.apply_to_lbm_populations),
        "modify_bounceback_formula": bool(application_config.modify_bounceback_formula),
    }


def summarize_wall_velocity_application(application_config, n_grid: int, phase: float) -> dict:
    if not isinstance(application_config, WallVelocityApplicationConfig):
        application_config = load_wall_velocity_application_config(application_config)
    velocity_grid, grid_summary = build_wall_velocity_grid(application_config, n_grid=n_grid, phase=phase)
    del velocity_grid
    summary = dict(grid_summary)
    summary.update(
        {
            "application_mode": application_config.application_mode,
            "target_lbm_field": application_config.target_lbm_field,
            "application_policy": application_config.application_policy,
            "apply_to_lbm_solid_vel": bool(application_config.apply_to_lbm_solid_vel),
            "apply_to_lbm_populations": bool(application_config.apply_to_lbm_populations),
            "apply_to_mpm": bool(application_config.apply_to_mpm),
            "apply_to_projector": bool(application_config.apply_to_projector),
            "modify_bounceback_formula": bool(application_config.modify_bounceback_formula),
            "report_pass": bool(
                grid_summary["finite_pass"]
                and grid_summary["cap_pass"]
                and grid_summary["applied_cell_count"] > 0
                and not application_config.apply_to_lbm_populations
                and not application_config.modify_bounceback_formula
            ),
        }
    )
    return summary


def build_wall_velocity_application_report(application_config, n_grid: int, phase: float, application_result: dict | None = None) -> dict:
    if not isinstance(application_config, WallVelocityApplicationConfig):
        application_config = load_wall_velocity_application_config(application_config)
    summary = summarize_wall_velocity_application(application_config, n_grid=n_grid, phase=phase)
    if application_result:
        summary.update(application_result)
        summary["report_pass"] = bool(
            summary["finite_pass"]
            and summary["cap_pass"]
            and int(summary["applied_cell_count"]) > 0
            and float(summary["max_applied_velocity_norm"]) <= float(application_config.wall_velocity_cap_lbm) + 1.0e-12
            and int(summary["lbm_population_update_count"]) == 0
            and not bool(summary["modify_bounceback_formula"])
        )
    return {"summary": summary, "config": application_config.to_dict()}


def apply_wall_velocity_application_to_lbm(lbm, application_config_path, n_grid: int, lbm_step: int, report_path=None) -> dict:
    config = load_wall_velocity_application_config(application_config_path)
    requested_phase = phase_for_lbm_step(config, lbm_step)
    velocity_grid, grid_summary = build_wall_velocity_grid(config, n_grid=n_grid, phase=requested_phase)
    application_result = apply_wall_velocity_to_lbm_solid_vel(lbm, velocity_grid, config)
    summary = dict(grid_summary)
    summary.update(
        {
            "application_mode": config.application_mode,
            "target_lbm_field": config.target_lbm_field,
            "application_policy": config.application_policy,
            "apply_to_lbm_solid_vel": bool(config.apply_to_lbm_solid_vel),
            "apply_to_lbm_populations": bool(config.apply_to_lbm_populations),
            "apply_to_mpm": bool(config.apply_to_mpm),
            "apply_to_projector": bool(config.apply_to_projector),
            "driver_lbm_step": int(lbm_step),
        }
    )
    summary.update(application_result)
    summary["report_pass"] = bool(
        summary["finite_pass"]
        and summary["cap_pass"]
        and int(summary["applied_cell_count"]) > 0
        and float(summary["max_applied_velocity_norm"]) <= float(config.wall_velocity_cap_lbm) + 1.0e-12
        and int(summary["lbm_population_update_count"]) == 0
        and not bool(summary["modify_bounceback_formula"])
    )
    report = {"summary": summary, "config": config.to_dict()}
    if report_path:
        write_wall_velocity_application_report(report, report_path)
    return report


def write_wall_velocity_application_report(report, path) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")


def _region_velocity_vectors(region_id: str, points: np.ndarray, geometry_config: GeometryConfig, motion_row: dict) -> np.ndarray:
    pts = _as_points(points)
    if len(pts) == 0:
        return np.zeros((0, 3), dtype=np.float64)
    if region_id == "mantle_outer":
        return _mantle_velocity_vectors(pts, geometry_config, motion_row)
    if region_id == "mantle_cavity_proxy":
        return _axis_velocity_vectors(pts, float(motion_row["volume_rate"]) * 0.05)
    if region_id == "funnel_outlet_proxy":
        return _axis_velocity_vectors(pts, float(motion_row["aperture_rate"]) * 0.08)
    raise ValueError(f"unsupported Step 36 region: {region_id}")


def _mantle_velocity_vectors(points: np.ndarray, geometry_config: GeometryConfig, motion_row: dict) -> np.ndarray:
    center = np.asarray(as_vec3(geometry_config.mantle_center, "mantle_center"), dtype=np.float64)
    radii = np.asarray(as_vec3(geometry_config.mantle_radii, "mantle_radii"), dtype=np.float64)
    normalized = (points - center) / radii
    norms = np.linalg.norm(normalized, axis=1)
    safe_norms = np.where(norms > 1.0e-12, norms, 1.0)
    unit = normalized / safe_norms[:, None]
    physical_radius = float(np.mean(radii))
    radial_distance = norms * physical_radius
    signed_velocity = radial_distance * float(motion_row["mantle_radius_rate"])
    return unit * signed_velocity[:, None]


def _axis_velocity_vectors(points: np.ndarray, scale: float) -> np.ndarray:
    vectors = np.zeros((len(points), 3), dtype=np.float64)
    vectors[:, 1] = float(scale)
    return vectors


def _cap_vectors(vectors: np.ndarray, cap: float) -> np.ndarray:
    arr = np.asarray(vectors, dtype=np.float64).copy()
    if arr.size == 0:
        return arr
    norms = np.linalg.norm(arr, axis=-1)
    mask = norms > float(cap)
    if np.any(mask):
        arr[mask] *= (float(cap) / norms[mask])[..., None]
    return arr


def _as_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("points must have shape (n, 3)")
    if not np.all(np.isfinite(array)):
        raise ValueError("points must be finite")
    return array


def _safe_max(values) -> float:
    array = np.asarray(values, dtype=np.float64)
    return float(np.max(array)) if array.size else 0.0


def _safe_mean(values) -> float:
    array = np.asarray(values, dtype=np.float64)
    return float(np.mean(array)) if array.size else 0.0


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
