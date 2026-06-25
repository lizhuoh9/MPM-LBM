from __future__ import annotations

import time
from dataclasses import fields
from pathlib import Path

from src.mpm_lbm.evidence.step109_response_sensitivity_matrix_runner import normalize_flap_tip_timeseries
from src.mpm_lbm.evidence.step111_common import (
    ALLOWED_CLAIM,
    has_nan_or_inf,
    max_numeric,
    numeric_values_finite,
    read_csv_rows,
    read_json,
    reset_output_dir,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)
from src.mpm_lbm.evidence.step111_real_monitor_extraction import (
    append_step111_monitors,
    build_step111_monitor_report,
    fixed_base_stats,
    write_step111_monitor_timeseries,
)


SOLVER_FIELDS = [
    "row_name",
    "driver_run_called",
    "canonical_driver_module",
    "preflow_source",
    "restart_loaded",
    "completed_official_fsi_steps",
    "completed_lbm_substeps",
    "diagnostics_row_count",
    "flap_tip_timeseries_row_count",
    "nearest_monitor_timeseries_row_count",
    "solver_curve_time_end_s",
    "peak_nearest_monitor_m",
    "hydro_force_max_norm_max",
    "max_grid_reaction_norm_max",
    "fixed_base_particle_count",
    "fixed_base_constraint_applied",
    "fixed_base_max_displacement_norm",
    "fixed_base_max_velocity_norm",
    "step36_squid_wall_velocity_config_used",
    "has_nan",
    "has_inf",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
    "stable",
]


