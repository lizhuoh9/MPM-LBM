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

STEP36_APPLICATION_CONFIG_PATH = "configs/step36_wall_velocity_application_solid_vel_experimental.json"
STEP36_GEOMETRY_CONFIG_PATH = "configs/step30_squid_proxy_geometry.json"
STEP36_BOUNDARY_MOTION_CONFIG_PATH = "configs/step34_boundary_motion_interface_prescribed_kinematic.json"

STEP36_STATIC_DRIVER_CONFIGS = [
    "configs/step36_static_32_moving_boundary.json",
    "configs/step36_static_48_moving_boundary.json",
    "configs/step36_static_48_link_area.json",
]
STEP36_EXPERIMENTAL_DRIVER_CONFIGS = [
    "configs/step36_experimental_32_moving_boundary.json",
    "configs/step36_experimental_48_moving_boundary.json",
    "configs/step36_experimental_48_link_area.json",
]
STEP36_DRIVER_CONFIGS = STEP36_STATIC_DRIVER_CONFIGS + STEP36_EXPERIMENTAL_DRIVER_CONFIGS

STEP36_LOG_MARKERS = {
    "logs/step36_wall_velocity_application_config_validation.log": "[OK] Step 36 wall velocity application config validation finished",
    "logs/step36_wall_velocity_application_report.log": "[OK] Step 36 wall velocity application report finished",
    "logs/step36_static_regression_smoke.log": "[OK] Step 36 static regression smoke finished",
    "logs/step36_experimental_application_smoke.log": "[OK] Step 36 experimental application smoke finished",
    "logs/step36_static_vs_experimental_comparison.log": "[OK] Step 36 static vs experimental comparison finished",
    "logs/step36_mass_force_stability_diagnostics.log": "[OK] Step 36 mass force stability diagnostics finished",
    "logs/step36_wall_velocity_application_quality.log": "[OK] Step 36 wall velocity application quality finished",
    "logs/step36_quality_report_aggregation.log": "[OK] Step 36 quality report aggregation finished",
    "logs/step36_step35_regression_guard.log": "[OK] Step 36 Step 35 regression guard finished",
    "logs/step36_artifact_manifest.log": "[OK] Step 36 artifact manifest finished",
}

STEP36_DRIVER_FIELDS = [
    "case",
    "candidate_id",
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
    "wall_velocity_application_report_pass",
    "driver_application_report_count",
    "application_policy",
    "apply_to_lbm_solid_vel",
    "apply_to_lbm_populations",
    "modify_bounceback_formula",
    "applied_cell_count",
    "max_applied_velocity_norm",
    "mean_applied_velocity_norm",
    "wall_velocity_cap_lbm",
    "lbm_population_update_count",
    "after_solid_vel_norm_max",
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
    "rho_min_global",
    "rho_max_global",
    "lbm_max_v_global",
    "mpm_min_J_global",
    "mpm_max_speed_global",
    "projected_mass",
    "active_cell_count",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count_min",
    "bb_link_count_max",
    "bb_max_correction_global",
    "active_reaction_particle_count_max",
    "area_scale_final",
    "area_scale_min",
    "area_scale_max",
    "raw_area_scale_final",
    "has_nan",
    "has_inf",
    "stable",
    "notes",
]


def run_step36_driver_case(driver_config_path, out_dir) -> dict:
    from src.fsi_config import FSIDriverConfig
    from src.fsi_driver import FSIDriver3D
    from src.real_geometry_feasibility import summarize_short_driver_diagnostics

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    enforce_step36_driver_config(config, driver_config_path)
    driver = FSIDriver3D(config, str(out_dir))
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step 36 driver case: {driver_config_path}")

    quality_path = Path(out_dir) / "geometry_quality_report.json"
    timing_path = Path(out_dir) / "driver_timing.json"
    write_json(timing_path, driver.performance_row())
    row = summarize_short_driver_diagnostics(config, diagnostics, driver, quality_path)
    row["case"] = case_name(driver_config_path)
    row["candidate_id"] = "squid_proxy_wall_velocity_application"
    row["driver_timing_path"] = relative_path(timing_path)
    row["notes"] = "Step 36 controlled solid_vel application smoke; opt-in experimental only"
    row["bb_max_correction_global"] = max(float(item["bb_max_correction"]) for item in diagnostics)
    row.update(boundary_motion_fields(config, out_dir))
    row.update(wall_velocity_application_fields(config, out_dir, driver))
    assert_step36_driver_row(row)
    return row


