from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np

from src.mpm_lbm.evidence.step111_common import (
    read_json,
    reset_output_dir,
    safe_ratio,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)
from src.mpm_lbm.sim.lbm.restart import read_lbm_restart_npz, save_lbm_restart_from_lbm


PREFLOW_FIELDS = [
    "row_name",
    "preflow_source",
    "real_lbm_step_called",
    "n_grid",
    "completed_lbm_substeps",
    "target_u_lbm_x",
    "inlet_plane_mean_ux_final",
    "mid_duct_plane_mean_ux_final",
    "outlet_plane_mean_ux_final",
    "rho_min_final",
    "rho_max_final",
    "has_nan",
    "has_inf",
    "restart_path",
    "restart_written",
    "restart_reload_arrays_match",
    "restart_metadata_matches_config",
    "stable",
]

FLOW_FIELDS = [
    "sample_index",
    "completed_lbm_substeps",
    "time_s",
    "inlet_mean_ux",
    "mid_mean_ux",
    "outlet_mean_ux",
    "rho_min",
    "rho_max",
    "mass_total",
    "has_nan",
    "has_inf",
]


def build_step111_real_lbm_preflow(
    root: Path,
    run_config_path: str = "configs/step111_real_lbm_preflow_48_6000substeps.json",
    policy_path: str = "configs/step108_low_mach_subcycling_policy.json",
) -> tuple[list[dict], dict, list[dict]]:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    root = Path(root)
    policy = read_json(root / policy_path)
    config = FSIDriverConfig.from_json(root / run_config_path)
    enforce_preflow_config(config, policy)

    out_dir = root / "outputs" / "step111_real_lbm_preflow"
    reset_output_dir(out_dir, root / "outputs")
    driver = FSIDriver3D(config, str(out_dir))
    driver.initialize()

    total = int(policy["total_lbm_substeps"])
    sample_every = int(policy["lbm_substeps_per_fsi_step"])
    timeseries = [flow_row(0, 0, 0.0, driver.lbm)]
    started = time.perf_counter()
    for substep in range(1, total + 1):
        driver.lbm.step()
        if substep % sample_every == 0 or substep == total:
            official_step = substep // sample_every
            timeseries.append(flow_row(len(timeseries), substep, official_step * float(policy["official_fsi_dt_s"]), driver.lbm))
    elapsed_seconds = time.perf_counter() - started

    metadata = {
        "lbm_boundary_condition_mode": config.lbm_boundary_condition_mode,
        "lbm_restart_scope": config.lbm_restart_scope,
        "n_grid": int(config.n_grid),
        "preflow_source": "real_lbm_simulation",
        "target_u_lbm": [float(value) for value in config.target_u_lbm],
        "total_lbm_substeps": total,
    }
    restart_path = out_dir / "lbm_preflow_restart.npz"
    restart_stats = save_lbm_restart_from_lbm(driver.lbm, restart_path, metadata)
    arrays, read_metadata = read_lbm_restart_npz(restart_path)
    live_arrays = {
        "rho": driver.lbm.rho.to_numpy(),
        "v": driver.lbm.v.to_numpy(),
        "f": driver.lbm.f.to_numpy(),
        "F": driver.lbm.F.to_numpy(),
        "solid": driver.lbm.solid.to_numpy(),
        "static_solid": driver.lbm.static_solid.to_numpy(),
    }
    arrays_match = all(np.array_equal(np.asarray(live_arrays[key]), np.asarray(arrays[key])) for key in live_arrays)
    metadata_matches = all(read_metadata.get(key) == metadata.get(key) for key in ("lbm_boundary_condition_mode", "lbm_restart_scope", "n_grid", "target_u_lbm"))

    final = timeseries[-1]
    row = {
        "completed_lbm_substeps": total,
        "elapsed_seconds": elapsed_seconds,
        "has_inf": bool(final["has_inf"]),
        "has_nan": bool(final["has_nan"]),
        "inlet_plane_mean_ux_final": float(final["inlet_mean_ux"]),
        "mid_duct_plane_mean_ux_final": float(final["mid_mean_ux"]),
        "n_grid": int(config.n_grid),
        "outlet_plane_mean_ux_final": float(final["outlet_mean_ux"]),
        "preflow_source": "real_lbm_simulation",
        "real_lbm_step_called": True,
        "restart_metadata_matches_config": bool(metadata_matches),
        "restart_path": "outputs/step111_real_lbm_preflow/lbm_preflow_restart.npz",
        "restart_reload_arrays_match": bool(arrays_match),
        "restart_written": restart_path.is_file(),
        "rho_max_final": float(final["rho_max"]),
        "rho_min_final": float(final["rho_min"]),
        "row_name": "real_lbm_preflow_48_6000substeps",
        "stable": False,
        "target_u_lbm_x": float(config.target_u_lbm[0]),
    }
    row["stable"] = preflow_row_pass(row, policy)
    rows = [row]
    summary = {
        "preflow_pass": bool(row["stable"]),
        "preflow_source": "real_lbm_simulation",
        "real_lbm_step_called_count": 1,
        "restart_payload_has_inf": bool(restart_stats["has_inf"]),
        "restart_payload_has_nan": bool(restart_stats["has_nan"]),
        "row_count": 1,
    }
    write_preflow_artifacts(out_dir, rows, summary, timeseries, restart_stats)
    if not summary["preflow_pass"]:
        raise RuntimeError(f"Step111 real LBM preflow failed: {summary}")
    return rows, summary, timeseries


