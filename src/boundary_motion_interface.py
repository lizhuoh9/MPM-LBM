import json
import math
import os
from pathlib import Path

from .boundary_motion_config import (
    BoundaryMotionInterfaceConfig,
    execution_flag_enabled_count,
    execution_flags,
    summarize_boundary_motion_config_validation,
    validate_boundary_motion_interface_config,
)
from .squid_kinematics_config import SquidKinematicsScheduleConfig
from .squid_kinematics_schedule import schedule_rows, summarize_schedule
from .squid_motion_mapping import compute_region_motion_rows, load_motion_mapping_inputs, summarize_motion_rows


BOUNDARY_MOTION_SCOPE_NOTE = "Step 34 diagnostic-only boundary-motion driver interface; no LBM state update"


def build_boundary_motion_interface_report(config_path, boundary_motion_mode="prescribed_kinematic") -> dict:
    config = BoundaryMotionInterfaceConfig.from_json(_resolve_path(config_path))
    validation_rows = validate_boundary_motion_interface_config(config, root=_repo_root())
    validation_summary = summarize_boundary_motion_config_validation(validation_rows)
    if not validation_summary["validation_pass"]:
        raise ValueError(f"Boundary motion interface config validation failed: {validation_rows}")

    schedule = _load_schedule_rows(config)
    motion_rows = _load_motion_rows(config)
    schedule_summary = summarize_schedule(schedule)
    motion_summary = summarize_motion_rows(motion_rows)
    tracked_regions = sorted({row["region_id"] for row in motion_rows})
    finite_motion_pass = _finite_motion_rows(motion_rows)
    no_op_flags = execution_flags(config)
    no_op_pass = bool(
        config.diagnostic_only
        and validation_summary["validation_pass"]
        and execution_flag_enabled_count(config) == 0
        and int(schedule_summary["row_count"]) == int(config.expected_schedule_row_count)
        and int(motion_summary["row_count"]) == int(config.expected_motion_row_count)
        and int(motion_summary["tracked_region_count"]) == int(config.expected_tracked_region_count)
        and bool(schedule_summary["finite_pass"])
        and bool(motion_summary["finite_pass"])
        and finite_motion_pass
    )
    summary = {
        "interface_id": config.interface_id,
        "boundary_motion_mode": boundary_motion_mode,
        "diagnostic_only": bool(config.diagnostic_only),
        "deterministic": bool(config.deterministic),
        "config_validation_pass": bool(validation_summary["validation_pass"]),
        "config_validation_row_count": int(validation_summary["row_count"]),
        "config_validation_pass_count": int(validation_summary["pass_count"]),
        "schedule_config_path": config.schedule_config_path,
        "schedule_output_path": config.schedule_output_path,
        "schedule_row_count": int(schedule_summary["row_count"]),
        "expected_schedule_row_count": int(config.expected_schedule_row_count),
        "schedule_finite_pass": bool(schedule_summary["finite_pass"]),
        "motion_mapping_config_path": config.motion_mapping_config_path,
        "motion_mapping_output_path": config.motion_mapping_output_path,
        "motion_mapping_row_count": int(motion_summary["row_count"]),
        "expected_motion_row_count": int(config.expected_motion_row_count),
        "tracked_region_count": int(motion_summary["tracked_region_count"]),
        "expected_tracked_region_count": int(config.expected_tracked_region_count),
        "tracked_regions": tracked_regions,
        "motion_finite_pass": bool(motion_summary["finite_pass"]),
        "motion_bounds_pass": bool(motion_summary["bounds_pass"]),
        "finite_motion_pass": bool(finite_motion_pass),
        "driver_integration_enabled_count": int(motion_summary["driver_integration_enabled_count"]),
        "lbm_wall_velocity_enabled_count": int(motion_summary["lbm_wall_velocity_enabled_count"]),
        "jet_model_enabled_count": int(motion_summary["jet_model_enabled_count"]),
        "actuation_enabled_count": int(motion_summary["actuation_enabled_count"]),
        "execution_flag_enabled_count": int(execution_flag_enabled_count(config)),
        "no_op_pass": no_op_pass,
        "scope_note": BOUNDARY_MOTION_SCOPE_NOTE,
    }
    summary.update(no_op_flags)
    return {
        "summary": summary,
        "config": config.to_dict(),
        "validation_summary": validation_summary,
        "validation_rows": validation_rows,
        "schedule_summary": schedule_summary,
        "motion_summary": motion_summary,
    }