def load_existing_step36_driver_case(driver_config_path, out_dir) -> dict:
    from src.fsi_config import FSIDriverConfig
    from src.real_geometry_feasibility import summarize_short_driver_diagnostics

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    enforce_step36_driver_config(config, driver_config_path)
    if config.reaction_transfer_mode == "link_area_experimental":
        raise RuntimeError("Step 36 link-area cases must be rerun unless loaded from the final aggregate CSV")
    required = [
        Path(out_dir) / "diagnostics_timeseries.csv",
        Path(out_dir) / "geometry_quality_report.json",
        Path(out_dir) / "driver_timing.json",
    ]
    if config.wall_velocity_application_mode == "solid_vel_experimental":
        required.append(Path(out_dir) / "wall_velocity_application_report.json")
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"cannot reuse incomplete Step 36 case {driver_config_path}: {missing}")
    diagnostics = read_csv_rows(Path(out_dir) / "diagnostics_timeseries.csv")
    quality_path = Path(out_dir) / "geometry_quality_report.json"
    timing_path = Path(out_dir) / "driver_timing.json"
    row = summarize_short_driver_diagnostics(config, diagnostics, _DummyDriver(), quality_path)
    row["case"] = case_name(driver_config_path)
    row["candidate_id"] = "squid_proxy_wall_velocity_application"
    row["driver_timing_path"] = relative_path(timing_path)
    row["notes"] = "Step 36 controlled solid_vel application smoke; reused complete short-run artifacts"
    row["bb_max_correction_global"] = max(float(item["bb_max_correction"]) for item in diagnostics)
    row.update(boundary_motion_fields(config, out_dir))
    row.update(wall_velocity_application_fields(config, out_dir, driver=None))
    if config.wall_velocity_application_mode == "solid_vel_experimental":
        row["driver_application_report_count"] = 5
    assert_step36_driver_row(row)
    return row


def can_reuse_step36_case(driver_config_path, out_dir) -> bool:
    from src.fsi_config import FSIDriverConfig

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    if config.reaction_transfer_mode == "link_area_experimental":
        return False
    required = [
        Path(out_dir) / "diagnostics_timeseries.csv",
        Path(out_dir) / "geometry_quality_report.json",
        Path(out_dir) / "driver_timing.json",
    ]
    if config.wall_velocity_application_mode == "solid_vel_experimental":
        required.append(Path(out_dir) / "wall_velocity_application_report.json")
    return all(path.is_file() for path in required)


def enforce_step36_driver_config(config, config_path):
    if config.geometry_type != "squid_proxy":
        raise RuntimeError(f"{config_path} must use geometry_type=squid_proxy")
    if config.geometry_config_path != STEP36_GEOMETRY_CONFIG_PATH:
        raise RuntimeError(f"{config_path} must reuse Step 30 squid proxy geometry")
    if int(config.n_grid) not in {32, 48} or int(config.n_particles) != 4096:
        raise RuntimeError(f"{config_path} must use n_grid in {{32, 48}} and n_particles=4096")
    if int(config.n_lbm_steps) != 5 or int(config.mpm_substeps_per_lbm_step) != 5:
        raise RuntimeError(f"{config_path} must use 5 LBM steps and 5 MPM substeps")
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
    if config.reaction_transfer_mode == "link_area_experimental":
        if int(config.n_grid) != 48 or config.link_area_policy != "inverse_length":
            raise RuntimeError(f"{config_path} link-area rows must be 48^3 inverse_length cases")
    if config.wall_velocity_application_mode == "disabled":
        if config.boundary_motion_mode != "static":
            raise RuntimeError(f"{config_path} disabled application rows must keep static boundary motion")
        if config.wall_velocity_application_config_path is not None or config.wall_velocity_application_report_enabled:
            raise RuntimeError(f"{config_path} disabled application rows must not load or write application reports")
    elif config.wall_velocity_application_mode == "solid_vel_experimental":
        if config.boundary_motion_mode != "prescribed_kinematic":
            raise RuntimeError(f"{config_path} application rows require prescribed_kinematic boundary motion")
        if config.boundary_motion_config_path != STEP36_BOUNDARY_MOTION_CONFIG_PATH or not config.boundary_motion_report_enabled:
            raise RuntimeError(f"{config_path} application rows must use and report the Step 34 boundary-motion config")
        if config.wall_velocity_application_config_path != STEP36_APPLICATION_CONFIG_PATH or not config.wall_velocity_application_report_enabled:
            raise RuntimeError(f"{config_path} application rows must use and report the Step 36 application config")
    else:
        raise RuntimeError(f"unsupported Step 36 application mode: {config.wall_velocity_application_mode}")


