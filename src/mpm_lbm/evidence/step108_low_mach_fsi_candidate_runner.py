from __future__ import annotations

import math
import shutil
from pathlib import Path

from src.mpm_lbm.evidence.step108_common import (
    numeric_values_finite,
    read_csv_rows,
    read_json,
    reset_output_dir,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)


FSI_FIELDS = [
    "row_name",
    "driver_run_called",
    "canonical_driver_module",
    "geometry_type",
    "n_grid",
    "n_particles",
    "completed_official_fsi_steps",
    "completed_lbm_substeps",
    "lbm_substeps_per_fsi_step",
    "official_fsi_dt_s",
    "lbm_dt_phys_s",
    "target_inlet_velocity_mps",
    "target_u_lbm",
    "flap_tip_timeseries_row_count",
    "solver_curve_time_start_s",
    "solver_curve_time_end_s",
    "diagnostics_row_count",
    "fixed_base_particle_count",
    "fixed_base_constraint_applied",
    "fixed_base_max_displacement_norm",
    "fixed_base_max_velocity_norm",
    "step36_squid_wall_velocity_config_used",
    "target_u_lbm_applied_to_solid_initial_velocity",
    "target_u_lbm_applied_to_inlet",
    "has_nan",
    "has_inf",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
    "stable",
]

FLAP_FIELDS = [
    "step",
    "time_s",
    "flap_tip_total_displacement_m",
    "flap_tip_x_displacement_m",
    "flap_tip_y_displacement_m",
]


