import csv
import json
import math
import os
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEP43_GEOMETRY_CONFIG_PATH = "configs/step30_squid_proxy_geometry.json"
STEP43_GEOMETRY_MOTION_CONFIG_PATH = "configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json"

STEP43_STATIC_DRIVER_CONFIGS = [
    "configs/step43_static_48_moving_boundary.json",
    "configs/step43_static_48_link_area.json",
]

STEP43_DIAGNOSTIC_DRIVER_CONFIGS = [
    "configs/step43_diagnostic_geometry_motion_48_moving_boundary.json",
    "configs/step43_diagnostic_geometry_motion_48_link_area.json",
]

STEP43_DRIVER_FIELDS = [
    "case",
    "candidate_id",
    "mode_class",
    "geometry_type",
    "geometry_source",
    "mode",
    "reaction_transfer_mode",
    "boundary_motion_mode",
    "boundary_motion_config_path",
    "boundary_motion_report_enabled",
    "boundary_motion_report_written",
    "boundary_motion_interface_report_path",
    "wall_velocity_application_mode",
    "wall_velocity_application_config_path",
    "wall_velocity_application_report_enabled",
    "wall_velocity_application_report_written",
    "wall_velocity_application_report_path",
    "geometry_motion_mode",
    "geometry_motion_config_path",
    "geometry_motion_report_enabled",
    "geometry_motion_report_written",
    "geometry_motion_interface_report_path",
    "geometry_motion_application_mode",
    "geometry_motion_application_config_path",
    "geometry_motion_application_report_enabled",
    "geometry_motion_no_op_pass",
    "geometry_motion_displacement_row_count",
    "geometry_motion_phase_sample_count",
    "geometry_motion_tracked_region_count",
    "geometry_motion_mutation_flag_enabled_count",
    "apply_to_driver",
    "apply_to_mpm_particles",
    "apply_to_lbm_solid_phi",
    "apply_to_lbm_solid_vel",
    "apply_to_projection",
    "update_dynamic_solid",
    "recompute_boundary_links",
    "mutate_geometry_state",
    "quality_check_enabled",
    "quality_check_strict",
    "quality_pass",
    "quality_severity",
    "quality_warnings_count",
    "quality_reasons_count",
    "quality_gate_strict",
    "quality_report_path",
    "driver_timing_path",
    "n_grid",
    "n_particles",
    "n_lbm_steps",
    "mpm_substeps_per_lbm_step",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "diagnostics_row_count",
    "rho_min_global",
    "rho_max_global",
    "lbm_max_v_global",
    "mpm_min_J_global",
    "mpm_max_speed_global",
    "projected_mass_min",
    "projected_mass_max",
    "active_cell_count",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count_min",
    "bb_link_count_max",
    "bb_max_correction_max",
    "active_reaction_particle_count_max",
    "max_grid_reaction_norm",
    "area_scale_final",
    "area_scale_min",
    "area_scale_max",
    "raw_area_scale_final",
    "has_nan",
    "has_inf",
    "stable",
    "notes",
]


def load_geometry_motion_config():
    from src.geometry_motion_config import GeometryMotionInterfaceConfig

    return GeometryMotionInterfaceConfig.from_json(resolve_path(STEP43_GEOMETRY_MOTION_CONFIG_PATH))