def enforce_preflow_config(config, policy: dict) -> None:
    if config.lbm_boundary_condition_mode != "duct_velocity_inlet_pressure_outlet":
        raise RuntimeError("Step111 preflow requires duct velocity inlet / pressure outlet")
    if int(config.n_grid) != int(policy["n_grid"]):
        raise RuntimeError("Step111 preflow n_grid mismatch")
    if int(config.n_lbm_steps) != int(policy["official_steps"]):
        raise RuntimeError("Step111 preflow official step count mismatch")
    if int(config.lbm_substeps_per_fsi_step) != int(policy["lbm_substeps_per_fsi_step"]):
        raise RuntimeError("Step111 preflow substep count mismatch")
    if list(config.target_u_lbm) != list(policy["target_u_lbm_vector"]):
        raise RuntimeError("Step111 preflow target_u_lbm mismatch")
    if config.write_vtk or config.write_particles:
        raise RuntimeError("Step111 preflow must not write large visualization outputs")


def flow_row(sample_index: int, completed_lbm_substeps: int, time_s: float, lbm) -> dict:
    velocity = lbm.v.to_numpy()
    rho = lbm.rho.to_numpy()
    solid = lbm.solid.to_numpy()
    fluid = solid == 0
    rho_fluid = rho[fluid]
    vel_fluid = velocity[fluid]
    n_grid = int(velocity.shape[0])
    inlet = plane_mean_ux(velocity, solid, 0)
    mid = plane_mean_ux(velocity, solid, n_grid // 2)
    outlet = plane_mean_ux(velocity, solid, n_grid - 1)
    return {
        "completed_lbm_substeps": int(completed_lbm_substeps),
        "has_inf": bool(np.isinf(rho_fluid).any() or np.isinf(vel_fluid).any()),
        "has_nan": bool(np.isnan(rho_fluid).any() or np.isnan(vel_fluid).any()),
        "inlet_mean_ux": inlet,
        "mass_total": float(np.sum(rho_fluid)) if rho_fluid.size else 0.0,
        "mid_mean_ux": mid,
        "outlet_mean_ux": outlet,
        "rho_max": float(np.max(rho_fluid)) if rho_fluid.size else float("nan"),
        "rho_min": float(np.min(rho_fluid)) if rho_fluid.size else float("nan"),
        "sample_index": int(sample_index),
        "time_s": float(time_s),
    }


def plane_mean_ux(velocity: np.ndarray, solid: np.ndarray, x_index: int) -> float:
    fluid = solid[x_index, :, :] == 0
    if not np.any(fluid):
        return 0.0
    return float(np.mean(velocity[x_index, :, :, 0][fluid]))


def preflow_row_pass(row: dict, policy: dict) -> bool:
    inlet_lo, inlet_hi = policy["duct_only_inlet_mean_ux_range"]
    return bool(
        row["preflow_source"] == "real_lbm_simulation"
        and row["real_lbm_step_called"]
        and int(row["completed_lbm_substeps"]) == int(policy["total_lbm_substeps"])
        and float(inlet_lo) <= float(row["inlet_plane_mean_ux_final"]) <= float(inlet_hi)
        and float(row["mid_duct_plane_mean_ux_final"]) > float(policy["duct_only_min_mid_duct_plane_mean_ux"])
        and float(row["outlet_plane_mean_ux_final"]) > float(policy["duct_only_min_outlet_plane_mean_ux"])
        and float(row["rho_min_final"]) > float(policy["duct_only_rho_min_lower_bound"])
        and float(row["rho_max_final"]) < float(policy["duct_only_rho_max_upper_bound"])
        and row["restart_written"]
        and row["restart_reload_arrays_match"]
        and row["restart_metadata_matches_config"]
        and not row["has_nan"]
        and not row["has_inf"]
        and all(math.isfinite(float(row[key])) for key in ("inlet_plane_mean_ux_final", "mid_duct_plane_mean_ux_final", "outlet_plane_mean_ux_final"))
    )


def write_preflow_artifacts(out_dir: Path, rows: list[dict], summary: dict, timeseries: list[dict], restart_stats: dict) -> None:
    write_json(out_dir / "preflow_report.json", {"summary": summary, "rows": rows})
    write_json(out_dir / "restart_payload_report.json", restart_stats)
    write_csv_rows(out_dir / "preflow_report.csv", rows, PREFLOW_FIELDS)
    write_csv_rows(out_dir / "preflow_summary.csv", summary_rows(summary), ["metric", "value"])
    write_csv_rows(out_dir / "flow_plane_timeseries.csv", timeseries, FLOW_FIELDS)
    write_markdown_table(out_dir / "preflow_report.md", "Step111 Real LBM Preflow", rows, PREFLOW_FIELDS)
