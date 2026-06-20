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

STEP28_DESCRIPTORS = [
    "configs/step25_candidate_smoke_mesh_descriptor.json",
    "configs/step25_candidate_smoke_voxel_descriptor.json",
]

STEP28_GEOMETRY_CONFIGS = {
    "real_candidate_smoke_mesh": "configs/step26_real_candidate_smoke_mesh_geometry.json",
    "real_candidate_smoke_voxel": "configs/step26_real_candidate_smoke_voxel_geometry.json",
}

STEP28_DRIVER_CONFIGS = [
    "configs/step28_compare_real_candidate_smoke_mesh_64_moving_boundary.json",
    "configs/step28_compare_real_candidate_smoke_mesh_64_link_area.json",
    "configs/step28_compare_real_candidate_smoke_voxel_64_moving_boundary.json",
    "configs/step28_compare_real_candidate_smoke_voxel_64_link_area.json",
]

STEP28_LOG_MARKERS = {
    "logs/step28_candidate_fingerprint_guard.log": "[OK] Step 28 candidate fingerprint guard finished",
    "logs/step28_64_transfer_pair_driver.log": "[OK] Step 28 64 transfer pair driver finished",
    "logs/step28_engineering_vs_link_area_comparison.log": "[OK] Step 28 engineering vs link-area comparison finished",
    "logs/step28_force_reaction_diagnostics.log": "[OK] Step 28 force reaction diagnostics finished",
    "logs/step28_area_scale_envelope.log": "[OK] Step 28 area-scale envelope finished",
    "logs/step28_step27_prefix_regression.log": "[OK] Step 28 Step 27 prefix regression finished",
    "logs/step28_quality_report_aggregation.log": "[OK] Step 28 quality report aggregation finished",
    "logs/step28_step27_regression_guard.log": "[OK] Step 28 Step 27 regression guard finished",
    "logs/step28_artifact_manifest.log": "[OK] Step 28 artifact manifest finished",
}


def run_step28_transfer_driver_case(driver_config_path, out_dir) -> dict:
    from src.fsi_config import FSIDriverConfig
    from src.fsi_driver import FSIDriver3D
    from src.real_geometry_feasibility import summarize_short_driver_diagnostics

    config = FSIDriverConfig.from_json(resolve_path(driver_config_path))
    enforce_step28_driver_config(config, driver_config_path)
    driver = FSIDriver3D(config, str(out_dir))
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step 28 driver case: {driver_config_path}")
    report_path = Path(out_dir) / "geometry_quality_report.json"
    timing_path = Path(out_dir) / "driver_timing.json"
    write_json(timing_path, driver.performance_row())
    row = summarize_short_driver_diagnostics(config, diagnostics, driver, report_path)
    row["driver_timing_path"] = relative_path(timing_path)
    row["notes"] = "Step 28 controlled real geometry 64^3 transfer diagnostics; not real squid validation"
    assert_step28_transfer_driver_row(row)
    return row


def enforce_step28_driver_config(config, config_path):
    if int(config.n_grid) != 64:
        raise RuntimeError(f"{config_path} must use n_grid=64")
    if int(config.n_lbm_steps) != 10 or int(config.mpm_substeps_per_lbm_step) != 5:
        raise RuntimeError(f"{config_path} must use 10 LBM steps and 5 MPM substeps")
    if int(config.output_interval) != 1:
        raise RuntimeError(f"{config_path} must write diagnostics every LBM step")
    if config.write_vtk or config.write_particles:
        raise RuntimeError(f"{config_path} must disable VTK and particle outputs")
    if not config.quality_check_enabled or not config.quality_check_strict:
        raise RuntimeError(f"{config_path} must enable strict quality checks")
    if config.coupling_mode != "moving_boundary":
        raise RuntimeError(f"{config_path} must be a moving_boundary row")
    if config.reaction_transfer_mode not in {"engineering", "link_area_experimental"}:
        raise RuntimeError(f"{config_path} has unsupported transfer mode: {config.reaction_transfer_mode}")
    if config.reaction_transfer_mode == "link_area_experimental":
        if config.link_area_policy != "inverse_length":
            raise RuntimeError(f"{config_path} link-area policy must be inverse_length")
        if float(config.link_area_scale_min) != 0.25 or float(config.link_area_scale_max) != 2.0:
            raise RuntimeError(f"{config_path} link-area scale bounds must be [0.25, 2.0]")


