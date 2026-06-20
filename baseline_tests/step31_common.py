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

STEP31_GEOMETRY_CONFIG_PATH = "configs/step30_squid_proxy_geometry.json"
STEP31_REGION_CONFIG_PATH = "configs/step30_squid_proxy_region_config.json"
STEP31_DRIVER_CONFIGS = [
    "configs/step31_squid_proxy_region_48_none.json",
    "configs/step31_squid_proxy_region_48_penalty.json",
    "configs/step31_squid_proxy_region_48_moving_boundary.json",
    "configs/step31_squid_proxy_region_48_link_area.json",
]

STEP31_LOG_MARKERS = {
    "logs/step31_region_projection_scale.log": "[OK] Step 31 region projection scale finished",
    "logs/step31_static_driver_smoke.log": "[OK] Step 31 static driver smoke finished",
    "logs/step31_region_driver_alignment.log": "[OK] Step 31 region driver alignment finished",
    "logs/step31_engineering_vs_link_area_static_comparison.log": "[OK] Step 31 engineering vs link-area static comparison finished",
    "logs/step31_quality_report_aggregation.log": "[OK] Step 31 quality report aggregation finished",
    "logs/step31_step30_regression_guard.log": "[OK] Step 31 Step 30 regression guard finished",
    "logs/step31_artifact_manifest.log": "[OK] Step 31 artifact manifest finished",
}