def run_step43_driver_case(driver_config_path, out_dir) -> dict:
    from src.fsi_config import FSIDriverConfig
    from src.fsi_driver import FSIDriver3D
    from src.real_geometry_feasibility import summarize_short_driver_diagnostics
    from src.wall_velocity_application_envelope import summarize_driver_stability_envelope

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    enforce_step43_driver_config(config, driver_config_path)
    driver = FSIDriver3D(config, str(out_dir))
    try:
        diagnostics = driver.run()
        if not diagnostics:
            raise RuntimeError(f"empty diagnostics for Step 43 driver case: {driver_config_path}")

        case = case_name(driver_config_path)
        quality_path = Path(out_dir) / "geometry_quality_report.json"
        timing_path = Path(out_dir) / "driver_timing.json"
        write_json(timing_path, driver.performance_row())
        short_row = summarize_short_driver_diagnostics(config, diagnostics, driver, quality_path)
        stability = summarize_driver_stability_envelope(diagnostics)
        row = {
            "case": case,
            "candidate_id": "squid_proxy_geometry_motion_driver_interface",
            "mode_class": mode_class(config),
            "geometry_type": config.geometry_type,
            "geometry_source": config.geometry_config_path,
            "mode": config.coupling_mode,
            "reaction_transfer_mode": config.reaction_transfer_mode,
            "driver_timing_path": relative_path(timing_path),
            "notes": "Step 43 controlled geometry-motion driver interface no-op contract",
        }
        row.update(boundary_motion_fields(config, out_dir))
        row.update(wall_velocity_application_fields(config, out_dir))
        row.update(geometry_motion_fields(config, driver, out_dir))
        row.update(quality_fields(short_row))
        row.update(config_fields(config))
        row.update(stability)
        row.update(area_fields(short_row))
        row["stable"] = bool(step43_stability_pass(row) and row["quality_pass"] and geometry_motion_row_pass(row))
        row["has_nan"] = bool(row["has_nan"] or not finite_values(row, excluded=step43_driver_string_fields()))
        row["has_inf"] = row["has_nan"]
        assert_step43_driver_row(row)
        return row
    finally:
        cleanup_generated_driver_geometry(driver)


def cleanup_generated_driver_geometry(driver) -> None:
    geo_path = getattr(driver, "geo_path", "")
    if not geo_path:
        return
    resolved = resolve_path(geo_path)
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        return
    if resolved.is_file() and resolved.name.startswith("geo_all_fluid_") and resolved.suffix == ".dat":
        resolved.unlink()


def enforce_step43_driver_config(config, config_path):
    if config.geometry_type != "squid_proxy":
        raise RuntimeError(f"{config_path} must use geometry_type=squid_proxy")
    if config.geometry_config_path != STEP43_GEOMETRY_CONFIG_PATH:
        raise RuntimeError(f"{config_path} must reuse Step 30 squid proxy geometry")
    if int(config.n_grid) != 48 or int(config.n_particles) != 4096:
        raise RuntimeError(f"{config_path} must use n_grid=48 and n_particles=4096")
    if int(config.n_lbm_steps) != 5 or int(config.mpm_substeps_per_lbm_step) != 5:
        raise RuntimeError(f"{config_path} must use 5 LBM steps and 5 MPM substeps")
    if tuple(float(value) for value in config.target_u_lbm) != (0.0, 0.0, 0.0):
        raise RuntimeError(f"{config_path} must keep target_u_lbm zero")
    if int(config.output_interval) != 1:
        raise RuntimeError(f"{config_path} must write diagnostics every LBM step")
    if config.write_vtk or config.write_particles:
        raise RuntimeError(f"{config_path} must disable VTK and particle outputs")
    if not config.quality_check_enabled or not config.quality_check_strict:
        raise RuntimeError(f"{config_path} must enable strict quality checks")
    if config.coupling_mode != "moving_boundary":
        raise RuntimeError(f"{config_path} must use moving_boundary")
    if config.reaction_transfer_mode not in {"engineering", "link_area_experimental"}:
        raise RuntimeError(f"{config_path} has unsupported transfer mode")
    if config.reaction_transfer_mode == "link_area_experimental" and config.link_area_policy != "inverse_length":
        raise RuntimeError(f"{config_path} link-area rows must use inverse_length")
    if config.boundary_motion_mode != "static":
        raise RuntimeError(f"{config_path} must keep boundary_motion_mode static")
    if config.wall_velocity_application_mode != "disabled" or config.wall_velocity_application_config_path is not None:
        raise RuntimeError(f"{config_path} must keep wall velocity application disabled")
    if config.geometry_motion_mode == "static":
        if config.geometry_motion_application_mode != "disabled" or config.geometry_motion_config_path is not None:
            raise RuntimeError(f"{config_path} static geometry motion must stay disabled")
    elif config.geometry_motion_mode == "prescribed_kinematic":
        if config.geometry_motion_application_mode != "diagnostic_only":
            raise RuntimeError(f"{config_path} prescribed geometry motion must be diagnostic_only")
        if config.geometry_motion_config_path != STEP43_GEOMETRY_MOTION_CONFIG_PATH:
            raise RuntimeError(f"{config_path} must use the Step 43 geometry-motion config")
        if config.geometry_motion_application_config_path != STEP43_GEOMETRY_MOTION_CONFIG_PATH:
            raise RuntimeError(f"{config_path} must use the Step 43 geometry-motion application config")
    else:
        raise RuntimeError(f"unsupported geometry_motion_mode: {config.geometry_motion_mode}")


