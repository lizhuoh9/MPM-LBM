from __future__ import annotations

from dataclasses import fields
import math
import os
from pathlib import Path
import shutil
import time

import numpy as np

from src.mpm_lbm.evidence.step109_common import (
    ALLOWED_CLAIM,
    has_nan_or_inf,
    max_numeric,
    numeric_values_finite,
    read_csv_rows,
    read_json,
    reset_output_dir,
    safe_ratio,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)
from src.mpm_lbm.evidence.step109_error_comparison import evaluate_solver_curve_against_step107_public_reference


MATRIX_FIELDS = [
    "row_name",
    "matrix_family",
    "source_config_path",
    "geometry_config_path",
    "n_grid",
    "n_particles",
    "completed_official_fsi_steps",
    "completed_lbm_substeps",
    "lbm_substeps_per_fsi_step",
    "official_fsi_dt_s",
    "lbm_dt_phys_s",
    "target_inlet_velocity_mps",
    "target_u_lbm_x",
    "mb_force_cap_norm",
    "mb_reaction_scale",
    "youngs_modulus",
    "density",
    "flap_tip_timeseries_row_count",
    "solver_curve_time_start_s",
    "solver_curve_time_end_s",
    "diagnostics_row_count",
    "hydro_force_max_norm_max",
    "max_grid_reaction_norm_max",
    "max_grid_reaction_to_cap_ratio",
    "active_reaction_particle_count_final",
    "peak_reference_m",
    "peak_solver_m",
    "peak_ratio",
    "peak_relative_error",
    "normalized_rms_error",
    "shape_correlation",
    "peak_time_error_s",
    "all_metrics_finite",
    "has_nan",
    "has_inf",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
    "stable",
    "driver_error",
]

FLAP_FIELDS = [
    "step",
    "time_s",
    "flap_tip_total_displacement_m",
    "flap_tip_x_displacement_m",
    "flap_tip_y_displacement_m",
]

MONITOR_FIELDS = [
    "step",
    "time_s",
    "total_displacement_m",
    "x_displacement_m",
    "y_displacement_m",
    "z_displacement_m",
]

STEP109_EXTRA_CONFIG_KEYS = {"row_name", "matrix_family", "material_reference_override"}


def build_step109_response_sensitivity_matrix(
    root: Path,
    policy_path: str = "configs/step109_response_matrix_policy.json",
    monitor_policy_path: str = "configs/step109_monitor_sensitivity_policy.json",
) -> tuple[list[dict], dict]:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    root = Path(root)
    previous_cwd = Path.cwd()
    os.chdir(root)
    try:
        policy = read_json(root / policy_path)
        monitor_policy = read_json(root / monitor_policy_path)
        output_dir = root / "outputs" / "step109_response_sensitivity_matrix"
        run_root = root / "outputs" / "step109_driver_runs"
        reset_output_dir(output_dir, root / "outputs")
        run_root.mkdir(parents=True, exist_ok=True)

        config_fields = {field.name for field in fields(FSIDriverConfig)}
        rows = []
        for config_path in policy["response_matrix_configs"]:
            raw_config = read_json(root / config_path)
            row_name = str(raw_config["row_name"])
            row = run_step109_response_matrix_row(
                root=root,
                output_dir=output_dir,
                run_root=run_root,
                config_path=config_path,
                raw_config=raw_config,
                policy=policy,
                monitor_policy=monitor_policy,
                config_fields=config_fields,
            )
            rows.append(row)
            write_json(output_dir / "response_matrix_progress.json", {"rows": rows})

        for _ in range(3):
            summary = step109_response_matrix_summary(rows, policy)
            if not summary["best_candidate_row_name"]:
                break
            updated = ensure_best_monitor_timeseries(
                root=root,
                output_dir=output_dir,
                run_root=run_root,
                rows=rows,
                policy=policy,
                monitor_policy=monitor_policy,
                config_fields=config_fields,
            )
            if not updated:
                break
            rows = updated
        summary = step109_response_matrix_summary(rows, policy)
        write_step109_response_matrix_artifacts(output_dir, rows, summary)
        if not summary["response_matrix_pass"]:
            raise RuntimeError(f"Step109 response sensitivity matrix failed: {summary}")
        return rows, summary
    finally:
        os.chdir(previous_cwd)