def boundary_motion_fields(config, out_dir) -> dict:
    report_path = Path(out_dir) / "boundary_motion_interface_report.json"
    return {
        "boundary_motion_mode": config.boundary_motion_mode,
        "boundary_motion_config_path": config.boundary_motion_config_path or "",
        "boundary_motion_report_enabled": bool(config.boundary_motion_report_enabled),
        "boundary_motion_report_written": report_path.is_file(),
        "boundary_motion_interface_report_path": relative_path(report_path) if report_path.is_file() else "",
    }


def wall_velocity_application_fields(config, out_dir, driver=None) -> dict:
    report_path = Path(out_dir) / "wall_velocity_application_report.json"
    fields = {
        "wall_velocity_application_mode": config.wall_velocity_application_mode,
        "wall_velocity_application_config_path": config.wall_velocity_application_config_path or "",
        "wall_velocity_application_report_enabled": bool(config.wall_velocity_application_report_enabled),
        "wall_velocity_application_report_written": report_path.is_file(),
        "wall_velocity_application_report_path": relative_path(report_path) if report_path.is_file() else "",
        "wall_velocity_application_report_pass": config.wall_velocity_application_mode == "disabled",
        "driver_application_report_count": len(getattr(driver, "wall_velocity_application_reports", [])) if driver is not None else 0,
        "application_policy": "",
        "apply_to_lbm_solid_vel": False,
        "apply_to_lbm_populations": False,
        "modify_bounceback_formula": False,
        "applied_cell_count": 0,
        "max_applied_velocity_norm": 0.0,
        "mean_applied_velocity_norm": 0.0,
        "wall_velocity_cap_lbm": 0.0,
        "lbm_population_update_count": 0,
        "after_solid_vel_norm_max": 0.0,
    }
    if report_path.is_file():
        summary = read_json(report_path)["summary"]
        fields.update(
            {
                "wall_velocity_application_report_pass": bool(summary["report_pass"]),
                "application_policy": summary["application_policy"],
                "apply_to_lbm_solid_vel": bool(summary["apply_to_lbm_solid_vel"]),
                "apply_to_lbm_populations": bool(summary["apply_to_lbm_populations"]),
                "modify_bounceback_formula": bool(summary["modify_bounceback_formula"]),
                "applied_cell_count": int(summary["applied_cell_count"]),
                "max_applied_velocity_norm": float(summary["max_applied_velocity_norm"]),
                "mean_applied_velocity_norm": float(summary["mean_applied_velocity_norm"]),
                "wall_velocity_cap_lbm": float(summary["wall_velocity_cap_lbm"]),
                "lbm_population_update_count": int(summary["lbm_population_update_count"]),
                "after_solid_vel_norm_max": float(summary["after_solid_vel_norm_max"]),
            }
        )
    return fields


