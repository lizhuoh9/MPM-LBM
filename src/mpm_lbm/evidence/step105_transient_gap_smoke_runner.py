from __future__ import annotations

import math
import shutil
import time
from pathlib import Path

import numpy as np

from src.mpm_lbm.evidence.step105_common import (
    ALLOWED_CLAIM,
    STEP105_ROW_NAME,
    read_json,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)
from src.mpm_lbm.evidence.step105_gap_taxonomy import build_step105_gap_taxonomy


TRANSIENT_FIELDS = [
    "row_name",
    "driver_run_called",
    "canonical_driver_module",
    "geometry_type",
    "n_grid",
    "n_particles",
    "n_lbm_steps",
    "completed_lbm_steps",
    "diagnostics_row_count",
    "flap_tip_timeseries_row_count",
    "target_u_lbm_applied_to_solid_initial_velocity",
    "target_u_lbm_applied_to_inlet",
    "lbm_boundary_condition_mode",
    "all_fluid_geometry_used",
    "fixed_base_particle_count",
    "fixed_base_constraint_applied",
    "fixed_base_max_displacement_norm",
    "fixed_base_max_velocity_norm",
    "step36_squid_wall_velocity_config_used",
    "direct_quantitative_equivalence_allowed",
    "validation_claim_allowed",
    "has_nan",
    "has_inf",
    "stable",
]

FLOW_FIELDS = [
    "row_name",
    "inlet_plane_mean_ux",
    "inlet_plane_max_ux",
    "mid_duct_plane_mean_ux",
    "mid_duct_plane_max_ux",
    "outlet_plane_mean_ux",
    "outlet_plane_max_ux",
    "final_fluid_mean_ux",
    "final_far_field_fluid_mean_ux",
    "inlet_plane_flow_present",
    "mid_duct_plane_flow_present",
    "outlet_plane_flow_present",
    "flow_development_not_fluent_equivalent",
    "direct_quantitative_equivalence_allowed",
    "validation_claim_allowed",
]


def build_step105_transient_gap_smoke(
    root: Path,
    run_config_path: str = "configs/step105_fluent_duct_flap_proxy_48_50step_transient_gap_smoke.json",
    acceptance_policy_path: str = "configs/step105_acceptance_policy.json",
) -> tuple[list[dict], dict, list[dict], dict]:
    root = Path(root)
    policy = read_json(root / acceptance_policy_path)
    row, flow_row = run_step105_transient_gap_smoke_case(root, run_config_path, policy)
    rows = [row]
    flow_rows = [flow_row]
    summary = step105_transient_summary(rows, policy)
    flow_summary = step105_flow_summary(flow_rows)
    return rows, summary, flow_rows, flow_summary