def run_step109_response_matrix_row(
    root: Path,
    output_dir: Path,
    run_root: Path,
    config_path: str,
    raw_config: dict,
    policy: dict,
    monitor_policy: dict,
    config_fields: set[str],
) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    row_name = str(raw_config["row_name"])
    row_output_dir = run_root / row_name
    row_output_dir.mkdir(parents=True, exist_ok=True)
    material = material_reference_for_row(root, output_dir, row_name, raw_config)
    config_data = {key: value for key, value in raw_config.items() if key in config_fields}
    if material["generated_geometry_config_path"]:
        config_data["geometry_config_path"] = material["generated_geometry_config_path"]
    config = FSIDriverConfig(**config_data)
    row = base_row(row_name, config_path, raw_config, config, material)

    try:
        enforce_step109_row_config(config, policy)
        if completed_driver_outputs_available(row_output_dir, policy):
            return build_row_from_existing_driver_output(
                root=root,
                output_dir=output_dir,
                row_output_dir=row_output_dir,
                row=row,
                config=config,
                policy=policy,
            )
        reset_output_dir(row_output_dir, run_root)
        driver = FSIDriver3D(config, str(row_output_dir))
        diagnostics, monitor_timeseries = run_driver_with_step109_monitors(driver, monitor_policy)
        if not diagnostics:
            raise RuntimeError("empty diagnostics")

        curve_rows = normalize_flap_tip_timeseries(
            row_output_dir / "flap_tip_displacement_timeseries.csv",
            official_dt_s=float(config.official_fsi_dt_s),
        )
        has_nan, has_inf = has_nan_or_inf(diagnostics)
        metrics = evaluate_solver_curve_against_step107_public_reference(
            root,
            row_output_dir / "flap_tip_displacement_timeseries.csv",
            monitor_name="free_tip_proxy_mean",
            policy=policy,
        )
        curve_copy = output_dir / "curves" / f"flap_tip_displacement_timeseries_{row_name}.csv"
        curve_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(row_output_dir / "flap_tip_displacement_timeseries.csv", curve_copy)
        write_monitor_timeseries(output_dir, row_name, monitor_timeseries)

        row.update(metric_fields(metrics))
        row.update(
            {
                "active_reaction_particle_count_final": int(diagnostics[-1]["active_reaction_particle_count"]),
                "completed_lbm_substeps": int(driver.total_lbm_substeps),
                "completed_official_fsi_steps": int(driver.current_lbm_step),
                "diagnostics_row_count": len(diagnostics),
                "driver_error": "",
                "flap_tip_timeseries_row_count": len(curve_rows),
                "has_inf": bool(has_inf),
                "has_nan": bool(has_nan),
                "hydro_force_max_norm_max": max_numeric(diagnostics, "hydro_force_max_norm"),
                "max_grid_reaction_norm_max": max_numeric(diagnostics, "max_grid_reaction_norm"),
                "solver_curve_time_end_s": float(curve_rows[-1]["time_s"]),
                "solver_curve_time_start_s": float(curve_rows[0]["time_s"]),
            }
        )
        row["max_grid_reaction_to_cap_ratio"] = safe_ratio(
            row["max_grid_reaction_norm_max"],
            row["mb_force_cap_norm"],
        )
        row["peak_ratio"] = safe_ratio(abs(row["peak_solver_m"]), abs(row["peak_reference_m"]))
        row["stable"] = step109_row_pass(row, policy)
        return row
    except Exception as exc:
        row["driver_error"] = str(exc)
        row["stable"] = False
        return row