def boundary_motion_fields(config, out_dir) -> dict:
    report_path = Path(out_dir) / "boundary_motion_interface_report.json"
    return {
        "boundary_motion_mode": config.boundary_motion_mode,
        "boundary_motion_config_path": config.boundary_motion_config_path or "",
        "boundary_motion_report_enabled": bool(config.boundary_motion_report_enabled),
        "boundary_motion_report_written": report_path.is_file(),
        "boundary_motion_interface_report_path": relative_path(report_path) if report_path.is_file() else "",
    }


def wall_velocity_application_fields(config, out_dir) -> dict:
    report_path = Path(out_dir) / "wall_velocity_application_report.json"
    return {
        "wall_velocity_application_mode": config.wall_velocity_application_mode,
        "wall_velocity_application_config_path": config.wall_velocity_application_config_path or "",
        "wall_velocity_application_report_enabled": bool(config.wall_velocity_application_report_enabled),
        "wall_velocity_application_report_written": report_path.is_file(),
        "wall_velocity_application_report_path": relative_path(report_path) if report_path.is_file() else "",
    }


def geometry_motion_fields(config, driver, out_dir) -> dict:
    report_path = Path(out_dir) / "geometry_motion_interface_report.json"
    report = driver.geometry_motion_interface_report or {}
    summary = report.get("summary", {})
    flags = {
        "apply_to_driver": False,
        "apply_to_mpm_particles": False,
        "apply_to_lbm_solid_phi": False,
        "apply_to_lbm_solid_vel": False,
        "apply_to_projection": False,
        "update_dynamic_solid": False,
        "recompute_boundary_links": False,
        "mutate_geometry_state": False,
    }
    flags.update({key: bool(summary.get(key, flags[key])) for key in flags})
    return {
        "geometry_motion_mode": config.geometry_motion_mode,
        "geometry_motion_config_path": config.geometry_motion_config_path or "",
        "geometry_motion_report_enabled": bool(config.geometry_motion_report_enabled),
        "geometry_motion_report_written": report_path.is_file(),
        "geometry_motion_interface_report_path": relative_path(report_path) if report_path.is_file() else "",
        "geometry_motion_application_mode": config.geometry_motion_application_mode,
        "geometry_motion_application_config_path": config.geometry_motion_application_config_path or "",
        "geometry_motion_application_report_enabled": bool(config.geometry_motion_application_report_enabled),
        "geometry_motion_no_op_pass": bool(summary.get("no_op_pass", config.geometry_motion_application_mode == "disabled")),
        "geometry_motion_displacement_row_count": int(summary.get("displacement_row_count", 0)),
        "geometry_motion_phase_sample_count": int(summary.get("phase_sample_count", 0)),
        "geometry_motion_tracked_region_count": int(summary.get("tracked_region_count", 0)),
        "geometry_motion_mutation_flag_enabled_count": int(summary.get("mutation_flag_enabled_count", 0)),
        **flags,
    }


def quality_fields(short_row) -> dict:
    return {
        "quality_check_enabled": bool(short_row["quality_check_enabled"]),
        "quality_check_strict": bool(short_row["quality_check_strict"]),
        "quality_pass": bool(short_row["quality_pass"]),
        "quality_severity": short_row["quality_severity"],
        "quality_warnings_count": int(short_row["quality_warnings_count"]),
        "quality_reasons_count": int(short_row["quality_reasons_count"]),
        "quality_gate_strict": bool(short_row["quality_gate_strict"]),
        "quality_report_path": short_row["quality_report_path"],
    }


