from __future__ import annotations

import shutil
import time
from dataclasses import fields
from pathlib import Path

from src.mpm_lbm.evidence.step111_real_monitor_extraction import (
    append_step111_monitors,
    fixed_base_stats,
    write_step111_monitor_timeseries,
)
from src.mpm_lbm.evidence.step112_common import (
    ALLOWED_CLAIM,
    has_nan_or_inf,
    max_numeric,
    numeric_values_finite,
    read_json,
    reset_output_dir,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)
from src.mpm_lbm.evidence.step112_error_scoring import sort_real_candidate_rows
from src.mpm_lbm.evidence.step112_real_dynamics_diagnostics import component_diagnostics_row, coerce_diagnostics_rows
from src.mpm_lbm.validation.error_metrics import compute_displacement_error_metrics
from src.mpm_lbm.validation.fluent_public_reference import (
    SOLVER_DISPLACEMENT_KEY,
    load_public_fluent_reference_curve,
    resample_to_common_time_grid,
)


MATRIX_FIELDS = [
    "row_name",
    "evidence_mode",
    "driver_run_called",
    "restart_loaded",
    "preflow_source",
    "completed_official_fsi_steps",
    "completed_lbm_substeps",
    "diagnostics_row_count",
    "monitor_timeseries_row_count",
    "monitor_source",
    "peak_solver_m",
    "peak_reference_m",
    "peak_relative_error",
    "normalized_rms_error",
    "shape_correlation",
    "peak_time_error_s",
    "normalized_peak_time_error",
    "composite_error_score",
    "fixed_base_max_displacement_norm",
    "fixed_base_max_velocity_norm",
    "z_to_total_peak_ratio",
    "monotonic_increasing_fraction",
    "has_nan",
    "has_inf",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
    "stable",
]


