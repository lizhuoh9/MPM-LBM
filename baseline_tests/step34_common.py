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

STEP34_BOUNDARY_MOTION_CONFIG_PATH = "configs/step34_boundary_motion_interface_prescribed_kinematic.json"
STEP34_GEOMETRY_CONFIG_PATH = "configs/step30_squid_proxy_geometry.json"
STEP34_STATIC_DRIVER_CONFIGS = [
    "configs/step34_squid_proxy_static_48_none.json",
    "configs/step34_squid_proxy_static_48_penalty.json",
    "configs/step34_squid_proxy_static_48_moving_boundary.json",
    "configs/step34_squid_proxy_static_48_link_area.json",
]
STEP34_PRESCRIBED_DRIVER_CONFIGS = [
    "configs/step34_squid_proxy_prescribed_interface_48_moving_boundary.json",
    "configs/step34_squid_proxy_prescribed_interface_48_link_area.json",
]
STEP34_DRIVER_CONFIGS = STEP34_STATIC_DRIVER_CONFIGS + STEP34_PRESCRIBED_DRIVER_CONFIGS

STEP34_LOG_MARKERS = {
    "logs/step34_boundary_motion_config_validation.log": "[OK] Step 34 boundary motion config validation finished",
    "logs/step34_boundary_motion_interface_report.log": "[OK] Step 34 boundary motion interface report finished",
    "logs/step34_static_driver_regression.log": "[OK] Step 34 static driver regression finished",
    "logs/step34_prescribed_interface_noop_smoke.log": "[OK] Step 34 prescribed interface no-op smoke finished",
    "logs/step34_step31_static_comparison.log": "[OK] Step 34 Step 31 static comparison finished",
    "logs/step34_noop_state_guard.log": "[OK] Step 34 no-op state guard finished",
    "logs/step34_quality_report_aggregation.log": "[OK] Step 34 quality report aggregation finished",
    "logs/step34_step33_regression_guard.log": "[OK] Step 34 Step 33 regression guard finished",
    "logs/step34_artifact_manifest.log": "[OK] Step 34 artifact manifest finished",
}

