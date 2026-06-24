from __future__ import annotations

import math
import shutil
import time
from pathlib import Path

from src.mpm_lbm.evidence.step104_common import (
    ALLOWED_CLAIM,
    STEP104_ROW_NAME,
    read_json,
    rel_path,
    write_csv_rows,
    write_json,
    write_markdown_table,
)
from src.mpm_lbm.evidence.step104_fluent_duct_flap_setup_gap_report import (
    step104_capability_gap_count,
    step104_gap_fields,
)


REPORT_FIELDS = [
    "row_name",
    "driver_run_called",
    "canonical_driver_module",
    "geometry_type",
    "n_grid",
    "n_particles",
    "n_lbm_steps",
    "completed_lbm_steps",
    "diagnostics_row_count",
    "target_u_lbm_applied_to_solid_initial_velocity",
    "target_u_lbm_applied_to_inlet",
    "lbm_boundary_condition_mode",
    "all_fluid_geometry_used",
    "fixed_base_particle_count",
    "fixed_base_constraint_applied",
    "material_reference_used_for_mpm_config",
    "step36_squid_wall_velocity_config_used",
    "proxy_flap_tip_displacement_available",
    "direct_quantitative_equivalence_allowed",
    "validation_claim_allowed",
    "stable",
]


def build_step104_fluent_duct_flap_setup_repair(
    root: Path,
    run_config_path: str = "configs/step104_fluent_duct_flap_setup_repair_48_5step_smoke.json",
    acceptance_policy_path: str = "configs/step104_acceptance_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / acceptance_policy_path)
    row = run_step104_fluent_duct_flap_setup_repair_case(root, run_config_path, policy)
    rows = [row]
    summary = step104_setup_summary(rows, policy)
    return rows, summary


def run_step104_fluent_duct_flap_setup_repair_case(root: Path, config_path: str, policy: dict) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D
    from src.mpm_lbm.sim.geometry.config import GeometryConfig
    from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D

    row_name = row_name_from_config(config_path)
    config = FSIDriverConfig.from_json(root / config_path)
    enforce_step104_config(root, config, row_name, policy)
    geometry_config = GeometryConfig.from_json(str(root / config.geometry_config_path))
    sampling_cloud = GeometrySampler3D(geometry_config).sample_particles()
    sampling_stats = sampling_cloud["sampling_stats"]

    output_dir = root / "outputs" / "step104_fluent_duct_flap_setup_repair"
    run_root = root / "outputs" / "step104_driver_runs"
    out_dir = run_root / row_name
    reset_output_dir(output_dir, root / "outputs")
    reset_output_dir(out_dir, run_root)

    driver = FSIDriver3D(config, str(out_dir))
    started = time.perf_counter()
    diagnostics = driver.run()
    elapsed_seconds = time.perf_counter() - started
    write_json(out_dir / "driver_timing.json", driver.performance_row())
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step104 row: {row_name}")

    copy_required_driver_artifacts(out_dir, output_dir)
    final = diagnostics[-1]
    has_nan, has_inf = diagnostics_have_nan_or_inf(diagnostics)
    fixed_stats = driver.solid.get_fixed_particle_stats()
    duct_boundary = read_json(output_dir / "duct_boundary_condition_report.json")
    duct_geometry = read_json(output_dir / "duct_static_geometry_report.json")
    gap_fields = step104_gap_fields()
    mpm_config = driver.solid.config

    row = {
        "allowed_claim": ALLOWED_CLAIM,
        "all_fluid_geometry_used": bool(duct_geometry["all_fluid_geometry_used"]),
        "canonical_driver_module": driver.__class__.__module__,
        "capability_gap_count": step104_capability_gap_count(gap_fields),
        "completed_lbm_steps": int(driver.current_lbm_step),
        "coupling_mode": config.coupling_mode,
        "diagnostics_csv_exists": (out_dir / "diagnostics_timeseries.csv").is_file(),
        "diagnostics_npz_exists": (out_dir / "diagnostics_timeseries.npz").is_file(),
        "diagnostics_row_count": len(diagnostics),
        "driver_run_called": True,
        "elapsed_seconds": elapsed_seconds,
        "flap_tip_timeseries_exists": (output_dir / "flap_tip_displacement_timeseries.csv").is_file(),
        "flap_tip_timeseries_row_count": len(driver.flap_tip_monitor_rows),
        "fluid_cell_count": int(duct_geometry["fluid_cell_count"]),
        "geo_path_name": Path(driver.geo_path).name,
        "geometry_config_path": config.geometry_config_path,
        "geometry_config_path_exists": (root / config.geometry_config_path).is_file(),
        "geometry_type": config.geometry_type,
        "has_inf": bool(has_inf),
        "has_nan": bool(has_nan),
        "initial_solid_velocity_norm": list(config.initial_solid_velocity_norm),
        "lbm_boundary_condition_mode": config.lbm_boundary_condition_mode,
        "mpm_p_rho": float(mpm_config.p_rho),
        "mpm_poisson_ratio": float(mpm_config.poisson_ratio),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "mpm_young_modulus": float(mpm_config.young_modulus),
        "n_grid": int(config.n_grid),
        "n_lbm_steps": int(config.n_lbm_steps),
        "n_particles": int(config.n_particles),
        "pressure_outlet_cell_count": int(duct_boundary["pressure_outlet_cell_count"]),
        "projected_mass_final": float(final["projected_mass"]),
        "proxy_flap_tip_displacement_available": bool(gap_fields["proxy_flap_tip_displacement_available"]),
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "rho_max_max": max_float(diagnostics, "rho_max"),
        "rho_min_min": min_float(diagnostics, "rho_min"),
        "row_name": row_name,
        "sampling_fixed_base_particle_count": int(sampling_stats["fixed_base_particle_count"]),
        "sampling_free_tip_proxy_particle_count": int(sampling_stats["free_tip_proxy_particle_count"]),
        "sampling_particle_count": int(sampling_stats["particle_count"]),
        "solid_cell_count": int(duct_geometry["solid_cell_count"]),
        "stable": False,
        "step36_squid_wall_velocity_config_used": step36_wall_velocity_config_used(config),
        "target_u_lbm": list(config.target_u_lbm),
        "target_u_lbm_applied_to_inlet": bool(duct_boundary["target_u_lbm_applied_to_inlet"]),
        "target_u_lbm_applied_to_solid_initial_velocity": bool(
            list(config.target_u_lbm) == list(config.initial_solid_velocity_norm)
            and any(abs(value) > 0.0 for value in config.target_u_lbm)
        ),
        "total_mpm_substeps": int(driver.total_mpm_substeps),
        "validation_claim_allowed": bool(gap_fields["validation_claim_allowed"]),
        "velocity_inlet_cell_count": int(duct_boundary["velocity_inlet_cell_count"]),
        "vtr_output_count": count_files_by_suffix((out_dir, output_dir), ".vtr"),
        "write_particles": bool(config.write_particles),
        "write_vtk": bool(config.write_vtk),
        **fixed_stats,
        **gap_fields,
    }
    row["material_reference_used_for_mpm_config"] = bool(driver.material_reference_used_for_mpm_config)
    row["stable"] = step104_row_pass(row, policy)
    if not row["stable"]:
        raise RuntimeError(f"Step104 setup repair row failed acceptance: {row}")
    return row


def write_step104_setup_repair_artifacts(root: Path, rows: list[dict], summary: dict) -> None:
    output_dir = root / "outputs" / "step104_fluent_duct_flap_setup_repair"
    write_json(output_dir / "setup_repair_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(output_dir / "setup_repair_report.csv", rows, REPORT_FIELDS)
    write_csv_rows(output_dir / "setup_repair_summary.csv", [{"metric": k, "value": v} for k, v in sorted(summary.items())], ["metric", "value"])
    write_markdown_table(output_dir / "setup_repair_report.md", "Step104 Setup Repair Report", rows, REPORT_FIELDS)


def enforce_step104_config(root: Path, config, row_name: str, policy: dict) -> None:
    if row_name not in set(policy["required_row_names"]):
        raise RuntimeError(f"unexpected Step104 row: {row_name}")
    expected = {
        "n_grid": int(policy["required_n_grid"]),
        "n_particles": int(policy["required_n_particles"]),
        "n_lbm_steps": int(policy["required_n_lbm_steps"]),
        "mpm_substeps_per_lbm_step": int(policy["mpm_substeps_per_lbm_step"]),
    }
    actual = {
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
    }
    if actual != expected:
        raise RuntimeError(f"Step104 config mismatch: {actual} != {expected}")
    if config.geometry_type != policy["required_geometry_type"]:
        raise RuntimeError("Step104 must use duct_flap_proxy geometry")
    if config.geometry_config_path != policy["required_geometry_config_path"]:
        raise RuntimeError("Step104 must use the required duct-flap geometry config")
    if list(config.target_u_lbm) != list(policy["required_target_u_lbm"]):
        raise RuntimeError("Step104 target_u_lbm mismatch")
    if list(config.initial_solid_velocity_norm) != list(policy["required_initial_solid_velocity_norm"]):
        raise RuntimeError("Step104 initial_solid_velocity_norm mismatch")
    if config.lbm_boundary_condition_mode != policy["required_lbm_boundary_condition_mode"]:
        raise RuntimeError("Step104 must use explicit duct inlet/outlet LBM boundary mode")
    if config.wall_velocity_application_mode != "disabled" or config.wall_velocity_application_config_path is not None:
        raise RuntimeError("Step104 must disable Step36 squid wall velocity")
    if config.coupling_mode != "moving_boundary" or config.reaction_transfer_mode != "engineering":
        raise RuntimeError("Step104 must use moving_boundary with engineering reaction transfer")
    if config.write_vtk or config.write_particles:
        raise RuntimeError("Step104 must not write VTK or particle arrays")
    if not (root / config.geometry_config_path).is_file():
        raise RuntimeError(f"Step104 geometry config is not resolvable: {config.geometry_config_path}")


def step104_row_pass(row: dict, policy: dict) -> bool:
    return bool(
        row["driver_run_called"]
        and row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
        and row["row_name"] in set(policy["required_row_names"])
        and int(row["n_grid"]) == int(policy["required_n_grid"])
        and int(row["n_particles"]) == int(policy["required_n_particles"])
        and int(row["n_lbm_steps"]) == int(policy["required_n_lbm_steps"])
        and int(row["completed_lbm_steps"]) == int(row["n_lbm_steps"])
        and int(row["diagnostics_row_count"]) >= int(policy["min_diagnostics_row_count"])
        and row["geometry_type"] == policy["required_geometry_type"]
        and row["lbm_boundary_condition_mode"] == policy["required_lbm_boundary_condition_mode"]
        and row["geo_path_name"] == f"geo_duct_flap_proxy_{int(row['n_grid'])}.dat"
        and not row["target_u_lbm_applied_to_solid_initial_velocity"]
        and row["target_u_lbm_applied_to_inlet"]
        and not row["all_fluid_geometry_used"]
        and int(row["velocity_inlet_cell_count"]) > 0
        and int(row["pressure_outlet_cell_count"]) > 0
        and int(row["solid_cell_count"]) > 0
        and int(row["fixed_base_particle_count"]) > 0
        and row["fixed_base_constraint_applied"]
        and float(row["fixed_base_max_displacement_norm"]) <= 1.0e-7
        and float(row["fixed_base_max_velocity_norm"]) <= 1.0e-7
        and row["material_reference_used_for_mpm_config"]
        and float(row["mpm_p_rho"]) == 1600.0
        and float(row["mpm_young_modulus"]) == 1000000.0
        and float(row["mpm_poisson_ratio"]) == 0.47
        and not row["step36_squid_wall_velocity_config_used"]
        and row["proxy_flap_tip_displacement_available"]
        and row["flap_tip_timeseries_exists"]
        and int(row["flap_tip_timeseries_row_count"]) >= int(policy["min_diagnostics_row_count"])
        and not row["direct_quantitative_equivalence_allowed"]
        and not row["validation_claim_allowed"]
        and not row["has_nan"]
        and not row["has_inf"]
        and not row["write_vtk"]
        and not row["write_particles"]
        and int(row["vtr_output_count"]) == 0
        and not row["elapsed_seconds"] > float(policy["runtime_hard_fail_seconds"])
        and numeric_values_finite(row)
    )


def step104_setup_summary(rows: list[dict], policy: dict) -> dict:
    required_names = set(policy["required_row_names"])
    row_names = {row["row_name"] for row in rows}
    summary = {
        "all_fluid_geometry_used_count": sum(1 for row in rows if row["all_fluid_geometry_used"]),
        "driver_run_called_count": sum(1 for row in rows if row["driver_run_called"]),
        "fixed_base_constraint_applied_count": sum(1 for row in rows if row["fixed_base_constraint_applied"]),
        "has_inf_count": sum(1 for row in rows if row["has_inf"]),
        "has_nan_count": sum(1 for row in rows if row["has_nan"]),
        "material_reference_used_for_mpm_config_count": sum(1 for row in rows if row["material_reference_used_for_mpm_config"]),
        "missing_required_rows": sorted(required_names - row_names),
        "proxy_flap_tip_displacement_available_count": sum(1 for row in rows if row["proxy_flap_tip_displacement_available"]),
        "required_row_count": len(required_names),
        "required_stable_count": sum(1 for row in rows if row["row_name"] in required_names and row["stable"]),
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if row["stable"]),
        "step104_setup_repair_pass": False,
        "target_u_lbm_applied_to_inlet_count": sum(1 for row in rows if row["target_u_lbm_applied_to_inlet"]),
        "target_u_lbm_applied_to_solid_initial_velocity_count": sum(
            1 for row in rows if row["target_u_lbm_applied_to_solid_initial_velocity"]
        ),
        "total_elapsed_seconds": sum(float(row["elapsed_seconds"]) for row in rows),
    }
    summary["step104_setup_repair_pass"] = bool(
        summary["missing_required_rows"] == []
        and summary["required_stable_count"] == summary["required_row_count"]
        and summary["stable_count"] == summary["row_count"]
        and summary["driver_run_called_count"] == 1
        and summary["target_u_lbm_applied_to_inlet_count"] == 1
        and summary["target_u_lbm_applied_to_solid_initial_velocity_count"] == 0
        and summary["all_fluid_geometry_used_count"] == 0
        and summary["fixed_base_constraint_applied_count"] == 1
        and summary["material_reference_used_for_mpm_config_count"] == 1
        and summary["proxy_flap_tip_displacement_available_count"] == 1
        and summary["has_nan_count"] == 0
        and summary["has_inf_count"] == 0
    )
    return summary


def copy_required_driver_artifacts(out_dir: Path, output_dir: Path) -> None:
    for name in (
        "duct_boundary_condition_report.json",
        "duct_static_geometry_report.json",
        "flap_tip_displacement_timeseries.csv",
    ):
        source = out_dir / name
        if not source.is_file():
            raise RuntimeError(f"missing Step104 driver artifact: {source}")
        shutil.copy2(source, output_dir / name)


def reset_output_dir(out_dir: Path, required_parent: Path) -> None:
    resolved_out = out_dir.resolve()
    resolved_parent = required_parent.resolve()
    if resolved_out == resolved_parent or resolved_parent not in resolved_out.parents:
        raise RuntimeError(f"refusing to reset unexpected Step104 output directory: {out_dir}")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)


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


def count_files_by_suffix(roots, suffix: str) -> int:
    count = 0
    for root in roots:
        root = Path(root)
        if not root.exists():
            continue
        count += sum(1 for path in root.rglob("*") if path.is_file() and path.suffix.lower() == suffix)
    return count


def max_float(rows: list[dict], key: str) -> float:
    return max(float(row[key]) for row in rows)


def min_float(rows: list[dict], key: str) -> float:
    return min(float(row[key]) for row in rows)


def numeric_values_finite(row: dict) -> bool:
    for value in row.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            return False
    return True


def row_name_from_config(config_path: str) -> str:
    return Path(config_path).stem.removeprefix("step104_")


def step36_wall_velocity_config_used(config) -> bool:
    value = config.wall_velocity_application_config_path
    return bool(value and "step36_wall_velocity_application_solid_vel_experimental" in value)