def build_step108_low_mach_fsi_candidate(
    root: Path,
    run_config_path: str = "configs/step108_fluent_duct_flap_low_mach_subcycling_48_50step_candidate.json",
    policy_path: str = "configs/step108_low_mach_subcycling_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    row = run_step108_low_mach_fsi_case(root, run_config_path, policy)
    rows = [row]
    summary = step108_fsi_summary(rows)
    out_dir = root / "outputs" / "step108_low_mach_fsi_candidate"
    write_step108_fsi_artifacts(out_dir, rows, summary)
    if not summary["step108_low_mach_fsi_candidate_pass"]:
        raise RuntimeError(f"Step108 low-Mach FSI candidate failed: {summary}")
    return rows, summary


def run_step108_low_mach_fsi_case(root: Path, config_path: str, policy: dict) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    config = FSIDriverConfig.from_json(root / config_path)
    row_name = Path(config_path).stem.removeprefix("step108_")
    enforce_step108_fsi_config(config, row_name, policy)

    output_dir = root / "outputs" / "step108_low_mach_fsi_candidate"
    run_root = root / "outputs" / "step108_driver_runs"
    out_dir = run_root / row_name
    reset_output_dir(output_dir, root / "outputs")
    reset_output_dir(out_dir, run_root)

    driver = FSIDriver3D(config, str(out_dir))
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step108 row: {row_name}")

    copy_required_driver_artifacts(out_dir, output_dir)
    curve_rows = normalize_flap_tip_timeseries(
        output_dir / "flap_tip_displacement_timeseries.csv",
        official_dt_s=float(config.official_fsi_dt_s),
    )
    has_nan, has_inf = diagnostics_have_nan_or_inf(diagnostics)
    fixed_stats = driver.solid.get_fixed_particle_stats()
    duct_boundary = read_json(output_dir / "duct_boundary_condition_report.json")
    row = {
        "canonical_driver_module": driver.__class__.__module__,
        "completed_lbm_substeps": int(driver.total_lbm_substeps),
        "completed_official_fsi_steps": int(driver.current_lbm_step),
        "diagnostics_row_count": len(diagnostics),
        "direct_quantitative_equivalence_allowed": False,
        "driver_run_called": True,
        "flap_tip_timeseries_row_count": len(curve_rows),
        "geometry_type": config.geometry_type,
        "has_inf": bool(has_inf),
        "has_nan": bool(has_nan),
        "lbm_dt_phys_s": float(config.lbm_dt_phys_override_s),
        "lbm_substeps_per_fsi_step": int(config.lbm_substeps_per_fsi_step),
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "official_fsi_dt_s": float(config.official_fsi_dt_s),
        "row_name": row_name,
        "solver_curve_time_end_s": float(curve_rows[-1]["time_s"]),
        "solver_curve_time_start_s": float(curve_rows[0]["time_s"]),
        "stable": False,
        "step36_squid_wall_velocity_config_used": step36_wall_velocity_config_used(config),
        "target_inlet_velocity_mps": float(config.target_inlet_velocity_mps),
        "target_u_lbm": list(config.target_u_lbm),
        "target_u_lbm_applied_to_inlet": bool(duct_boundary["target_u_lbm_applied_to_inlet"]),
        "target_u_lbm_applied_to_solid_initial_velocity": bool(
            list(config.target_u_lbm) == list(config.initial_solid_velocity_norm)
            and any(abs(value) > 0.0 for value in config.target_u_lbm)
        ),
        "validation_claim_allowed": False,
        **fixed_stats,
    }
    row["stable"] = step108_fsi_row_pass(row, policy)
    if not row["stable"]:
        raise RuntimeError(f"Step108 low-Mach FSI row failed acceptance: {row}")
    return row


def enforce_step108_fsi_config(config, row_name: str, policy: dict) -> None:
    if row_name != policy["required_candidate_row_name"]:
        raise RuntimeError("Step108 FSI row name mismatch")
    expected = {
        "geometry_config_path": policy["geometry_config_path"],
        "lbm_boundary_condition_mode": policy["required_lbm_boundary_condition_mode"],
        "lbm_dt_phys_override_s": float(policy["lbm_dt_phys_s"]),
        "lbm_substeps_per_fsi_step": int(policy["lbm_substeps_per_fsi_step"]),
        "n_grid": int(policy["n_grid"]),
        "n_lbm_steps": int(policy["official_steps"]),
        "official_fsi_dt_s": float(policy["official_fsi_dt_s"]),
        "physical_duct_length_m": float(policy["physical_duct_length_m"]),
        "target_inlet_velocity_mps": float(policy["target_inlet_velocity_mps"]),
        "target_u_lbm_for_dimensional_mapping": float(policy["target_u_lbm"]),
    }
    actual = {
        "geometry_config_path": config.geometry_config_path,
        "lbm_boundary_condition_mode": config.lbm_boundary_condition_mode,
        "lbm_dt_phys_override_s": config.lbm_dt_phys_override_s,
        "lbm_substeps_per_fsi_step": config.lbm_substeps_per_fsi_step,
        "n_grid": config.n_grid,
        "n_lbm_steps": config.n_lbm_steps,
        "official_fsi_dt_s": config.official_fsi_dt_s,
        "physical_duct_length_m": config.physical_duct_length_m,
        "target_inlet_velocity_mps": config.target_inlet_velocity_mps,
        "target_u_lbm_for_dimensional_mapping": config.target_u_lbm_for_dimensional_mapping,
    }
    for key, expected_value in expected.items():
        actual_value = actual[key]
        if isinstance(expected_value, float):
            if abs(float(actual_value) - expected_value) > 1.0e-15:
                raise RuntimeError(f"Step108 FSI config mismatch for {key}: {actual_value} != {expected_value}")
        elif actual_value != expected_value:
            raise RuntimeError(f"Step108 FSI config mismatch for {key}: {actual_value} != {expected_value}")
    if list(config.target_u_lbm) != list(policy["target_u_lbm_vector"]):
        raise RuntimeError("Step108 FSI target_u_lbm mismatch")
    if config.fsi_exchange_mode != "lbm_subcycled_per_fsi_step":
        raise RuntimeError("Step108 FSI must enable lbm_subcycled_per_fsi_step")
    if config.wall_velocity_application_mode != "disabled" or config.wall_velocity_application_config_path is not None:
        raise RuntimeError("Step108 FSI must keep Step36 wall velocity disabled")
    if config.coupling_mode != "moving_boundary" or config.reaction_transfer_mode != "engineering":
        raise RuntimeError("Step108 FSI must preserve moving_boundary engineering transfer")
    if config.write_vtk or config.write_particles:
        raise RuntimeError("Step108 FSI must not write VTK or particle arrays")


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


def step108_fsi_row_pass(row: dict, policy: dict) -> bool:
    return bool(
        row["driver_run_called"]
        and row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
        and row["row_name"] == policy["required_candidate_row_name"]
        and int(row["completed_official_fsi_steps"]) == int(policy["official_steps"])
        and int(row["completed_lbm_substeps"]) == int(policy["total_lbm_substeps"])
        and int(row["flap_tip_timeseries_row_count"]) == int(policy["expected_solver_curve_rows"])
        and math.isclose(float(row["solver_curve_time_start_s"]), 0.0, rel_tol=0.0, abs_tol=1.0e-15)
        and math.isclose(float(row["solver_curve_time_end_s"]), float(policy["time_end_s"]), rel_tol=0.0, abs_tol=1.0e-15)
        and row["target_u_lbm_applied_to_inlet"]
        and not row["target_u_lbm_applied_to_solid_initial_velocity"]
        and int(row["fixed_base_particle_count"]) > 0
        and row["fixed_base_constraint_applied"]
        and float(row["fixed_base_max_displacement_norm"]) <= 1.0e-7
        and float(row["fixed_base_max_velocity_norm"]) <= 1.0e-7
        and not row["step36_squid_wall_velocity_config_used"]
        and not row["has_nan"]
        and not row["has_inf"]
        and not row["direct_quantitative_equivalence_allowed"]
        and not row["validation_claim_allowed"]
        and numeric_values_finite(row)
    )


def step108_fsi_summary(rows: list[dict]) -> dict:
    summary = {
        "direct_quantitative_equivalence_allowed": False,
        "has_inf_count": sum(1 for row in rows if row["has_inf"]),
        "has_nan_count": sum(1 for row in rows if row["has_nan"]),
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if row["stable"]),
        "step108_low_mach_fsi_candidate_pass": False,
        "validation_claim_allowed": False,
    }
    summary["step108_low_mach_fsi_candidate_pass"] = bool(
        rows
        and summary["stable_count"] == summary["row_count"]
        and summary["has_nan_count"] == 0
        and summary["has_inf_count"] == 0
        and not summary["direct_quantitative_equivalence_allowed"]
        and not summary["validation_claim_allowed"]
    )
    return summary


