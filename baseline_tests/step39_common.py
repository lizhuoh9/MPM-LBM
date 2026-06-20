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


STEP39_APPLICATION_CONFIG_PATH = "configs/step36_wall_velocity_application_solid_vel_experimental.json"
STEP39_GEOMETRY_CONFIG_PATH = "configs/step30_squid_proxy_geometry.json"
STEP39_BOUNDARY_MOTION_CONFIG_PATH = "configs/step34_boundary_motion_interface_prescribed_kinematic.json"
STEP39_SCHEDULE_CONFIG_PATH = "configs/step32_squid_proxy_kinematics_schedule.json"
STEP39_SCHEDULE_OUTPUT_PATH = "outputs/step32_kinematics_schedule/kinematics_schedule.json"
CYCLE_PERIOD_STEPS = 40
CYCLE_COUNT = 2
N_LBM_STEPS = CYCLE_PERIOD_STEPS * CYCLE_COUNT

STEP39_DRIVER_CONFIGS = [
    "configs/step39_multicycle_static_48_moving_boundary.json",
    "configs/step39_multicycle_experimental_48_moving_boundary.json",
    "configs/step39_multicycle_static_48_link_area.json",
    "configs/step39_multicycle_experimental_48_link_area.json",
]

STEP39_DRIVER_FIELDS = [
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


def run_step39_driver_case(driver_config_path, out_dir) -> dict:
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
    enforce_step39_driver_config(config, driver_config_path)
    driver = FSIDriver3D(config, str(out_dir))
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step 39 driver case: {driver_config_path}")

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
        "candidate_id": "squid_proxy_multicycle_jet_proxy_stability",
        "mode_class": mode_class(config),
        "geometry_type": config.geometry_type,
        "geometry_source": config.geometry_config_path,
        "mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "driver_timing_path": relative_path(timing_path),
        "notes": "Step 39 controlled jet-cycle proxy multi-cycle stability envelope",
    }
    row.update(boundary_motion_fields(config, out_dir))
    row.update(wall_velocity_application_fields(config, out_dir, timeseries_path))
    row.update(app_summary)
    row.update(quality_fields(short_row))
    row.update(config_fields(config))
    row.update(stability)
    row.update(area_fields(short_row))
    row["stable"] = bool(row["stable"] and row["quality_pass"] and application_row_pass(row))
    row["has_nan"] = bool(row["has_nan"] or not finite_values(row, excluded=step39_driver_string_fields()))
    row["has_inf"] = row["has_nan"]
    assert_step39_driver_row(row)
    return row


def enforce_step39_driver_config(config, config_path):
    if config.geometry_type != "squid_proxy":
        raise RuntimeError(f"{config_path} must use geometry_type=squid_proxy")
    if config.geometry_config_path != STEP39_GEOMETRY_CONFIG_PATH:
        raise RuntimeError(f"{config_path} must reuse Step 30 squid proxy geometry")
    if int(config.n_grid) != 48 or int(config.n_particles) != 4096:
        raise RuntimeError(f"{config_path} must use n_grid=48 and n_particles=4096")
    if int(config.n_lbm_steps) != N_LBM_STEPS or int(config.mpm_substeps_per_lbm_step) != 5:
        raise RuntimeError(f"{config_path} must use 80 LBM steps and 5 MPM substeps")
    if tuple(float(value) for value in config.target_u_lbm) != (0.0, 0.0, 0.0):
        raise RuntimeError(f"{config_path} must keep target_u_lbm zero for tethered multicycle diagnostics")
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
        if config.boundary_motion_config_path != STEP39_BOUNDARY_MOTION_CONFIG_PATH or not config.boundary_motion_report_enabled:
            raise RuntimeError(f"{config_path} experimental rows must report the Step 34 boundary-motion config")
        if config.wall_velocity_application_config_path != STEP39_APPLICATION_CONFIG_PATH or not config.wall_velocity_application_report_enabled:
            raise RuntimeError(f"{config_path} experimental rows must use/report the Step 36 application config")
    else:
        raise RuntimeError(f"unsupported Step 39 wall_velocity_application_mode: {config.wall_velocity_application_mode}")


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