def write_boundary_motion_interface_report(config_path, report_path, boundary_motion_mode="prescribed_kinematic") -> dict:
    payload = build_boundary_motion_interface_report(config_path, boundary_motion_mode=boundary_motion_mode)
    _write_json(report_path, payload)
    return payload


def build_static_boundary_motion_interface_report() -> dict:
    summary = {
        "interface_id": "step34_static_boundary_motion_interface",
        "boundary_motion_mode": "static",
        "diagnostic_only": True,
        "deterministic": True,
        "config_validation_pass": True,
        "config_validation_row_count": 0,
        "config_validation_pass_count": 0,
        "schedule_row_count": 0,
        "expected_schedule_row_count": 0,
        "schedule_finite_pass": True,
        "motion_mapping_row_count": 0,
        "expected_motion_row_count": 0,
        "tracked_region_count": 0,
        "expected_tracked_region_count": 0,
        "tracked_regions": [],
        "motion_finite_pass": True,
        "motion_bounds_pass": True,
        "finite_motion_pass": True,
        "driver_integration_enabled_count": 0,
        "lbm_wall_velocity_enabled_count": 0,
        "jet_model_enabled_count": 0,
        "actuation_enabled_count": 0,
        "execution_flag_enabled_count": 0,
        "driver_integration_enabled": False,
        "lbm_wall_velocity_enabled": False,
        "lbm_population_update_enabled": False,
        "mpm_grid_velocity_enabled": False,
        "projector_integration_enabled": False,
        "coupling_integration_enabled": False,
        "moving_bounceback_update_enabled": False,
        "jet_model_enabled": False,
        "actuation_enabled": False,
        "no_op_pass": True,
        "scope_note": "Step 34 static boundary-motion mode; no boundary-motion config loaded",
    }
    return {"summary": summary}


def write_static_boundary_motion_interface_report(report_path) -> dict:
    payload = build_static_boundary_motion_interface_report()
    _write_json(report_path, payload)
    return payload


def _load_schedule_rows(config: BoundaryMotionInterfaceConfig) -> list[dict]:
    if config.schedule_output_path and _resolve_path(config.schedule_output_path).is_file():
        return _read_rows_from_output(config.schedule_output_path)
    schedule_config = SquidKinematicsScheduleConfig.from_json(_resolve_path(config.schedule_config_path))
    return schedule_rows(schedule_config)


def _load_motion_rows(config: BoundaryMotionInterfaceConfig) -> list[dict]:
    if config.motion_mapping_output_path and _resolve_path(config.motion_mapping_output_path).is_file():
        return _read_rows_from_output(config.motion_mapping_output_path)
    inputs = load_motion_mapping_inputs(config.motion_mapping_config_path)
    return compute_region_motion_rows(
        inputs["mapping_config"],
        inputs["schedule_rows"],
        inputs["geometry_config"],
        inputs["region_config"],
        inputs["points"],
        inputs["masks"],
    )


def _read_rows_from_output(path) -> list[dict]:
    payload = _read_json(path)
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError(f"{path} must contain a rows list")
    return rows


def _finite_motion_rows(rows: list[dict]) -> bool:
    numeric_fields = (
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
    for row in rows:
        for field in numeric_fields:
            if not math.isfinite(float(row[field])):
                return False
    return True


def _read_json(path):
    with _resolve_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, payload):
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
