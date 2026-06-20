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

STEP37_APPLICATION_CONFIG_PATH = "configs/step36_wall_velocity_application_solid_vel_experimental.json"
STEP37_GEOMETRY_CONFIG_PATH = "configs/step30_squid_proxy_geometry.json"
STEP37_BOUNDARY_MOTION_CONFIG_PATH = "configs/step34_boundary_motion_interface_prescribed_kinematic.json"

STEP37_DRIVER_CONFIGS = [
    "configs/step37_static_48_moving_boundary.json",
    "configs/step37_experimental_48_moving_boundary.json",
    "configs/step37_static_48_link_area.json",
    "configs/step37_experimental_48_link_area.json",
]

STEP37_LOG_MARKERS = {
    "logs/step37_application_window_driver.log": "[OK] Step 37 application window driver finished",
    "logs/step37_application_envelope_summary.log": "[OK] Step 37 application envelope summary finished",
    "logs/step37_static_vs_experimental_envelope.log": "[OK] Step 37 static vs experimental envelope finished",
    "logs/step37_engineering_vs_link_area_envelope.log": "[OK] Step 37 engineering vs link-area envelope finished",
    "logs/step37_mass_force_bounceback_envelope.log": "[OK] Step 37 mass force bounceback envelope finished",
    "logs/step37_wall_velocity_timeseries_quality.log": "[OK] Step 37 wall velocity timeseries quality finished",
    "logs/step37_quality_report_aggregation.log": "[OK] Step 37 quality report aggregation finished",
    "logs/step37_step36_regression_guard.log": "[OK] Step 37 Step 36 regression guard finished",
    "logs/step37_artifact_manifest.log": "[OK] Step 37 artifact manifest finished",
}