def assert_step28_transfer_driver_row(row):
    if not as_bool(row["stable"]):
        raise RuntimeError(f"Step 28 driver row is not stable: {row}")
    if not as_bool(row["quality_check_enabled"]) or not as_bool(row["quality_check_strict"]):
        raise RuntimeError(f"Step 28 row must use strict quality checks: {row}")
    if not as_bool(row["quality_gate_strict"]) or not as_bool(row["quality_pass"]):
        raise RuntimeError(f"Step 28 strict quality gate failed: {row}")
    if row["quality_severity"] != "ok":
        raise RuntimeError(f"Step 28 quality severity must be ok: {row}")
    if int(float(row["quality_warnings_count"])) != 0 or int(float(row["quality_reasons_count"])) != 0:
        raise RuntimeError(f"Step 28 quality report must have zero warnings/reasons: {row}")
    if int(float(row["n_grid"])) != 64 or int(float(row["n_lbm_steps"])) != 10:
        raise RuntimeError(f"Step 28 driver row has the wrong grid or window: {row}")
    if int(float(row["completed_lbm_steps"])) < 10 or int(float(row["total_mpm_substeps"])) < 50:
        raise RuntimeError(f"Step 28 driver row did not finish configured short run: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 28 density out of range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 28 velocity out of range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0 or float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 28 MPM diagnostics out of range: {row}")
    if float(row["projected_mass"]) <= 0.0 or int(float(row["active_cell_count"])) <= 0:
        raise RuntimeError(f"Step 28 projection diagnostics invalid: {row}")
    if as_bool(row["has_nan"]) or as_bool(row["has_inf"]):
        raise RuntimeError(f"Step 28 driver row contains NaN or Inf: {row}")
    if row["mode"] != "moving_boundary":
        raise RuntimeError(f"Step 28 only accepts moving_boundary rows: {row}")
    if float(row["cell_force_max_norm"]) != 0.0:
        raise RuntimeError(f"Step 28 moving_boundary rows must keep cell force at zero: {row}")
    if float(row["hydro_force_max_norm"]) <= 0.0:
        raise RuntimeError(f"Step 28 row lacks positive hydrodynamic force diagnostics: {row}")
    if int(float(row["bb_link_count_min"])) <= 0 or int(float(row["bb_link_count_max"])) <= 0:
        raise RuntimeError(f"Step 28 row lacks moving-boundary links: {row}")
    if int(float(row["active_reaction_particle_count_max"])) <= 0:
        raise RuntimeError(f"Step 28 row lacks active reaction particles: {row}")
    if row["reaction_transfer_mode"] == "link_area_experimental":
        if not math.isfinite(float(row["area_scale_final"])):
            raise RuntimeError(f"Step 28 link-area row area scale is not finite: {row}")
        if not math.isfinite(float(row["raw_area_scale_final"])):
            raise RuntimeError(f"Step 28 link-area row raw area scale is not finite: {row}")
        if not (0.25 <= float(row["area_scale_final"]) <= 2.0):
            raise RuntimeError(f"Step 28 link-area final area scale out of range: {row}")
        if not (0.25 <= float(row["area_scale_min"]) <= float(row["area_scale_max"]) <= 2.0):
            raise RuntimeError(f"Step 28 link-area area scale bounds out of range: {row}")
    if not finite_values(row, excluded=short_driver_string_fields()):
        raise RuntimeError(f"Step 28 driver row has non-finite numeric diagnostics: {row}")