def assert_step39_driver_row(row):
    if not as_bool(row["quality_check_enabled"]) or not as_bool(row["quality_check_strict"]):
        raise RuntimeError(f"Step 39 row must use strict quality checks: {row}")
    if not as_bool(row["quality_pass"]) or not as_bool(row["quality_gate_strict"]):
        raise RuntimeError(f"Step 39 quality gate failed: {row}")
    if row["quality_severity"] != "ok" or int(row["quality_warnings_count"]) != 0 or int(row["quality_reasons_count"]) != 0:
        raise RuntimeError(f"Step 39 quality report must be clean: {row}")
    if int(row["completed_lbm_steps"]) < N_LBM_STEPS or int(row["total_mpm_substeps"]) < N_LBM_STEPS * 5:
        raise RuntimeError(f"Step 39 row did not complete two cycles: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 39 density envelope out of range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 39 velocity envelope out of range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0 or float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 39 MPM envelope out of range: {row}")
    if float(row["projected_mass_min"]) <= 0.0 or float(row["projected_mass_max"]) <= 0.0:
        raise RuntimeError(f"Step 39 projected mass envelope is invalid: {row}")
    if int(row["active_cell_count"]) <= 0 or int(row["bb_link_count_max"]) <= 0:
        raise RuntimeError(f"Step 39 moving-boundary diagnostics are missing: {row}")
    if as_bool(row["has_nan"]) or as_bool(row["has_inf"]) or not finite_values(row, excluded=step39_driver_string_fields()):
        raise RuntimeError(f"Step 39 row has non-finite values: {row}")
    if not application_row_pass(row):
        raise RuntimeError(f"Step 39 application fields failed: {row}")
    if not as_bool(row["stable"]):
        raise RuntimeError(f"Step 39 row is not stable: {row}")


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
        "scope_note": "Step 39 controlled jet-cycle proxy multi-cycle stability envelope; not propulsion or swimming validation.",
    }