def completed_driver_outputs_available(row_output_dir: Path, policy: dict) -> bool:
    curve_path = row_output_dir / "flap_tip_displacement_timeseries.csv"
    diagnostics_path = row_output_dir / "diagnostics_timeseries.csv"
    if not curve_path.is_file() or not diagnostics_path.is_file():
        return False
    try:
        curve_rows = read_csv_rows(curve_path)
        diagnostics = read_csv_rows(diagnostics_path)
    except Exception:
        return False
    if len(curve_rows) != int(policy["expected_solver_curve_rows"]) or len(diagnostics) != int(policy["expected_solver_curve_rows"]):
        return False
    return (
        math.isclose(float(curve_rows[0]["time_s"]), 0.0, rel_tol=0.0, abs_tol=1.0e-15)
        and math.isclose(float(curve_rows[-1]["time_s"]), float(policy["time_end_s"]), rel_tol=0.0, abs_tol=1.0e-15)
        and int(float(diagnostics[-1]["step"])) == int(policy["official_steps"])
    )


def build_row_from_existing_driver_output(
    root: Path,
    output_dir: Path,
    row_output_dir: Path,
    row: dict,
    config,
    policy: dict,
) -> dict:
    diagnostics = coerce_numeric_diagnostics(read_csv_rows(row_output_dir / "diagnostics_timeseries.csv"))
    curve_rows = normalize_flap_tip_timeseries(
        row_output_dir / "flap_tip_displacement_timeseries.csv",
        official_dt_s=float(config.official_fsi_dt_s),
    )
    has_nan, has_inf = has_nan_or_inf(diagnostics)
    metrics = evaluate_solver_curve_against_step107_public_reference(
        root,
        row_output_dir / "flap_tip_displacement_timeseries.csv",
        monitor_name="free_tip_proxy_mean",
        policy=policy,
    )
    curve_copy = output_dir / "curves" / f"flap_tip_displacement_timeseries_{row['row_name']}.csv"
    curve_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(row_output_dir / "flap_tip_displacement_timeseries.csv", curve_copy)
    row.update(metric_fields(metrics))
    row.update(
        {
            "active_reaction_particle_count_final": int(diagnostics[-1]["active_reaction_particle_count"]),
            "completed_lbm_substeps": int(policy["total_lbm_substeps"]),
            "completed_official_fsi_steps": int(diagnostics[-1]["step"]),
            "diagnostics_row_count": len(diagnostics),
            "driver_error": "",
            "flap_tip_timeseries_row_count": len(curve_rows),
            "has_inf": bool(has_inf),
            "has_nan": bool(has_nan),
            "hydro_force_max_norm_max": max_numeric(diagnostics, "hydro_force_max_norm"),
            "max_grid_reaction_norm_max": max_numeric(diagnostics, "max_grid_reaction_norm"),
            "solver_curve_time_end_s": float(curve_rows[-1]["time_s"]),
            "solver_curve_time_start_s": float(curve_rows[0]["time_s"]),
        }
    )
    row["max_grid_reaction_to_cap_ratio"] = safe_ratio(row["max_grid_reaction_norm_max"], row["mb_force_cap_norm"])
    row["peak_ratio"] = safe_ratio(abs(row["peak_solver_m"]), abs(row["peak_reference_m"]))
    row["stable"] = step109_row_pass(row, policy)
    return row


def coerce_numeric_diagnostics(rows: list[dict]) -> list[dict]:
    numeric = []
    for row in rows:
        converted = {}
        for key, value in row.items():
            if key == "coupling_mode":
                converted[key] = value
            elif key in {"step", "total_mpm_substeps", "active_cell_count", "bb_link_count", "active_reaction_particle_count"}:
                converted[key] = int(float(value))
            else:
                converted[key] = float(value)
        numeric.append(converted)
    return numeric


