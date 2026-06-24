from __future__ import annotations

import math
import shutil
import time
from pathlib import Path

import numpy as np

from src.mpm_lbm.evidence.step105_gap_taxonomy import build_step105_gap_taxonomy
from src.mpm_lbm.evidence.step106_common import (
    ALLOWED_CLAIM,
    STEP106_DUCT_ROW_NAME,
    STEP106_FSI_ROW_NAME,
    numeric_values_finite,
    read_json,
    reset_output_dir,
    safe_ratio,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)


DUCT_FLOW_FIELDS = [
    "row_name",
    "n_grid",
    "n_lbm_steps",
    "completed_lbm_steps",
    "bc_x_left",
    "bc_x_right",
    "target_u_lbm",
    "pressure_outlet_policy",
    "inlet_plane_mean_ux_final",
    "inlet_plane_max_ux_final",
    "mid_duct_plane_mean_ux_final",
    "mid_duct_plane_max_ux_final",
    "outlet_plane_mean_ux_final",
    "outlet_plane_max_ux_final",
    "outlet_to_mid_mean_ux_ratio_final",
    "outlet_to_inlet_mean_ux_ratio_final",
    "rho_min_final",
    "rho_max_final",
    "mass_total_final",
    "has_nan",
    "has_inf",
    "direct_quantitative_equivalence_allowed",
    "validation_claim_allowed",
    "stable",
]

FLOW_TIMESERIES_FIELDS = [
    "step",
    "inlet_mean_ux",
    "inlet_max_ux",
    "mid_mean_ux",
    "mid_max_ux",
    "outlet_mean_ux",
    "outlet_max_ux",
    "outlet_to_mid_mean_ux_ratio",
    "outlet_to_inlet_mean_ux_ratio",
    "rho_min",
    "rho_max",
    "mass_total",
    "has_nan",
    "has_inf",
]

FSI_FIELDS = [
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
    "fixed_base_particle_count",
    "fixed_base_constraint_applied",
    "fixed_base_max_displacement_norm",
    "fixed_base_max_velocity_norm",
    "step36_squid_wall_velocity_config_used",
    "outlet_plane_mean_ux_final",
    "outlet_plane_max_ux_final",
    "outlet_plane_flow_present",
    "gap_count",
    "direct_quantitative_equivalence_allowed",
    "validation_claim_allowed",
    "has_nan",
    "has_inf",
    "stable",
]