def transfer_pair_summary(rows) -> dict:
    timings = [load_json(row["driver_timing_path"]) for row in rows]
    total_times = [float(item.get("total_time", 0.0)) for item in timings]
    return {
        "driver_row_count": len(rows),
        "candidate_count": len({row["candidate_id"] for row in rows}),
        "mesh_row_count": sum(1 for row in rows if row["geometry_type"] == "mesh"),
        "voxel_row_count": sum(1 for row in rows if row["geometry_type"] == "voxel"),
        "moving_boundary_row_count": sum(1 for row in rows if row["mode"] == "moving_boundary"),
        "engineering_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "engineering"),
        "link_area_row_count": sum(1 for row in rows if row["reaction_transfer_mode"] == "link_area_experimental"),
        "stable_count": sum(1 for row in rows if as_bool(row["stable"])),
        "quality_report_count": sum(1 for row in rows if (ROOT / row["quality_report_path"]).is_file()),
        "quality_pass_count": sum(1 for row in rows if as_bool(row["quality_pass"])),
        "strict_count": sum(1 for row in rows if as_bool(row["quality_gate_strict"])),
        "min_rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "max_lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows),
        "min_mpm_min_J_global": min(float(row["mpm_min_J_global"]) for row in rows),
        "max_mpm_max_speed_global": max(float(row["mpm_max_speed_global"]) for row in rows),
        "min_projected_mass": min(float(row["projected_mass"]) for row in rows),
        "min_active_cell_count": min(int(float(row["active_cell_count"])) for row in rows),
        "max_hydro_force_max_norm": max(float(row["hydro_force_max_norm"]) for row in rows),
        "min_bb_link_count_min": min(int(float(row["bb_link_count_min"])) for row in rows),
        "max_driver_total_time": max(total_times) if total_times else 0.0,
        "scope_note": "Step 28 64^3 transfer diagnostics only; not real squid validation.",
    }


def assert_transfer_pair_summary(summary):
    if int(summary["driver_row_count"]) != 4 or int(summary["candidate_count"]) != 2:
        raise RuntimeError(f"expected 4 Step 28 transfer rows across 2 candidates: {summary}")
    if int(summary["mesh_row_count"]) != 2 or int(summary["voxel_row_count"]) != 2:
        raise RuntimeError(f"Step 28 geometry split is wrong: {summary}")
    if int(summary["moving_boundary_row_count"]) != 4:
        raise RuntimeError(f"Step 28 must only contain moving_boundary rows: {summary}")
    if int(summary["engineering_row_count"]) != 2 or int(summary["link_area_row_count"]) != 2:
        raise RuntimeError(f"Step 28 transfer split is wrong: {summary}")
    if int(summary["stable_count"]) != 4 or int(summary["quality_report_count"]) != 4:
        raise RuntimeError(f"all Step 28 rows must be stable and report-backed: {summary}")
    if int(summary["quality_pass_count"]) != 4 or int(summary["strict_count"]) != 4:
        raise RuntimeError(f"all Step 28 rows must pass strict quality gates: {summary}")
    if float(summary["min_rho_min_global"]) <= 0.95 or float(summary["max_rho_max_global"]) >= 1.05:
        raise RuntimeError(f"Step 28 density summary is out of range: {summary}")
    if float(summary["max_lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"Step 28 velocity summary is out of range: {summary}")
    if float(summary["min_mpm_min_J_global"]) <= 0.0 or float(summary["max_mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"Step 28 MPM summary is out of range: {summary}")
    if float(summary["min_projected_mass"]) <= 0.0 or int(summary["min_active_cell_count"]) <= 0:
        raise RuntimeError(f"Step 28 projection summary is invalid: {summary}")
    if int(summary["min_bb_link_count_min"]) <= 0:
        raise RuntimeError(f"Step 28 moving-boundary link summary is invalid: {summary}")
    if not math.isfinite(float(summary["max_driver_total_time"])) or float(summary["max_driver_total_time"]) <= 0.0:
        raise RuntimeError(f"Step 28 driver timing summary is invalid: {summary}")


def diagnostics_path_from_driver_row(row) -> str:
    return relative_path(Path(row["driver_timing_path"]).parent / "diagnostics_timeseries.csv")


def load_json(path):
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


def relative_path(path) -> str:
    return os.path.relpath(resolve_path(path), ROOT).replace("\\", "/")


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return ROOT / path_obj


def case_name(config_path):
    return Path(config_path).stem.removeprefix("step28_compare_")


def csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


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


def short_driver_string_fields():
    return {
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