STEP37_DRIVER_FIELDS = [
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
    "wall_velocity_application_timeseries_path",
    "application_report_count",
    "application_envelope_pass",
    "applied_cell_count_min",
    "applied_cell_count_max",
    "max_applied_velocity_norm",
    "mean_applied_velocity_norm_max",
    "wall_velocity_cap_lbm",
    "lbm_population_update_count_max",
    "modify_bounceback_formula_any",
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


def run_step37_driver_case(driver_config_path, out_dir) -> dict:
    from src.fsi_config import FSIDriverConfig
    from src.fsi_driver import FSIDriver3D
    from src.real_geometry_feasibility import summarize_short_driver_diagnostics
    from src.wall_velocity_application_envelope import (
        reports_to_timeseries_rows,
        summarize_application_envelope,
        summarize_driver_stability_envelope,
        write_timeseries,
    )

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    enforce_step37_driver_config(config, driver_config_path)
    driver = FSIDriver3D(config, str(out_dir))
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step 37 driver case: {driver_config_path}")

    case = case_name(driver_config_path)
    quality_path = Path(out_dir) / "geometry_quality_report.json"
    timing_path = Path(out_dir) / "driver_timing.json"
    write_json(timing_path, driver.performance_row())
    short_row = summarize_short_driver_diagnostics(config, diagnostics, driver, quality_path)
    stability = summarize_driver_stability_envelope(diagnostics)
    app_summary, timeseries_path = application_timeseries_fields(config, driver, case, out_dir)
    if config.wall_velocity_application_mode == "solid_vel_experimental":
        timeseries_rows = reports_to_timeseries_rows(driver.wall_velocity_application_reports, case, config.reaction_transfer_mode)
        write_timeseries(
            timeseries_rows,
            Path(out_dir) / "wall_velocity_application_timeseries.csv",
            Path(out_dir) / "wall_velocity_application_timeseries.json",
            summary=app_summary,
        )

    row = {
        "case": case,
        "candidate_id": "squid_proxy_wall_velocity_application_envelope",
        "mode_class": mode_class(config),
        "geometry_type": config.geometry_type,
        "geometry_source": config.geometry_config_path,
        "mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "driver_timing_path": relative_path(timing_path),
        "notes": "Step 37 controlled moving-wall application short-window envelope",
    }
    row.update(boundary_motion_fields(config, out_dir))
    row.update(wall_velocity_application_fields(config, out_dir, timeseries_path))
    row.update(app_summary)
    row.update(quality_fields(short_row))
    row.update(config_fields(config))
    row.update(stability)
    row.update(area_fields(short_row))
    row["stable"] = bool(row["stable"] and row["quality_pass"] and application_row_pass(row))
    row["has_nan"] = bool(row["has_nan"] or not finite_values(row, excluded=step37_driver_string_fields()))
    row["has_inf"] = row["has_nan"]
    assert_step37_driver_row(row)
    return row


def enforce_step37_driver_config(config, config_path):
    if config.geometry_type != "squid_proxy":
        raise RuntimeError(f"{config_path} must use geometry_type=squid_proxy")
    if config.geometry_config_path != STEP37_GEOMETRY_CONFIG_PATH:
        raise RuntimeError(f"{config_path} must reuse Step 30 squid proxy geometry")
    if int(config.n_grid) != 48 or int(config.n_particles) != 4096:
        raise RuntimeError(f"{config_path} must use n_grid=48 and n_particles=4096")
    if int(config.n_lbm_steps) != 20 or int(config.mpm_substeps_per_lbm_step) != 5:
        raise RuntimeError(f"{config_path} must use 20 LBM steps and 5 MPM substeps")
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
    if config.wall_velocity_application_mode == "disabled":
        if config.boundary_motion_mode != "static":
            raise RuntimeError(f"{config_path} disabled rows must keep static boundary motion")
        if config.wall_velocity_application_config_path is not None or config.wall_velocity_application_report_enabled:
            raise RuntimeError(f"{config_path} disabled rows must not load/write application reports")
    elif config.wall_velocity_application_mode == "solid_vel_experimental":
        if config.boundary_motion_mode != "prescribed_kinematic":
            raise RuntimeError(f"{config_path} experimental rows require prescribed_kinematic boundary motion")
        if config.boundary_motion_config_path != STEP37_BOUNDARY_MOTION_CONFIG_PATH or not config.boundary_motion_report_enabled:
            raise RuntimeError(f"{config_path} experimental rows must report the Step 34 boundary-motion config")
        if config.wall_velocity_application_config_path != STEP37_APPLICATION_CONFIG_PATH or not config.wall_velocity_application_report_enabled:
            raise RuntimeError(f"{config_path} experimental rows must use/report the Step 36 application config")
    else:
        raise RuntimeError(f"unsupported Step 37 wall_velocity_application_mode: {config.wall_velocity_application_mode}")


def boundary_motion_fields(config, out_dir) -> dict:
    report_path = Path(out_dir) / "boundary_motion_interface_report.json"
    return {
        "boundary_motion_mode": config.boundary_motion_mode,
        "boundary_motion_config_path": config.boundary_motion_config_path or "",
        "boundary_motion_report_enabled": bool(config.boundary_motion_report_enabled),
        "boundary_motion_report_written": report_path.is_file(),
        "boundary_motion_interface_report_path": relative_path(report_path) if report_path.is_file() else "",
    }


def wall_velocity_application_fields(config, out_dir, timeseries_path) -> dict:
    report_path = Path(out_dir) / "wall_velocity_application_report.json"
    return {
        "wall_velocity_application_mode": config.wall_velocity_application_mode,
        "wall_velocity_application_config_path": config.wall_velocity_application_config_path or "",
        "wall_velocity_application_report_enabled": bool(config.wall_velocity_application_report_enabled),
        "wall_velocity_application_report_written": report_path.is_file(),
        "wall_velocity_application_report_path": relative_path(report_path) if report_path.is_file() else "",
        "wall_velocity_application_timeseries_path": timeseries_path,
    }


def application_timeseries_fields(config, driver, case, out_dir) -> tuple[dict, str]:
    from src.wall_velocity_application_envelope import reports_to_timeseries_rows, summarize_application_envelope

    if config.wall_velocity_application_mode == "disabled":
        return (
            {
                "application_report_count": 0,
                "application_envelope_pass": True,
                "applied_cell_count_min": 0,
                "applied_cell_count_max": 0,
                "max_applied_velocity_norm": 0.0,
                "mean_applied_velocity_norm_max": 0.0,
                "wall_velocity_cap_lbm": 0.0,
                "lbm_population_update_count_max": 0,
                "modify_bounceback_formula_any": False,
            },
            "",
        )
    rows = reports_to_timeseries_rows(driver.wall_velocity_application_reports, case, config.reaction_transfer_mode)
    summary = summarize_application_envelope(rows)
    fields = {
        "application_report_count": int(summary["application_report_count"]),
        "application_envelope_pass": bool(summary["application_envelope_pass"]),
        "applied_cell_count_min": int(summary["applied_cell_count_min"]),
        "applied_cell_count_max": int(summary["applied_cell_count_max"]),
        "max_applied_velocity_norm": float(summary["max_applied_velocity_norm"]),
        "mean_applied_velocity_norm_max": float(summary["mean_applied_velocity_norm_max"]),
        "wall_velocity_cap_lbm": float(summary["wall_velocity_cap_lbm"]),
        "lbm_population_update_count_max": int(summary["lbm_population_update_count_max"]),
        "modify_bounceback_formula_any": bool(summary["modify_bounceback_formula_any"]),
    }
    return fields, relative_path(Path(out_dir) / "wall_velocity_application_timeseries.csv")


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
    return "experimental" if config.wall_velocity_application_mode == "solid_vel_experimental" else "static"


def application_row_pass(row) -> bool:
    if row["mode_class"] == "static":
        return int(row["application_report_count"]) == 0 and int(row["applied_cell_count_max"]) == 0
    return bool(
        int(row["application_report_count"]) >= 20
        and bool(row["application_envelope_pass"])
        and int(row["applied_cell_count_min"]) > 0
        and float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12
        and int(row["lbm_population_update_count_max"]) == 0
        and not as_bool(row["modify_bounceback_formula_any"])
    )


def assert_step37_driver_row(row):
    if not as_bool(row["quality_check_enabled"]) or not as_bool(row["quality_check_strict"]):
        raise RuntimeError(f"Step 37 row must use strict quality checks: {row}")
    if not as_bool(row["quality_pass"]) or not as_bool(row["quality_gate_strict"]):
        raise RuntimeError(f"Step 37 quality gate failed: {row}")
    if row["quality_severity"] != "ok" or int(row["quality_warnings_count"]) != 0 or int(row["quality_reasons_count"]) != 0:
        raise RuntimeError(f"Step 37 quality report must be clean: {row}")
    if int(row["completed_lbm_steps"]) < 20 or int(row["total_mpm_substeps"]) < 100:
        raise RuntimeError(f"Step 37 row did not complete 20-step window: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 37 density envelope out of range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 37 velocity envelope out of range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0 or float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 37 MPM envelope out of range: {row}")
    if float(row["projected_mass_min"]) <= 0.0 or float(row["projected_mass_max"]) <= 0.0:
        raise RuntimeError(f"Step 37 projected mass envelope is invalid: {row}")
    if int(row["active_cell_count"]) <= 0 or int(row["bb_link_count_max"]) <= 0:
        raise RuntimeError(f"Step 37 moving-boundary diagnostics are missing: {row}")
    if as_bool(row["has_nan"]) or as_bool(row["has_inf"]) or not finite_values(row, excluded=step37_driver_string_fields()):
        raise RuntimeError(f"Step 37 row has non-finite values: {row}")
    if not application_row_pass(row):
        raise RuntimeError(f"Step 37 application fields failed: {row}")
    if not as_bool(row["stable"]):
        raise RuntimeError(f"Step 37 row is not stable: {row}")


def driver_summary(rows) -> dict:
    return {
        "row_count": len(rows),
        "static_row_count": sum(1 for row in rows if row["mode_class"] == "static"),
        "experimental_row_count": sum(1 for row in rows if row["mode_class"] == "experimental"),
        "engineering_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "engineering"),
        "link_area_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "link_area_experimental"),
        "stable_count": sum(1 for row in rows if as_bool(row["stable"])),
        "quality_pass_count": sum(1 for row in rows if as_bool(row["quality_pass"])),
        "min_completed_lbm_steps": min(int(row["completed_lbm_steps"]) for row in rows),
        "min_total_mpm_substeps": min(int(row["total_mpm_substeps"]) for row in rows),
        "min_rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "max_lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows),
        "min_mpm_min_J_global": min(float(row["mpm_min_J_global"]) for row in rows),
        "max_mpm_max_speed_global": max(float(row["mpm_max_speed_global"]) for row in rows),
        "min_projected_mass_min": min(float(row["projected_mass_min"]) for row in rows),
        "max_projected_mass_max": max(float(row["projected_mass_max"]) for row in rows),
        "min_active_cell_count": min(int(row["active_cell_count"]) for row in rows),
        "min_bb_link_count_max": min(int(row["bb_link_count_max"]) for row in rows),
        "max_application_report_count": max(int(row["application_report_count"]) for row in rows),
        "max_applied_velocity_norm": max(float(row["max_applied_velocity_norm"]) for row in rows),
        "max_lbm_population_update_count": max(int(row["lbm_population_update_count_max"]) for row in rows),
        "scope_note": "Step 37 controlled moving-wall application short-window envelope; not jet or swimming validation.",
    }