def config_fields(config) -> dict:
    return {
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
    }


def area_fields(short_row) -> dict:
    return {
        "area_scale_final": float(short_row["area_scale_final"]),
        "area_scale_min": float(short_row["area_scale_min"]),
        "area_scale_max": float(short_row["area_scale_max"]),
        "raw_area_scale_final": float(short_row["raw_area_scale_final"]),
    }


def mode_class(config) -> str:
    return "diagnostic" if config.geometry_motion_application_mode == "diagnostic_only" else "static"


def geometry_motion_row_pass(row) -> bool:
    if row["mode_class"] == "static":
        return row["geometry_motion_mode"] == "static" and row["geometry_motion_application_mode"] == "disabled" and not row["geometry_motion_report_written"]
    return bool(
        row["geometry_motion_mode"] == "prescribed_kinematic"
        and row["geometry_motion_application_mode"] == "diagnostic_only"
        and row["geometry_motion_report_written"]
        and row["geometry_motion_no_op_pass"]
        and int(row["geometry_motion_displacement_row_count"]) == 243
        and int(row["geometry_motion_mutation_flag_enabled_count"]) == 0
        and not any(bool(row[field]) for field in geometry_motion_flag_fields())
    )


def step43_stability_pass(row) -> bool:
    return bool(
        not as_bool(row["has_nan"])
        and not as_bool(row["has_inf"])
        and int(row["completed_lbm_steps"]) >= 5
        and int(row["total_mpm_substeps"]) >= 25
        and float(row["rho_min_global"]) > 0.95
        and float(row["rho_max_global"]) < 1.05
        and float(row["lbm_max_v_global"]) < 0.1
        and float(row["mpm_min_J_global"]) > 0.0
        and float(row["mpm_max_speed_global"]) < 10.0
        and float(row["projected_mass_min"]) > 0.0
        and float(row["projected_mass_max"]) > 0.0
        and int(row["active_cell_count"]) > 0
        and int(row["bb_link_count_max"]) > 0
        and math.isfinite(float(row["hydro_force_max_norm"]))
        and math.isfinite(float(row["bb_max_correction_max"]))
        and math.isfinite(float(row["max_grid_reaction_norm"]))
    )


def assert_step43_driver_row(row):
    if not as_bool(row["quality_check_enabled"]) or not as_bool(row["quality_check_strict"]):
        raise RuntimeError(f"Step 43 row must use strict quality checks: {row}")
    if not as_bool(row["quality_pass"]) or not as_bool(row["quality_gate_strict"]):
        raise RuntimeError(f"Step 43 quality gate failed: {row}")
    if row["quality_severity"] != "ok" or int(row["quality_warnings_count"]) != 0 or int(row["quality_reasons_count"]) != 0:
        raise RuntimeError(f"Step 43 quality report must be clean: {row}")
    if int(row["completed_lbm_steps"]) < 5 or int(row["total_mpm_substeps"]) < 25:
        raise RuntimeError(f"Step 43 row did not complete the short smoke window: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 43 density envelope out of range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 43 velocity envelope out of range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0 or float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 43 MPM envelope out of range: {row}")
    if float(row["projected_mass_min"]) <= 0.0 or float(row["projected_mass_max"]) <= 0.0:
        raise RuntimeError(f"Step 43 projected mass envelope is invalid: {row}")
    if int(row["active_cell_count"]) <= 0 or int(row["bb_link_count_max"]) <= 0:
        raise RuntimeError(f"Step 43 moving-boundary diagnostics are missing: {row}")
    if as_bool(row["has_nan"]) or as_bool(row["has_inf"]) or not finite_values(row, excluded=step43_driver_string_fields()):
        raise RuntimeError(f"Step 43 row has non-finite values: {row}")
    if not geometry_motion_row_pass(row):
        raise RuntimeError(f"Step 43 geometry motion fields failed: {row}")
    if not as_bool(row["stable"]):
        raise RuntimeError(f"Step 43 row is not stable: {row}")