STEP31_DRIVER_FIELDS = [
    "case",
    "candidate_id",
    "geometry_type",
    "geometry_source",
    "mode",
    "reaction_transfer_mode",
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


def run_step31_static_driver_case(driver_config_path, out_dir) -> dict:
    from src.fsi_config import FSIDriverConfig
    from src.fsi_driver import FSIDriver3D
    from src.real_geometry_feasibility import summarize_short_driver_diagnostics

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    enforce_step31_driver_config(config, driver_config_path)
    driver = FSIDriver3D(config, str(out_dir))
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step 31 driver case: {driver_config_path}")
    report_path = Path(out_dir) / "geometry_quality_report.json"
    timing_path = Path(out_dir) / "driver_timing.json"
    write_json(timing_path, driver.performance_row())
    row = summarize_short_driver_diagnostics(config, diagnostics, driver, report_path)
    row["case"] = case_name(driver_config_path)
    row["candidate_id"] = "squid_proxy_region"
    row["driver_timing_path"] = relative_path(timing_path)
    row["notes"] = "Step 31 static squid proxy region driver smoke; no actuation, no swimming, no new FSI physics"
    assert_step31_static_driver_row(row)
    return row


def load_existing_step31_static_driver_case(driver_config_path, out_dir) -> dict:
    from src.fsi_config import FSIDriverConfig
    from src.real_geometry_feasibility import summarize_short_driver_diagnostics

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    enforce_step31_driver_config(config, driver_config_path)
    if config.reaction_transfer_mode == "link_area_experimental":
        raise RuntimeError("existing link-area rows must be loaded from the final static CSV or rerun")
    required = [
        Path(out_dir) / "diagnostics_timeseries.csv",
        Path(out_dir) / "geometry_quality_report.json",
        Path(out_dir) / "driver_timing.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"cannot reuse incomplete Step 31 case {driver_config_path}: {missing}")
    diagnostics = read_csv_rows(Path(out_dir) / "diagnostics_timeseries.csv")
    row = summarize_short_driver_diagnostics(config, diagnostics, _DummyDriver(), Path(out_dir) / "geometry_quality_report.json")
    row["case"] = case_name(driver_config_path)
    row["candidate_id"] = "squid_proxy_region"
    row["driver_timing_path"] = relative_path(Path(out_dir) / "driver_timing.json")
    row["notes"] = "Step 31 static squid proxy region driver smoke; no actuation, no swimming, no new FSI physics"
    assert_step31_static_driver_row(row)
    return row


def can_reuse_existing_step31_case(driver_config_path, out_dir) -> bool:
    from src.fsi_config import FSIDriverConfig

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    if config.reaction_transfer_mode == "link_area_experimental":
        return False
    return (
        (Path(out_dir) / "diagnostics_timeseries.csv").is_file()
        and (Path(out_dir) / "geometry_quality_report.json").is_file()
        and (Path(out_dir) / "driver_timing.json").is_file()
    )


def enforce_step31_driver_config(config, config_path):
    if config.geometry_type != "squid_proxy":
        raise RuntimeError(f"{config_path} must use geometry_type=squid_proxy")
    if config.geometry_config_path != STEP31_GEOMETRY_CONFIG_PATH:
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
    if config.coupling_mode in {"none", "penalty"} and config.reaction_transfer_mode != "engineering":
        raise RuntimeError(f"{config_path} none/penalty rows must keep engineering transfer")
    if config.coupling_mode == "moving_boundary" and config.reaction_transfer_mode not in {"engineering", "link_area_experimental"}:
        raise RuntimeError(f"{config_path} moving_boundary row has unsupported transfer mode")
    if config.reaction_transfer_mode == "link_area_experimental":
        if config.coupling_mode != "moving_boundary":
            raise RuntimeError(f"{config_path} link-area row must use moving_boundary")
        if config.link_area_policy != "inverse_length":
            raise RuntimeError(f"{config_path} link-area policy must be inverse_length")
        if float(config.link_area_scale_min) != 0.25 or float(config.link_area_scale_max) != 2.0:
            raise RuntimeError(f"{config_path} link-area scale bounds must be [0.25, 2.0]")


def assert_step31_static_driver_row(row):
    if not as_bool(row["stable"]):
        raise RuntimeError(f"Step 31 driver row is not stable: {row}")
    if not as_bool(row["quality_check_enabled"]) or not as_bool(row["quality_check_strict"]):
        raise RuntimeError(f"Step 31 row must use strict quality checks: {row}")
    if not as_bool(row["quality_gate_strict"]) or not as_bool(row["quality_pass"]):
        raise RuntimeError(f"Step 31 strict quality gate failed: {row}")
    if row["quality_severity"] != "ok":
        raise RuntimeError(f"Step 31 quality severity must be ok: {row}")
    if int(float(row["quality_warnings_count"])) != 0 or int(float(row["quality_reasons_count"])) != 0:
        raise RuntimeError(f"Step 31 quality report must have zero warnings/reasons: {row}")
    if int(float(row["n_grid"])) != 48 or int(float(row["n_particles"])) != 4096:
        raise RuntimeError(f"Step 31 driver row has wrong grid or particles: {row}")
    if int(float(row["completed_lbm_steps"])) < 5 or int(float(row["total_mpm_substeps"])) < 25:
        raise RuntimeError(f"Step 31 driver row did not finish the configured short run: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 31 density out of range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 31 velocity out of range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0 or float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 31 MPM diagnostics out of range: {row}")
    if float(row["projected_mass"]) <= 0.0 or int(float(row["active_cell_count"])) <= 0:
        raise RuntimeError(f"Step 31 projection diagnostics invalid: {row}")
    if as_bool(row["has_nan"]) or as_bool(row["has_inf"]):
        raise RuntimeError(f"Step 31 row contains NaN or Inf: {row}")
    if not finite_values(row, excluded=step31_short_driver_string_fields()):
        raise RuntimeError(f"Step 31 row has non-finite numeric diagnostics: {row}")
    _assert_step31_mode_specific(row)


def _assert_step31_mode_specific(row):
    mode = row["mode"]
    transfer = row["reaction_transfer_mode"]
    if mode == "none":
        if float(row["cell_force_max_norm"]) != 0.0 or int(float(row["bb_link_count_max"])) != 0:
            raise RuntimeError(f"Step 31 none row has coupling side effects: {row}")
    if mode == "penalty":
        if float(row["cell_force_max_norm"]) <= 0.0:
            raise RuntimeError(f"Step 31 penalty row lacks positive cell-force diagnostics: {row}")
        if int(float(row["bb_link_count_max"])) != 0:
            raise RuntimeError(f"Step 31 penalty row must not use moving-boundary links: {row}")
    if mode == "moving_boundary":
        if float(row["cell_force_max_norm"]) != 0.0:
            raise RuntimeError(f"Step 31 moving_boundary rows must keep cell force at zero: {row}")
        if int(float(row["bb_link_count_max"])) <= 0:
            raise RuntimeError(f"Step 31 moving_boundary row lacks bounce-back links: {row}")
        if int(float(row["active_reaction_particle_count_max"])) <= 0:
            raise RuntimeError(f"Step 31 moving_boundary row lacks active reaction particles: {row}")
        if transfer == "link_area_experimental":
            if not math.isfinite(float(row["area_scale_final"])):
                raise RuntimeError(f"Step 31 link-area row area scale is not finite: {row}")
            if not (0.25 <= float(row["area_scale_final"]) <= 2.0):
                raise RuntimeError(f"Step 31 link-area row area scale out of range: {row}")


def static_driver_summary(rows) -> dict:
    timings = [read_json(row["driver_timing_path"]) for row in rows]
    total_times = [float(item.get("total_time", 0.0)) for item in timings]
    moving_rows = [row for row in rows if row["mode"] == "moving_boundary"]
    return {
        "driver_row_count": len(rows),
        "candidate_count": len({row["candidate_id"] for row in rows}),
        "none_row_count": sum(1 for row in rows if row["mode"] == "none"),
        "penalty_row_count": sum(1 for row in rows if row["mode"] == "penalty"),
        "moving_boundary_row_count": len(moving_rows),
        "engineering_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "engineering"),
        "link_area_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "link_area_experimental"),
        "stable_count": sum(1 for row in rows if as_bool(row["stable"])),
        "quality_report_count": sum(1 for row in rows if (ROOT / row["quality_report_path"]).is_file()),
        "quality_pass_count": sum(1 for row in rows if as_bool(row["quality_pass"])),
        "strict_count": sum(1 for row in rows if as_bool(row["quality_gate_strict"])),
        "min_completed_lbm_steps": min(int(float(row["completed_lbm_steps"])) for row in rows),
        "min_total_mpm_substeps": min(int(float(row["total_mpm_substeps"])) for row in rows),
        "min_rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "max_lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows),
        "min_mpm_min_J_global": min(float(row["mpm_min_J_global"]) for row in rows),
        "max_mpm_max_speed_global": max(float(row["mpm_max_speed_global"]) for row in rows),
        "min_projected_mass": min(float(row["projected_mass"]) for row in rows),
        "min_active_cell_count": min(int(float(row["active_cell_count"])) for row in rows),
        "max_cell_force_max_norm": max(float(row["cell_force_max_norm"]) for row in rows),
        "max_hydro_force_max_norm": max(float(row["hydro_force_max_norm"]) for row in rows),
        "min_moving_bb_link_count_max": min(int(float(row["bb_link_count_max"])) for row in moving_rows) if moving_rows else 0,
        "min_moving_active_reaction_particle_count_max": min(int(float(row["active_reaction_particle_count_max"])) for row in moving_rows) if moving_rows else 0,
        "max_driver_total_time": max(total_times) if total_times else 0.0,
        "scope_note": "Step 31 static squid proxy region driver smoke only; not real squid validation.",
    }


def assert_static_driver_summary(summary):
    if int(summary["driver_row_count"]) != 4 or int(summary["candidate_count"]) != 1:
        raise RuntimeError(f"expected four Step 31 driver rows for one proxy candidate: {summary}")
    if int(summary["none_row_count"]) != 1 or int(summary["penalty_row_count"]) != 1 or int(summary["moving_boundary_row_count"]) != 2:
        raise RuntimeError(f"Step 31 mode split is wrong: {summary}")
    if int(summary["engineering_row_count"]) != 3 or int(summary["link_area_row_count"]) != 1:
        raise RuntimeError(f"Step 31 transfer split is wrong: {summary}")
    if int(summary["stable_count"]) != 4 or int(summary["quality_report_count"]) != 4:
        raise RuntimeError(f"all Step 31 rows must be stable and report-backed: {summary}")
    if int(summary["quality_pass_count"]) != 4 or int(summary["strict_count"]) != 4:
        raise RuntimeError(f"all Step 31 rows must pass strict quality gates: {summary}")
    if int(summary["min_completed_lbm_steps"]) < 5 or int(summary["min_total_mpm_substeps"]) < 25:
        raise RuntimeError(f"Step 31 driver completion summary is wrong: {summary}")
    if float(summary["min_rho_min_global"]) <= 0.95 or float(summary["max_rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 31 density summary is out of range: {summary}")
    if float(summary["max_lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 31 velocity summary is out of range: {summary}")
    if float(summary["min_mpm_min_J_global"]) <= 0.0 or float(summary["max_mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 31 MPM summary is out of range: {summary}")
    if float(summary["min_projected_mass"]) <= 0.0 or int(summary["min_active_cell_count"]) <= 0:
        raise RuntimeError(f"Step 31 projection summary is invalid: {summary}")
    if int(summary["min_moving_bb_link_count_max"]) <= 0 or int(summary["min_moving_active_reaction_particle_count_max"]) <= 0:
        raise RuntimeError(f"Step 31 moving-boundary summary lacks reaction diagnostics: {summary}")


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
    return Path(config_path).stem.removeprefix("step31_")


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


def step31_short_driver_string_fields():
    return {
        "case",
        "candidate_id",
        "geometry_type",
        "geometry_source",
        "mode",
        "reaction_transfer_mode",
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