def write_step108_fsi_artifacts(out_dir: Path, rows: list[dict], summary: dict) -> None:
    write_json(out_dir / "low_mach_fsi_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "low_mach_fsi_report.csv", rows, FSI_FIELDS)
    write_csv_rows(out_dir / "low_mach_fsi_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(
        out_dir / "low_mach_fsi_report.md",
        "Step108 Low-Mach FSI Candidate Report",
        rows,
        FSI_FIELDS,
        note="This is an official-speed low-Mach proxy smoke, not Fluent validation.",
    )


def copy_required_driver_artifacts(out_dir: Path, output_dir: Path) -> None:
    for name in (
        "diagnostics_timeseries.csv",
        "duct_boundary_condition_report.json",
        "duct_static_geometry_report.json",
        "flap_tip_displacement_timeseries.csv",
    ):
        source = out_dir / name
        if not source.is_file():
            raise RuntimeError(f"missing Step108 driver artifact: {source}")
        shutil.copy2(source, output_dir / name)


def diagnostics_have_nan_or_inf(diagnostics: list[dict]) -> tuple[bool, bool]:
    has_nan = False
    has_inf = False
    for row in diagnostics:
        for value in row.values():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            if math.isnan(float(value)):
                has_nan = True
            if math.isinf(float(value)):
                has_inf = True
    return has_nan, has_inf


def step36_wall_velocity_config_used(config) -> bool:
    value = config.wall_velocity_application_config_path
    return bool(value and "step36_wall_velocity_application_solid_vel_experimental" in value)
