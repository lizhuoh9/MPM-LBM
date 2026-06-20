import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from step37_common import (  # noqa: E402
    area_fields,
    boundary_motion_fields,
    config_fields,
    fieldnames_from_rows,
    finite_values,
    quality_fields,
    read_csv_rows,
    read_json,
    relative_path,
    resolve_path,
    summary_rows,
    wall_velocity_application_fields,
    write_csv_rows,
    write_json,
    write_log,
    write_rows_csv_npz,
)
from src.jet_cycle_parameter_sensitivity import (  # noqa: E402
    parse_wall_velocity_scale_from_case,
    summarize_parameter_driver_rows,
)


STEP40_GEOMETRY_CONFIG_PATH = "configs/step30_squid_proxy_geometry.json"
STEP40_BOUNDARY_MOTION_CONFIG_PATH = "configs/step34_boundary_motion_interface_prescribed_kinematic.json"
STEP40_APPLICATION_CONFIGS = [
    "configs/step40_wall_velocity_application_scale_0025.json",
    "configs/step40_wall_velocity_application_scale_0050.json",
    "configs/step40_wall_velocity_application_scale_0075.json",
]
STEP40_DRIVER_CONFIGS = [
    "configs/step40_static_48_moving_boundary.json",
    "configs/step40_static_48_link_area.json",
    "configs/step40_experimental_48_moving_boundary_scale_0025.json",
    "configs/step40_experimental_48_moving_boundary_scale_0050.json",
    "configs/step40_experimental_48_moving_boundary_scale_0075.json",
    "configs/step40_experimental_48_link_area_scale_0025.json",
    "configs/step40_experimental_48_link_area_scale_0050.json",
    "configs/step40_experimental_48_link_area_scale_0075.json",
]
N_LBM_STEPS = 40
MPM_SUBSTEPS_PER_LBM_STEP = 5

STEP40_DRIVER_FIELDS = [
    "case",
    "candidate_id",
    "mode_class",
    "geometry_type",
    "geometry_source",
    "mode",
    "reaction_transfer_mode",
    "wall_velocity_scale",
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


def run_step40_driver_case(driver_config_path, out_dir) -> dict:
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
    enforce_step40_driver_config(config, driver_config_path)
    driver = FSIDriver3D(config, str(out_dir))
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step 40 driver case: {driver_config_path}")

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
        "candidate_id": "squid_proxy_parameter_sensitivity_smoke",
        "mode_class": mode_class(config),
        "geometry_type": config.geometry_type,
        "geometry_source": config.geometry_config_path,
        "mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "wall_velocity_scale": wall_velocity_scale(config),
        "driver_timing_path": relative_path(timing_path),
        "notes": "Step 40 controlled jet-cycle proxy parameter sensitivity smoke",
    }
    row.update(boundary_motion_fields(config, out_dir))
    row.update(wall_velocity_application_fields(config, out_dir, timeseries_path))
    row.update(app_summary)
    row.update(quality_fields(short_row))
    row.update(config_fields(config))
    row.update(stability)
    row.update(area_fields(short_row))
    row["stable"] = bool(row["stable"] and row["quality_pass"] and application_row_pass(row))
    row["has_nan"] = bool(row["has_nan"] or not finite_values(row, excluded=step40_driver_string_fields()))
    row["has_inf"] = row["has_nan"]
    assert_step40_driver_row(row)
    return row


def enforce_step40_driver_config(config, config_path):
    if config.geometry_type != "squid_proxy":
        raise RuntimeError(f"{config_path} must use geometry_type=squid_proxy")
    if config.geometry_config_path != STEP40_GEOMETRY_CONFIG_PATH:
        raise RuntimeError(f"{config_path} must reuse Step 30 squid proxy geometry")
    if int(config.n_grid) != 48 or int(config.n_particles) != 4096:
        raise RuntimeError(f"{config_path} must use n_grid=48 and n_particles=4096")
    if int(config.n_lbm_steps) != N_LBM_STEPS or int(config.mpm_substeps_per_lbm_step) != MPM_SUBSTEPS_PER_LBM_STEP:
        raise RuntimeError(f"{config_path} must use 40 LBM steps and 5 MPM substeps")
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
    if config.wall_velocity_application_mode == "disabled":
        if config.boundary_motion_mode != "static":
            raise RuntimeError(f"{config_path} disabled rows must keep static boundary motion")
        if config.wall_velocity_application_config_path is not None or config.wall_velocity_application_report_enabled:
            raise RuntimeError(f"{config_path} disabled rows must not load/write application reports")
    elif config.wall_velocity_application_mode == "solid_vel_experimental":
        if config.boundary_motion_mode != "prescribed_kinematic":
            raise RuntimeError(f"{config_path} experimental rows require prescribed_kinematic boundary motion")
        if config.boundary_motion_config_path != STEP40_BOUNDARY_MOTION_CONFIG_PATH or not config.boundary_motion_report_enabled:
            raise RuntimeError(f"{config_path} experimental rows must report the Step 34 boundary-motion config")
        if config.wall_velocity_application_config_path not in STEP40_APPLICATION_CONFIGS or not config.wall_velocity_application_report_enabled:
            raise RuntimeError(f"{config_path} experimental rows must use/report a Step 40 application config")
    else:
        raise RuntimeError(f"unsupported Step 40 wall_velocity_application_mode: {config.wall_velocity_application_mode}")


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