def ensure_best_monitor_timeseries(
    root: Path,
    output_dir: Path,
    run_root: Path,
    rows: list[dict],
    policy: dict,
    monitor_policy: dict,
    config_fields: set[str],
) -> list[dict] | None:
    best = max((row for row in rows if row["stable"]), key=lambda row: abs(float(row["peak_solver_m"])), default=None)
    if best is None:
        return None
    missing = [
        name
        for name in monitor_policy["required_monitor_names"]
        if not (output_dir / "monitor_timeseries" / f"{best['row_name']}__{name}.csv").is_file()
    ]
    if not missing:
        return None
    raw_config = read_json(root / best["source_config_path"])
    reset_output_dir(run_root / best["row_name"], run_root)
    updated_best = run_step109_response_matrix_row(
        root=root,
        output_dir=output_dir,
        run_root=run_root,
        config_path=best["source_config_path"],
        raw_config=raw_config,
        policy=policy,
        monitor_policy=monitor_policy,
        config_fields=config_fields,
    )
    return [updated_best if row["row_name"] == best["row_name"] else row for row in rows]


def run_driver_with_step109_monitors(driver, monitor_policy: dict) -> tuple[list[dict], dict[str, list[dict]]]:
    total_start = time.perf_counter()
    if not driver.initialized:
        driver.initialize()

    monitor_rows = {name: [] for name in monitor_policy["required_monitor_names"]}
    driver.collect_diagnostics(0)
    append_step109_monitors(driver, monitor_policy, monitor_rows, step=0)
    for _ in range(driver.config.n_lbm_steps):
        driver.step_once()
        should_record = (
            driver.current_lbm_step % driver.config.output_interval == 0
            or driver.current_lbm_step == driver.config.n_lbm_steps
        )
        if should_record:
            driver.collect_diagnostics(driver.current_lbm_step)
            append_step109_monitors(driver, monitor_policy, monitor_rows, step=driver.current_lbm_step)

    driver.export_outputs(driver.current_lbm_step)
    driver.save_timeseries()
    driver.timing["total_time"] = time.perf_counter() - total_start
    return driver.diagnostics_rows, monitor_rows


def append_step109_monitors(driver, monitor_policy: dict, monitor_rows: dict[str, list[dict]], step: int) -> None:
    rows = compute_step109_monitor_rows(driver, monitor_policy, step)
    for name, row in rows.items():
        monitor_rows[name].append(row)


def compute_step109_monitor_rows(driver, monitor_policy: dict, step: int) -> dict[str, dict]:
    if driver.initial_particle_positions is None or driver.free_tip_proxy_mask is None:
        raise RuntimeError("Step109 monitor capture requires duct-flap sampled particles")
    initial = np.asarray(driver.initial_particle_positions, dtype=np.float64)
    current = np.asarray(driver.solid.x.to_numpy(), dtype=np.float64)
    displacement_m = (current - initial) * float(driver._duct_length_scale_m())
    free_mask = np.asarray(driver.free_tip_proxy_mask, dtype=bool)
    if not np.any(free_mask):
        raise RuntimeError("Step109 monitor capture requires a non-empty free-tip proxy mask")

    target = public_monitor_normalized_position(driver, monitor_policy)
    distances = np.linalg.norm(initial - target, axis=1)
    nearest_index = int(np.argmin(distances))
    top_count = min(5, len(distances))
    top_indices = np.argsort(distances)[:top_count]
    free_displacements = displacement_m[free_mask]
    max_free_index = int(np.argmax(np.linalg.norm(free_displacements, axis=1)))
    time_s = float(step) * float(driver.config.official_fsi_dt_s)
    return {
        "free_tip_proxy_mean": monitor_row(step, time_s, np.mean(free_displacements, axis=0)),
        "free_tip_proxy_max_total_displacement": monitor_row(step, time_s, free_displacements[max_free_index]),
        "nearest_public_monitor_point": monitor_row(step, time_s, displacement_m[nearest_index]),
        "top_5_nearest_public_monitor_mean": monitor_row(step, time_s, np.mean(displacement_m[top_indices], axis=0)),
    }