STEP34_DRIVER_FIELDS = [
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
    "boundary_motion_no_op_pass",
    "boundary_motion_schedule_row_count",
    "boundary_motion_motion_mapping_row_count",
    "boundary_motion_tracked_region_count",
    "boundary_motion_execution_flag_enabled_count",
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

NOOP_COMPARE_FIELDS = [
    "rho_min_global",
    "rho_max_global",
    "lbm_max_v_global",
    "mpm_min_J_global",
    "mpm_max_speed_global",
    "projected_mass",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "area_scale_final",
    "area_scale_min",
    "area_scale_max",
    "raw_area_scale_final",
]

NOOP_COMPARE_INT_FIELDS = [
    "active_cell_count",
    "bb_link_count_min",
    "bb_link_count_max",
    "active_reaction_particle_count_max",
    "completed_lbm_steps",
    "total_mpm_substeps",
]


def run_step34_driver_case(driver_config_path, out_dir) -> dict:
    from src.fsi_config import FSIDriverConfig
    from src.fsi_driver import FSIDriver3D
    from src.real_geometry_feasibility import summarize_short_driver_diagnostics

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    enforce_step34_driver_config(config, driver_config_path)
    driver = FSIDriver3D(config, str(out_dir))
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step 34 driver case: {driver_config_path}")
    report_path = Path(out_dir) / "geometry_quality_report.json"
    timing_path = Path(out_dir) / "driver_timing.json"
    write_json(timing_path, driver.performance_row())
    row = summarize_short_driver_diagnostics(config, diagnostics, driver, report_path)
    row["case"] = case_name(driver_config_path)
    row["candidate_id"] = "squid_proxy_boundary_motion_interface"
    row["driver_timing_path"] = relative_path(timing_path)
    row["notes"] = "Step 34 boundary-motion driver interface; diagnostic-only no-op hook"
    row.update(boundary_motion_row_fields(config, out_dir))
    assert_step34_driver_row(row)
    return row


def load_existing_step34_driver_case(driver_config_path, out_dir) -> dict:
    from src.fsi_config import FSIDriverConfig
    from src.real_geometry_feasibility import summarize_short_driver_diagnostics

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    enforce_step34_driver_config(config, driver_config_path)
    if config.reaction_transfer_mode == "link_area_experimental":
        raise RuntimeError("existing link-area rows must be loaded from the final Step 34 CSV or rerun")
    required = [
        Path(out_dir) / "diagnostics_timeseries.csv",
        Path(out_dir) / "geometry_quality_report.json",
        Path(out_dir) / "driver_timing.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"cannot reuse incomplete Step 34 case {driver_config_path}: {missing}")
    diagnostics = read_csv_rows(Path(out_dir) / "diagnostics_timeseries.csv")
    row = summarize_short_driver_diagnostics(config, diagnostics, _DummyDriver(), Path(out_dir) / "geometry_quality_report.json")
    row["case"] = case_name(driver_config_path)
    row["candidate_id"] = "squid_proxy_boundary_motion_interface"
    row["driver_timing_path"] = relative_path(Path(out_dir) / "driver_timing.json")
    row["notes"] = "Step 34 boundary-motion driver interface; diagnostic-only no-op hook"
    row.update(boundary_motion_row_fields(config, out_dir))
    assert_step34_driver_row(row)
    return row


def can_reuse_existing_step34_case(driver_config_path, out_dir) -> bool:
    from src.fsi_config import FSIDriverConfig

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    if config.reaction_transfer_mode == "link_area_experimental":
        return False
    return (
        (Path(out_dir) / "diagnostics_timeseries.csv").is_file()
        and (Path(out_dir) / "geometry_quality_report.json").is_file()
        and (Path(out_dir) / "driver_timing.json").is_file()
    )


def enforce_step34_driver_config(config, config_path):
    if config.geometry_type != "squid_proxy":
        raise RuntimeError(f"{config_path} must use geometry_type=squid_proxy")
    if config.geometry_config_path != STEP34_GEOMETRY_CONFIG_PATH:
        raise RuntimeError(f"{config_path} must reuse the Step 30 squid proxy geometry config")
    if int(config.n_grid) != 48 or int(config.n_particles) != 4096:
        raise RuntimeError(f"{config_path} must use n_grid=48 and n_particles=4096")
    if int(config.n_lbm_steps) != 5 or int(config.mpm_substeps_per_lbm_step) != 5:
        raise RuntimeError(f"{config_path} must use 5 LBM steps and 5 MPM substeps")
    if int(config.output_interval) != 1:
        raise RuntimeError(f"{config_path} must write diagnostics every LBM step")
    if config.write_vtk or config.write_particles:
        raise RuntimeError(f"{config_path} must disable VTK and particle outputs")
    if not config.quality_check_enabled or not config.quality_check_strict:
        raise RuntimeError(f"{config_path} must enable strict quality checks")
    if config.boundary_motion_mode == "static":
        if config.boundary_motion_config_path is not None or config.boundary_motion_report_enabled:
            raise RuntimeError(f"{config_path} static rows must not load or write boundary-motion reports")
    elif config.boundary_motion_mode == "prescribed_kinematic":
        if config.boundary_motion_config_path != STEP34_BOUNDARY_MOTION_CONFIG_PATH:
            raise RuntimeError(f"{config_path} prescribed rows must use the Step 34 boundary-motion config")
        if not config.boundary_motion_report_enabled:
            raise RuntimeError(f"{config_path} prescribed rows must enable boundary-motion reporting")
        if config.coupling_mode != "moving_boundary":
            raise RuntimeError(f"{config_path} prescribed rows are limited to moving_boundary smoke cases")
    else:
        raise RuntimeError(f"{config_path} has unsupported boundary_motion_mode={config.boundary_motion_mode}")
    if config.coupling_mode in {"none", "penalty"} and config.reaction_transfer_mode != "engineering":
        raise RuntimeError(f"{config_path} none/penalty rows must keep engineering transfer")
    if config.coupling_mode == "moving_boundary" and config.reaction_transfer_mode not in {"engineering", "link_area_experimental"}:
        raise RuntimeError(f"{config_path} moving_boundary row has unsupported transfer mode")
    if config.reaction_transfer_mode == "link_area_experimental":
        if config.coupling_mode != "moving_boundary":
            raise RuntimeError(f"{config_path} link-area row must use moving_boundary")
        if config.link_area_policy != "inverse_length":
            raise RuntimeError(f"{config_path} link-area policy must be inverse_length")


def boundary_motion_row_fields(config, out_dir) -> dict:
    report_path = Path(out_dir) / "boundary_motion_interface_report.json"
    fields = {
        "boundary_motion_mode": config.boundary_motion_mode,
        "boundary_motion_config_path": config.boundary_motion_config_path or "",
        "boundary_motion_report_enabled": bool(config.boundary_motion_report_enabled),
        "boundary_motion_report_written": report_path.is_file(),
        "boundary_motion_interface_report_path": relative_path(report_path) if report_path.is_file() else "",
        "boundary_motion_no_op_pass": config.boundary_motion_mode == "static",
        "boundary_motion_schedule_row_count": 0,
        "boundary_motion_motion_mapping_row_count": 0,
        "boundary_motion_tracked_region_count": 0,
        "boundary_motion_execution_flag_enabled_count": 0,
    }
    if report_path.is_file():
        summary = read_json(report_path)["summary"]
        fields.update(
            {
                "boundary_motion_no_op_pass": bool(summary["no_op_pass"]),
                "boundary_motion_schedule_row_count": int(summary["schedule_row_count"]),
                "boundary_motion_motion_mapping_row_count": int(summary["motion_mapping_row_count"]),
                "boundary_motion_tracked_region_count": int(summary["tracked_region_count"]),
                "boundary_motion_execution_flag_enabled_count": int(summary["execution_flag_enabled_count"]),
            }
        )
    return fields


def assert_step34_driver_row(row):
    if not as_bool(row["stable"]):
        raise RuntimeError(f"Step 34 driver row is not stable: {row}")
    if not as_bool(row["quality_check_enabled"]) or not as_bool(row["quality_check_strict"]):
        raise RuntimeError(f"Step 34 row must use strict quality checks: {row}")
    if not as_bool(row["quality_gate_strict"]) or not as_bool(row["quality_pass"]):
        raise RuntimeError(f"Step 34 strict quality gate failed: {row}")
    if row["quality_severity"] != "ok":
        raise RuntimeError(f"Step 34 quality severity must be ok: {row}")
    if int(float(row["quality_warnings_count"])) != 0 or int(float(row["quality_reasons_count"])) != 0:
        raise RuntimeError(f"Step 34 quality report must have zero warnings/reasons: {row}")
    if int(float(row["n_grid"])) != 48 or int(float(row["n_particles"])) != 4096:
        raise RuntimeError(f"Step 34 driver row has wrong grid or particles: {row}")
    if int(float(row["completed_lbm_steps"])) < 5 or int(float(row["total_mpm_substeps"])) < 25:
        raise RuntimeError(f"Step 34 driver row did not finish the configured short run: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 34 density out of range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 34 velocity out of range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0 or float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 34 MPM diagnostics out of range: {row}")
    if float(row["projected_mass"]) <= 0.0 or int(float(row["active_cell_count"])) <= 0:
        raise RuntimeError(f"Step 34 projection diagnostics invalid: {row}")
    if as_bool(row["has_nan"]) or as_bool(row["has_inf"]):
        raise RuntimeError(f"Step 34 row contains NaN or Inf: {row}")
    if not finite_values(row, excluded=step34_driver_string_fields()):
        raise RuntimeError(f"Step 34 row has non-finite numeric diagnostics: {row}")
    _assert_step34_mode_specific(row)
    _assert_step34_boundary_fields(row)


def _assert_step34_mode_specific(row):
    mode = row["mode"]
    transfer = row["reaction_transfer_mode"]
    if mode == "none":
        if float(row["cell_force_max_norm"]) != 0.0 or int(float(row["bb_link_count_max"])) != 0:
            raise RuntimeError(f"Step 34 none row has coupling side effects: {row}")
    if mode == "penalty":
        if float(row["cell_force_max_norm"]) <= 0.0:
            raise RuntimeError(f"Step 34 penalty row lacks positive cell-force diagnostics: {row}")
        if int(float(row["bb_link_count_max"])) != 0:
            raise RuntimeError(f"Step 34 penalty row must not use moving-boundary links: {row}")
    if mode == "moving_boundary":
        if float(row["cell_force_max_norm"]) != 0.0:
            raise RuntimeError(f"Step 34 moving_boundary rows must keep cell force at zero: {row}")
        if int(float(row["bb_link_count_max"])) <= 0:
            raise RuntimeError(f"Step 34 moving_boundary row lacks bounce-back links: {row}")
        if int(float(row["active_reaction_particle_count_max"])) <= 0:
            raise RuntimeError(f"Step 34 moving_boundary row lacks active reaction particles: {row}")
        if transfer == "link_area_experimental" and not (0.25 <= float(row["area_scale_final"]) <= 2.0):
            raise RuntimeError(f"Step 34 link-area row area scale out of range: {row}")


def _assert_step34_boundary_fields(row):
    mode = row["boundary_motion_mode"]
    if mode == "static":
        if as_bool(row["boundary_motion_report_written"]):
            raise RuntimeError(f"Step 34 static row unexpectedly wrote a boundary-motion report: {row}")
        if not as_bool(row["boundary_motion_no_op_pass"]):
            raise RuntimeError(f"Step 34 static boundary-motion no-op must pass: {row}")
    elif mode == "prescribed_kinematic":
        if not as_bool(row["boundary_motion_report_written"]) or not as_bool(row["boundary_motion_no_op_pass"]):
            raise RuntimeError(f"Step 34 prescribed row must write a passing no-op report: {row}")
        if int(float(row["boundary_motion_schedule_row_count"])) != 81:
            raise RuntimeError(f"Step 34 prescribed row has wrong schedule row count: {row}")
        if int(float(row["boundary_motion_motion_mapping_row_count"])) != 243:
            raise RuntimeError(f"Step 34 prescribed row has wrong motion row count: {row}")
        if int(float(row["boundary_motion_tracked_region_count"])) != 3:
            raise RuntimeError(f"Step 34 prescribed row has wrong tracked-region count: {row}")
        if int(float(row["boundary_motion_execution_flag_enabled_count"])) != 0:
            raise RuntimeError(f"Step 34 prescribed row has enabled execution flags: {row}")
    else:
        raise RuntimeError(f"unsupported Step 34 boundary motion mode in row: {row}")


def driver_summary(rows) -> dict:
    return {
        "driver_row_count": len(rows),
        "static_boundary_motion_row_count": sum(1 for row in rows if row["boundary_motion_mode"] == "static"),
        "prescribed_boundary_motion_row_count": sum(1 for row in rows if row["boundary_motion_mode"] == "prescribed_kinematic"),
        "none_row_count": sum(1 for row in rows if row["mode"] == "none"),
        "penalty_row_count": sum(1 for row in rows if row["mode"] == "penalty"),
        "moving_boundary_row_count": sum(1 for row in rows if row["mode"] == "moving_boundary"),
        "engineering_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "engineering"),
        "link_area_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "link_area_experimental"),
        "stable_count": sum(1 for row in rows if as_bool(row["stable"])),
        "quality_pass_count": sum(1 for row in rows if as_bool(row["quality_pass"])),
        "strict_count": sum(1 for row in rows if as_bool(row["quality_gate_strict"])),
        "boundary_report_count": sum(1 for row in rows if as_bool(row["boundary_motion_report_written"])),
        "boundary_no_op_pass_count": sum(1 for row in rows if as_bool(row["boundary_motion_no_op_pass"])),
        "min_completed_lbm_steps": min(int(float(row["completed_lbm_steps"])) for row in rows),
        "min_total_mpm_substeps": min(int(float(row["total_mpm_substeps"])) for row in rows),
        "min_rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "max_lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows),
        "min_mpm_min_J_global": min(float(row["mpm_min_J_global"]) for row in rows),
        "max_mpm_max_speed_global": max(float(row["mpm_max_speed_global"]) for row in rows),
        "min_projected_mass": min(float(row["projected_mass"]) for row in rows),
        "min_active_cell_count": min(int(float(row["active_cell_count"])) for row in rows),
        "max_boundary_motion_execution_flag_enabled_count": max(int(float(row["boundary_motion_execution_flag_enabled_count"])) for row in rows),
        "scope_note": "Step 34 driver rows verify a diagnostic-only boundary-motion interface, not solver actuation.",
    }


def assert_driver_summary(summary, expected_rows, expected_boundary_reports):
    if int(summary["driver_row_count"]) != int(expected_rows):
        raise RuntimeError(f"unexpected Step 34 driver row count: {summary}")
    if int(summary["stable_count"]) != int(expected_rows):
        raise RuntimeError(f"all Step 34 driver rows must be stable: {summary}")
    if int(summary["quality_pass_count"]) != int(expected_rows) or int(summary["strict_count"]) != int(expected_rows):
        raise RuntimeError(f"all Step 34 driver rows must pass strict quality gates: {summary}")
    if int(summary["boundary_report_count"]) != int(expected_boundary_reports):
        raise RuntimeError(f"unexpected Step 34 boundary report count: {summary}")
    if int(summary["boundary_no_op_pass_count"]) != int(expected_rows):
        raise RuntimeError(f"all Step 34 rows must pass boundary no-op checks: {summary}")
    if int(summary["min_completed_lbm_steps"]) < 5 or int(summary["min_total_mpm_substeps"]) < 25:
        raise RuntimeError(f"Step 34 driver completion summary is wrong: {summary}")
    if float(summary["min_rho_min_global"]) <= 0.95 or float(summary["max_rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 34 density summary is out of range: {summary}")
    if float(summary["max_lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 34 velocity summary is out of range: {summary}")
    if float(summary["min_mpm_min_J_global"]) <= 0.0 or float(summary["max_mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 34 MPM summary is out of range: {summary}")
    if float(summary["min_projected_mass"]) <= 0.0 or int(summary["min_active_cell_count"]) <= 0:
        raise RuntimeError(f"Step 34 projection summary is invalid: {summary}")
    if int(summary["max_boundary_motion_execution_flag_enabled_count"]) != 0:
        raise RuntimeError(f"Step 34 enabled boundary-motion execution flags: {summary}")


def compare_row_pair(left, right, comparison_name, tolerance=1.0e-6) -> dict:
    row = {
        "comparison": comparison_name,
        "left_case": left["case"],
        "right_case": right["case"],
        "mode": left["mode"],
        "reaction_transfer_mode": left["reaction_transfer_mode"],
        "max_abs_float_delta": 0.0,
        "int_mismatch_count": 0,
        "comparison_pass": True,
        "notes": "Step 34 no-op comparison over accepted short-driver diagnostics",
    }
    for field in NOOP_COMPARE_FIELDS:
        delta = abs(float(right[field]) - float(left[field]))
        row[f"{field}_delta"] = delta
        row["max_abs_float_delta"] = max(float(row["max_abs_float_delta"]), delta)
        if delta > tolerance:
            row["comparison_pass"] = False
    for field in NOOP_COMPARE_INT_FIELDS:
        delta = int(float(right[field])) - int(float(left[field]))
        row[f"{field}_delta"] = delta
        if delta != 0:
            row["int_mismatch_count"] += 1
            row["comparison_pass"] = False
    return row


def compare_summary(rows) -> dict:
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if as_bool(row["comparison_pass"])),
        "max_abs_float_delta": max(float(row["max_abs_float_delta"]) for row in rows) if rows else 0.0,
        "int_mismatch_count": sum(int(row["int_mismatch_count"]) for row in rows),
        "comparison_pass": all(as_bool(row["comparison_pass"]) for row in rows),
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
    return Path(config_path).stem.removeprefix("step34_")


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


def step34_driver_string_fields():
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
        "boundary_motion_no_op_pass",
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