def wall_velocity_scale(config) -> float:
    if config.wall_velocity_application_mode == "disabled":
        return 0.0
    return parse_wall_velocity_scale_from_case(config.wall_velocity_application_config_path)


def mode_class(config) -> str:
    return "experimental" if config.wall_velocity_application_mode == "solid_vel_experimental" else "static"


def application_row_pass(row) -> bool:
    if row["mode_class"] == "static":
        return int(row["application_report_count"]) == 0 and int(row["applied_cell_count_max"]) == 0
    return bool(
        int(row["application_report_count"]) >= N_LBM_STEPS
        and bool(row["application_envelope_pass"])
        and int(row["applied_cell_count_min"]) > 0
        and float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12
        and int(row["lbm_population_update_count_max"]) == 0
        and not as_bool(row["modify_bounceback_formula_any"])
    )


def assert_step40_driver_row(row):
    if not as_bool(row["quality_check_enabled"]) or not as_bool(row["quality_check_strict"]):
        raise RuntimeError(f"Step 40 row must use strict quality checks: {row}")
    if not as_bool(row["quality_pass"]) or not as_bool(row["quality_gate_strict"]):
        raise RuntimeError(f"Step 40 quality gate failed: {row}")
    if row["quality_severity"] != "ok" or int(row["quality_warnings_count"]) != 0 or int(row["quality_reasons_count"]) != 0:
        raise RuntimeError(f"Step 40 quality report must be clean: {row}")
    if int(row["completed_lbm_steps"]) < N_LBM_STEPS or int(row["total_mpm_substeps"]) < N_LBM_STEPS * MPM_SUBSTEPS_PER_LBM_STEP:
        raise RuntimeError(f"Step 40 row did not complete one cycle: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 40 density envelope out of range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 40 velocity envelope out of range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0 or float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 40 MPM envelope out of range: {row}")
    if float(row["projected_mass_min"]) <= 0.0 or float(row["projected_mass_max"]) <= 0.0:
        raise RuntimeError(f"Step 40 projected mass envelope is invalid: {row}")
    if int(row["active_cell_count"]) <= 0 or int(row["bb_link_count_max"]) <= 0:
        raise RuntimeError(f"Step 40 moving-boundary diagnostics are missing: {row}")
    if as_bool(row["has_nan"]) or as_bool(row["has_inf"]) or not finite_values(row, excluded=step40_driver_string_fields()):
        raise RuntimeError(f"Step 40 row has non-finite values: {row}")
    if not application_row_pass(row):
        raise RuntimeError(f"Step 40 application fields failed: {row}")
    if not as_bool(row["stable"]):
        raise RuntimeError(f"Step 40 row is not stable: {row}")


def read_driver_rows():
    return read_json("outputs/step40_parameter_sweep_driver/parameter_sweep_results.json")["rows"]


def read_timeseries_rows(driver_row: dict):
    path = driver_row["wall_velocity_application_timeseries_path"]
    if not path:
        return []
    json_path = path.replace("\\", "/").replace(".csv", ".json")
    return read_json(json_path)["rows"]


def read_diagnostics_rows(driver_row: dict):
    return read_csv_rows(f"outputs/step40_parameter_sweep_driver/{driver_row['case']}/diagnostics_timeseries.csv")


def case_name(config_path):
    return Path(config_path).stem.removeprefix("step40_")


def step40_driver_string_fields():
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


def write_summary_csv(path, summary: dict) -> None:
    write_csv_rows(path, summary_rows(summary), ["metric", "value"])


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def driver_summary(rows: list[dict]) -> dict:
    return summarize_parameter_driver_rows(rows)
