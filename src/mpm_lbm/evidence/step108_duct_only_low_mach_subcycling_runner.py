from __future__ import annotations

import time
from pathlib import Path

import numpy as np

from src.mpm_lbm.evidence.step108_common import (
    numeric_values_finite,
    read_json,
    reset_output_dir,
    safe_ratio,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)


DUCT_FIELDS = [
    "row_name",
    "n_grid",
    "official_steps",
    "lbm_substeps_per_fsi_step",
    "completed_official_steps",
    "completed_lbm_substeps",
    "low_mach_mapping_enabled",
    "target_inlet_velocity_mps",
    "target_u_lbm",
    "lbm_dt_phys_s",
    "official_fsi_dt_s",
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
    "stable",
]

FLOW_TIMESERIES_FIELDS = [
    "official_step",
    "completed_lbm_substeps",
    "time_s",
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


def build_step108_duct_only_low_mach_subcycling(
    root: Path,
    run_config_path: str = "configs/step108_duct_only_low_mach_subcycling_48_50official_steps.json",
    policy_path: str = "configs/step108_low_mach_subcycling_policy.json",
) -> tuple[list[dict], dict, list[dict]]:
    root = Path(root)
    policy = read_json(root / policy_path)
    config = read_json(root / run_config_path)
    enforce_step108_duct_config(config, policy)

    out_dir = root / "outputs" / "step108_duct_only_low_mach_subcycling"
    reset_output_dir(out_dir, root / "outputs")
    row, timeseries = run_step108_duct_only_case(root, config, policy, out_dir)
    rows = [row]
    summary = step108_duct_summary(rows)
    write_step108_duct_artifacts(out_dir, rows, summary, timeseries)
    return rows, summary, timeseries


def run_step108_duct_only_case(root: Path, config: dict, policy: dict, out_dir: Path) -> tuple[dict, list[dict]]:
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
    geometry_report["low_mach_mapping_enabled"] = bool(config["low_mach_mapping_enabled"])
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

    official_steps = int(config["official_steps"])
    substeps = int(config["lbm_substeps_per_fsi_step"])
    timeseries = [flow_timeseries_row(0, 0, 0.0, lbm)]
    started = time.perf_counter()
    completed_lbm_substeps = 0
    for official_step in range(1, official_steps + 1):
        for _ in range(substeps):
            lbm.step()
            completed_lbm_substeps += 1
        timeseries.append(
            flow_timeseries_row(
                official_step,
                completed_lbm_substeps,
                float(official_step) * float(config["official_fsi_dt_s"]),
                lbm,
            )
        )
    elapsed_seconds = time.perf_counter() - started

    final = timeseries[-1]
    row = {
        "completed_lbm_substeps": completed_lbm_substeps,
        "completed_official_steps": official_steps,
        "elapsed_seconds": elapsed_seconds,
        "has_inf": bool(final["has_inf"]),
        "has_nan": bool(final["has_nan"]),
        "inlet_plane_max_ux_final": float(final["inlet_max_ux"]),
        "inlet_plane_mean_ux_final": float(final["inlet_mean_ux"]),
        "lbm_dt_phys_s": float(config["lbm_dt_phys_s"]),
        "lbm_substeps_per_fsi_step": substeps,
        "low_mach_mapping_enabled": bool(config["low_mach_mapping_enabled"]),
        "mass_total_final": float(final["mass_total"]),
        "mid_duct_plane_max_ux_final": float(final["mid_max_ux"]),
        "mid_duct_plane_mean_ux_final": float(final["mid_mean_ux"]),
        "n_grid": n_grid,
        "official_fsi_dt_s": float(config["official_fsi_dt_s"]),
        "official_steps": official_steps,
        "outlet_plane_max_ux_final": float(final["outlet_max_ux"]),
        "outlet_plane_mean_ux_final": float(final["outlet_mean_ux"]),
        "outlet_to_inlet_mean_ux_ratio_final": float(final["outlet_to_inlet_mean_ux_ratio"]),
        "outlet_to_mid_mean_ux_ratio_final": float(final["outlet_to_mid_mean_ux_ratio"]),
        "rho_max_final": float(final["rho_max"]),
        "rho_min_final": float(final["rho_min"]),
        "row_name": str(config["row_name"]),
        "stable": False,
        "target_inlet_velocity_mps": float(config["target_inlet_velocity_mps"]),
        "target_u_lbm": list(config["target_u_lbm"]),
    }
    row["stable"] = step108_duct_row_pass(row, policy)
    if not row["stable"]:
        raise RuntimeError(f"Step108 duct-only low-Mach subcycling failed acceptance: {row}")
    return row, timeseries


def flow_timeseries_row(official_step: int, completed_lbm_substeps: int, time_s: float, lbm) -> dict:
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
        "completed_lbm_substeps": int(completed_lbm_substeps),
        "has_inf": has_inf,
        "has_nan": has_nan,
        "inlet_max_ux": inlet["max_ux"],
        "inlet_mean_ux": inlet["mean_ux"],
        "mass_total": float(np.sum(rho_fluid)) if rho_fluid.size else 0.0,
        "mid_max_ux": mid["max_ux"],
        "mid_mean_ux": mid["mean_ux"],
        "official_step": int(official_step),
        "outlet_max_ux": outlet["max_ux"],
        "outlet_mean_ux": outlet["mean_ux"],
        "outlet_to_inlet_mean_ux_ratio": safe_ratio(outlet["mean_ux"], inlet["mean_ux"]),
        "outlet_to_mid_mean_ux_ratio": safe_ratio(outlet["mean_ux"], mid["mean_ux"]),
        "rho_max": float(np.max(rho_fluid)) if rho_fluid.size else float("nan"),
        "rho_min": float(np.min(rho_fluid)) if rho_fluid.size else float("nan"),
        "time_s": float(time_s),
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


def enforce_step108_duct_config(config: dict, policy: dict) -> None:
    expected = {
        "geometry_config_path": policy["geometry_config_path"],
        "lbm_dt_phys_s": float(policy["lbm_dt_phys_s"]),
        "lbm_substeps_per_fsi_step": int(policy["lbm_substeps_per_fsi_step"]),
        "n_grid": int(policy["n_grid"]),
        "official_fsi_dt_s": float(policy["official_fsi_dt_s"]),
        "official_steps": int(policy["official_steps"]),
        "row_name": policy["required_duct_row_name"],
        "target_inlet_velocity_mps": float(policy["target_inlet_velocity_mps"]),
        "total_lbm_substeps": int(policy["total_lbm_substeps"]),
    }
    actual = {key: config[key] for key in expected.keys()}
    for key, expected_value in expected.items():
        actual_value = actual[key]
        if isinstance(expected_value, float):
            if abs(float(actual_value) - expected_value) > 1.0e-15:
                raise RuntimeError(f"Step108 duct config mismatch for {key}: {actual_value} != {expected_value}")
        elif actual_value != expected_value:
            raise RuntimeError(f"Step108 duct config mismatch for {key}: {actual_value} != {expected_value}")
    if list(config["target_u_lbm"]) != list(policy["target_u_lbm_vector"]):
        raise RuntimeError("Step108 duct config target_u_lbm mismatch")
    if bool(config["include_flap_in_lbm_static_geometry"]):
        raise RuntimeError("Step108 duct-only LBM static geometry must exclude the flap")
    if config["write_vtk"] or config["write_particles"]:
        raise RuntimeError("Step108 duct-only runner must not write VTK or particles")


def step108_duct_row_pass(row: dict, policy: dict) -> bool:
    inlet_lo, inlet_hi = policy["duct_only_inlet_mean_ux_range"]
    return bool(
        row["row_name"] == policy["required_duct_row_name"]
        and int(row["n_grid"]) == int(policy["n_grid"])
        and int(row["completed_official_steps"]) == int(policy["official_steps"])
        and int(row["completed_lbm_substeps"]) == int(policy["total_lbm_substeps"])
        and int(row["lbm_substeps_per_fsi_step"]) == int(policy["lbm_substeps_per_fsi_step"])
        and row["low_mach_mapping_enabled"]
        and list(row["target_u_lbm"]) == list(policy["target_u_lbm_vector"])
        and float(inlet_lo) <= float(row["inlet_plane_mean_ux_final"]) <= float(inlet_hi)
        and float(row["mid_duct_plane_mean_ux_final"]) > float(policy["duct_only_min_mid_duct_plane_mean_ux"])
        and float(row["outlet_plane_mean_ux_final"]) > float(policy["duct_only_min_outlet_plane_mean_ux"])
        and float(row["rho_min_final"]) > float(policy["duct_only_rho_min_lower_bound"])
        and float(row["rho_max_final"]) < float(policy["duct_only_rho_max_upper_bound"])
        and not row["has_nan"]
        and not row["has_inf"]
        and numeric_values_finite(row)
    )


def step108_duct_summary(rows: list[dict]) -> dict:
    summary = {
        "duct_only_low_mach_subcycling_pass": False,
        "has_inf_count": sum(1 for row in rows if row["has_inf"]),
        "has_nan_count": sum(1 for row in rows if row["has_nan"]),
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if row["stable"]),
    }
    summary["duct_only_low_mach_subcycling_pass"] = bool(
        rows
        and summary["stable_count"] == summary["row_count"]
        and summary["has_nan_count"] == 0
        and summary["has_inf_count"] == 0
    )
    return summary


def write_step108_duct_artifacts(out_dir: Path, rows: list[dict], summary: dict, timeseries: list[dict]) -> None:
    write_json(out_dir / "flow_plane_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "flow_plane_report.csv", rows, DUCT_FIELDS)
    write_csv_rows(out_dir / "flow_plane_summary.csv", summary_rows(summary), ["metric", "value"])
    write_csv_rows(out_dir / "flow_plane_timeseries.csv", timeseries, FLOW_TIMESERIES_FIELDS)
    write_markdown_table(
        out_dir / "flow_plane_report.md",
        "Step108 Duct-Only Low-Mach Subcycling Report",
        rows,
        DUCT_FIELDS,
    )