def build_step111_real_solver_candidate(
    root: Path,
    run_config_path: str = "configs/step111_real_solver_candidate_cap_2e-2_E_2e4_48_50step.json",
    monitor_policy_path: str = "configs/step111_monitor_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    monitor_policy = read_json(root / monitor_policy_path)
    output_dir = root / "outputs" / "step111_real_solver_candidate"
    run_dir = root / "outputs" / "step111_driver_runs" / "cap_2e-2_E_2e4"
    reset_output_dir(output_dir, root / "outputs")
    reset_output_dir(run_dir, root / "outputs" / "step111_driver_runs")
    config, raw_config = materialized_config(root, run_config_path, output_dir)
    enforce_solver_config(config, raw_config)

    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

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
    copy_driver_file(run_dir, output_dir, "diagnostics_timeseries.csv")
    copy_driver_file(run_dir, output_dir, "flap_tip_displacement_timeseries.csv")
    copy_driver_file(run_dir, output_dir, "lbm_restart_load_report.json")
    copy_driver_file(run_dir, output_dir, "duct_boundary_condition_report.json")
    curve_rows = normalize_flap_tip_timeseries(output_dir / "flap_tip_displacement_timeseries.csv", float(config.official_fsi_dt_s))
    write_step111_monitor_timeseries(output_dir, monitor_rows)
    build_step111_monitor_report(root)

    has_nan, has_inf = has_nan_or_inf(driver.diagnostics_rows)
    nearest_rows = monitor_rows["nearest_public_monitor_point"]
    restart_report = driver.lbm_restart_load_report or {}
    preflow_source = str((restart_report.get("metadata") or {}).get("preflow_source", ""))
    row = {
        "canonical_driver_module": driver.__class__.__module__,
        "completed_lbm_substeps": int(driver.total_lbm_substeps),
        "completed_official_fsi_steps": int(driver.current_lbm_step),
        "diagnostics_row_count": len(driver.diagnostics_rows),
        "direct_quantitative_equivalence_allowed": False,
        "driver_run_called": True,
        "flap_tip_timeseries_row_count": len(curve_rows),
        "has_inf": bool(has_inf),
        "has_nan": bool(has_nan),
        "hydro_force_max_norm_max": max_numeric(driver.diagnostics_rows, "hydro_force_max_norm"),
        "max_grid_reaction_norm_max": max_numeric(driver.diagnostics_rows, "max_grid_reaction_norm"),
        "nearest_monitor_timeseries_row_count": len(nearest_rows),
        "peak_nearest_monitor_m": max(abs(float(row["total_displacement_m"])) for row in nearest_rows),
        "preflow_source": preflow_source,
        "restart_loaded": bool(restart_report.get("restart_loaded", False)),
        "row_name": str(raw_config["candidate_row_name"]),
        "solver_curve_time_end_s": float(nearest_rows[-1]["time_s"]),
        "stable": False,
        "step36_squid_wall_velocity_config_used": bool(config.wall_velocity_application_config_path),
        "validation_claim_allowed": False,
        **fixed_base_stats(driver),
    }
    row["stable"] = solver_row_pass(row, config)
    rows = [row]
    summary = {
        "allowed_claim": ALLOWED_CLAIM,
        "direct_quantitative_equivalence_allowed": False,
        "real_solver_candidate_pass": bool(row["stable"]),
        "row_count": 1,
        "validation_claim_allowed": False,
    }
    write_solver_artifacts(output_dir, rows, summary)
    if not summary["real_solver_candidate_pass"]:
        raise RuntimeError(f"Step111 real solver candidate failed: {summary}")
    return rows, summary


def materialized_config(root: Path, run_config_path: str, output_dir: Path):
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    raw = read_json(root / run_config_path)
    geometry = read_json(root / raw["geometry_config_path"])
    material = dict(raw["material_reference_override"])
    geometry["material_reference"] = material
    geometry["p_rho"] = float(material["density"])
    generated_rel = "outputs/step111_real_solver_candidate/generated_geometry_step111_cap_2e-2_E_2e4.json"
    write_json(root / generated_rel, geometry)
    valid = {field.name for field in fields(FSIDriverConfig)}
    config_data = {key: value for key, value in raw.items() if key in valid}
    config_data["geometry_config_path"] = generated_rel
    write_json(output_dir / "materialized_driver_config.json", config_data)
    return FSIDriverConfig(**config_data), raw


def enforce_solver_config(config, raw: dict) -> None:
    if raw["candidate_row_name"] != "cap_2e-2_E_2e4":
        raise RuntimeError("Step111 must materialize the Step110-selected candidate")
    if config.mb_force_cap_norm != 0.02:
        raise RuntimeError("Step111 candidate force cap mismatch")
    if config.n_lbm_steps != 50 or config.lbm_substeps_per_fsi_step != 120:
        raise RuntimeError("Step111 candidate time window mismatch")
    if not config.lbm_restart_required or not config.lbm_restart_path:
        raise RuntimeError("Step111 candidate must require the real LBM preflow restart")
    if config.wall_velocity_application_mode != "disabled" or config.wall_velocity_application_config_path is not None:
        raise RuntimeError("Step111 keeps wall velocity disabled")
    if config.write_vtk or config.write_particles:
        raise RuntimeError("Step111 must not write large visualization outputs")


def solver_row_pass(row: dict, config) -> bool:
    return bool(
        row["driver_run_called"]
        and row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
        and row["restart_loaded"]
        and row["preflow_source"] == "real_lbm_simulation"
        and int(row["completed_official_fsi_steps"]) == int(config.n_lbm_steps)
        and int(row["completed_lbm_substeps"]) == int(config.n_lbm_steps * config.lbm_substeps_per_fsi_step)
        and int(row["diagnostics_row_count"]) == 51
        and int(row["flap_tip_timeseries_row_count"]) == 51
        and int(row["nearest_monitor_timeseries_row_count"]) == 51
        and float(row["fixed_base_max_displacement_norm"]) <= 1.0e-7
        and float(row["fixed_base_max_velocity_norm"]) <= 1.0e-7
        and not row["step36_squid_wall_velocity_config_used"]
        and not row["has_nan"]
        and not row["has_inf"]
        and not row["validation_claim_allowed"]
        and not row["direct_quantitative_equivalence_allowed"]
        and numeric_values_finite(row)
    )


def copy_driver_file(run_dir: Path, output_dir: Path, name: str) -> None:
    source = run_dir / name
    if not source.is_file():
        raise RuntimeError(f"missing Step111 driver artifact: {name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / name).write_bytes(source.read_bytes())


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


def write_solver_artifacts(out_dir: Path, rows: list[dict], summary: dict) -> None:
    write_json(out_dir / "real_solver_candidate_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "real_solver_candidate_report.csv", rows, SOLVER_FIELDS)
    write_csv_rows(out_dir / "real_solver_candidate_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(
        out_dir / "real_solver_candidate_report.md",
        "Step111 Real Solver Candidate",
        rows,
        SOLVER_FIELDS,
        note="This is a real solver run over the public tutorial time window and is not a vendor-case parity statement.",
    )