def run_step105_transient_gap_smoke_case(root: Path, config_path: str, policy: dict) -> tuple[dict, dict]:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    row_name = row_name_from_config(config_path)
    config = FSIDriverConfig.from_json(root / config_path)
    enforce_step105_config(root, config, row_name, policy)

    output_dir = root / "outputs" / "step105_transient_gap_smoke"
    flow_dir = root / "outputs" / "step105_flow_development"
    run_root = root / "outputs" / "step105_driver_runs"
    out_dir = run_root / row_name
    reset_output_dir(output_dir, root / "outputs")
    reset_output_dir(flow_dir, root / "outputs")
    reset_output_dir(out_dir, run_root)

    driver = FSIDriver3D(config, str(out_dir))
    started = time.perf_counter()
    diagnostics = driver.run()
    elapsed_seconds = time.perf_counter() - started
    write_json(out_dir / "driver_timing.json", driver.performance_row())
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step105 row: {row_name}")

    copy_required_driver_artifacts(out_dir, output_dir)
    has_nan, has_inf = diagnostics_have_nan_or_inf(diagnostics)
    fixed_stats = driver.solid.get_fixed_particle_stats()
    duct_boundary = read_json(output_dir / "duct_boundary_condition_report.json")
    duct_geometry = read_json(output_dir / "duct_static_geometry_report.json")
    gap_rows, gap_summary = build_step105_gap_taxonomy(root)

    row = {
        "allowed_claim": ALLOWED_CLAIM,
        "all_fluid_geometry_used": bool(duct_geometry["all_fluid_geometry_used"]),
        "canonical_driver_module": driver.__class__.__module__,
        "completed_lbm_steps": int(driver.current_lbm_step),
        "diagnostics_csv_exists": (out_dir / "diagnostics_timeseries.csv").is_file(),
        "diagnostics_npz_exists": (out_dir / "diagnostics_timeseries.npz").is_file(),
        "diagnostics_row_count": len(diagnostics),
        "direct_quantitative_equivalence_allowed": False,
        "driver_run_called": True,
        "elapsed_seconds": elapsed_seconds,
        "flap_tip_timeseries_exists": (output_dir / "flap_tip_displacement_timeseries.csv").is_file(),
        "flap_tip_timeseries_row_count": len(driver.flap_tip_monitor_rows),
        "fluid_cell_count": int(duct_geometry["fluid_cell_count"]),
        "geo_path_name": Path(driver.geo_path).name,
        "geometry_config_path": config.geometry_config_path,
        "geometry_type": config.geometry_type,
        "gap_count": int(gap_summary["gap_count"]),
        "has_inf": bool(has_inf),
        "has_nan": bool(has_nan),
        "initial_solid_velocity_norm": list(config.initial_solid_velocity_norm),
        "lbm_boundary_condition_mode": config.lbm_boundary_condition_mode,
        "n_grid": int(config.n_grid),
        "n_lbm_steps": int(config.n_lbm_steps),
        "n_particles": int(config.n_particles),
        "pressure_outlet_cell_count": int(duct_boundary["pressure_outlet_cell_count"]),
        "row_name": row_name,
        "stable": False,
        "step36_squid_wall_velocity_config_used": step36_wall_velocity_config_used(config),
        "target_u_lbm": list(config.target_u_lbm),
        "target_u_lbm_applied_to_inlet": bool(duct_boundary["target_u_lbm_applied_to_inlet"]),
        "target_u_lbm_applied_to_solid_initial_velocity": bool(
            list(config.target_u_lbm) == list(config.initial_solid_velocity_norm)
            and any(abs(value) > 0.0 for value in config.target_u_lbm)
        ),
        "validation_claim_allowed": False,
        "velocity_inlet_cell_count": int(duct_boundary["velocity_inlet_cell_count"]),
        "vtr_output_count": count_files_by_suffix((out_dir, output_dir), ".vtr"),
        "write_particles": bool(config.write_particles),
        "write_vtk": bool(config.write_vtk),
        **fixed_stats,
    }
    row["stable"] = step105_row_pass(row, policy)
    if not row["stable"]:
        raise RuntimeError(f"Step105 transient row failed acceptance: {row}")

    flow_row = build_flow_development_row(row_name, driver, diagnostics[-1], policy)
    return row, flow_row