def build_step106_outlet_boundary_flow(
    root: Path,
    run_config_path: str = "configs/step106_duct_only_lbm_outlet_boundary_flow_48.json",
    policy_path: str = "configs/step106_outlet_boundary_flow_policy.json",
) -> tuple[list[dict], dict, list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    config = read_json(root / run_config_path)
    enforce_step106_duct_config(config, policy)

    out_dir = root / "outputs" / "step106_outlet_boundary_flow_propagation"
    reset_output_dir(out_dir, root / "outputs")
    row, timeseries, semantics = run_step106_duct_only_case(root, config, policy, out_dir)
    rows = [row]
    summary = step106_duct_summary(rows)
    write_step106_duct_artifacts(out_dir, rows, summary, timeseries, semantics)
    return rows, summary, timeseries, semantics


def run_step106_duct_only_case(root: Path, config: dict, policy: dict, out_dir: Path) -> tuple[dict, list[dict], dict]:
    from src.mpm_lbm.sim.geometry.config import GeometryConfig
    from src.mpm_lbm.sim.geometry.duct_flap_proxy import duct_flap_proxy_static_geometry
    from src.mpm_lbm.sim.lbm.config import LBMConfig
    from src.mpm_lbm.sim.lbm.fluid import LBMFluid3D

    n_grid = int(config["n_grid"])
    geometry_config = GeometryConfig.from_json(str(root / config["geometry_config_path"]))
    solid_geo, geometry_report = duct_flap_proxy_static_geometry(
        n_grid,
        geometry_config,
        include_flap=bool(config["include_flap_in_lbm_static_geometry"]),
    )
    geo_path = out_dir / f"geo_duct_flap_proxy_{n_grid}.dat"
    np.savetxt(geo_path, solid_geo.reshape(-1, order="F"), fmt="%d")
    geometry_report = dict(geometry_report)
    geometry_report["geo_path"] = geo_path.name
    geometry_report["lbm_boundary_condition_mode"] = "duct_velocity_inlet_pressure_outlet"
    write_json(out_dir / "duct_static_geometry_report.json", geometry_report)

    lbm_config = LBMConfig(
        nx=n_grid,
        ny=n_grid,
        nz=n_grid,
        niu=float(config["lbm_niu"]),
        rho0=float(config["rho0"]),
        bc_x_left=int(config["bc_x_left"]),
        bc_x_right=int(config["bc_x_right"]),
        vel_bc_x_left=tuple(float(value) for value in config["target_u_lbm"]),
        rho_bc_x_right=float(config["rho_bc_x_right"]),
    )
    lbm = LBMFluid3D(lbm_config)
    lbm.init_geo(str(geo_path))
    lbm.init_simulation()

    timeseries = [flow_timeseries_row(0, lbm)]
    started = time.perf_counter()
    for step in range(1, int(config["n_lbm_steps"]) + 1):
        lbm.step()
        timeseries.append(flow_timeseries_row(step, lbm))
    elapsed_seconds = time.perf_counter() - started

    final = timeseries[-1]
    semantics = step106_boundary_semantics(config, lbm_config)
    row = {
        "allowed_claim": ALLOWED_CLAIM,
        "bc_x_left": int(lbm_config.bc_x_left),
        "bc_x_right": int(lbm_config.bc_x_right),
        "completed_lbm_steps": int(config["n_lbm_steps"]),
        "direct_quantitative_equivalence_allowed": False,
        "elapsed_seconds": elapsed_seconds,
        "has_inf": bool(final["has_inf"]),
        "has_nan": bool(final["has_nan"]),
        "inlet_plane_max_ux_final": float(final["inlet_max_ux"]),
        "inlet_plane_mean_ux_final": float(final["inlet_mean_ux"]),
        "mass_total_final": float(final["mass_total"]),
        "mid_duct_plane_max_ux_final": float(final["mid_max_ux"]),
        "mid_duct_plane_mean_ux_final": float(final["mid_mean_ux"]),
        "n_grid": n_grid,
        "n_lbm_steps": int(config["n_lbm_steps"]),
        "outlet_plane_max_ux_final": float(final["outlet_max_ux"]),
        "outlet_plane_mean_ux_final": float(final["outlet_mean_ux"]),
        "outlet_to_inlet_mean_ux_ratio_final": float(final["outlet_to_inlet_mean_ux_ratio"]),
        "outlet_to_mid_mean_ux_ratio_final": float(final["outlet_to_mid_mean_ux_ratio"]),
        "pressure_outlet_policy": config["pressure_outlet_velocity_policy"],
        "rho_max_final": float(final["rho_max"]),
        "rho_min_final": float(final["rho_min"]),
        "row_name": str(config["row_name"]),
        "stable": False,
        "target_u_lbm": list(config["target_u_lbm"]),
        "validation_claim_allowed": False,
    }
    row["stable"] = step106_duct_row_pass(row, semantics, policy)
    if not row["stable"]:
        raise RuntimeError(f"Step106 duct-only outlet flow failed acceptance: {row}")
    return row, timeseries, semantics


def flow_timeseries_row(step: int, lbm) -> dict:
    velocity = lbm.v.to_numpy()
    rho = lbm.rho.to_numpy()
    solid = lbm.solid.to_numpy()
    fluid = solid == 0
    rho_fluid = rho[fluid]
    vel_fluid = velocity[fluid]
    has_nan = bool(np.isnan(rho_fluid).any() or np.isnan(vel_fluid).any())
    has_inf = bool(np.isinf(rho_fluid).any() or np.isinf(vel_fluid).any())
    n_grid = int(velocity.shape[0])
    inlet = plane_ux_stats(velocity, solid, 0)
    mid = plane_ux_stats(velocity, solid, n_grid // 2)
    outlet = plane_ux_stats(velocity, solid, n_grid - 1)
    return {
        "has_inf": has_inf,
        "has_nan": has_nan,
        "inlet_max_ux": inlet["max_ux"],
        "inlet_mean_ux": inlet["mean_ux"],
        "mass_total": float(np.sum(rho_fluid)) if rho_fluid.size else 0.0,
        "mid_max_ux": mid["max_ux"],
        "mid_mean_ux": mid["mean_ux"],
        "outlet_max_ux": outlet["max_ux"],
        "outlet_mean_ux": outlet["mean_ux"],
        "outlet_to_inlet_mean_ux_ratio": safe_ratio(outlet["mean_ux"], inlet["mean_ux"]),
        "outlet_to_mid_mean_ux_ratio": safe_ratio(outlet["mean_ux"], mid["mean_ux"]),
        "rho_max": float(np.max(rho_fluid)) if rho_fluid.size else float("nan"),
        "rho_min": float(np.min(rho_fluid)) if rho_fluid.size else float("nan"),
        "step": int(step),
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


def step106_boundary_semantics(config: dict, lbm_config) -> dict:
    return {
        "bc_x_left": int(lbm_config.bc_x_left),
        "bc_x_right": int(lbm_config.bc_x_right),
        "direct_quantitative_equivalence_allowed": False,
        "pressure_outlet_policy": "interior_neighbor_velocity_extrapolation",
        "pressure_outlet_uses_boundary_self_velocity": False,
        "pressure_outlet_uses_interior_neighbor_velocity": True,
        "pressure_outlet_velocity_source": "self.v[self.nx-2,j,k] when the x-right interior neighbor is fluid",
        "rho_bc_x_right": float(lbm_config.rho_bc_x_right),
        "target_u_lbm": list(config["target_u_lbm"]),
        "validation_claim_allowed": False,
        "velocity_inlet_policy": "fixed_equilibrium_velocity",
    }


def step106_duct_row_pass(row: dict, semantics: dict, policy: dict) -> bool:
    inlet_lo, inlet_hi = policy["inlet_plane_mean_ux_range"]
    return bool(
        row["row_name"] == policy["required_duct_row_name"]
        and int(row["n_grid"]) == int(policy["required_duct_n_grid"])
        and int(row["bc_x_left"]) == int(policy["required_bc_x_left"])
        and int(row["bc_x_right"]) == int(policy["required_bc_x_right"])
        and list(row["target_u_lbm"]) == list(policy["required_target_u_lbm"])
        and row["pressure_outlet_policy"] == policy["pressure_outlet_policy"]
        and int(row["completed_lbm_steps"]) == int(row["n_lbm_steps"])
        and float(row["outlet_plane_mean_ux_final"]) > float(policy["min_outlet_plane_mean_ux"])
        and float(row["outlet_plane_max_ux_final"]) > float(policy["min_outlet_plane_max_ux"])
        and float(row["mid_duct_plane_mean_ux_final"]) > float(policy["min_mid_duct_plane_mean_ux"])
        and float(inlet_lo) <= float(row["inlet_plane_mean_ux_final"]) <= float(inlet_hi)
        and float(row["rho_min_final"]) > float(policy["rho_min_lower_bound"])
        and float(row["rho_max_final"]) < float(policy["rho_max_upper_bound"])
        and not row["has_nan"]
        and not row["has_inf"]
        and semantics["pressure_outlet_uses_boundary_self_velocity"] is False
        and semantics["pressure_outlet_uses_interior_neighbor_velocity"] is True
        and not row["direct_quantitative_equivalence_allowed"]
        and not row["validation_claim_allowed"]
        and numeric_values_finite(row)
    )


def step106_duct_summary(rows: list[dict]) -> dict:
    summary = {
        "direct_quantitative_equivalence_allowed": False,
        "duct_only_outlet_boundary_flow_pass": False,
        "has_inf_count": sum(1 for row in rows if row["has_inf"]),
        "has_nan_count": sum(1 for row in rows if row["has_nan"]),
        "outlet_flow_present_count": sum(1 for row in rows if row["outlet_plane_mean_ux_final"] > 1.0e-5),
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if row["stable"]),
        "validation_claim_allowed": False,
    }
    summary["duct_only_outlet_boundary_flow_pass"] = bool(
        rows
        and summary["stable_count"] == summary["row_count"]
        and summary["has_nan_count"] == 0
        and summary["has_inf_count"] == 0
        and not summary["direct_quantitative_equivalence_allowed"]
        and not summary["validation_claim_allowed"]
    )
    return summary


def write_step106_duct_artifacts(out_dir: Path, rows: list[dict], summary: dict, timeseries: list[dict], semantics: dict) -> None:
    write_json(out_dir / "flow_plane_report.json", {"summary": summary, "rows": rows})
    write_json(out_dir / "boundary_condition_semantics_report.json", semantics)
    write_csv_rows(out_dir / "flow_plane_report.csv", rows, DUCT_FLOW_FIELDS)
    write_csv_rows(out_dir / "flow_plane_summary.csv", summary_rows(summary), ["metric", "value"])
    write_csv_rows(out_dir / "flow_plane_timeseries.csv", timeseries, FLOW_TIMESERIES_FIELDS)
    write_markdown_table(out_dir / "flow_plane_report.md", "Step106 Outlet Boundary Flow Report", rows, DUCT_FLOW_FIELDS)


def build_step106_fsi_outlet_repair_regression(
    root: Path,
    run_config_path: str = "configs/step106_fluent_duct_flap_proxy_48_20step_outlet_repair_regression_smoke.json",
    policy_path: str = "configs/step106_outlet_boundary_flow_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [run_step106_fsi_regression_case(root, run_config_path, policy)]
    summary = step106_fsi_summary(rows)
    out_dir = root / "outputs" / "step106_fsi_outlet_repair_regression"
    write_step106_fsi_artifacts(out_dir, rows, summary)
    return rows, summary


def run_step106_fsi_regression_case(root: Path, config_path: str, policy: dict) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    config = FSIDriverConfig.from_json(root / config_path)
    row_name = Path(config_path).stem.removeprefix("step106_")
    enforce_step106_fsi_config(config, row_name, policy)

    output_dir = root / "outputs" / "step106_fsi_outlet_repair_regression"
    run_root = root / "outputs" / "step106_driver_runs"
    out_dir = run_root / row_name
    reset_output_dir(output_dir, root / "outputs")
    reset_output_dir(out_dir, run_root)

    driver = FSIDriver3D(config, str(out_dir))
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for Step106 row: {row_name}")

    copy_required_driver_artifacts(out_dir, output_dir)
    has_nan, has_inf = diagnostics_have_nan_or_inf(diagnostics)
    fixed_stats = driver.solid.get_fixed_particle_stats()
    duct_boundary = read_json(output_dir / "duct_boundary_condition_report.json")
    gap_rows, gap_summary = build_step105_gap_taxonomy(root)
    outlet = plane_ux_stats(driver.lbm.v.to_numpy(), driver.lbm.solid.to_numpy(), int(config.n_grid) - 1)
    row = {
        "allowed_claim": ALLOWED_CLAIM,
        "canonical_driver_module": driver.__class__.__module__,
        "completed_lbm_steps": int(driver.current_lbm_step),
        "diagnostics_row_count": len(diagnostics),
        "direct_quantitative_equivalence_allowed": False,
        "driver_run_called": True,
        "flap_tip_timeseries_row_count": len(driver.flap_tip_monitor_rows),
        "gap_count": int(gap_summary["gap_count"]),
        "geometry_type": config.geometry_type,
        "has_inf": bool(has_inf),
        "has_nan": bool(has_nan),
        "lbm_boundary_condition_mode": config.lbm_boundary_condition_mode,
        "n_grid": int(config.n_grid),
        "n_lbm_steps": int(config.n_lbm_steps),
        "n_particles": int(config.n_particles),
        "outlet_plane_flow_present": bool(abs(outlet["max_ux"]) > 1.0e-12 or abs(outlet["mean_ux"]) > 1.0e-12),
        "outlet_plane_max_ux_final": outlet["max_ux"],
        "outlet_plane_mean_ux_final": outlet["mean_ux"],
        "row_name": row_name,
        "stable": False,
        "step36_squid_wall_velocity_config_used": step36_wall_velocity_config_used(config),
        "target_u_lbm_applied_to_inlet": bool(duct_boundary["target_u_lbm_applied_to_inlet"]),
        "target_u_lbm_applied_to_solid_initial_velocity": bool(
            list(config.target_u_lbm) == list(config.initial_solid_velocity_norm)
            and any(abs(value) > 0.0 for value in config.target_u_lbm)
        ),
        "validation_claim_allowed": False,
        **fixed_stats,
    }
    row["stable"] = step106_fsi_row_pass(row, policy)
    if not row["stable"]:
        raise RuntimeError(f"Step106 FSI regression row failed acceptance: {row}")
    return row


def enforce_step106_duct_config(config: dict, policy: dict) -> None:
    if config["row_name"] != policy["required_duct_row_name"]:
        raise RuntimeError("Step106 duct-only row name mismatch")
    if int(config["n_grid"]) != int(policy["required_duct_n_grid"]):
        raise RuntimeError("Step106 duct-only grid mismatch")
    if config["geometry_type"] != policy["required_geometry_type"]:
        raise RuntimeError("Step106 duct-only geometry_type mismatch")
    if config["geometry_config_path"] != policy["required_geometry_config_path"]:
        raise RuntimeError("Step106 duct-only geometry_config_path mismatch")
    if list(config["target_u_lbm"]) != list(policy["required_target_u_lbm"]):
        raise RuntimeError("Step106 duct-only target_u_lbm mismatch")
    if int(config["bc_x_left"]) != int(policy["required_bc_x_left"]) or int(config["bc_x_right"]) != int(policy["required_bc_x_right"]):
        raise RuntimeError("Step106 duct-only boundary code mismatch")
    if config["pressure_outlet_velocity_policy"] != policy["pressure_outlet_policy"]:
        raise RuntimeError("Step106 duct-only pressure outlet policy mismatch")
    if bool(config["include_flap_in_lbm_static_geometry"]):
        raise RuntimeError("Step106 duct-only LBM static geometry must exclude the flap")
    if config["write_vtk"] or config["write_particles"]:
        raise RuntimeError("Step106 duct-only runner must not write VTK or particles")


def enforce_step106_fsi_config(config, row_name: str, policy: dict) -> None:
    if row_name != policy["required_fsi_row_name"]:
        raise RuntimeError("Step106 FSI row name mismatch")
    expected = {
        "n_grid": int(policy["required_fsi_n_grid"]),
        "n_particles": int(policy["required_fsi_n_particles"]),
        "n_lbm_steps": int(policy["required_fsi_n_lbm_steps"]),
    }
    actual = {
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
    }
    if actual != expected:
        raise RuntimeError(f"Step106 FSI config mismatch: {actual} != {expected}")
    if config.geometry_type != policy["required_geometry_type"]:
        raise RuntimeError("Step106 FSI geometry_type mismatch")
    if config.geometry_config_path != policy["required_geometry_config_path"]:
        raise RuntimeError("Step106 FSI geometry_config_path mismatch")
    if list(config.target_u_lbm) != list(policy["required_target_u_lbm"]):
        raise RuntimeError("Step106 FSI target_u_lbm mismatch")
    if list(config.initial_solid_velocity_norm) != list(policy["required_initial_solid_velocity_norm"]):
        raise RuntimeError("Step106 FSI initial_solid_velocity_norm mismatch")
    if config.lbm_boundary_condition_mode != policy["required_lbm_boundary_condition_mode"]:
        raise RuntimeError("Step106 FSI LBM boundary mode mismatch")
    if config.wall_velocity_application_mode != "disabled" or config.wall_velocity_application_config_path is not None:
        raise RuntimeError("Step106 FSI must keep Step36 wall velocity disabled")
    if config.coupling_mode != "moving_boundary" or config.reaction_transfer_mode != "engineering":
        raise RuntimeError("Step106 FSI must preserve moving_boundary engineering transfer")
    if config.write_vtk or config.write_particles:
        raise RuntimeError("Step106 FSI must not write VTK or particle arrays")


def step106_fsi_row_pass(row: dict, policy: dict) -> bool:
    return bool(
        row["driver_run_called"]
        and row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
        and row["row_name"] == policy["required_fsi_row_name"]
        and int(row["completed_lbm_steps"]) == int(policy["required_fsi_n_lbm_steps"])
        and int(row["diagnostics_row_count"]) >= int(policy["required_fsi_n_lbm_steps"]) + 1
        and int(row["flap_tip_timeseries_row_count"]) >= int(policy["required_fsi_n_lbm_steps"]) + 1
        and row["target_u_lbm_applied_to_inlet"]
        and not row["target_u_lbm_applied_to_solid_initial_velocity"]
        and int(row["fixed_base_particle_count"]) > 0
        and row["fixed_base_constraint_applied"]
        and float(row["fixed_base_max_displacement_norm"]) <= 1.0e-7
        and float(row["fixed_base_max_velocity_norm"]) <= 1.0e-7
        and not row["step36_squid_wall_velocity_config_used"]
        and int(row["gap_count"]) >= 8
        and not row["has_nan"]
        and not row["has_inf"]
        and not row["direct_quantitative_equivalence_allowed"]
        and not row["validation_claim_allowed"]
        and numeric_values_finite(row)
    )


def step106_fsi_summary(rows: list[dict]) -> dict:
    summary = {
        "direct_quantitative_equivalence_allowed": False,
        "has_inf_count": sum(1 for row in rows if row["has_inf"]),
        "has_nan_count": sum(1 for row in rows if row["has_nan"]),
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if row["stable"]),
        "step106_fsi_outlet_repair_regression_pass": False,
        "validation_claim_allowed": False,
    }
    summary["step106_fsi_outlet_repair_regression_pass"] = bool(
        rows
        and summary["stable_count"] == summary["row_count"]
        and summary["has_nan_count"] == 0
        and summary["has_inf_count"] == 0
        and not summary["direct_quantitative_equivalence_allowed"]
        and not summary["validation_claim_allowed"]
    )
    return summary


def write_step106_fsi_artifacts(out_dir: Path, rows: list[dict], summary: dict) -> None:
    write_json(out_dir / "fsi_outlet_repair_regression_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "fsi_outlet_repair_regression_report.csv", rows, FSI_FIELDS)
    write_csv_rows(out_dir / "fsi_outlet_repair_regression_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(out_dir / "fsi_outlet_repair_regression_report.md", "Step106 FSI Outlet Repair Regression Report", rows, FSI_FIELDS)


def copy_required_driver_artifacts(out_dir: Path, output_dir: Path) -> None:
    for name in (
        "duct_boundary_condition_report.json",
        "duct_static_geometry_report.json",
        "flap_tip_displacement_timeseries.csv",
    ):
        source = out_dir / name
        if not source.is_file():
            raise RuntimeError(f"missing Step106 driver artifact: {source}")
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