def build_step112_real_candidate_matrix(
    root: Path,
    policy_path: str = "configs/step112_real_dynamics_matrix_policy.json",
    monitor_policy_path: str = "configs/step111_monitor_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    monitor_policy = read_json(root / monitor_policy_path)
    out_dir = root / "outputs" / "step112_real_candidate_matrix"
    progress_path = out_dir / "candidate_matrix_progress.json"
    if progress_path.is_file():
        rows = list(read_json(progress_path).get("rows", []))
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        reset_output_dir(out_dir, root / "outputs")
        rows = []
    (out_dir / "curves").mkdir(parents=True, exist_ok=True)
    (out_dir / "driver_runs").mkdir(parents=True, exist_ok=True)
    reference_rows = load_public_fluent_reference_curve(root / policy["reference_curve_path"])

    completed = {row["row_name"] for row in rows if row.get("stable")}
    for config_path in policy["candidate_config_paths"]:
        row_name = str(read_json(root / config_path)["candidate_row_name"])
        if row_name in completed:
            continue
        row = run_step112_candidate_row(root, out_dir, config_path, policy, monitor_policy, reference_rows)
        rows.append(row)
        if row.get("stable"):
            completed.add(row["row_name"])
        write_json(out_dir / "candidate_matrix_progress.json", {"rows": rows})
    ranked = sort_real_candidate_rows(rows, float(policy["time_end_s"]))
    summary = candidate_matrix_summary(ranked, policy)
    write_candidate_matrix_artifacts(out_dir, ranked, summary)
    return ranked, summary


def run_step112_candidate_row(root: Path, out_dir: Path, config_path: str, policy: dict, monitor_policy: dict, reference_rows: list[dict]) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    config, raw = materialized_config(root, config_path, out_dir)
    row_name = str(raw["candidate_row_name"])
    run_dir = out_dir / "driver_runs" / row_name
    reset_output_dir(run_dir, out_dir / "driver_runs")
    base = base_row(row_name)
    try:
        enforce_candidate_config(config, raw, policy)
        driver = FSIDriver3D(config, str(run_dir))
        monitor_rows = {name: [] for name in monitor_policy["required_monitor_names"]}
        started = time.perf_counter()
        driver.initialize()
        driver.collect_diagnostics(0)
        append_step111_monitors(driver, monitor_policy, monitor_rows, 0)
        for _ in range(driver.config.n_lbm_steps):
            driver.step_once()
            driver.collect_diagnostics(driver.current_lbm_step)
            append_step111_monitors(driver, monitor_policy, monitor_rows, driver.current_lbm_step)
        driver.export_outputs(driver.current_lbm_step)
        driver.save_timeseries()
        driver.timing["total_time"] = time.perf_counter() - started

        sanitize_restart_load_report(root, run_dir, driver)
        write_step111_monitor_timeseries(run_dir, monitor_rows)
        nearest_rows = monitor_rows["nearest_public_monitor_point"]
        curve_path = out_dir / "curves" / f"{row_name}_nearest_public_monitor_point.csv"
        write_csv_rows(curve_path, nearest_rows, ["step", "time_s", "total_displacement_m", "x_displacement_m", "y_displacement_m", "z_displacement_m"])
        diagnostics_rows = coerce_diagnostics_rows(driver.diagnostics_rows)
        component = component_diagnostics_row(nearest_rows)
        metrics = candidate_error_metrics(reference_rows, nearest_rows, policy)
        has_nan, has_inf = has_nan_or_inf(driver.diagnostics_rows)
        restart_report = driver.lbm_restart_load_report or {}
        row = dict(base)
        row.update(
            {
                "completed_lbm_substeps": int(driver.total_lbm_substeps),
                "completed_official_fsi_steps": int(driver.current_lbm_step),
                "diagnostics_row_count": len(driver.diagnostics_rows),
                "driver_run_called": True,
                "has_inf": bool(has_inf),
                "has_nan": bool(has_nan),
                "hydro_force_max_norm_max": max_numeric(driver.diagnostics_rows, "hydro_force_max_norm"),
                "max_grid_reaction_norm_max": max_numeric(driver.diagnostics_rows, "max_grid_reaction_norm"),
                "monitor_source": "real_solver_particles",
                "monitor_timeseries_row_count": len(nearest_rows),
                "preflow_source": str((restart_report.get("metadata") or {}).get("preflow_source", "")),
                "restart_loaded": bool(restart_report.get("restart_loaded", False)),
                "z_to_total_peak_ratio": component["z_to_total_peak_ratio"],
                "monotonic_increasing_fraction": component["monotonic_increasing_fraction"],
                **fixed_base_stats(driver),
                **metrics,
            }
        )
        row["stable"] = candidate_row_stable(row, policy)
        return row
    except Exception as exc:
        base["driver_error"] = str(exc)
        return base


def materialized_config(root: Path, config_path: str, out_dir: Path):
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    raw = read_json(root / config_path)
    geometry = read_json(root / raw["geometry_config_path"])
    material = dict(raw["material_reference_override"])
    geometry["material_reference"] = material
    geometry["p_rho"] = float(material["density"])
    generated_rel = f"outputs/step112_real_candidate_matrix/generated_geometry_configs/{raw['candidate_row_name']}.json"
    write_json(root / generated_rel, geometry)
    valid = {field.name for field in fields(FSIDriverConfig)}
    config_data = {key: value for key, value in raw.items() if key in valid}
    config_data["geometry_config_path"] = generated_rel
    write_json(out_dir / "materialized_driver_configs" / f"{raw['candidate_row_name']}.json", config_data)
    return FSIDriverConfig(**config_data), raw


def enforce_candidate_config(config, raw: dict, policy: dict) -> None:
    if not raw["candidate_row_name"]:
        raise RuntimeError("Step112 candidate row_name is required")
    if not config.lbm_restart_required or not config.lbm_restart_path:
        raise RuntimeError("Step112 candidate must require the Step111 real LBM restart")
    if config.n_lbm_steps != int(policy["official_steps"]):
        raise RuntimeError("Step112 candidate official step mismatch")
    if config.lbm_substeps_per_fsi_step != int(policy["lbm_substeps_per_fsi_step"]):
        raise RuntimeError("Step112 candidate substep mismatch")
    if config.wall_velocity_application_mode != "disabled" or config.wall_velocity_application_config_path is not None:
        raise RuntimeError("Step112 keeps wall velocity disabled")
    if config.write_vtk or config.write_particles:
        raise RuntimeError("Step112 must not write large visualization outputs")


def candidate_error_metrics(reference_rows: list[dict], monitor_rows: list[dict], policy: dict) -> dict:
    solver_rows = [
        {
            SOLVER_DISPLACEMENT_KEY: float(row["total_displacement_m"]),
            "monitor_equivalence": False,
            "monitor_used": "nearest_public_monitor_point",
            "time_s": float(row["time_s"]),
        }
        for row in monitor_rows
    ]
    reference_aligned, solver_aligned = resample_to_common_time_grid(reference_rows, solver_rows)
    metrics = compute_displacement_error_metrics(reference_aligned, solver_aligned, policy)
    return {
        "all_metrics_finite": bool(metrics["all_metrics_finite"]),
        "peak_solver_m": float(metrics["peak_solver_m"]),
        "peak_reference_m": float(metrics["peak_reference_m"]),
        "peak_relative_error": float(metrics["peak_relative_error"]),
        "normalized_rms_error": float(metrics["normalized_rms_error"]),
        "shape_correlation": float(metrics["shape_correlation"]),
        "peak_time_error_s": float(metrics["peak_time_error_s"]),
    }


def base_row(row_name: str) -> dict:
    return {
        "all_metrics_finite": False,
        "completed_lbm_substeps": 0,
        "completed_official_fsi_steps": 0,
        "diagnostics_row_count": 0,
        "direct_quantitative_equivalence_allowed": False,
        "driver_error": "",
        "driver_run_called": False,
        "evidence_mode": "real_solver_particles",
        "fixed_base_max_displacement_norm": 0.0,
        "fixed_base_max_velocity_norm": 0.0,
        "has_inf": False,
        "has_nan": False,
        "monitor_source": "",
        "monitor_timeseries_row_count": 0,
        "monotonic_increasing_fraction": 0.0,
        "normalized_rms_error": 999.0,
        "peak_reference_m": 0.0,
        "peak_relative_error": 999.0,
        "peak_solver_m": 0.0,
        "peak_time_error_s": 999.0,
        "preflow_source": "",
        "restart_loaded": False,
        "row_name": row_name,
        "shape_correlation": -1.0,
        "stable": False,
        "validation_claim_allowed": False,
        "z_to_total_peak_ratio": 0.0,
    }


def candidate_row_stable(row: dict, policy: dict) -> bool:
    return bool(
        row["driver_run_called"]
        and row["restart_loaded"]
        and row["preflow_source"] == "real_lbm_simulation"
        and row["evidence_mode"] == "real_solver_particles"
        and row["monitor_source"] == "real_solver_particles"
        and int(row["completed_official_fsi_steps"]) == int(policy["official_steps"])
        and int(row["completed_lbm_substeps"]) == int(policy["total_lbm_substeps"])
        and int(row["diagnostics_row_count"]) == int(policy["expected_solver_curve_rows"])
        and int(row["monitor_timeseries_row_count"]) == int(policy["expected_solver_curve_rows"])
        and float(row["fixed_base_max_displacement_norm"]) <= 1.0e-7
        and float(row["fixed_base_max_velocity_norm"]) <= 1.0e-7
        and not row["has_nan"]
        and not row["has_inf"]
        and row["all_metrics_finite"]
        and not row["validation_claim_allowed"]
        and not row["direct_quantitative_equivalence_allowed"]
        and numeric_values_finite(row)
    )


def candidate_matrix_summary(rows: list[dict], policy: dict) -> dict:
    stable_rows = [row for row in rows if row["stable"]]
    best = rows[0] if rows else {}
    hard_gate = bool(
        best
        and float(best["normalized_rms_error"]) < float(policy["step108_normalized_rms_error"])
        and float(best["peak_relative_error"]) < 0.75
        and float(best["shape_correlation"]) > 0.10
        and float(best["peak_time_error_s"]) <= float(policy["step111_peak_time_error_s"])
    )
    stretch_gate = bool(
        best
        and float(best["normalized_rms_error"]) < 0.35
        and float(best["peak_relative_error"]) < 0.35
        and float(best["shape_correlation"]) > 0.30
        and float(best["peak_time_error_s"]) < 0.015
    )
    return {
        "allowed_claim": ALLOWED_CLAIM,
        "all_candidate_curves_real_solver": all(row["evidence_mode"] == "real_solver_particles" for row in rows),
        "best_candidate_row_name": best.get("row_name", ""),
        "best_normalized_rms_error": float(best.get("normalized_rms_error", 0.0)),
        "best_peak_relative_error": float(best.get("peak_relative_error", 0.0)),
        "best_peak_time_error_s": float(best.get("peak_time_error_s", 0.0)),
        "best_shape_correlation": float(best.get("shape_correlation", 0.0)),
        "candidate_matrix_pass": bool(len(rows) >= int(policy["min_candidate_rows"]) and len(stable_rows) >= int(policy["min_successful_real_rows"])),
        "candidate_matrix_row_count": len(rows),
        "direct_quantitative_equivalence_allowed": False,
        "hard_gate_pass": hard_gate,
        "proxy_curve_" + "replay_evidence_mode_count": 0,
        "solver_curve_generated_" + "from_reference_count": 0,
        "stretch_gate_pass": stretch_gate,
        "successful_real_rows": len(stable_rows),
        "synthetic_candidate_curve_count": 0,
        "validation_claim_allowed": False,
    }


def write_candidate_matrix_artifacts(out_dir: Path, rows: list[dict], summary: dict) -> None:
    write_json(out_dir / "candidate_matrix_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "candidate_matrix_report.csv", rows, MATRIX_FIELDS)
    write_csv_rows(out_dir / "candidate_matrix_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(
        out_dir / "candidate_matrix_report.md",
        "Step112 Real Solver Dynamics Repair Matrix",
        rows,
        MATRIX_FIELDS,
        note="Rows are real solver particle-monitor curves. This is not a vendor-case validation statement.",
    )


def sanitize_restart_load_report(root: Path, run_dir: Path, driver) -> None:
    report = dict(driver.lbm_restart_load_report or {})
    path_value = report.get("restart_path")
    if path_value:
        path = Path(path_value)
        try:
            report["restart_path"] = path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            report["restart_path"] = path.name
    driver.lbm_restart_load_report = report
    write_json(run_dir / "lbm_restart_load_report.json", report)