def assert_driver_summary(summary):
    if int(summary["row_count"]) != 4:
        raise RuntimeError(f"Step 37 driver row count is wrong: {summary}")
    if int(summary["static_row_count"]) != 2 or int(summary["experimental_row_count"]) != 2:
        raise RuntimeError(f"Step 37 mode class split is wrong: {summary}")
    if int(summary["engineering_row_count"]) != 2 or int(summary["link_area_row_count"]) != 2:
        raise RuntimeError(f"Step 37 transfer split is wrong: {summary}")
    if int(summary["stable_count"]) != 4 or int(summary["quality_pass_count"]) != 4:
        raise RuntimeError(f"all Step 37 driver rows must be stable and quality-passing: {summary}")
    if int(summary["min_completed_lbm_steps"]) < 20 or int(summary["min_total_mpm_substeps"]) < 100:
        raise RuntimeError(f"Step 37 completion summary is wrong: {summary}")
    if float(summary["min_rho_min_global"]) <= 0.95 or float(summary["max_rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 37 density summary is out of range: {summary}")
    if float(summary["max_lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 37 velocity summary is out of range: {summary}")
    if float(summary["min_projected_mass_min"]) <= 0.0 or int(summary["min_active_cell_count"]) <= 0:
        raise RuntimeError(f"Step 37 projected/active summary is invalid: {summary}")
    if int(summary["min_bb_link_count_max"]) <= 0:
        raise RuntimeError(f"Step 37 bounce-back link summary is invalid: {summary}")
    if int(summary["max_lbm_population_update_count"]) != 0:
        raise RuntimeError(f"Step 37 must not directly update LBM populations: {summary}")


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
    return Path(config_path).stem.removeprefix("step37_")


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


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
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if isinstance(value, bool):
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


def step37_driver_string_fields():
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
        "wall_velocity_application_timeseries_path",
        "application_envelope_pass",
        "modify_bounceback_formula_any",
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