def public_monitor_normalized_position(driver, monitor_policy: dict) -> np.ndarray:
    geometry_config = driver._make_geometry_config()
    duct = geometry_config.duct or {}
    duct_x = [float(value) for value in duct.get("x", [0.0, 1.0])]
    duct_y = [float(value) for value in duct.get("y", [0.0, 1.0])]
    duct_z = [float(value) for value in duct.get("z", [0.0, 1.0])]
    x_norm = duct_x[0] + safe_ratio(float(monitor_policy["public_monitor_x_m"]), float(monitor_policy["duct_length_m"])) * (
        duct_x[1] - duct_x[0]
    )
    y_norm = duct_y[0] + safe_ratio(float(monitor_policy["public_monitor_y_m"]), float(monitor_policy["duct_height_m"])) * (
        duct_y[1] - duct_y[0]
    )
    z_norm = 0.5 * (duct_z[0] + duct_z[1])
    return np.asarray([x_norm, y_norm, z_norm], dtype=np.float64)


def monitor_row(step: int, time_s: float, displacement: np.ndarray) -> dict:
    vector = np.asarray(displacement, dtype=np.float64)
    return {
        "step": int(step),
        "time_s": float(time_s),
        "total_displacement_m": float(np.linalg.norm(vector)),
        "x_displacement_m": float(vector[0]),
        "y_displacement_m": float(vector[1]),
        "z_displacement_m": float(vector[2]),
    }


def write_monitor_timeseries(output_dir: Path, row_name: str, monitor_timeseries: dict[str, list[dict]]) -> None:
    for monitor_name, rows in monitor_timeseries.items():
        write_csv_rows(
            output_dir / "monitor_timeseries" / f"{row_name}__{monitor_name}.csv",
            rows,
            MONITOR_FIELDS,
        )


def material_reference_for_row(root: Path, output_dir: Path, row_name: str, raw_config: dict) -> dict:
    geometry_config_path = str(raw_config["geometry_config_path"])
    geometry = read_json(root / geometry_config_path)
    material = dict(geometry.get("material_reference") or {})
    generated_path = ""
    if raw_config.get("material_reference_override"):
        material = dict(raw_config["material_reference_override"])
        geometry["material_reference"] = material
        if "density" in material:
            geometry["p_rho"] = float(material["density"])
        rel_path = f"outputs/step109_response_sensitivity_matrix/generated_geometry_configs/step109_geometry_{row_name}.json"
        write_json(root / rel_path, geometry)
        generated_path = rel_path
    return {
        "density": float(material.get("density", geometry.get("p_rho", 0.0))),
        "generated_geometry_config_path": generated_path,
        "poisson_ratio": float(material.get("poisson_ratio", 0.0)),
        "youngs_modulus": float(material.get("youngs_modulus", 0.0)),
    }