def driver_summary(rows: list[dict]) -> dict:
    summary = {
        "row_count": len(rows),
        "static_row_count": sum(1 for row in rows if row["mode_class"] == "static"),
        "diagnostic_row_count": sum(1 for row in rows if row["mode_class"] == "diagnostic"),
        "engineering_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "engineering"),
        "link_area_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "link_area_experimental"),
        "stable_count": sum(1 for row in rows if as_bool(row["stable"])),
        "quality_pass_count": sum(1 for row in rows if as_bool(row["quality_pass"])),
        "geometry_motion_report_count": sum(1 for row in rows if as_bool(row["geometry_motion_report_written"])),
        "min_completed_lbm_steps": min(int(row["completed_lbm_steps"]) for row in rows),
        "min_total_mpm_substeps": min(int(row["total_mpm_substeps"]) for row in rows),
        "min_rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "max_lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows),
        "min_mpm_min_J_global": min(float(row["mpm_min_J_global"]) for row in rows),
        "max_mpm_max_speed_global": max(float(row["mpm_max_speed_global"]) for row in rows),
        "min_projected_mass_min": min(float(row["projected_mass_min"]) for row in rows),
        "min_active_cell_count": min(int(row["active_cell_count"]) for row in rows),
        "min_bb_link_count_max": min(int(row["bb_link_count_max"]) for row in rows),
        "no_op_pass_all": all(as_bool(row["geometry_motion_no_op_pass"]) for row in rows),
        "geometry_motion_mode_all_static": all(row["geometry_motion_mode"] == "static" for row in rows),
        "geometry_motion_application_mode_all_disabled": all(row["geometry_motion_application_mode"] == "disabled" for row in rows),
        "geometry_motion_mode_all_prescribed": all(row["geometry_motion_mode"] == "prescribed_kinematic" for row in rows),
        "geometry_motion_application_mode_all_diagnostic_only": all(row["geometry_motion_application_mode"] == "diagnostic_only" for row in rows),
    }
    summary["driver_pass"] = bool(
        summary["stable_count"] == len(rows)
        and summary["quality_pass_count"] == len(rows)
        and summary["min_completed_lbm_steps"] >= 5
        and summary["min_total_mpm_substeps"] >= 25
        and summary["min_rho_min_global"] > 0.95
        and summary["max_rho_max_global"] < 1.05
        and summary["max_lbm_max_v_global"] < 0.1
        and summary["min_mpm_min_J_global"] > 0.0
        and summary["min_projected_mass_min"] > 0.0
        and summary["min_active_cell_count"] > 0
        and summary["min_bb_link_count_max"] > 0
        and finite_values(summary)
    )
    return summary


def assert_driver_summary(summary: dict, expected_mode_class: str) -> None:
    if int(summary["row_count"]) != 2:
        raise RuntimeError(f"Step 43 driver row count is wrong: {summary}")
    if int(summary["engineering_row_count"]) != 1 or int(summary["link_area_row_count"]) != 1:
        raise RuntimeError(f"Step 43 transfer split is wrong: {summary}")
    if int(summary["stable_count"]) != 2 or int(summary["quality_pass_count"]) != 2:
        raise RuntimeError(f"all Step 43 driver rows must be stable and quality-passing: {summary}")
    if expected_mode_class == "static":
        if not summary["geometry_motion_mode_all_static"] or not summary["geometry_motion_application_mode_all_disabled"]:
            raise RuntimeError(f"Step 43 static rows must keep geometry motion disabled: {summary}")
    if expected_mode_class == "diagnostic":
        if not summary["geometry_motion_mode_all_prescribed"] or not summary["geometry_motion_application_mode_all_diagnostic_only"]:
            raise RuntimeError(f"Step 43 diagnostic rows must use prescribed diagnostic-only geometry motion: {summary}")
        if int(summary["geometry_motion_report_count"]) != 2 or not summary["no_op_pass_all"]:
            raise RuntimeError(f"Step 43 diagnostic reports must be no-op and present: {summary}")
    if not summary["driver_pass"]:
        raise RuntimeError(f"Step 43 driver summary failed: {summary}")