def assert_driver_summary(summary):
    if int(summary["row_count"]) != 4:
        raise RuntimeError(f"Step 39 driver row count is wrong: {summary}")
    if int(summary["static_row_count"]) != 2 or int(summary["experimental_row_count"]) != 2:
        raise RuntimeError(f"Step 39 mode class split is wrong: {summary}")
    if int(summary["engineering_row_count"]) != 2 or int(summary["link_area_row_count"]) != 2:
        raise RuntimeError(f"Step 39 transfer split is wrong: {summary}")
    if int(summary["stable_count"]) != 4 or int(summary["quality_pass_count"]) != 4:
        raise RuntimeError(f"all Step 39 driver rows must be stable and quality-passing: {summary}")
    if int(summary["min_completed_lbm_steps"]) < N_LBM_STEPS or int(summary["min_total_mpm_substeps"]) < N_LBM_STEPS * 5:
        raise RuntimeError(f"Step 39 completion summary is wrong: {summary}")
    if float(summary["min_rho_min_global"]) <= 0.95 or float(summary["max_rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 39 density summary is out of range: {summary}")
    if float(summary["max_lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 39 velocity summary is out of range: {summary}")
    if float(summary["min_projected_mass_min"]) <= 0.0 or int(summary["min_active_cell_count"]) <= 0:
        raise RuntimeError(f"Step 39 projected/active summary is invalid: {summary}")
    if int(summary["min_bb_link_count_max"]) <= 0:
        raise RuntimeError(f"Step 39 bounce-back link summary is invalid: {summary}")
    if int(summary["max_lbm_population_update_count"]) != 0:
        raise RuntimeError(f"Step 39 must not directly update LBM populations: {summary}")


def compare_static_experimental_multicycle(static_row: dict, experimental_row: dict) -> dict:
    row = {
        "comparison": f"static_vs_experimental_{experimental_row['reaction_transfer_mode']}",
        "static_case": static_row["case"],
        "experimental_case": experimental_row["case"],
        "reaction_transfer_mode": experimental_row["reaction_transfer_mode"],
        "both_stable": as_bool(static_row["stable"]) and as_bool(experimental_row["stable"]),
        "rho_min_delta": float(experimental_row["rho_min_global"]) - float(static_row["rho_min_global"]),
        "rho_max_delta": float(experimental_row["rho_max_global"]) - float(static_row["rho_max_global"]),
        "lbm_max_v_delta": float(experimental_row["lbm_max_v_global"]) - float(static_row["lbm_max_v_global"]),
        "mpm_min_J_delta": float(experimental_row["mpm_min_J_global"]) - float(static_row["mpm_min_J_global"]),
        "projected_mass_delta": float(experimental_row["projected_mass_max"]) - float(static_row["projected_mass_max"]),
        "active_cell_count_delta": int(experimental_row["active_cell_count"]) - int(static_row["active_cell_count"]),
        "bb_link_count_delta": int(experimental_row["bb_link_count_max"]) - int(static_row["bb_link_count_max"]),
        "experimental_applied_velocity_max": float(experimental_row["max_applied_velocity_norm"]),
        "notes": "bounded Step 39 static-vs-experimental two-cycle proxy comparison",
    }
    row["comparison_pass"] = bool(
        row["both_stable"]
        and finite_values(row, excluded={"comparison", "static_case", "experimental_case", "reaction_transfer_mode", "both_stable", "notes", "comparison_pass"})
        and abs(row["rho_min_delta"]) <= 0.05
        and abs(row["rho_max_delta"]) <= 0.05
        and abs(row["lbm_max_v_delta"]) <= 0.08
        and abs(row["mpm_min_J_delta"]) <= 0.05
        and abs(row["projected_mass_delta"]) <= 1.0e-3
        and abs(row["active_cell_count_delta"]) <= 500
        and abs(row["bb_link_count_delta"]) <= 500
        and row["experimental_applied_velocity_max"] > 0.0
    )
    return row


def compare_engineering_link_area_multicycle(engineering_row: dict, link_area_row: dict) -> dict:
    row = {
        "comparison": "experimental_engineering_vs_link_area_multicycle",
        "engineering_case": engineering_row["case"],
        "link_area_case": link_area_row["case"],
        "both_stable": as_bool(engineering_row["stable"]) and as_bool(link_area_row["stable"]),
        "link_area_scale_final": float(link_area_row["area_scale_final"]),
        "rho_min_delta": float(link_area_row["rho_min_global"]) - float(engineering_row["rho_min_global"]),
        "rho_max_delta": float(link_area_row["rho_max_global"]) - float(engineering_row["rho_max_global"]),
        "lbm_max_v_delta": float(link_area_row["lbm_max_v_global"]) - float(engineering_row["lbm_max_v_global"]),
        "mpm_min_J_delta": float(link_area_row["mpm_min_J_global"]) - float(engineering_row["mpm_min_J_global"]),
        "projected_mass_delta": float(link_area_row["projected_mass_max"]) - float(engineering_row["projected_mass_max"]),
        "notes": "bounded Step 39 experimental engineering-vs-link-area two-cycle proxy comparison",
    }
    row["comparison_pass"] = bool(
        row["both_stable"]
        and finite_values(row, excluded={"comparison", "engineering_case", "link_area_case", "both_stable", "notes", "comparison_pass"})
        and 0.25 <= row["link_area_scale_final"] <= 2.0
        and abs(row["projected_mass_delta"]) <= 1.0e-3
        and abs(row["rho_min_delta"]) <= 0.05
        and abs(row["rho_max_delta"]) <= 0.05
        and abs(row["lbm_max_v_delta"]) <= 0.08
        and abs(row["mpm_min_J_delta"]) <= 0.05
    )
    return row


def read_driver_rows():
    return read_json("outputs/step39_multicycle_driver/multicycle_driver_results.json")["rows"]


def read_timeseries_rows(driver_row: dict):
    path = driver_row["wall_velocity_application_timeseries_path"]
    if not path:
        return []
    json_path = path.replace("\\", "/").replace(".csv", ".json")
    return read_json(json_path)["rows"]


def read_diagnostics_rows(driver_row: dict):
    return read_csv_rows(f"outputs/step39_multicycle_driver/{driver_row['case']}/diagnostics_timeseries.csv")


def case_name(config_path):
    return Path(config_path).stem.removeprefix("step39_multicycle_")


def step39_driver_string_fields():
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


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def write_summary_csv(path, summary: dict) -> None:
    write_csv_rows(path, summary_rows(summary), ["metric", "value"])