def base_row(row_name: str, config_path: str, raw_config: dict, config, material: dict) -> dict:
    return {
        "active_reaction_particle_count_final": 0,
        "all_metrics_finite": False,
        "completed_lbm_substeps": 0,
        "completed_official_fsi_steps": 0,
        "density": material["density"],
        "diagnostics_row_count": 0,
        "direct_quantitative_equivalence_allowed": False,
        "driver_error": "",
        "flap_tip_timeseries_row_count": 0,
        "geometry_config_path": material["generated_geometry_config_path"] or str(raw_config["geometry_config_path"]),
        "has_inf": False,
        "has_nan": False,
        "hydro_force_max_norm_max": 0.0,
        "lbm_dt_phys_s": float(config.lbm_dt_phys_override_s),
        "lbm_substeps_per_fsi_step": int(config.lbm_substeps_per_fsi_step),
        "matrix_family": str(raw_config["matrix_family"]),
        "max_grid_reaction_norm_max": 0.0,
        "max_grid_reaction_to_cap_ratio": 0.0,
        "mb_force_cap_norm": float(config.mb_force_cap_norm),
        "mb_reaction_scale": float(config.mb_reaction_scale),
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "normalized_rms_error": 0.0,
        "official_fsi_dt_s": float(config.official_fsi_dt_s),
        "peak_ratio": 0.0,
        "peak_reference_m": 0.0,
        "peak_relative_error": 0.0,
        "peak_solver_m": 0.0,
        "peak_time_error_s": 0.0,
        "row_name": row_name,
        "shape_correlation": 0.0,
        "solver_curve_time_end_s": 0.0,
        "solver_curve_time_start_s": 0.0,
        "source_config_path": config_path,
        "stable": False,
        "target_inlet_velocity_mps": float(config.target_inlet_velocity_mps),
        "target_u_lbm_x": float(config.target_u_lbm[0]),
        "validation_claim_allowed": False,
        "youngs_modulus": material["youngs_modulus"],
    }


def metric_fields(metrics: dict) -> dict:
    keys = [
        "all_metrics_finite",
        "direct_quantitative_equivalence_allowed",
        "normalized_rms_error",
        "peak_reference_m",
        "peak_relative_error",
        "peak_solver_m",
        "peak_time_error_s",
        "shape_correlation",
        "solver_curve_time_end_s",
        "solver_curve_time_start_s",
        "validation_claim_allowed",
    ]
    return {key: metrics[key] for key in keys}


def enforce_step109_row_config(config, policy: dict) -> None:
    expected = {
        "fsi_exchange_mode": "lbm_subcycled_per_fsi_step",
        "lbm_dt_phys_override_s": float(policy["lbm_dt_phys_s"]),
        "lbm_substeps_per_fsi_step": int(policy["lbm_substeps_per_fsi_step"]),
        "n_lbm_steps": int(policy["official_steps"]),
        "official_fsi_dt_s": float(policy["official_fsi_dt_s"]),
    }
    actual = {key: getattr(config, key) for key in expected}
    for key, expected_value in expected.items():
        actual_value = actual[key]
        if isinstance(expected_value, float):
            if not math.isclose(float(actual_value), expected_value, rel_tol=0.0, abs_tol=1.0e-15):
                raise RuntimeError(f"Step109 config mismatch for {key}: {actual_value} != {expected_value}")
        elif actual_value != expected_value:
            raise RuntimeError(f"Step109 config mismatch for {key}: {actual_value} != {expected_value}")
    if list(config.target_u_lbm) != list(policy["target_u_lbm"]):
        raise RuntimeError("Step109 target_u_lbm mismatch")
    if config.wall_velocity_application_mode != "disabled" or config.wall_velocity_application_config_path is not None:
        raise RuntimeError("Step109 must keep wall velocity disabled")
    if config.coupling_mode != "moving_boundary" or config.reaction_transfer_mode != "engineering":
        raise RuntimeError("Step109 must preserve moving_boundary engineering transfer")
    if config.write_vtk or config.write_particles:
        raise RuntimeError("Step109 must not write VTK or particle arrays")


def normalize_flap_tip_timeseries(path: Path, official_dt_s: float) -> list[dict]:
    rows = read_csv_rows(path)
    normalized = []
    for index, row in enumerate(rows):
        normalized.append(
            {
                "flap_tip_total_displacement_m": float(row["flap_tip_total_displacement_m"]),
                "flap_tip_x_displacement_m": float(row["flap_tip_x_displacement_m"]),
                "flap_tip_y_displacement_m": float(row["flap_tip_y_displacement_m"]),
                "step": int(row["step"]),
                "time_s": float(index) * float(official_dt_s),
            }
        )
    write_csv_rows(path, normalized, FLAP_FIELDS)
    return normalized