def build_flow_development_row(row_name: str, driver, final_diagnostic: dict, policy: dict) -> dict:
    velocity = driver.lbm.v.to_numpy()
    solid = driver.lbm.solid.to_numpy()
    n_grid = int(driver.config.n_grid)
    eps = float(policy["flow_present_epsilon"])
    inlet = plane_ux_stats(velocity, solid, 0)
    mid = plane_ux_stats(velocity, solid, n_grid // 2)
    outlet = plane_ux_stats(velocity, solid, n_grid - 1)
    return {
        "direct_quantitative_equivalence_allowed": False,
        "final_far_field_fluid_mean_ux": float(final_diagnostic["far_field_fluid_mean_ux"]),
        "final_fluid_mean_ux": float(final_diagnostic["fluid_mean_ux"]),
        "flow_development_not_fluent_equivalent": True,
        "inlet_plane_flow_present": bool(abs(inlet["max_ux"]) > eps or abs(inlet["mean_ux"]) > eps),
        "inlet_plane_max_ux": inlet["max_ux"],
        "inlet_plane_mean_ux": inlet["mean_ux"],
        "inlet_plane_fluid_cell_count": inlet["fluid_cell_count"],
        "mid_duct_plane_flow_present": bool(abs(mid["max_ux"]) > eps or abs(mid["mean_ux"]) > eps),
        "mid_duct_plane_max_ux": mid["max_ux"],
        "mid_duct_plane_mean_ux": mid["mean_ux"],
        "mid_duct_plane_fluid_cell_count": mid["fluid_cell_count"],
        "outlet_plane_flow_present": bool(abs(outlet["max_ux"]) > eps or abs(outlet["mean_ux"]) > eps),
        "outlet_plane_max_ux": outlet["max_ux"],
        "outlet_plane_mean_ux": outlet["mean_ux"],
        "outlet_plane_fluid_cell_count": outlet["fluid_cell_count"],
        "row_name": row_name,
        "validation_claim_allowed": False,
    }


def plane_ux_stats(velocity: np.ndarray, solid: np.ndarray, x_index: int) -> dict:
    ux = velocity[x_index, :, :, 0]
    fluid = solid[x_index, :, :] == 0
    if not np.any(fluid):
        return {"fluid_cell_count": 0, "max_ux": 0.0, "mean_ux": 0.0}
    values = ux[fluid]
    return {
        "fluid_cell_count": int(np.count_nonzero(fluid)),
        "max_ux": float(np.max(values)),
        "mean_ux": float(np.mean(values)),
    }


def write_step105_transient_artifacts(root: Path, rows: list[dict], summary: dict) -> None:
    out_dir = Path(root) / "outputs" / "step105_transient_gap_smoke"
    write_json(out_dir / "transient_gap_smoke_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "transient_gap_smoke_report.csv", rows, TRANSIENT_FIELDS)
    write_csv_rows(out_dir / "transient_gap_smoke_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(out_dir / "transient_gap_smoke_report.md", "Step105 Transient Gap Smoke Report", rows, TRANSIENT_FIELDS)


def write_step105_flow_development_artifacts(root: Path, rows: list[dict], summary: dict) -> None:
    out_dir = Path(root) / "outputs" / "step105_flow_development"
    write_json(out_dir / "flow_development_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "flow_development_report.csv", rows, FLOW_FIELDS)
    write_csv_rows(out_dir / "flow_development_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(out_dir / "flow_development_report.md", "Step105 Flow Development Report", rows, FLOW_FIELDS)


def validate_step105_flow_development(root: Path) -> tuple[list[dict], dict]:
    payload = read_json(Path(root) / "outputs" / "step105_flow_development" / "flow_development_report.json")
    rows = payload["rows"]
    summary = step105_flow_summary(rows)
    if not summary["flow_development_report_pass"]:
        raise RuntimeError(f"Step105 flow development report failed: {summary}")
    write_step105_flow_development_artifacts(root, rows, summary)
    return rows, summary


def step105_flow_summary(rows: list[dict]) -> dict:
    summary = {
        "direct_quantitative_equivalence_allowed": False,
        "flow_development_report_pass": False,
        "inlet_plane_flow_present_count": sum(1 for row in rows if row["inlet_plane_flow_present"]),
        "row_count": len(rows),
        "validation_claim_allowed": False,
    }
    summary["flow_development_report_pass"] = bool(
        rows
        and summary["inlet_plane_flow_present_count"] == len(rows)
        and all(row["flow_development_not_fluent_equivalent"] for row in rows)
        and all(not row["direct_quantitative_equivalence_allowed"] for row in rows)
        and all(not row["validation_claim_allowed"] for row in rows)
        and all(flow_row_finite(row) for row in rows)
    )
    return summary


def enforce_step105_config(root: Path, config, row_name: str, policy: dict) -> None:
    if row_name not in set(policy["required_row_names"]):
        raise RuntimeError(f"unexpected Step105 row: {row_name}")
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
        raise RuntimeError(f"Step105 config mismatch: {actual} != {expected}")
    if config.geometry_type != policy["required_geometry_type"]:
        raise RuntimeError("Step105 must use duct_flap_proxy geometry")
    if config.geometry_config_path != policy["required_geometry_config_path"]:
        raise RuntimeError("Step105 must use the Step104 repaired duct-flap geometry config")
    if list(config.target_u_lbm) != list(policy["required_target_u_lbm"]):
        raise RuntimeError("Step105 target_u_lbm mismatch")
    if list(config.initial_solid_velocity_norm) != list(policy["required_initial_solid_velocity_norm"]):
        raise RuntimeError("Step105 initial_solid_velocity_norm mismatch")
    if config.lbm_boundary_condition_mode != policy["required_lbm_boundary_condition_mode"]:
        raise RuntimeError("Step105 must use explicit duct inlet/outlet LBM boundary mode")
    if config.wall_velocity_application_mode != "disabled" or config.wall_velocity_application_config_path is not None:
        raise RuntimeError("Step105 must disable Step36 squid wall velocity")
    if config.coupling_mode != "moving_boundary" or config.reaction_transfer_mode != "engineering":
        raise RuntimeError("Step105 must use moving_boundary with engineering reaction transfer")
    if config.write_vtk or config.write_particles:
        raise RuntimeError("Step105 must not write VTK or particle arrays")
    if not (root / config.geometry_config_path).is_file():
        raise RuntimeError(f"Step105 geometry config is not resolvable: {config.geometry_config_path}")


def step105_row_pass(row: dict, policy: dict) -> bool:
    return bool(
        row["driver_run_called"]
        and row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
        and row["row_name"] in set(policy["required_row_names"])
        and int(row["completed_lbm_steps"]) == int(policy["required_n_lbm_steps"])
        and int(row["diagnostics_row_count"]) >= int(policy["min_diagnostics_row_count"])
        and int(row["flap_tip_timeseries_row_count"]) >= int(policy["min_diagnostics_row_count"])
        and row["target_u_lbm_applied_to_inlet"]
        and not row["target_u_lbm_applied_to_solid_initial_velocity"]
        and not row["all_fluid_geometry_used"]
        and int(row["velocity_inlet_cell_count"]) > 0
        and int(row["pressure_outlet_cell_count"]) > 0
        and int(row["fixed_base_particle_count"]) > 0
        and row["fixed_base_constraint_applied"]
        and float(row["fixed_base_max_displacement_norm"]) <= 1.0e-7
        and float(row["fixed_base_max_velocity_norm"]) <= 1.0e-7
        and not row["step36_squid_wall_velocity_config_used"]
        and not row["direct_quantitative_equivalence_allowed"]
        and not row["validation_claim_allowed"]
        and int(row["gap_count"]) >= 8
        and not row["has_nan"]
        and not row["has_inf"]
        and not row["write_vtk"]
        and not row["write_particles"]
        and int(row["vtr_output_count"]) == 0
        and not row["elapsed_seconds"] > float(policy["runtime_hard_fail_seconds"])
        and numeric_values_finite(row)
    )


def step105_transient_summary(rows: list[dict], policy: dict) -> dict:
    required_names = set(policy["required_row_names"])
    row_names = {row["row_name"] for row in rows}
    summary = {
        "all_fluid_geometry_used_count": sum(1 for row in rows if row["all_fluid_geometry_used"]),
        "driver_run_called_count": sum(1 for row in rows if row["driver_run_called"]),
        "fixed_base_constraint_applied_count": sum(1 for row in rows if row["fixed_base_constraint_applied"]),
        "has_inf_count": sum(1 for row in rows if row["has_inf"]),
        "has_nan_count": sum(1 for row in rows if row["has_nan"]),
        "missing_required_rows": sorted(required_names - row_names),
        "required_row_count": len(required_names),
        "required_stable_count": sum(1 for row in rows if row["row_name"] in required_names and row["stable"]),
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if row["stable"]),
        "step105_transient_gap_smoke_pass": False,
        "target_u_lbm_applied_to_inlet_count": sum(1 for row in rows if row["target_u_lbm_applied_to_inlet"]),
        "target_u_lbm_applied_to_solid_initial_velocity_count": sum(
            1 for row in rows if row["target_u_lbm_applied_to_solid_initial_velocity"]
        ),
        "total_elapsed_seconds": sum(float(row["elapsed_seconds"]) for row in rows),
    }
    summary["step105_transient_gap_smoke_pass"] = bool(
        summary["missing_required_rows"] == []
        and summary["required_stable_count"] == summary["required_row_count"]
        and summary["stable_count"] == summary["row_count"]
        and summary["driver_run_called_count"] == 1
        and summary["target_u_lbm_applied_to_inlet_count"] == 1
        and summary["target_u_lbm_applied_to_solid_initial_velocity_count"] == 0
        and summary["all_fluid_geometry_used_count"] == 0
        and summary["fixed_base_constraint_applied_count"] == 1
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
            raise RuntimeError(f"missing Step105 driver artifact: {source}")
        shutil.copy2(source, output_dir / name)


def reset_output_dir(out_dir: Path, required_parent: Path) -> None:
    resolved_out = out_dir.resolve()
    resolved_parent = required_parent.resolve()
    if resolved_out == resolved_parent or resolved_parent not in resolved_out.parents:
        raise RuntimeError(f"refusing to reset unexpected Step105 output directory: {out_dir}")
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


def numeric_values_finite(row: dict) -> bool:
    for value in row.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            return False
    return True


def flow_row_finite(row: dict) -> bool:
    for key, value in row.items():
        if key.endswith("_ux") and not math.isfinite(float(value)):
            return False
    return True


def row_name_from_config(config_path: str) -> str:
    return Path(config_path).stem.removeprefix("step105_")


def step36_wall_velocity_config_used(config) -> bool:
    value = config.wall_velocity_application_config_path
    return bool(value and "step36_wall_velocity_application_solid_vel_experimental" in value)