def geometry_motion_flag_fields():
    return (
        "apply_to_driver",
        "apply_to_mpm_particles",
        "apply_to_lbm_solid_phi",
        "apply_to_lbm_solid_vel",
        "apply_to_projection",
        "update_dynamic_solid",
        "recompute_boundary_links",
        "mutate_geometry_state",
    )


def read_json(path):
    with resolve_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def read_csv_rows(path):
    with resolve_path(path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path, rows, fieldnames):
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field, "")) for field in fieldnames})


def write_rows_csv_npz(rows, csv_path, npz_path, fieldnames):
    write_csv_rows(csv_path, rows, fieldnames)
    payload = {"columns": np.asarray(fieldnames)}
    for field in fieldnames:
        values = [row.get(field, "") for row in rows]
        if is_string_field(values):
            payload[field + "s"] = np.asarray([str(value) for value in values])
            continue
        try:
            payload[field] = np.asarray([bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            payload[field + "s"] = np.asarray([str(value) for value in values])
    resolved = resolve_path(npz_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    np.savez(resolved, **payload)


def write_log(relative_path, lines):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line).rstrip() + "\n")


def resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return ROOT / path_obj


def relative_path(path) -> str:
    return os.path.relpath(resolve_path(path), ROOT).replace("\\", "/")


def case_name(config_path):
    return Path(config_path).stem.removeprefix("step43_")


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def check_row(check, passed, value, notes):
    return {"check": check, "pass": bool(passed), "value": value, "notes": notes}


def csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def fieldnames_from_rows(rows: list[dict]) -> list[str]:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def finite_values(row, excluded=()) -> bool:
    values = row.values() if isinstance(row, dict) else row
    iterable = ((key, value) for key, value in row.items() if key not in excluded) if isinstance(row, dict) else ((None, value) for value in values)
    for _, value in iterable:
        if isinstance(value, bool) or value == "":
            continue
        if isinstance(value, (list, tuple)):
            if not finite_values(value):
                return False
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True


def step43_driver_string_fields():
    return {
        "case",
        "candidate_id",
        "mode_class",
        "geometry_type",
        "geometry_source",
        "mode",
        "reaction_transfer_mode",
        "boundary_motion_mode",
        "boundary_motion_config_path",
        "boundary_motion_report_enabled",
        "boundary_motion_report_written",
        "boundary_motion_interface_report_path",
        "wall_velocity_application_mode",
        "wall_velocity_application_config_path",
        "wall_velocity_application_report_enabled",
        "wall_velocity_application_report_written",
        "wall_velocity_application_report_path",
        "geometry_motion_mode",
        "geometry_motion_config_path",
        "geometry_motion_report_enabled",
        "geometry_motion_report_written",
        "geometry_motion_interface_report_path",
        "geometry_motion_application_mode",
        "geometry_motion_application_config_path",
        "geometry_motion_application_report_enabled",
        "geometry_motion_no_op_pass",
        "apply_to_driver",
        "apply_to_mpm_particles",
        "apply_to_lbm_solid_phi",
        "apply_to_lbm_solid_vel",
        "apply_to_projection",
        "update_dynamic_solid",
        "recompute_boundary_links",
        "mutate_geometry_state",
        "quality_check_enabled",
        "quality_check_strict",
        "quality_pass",
        "quality_severity",
        "quality_gate_strict",
        "quality_report_path",
        "driver_timing_path",
        "has_nan",
        "has_inf",
        "stable",
        "notes",
    }


def is_string_field(values) -> bool:
    for value in values:
        if value == "":
            continue
        try:
            bool_to_float(value)
        except (TypeError, ValueError):
            return True
    return False


def bool_to_float(value):
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip().lower()
    if text in {"true", "false"}:
        return 1.0 if text == "true" else 0.0
    return float(value)


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}