def step109_row_pass(row: dict, policy: dict) -> bool:
    return bool(
        int(row["completed_official_fsi_steps"]) == int(policy["official_steps"])
        and int(row["completed_lbm_substeps"]) == int(policy["total_lbm_substeps"])
        and int(row["flap_tip_timeseries_row_count"]) == int(policy["expected_solver_curve_rows"])
        and math.isclose(float(row["solver_curve_time_start_s"]), 0.0, rel_tol=0.0, abs_tol=1.0e-15)
        and math.isclose(float(row["solver_curve_time_end_s"]), float(policy["time_end_s"]), rel_tol=0.0, abs_tol=1.0e-15)
        and not row["has_nan"]
        and not row["has_inf"]
        and row["all_metrics_finite"]
        and not row["validation_claim_allowed"]
        and not row["direct_quantitative_equivalence_allowed"]
        and numeric_values_finite(row)
    )


def step109_response_matrix_summary(rows: list[dict], policy: dict) -> dict:
    stable_rows = [row for row in rows if row["stable"]]
    best = max(stable_rows, key=lambda row: abs(float(row["peak_solver_m"])), default=None)
    best_peak = float(best["peak_solver_m"]) if best else 0.0
    summary = {
        "allowed_claim": ALLOWED_CLAIM,
        "best_candidate_direct_quantitative_equivalence_allowed": False,
        "best_candidate_row_name": best["row_name"] if best else "",
        "best_candidate_selected": best is not None,
        "best_candidate_validation_claim_allowed": False,
        "best_peak_solver_m": best_peak,
        "direct_quantitative_equivalence_allowed": False,
        "response_matrix_pass": False,
        "response_matrix_row_count": len(rows),
        "rows_above_min_peak_count": sum(1 for row in stable_rows if abs(float(row["peak_solver_m"])) > float(policy["min_peak_solver_m"])),
        "rows_above_step108_peak_count": sum(1 for row in stable_rows if abs(float(row["peak_solver_m"])) > float(policy["step108_peak_solver_m"])),
        "step108_peak_solver_m": float(policy["step108_peak_solver_m"]),
        "successful_response_matrix_rows": len(stable_rows),
        "validation_claim_allowed": False,
    }
    summary["response_matrix_pass"] = bool(
        len(rows) >= len(policy["required_cap_scale_rows"])
        and len(stable_rows) >= int(policy["min_successful_rows"])
        and best is not None
        and abs(best_peak) > float(policy["step108_peak_solver_m"])
        and abs(best_peak) > float(policy["min_peak_solver_m"])
        and all(not row["validation_claim_allowed"] for row in stable_rows)
        and all(not row["direct_quantitative_equivalence_allowed"] for row in stable_rows)
        and all(row["all_metrics_finite"] for row in stable_rows)
    )
    return summary


def write_step109_response_matrix_artifacts(output_dir: Path, rows: list[dict], summary: dict) -> None:
    write_json(output_dir / "response_matrix_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(output_dir / "response_matrix_report.csv", rows, MATRIX_FIELDS)
    write_csv_rows(output_dir / "response_matrix_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(
        output_dir / "response_matrix_report.md",
        "Step109 Response-Amplitude Sensitivity Matrix",
        rows,
        MATRIX_FIELDS,
        note=(
            "This matrix compares proxy response amplitudes against the Step107 public plot digitization. "
            "It does not assert monitor equivalence or official Fluent parity."
        ),
    )
    stable_rows = [row for row in rows if row["stable"]]
    best = max(stable_rows, key=lambda row: abs(float(row["peak_solver_m"])), default={})
    write_json(output_dir / "best_candidate_error_report.json", {"summary": summary, "row": best})
    if best:
        source = output_dir / "curves" / f"flap_tip_displacement_timeseries_{best['row_name']}.csv"
        shutil.copy2(source, output_dir / "best_candidate_flap_tip_displacement_timeseries.csv")