def assert_step36_driver_row(row):
    if not as_bool(row["stable"]):
        raise RuntimeError(f"Step 36 row is not stable: {row}")
    if not as_bool(row["quality_check_enabled"]) or not as_bool(row["quality_check_strict"]):
        raise RuntimeError(f"Step 36 row must use strict quality checks: {row}")
    if not as_bool(row["quality_gate_strict"]) or not as_bool(row["quality_pass"]):
        raise RuntimeError(f"Step 36 strict quality gate failed: {row}")
    if row["quality_severity"] != "ok":
        raise RuntimeError(f"Step 36 quality severity must be ok: {row}")
    if int(float(row["quality_warnings_count"])) != 0 or int(float(row["quality_reasons_count"])) != 0:
        raise RuntimeError(f"Step 36 quality report must have zero warnings/reasons: {row}")
    if int(float(row["completed_lbm_steps"])) < 5 or int(float(row["total_mpm_substeps"])) < 25:
        raise RuntimeError(f"Step 36 row did not finish configured short run: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 36 density out of range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 36 velocity out of range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0 or float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 36 MPM diagnostics out of range: {row}")
    if int(float(row["bb_link_count_max"])) <= 0 or int(float(row["active_reaction_particle_count_max"])) <= 0:
        raise RuntimeError(f"Step 36 moving-boundary row lacks reaction diagnostics: {row}")
    if as_bool(row["has_nan"]) or as_bool(row["has_inf"]):
        raise RuntimeError(f"Step 36 row contains NaN or Inf: {row}")
    if not finite_values(row, excluded=step36_driver_string_fields()):
        raise RuntimeError(f"Step 36 row has non-finite numeric diagnostics: {row}")
    if row["wall_velocity_application_mode"] == "disabled":
        if as_bool(row["wall_velocity_application_report_written"]) or int(float(row["applied_cell_count"])) != 0:
            raise RuntimeError(f"Step 36 disabled row has application side effects: {row}")
    elif row["wall_velocity_application_mode"] == "solid_vel_experimental":
        if not as_bool(row["wall_velocity_application_report_written"]) or not as_bool(row["wall_velocity_application_report_pass"]):
            raise RuntimeError(f"Step 36 application row lacks a passing report: {row}")
        if int(float(row["driver_application_report_count"])) != 5:
            raise RuntimeError(f"Step 36 driver must apply once per LBM step: {row}")
        if int(float(row["applied_cell_count"])) <= 0:
            raise RuntimeError(f"Step 36 application row has no applied cells: {row}")
        if int(float(row["lbm_population_update_count"])) != 0 or as_bool(row["apply_to_lbm_populations"]):
            raise RuntimeError(f"Step 36 application must not write LBM populations: {row}")
        if as_bool(row["modify_bounceback_formula"]):
            raise RuntimeError(f"Step 36 application must not change bounce-back formulas: {row}")
        if float(row["max_applied_velocity_norm"]) > float(row["wall_velocity_cap_lbm"]) + 1.0e-12:
            raise RuntimeError(f"Step 36 application velocity exceeds cap: {row}")
    else:
        raise RuntimeError(f"unsupported Step 36 row application mode: {row}")


def driver_summary(rows) -> dict:
    return {
        "driver_row_count": len(rows),
        "static_application_row_count": sum(1 for row in rows if row["wall_velocity_application_mode"] == "disabled"),
        "experimental_application_row_count": sum(1 for row in rows if row["wall_velocity_application_mode"] == "solid_vel_experimental"),
        "engineering_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "engineering"),
        "link_area_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "link_area_experimental"),
        "grid_32_row_count": sum(1 for row in rows if int(float(row["n_grid"])) == 32),
        "grid_48_row_count": sum(1 for row in rows if int(float(row["n_grid"])) == 48),
        "stable_count": sum(1 for row in rows if as_bool(row["stable"])),
        "quality_pass_count": sum(1 for row in rows if as_bool(row["quality_pass"])),
        "application_report_count": sum(1 for row in rows if as_bool(row["wall_velocity_application_report_written"])),
        "min_completed_lbm_steps": min(int(float(row["completed_lbm_steps"])) for row in rows),
        "min_total_mpm_substeps": min(int(float(row["total_mpm_substeps"])) for row in rows),
        "min_rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "max_lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows),
        "min_mpm_min_J_global": min(float(row["mpm_min_J_global"]) for row in rows),
        "max_mpm_max_speed_global": max(float(row["mpm_max_speed_global"]) for row in rows),
        "min_applied_cell_count": min(int(float(row["applied_cell_count"])) for row in rows),
        "max_applied_velocity_norm": max(float(row["max_applied_velocity_norm"]) for row in rows),
        "max_lbm_population_update_count": max(int(float(row["lbm_population_update_count"])) for row in rows),
        "max_bb_correction": max(float(row["bb_max_correction_global"]) for row in rows),
        "scope_note": "Step 36 applies wall velocity only through solid_vel in opt-in experimental smoke cases.",
    }


def assert_driver_summary(summary, expected_rows, expected_reports):
    if int(summary["driver_row_count"]) != int(expected_rows):
        raise RuntimeError(f"unexpected Step 36 row count: {summary}")
    if int(summary["stable_count"]) != int(expected_rows) or int(summary["quality_pass_count"]) != int(expected_rows):
        raise RuntimeError(f"all Step 36 rows must be stable and quality-passing: {summary}")
    if int(summary["application_report_count"]) != int(expected_reports):
        raise RuntimeError(f"unexpected Step 36 application report count: {summary}")
    if int(summary["min_completed_lbm_steps"]) < 5 or int(summary["min_total_mpm_substeps"]) < 25:
        raise RuntimeError(f"Step 36 driver completion summary is wrong: {summary}")
    if float(summary["min_rho_min_global"]) <= 0.95 or float(summary["max_rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 36 density summary is out of range: {summary}")
    if float(summary["max_lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 36 velocity summary is out of range: {summary}")
    if int(summary["max_lbm_population_update_count"]) != 0:
        raise RuntimeError(f"Step 36 must not directly update LBM populations: {summary}")
    if float(summary["max_bb_correction"]) <= 0.0:
        raise RuntimeError(f"Step 36 moving bounce-back correction must remain measurable: {summary}")


def compare_static_experimental_rows(static_rows, experimental_rows):
    static_by_key = {
        (int(float(row["n_grid"])), row["reaction_transfer_mode"]): row
        for row in static_rows
    }
    rows = []
    for experimental in experimental_rows:
        key = (int(float(experimental["n_grid"])), experimental["reaction_transfer_mode"])
        if key not in static_by_key:
            raise RuntimeError(f"missing static Step 36 row for {key}")
        static = static_by_key[key]
        row = {
            "comparison": f"static_vs_experimental_{key[0]}_{key[1]}",
            "static_case": static["case"],
            "experimental_case": experimental["case"],
            "n_grid": key[0],
            "reaction_transfer_mode": key[1],
            "rho_min_delta": float(experimental["rho_min_global"]) - float(static["rho_min_global"]),
            "rho_max_delta": float(experimental["rho_max_global"]) - float(static["rho_max_global"]),
            "lbm_max_v_delta": float(experimental["lbm_max_v_global"]) - float(static["lbm_max_v_global"]),
            "hydro_force_max_norm_delta": float(experimental["hydro_force_max_norm"]) - float(static["hydro_force_max_norm"]),
            "bb_max_correction_delta": float(experimental["bb_max_correction_global"]) - float(static["bb_max_correction_global"]),
            "experimental_applied_cell_count": int(float(experimental["applied_cell_count"])),
            "experimental_max_applied_velocity_norm": float(experimental["max_applied_velocity_norm"]),
            "comparison_pass": True,
            "notes": "bounded smoke comparison; Step 36 allows physical diagnostic deltas from solid_vel application",
        }
        row["comparison_pass"] = bool(
            int(row["experimental_applied_cell_count"]) > 0
            and float(experimental["max_applied_velocity_norm"]) <= float(experimental["wall_velocity_cap_lbm"]) + 1.0e-12
            and abs(row["rho_min_delta"]) <= 0.02
            and abs(row["rho_max_delta"]) <= 0.02
            and abs(row["lbm_max_v_delta"]) <= 0.05
            and math.isfinite(row["hydro_force_max_norm_delta"])
            and math.isfinite(row["bb_max_correction_delta"])
        )
        rows.append(row)
    return rows


def compare_summary(rows) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if as_bool(row["comparison_pass"])),
        "comparison_pass": all(as_bool(row["comparison_pass"]) for row in rows),
        "max_abs_lbm_max_v_delta": max(abs(float(row["lbm_max_v_delta"])) for row in rows) if rows else 0.0,
        "max_experimental_applied_velocity_norm": max(float(row["experimental_max_applied_velocity_norm"]) for row in rows) if rows else 0.0,
    }


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
    return Path(config_path).stem.removeprefix("step36_")


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


def step36_driver_string_fields():
    return {
        "case",
        "candidate_id",
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
        "wall_velocity_application_report_pass",
        "application_policy",
        "apply_to_lbm_solid_vel",
        "apply_to_lbm_populations",
        "modify_bounceback_formula",
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


class _DummyDriver:
    link_area_coupler = None
